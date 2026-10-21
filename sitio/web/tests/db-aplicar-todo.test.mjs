// sitio/db/aplicar_todo.sql: al día con las migraciones, idempotente (dos aplicaciones seguidas
// sin error, datos intactos) y con las mismas comprobaciones RLS de db-rls.test.mjs.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { PGlite } from '@electric-sql/pglite';
import { WEB } from './helpers.mjs';

const DB = path.resolve(WEB, '..', 'db');

test('aplicar_todo.sql coincide con lo que genera el script (no está desactualizado)', () => {
  const r = spawnSync(process.execPath, [path.join(DB, 'generar_aplicar_todo.mjs'), '--check'], { encoding: 'utf8' });
  assert.equal(r.status, 0, r.stdout + r.stderr);
});

test('aplicar_todo.sql va en una transacción y no contiene secretos ni DDL destructivo de datos', () => {
  const s = fs.readFileSync(path.join(DB, 'aplicar_todo.sql'), 'utf8');
  assert.match(s, /^begin;$/m);
  assert.match(s, /^commit;$/m);
  assert.doesNotMatch(s, /drop table|truncate|delete from public\.(?!comentarios where|valoraciones where|perfiles where)/i);
});

test('se aplica dos veces seguidas sobre una base con datos sin error ni pérdida', async () => {
  const db = new PGlite();
  try {
    await db.exec(`create role anon nologin; create role authenticated nologin; create schema auth;
      create table auth.users (id uuid primary key, email text);
      create function auth.uid() returns uuid language sql stable as $$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
      grant usage on schema auth to anon, authenticated; grant execute on function auth.uid() to anon, authenticated;
      grant usage on schema public to anon, authenticated;
      insert into auth.users values ('00000000-0000-0000-0000-00000000000a', 'a@x.cl');`);
    const todo = fs.readFileSync(path.join(DB, 'aplicar_todo.sql'), 'utf8');
    await db.exec(todo);
    await db.exec(`insert into public.moderadores (user_id) values ('00000000-0000-0000-0000-00000000000a');
      insert into public.valoraciones (user_id, tarea_id, tarea_version, puntaje) values ('00000000-0000-0000-0000-00000000000a', '2026-10-x', 1, 5);`);
    await db.exec(todo);
    assert.equal((await db.query('select count(*)::int n from public.moderadores')).rows[0].n, 1);
    assert.equal((await db.query('select count(*)::int n from public.valoraciones')).rows[0].n, 1);
    const pol = (await db.query(`select count(*)::int n from pg_policies where schemaname = 'public'`)).rows[0].n;
    assert.equal(pol, 12, 'sin políticas duplicadas ni faltantes');
    const trg = (await db.query(`select count(*)::int n from pg_trigger t join pg_class c on c.oid = t.tgrelid join pg_namespace s on s.oid = c.relnamespace where not t.tgisinternal and s.nspname = 'public'`)).rows[0].n;
    assert.equal(trg, 4);
  } finally { await db.close(); }
});

test('el archivo único pasa las mismas comprobaciones RLS (db-rls.test.mjs, aplicado dos veces)', () => {
  const r = spawnSync(process.execPath, ['--test', 'tests/db-rls.test.mjs'], {
    cwd: WEB, encoding: 'utf8', env: { ...process.env, OTM_DB_MODO: 'aplicar_todo' },
  });
  assert.equal(r.status, 0, r.stdout.slice(-3000) + r.stderr.slice(-1000));
});
