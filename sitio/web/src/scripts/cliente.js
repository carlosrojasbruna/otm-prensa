// Acceso al backend desde el navegador. La configuración sale de variables PUBLIC_* en el build.
import { crearBackend } from 'otm-api';

let promesa;
export function backend() {
  promesa ??= crearBackend({
    backend: import.meta.env.PUBLIC_BACKEND,
    supabaseUrl: import.meta.env.PUBLIC_SUPABASE_URL,
    supabaseAnonKey: import.meta.env.PUBLIC_SUPABASE_ANON_KEY,
    localApiUrl: import.meta.env.PUBLIC_LOCAL_API_URL || '',
  });
  return promesa;
}

export const MODO = (() => {
  const b = import.meta.env.PUBLIC_BACKEND;
  if (b === 'local' || b === 'none') return b;
  return import.meta.env.PUBLIC_SUPABASE_URL && import.meta.env.PUBLIC_SUPABASE_ANON_KEY ? 'supabase' : 'none';
})();

export const MENSAJES = {
  sin_sesion: 'Inicia sesión para continuar.',
  credenciales: 'Correo o contraseña incorrectos.',
  correo_en_uso: 'Ese correo ya tiene una cuenta. Inicia sesión.',
  aviso_no_aceptado: 'Debes aceptar el aviso de uso de datos.',
  sin_permiso: 'No tienes permiso para esta acción.',
  servicio: 'No se pudo completar la acción. Intenta de nuevo más tarde.',
  limite: 'Demasiados intentos. Espera unos minutos.',
};
export const mensajeDe = (e) => (e && MENSAJES[e.codigo] && !['texto_vacio', 'texto_largo'].includes(e.codigo) ? MENSAJES[e.codigo] : e?.message || MENSAJES.servicio);

/** Escapa texto para insertarlo como HTML. */
export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export function textoEstrellas(prom) {
  return Array.from({ length: 5 }, (_, i) => `<span class="${i + 1 <= Math.round(prom) ? 'on' : ''}">★</span>`).join('');
}
export const num = (n) => String(n).replace('.', ',');
