// Genera sitio/db/aplicar_todo.sql a partir de migrations/*.sql (0001 -> 0002 -> 0003 ...).
// Las migraciones NO se editan: este script las vuelve idempotentes por transformación textual.
//   create table X            -> create table if not exists X
//   create index X            -> create index if not exists X
//   create function X         -> create or replace function X
//   create trigger T ... on R -> drop trigger if exists T on R; create trigger T ...
//   create policy P on R      -> drop policy if exists P on R; create policy P on R
// Todo va en una transacción. Uso:
//   node sitio/db/generar_aplicar_todo.mjs           escribe aplicar_todo.sql
//   node sitio/db/generar_aplicar_todo.mjs --check   falla (código 1) si el archivo está desactualizado
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const aqui = path.dirname(fileURLToPath(import.meta.url));
const SALIDA = path.join(aqui, 'aplicar_todo.sql');

export function idempotente(sql) {
  return sql
    .replace(/^create table (?!if not exists)/gim, 'create table if not exists ')
    .replace(/^create index (?!if not exists)/gim, 'create index if not exists ')
    .replace(/^create function /gim, 'create or replace function ')
    .replace(/^create trigger (\w+)\b([^;]*?)\bon (public\.\w+)/gims,
      (m, nombre, medio, tabla) => `drop trigger if exists ${nombre} on ${tabla};\n${m}`)
    .replace(/^create policy (\w+) on (public\.\w+)/gim,
      (m, nombre, tabla) => `drop policy if exists ${nombre} on ${tabla};\n${m}`);
}

export function generar() {
  const dir = path.join(aqui, 'migrations');
  const archivos = fs.readdirSync(dir).filter((n) => /^\d{4}_.*\.sql$/.test(n)).sort();
  const cab = `-- OTM-Prensa · sitio docente · TODAS las migraciones en un solo archivo (GENERADO).
-- No editar a mano: lo produce sitio/db/generar_aplicar_todo.mjs a partir de migrations/.
-- Migraciones incluidas: ${archivos.join(', ')}.
--
-- Cómo correrlo en Supabase (SQL Editor):
--   1. Panel de Supabase > SQL Editor > New query.
--   2. Pegar TODO este archivo y pulsar Run (rol postgres).
--   3. Es idempotente: se puede correr más de una vez (tablas "if not exists", funciones
--      "create or replace", políticas y triggers se recrean). No borra datos.
--   4. Todo va en una transacción: si algo falla, no queda nada a medias.
-- Desde CI: deploy.yml lo aplica con psql si existe el secret SUPABASE_DB_URL.
-- Después: designar moderadores (ver sitio/db/README.md).

begin;
`;
  const cuerpo = archivos.map((f) =>
    `\n-- ================================================================ ${f}\n` +
    idempotente(fs.readFileSync(path.join(dir, f), 'utf8').replace(/\r\n/g, '\n')).trimEnd() + '\n').join('');
  return cab + cuerpo + '\ncommit;\n';
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const nuevo = generar();
  if (process.argv.includes('--check')) {
    const actual = fs.existsSync(SALIDA) ? fs.readFileSync(SALIDA, 'utf8').replace(/\r\n/g, '\n') : '';
    if (actual !== nuevo) { console.error('aplicar_todo.sql está desactualizado: corre node sitio/db/generar_aplicar_todo.mjs'); process.exit(1); }
    console.log('aplicar_todo.sql al día');
  } else {
    fs.writeFileSync(SALIDA, nuevo);
    console.log(`escrito ${SALIDA}`);
  }
}
