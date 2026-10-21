// URL pública relativa a la base del hosting (SITE_BASE).
export const u = (ruta = '') => {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  return `${base}/${String(ruta).replace(/^\//, '')}`;
};
