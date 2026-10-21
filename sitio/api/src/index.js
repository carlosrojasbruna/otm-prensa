// Fábrica del backend. La interfaz es la misma para todos los modos:
//   'supabase' (producción/staging) | 'local' (servidor simulado) | 'none' (sin cuentas).
// Los adaptadores se cargan con import dinámico: el sitio no descarga Supabase si no lo usa.
export * from './comun.js';

/**
 * Decide el modo a partir de la configuración pública.
 * - PUBLIC_BACKEND explícito gana ('supabase' | 'local' | 'none').
 * - Si no hay PUBLIC_BACKEND y hay URL de Supabase: 'supabase'. Si no: 'none'.
 */
export function resolverModo({ backend, supabaseUrl, supabaseAnonKey } = {}) {
  if (backend === 'local' || backend === 'none') return backend;
  if (backend === 'supabase' || (supabaseUrl && supabaseAnonKey)) return supabaseUrl && supabaseAnonKey ? 'supabase' : 'none';
  return 'none';
}

export async function crearBackend(config = {}) {
  const modo = resolverModo(config);
  if (modo === 'local') return (await import('./local.js')).crearBackendLocal(config);
  if (modo === 'supabase') return (await import('./supabase.js')).crearBackendSupabase(config);
  return { modo: 'none' };
}
