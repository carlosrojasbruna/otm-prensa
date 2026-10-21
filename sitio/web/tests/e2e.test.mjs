// (c) e2e: crear cuenta -> valorar -> comentar -> no visible hasta moderar -> moderar -> visible,
//     contra el backend local simulado, en Chrome headless (el ya instalado; no se descarga nada).
// (d) el aviso de uso de datos está en los formularios de valoración/comentario y de perfil.
import test, { before, after } from 'node:test';
import assert from 'node:assert/strict';
import { chromium } from 'playwright-core';
import { crearServidorLocal } from '../../api/src/local/server.mjs';
import { AVISO_USO_DATOS } from '../../api/src/comun.js';
import { chromeExe } from '../scripts/chrome.mjs';
import { construir, catalogoDe } from './helpers.mjs';

const dist = construir({ outDir: 'dist-e2e', env: { PUBLIC_BACKEND: 'local', PUBLIC_LOCAL_API_URL: '' } });
const tarea = catalogoDe().tareas.sort((a, b) => b.fecha_publicacion.localeCompare(a.fecha_publicacion) || b.rub01_total - a.rub01_total || a.id.localeCompare(b.id))[0];
const rutaTarea = `/${tarea.ruta}`;
const COMENTARIO = 'Comentario e2e: los grupos se trabaron al elegir el supuesto de partida.';

let srv, browser, URL_BASE;
before(async () => {
  srv = crearServidorLocal({ estatico: dist, moderadores: ['mod@ejemplo.cl'] });
  await new Promise((r) => srv.listen(0, '127.0.0.1', r));
  URL_BASE = `http://127.0.0.1:${srv.address().port}`;
  browser = await chromium.launch({ executablePath: chromeExe(), headless: true });
});
after(async () => { await browser?.close(); srv?.close(); });

async function contexto() {
  const ctx = await browser.newContext({ locale: 'es-CL' });
  const errores = [];
  ctx.on('page', (p) => p.on('pageerror', (e) => errores.push(String(e))));
  return { ctx, errores };
}

test('(d) el aviso de uso de datos está en el formulario de valoración/comentario y en los de cuenta y perfil', async () => {
  const { ctx } = await contexto();
  const p = await ctx.newPage();
  await p.goto(URL_BASE + rutaTarea);
  const aviso = await p.locator('#form-opinion [data-aviso-datos]').innerText();
  assert.ok(aviso.includes(AVISO_USO_DATOS), aviso);
  for (const palabra of ['anonimizada', 'investigación', 'moderación', 'editarlos o retirarlos']) assert.ok(aviso.includes(palabra), palabra);
  await p.goto(URL_BASE + '/cuenta/');
  // con el servicio local activo, el formulario de registro y el de perfil (oculto hasta iniciar sesión) llevan el aviso
  assert.ok((await p.locator('#f-registro [data-aviso-datos]').innerText()).includes(AVISO_USO_DATOS));
  assert.ok((await p.locator('#f-perfil [data-aviso-datos]').textContent()).includes(AVISO_USO_DATOS));
  // el envío exige aceptarlo
  await p.fill('#f-registro [name=email]', 'sinaviso@ejemplo.cl');
  await p.fill('#f-registro [name=password]', 'clave-segura-1');
  await p.click('#f-registro button[type=submit]');
  assert.match(await p.locator('#c-mensaje').innerText(), /aviso de uso de datos/);
  await ctx.close();
});

test('(c) flujo completo: cuenta -> valorar -> comentar -> pendiente (no visible) -> moderar -> visible', async () => {
  // 1. Docente anónima: ve la tarea, no puede valorar sin cuenta
  const doc = await contexto();
  const p = await doc.ctx.newPage();
  await p.goto(URL_BASE + rutaTarea);
  assert.equal(await p.locator('#form-opinion [name=texto]').isDisabled(), true);
  assert.match(await p.locator('#op-requiere').innerText(), /necesitas una cuenta/);

  // 2. Crea la cuenta y vuelve a la tarea
  await p.click('#secciones a[href="#comentarios"]');
  await p.click('#op-enlace-cuenta');
  await p.waitForURL('**/cuenta/**');
  await p.fill('#f-registro [name=email]', 'docente@ejemplo.cl');
  await p.fill('#f-registro [name=password]', 'clave-segura-1');
  await p.check('#f-registro [name=aviso]');
  await Promise.all([p.waitForURL('**' + rutaTarea), p.click('#f-registro button[type=submit]')]);

  // 3. Valora (4 estrellas) y comenta
  await p.click('#secciones a[href="#comentarios"]');
  await p.waitForSelector('#op-campos:not([disabled])');
  await p.click('label[for=p4]');
  await p.selectOption('[name=nivel]', 'S');
  await p.fill('[name=texto]', COMENTARIO);
  // sin aceptar el aviso no envía
  await p.click('#form-opinion button[type=submit]');
  assert.match(await p.locator('#op-mensaje').innerText(), /aviso de uso de datos/);
  await p.check('[name=aviso]');
  await p.click('#form-opinion button[type=submit]');
  await p.waitForFunction(() => /moderación/.test(document.getElementById('op-mensaje').textContent));
  assert.match(await p.locator('#mis-comentarios').innerText(), /En moderación/);
  assert.match(await p.locator('#bloque-valoracion .valoracion-txt').innerText(), /4 · 1 valoración/);

  // 4. Un visitante anónimo NO ve el comentario (pendiente), pero sí el promedio
  const vis = await contexto();
  const v = await vis.ctx.newPage();
  await v.goto(URL_BASE + rutaTarea + '#comentarios');
  await v.waitForFunction(() => /valoración/.test(document.querySelector('#bloque-valoracion .valoracion-txt').textContent));
  assert.ok(!(await v.locator('#lista-comentarios').innerText()).includes(COMENTARIO), 'pendiente no debe verse');
  assert.match(await v.locator('#lista-comentarios').innerText(), /Aún no hay comentarios publicados/);

  // 5. Una docente sin permisos no entra a moderar
  await p.goto(URL_BASE + '/moderacion/');
  await p.waitForFunction(() => document.getElementById('m-mensaje').textContent.length > 0);
  assert.match(await p.locator('#m-mensaje').innerText(), /no tiene permiso/);

  // 6. Moderadora aprueba
  const mod = await contexto();
  const m = await mod.ctx.newPage();
  await m.goto(URL_BASE + '/cuenta/');
  await m.fill('#f-registro [name=email]', 'mod@ejemplo.cl');
  await m.fill('#f-registro [name=password]', 'clave-segura-1');
  await m.check('#f-registro [name=aviso]');
  await Promise.all([m.waitForNavigation(), m.click('#f-registro button[type=submit]')]);
  await m.goto(URL_BASE + '/moderacion/');
  await m.waitForSelector('#m-lista .comentario');
  assert.match(await m.locator('#m-lista').innerText(), new RegExp(COMENTARIO.slice(0, 20)));
  await m.click('#m-lista [data-estado=aprobado]');
  await m.waitForFunction(() => /No hay comentarios pendientes/.test(document.getElementById('m-lista').textContent));

  // 7. Ahora el visitante sí lo ve, con rótulo anónimo (sin correo)
  await v.reload();
  await v.waitForFunction((t) => document.getElementById('lista-comentarios').textContent.includes(t), COMENTARIO);
  const publico = await v.locator('#lista-comentarios').innerText();
  assert.ok(publico.includes('Docente'));
  assert.ok(!publico.includes('docente@ejemplo.cl'));
  assert.match(await v.locator('#n-comentarios').innerText(), /\(1\)/);

  // 8. La home muestra el promedio hidratado
  await v.goto(URL_BASE + '/');
  await v.waitForFunction(() => [...document.querySelectorAll('[data-resumen] .valoracion-txt')].some((e) => /1 valoración/.test(e.textContent)));

  // 9. La docente edita su comentario: vuelve a moderación y deja de ser público
  await p.goto(URL_BASE + '/cuenta/');
  await p.waitForSelector('#c-mis .comentario');
  p.once('dialog', (d) => d.accept('Comentario editado por la docente.'));
  await p.click('#c-mis [data-editar]');
  await p.waitForFunction(() => /En moderación/.test(document.getElementById('c-mis').textContent));
  await v.goto(URL_BASE + rutaTarea + '#comentarios');
  await v.waitForFunction(() => /valoración/.test(document.querySelector('#bloque-valoracion .valoracion-txt').textContent));
  assert.match(await v.locator('#lista-comentarios').innerText(), /Aún no hay comentarios publicados/);

  // 10. Perfil opcional: se guarda (con aviso) y se retira; luego retira todos sus datos
  await p.selectOption('#f-perfil [name=nivelEnsenanza]', 'S');
  await p.selectOption('#f-perfil [name=region]', 'Valparaíso');
  await p.fill('#f-perfil [name=aniosExperiencia]', '8');
  await p.click('#f-perfil button[type=submit]');
  assert.match(await p.locator('#p-mensaje').innerText(), /aviso de uso de datos/);
  await p.check('#f-perfil [name=aviso]');
  await p.click('#f-perfil button[type=submit]');
  await p.waitForFunction(() => /Perfil guardado/.test(document.getElementById('p-mensaje').textContent));
  await p.reload();
  await p.waitForSelector('#c-sesion:not([hidden])');
  assert.equal(await p.locator('#f-perfil [name=region]').inputValue(), 'Valparaíso');
  p.once('dialog', (d) => d.accept());
  await p.click('#b-retirar-todo');
  await p.waitForFunction(() => /datos fueron retirados/.test(document.getElementById('c-mensaje').textContent));
  await p.reload();
  await p.waitForSelector('#c-sesion:not([hidden])');
  assert.equal(await p.locator('#f-perfil [name=region]').inputValue(), '');
  assert.match(await p.locator('#c-mis').innerText(), /Aún no has valorado/);

  for (const c of [doc, vis, mod]) { assert.deepEqual(c.errores, [], 'errores de JavaScript en la página'); await c.ctx.close(); }
});

test('la navegación por teclado llega a los campos del formulario y la página declara es-CL', async () => {
  const { ctx } = await contexto();
  const p = await ctx.newPage();
  await p.goto(URL_BASE + rutaTarea);
  assert.equal(await p.getAttribute('html', 'lang'), 'es-CL');
  await p.keyboard.press('Tab');
  assert.equal(await p.evaluate(() => document.activeElement.className), 'saltar');
  await ctx.close();
});
