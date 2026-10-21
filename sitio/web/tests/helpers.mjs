// Utilidades de las pruebas: construir el sitio con distintas configuraciones y leer su salida.
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

export const WEB = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const REPO = path.resolve(WEB, '..', '..');
export const FIXTURES = path.join(WEB, 'tests', 'fixtures');
const astroBin = path.join(WEB, '..', 'node_modules', 'astro', 'bin', 'astro.mjs');

/** Construye el sitio en `outDir` (relativo a sitio/web) con las variables indicadas. */
export function construir({ outDir, raiz = REPO, env = {} }) {
  const destino = path.join(WEB, outDir);
  fs.rmSync(destino, { recursive: true, force: true });
  const r = spawnSync(process.execPath, [astroBin, 'build'], {
    cwd: WEB, encoding: 'utf8',
    env: { ...process.env, OTM_OUT_DIR: outDir, OTM_REPO_ROOT: raiz, ...env },
  });
  if (r.status !== 0) throw new Error(`astro build falló (${outDir}):\n${r.stdout}\n${r.stderr}`);
  return destino;
}

export const leerHtml = (dist, ruta) => fs.readFileSync(path.join(dist, ruta, 'index.html'), 'utf8');

export function hrefs(html, filtro = () => true) {
  return [...html.matchAll(/<a\b[^>]*\bhref="([^"]+)"[^>]*>/g)].map((m) => ({ href: m[1], tag: m[0] })).filter(filtro);
}

/** Texto visible aproximado de un fragmento HTML. */
export function textoDe(html) {
  return html
    .replace(/<(script|style)[\s\S]*?<\/\1>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ').trim();
}

export function catalogoDe(raiz = REPO) {
  return JSON.parse(fs.readFileSync(path.join(raiz, 'tareas', 'catalogo.json'), 'utf8'));
}
