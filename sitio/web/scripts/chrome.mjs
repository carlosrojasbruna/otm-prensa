// Localiza un Chrome/Edge ya instalado. No descarga nada.
import fs from 'node:fs';

const CANDIDATOS = [
  process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
].filter(Boolean);

export function chromeExe() {
  const exe = CANDIDATOS.find((p) => fs.existsSync(p));
  if (!exe) throw new Error('No se encontró Chrome/Edge. Define CHROME_PATH con la ruta del ejecutable.');
  return exe;
}
