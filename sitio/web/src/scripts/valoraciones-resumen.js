// Hidrata los promedios de valoración (home, explorar, tarea). Sin backend, deja el texto estático.
import { backend, MODO, num, textoEstrellas } from './cliente.js';

export async function hidratarResumenes() {
  if (MODO === 'none') return null;
  const nodos = document.querySelectorAll('[data-resumen]');
  if (!nodos.length) return null;
  let datos;
  try { datos = await (await backend()).resumenes(); } catch { return null; }
  for (const el of nodos) {
    const r = datos[el.dataset.resumen];
    el.dataset.n = r?.n ?? 0;
    el.dataset.promedio = r?.promedio ?? 0;
    if (!r || !r.n) continue;
    const est = el.querySelector('.estrellas');
    if (est) { est.innerHTML = textoEstrellas(r.promedio); est.setAttribute('aria-hidden', 'true'); }
    const txt = el.querySelector('.valoracion-txt');
    if (txt) txt.textContent = `${num(r.promedio)} · ${r.n} ${r.n === 1 ? 'valoración' : 'valoraciones'}`;
  }
  return datos;
}
