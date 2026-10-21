// Sirve, tal cual, los archivos de cada tarea (md, json, svg) desde tareas/<ruta>/.
import fs from 'node:fs';
import { cargarCatalogo, rutaArchivoEnDisco, todosLosArchivos } from '../../../../../lib/catalogo.js';

export function getStaticPaths() {
  return cargarCatalogo().tareas.flatMap((t) =>
    todosLosArchivos(t).map((archivo) => ({ params: { mes: t.mes, slug: t.slug, archivo }, props: { ruta: rutaArchivoEnDisco(t, archivo) } })));
}

const TIPOS: Record<string, string> = {
  '.md': 'text/markdown; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
};

export function GET({ params, props }: { params: { archivo: string }; props: { ruta: string } }) {
  const ext = params.archivo.slice(params.archivo.lastIndexOf('.'));
  return new Response(fs.readFileSync(props.ruta), { headers: { 'Content-Type': TIPOS[ext] ?? 'application/octet-stream' } });
}
