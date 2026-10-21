import { defineConfig } from 'astro/config';

// Variables de construcción (todas opcionales):
//   SITE_BASE      ruta base del hosting (p. ej. "/otm-prensa/" en GitHub Pages). Por defecto "/".
//   SITE_URL       URL pública, para canonical y sitemap.
//   OTM_OUT_DIR    carpeta de salida (por defecto "dist").
//   OTM_REPO_ROOT  raíz del repositorio que contiene tareas/ (por defecto dos niveles sobre sitio/web).
export default defineConfig({
  output: 'static',
  base: process.env.SITE_BASE || '/',
  site: process.env.SITE_URL || undefined,
  outDir: process.env.OTM_OUT_DIR || 'dist',
  trailingSlash: 'always',
  build: { inlineStylesheets: 'always', format: 'directory' },
  compressHTML: true,
  devToolbar: { enabled: false },
  telemetry: false,
});
