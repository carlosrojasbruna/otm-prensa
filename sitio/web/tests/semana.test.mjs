// Regla de «Tarea de la semana» con fixtures sintéticos (no toca tareas/).
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { elegirTareaSemana } from '../src/lib/semana.js';
import { construir, leerHtml, FIXTURES } from './helpers.mjs';

const fx = JSON.parse(fs.readFileSync(path.join(FIXTURES, 'semana', 'tareas.json'), 'utf8'));
const por = (...ids) => fx.filter((t) => ids.includes(t.id));
const sinGit = { fechaCommit: () => null, hoy: '2026-10-20' };
const id = (r) => r.tarea.id;

test('mayor RUB01 gana aunque sea más antigua', () => {
  const r = elegirTareaSemana(por('a-22-nueva', 'b-24-vieja', 'c-23-media'), null, sinGit);
  assert.equal(id(r), 'b-24-vieja');
  assert.equal(r.criterio, 'mayor RUB01');
});

test('empate de RUB01: gana la de fecha_publicacion más reciente', () => {
  const r = elegirTareaSemana(por('b-24-vieja', 'd-24-reciente'), null, sinGit);
  assert.equal(id(r), 'd-24-reciente');
  assert.match(r.criterio, /fecha/);
});

test('empate de RUB01 y fecha: gana el commit de publicación más reciente', () => {
  const fechas = { aaa: '2026-10-20T10:00:00.000Z', bbb: '2026-10-20T12:00:00.000Z' };
  const r = elegirTareaSemana(por('e-24-mismo-dia-1', 'f-24-mismo-dia-2'), null, { hoy: '2026-10-20', fechaCommit: (c) => fechas[c] });
  assert.equal(id(r), 'f-24-mismo-dia-2');
  assert.match(r.criterio, /commit/);
});

test('empate total sin git: desempata por id y es independiente del orden de entrada', () => {
  const a = elegirTareaSemana(por('e-24-mismo-dia-1', 'f-24-mismo-dia-2'), null, sinGit);
  const b = elegirTareaSemana(por('f-24-mismo-dia-2', 'e-24-mismo-dia-1'), null, sinGit);
  assert.equal(id(a), 'e-24-mismo-dia-1');
  assert.equal(id(b), id(a));
  assert.equal(a.criterio, 'desempate por id');
});

test('fijación válida gana a la regla', () => {
  const cfg = { fijada: 'a-22-nueva', fijada_por: 'Carlos Rojas Bruna', fecha: '2026-10-20', hasta: '2026-10-27', motivo: 'prueba' };
  const r = elegirTareaSemana(fx, cfg, sinGit);
  assert.equal(id(r), 'a-22-nueva');
  assert.equal(r.criterio, 'fijada por el moderador');
  assert.deepEqual(r.avisos, []);
});

test('fijación sin vencimiento (hasta null) sigue vigente; el último día es inclusivo', () => {
  assert.equal(id(elegirTareaSemana(fx, { fijada: 'a-22-nueva', hasta: null }, sinGit)), 'a-22-nueva');
  assert.equal(id(elegirTareaSemana(fx, { fijada: 'a-22-nueva', hasta: '2026-10-20' }, sinGit)), 'a-22-nueva');
});

test('fijación a un id inexistente se ignora con aviso', () => {
  const r = elegirTareaSemana(fx, { fijada: 'no-existe', hasta: null }, sinGit);
  assert.notEqual(id(r), 'no-existe');
  assert.equal(id(r), elegirTareaSemana(fx, null, sinGit).tarea.id);
  assert.equal(r.avisos.length, 1);
  assert.match(r.avisos[0], /no existe/);
});

test('fijación vencida se ignora con aviso', () => {
  const r = elegirTareaSemana(fx, { fijada: 'a-22-nueva', hasta: '2026-10-19' }, sinGit);
  assert.notEqual(id(r), 'a-22-nueva');
  assert.equal(r.avisos.length, 1);
  assert.match(r.avisos[0], /venció/);
});

test('catálogo vacío no falla', () => {
  assert.equal(elegirTareaSemana([], { fijada: 'x' }, sinGit).tarea, null);
});

test('la home construida elige por mayor RUB01 (fixture v11, sin fijación)', () => {
  const dist = construir({ outDir: 'dist-test-semana', raiz: path.join(FIXTURES, 'v11') });
  const h1 = /<h1 id="hero-titulo">([\s\S]*?)<\/h1>/.exec(leerHtml(dist, ''))[1].replace(/<[^>]+>/g, '');
  assert.match(h1, /Tarea de prueba uno/); // fixture v11: uno tiene RUB01 22 y dos tiene 21
});
