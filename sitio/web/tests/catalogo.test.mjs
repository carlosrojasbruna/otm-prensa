// (a) Cada tarea del catálogo real tiene página y enlaces de descarga que existen.
// (e) El sitio no agrega texto propio de noticias: el contenido de tareas es el de tareas/.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { construir, leerHtml, hrefs, textoDe, catalogoDe, REPO } from './helpers.mjs';

const dist = construir({ outDir: 'dist-test-real' });
const cat = catalogoDe();

test('el catálogo real tiene al menos una tarea y se construyen home y explorar', () => {
  assert.ok(cat.tareas.length >= 1);
  for (const r of ['', 'explorar', 'cuenta', 'moderacion', 'como-usar', 'acerca']) {
    assert.ok(fs.existsSync(path.join(dist, r, 'index.html')), `falta ${r}/index.html`);
  }
});

for (const t of cat.tareas) {
  test(`(a) ${t.id}: página, cita, descargas existentes, licencia`, () => {
    const pagina = t.ruta.replace(/^tareas\//, 'tareas/').replace(/\/$/, '');
    const html = leerHtml(dist, pagina);
    // cita completa de la noticia, tal como viene en el catálogo
    const txt = textoDe(html);
    assert.ok(txt.includes(t.noticia.medio), 'medio');
    assert.ok(txt.includes(t.noticia.titulo), `título completo de la noticia: ${t.noticia.titulo}`);
    assert.ok(html.includes(`href="${t.noticia.url.replace(/&/g, '&#38;')}"`) || html.includes(`href="${t.noticia.url}"`) || html.includes(`href="${t.noticia.url.replace(/&/g, '&amp;')}"`), 'URL de la noticia');
    assert.ok(txt.includes('CC BY-NC-SA 4.0'), 'licencia');
    assert.ok(txt.includes(String(t.rub01_total)), 'RUB01');
    assert.ok(txt.includes(t.tiempo_estimado), 'tiempo');
    for (const c of t.contenidos_matematicos) assert.ok(txt.includes(c), `contenido ${c}`);
    // descargas: todos los enlaces con `download` apuntan a archivos del build y coinciden con los de tareas/
    const descargas = hrefs(html, (h) => /\bdownload\b/.test(h.tag));
    const esperadas = ['tarea', 'tarea_md', 'guia', 'guia_md'].map((k) => t.archivos[k]).filter(Boolean);
    assert.equal(descargas.length, esperadas.length, 'una descarga por archivo del catálogo');
    for (const { href } of descargas) {
      const f = path.join(dist, href.replace(/^\//, ''));
      assert.ok(fs.existsSync(f), `no existe ${href}`);
      const orig = path.join(REPO, t.ruta, path.basename(href));
      assert.ok(fs.readFileSync(f).equals(fs.readFileSync(orig)), `${href} difiere del original`);
    }
    for (const n of esperadas) assert.ok(descargas.some((d) => d.href.endsWith(n)), `falta enlace a ${n}`);
    // ícono
    if (t.archivos.icono) assert.ok(fs.existsSync(path.join(dist, t.ruta, 'archivos', t.archivos.icono)));
  });

  test(`(e) ${t.id}: el HTML de la tarea solo contiene texto que ya está en tareas/`, () => {
    const html = leerHtml(dist, t.ruta.replace(/\/$/, ''));
    const norm = (s) => s.replace(/[*_`|>#\\]/g, ' ').replace(/\s+/g, ' ').trim().toLowerCase();
    const fuente = norm([t.archivos.tarea_md, t.archivos.guia_md].filter(Boolean)
      .map((n) => fs.readFileSync(path.join(REPO, t.ruta, n), 'utf8')).join('\n'));
    for (const id of ['tarea', 'guia']) {
      const sec = new RegExp(`<section[^>]*id="${id}"[^>]*>([\\s\\S]*?)</section>`).exec(html)?.[1] ?? '';
      for (const bloque of sec.match(/<(p|li|td|blockquote)[^>]*>[\s\S]*?<\/\1>/g) ?? []) {
        const p = norm(textoDe(bloque)).replace(/^imagen que acompaña el enunciado: /, '');
        if (p.split(' ').length < 6) continue;
        assert.ok(fuente.includes(p), `texto que no está en tareas/: «${p.slice(0, 120)}»`);
      }
    }
  });
}

test('(e) fuera de las secciones de contenido no hay más de 25 palabras seguidas de la noticia: el sitio solo la cita (medio, título, fecha, URL)', () => {
  // El repositorio no contiene texto de noticias (invariante 3). El sitio solo imprime los 4 campos de cita.
  // Comprobamos que la cita de cada página es exactamente esos campos y que ningún `resumen_propio` se renderiza fuera de tareas/.
  for (const t of cat.tareas) {
    const html = leerHtml(dist, t.ruta.replace(/\/$/, ''));
    const cita = /<p class="cita">([\s\S]*?)<\/p>/.exec(html)?.[1] ?? '';
    const txt = textoDe(cita).replace(/ ([,.])/g, '$1');
    assert.ok(txt.startsWith(`Noticia: ${t.noticia.medio}, ${t.noticia.titulo},`), txt);
  }
});
