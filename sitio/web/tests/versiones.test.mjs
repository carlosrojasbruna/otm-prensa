// (b) Versiones anteriores y degradación con catálogo 1.0, con catálogos fixture (no toca tareas/).
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { construir, leerHtml, hrefs, textoDe, FIXTURES } from './helpers.mjs';

const d11 = construir({ outDir: 'dist-test-v11', raiz: path.join(FIXTURES, 'v11') });
const d10 = construir({ outDir: 'dist-test-v10', raiz: path.join(FIXTURES, 'v10') });

test('(b) catálogo 1.1: la versión vigente y sus versiones anteriores se listan con sus archivos', () => {
  const html = leerHtml(d11, 'tareas/2026-09/prueba-uno');
  const txt = textoDe(html);
  assert.match(txt, /Versión vigente: v2/);
  const bloque = /<ul class="traza" id="versiones-anteriores">([\s\S]*?)<\/ul>/.exec(html)?.[1];
  assert.ok(bloque, 'lista de versiones anteriores');
  assert.match(textoDe(bloque), /v1 · 2026-09-20 · commit 1234567890ab/);
  const links = hrefs(bloque);
  assert.deepEqual(links.map((l) => path.basename(l.href)).sort(),
    ['guia_v1.0_2026-09-20.json', 'tarea_v1.0_2026-09-20.json', 'tarea_v1.0_2026-09-20.md']);
  for (const l of links) assert.ok(fs.existsSync(path.join(d11, l.href.replace(/^\//, ''))), `no existe ${l.href}`);
});

test('(b) tarea sin versiones anteriores y sin guía en Markdown degrada con elegancia', () => {
  const html = leerHtml(d11, 'tareas/2026-09/prueba-dos');
  const txt = textoDe(html);
  assert.match(txt, /Esta es la primera versión/);
  assert.match(txt, /solo está disponible como archivo descargable/);
  const descargas = hrefs(html, (h) => /\bdownload\b/.test(h.tag)).map((h) => path.basename(h.href));
  assert.deepEqual(descargas.sort(), ['guia_v1.0_2026-09-25.json', 'tarea_v1.0_2026-09-25.json', 'tarea_v1.0_2026-09-25.md']);
});

test('(b) catálogo 1.0 sin tarea_md/guia_md: página con enunciado del JSON, sin enlaces rotos', () => {
  const html = leerHtml(d10, 'tareas/2026-08/antigua');
  const txt = textoDe(html);
  assert.match(txt, /Enunciado de una tarea con catálogo 1\.0/);
  assert.match(txt, /v1 · 2026-08-01 · commit aaaaaaa/);
  for (const { href } of hrefs(html, (h) => /\bdownload\b/.test(h.tag))) {
    assert.ok(fs.existsSync(path.join(d10, href.replace(/^\//, ''))), `no existe ${href}`);
  }
});

test('home y explorar funcionan con 2 tareas (orden por fecha, hero = la más reciente)', () => {
  const home = leerHtml(d11, '');
  assert.match(/<h1 id="hero-titulo">([\s\S]*?)<\/h1>/.exec(home)[1].replace(/<[^>]+>/g, ''), /Tarea de prueba uno/);
  const exp = leerHtml(d11, 'explorar');
  const ids = [...exp.matchAll(/data-id="([^"]+)"/g)].map((m) => m[1]);
  assert.deepEqual(ids, ['2026-09-prueba-uno', '2026-09-prueba-dos']);
  assert.ok(fs.existsSync(path.join(d11, 'tareas/2026-09/prueba-uno/archivos/icono_v2.0_2026-09-30.svg')));
});

test('el título de la noticia se cita completo, con sus caracteres especiales', () => {
  const txt = textoDe(leerHtml(d11, 'tareas/2026-09/prueba-uno'));
  assert.ok(txt.includes('Titular de prueba completo, con coma y comillas «especiales»'));
});
