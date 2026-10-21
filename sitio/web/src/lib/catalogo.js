// Lectura del catálogo y de los archivos de cada tarea, en tiempo de construcción.
// Fuente: <raíz>/tareas/catalogo.json (contrato catalogo.schema.json v1.0/v1.1) y <raíz>/<ruta>/*.
// No se codifica ningún id: todo sale del catálogo. No se agrega texto de noticias.
import fs from 'node:fs';
import path from 'node:path';
import { marked } from 'marked';

export const RAIZ = path.resolve(process.env.OTM_REPO_ROOT || path.join(process.cwd(), '..', '..'));

export const AREAS = {
  medio_ambiente: 'Medio ambiente',
  economia: 'Economía',
  salud: 'Salud',
  ciencia_tecnologia: 'Ciencia y tecnología',
  deporte: 'Deporte',
  transporte_ciudad: 'Transporte y ciudad',
  sociedad_datos: 'Sociedad y datos',
};

// Niveles MAR03 v1.0. Colores de chip tomados de make_home.py (LEVEL).
export const NIVEL_INFO = {
  P: { corto: 'P', edad: '10–12', largo: 'P · primaria (10–12 años)', fondo: '#fef3c7', texto: '#b45309' },
  S: { corto: 'S', edad: '13–18', largo: 'S · secundaria (13–18 años)', fondo: '#dcfce7', texto: '#15803d' },
  S1: { corto: 'S1', edad: '13–15', largo: 'S1 · 13–15 años', fondo: '#dcfce7', texto: '#15803d' },
  S2: { corto: 'S2', edad: '16–18', largo: 'S2 · 16–18 años', fondo: '#ede9fe', texto: '#6d28d9' },
  U: { corto: 'U', edad: '18–20', largo: 'U · universitario (18–20 años)', fondo: '#dbeafe', texto: '#1d4ed8' },
};

export function nivelDe(entrada) {
  return NIVEL_INFO[entrada.sub_tramo] || NIVEL_INFO[entrada.nivel_principal] || NIVEL_INFO.S;
}

export function fechaLarga(iso) {
  const [a, m, d] = iso.split('-').map(Number);
  const meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  return `${d} ${meses[m - 1]} ${a}`;
}

/** Semana ISO 8601 de una fecha AAAA-MM-DD. */
export function semanaIso(iso) {
  const [a, m, d] = iso.split('-').map(Number);
  const f = new Date(Date.UTC(a, m - 1, d));
  const dia = f.getUTCDay() || 7;
  f.setUTCDate(f.getUTCDate() + 4 - dia);
  const ini = new Date(Date.UTC(f.getUTCFullYear(), 0, 1));
  return { semana: Math.ceil(((f - ini) / 86400000 + 1) / 7), anio: f.getUTCFullYear() };
}

function leer(ruta) {
  try { return fs.readFileSync(ruta, 'utf8'); } catch { return null; }
}

// ---------------------------------------------------------------- markdown
const ENT = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ENT[c]);

/**
 * Prepara el .md de PLT01/PLT02 para mostrarlo: quita el h1 (la página ya lo muestra),
 * quita el bloque yaml de frontmatter (los datos se muestran estructurados) y convierte
 * los bloques `text enunciado_es` / `text foto_descripcion` en citas.
 */
export function prepararMarkdown(md) {
  let t = md.replace(/\r\n/g, '\n');
  t = t.replace(/^# .*\n+/, '');
  t = t.replace(/```yaml frontmatter\n[\s\S]*?\n```\n*/g, '');
  t = t.replace(/```text enunciado_es\n([\s\S]*?)\n```/g, (_, c) => c.split('\n').map((l) => `> ${l}`).join('\n'));
  t = t.replace(/```text foto_descripcion\n([\s\S]*?)\n```/g, (_, c) => `> *Imagen que acompaña el enunciado:* ${c.replace(/\n/g, ' ')}`);
  return t;
}

const renderer = new marked.Renderer();
renderer.heading = function ({ tokens, depth }) {
  const nivel = Math.min(depth + 1, 6); // el h1 es el título de la tarea; los títulos del markdown parten en h3
  return `<h${nivel}>${this.parser.parseInline(tokens)}</h${nivel}>\n`;
};
renderer.html = ({ text }) => esc(text);
renderer.table = function (token) {
  const base = marked.Renderer.prototype.table.call(this, token);
  return `<div class="tabla-scroll" tabindex="0" role="region" aria-label="Tabla desplazable">${base}</div>\n`;
};
renderer.link = function ({ href, tokens }) {
  const ext = /^https?:/i.test(href);
  return `<a href="${esc(href)}"${ext ? ' rel="noopener noreferrer"' : ''}>${this.parser.parseInline(tokens)}</a>`;
};

export function renderMarkdown(md) {
  return marked.parse(prepararMarkdown(md), { renderer, gfm: true, async: false });
}

// ------------------------------------------------------------------ catálogo
function dirDe(ruta) {
  return path.join(RAIZ, ruta);
}

/** Resuelve los archivos de una versión: solo los que existen en disco. */
function resolverArchivos(ruta, archivos = {}) {
  const dir = dirDe(ruta);
  const out = {};
  for (const [clave, nombre] of Object.entries(archivos)) {
    if (typeof nombre === 'string' && fs.existsSync(path.join(dir, nombre))) out[clave] = nombre;
  }
  return out;
}

export function cargarCatalogo() {
  const crudo = leer(path.join(RAIZ, 'tareas', 'catalogo.json'));
  if (crudo === null) throw new Error(`No se encontró ${path.join(RAIZ, 'tareas', 'catalogo.json')}`);
  const cat = JSON.parse(crudo);
  if (!['1.0', '1.1'].includes(cat.version_contrato)) throw new Error(`version_contrato no soportada: ${cat.version_contrato}`);

  const tareas = cat.tareas.map((e) => {
    const [, mes, slug] = /^tareas\/([0-9]{4}-[0-9]{2})\/([^/]+)\/$/.exec(e.ruta) || [];
    if (!slug) throw new Error(`ruta inválida en ${e.id}: ${e.ruta}`);
    const archivos = resolverArchivos(e.ruta, e.archivos);
    const anteriores = (e.versiones_anteriores || [])
      .map((v) => ({ ...v, archivos: resolverArchivos(e.ruta, v.archivos) }))
      .sort((a, b) => b.version - a.version);
    return { ...e, mes, slug, archivos, versiones_anteriores: anteriores, url: `tareas/${mes}/${slug}/` };
  });

  // Orden por defecto: más reciente primero; empate por puntaje RUB01 y luego por id (determinista).
  tareas.sort((a, b) =>
    b.fecha_publicacion.localeCompare(a.fecha_publicacion) || b.rub01_total - a.rub01_total || a.id.localeCompare(b.id));
  return { version_contrato: cat.version_contrato, actualizado: cat.actualizado, tareas };
}

/** Contenido de una tarea: HTML de tarea_md y guia_md, enunciado del JSON como alternativa, ícono. */
export function cargarContenido(t) {
  const dir = dirDe(t.ruta);
  const md = (n) => (n ? leer(path.join(dir, n)) : null);
  const tareaMd = md(t.archivos.tarea_md);
  const guiaMd = md(t.archivos.guia_md);
  let enunciado = null;
  if (!tareaMd && t.archivos.tarea) {
    try { enunciado = JSON.parse(leer(path.join(dir, t.archivos.tarea)))?.estudiante?.enunciado_es ?? null; } catch { /* sin enunciado */ }
  }
  let iconoAlt = '';
  if (t.archivos.icono) {
    const svg = leer(path.join(dir, t.archivos.icono)) || '';
    iconoAlt = /<title>([^<]*)<\/title>/.exec(svg)?.[1] ?? '';
  }
  return {
    tareaHtml: tareaMd ? renderMarkdown(tareaMd) : null,
    guiaHtml: guiaMd ? renderMarkdown(guiaMd) : null,
    enunciado,
    iconoAlt,
  };
}

/** Ruta pública (relativa a la base) de un archivo de una tarea. */
export function urlArchivo(t, nombre) {
  return `tareas/${t.mes}/${t.slug}/archivos/${nombre}`;
}

export function rutaArchivoEnDisco(t, nombre) {
  return path.join(dirDe(t.ruta), nombre);
}

/** Todos los archivos publicables (versión vigente + anteriores) con su nombre. */
export function todosLosArchivos(t) {
  const set = new Set();
  const agregar = (a) => { for (const [k, n] of Object.entries(a || {})) if (k !== 'trazas' && k !== 'evaluacion') set.add(n); };
  agregar(t.archivos);
  for (const v of t.versiones_anteriores) agregar(v.archivos);
  return [...set];
}

export function relacionadas(todas, t, max = 4) {
  return todas
    .filter((x) => x.id !== t.id)
    .map((x) => ({ x, p: (x.area === t.area ? 2 : 0) + (x.nivel_principal === t.nivel_principal ? 1 : 0) + x.contenidos_matematicos.filter((c) => t.contenidos_matematicos.includes(c)).length }))
    .sort((a, b) => b.p - a.p)
    .slice(0, max)
    .map((r) => r.x);
}
