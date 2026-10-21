// scripts/staging.mjs contra un Supabase simulado en memoria (fetch falso): flujo completo, limpieza
// aun cuando falla a mitad, "migraciones no aplicadas" y que ninguna clave se imprima.
import test from 'node:test';
import assert from 'node:assert/strict';
import { verificarStaging, MigracionesNoAplicadas, FaltanVariables } from '../scripts/staging.mjs';

const ENV = { SUPABASE_URL: 'https://x.supabase.co', SUPABASE_PUBLISHABLE_KEY: 'sb_publishable_PUBLICA123', SUPABASE_SERVICE_KEY: 'sb_secret_SECRETA456' };
const TAREA = { id: '2026-10-prueba', version: 1, ruta: 'tareas/2026-10/prueba/' };

/** Supabase mínimo en memoria. `opciones`: migraciones=false, fallaEn='moderar'|'comentar', brechaPendiente=true. */
function falsoSupabase(opciones = {}) {
  const db = { usuarios: {}, valoraciones: [], perfiles: [], comentarios: [], moderadores: [] };
  const llamadas = [];
  const resp = (status, cuerpo) => ({ status, text: async () => (cuerpo === undefined ? '' : JSON.stringify(cuerpo)) });
  const fetchFn = async (url, { method, headers, body }) => {
    const u = new URL(url); const ruta = u.pathname; const b = body ? JSON.parse(body) : {};
    llamadas.push({ method, ruta, headers });
    const esServicio = headers.apikey === ENV.SUPABASE_SERVICE_KEY;
    const uid = headers.Authorization?.startsWith('Bearer tok-') ? headers.Authorization.slice(11) : null;
    if (ruta === '/auth/v1/admin/users' && method === 'POST') {
      if (!esServicio) return resp(401, {});
      const id = 'u' + (Object.keys(db.usuarios).length + 1); db.usuarios[id] = { email: b.email, password: b.password }; return resp(200, { id });
    }
    if (ruta.startsWith('/auth/v1/admin/users/') && method === 'DELETE') { delete db.usuarios[ruta.split('/').pop()]; return resp(200, {}); }
    if (ruta === '/auth/v1/token') {
      const e = Object.entries(db.usuarios).find(([, x]) => x.email === b.email && x.password === b.password);
      return e ? resp(200, { access_token: 'tok-' + e[0] }) : resp(400, {});
    }
    if (ruta.startsWith('/rest/v1/') && opciones.migraciones === false) return resp(404, { code: 'PGRST202', message: 'no existe' });
    if (ruta === '/rest/v1/rpc/resumen_valoraciones') {
      const n = db.valoraciones.length; return resp(200, n ? [{ tarea_id: TAREA.id, n }] : []);
    }
    if (ruta === '/rest/v1/rpc/comentarios_aprobados') {
      return resp(200, db.comentarios.filter((c) => c.estado === 'aprobado' || opciones.brechaPendiente).map((c) => ({ id: c.id, texto: c.texto, rotulo: 'Docente' })));
    }
    if (ruta === '/rest/v1/rpc/moderar_comentario') {
      if (opciones.fallaEn === 'moderar') return resp(500, { message: 'boom' });
      if (!db.moderadores.includes(uid)) return resp(403, { code: '42501' });
      db.comentarios.find((c) => c.id === b.p_id).estado = b.p_estado; return resp(204);
    }
    const tabla = ruta.replace('/rest/v1/', '');
    if (method === 'POST' && tabla === 'valoraciones') { db.valoraciones.push({ user_id: uid }); return resp(201); }
    if (method === 'POST' && tabla === 'perfiles') { db.perfiles.push({ user_id: b.user_id }); return resp(201); }
    if (method === 'POST' && tabla === 'comentarios') {
      if (opciones.fallaEn === 'comentar') return resp(500, { message: 'boom' });
      const c = { id: 'c' + (db.comentarios.length + 1), user_id: uid, texto: b.texto, estado: 'pendiente' }; db.comentarios.push(c); return resp(201, [c]);
    }
    if (method === 'POST' && tabla === 'moderadores') { db.moderadores.push(b.user_id); return resp(201); }
    if (method === 'GET' && tabla === 'comentarios') return resp(200, []);   // anon: RLS cierra la tabla
    if (method === 'DELETE') {
      const uidDel = u.searchParams.get('user_id').replace('eq.', '');
      const t = tabla.split('?')[0];
      if (t === 'moderadores') db.moderadores = db.moderadores.filter((x) => x !== uidDel);
      else db[t] = db[t].filter((x) => x.user_id !== uidDel);
      return resp(204);
    }
    return resp(404, {});
  };
  return { db, fetchFn, llamadas };
}

const correr = (s, extra = {}) => verificarStaging({ env: ENV, fetchFn: s.fetchFn, tarea: TAREA, log: () => {}, ...extra });
const vacia = (db) => Object.values(db.usuarios).length === 0 && !db.valoraciones.length && !db.perfiles.length && !db.comentarios.length && !db.moderadores.length;

test('flujo completo OK y deja la base como estaba', async () => {
  const s = falsoSupabase();
  const r = await correr(s);
  assert.ok(r.pasos.length >= 7);
  assert.ok(vacia(s.db), JSON.stringify(s.db));
  assert.match(r.usuario_prueba, /^otm-staging\+\d+@example\.invalid$/);
});

test('las claves sb_* viajan solo en apikey, nunca como Authorization', async () => {
  const s = falsoSupabase();
  await correr(s);
  for (const l of s.llamadas) assert.ok(!/sb_(publishable|secret)/.test(l.headers.Authorization ?? ''), l.ruta);
});

test('sin migraciones: MigracionesNoAplicadas y no se crea ningún usuario', async () => {
  const s = falsoSupabase({ migraciones: false });
  await assert.rejects(() => correr(s), (e) => e instanceof MigracionesNoAplicadas && /migraciones no aplicadas/.test(e.message));
  assert.equal(Object.keys(s.db.usuarios).length, 0);
});

test('si falla a mitad (moderar) igual borra todo lo creado', async () => {
  const s = falsoSupabase({ fallaEn: 'moderar' });
  await assert.rejects(() => correr(s), /moderar_comentario falló/);
  assert.ok(vacia(s.db), JSON.stringify(s.db));
});

test('si falla al comentar igual borra usuario, valoración y perfil', async () => {
  const s = falsoSupabase({ fallaEn: 'comentar' });
  await assert.rejects(() => correr(s), /comentar falló/);
  assert.ok(vacia(s.db));
});

test('un comentario pendiente visible al público se reporta como falla de seguridad (y se limpia)', async () => {
  const s = falsoSupabase({ brechaPendiente: true });
  await assert.rejects(() => correr(s), /FALLA DE SEGURIDAD/);
  assert.ok(vacia(s.db));
});

test('faltan variables: FaltanVariables sin llamar a la red', async () => {
  const s = falsoSupabase();
  await assert.rejects(() => verificarStaging({ env: {}, fetchFn: s.fetchFn, tarea: TAREA, log: () => {} }), FaltanVariables);
  assert.equal(s.llamadas.length, 0);
});

test('los mensajes de error no contienen las claves', async () => {
  const s = falsoSupabase({ fallaEn: 'comentar' });
  const orig = s.fetchFn;
  s.fetchFn = async (u, o) => { const r = await orig(u, o); if (u.includes('/comentarios') && o.method === 'POST') return { status: 500, text: async () => `error con ${ENV.SUPABASE_SERVICE_KEY}` }; return r; };
  await assert.rejects(() => correr(s), (e) => !e.message.includes('SECRETA456'));
});
