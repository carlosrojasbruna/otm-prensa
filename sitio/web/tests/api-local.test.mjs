// Semántica del backend local simulado (equivale a las políticas de sitio/db):
// cuenta requerida, comentarios pendientes invisibles, moderación solo moderadores,
// edición que vuelve a moderación, retiro de datos propios, perfil opcional.
import test, { before, after } from 'node:test';
import assert from 'node:assert/strict';
import { crearServidorLocal } from '../../api/src/local/server.mjs';

let srv, base;
before(async () => {
  srv = crearServidorLocal({ moderadores: ['mod@ejemplo.cl'] });
  await new Promise((r) => srv.listen(0, '127.0.0.1', r));
  base = `http://127.0.0.1:${srv.address().port}/api`;
});
after(() => srv.close());

async function llamar(m, ruta, cuerpo, token) {
  const r = await fetch(base + ruta, { method: m, headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }, body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo) });
  return { status: r.status, datos: r.status === 204 ? null : await r.json() };
}
async function cuenta(email) {
  const r = await llamar('POST', '/auth/registro', { email, password: 'clave-segura-1' });
  assert.equal(r.status, 201);
  return r.datos.token;
}
const T = '2026-10-prueba';

test('sin sesión no se puede valorar ni comentar; la lectura pública es libre', async () => {
  assert.equal((await llamar('PUT', `/valoraciones/${T}`, { version: 1, puntaje: 5 })).status, 401);
  assert.equal((await llamar('POST', '/comentarios', { tareaId: T, version: 1, texto: 'x', avisoAceptado: true })).status, 401);
  assert.equal((await llamar('GET', '/resumenes')).status, 200);
  assert.equal((await llamar('GET', `/tareas/${T}/comentarios`)).status, 200);
});

test('valoración 1-5, una por docente y tarea (la segunda actualiza), agregados públicos', async () => {
  const a = await cuenta('a@ejemplo.cl'); const b = await cuenta('b@ejemplo.cl');
  assert.equal((await llamar('PUT', `/valoraciones/${T}`, { version: 1, puntaje: 6 }, a)).status, 400);
  assert.equal((await llamar('PUT', `/valoraciones/${T}`, { version: 1, puntaje: 4 }, a)).status, 204);
  assert.equal((await llamar('PUT', `/valoraciones/${T}`, { version: 1, puntaje: 2 }, a)).status, 204);
  assert.equal((await llamar('PUT', `/valoraciones/${T}`, { version: 1, puntaje: 5 }, b)).status, 204);
  const r = (await llamar('GET', '/resumenes')).datos[T];
  assert.equal(r.n, 2);
  assert.equal(r.promedio, 3.5);
  assert.deepEqual(r.distribucion, [0, 1, 0, 0, 1]);
  assert.equal((await llamar('DELETE', `/valoraciones/${T}`, undefined, a)).status, 204);
  assert.equal((await llamar('GET', '/resumenes')).datos[T].n, 1);
});

test('comentario: exige aviso, nace pendiente, solo se ve tras aprobar; editar vuelve a moderación', async () => {
  const autor = await cuenta('autor@ejemplo.cl');
  const otro = await cuenta('otro@ejemplo.cl');
  const mod = await cuenta('mod@ejemplo.cl');
  assert.equal((await llamar('POST', '/comentarios', { tareaId: T, version: 1, texto: 'hola' }, autor)).status, 400);
  const c = await llamar('POST', '/comentarios', { tareaId: T, version: 1, texto: 'Funcionó bien', avisoAceptado: true }, autor);
  assert.equal(c.status, 201);
  assert.equal(c.datos.estado, 'pendiente');
  const id = c.datos.id;
  assert.equal((await llamar('GET', `/tareas/${T}/comentarios`)).datos.length, 0, 'pendiente no es público');
  // el autor lo ve con su estado; otro docente no puede tocarlo
  assert.equal((await llamar('GET', '/mis-datos', undefined, autor)).datos.comentarios[0].estado, 'pendiente');
  assert.equal((await llamar('PATCH', `/comentarios/${id}`, { texto: 'hack' }, otro)).status, 404);
  assert.equal((await llamar('DELETE', `/comentarios/${id}`, undefined, otro)).status, 404);
  // moderación: solo moderadores
  assert.equal((await llamar('GET', '/moderacion/pendientes', undefined, autor)).status, 403);
  assert.equal((await llamar('POST', `/moderacion/${id}`, { estado: 'aprobado' }, autor)).status, 403);
  assert.equal((await llamar('GET', '/moderacion/pendientes', undefined, mod)).datos.length, 1);
  assert.equal((await llamar('POST', `/moderacion/${id}`, { estado: 'aprobado' }, mod)).status, 204);
  const pub = (await llamar('GET', `/tareas/${T}/comentarios`)).datos;
  assert.equal(pub.length, 1);
  assert.equal(pub[0].texto, 'Funcionó bien');
  assert.ok(!('userId' in pub[0]) && !('email' in pub[0]), 'no expone identidad');
  // editar → vuelve a pendiente y deja de ser público
  assert.equal((await llamar('PATCH', `/comentarios/${id}`, { texto: 'Funcionó muy bien' }, autor)).status, 204);
  assert.equal((await llamar('GET', `/tareas/${T}/comentarios`)).datos.length, 0);
  // rechazar y retirar
  assert.equal((await llamar('POST', `/moderacion/${id}`, { estado: 'rechazado', motivo: 'prueba' }, mod)).status, 204);
  assert.equal((await llamar('GET', `/tareas/${T}/comentarios`)).datos.length, 0);
  assert.equal((await llamar('DELETE', `/comentarios/${id}`, undefined, autor)).status, 204);
  assert.equal((await llamar('GET', '/mis-datos', undefined, autor)).datos.comentarios.length, 0);
});

test('perfil opcional: se guarda con aviso, valida campos, se retira; retirar todo borra lo propio', async () => {
  const t = await cuenta('perfil@ejemplo.cl');
  assert.equal((await llamar('PUT', '/perfil', {}, t)).status, 400, 'sin aviso');
  assert.equal((await llamar('PUT', '/perfil', { avisoAceptado: true }, t)).status, 204, 'vacío es válido en el piloto');
  assert.equal((await llamar('PUT', '/perfil', { nivelEnsenanza: 'Z', avisoAceptado: true }, t)).status, 400);
  assert.equal((await llamar('PUT', '/perfil', { nivelEnsenanza: 'S', tipoEstablecimiento: 'municipal', region: 'Valparaíso', aniosExperiencia: 12, avisoAceptado: true }, t)).status, 204);
  assert.deepEqual((await llamar('GET', '/mis-datos', undefined, t)).datos.perfil,
    { nivelEnsenanza: 'S', tipoEstablecimiento: 'municipal', region: 'Valparaíso', aniosExperiencia: 12 });
  await llamar('PUT', `/valoraciones/${T}`, { version: 1, puntaje: 3 }, t);
  assert.equal((await llamar('DELETE', '/mis-datos', undefined, t)).status, 204);
  const d = (await llamar('GET', '/mis-datos', undefined, t)).datos;
  assert.equal(d.perfil, null); assert.equal(d.valoraciones.length, 0);
});

test('registro y login: correo único, contraseña mínima, credenciales incorrectas', async () => {
  assert.equal((await llamar('POST', '/auth/registro', { email: 'x@ejemplo.cl', password: 'corta' })).status, 400);
  await cuenta('dup@ejemplo.cl');
  assert.equal((await llamar('POST', '/auth/registro', { email: 'dup@ejemplo.cl', password: 'clave-segura-1' })).status, 409);
  assert.equal((await llamar('POST', '/auth/login', { email: 'dup@ejemplo.cl', password: 'otra-clave-123' })).status, 401);
  const ok = await llamar('POST', '/auth/login', { email: 'dup@ejemplo.cl', password: 'clave-segura-1' });
  assert.equal(ok.status, 200);
  assert.equal((await llamar('GET', '/sesion', undefined, ok.datos.token)).datos.usuario.email, 'dup@ejemplo.cl');
});
