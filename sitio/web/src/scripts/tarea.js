// Página de tarea: secciones con pestañas (mejora progresiva), valoración y comentarios.
import { backend, MODO, esc, mensajeDe } from './cliente.js';
import { ETIQUETA_ESTADO } from 'otm-api';
import { hidratarResumenes } from './valoraciones-resumen.js';

const $ = (id) => document.getElementById(id);

// ---- secciones: sin JS se ven todas; con JS se muestra una a la vez según el hash
const SECCIONES = ['tarea', 'guia', 'comentarios'];
const enlaces = [...document.querySelectorAll('#secciones a')];
function mostrar(id) {
  if (!SECCIONES.includes(id)) id = 'tarea';
  for (const s of SECCIONES) $(s).hidden = s !== id;
  for (const a of enlaces) a.setAttribute('aria-current', String(a.getAttribute('href') === `#${id}`));
}
function desdeHash() {
  const id = location.hash.slice(1);
  mostrar(SECCIONES.includes(id) ? id : 'tarea');
}
window.addEventListener('hashchange', desdeHash);
for (const a of document.querySelectorAll('a[href="#comentarios"]')) {
  a.addEventListener('click', () => mostrar('comentarios'));
}
desdeHash();

// ---- valoración y comentarios
const form = $('form-opinion');
const tareaId = form.dataset.tareaId;
const version = Number(form.dataset.version);
const msg = $('op-mensaje');
function aviso(tipo, texto) {
  msg.hidden = false;
  msg.className = `mensaje ${tipo}`;
  msg.textContent = texto;
}

{
  const enlace = $('op-enlace-cuenta');
  enlace.setAttribute('href', `${enlace.getAttribute('href')}?volver=${encodeURIComponent(location.pathname)}`);
}

async function pintarComentarios(b) {
  let lista = [];
  try { lista = await b.comentariosPublicos(tareaId); } catch { /* sin servicio */ }
  const cont = $('lista-comentarios');
  $('n-comentarios').textContent = lista.length ? `(${lista.length})` : '';
  if (!lista.length) { cont.innerHTML = '<p class="licencia-nota">Aún no hay comentarios publicados.</p>'; return; }
  cont.innerHTML = lista.map((c) => `
    <article class="comentario">
      <header><b>${esc(c.rotulo)}${c.nivelImplementado ? ` · implementada en nivel ${esc(c.nivelImplementado)}` : ''}</b>
        <time datetime="${esc(c.creado)}">${esc(new Date(c.creado).toLocaleDateString('es-CL'))} · v${esc(c.tareaVersion)}</time></header>
      <p>${esc(c.texto)}</p>
    </article>`).join('');
}

async function pintarMios(b) {
  let d;
  try { d = await b.misDatos(); } catch { return; }
  const mia = d.valoraciones.find((v) => v.tareaId === tareaId);
  if (mia) { const r = form.querySelector(`input[name=puntaje][value="${mia.puntaje}"]`); if (r) r.checked = true; }
  const propios = d.comentarios.filter((c) => c.tareaId === tareaId);
  let caja = $('mis-comentarios');
  if (!caja) { caja = document.createElement('div'); caja.id = 'mis-comentarios'; form.after(caja); }
  caja.innerHTML = propios.length ? `<h3>Tus comentarios en esta tarea</h3>` + propios.map((c) => `
    <article class="comentario" data-id="${esc(c.id)}">
      <header><b>${esc(ETIQUETA_ESTADO[c.estado])}</b><small>v${esc(c.tareaVersion)}</small></header>
      <p>${esc(c.texto)}</p>
      <div class="acciones"><button type="button" class="boton-mini" data-editar>Editar</button>
        <button type="button" class="boton-mini peligro" data-retirar>Retirar</button></div>
    </article>`).join('') : '';
  caja.querySelectorAll('[data-retirar]').forEach((btn) => btn.addEventListener('click', async () => {
    try { await b.retirarComentario(btn.closest('.comentario').dataset.id); aviso('ok', 'Comentario retirado.'); await pintarMios(b); await pintarComentarios(b); } catch (e) { aviso('error', mensajeDe(e)); }
  }));
  caja.querySelectorAll('[data-editar]').forEach((btn) => btn.addEventListener('click', async () => {
    const art = btn.closest('.comentario');
    const nuevo = window.prompt('Edita tu comentario. Volverá a moderación antes de publicarse.', art.querySelector('p').textContent);
    if (nuevo == null) return;
    try { await b.editarComentario(art.dataset.id, { texto: nuevo, nivelImplementado: null }); aviso('ok', 'Comentario actualizado; vuelve a moderación.'); await pintarMios(b); await pintarComentarios(b); } catch (e) { aviso('error', mensajeDe(e)); }
  }));
}

async function iniciar() {
  if (MODO === 'none') {
    $('op-requiere').textContent = 'Las cuentas, valoraciones y comentarios aún no están habilitados en este sitio. La lectura y la descarga son libres.';
    return;
  }
  const b = await backend();
  await pintarComentarios(b);
  const s = await b.sesion().catch(() => null);
  if (!s) return;
  $('op-requiere').hidden = true;
  $('op-campos').disabled = false;
  await pintarMios(b);
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  msg.hidden = true;
  const b = await backend();
  const f = new FormData(form);
  const puntaje = f.get('puntaje') ? Number(f.get('puntaje')) : null;
  const texto = String(f.get('texto') || '').trim();
  try {
    if (!puntaje && !texto) throw Object.assign(new Error('Elige una valoración o escribe un comentario.'), { codigo: 'vacio' });
    if (!f.get('aviso')) throw Object.assign(new Error('Debes aceptar el aviso de uso de datos.'), { codigo: 'aviso_no_aceptado' });
    if (puntaje) await b.valorar({ tareaId, version, puntaje });
    if (texto) await b.comentar({ tareaId, version, texto, nivelImplementado: f.get('nivel') || null, avisoAceptado: true });
    aviso('ok', texto
      ? 'Gracias. Tu comentario quedó en moderación y se publicará cuando sea aprobado.'
      : 'Gracias. Tu valoración quedó registrada.');
    form.querySelector('textarea').value = '';
    await pintarMios(b);
    await hidratarResumenes();
  } catch (e) {
    aviso('error', mensajeDe(e));
  }
});

hidratarResumenes();
iniciar().catch(() => {});
