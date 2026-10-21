// Adaptador de desarrollo: habla con el backend local simulado (src/local/server.mjs).
// Misma interfaz que el adaptador de Supabase. Solo corre en el navegador (usa fetch y localStorage).
import { ErrorOtm, exigirAviso, validarComentario, validarCredenciales, validarPerfil, validarPuntaje, validarTarea, resumenVacio } from './comun.js';

const CLAVE_TOKEN = 'otm.local.token';

export function crearBackendLocal({ localApiUrl = '' } = {}) {
  const base = String(localApiUrl).replace(/\/$/, '');
  const leerToken = () => (typeof localStorage === 'undefined' ? null : localStorage.getItem(CLAVE_TOKEN));
  const guardarToken = (t) => (t ? localStorage.setItem(CLAVE_TOKEN, t) : localStorage.removeItem(CLAVE_TOKEN));

  async function llamar(metodo, ruta, cuerpo) {
    const cab = { Accept: 'application/json' };
    const token = leerToken();
    if (token) cab.Authorization = `Bearer ${token}`;
    if (cuerpo !== undefined) cab['Content-Type'] = 'application/json';
    let r;
    try {
      r = await fetch(`${base}/api${ruta}`, { method: metodo, headers: cab, body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo) });
    } catch {
      throw new ErrorOtm('servicio', 'No se pudo conectar con el servicio de cuentas.');
    }
    const datos = r.status === 204 ? null : await r.json().catch(() => null);
    if (!r.ok) throw new ErrorOtm(datos?.error?.codigo || 'servicio', datos?.error?.mensaje || `Error ${r.status}`);
    return datos;
  }

  return {
    modo: 'local',

    async registrar(cred) {
      const c = validarCredenciales(cred);
      const d = await llamar('POST', '/auth/registro', c);
      guardarToken(d.token);
      return { id: d.usuario.id, email: d.usuario.email, requiereConfirmacion: false };
    },
    async iniciarSesion(cred) {
      const c = validarCredenciales(cred);
      const d = await llamar('POST', '/auth/login', c);
      guardarToken(d.token);
      return d.usuario;
    },
    async cerrarSesion() {
      try { await llamar('POST', '/auth/logout', {}); } finally { guardarToken(null); }
    },
    async sesion() {
      if (!leerToken()) return null;
      try { return (await llamar('GET', '/sesion')).usuario; } catch (e) {
        if (e.codigo === 'sin_sesion') { guardarToken(null); return null; }
        throw e;
      }
    },

    resumenes: () => llamar('GET', '/resumenes'),
    async resumen(tareaId) { return (await this.resumenes())[tareaId] ?? resumenVacio(); },
    comentariosPublicos: (tareaId) => llamar('GET', `/tareas/${encodeURIComponent(tareaId)}/comentarios`),

    misDatos: () => llamar('GET', '/mis-datos'),

    async valorar({ tareaId, version, puntaje }) {
      validarTarea(tareaId, version); validarPuntaje(puntaje);
      await llamar('PUT', `/valoraciones/${encodeURIComponent(tareaId)}`, { version, puntaje });
    },
    async retirarValoracion(tareaId) { await llamar('DELETE', `/valoraciones/${encodeURIComponent(tareaId)}`); },

    async comentar({ tareaId, version, texto, nivelImplementado, avisoAceptado }) {
      validarTarea(tareaId, version); exigirAviso(avisoAceptado);
      const v = validarComentario({ texto, nivelImplementado });
      return llamar('POST', '/comentarios', { tareaId, version, ...v, avisoAceptado });
    },
    async editarComentario(id, datos) {
      const v = validarComentario(datos);
      await llamar('PATCH', `/comentarios/${encodeURIComponent(id)}`, v);
    },
    async retirarComentario(id) { await llamar('DELETE', `/comentarios/${encodeURIComponent(id)}`); },

    async guardarPerfil(perfil, avisoAceptado) {
      exigirAviso(avisoAceptado);
      await llamar('PUT', '/perfil', { ...validarPerfil(perfil), avisoAceptado });
    },
    async retirarPerfil() { await llamar('DELETE', '/perfil'); },
    async retirarTodo() { await llamar('DELETE', '/mis-datos'); },

    pendientes: () => llamar('GET', '/moderacion/pendientes'),
    async moderar(id, estado, motivo = null) { await llamar('POST', `/moderacion/${encodeURIComponent(id)}`, { estado, motivo }); },
  };
}
