// Ejecuta todas las pruebas del sitio (node:test). Uso: npm test
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const web = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const archivos = fs.readdirSync(path.join(web, 'tests')).filter((f) => f.endsWith('.test.mjs')).map((f) => path.join('tests', f));
const r = spawnSync(process.execPath, ['--test', '--test-concurrency=1', ...archivos], { cwd: web, stdio: 'inherit' });
// Limpia las salidas temporales de las pruebas.
for (const d of fs.readdirSync(web).filter((n) => n.startsWith('dist-test-') || n === 'dist-e2e')) fs.rmSync(path.join(web, d), { recursive: true, force: true });
process.exit(r.status ?? 1);
