// Verificación en staging contra el Supabase real (flujo del docente de punta a punta).
//
//   SUPABASE_URL=... SUPABASE_PUBLISHABLE_KEY=... SUPABASE_SERVICE_KEY=... npm run staging
//   npm run staging -- --url https://carlosrojasbruna.github.io/otm-prensa/   (además, el flujo por la UI en Chrome)
//
// Pasos: (0) comprueba que las migraciones estén aplicadas; (1) crea con la API admin un usuario de
// prueba confirmado (otm-staging+<timestamp>@example.invalid); (2) inicia sesión con la clave
// publicable; (3) valora y comenta una tarea del catálogo (por API, o por la UI con --url);
// (4) comprueba que el comentario pendiente NO es visible al público; (5) promueve temporalmente al
// usuario a moderador (clave de servicio), aprueba con moderar_comentario() y comprueba que se ve;
// (6) borra todo lo creado (comentario, valoración, perfil, moderador temporal, usuario), incluso si
// algo falla. Códigos de salida: 0 todo bien; 1 falla; 2 migraciones no aplicadas; 3 faltan variables.
// Las claves solo se leen del entorno y nunca se imprimen.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { AVISO_VERSION } from '../../api/src/comun.js';

const aqui = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(aqui, '..', '..', '..');

export class MigracionesNoAplicadas extends Error {}
export class FaltanVariables extends Error {}

export function tareaDelCatalogo(raiz = REPO) {
  const cat = JSON.parse(fs.readFileSync(path.join(raiz, 'tareas', 'catalogo.json'), 'utf8'));
  const t = [...cat.tareas].sort((a, b) => b.fecha_publicacion.localeCompare(a.fecha_publicacion) || a.id.localeCompare(b.id))[0];
  if (!t) throw new Error('el catálogo no tiene tareas');
  return { id: t.id, version: t.version, ruta: t.ruta };
}

/** Cliente HTTP mínimo; redacta las claves de cualquier mensaje de error. */
function crearCliente({ url, publicable, servicio, fetchFn }) {
  const base = url.replace(/\/+$/, '');
  const secretos = [publicable, servicio].filter(Boolean);
  const redactar = (s) => secretos.reduce((t, k) => t.split(k).join('***'), String(s));
  const esJwt = (k) => k.startsWith('eyJ');
  async function llamar(ruta, { metodo = 'GET', clave, token, cuerpo, cabeceras = {} } = {}) {
    const h = { apikey: clave, 'Content-Type': 'application/json', ...cabeceras };
    if (token) h.Authorization = `Bearer ${token}`;
    else if (esJwt(clave)) h.Authorization = `Bearer ${clave}`; // las claves sb_* viajan solo en `apikey`
    const r = await fetchFn(base + ruta, { method: metodo, headers: h, body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo) });
    const texto = await r.text();
    let json = null;
    try { json = texto ? JSON.parse(texto) : null; } catch { /* cuerpo no JSON */ }
    return { status: r.status, ok: r.status >= 200 && r.status < 300, json, texto: redactar(texto).slice(0, 300) };
  }
  return {
    llamar, redactar,
    publica: (ruta, o = {}) => llamar(ruta, { clave: publicable, ...o }),
    servicio: (ruta, o = {}) => llamar(ruta, { clave: servicio, ...o }),
  };
}

const migracionesFaltan = (r) => r.status === 404 || ['PGRST202', 'PGRST205', '42883', '42P01'].includes(r.json?.code);

/**
 * Ejecuta la verificación. `ui` (opcional): async ({ rutaTarea, correo, clave, comentario }) que
 * valora y comenta por la interfaz; si no se da, se hace por API.
 */
export async function verificarStaging({ env = process.env, fetchFn = fetch, tarea = tareaDelCatalogo(), ui = null, log = console.log } = {}) {
  const url = env.SUPABASE_URL, publicable = env.SUPABASE_PUBLISHABLE_KEY, servicio = env.SUPABASE_SERVICE_KEY;
  const faltan = [['SUPABASE_URL', url], ['SUPABASE_PUBLISHABLE_KEY', publicable], ['SUPABASE_SERVICE_KEY', servicio]].filter(([, v]) => !v).map(([k]) => k);
  if (faltan.length) throw new FaltanVariables(`faltan variables de entorno: ${faltan.join(', ')}`);
  const c = crearCliente({ url, publicable, servicio, fetchFn });
  const creado = { usuario: null, comentario: null };
  const pasos = [];
  const paso = (nombre) => { pasos.push(nombre); log(`ok   ${nombre}`); };
  const exigir = (cond, msg) => { if (!cond) throw new Error(msg); };

  // 0. migraciones
  const sonda = await c.publica('/rest/v1/rpc/resumen_valoraciones', { metodo: 'POST', cuerpo: {} });
  if (migracionesFaltan(sonda)) throw new MigracionesNoAplicadas('migraciones no aplicadas: aplicar sitio/db/aplicar_todo.sql (ver sitio/db/README.md)');
  exigir(sonda.ok, `la sonda de migraciones respondió ${sonda.status}: ${sonda.texto}`);
  paso('migraciones aplicadas (resumen_valoraciones responde)');

  const correo = `otm-staging+${Date.now()}@example.invalid`;
  const clave = 'Stg-' + crypto.randomBytes(12).toString('base64url');
  const textoComentario = `Comentario de verificación en staging ${new Date().toISOString()}. Se borra solo.`;
  let token = null;
  const errores = [];
  try {
    // 1. usuario de prueba confirmado
    const u = await c.servicio('/auth/v1/admin/users', { metodo: 'POST', cuerpo: { email: correo, password: clave, email_confirm: true } });
    exigir(u.ok && u.json?.id, `no se pudo crear el usuario de prueba (${u.status}): ${u.texto}`);
    creado.usuario = u.json.id;
    paso('usuario de prueba creado y confirmado (API admin)');

    // 2. inicio de sesión con la clave publicable
    const s = await c.publica('/auth/v1/token?grant_type=password', { metodo: 'POST', cuerpo: { email: correo, password: clave } });
    exigir(s.ok && s.json?.access_token, `inicio de sesión falló (${s.status}): ${s.texto}`);
    token = s.json.access_token;
    paso('inicio de sesión con la clave publicable');

    // 3. valorar y comentar
    if (ui) {
      await ui({ rutaTarea: tarea.ruta, correo, clave, comentario: textoComentario });
      paso('valoración y comentario por la interfaz (Chrome headless)');
      const mis = await c.publica('/rest/v1/comentarios?select=id,estado&user_id=eq.' + creado.usuario, { token });
      exigir(mis.ok && mis.json?.length === 1, `se esperaba 1 comentario del usuario de prueba: ${mis.texto}`);
      creado.comentario = mis.json[0].id;
      exigir(mis.json[0].estado === 'pendiente', `el comentario debía quedar pendiente y está ${mis.json[0].estado}`);
    } else {
      const v = await c.publica('/rest/v1/valoraciones', { metodo: 'POST', token, cuerpo: { tarea_id: tarea.id, tarea_version: tarea.version, puntaje: 4 } });
      exigir(v.ok, `valorar falló (${v.status}): ${v.texto}`);
      const p = await c.publica('/rest/v1/perfiles', { metodo: 'POST', token, cuerpo: { user_id: creado.usuario, nivel_ensenanza: 'S', aviso_version: AVISO_VERSION } });
      exigir(p.ok, `crear perfil falló (${p.status}): ${p.texto}`);
      const cm = await c.publica('/rest/v1/comentarios', {
        metodo: 'POST', token, cabeceras: { Prefer: 'return=representation' },
        cuerpo: { tarea_id: tarea.id, tarea_version: tarea.version, texto: textoComentario, nivel_implementado: 'S', aviso_version: AVISO_VERSION },
      });
      exigir(cm.ok && cm.json?.[0]?.id, `comentar falló (${cm.status}): ${cm.texto}`);
      creado.comentario = cm.json[0].id;
      exigir(cm.json[0].estado === 'pendiente', 'el comentario nuevo debía nacer pendiente');
      paso('valoración, perfil y comentario creados (nace pendiente)');
    }

    const resumen = await c.publica('/rest/v1/rpc/resumen_valoraciones', { metodo: 'POST', cuerpo: {} });
    exigir(resumen.ok && resumen.json.some((r) => r.tarea_id === tarea.id && Number(r.n) >= 1), 'la valoración no aparece en resumen_valoraciones()');
    paso('la valoración aparece en el resumen público');

    // 4. pendiente: invisible al público
    const publicos = async () => {
      const r = await c.publica('/rest/v1/rpc/comentarios_aprobados', { metodo: 'POST', cuerpo: { p_tarea_id: tarea.id } });
      exigir(r.ok, `comentarios_aprobados falló (${r.status}): ${r.texto}`);
      return r.json;
    };
    exigir(!(await publicos()).some((x) => x.id === creado.comentario), 'FALLA DE SEGURIDAD: un comentario pendiente es visible al público');
    const directo = await c.publica('/rest/v1/comentarios?select=id');
    exigir(!directo.ok || (directo.json ?? []).length === 0, 'FALLA DE SEGURIDAD: anon puede leer la tabla comentarios');
    paso('el comentario pendiente no es visible al público (ni por función ni por tabla)');

    // 5. moderación: moderador temporal -> aprobar -> visible
    const mod = await c.servicio('/rest/v1/moderadores', { metodo: 'POST', cuerpo: { user_id: creado.usuario } });
    exigir(mod.ok, `no se pudo promover a moderador (${mod.status}): ${mod.texto}`);
    const ap = await c.publica('/rest/v1/rpc/moderar_comentario', { metodo: 'POST', token, cuerpo: { p_id: creado.comentario, p_estado: 'aprobado', p_motivo: null } });
    exigir(ap.ok, `moderar_comentario falló (${ap.status}): ${ap.texto}`);
    const visible = (await publicos()).find((x) => x.id === creado.comentario);
    exigir(visible, 'el comentario aprobado no aparece en comentarios_aprobados()');
    exigir(!('user_id' in visible) && !JSON.stringify(visible).includes(correo), 'el comentario público expone identidad');
    paso('aprobado por moderador temporal: ahora es visible, sin identidad');
  } catch (e) {
    errores.push(e);
  } finally {
    // 6. limpieza: siempre, cada paso por separado
    const uid = creado.usuario;
    if (uid) {
      const borrar = async (nombre, ruta) => {
        try {
          const r = await c.servicio(ruta, { metodo: 'DELETE' });
          if (!r.ok) throw new Error(`${r.status} ${r.texto}`);
          log(`ok   limpieza: ${nombre}`);
        } catch (e) { errores.push(new Error(`limpieza de ${nombre} falló: ${c.redactar(e.message)}`)); }
      };
      await borrar('comentarios', `/rest/v1/comentarios?user_id=eq.${uid}`);
      await borrar('valoraciones', `/rest/v1/valoraciones?user_id=eq.${uid}`);
      await borrar('perfil', `/rest/v1/perfiles?user_id=eq.${uid}`);
      await borrar('moderador temporal', `/rest/v1/moderadores?user_id=eq.${uid}`);
      await borrar('usuario', `/auth/v1/admin/users/${uid}`);
      if (errores.some((e) => /^limpieza/.test(e.message))) log(`ATENCION: borrar a mano al usuario ${correo} (id ${uid}) en Supabase > Authentication.`);
    }
  }
  if (errores.length) { const e = errores[0]; e.todos = errores; throw e; }
  return { tarea: tarea.id, pasos, usuario_prueba: correo };
}

// ---------------------------------------------------------------- interfaz (opcional, --url)
async function uiChrome(urlBase, { rutaTarea, correo, clave, comentario }) {
  const { chromium } = await import('playwright-core');
  const { chromeExe } = await import('./chrome.mjs');
  const base = urlBase.replace(/\/+$/, '/');
  const browser = await chromium.launch({ executablePath: chromeExe(), headless: true, args: ['--no-sandbox'] });
  try {
    const p = await (await browser.newContext({ locale: 'es-CL' })).newPage();
    const errs = []; p.on('pageerror', (e) => errs.push(String(e)));
    await p.goto(base + 'cuenta/');
    if (await p.locator('#c-nodisp:not([hidden])').count()) throw new Error('el sitio publicado se construyó sin Supabase (cuentas no habilitadas)');
    await p.fill('#f-ingresar [name=email]', correo);
    await p.fill('#f-ingresar [name=password]', clave);
    await p.click('#f-ingresar button[type=submit]');
    await p.waitForSelector('#c-sesion:not([hidden])', { timeout: 20000 });
    await p.goto(base + rutaTarea.replace(/^\//, '') + '#comentarios');
    await p.waitForSelector('#op-campos:not([disabled])', { timeout: 20000 });
    await p.click('label[for=p4]');
    await p.fill('[name=texto]', comentario);
    await p.check('[name=aviso]');
    await p.click('#form-opinion button[type=submit]');
    await p.waitForFunction(() => /moderación/.test(document.getElementById('op-mensaje').textContent), null, { timeout: 20000 });
    if (errs.length) throw new Error('errores de JavaScript en la página: ' + errs.join(' | ').slice(0, 300));
  } finally { await browser.close(); }
}

// ---------------------------------------------------------------- CLI
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const i = process.argv.indexOf('--url');
  const urlPublica = i > 0 ? process.argv[i + 1] : null;
  try {
    const tarea = tareaDelCatalogo();
    const r = await verificarStaging({ tarea, ui: urlPublica ? (d) => uiChrome(urlPublica, d) : null });
    console.log(`\nStaging OK (${r.pasos.length} comprobaciones; tarea ${r.tarea}; usuario de prueba borrado).`);
  } catch (e) {
    console.error(`\nSTAGING FALLÓ: ${e.message}`);
    process.exitCode = e instanceof MigracionesNoAplicadas ? 2 : e instanceof FaltanVariables ? 3 : 1;
  }
}
