// Sitio + backend local simulado en un solo puerto (sin servicios externos).
//   npm run local            -> construye con PUBLIC_BACKEND=local y sirve en http://127.0.0.1:8787
//   OTM_LOCAL_MODERADORES=yo@ejemplo.cl npm run local     (quien se registre con ese correo modera)
// Los datos quedan en sitio/api/.local-data/db.json (ignorado por git).
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { crearServidorLocal } from '../../api/src/local/server.mjs';

const web = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = 'dist-local';
const puerto = Number(process.env.OTM_LOCAL_PORT || 8787);
const moderadores = (process.env.OTM_LOCAL_MODERADORES || 'moderador@ejemplo.cl').split(',');
const datos = process.env.OTM_LOCAL_DATA || path.resolve(web, '..', 'api', '.local-data', 'db.json');

const astro = path.join(web, '..', 'node_modules', 'astro', 'bin', 'astro.mjs');
const r = spawnSync(process.execPath, [astro, 'build'], {
  cwd: web, stdio: 'inherit',
  env: { ...process.env, OTM_OUT_DIR: out, PUBLIC_BACKEND: 'local', PUBLIC_LOCAL_API_URL: '' },
});
if (r.status !== 0) process.exit(r.status ?? 1);

crearServidorLocal({ datos, estatico: path.join(web, out), moderadores }).listen(puerto, '127.0.0.1', () => {
  console.log(`\nSitio con backend local simulado: http://127.0.0.1:${puerto}/`);
  console.log(`Moderadores: ${moderadores.join(', ')}  ->  http://127.0.0.1:${puerto}/moderacion/`);
  console.log(`Datos: ${datos}`);
});
