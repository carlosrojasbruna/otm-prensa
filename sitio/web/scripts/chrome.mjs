// Localiza un Chrome/Edge ya instalado. No descarga nada.
import fs from 'node:fs';
import path from 'node:path';

const CANDIDATOS = [
  process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
].filter(Boolean);

// CHROME_PATH puede ser un nombre de comando (p. ej. `google-chrome` en el runner de Actions): se busca en PATH.
function enPath(nombre) {
  if (!nombre || nombre.includes('/') || nombre.includes('\\')) return nombre;
  for (const d of (process.env.PATH || '').split(path.delimiter)) {
    for (const ext of process.platform === 'win32' ? ['.exe', '.cmd', ''] : ['']) {
      const c = path.join(d, nombre + ext);
      if (d && fs.existsSync(c)) return c;
    }
  }
  return nombre;
}

export function chromeExe() {
  const exe = CANDIDATOS.map(enPath).find((p) => fs.existsSync(p));
  if (!exe) throw new Error('No se encontró Chrome/Edge. Define CHROME_PATH con la ruta del ejecutable.');
  return exe;
}
