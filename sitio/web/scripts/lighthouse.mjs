// Lighthouse sobre el build estático (home y una página de tarea), móvil y escritorio.
// Usa el Chrome ya instalado (CHROME_PATH); no descarga navegadores.
// Uso: npm run build && npm run lighthouse [-- --dir dist --umbral 90]
//      npm run lighthouse -- --url https://carlosrojasbruna.github.io/otm-prensa/   (sitio publicado: no usa dist/)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { launch } from 'chrome-launcher';
import lighthouse from 'lighthouse';
import { crearServidorLocal } from '../../api/src/local/server.mjs';
import { chromeExe } from './chrome.mjs';

const aqui = path.dirname(fileURLToPath(import.meta.url));
const web = path.resolve(aqui, '..');
const arg = (n, d) => { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : d; };
const dir = path.resolve(web, arg('dir', 'dist'));
const umbral = Number(arg('umbral', 90));
const urlPublica = arg('url', null);
const salida = path.join(web, urlPublica ? 'lighthouse-publico' : 'lighthouse');
fs.mkdirSync(salida, { recursive: true });

// Páginas: home y una página de tarea (la primera del build, o la más reciente del catálogo con --url).
function primeraTarea() {
  if (urlPublica) {
    const cat = JSON.parse(fs.readFileSync(path.resolve(web, '..', '..', 'tareas', 'catalogo.json'), 'utf8'));
    const t = [...cat.tareas].sort((a, b) => b.fecha_publicacion.localeCompare(a.fecha_publicacion) || a.id.localeCompare(b.id))[0];
    return `/${t.ruta}`;
  }
  const base = path.join(dir, 'tareas');
  for (const mes of fs.readdirSync(base)) {
    for (const slug of fs.readdirSync(path.join(base, mes))) {
      if (fs.existsSync(path.join(base, mes, slug, 'index.html'))) return `/tareas/${mes}/${slug}/`;
    }
  }
  throw new Error('No hay páginas de tarea en el build');
}
const paginas = { home: '/', tarea: primeraTarea() };

// Origen: servidor local sobre dist/, o la URL pública (con su subruta, p. ej. /otm-prensa/).
let servidor = null, origen, prefijo = '';
if (urlPublica) {
  const u = new URL(urlPublica);
  origen = u.origin; prefijo = u.pathname.replace(/\/+$/, '');
} else {
  servidor = crearServidorLocal({ estatico: dir });
  await new Promise((r) => servidor.listen(0, '127.0.0.1', r));
  origen = `http://127.0.0.1:${servidor.address().port}`;
}
const direccion = (ruta) => origen + prefijo + ruta;

const chrome = await launch({ chromePath: chromeExe(), chromeFlags: ['--headless=new', '--no-sandbox', '--disable-gpu'] });
const categorias = ['performance', 'accessibility', 'best-practices', 'seo'];
const resumen = { fecha: new Date().toISOString(), umbral, url: urlPublica, chrome: chromeExe(), resultados: [] };
let falla = false;

try {
  for (const [nombre, ruta] of Object.entries(paginas)) {
    for (const preset of ['mobile', 'desktop']) {
      const opciones = { port: chrome.port, output: 'json', logLevel: 'error', onlyCategories: categorias };
      const config = preset === 'desktop' ? (await import('lighthouse/core/config/desktop-config.js')).default : undefined;
      const r = await lighthouse(direccion(ruta), opciones, config);
      fs.writeFileSync(path.join(salida, `${nombre}-${preset}.json`), r.report);
      const notas = Object.fromEntries(categorias.map((c) => [c, Math.round(r.lhr.categories[c].score * 100)]));
      const m = r.lhr.audits;
      resumen.resultados.push({ pagina: nombre, ruta, preset, notas, lcp_ms: Math.round(m['largest-contentful-paint'].numericValue), cls: Number(m['cumulative-layout-shift'].numericValue.toFixed(3)), tbt_ms: Math.round(m['total-blocking-time'].numericValue) });
      const bajo = Object.entries(notas).filter(([, v]) => v < umbral);
      if (bajo.length) falla = true;
      console.log(`${nombre.padEnd(6)} ${preset.padEnd(8)} ${direccion(ruta)}  ` + categorias.map((c) => `${c}=${notas[c]}`).join('  ') + (bajo.length ? '  << BAJO UMBRAL' : ''));
    }
  }
} finally {
  await chrome.kill();
  servidor?.close();
}
fs.writeFileSync(path.join(salida, 'resumen.json'), JSON.stringify(resumen, null, 2) + '\n');
console.log(`\nResumen: ${path.join(salida, 'resumen.json')}  (umbral ${umbral})`);
process.exit(falla ? 1 : 0);
