// El adaptador de Supabase habla con la API REST/RPC esperada por sitio/db (fetch simulado, sin red).
import test from 'node:test';
import assert from 'node:assert/strict';
import { crearBackend, resolverModo } from '../../api/src/index.js';

const URL_SB = 'https://proyecto-falso.supabase.co';
const ANON = 'anon-key-publica-de-prueba';

function simular(rutas) {
  const llamadas = [];
  globalThis.fetch = async (url, init = {}) => {
    const u = new URL(url);
    llamadas.push({ metodo: init.method || 'GET', ruta: u.pathname, query: u.search, cab: Object.fromEntries(new Headers(init.headers)), cuerpo: init.body ? JSON.parse(init.body) : undefined });
    const h = rutas.find((r) => u.pathname === r.ruta && (r.metodo || 'GET') === (init.method || 'GET'));
    if (!h) return new Response(JSON.stringify({ message: 'sin ruta ' + u.pathname }), { status: 404, headers: { 'Content-Type': 'application/json' } });
    return new Response(JSON.stringify(h.cuerpo), { status: h.status || 200, headers: { 'Content-Type': 'application/json' } });
  };
  return llamadas;
}

test('resolverModo: sin variables no hay cuentas; con URL y anon key, supabase; local solo si se pide', () => {
  assert.equal(resolverModo({}), 'none');
  assert.equal(resolverModo({ supabaseUrl: URL_SB }), 'none');
  assert.equal(resolverModo({ supabaseUrl: URL_SB, supabaseAnonKey: ANON }), 'supabase');
  assert.equal(resolverModo({ backend: 'local' }), 'local');
  assert.equal(resolverModo({ backend: 'supabase' }), 'none', 'supabase sin credenciales públicas no se activa');
});

test('lectura pública vía RPC, con la anon key como única credencial', async () => {
  const llamadas = simular([
    { ruta: '/rest/v1/rpc/resumen_valoraciones', metodo: 'POST', cuerpo: [{ tarea_id: '2026-10-a', n: '3', promedio: '4.33', n1: 0, n2: 0, n3: 1, n4: 0, n5: 2 }] },
    { ruta: '/rest/v1/rpc/comentarios_aprobados', metodo: 'POST', cuerpo: [{ id: 'c1', tarea_version: 2, texto: 'Hola', nivel_implementado: 'S', rotulo: 'Docente · nivel S', creado: '2026-10-20T00:00:00Z' }] },
  ]);
  const b = await crearBackend({ supabaseUrl: URL_SB, supabaseAnonKey: ANON });
  assert.equal(b.modo, 'supabase');
  assert.deepEqual(await b.resumenes(), { '2026-10-a': { n: 3, promedio: 4.33, distribucion: [0, 0, 1, 0, 2] } });
  const c = await b.comentariosPublicos('2026-10-a');
  assert.deepEqual(c, [{ id: 'c1', tareaVersion: 2, texto: 'Hola', nivelImplementado: 'S', rotulo: 'Docente · nivel S', creado: '2026-10-20T00:00:00Z' }]);
  assert.deepEqual(llamadas[1].cuerpo, { p_tarea_id: '2026-10-a' });
  for (const l of llamadas) assert.equal(l.cab.apikey, ANON);
  assert.ok(!JSON.stringify(llamadas).includes('service_role'));
});

test('escribir exige sesión y validaciones del cliente (puntaje, aviso, texto)', async () => {
  simular([]);
  const b = await crearBackend({ supabaseUrl: URL_SB, supabaseAnonKey: ANON });
  await assert.rejects(() => b.valorar({ tareaId: '2026-10-a', version: 1, puntaje: 9 }), /1 a 5/);
  await assert.rejects(() => b.valorar({ tareaId: '2026-10-a', version: 1, puntaje: 5 }), (e) => e.codigo === 'sin_sesion');
  await assert.rejects(() => b.comentar({ tareaId: '2026-10-a', version: 1, texto: 'x', avisoAceptado: false }), (e) => e.codigo === 'aviso_no_aceptado');
  await assert.rejects(() => b.comentar({ tareaId: '2026-10-a', version: 1, texto: '  ', avisoAceptado: true }), (e) => e.codigo === 'texto_vacio');
  await assert.rejects(() => b.guardarPerfil({}, false), (e) => e.codigo === 'aviso_no_aceptado');
  await assert.rejects(() => b.guardarPerfil({ aniosExperiencia: 70 }, true), (e) => e.codigo === 'anios_invalidos');
});

test('valorar y guardar perfil: PATCH de la fila propia y, si no existe, POST (nunca upsert, ver db-rls)', async () => {
  const SESION = { access_token: 'jwt', refresh_token: 'r', expires_in: 3600, token_type: 'bearer', user: { id: 'u-1', email: 'a@x.cl' } };
  const llamadas = simular([
    { ruta: '/auth/v1/token', metodo: 'POST', cuerpo: SESION },
    { ruta: '/rest/v1/valoraciones', metodo: 'PATCH', cuerpo: [] },
    { ruta: '/rest/v1/valoraciones', metodo: 'POST', cuerpo: [], status: 201 },
    { ruta: '/rest/v1/perfiles', metodo: 'PATCH', cuerpo: [{ user_id: 'u-1' }] },
  ]);
  const b = await crearBackend({ supabaseUrl: URL_SB, supabaseAnonKey: ANON });
  await b.iniciarSesion({ email: 'a@x.cl', password: 'clave-larga-123' });
  await b.valorar({ tareaId: '2026-10-a', version: 2, puntaje: 4 });
  await b.guardarPerfil({ aniosExperiencia: 5 }, true);
  const rest = llamadas.filter((l) => l.ruta.startsWith('/rest/'));
  assert.deepEqual(rest.map((l) => `${l.metodo} ${l.ruta}`),
    ['PATCH /rest/v1/valoraciones', 'POST /rest/v1/valoraciones', 'PATCH /rest/v1/perfiles']);
  assert.deepEqual(rest[0].cuerpo, { tarea_version: 2, puntaje: 4 }, 'el PATCH solo lleva columnas con GRANT UPDATE');
  assert.match(rest[0].query, /user_id=eq\.u-1/); assert.match(rest[0].query, /tarea_id=eq\.2026-10-a/);
  assert.deepEqual(rest[1].cuerpo, { user_id: 'u-1', tarea_id: '2026-10-a', tarea_version: 2, puntaje: 4 });
  for (const l of rest) assert.ok(!/on_conflict/.test(l.query) && !/resolution=/.test(l.cab.prefer || ''), 'sin upsert');
  assert.ok(!('user_id' in rest[2].cuerpo));
});
