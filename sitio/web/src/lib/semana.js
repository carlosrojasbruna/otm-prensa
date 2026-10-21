// Regla de «Tarea de la semana» (decisión de Carlos, 2026-10-20), sin ids fijos.
//   1. Si el moderador fijó una tarea (src/config/tarea_semana.json) que existe en el catálogo
//      y no está vencida, gana esa.
//   2. Si no: entre las tareas del catálogo (todas están publicadas), la de mayor rub01_total.
//   3. Empate: mayor fecha_publicacion.
//   4. Empate: fecha del commit de publicación (campo `commit` de la entrada, consultado en git
//      en el build), la más reciente. Solo se usa si todas las empatadas la tienen.
//   5. Empate (o git no disponible): id en orden alfabético ascendente. Siempre determinista.
import { execFileSync } from 'node:child_process';

/** Fecha ISO del commit (cadena comparable) o null si git/historial no está disponible. */
export function fechaCommitGit(commit, cwd = process.cwd()) {
  if (!commit) return null;
  try {
    const s = execFileSync('git', ['log', '-1', '--format=%cI', commit], { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
    return s ? new Date(s).toISOString() : null;
  } catch { return null; }
}

const hoyIso = () => new Date().toISOString().slice(0, 10);

/**
 * @param {Array} tareas entradas del catálogo
 * @param {object|null} config contenido de tarea_semana.json
 * @param {{hoy?: string, fechaCommit?: (commit:string)=>string|null}} [opc]
 * @returns {{tarea: object|null, criterio: string, avisos: string[]}}
 */
export function elegirTareaSemana(tareas, config = null, opc = {}) {
  const hoy = opc.hoy || hoyIso();
  const fechaCommit = opc.fechaCommit || fechaCommitGit;
  const avisos = [];
  if (!tareas.length) return { tarea: null, criterio: 'sin tareas', avisos };

  if (config && config.fijada) {
    const t = tareas.find((x) => x.id === config.fijada);
    if (!t) avisos.push(`tarea_semana.json: «${config.fijada}» no existe en el catálogo; se ignora la fijación y se aplica la regla.`);
    else if (config.hasta && config.hasta < hoy) avisos.push(`tarea_semana.json: la fijación de «${config.fijada}» venció el ${config.hasta}; se ignora y se aplica la regla.`);
    else return { tarea: t, criterio: 'fijada por el moderador', avisos };
  }

  let c = tareas;
  const quedan = (clave, criterio, mejorEs) => {
    const vals = c.map(clave);
    if (vals.some((v) => v == null)) return false;
    const mejor = vals.reduce((a, b) => (mejorEs(b, a) ? b : a));
    c = c.filter((_, i) => vals[i] === mejor);
    return c.length === 1 ? criterio : false;
  };
  const pasos = [
    [(t) => t.rub01_total, 'mayor RUB01', (b, a) => b > a],
    [(t) => t.fecha_publicacion, 'publicada más recientemente (fecha)', (b, a) => b > a],
    [(t) => fechaCommit(t.commit), 'publicada más recientemente (commit en git)', (b, a) => b > a],
  ];
  for (const [clave, criterio, mejor] of pasos) {
    const r = quedan(clave, criterio, mejor);
    if (r) return { tarea: c[0], criterio: r, avisos };
  }
  c = [...c].sort((a, b) => a.id.localeCompare(b.id));
  return { tarea: c[0], criterio: c.length === 1 ? 'única' : 'desempate por id', avisos };
}
