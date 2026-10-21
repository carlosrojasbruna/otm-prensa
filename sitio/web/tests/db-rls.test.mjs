// Aplica sitio/db/migrations a un Postgres embebido (PGlite) con un esquema `auth` simulado y
// comprueba las políticas RLS reales: lectura pública solo de aprobados, escritura solo propia,
// moderación solo de moderadores, edición que reinicia moderación, retiro de datos.
import test, { before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { PGlite } from '@electric-sql/pglite';
import { WEB } from './helpers.mjs';

const MIGRACIONES = path.resolve(WEB, '..', 'db', 'migrations');
const T = '2026-10-prueba';
const U = { ana: '00000000-0000-0000-0000-00000000000a', beto: '00000000-0000-0000-0000-00000000000b', mod: '00000000-0000-0000-0000-0000000000f0' };
let db;

// Ejecuta `fn` como un rol y usuario (como hace PostgREST con el JWT).
async function como(rol, uid, fn) {
  await db.exec(`select set_config('request.jwt.claim.sub', '${uid ?? ''}', false); set role ${rol};`);
  try { return await fn(); } finally { await db.exec('reset role;'); }
}
const q = (sql, params) => db.query(sql, params);
const falla = async (fn, patron) => assert.rejects(fn, patron);

before(async () => {
  db = new PGlite();
  await db.exec(`
    create role anon nologin; create role authenticated nologin;
    create schema auth;
    create table auth.users (id uuid primary key, email text);
    create function auth.uid() returns uuid language sql stable as
      $$ select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
    grant usage on schema auth to anon, authenticated;
    grant execute on function auth.uid() to anon, authenticated;
    grant usage on schema public to anon, authenticated;
    insert into auth.users values ('${U.ana}', 'ana@x.cl'), ('${U.beto}', 'beto@x.cl'), ('${U.mod}', 'mod@x.cl');
  `);
  if (process.env.OTM_DB_MODO === 'aplicar_todo') {
    // Mismas comprobaciones, pero con el archivo único aplicado DOS veces (idempotencia).
    const todo = fs.readFileSync(path.resolve(MIGRACIONES, '..', 'aplicar_todo.sql'), 'utf8');
    await db.exec(todo);
    await db.exec(todo);
  } else {
    for (const f of fs.readdirSync(MIGRACIONES).filter((n) => n.endsWith('.sql')).sort()) {
      await db.exec(fs.readFileSync(path.join(MIGRACIONES, f), 'utf8'));
    }
  }
  await db.exec(`insert into public.moderadores (user_id) values ('${U.mod}');`);
});
after(async () => { await db?.close(); });

test('las migraciones se aplican en orden y crean las tablas con RLS activa', async () => {
  const r = await q(`select relname, relrowsecurity from pg_class where relname in ('perfiles','valoraciones','comentarios','moderadores') order by 1`);
  assert.deepEqual(r.rows.map((x) => [x.relname, x.relrowsecurity]),
    [['comentarios', true], ['moderadores', true], ['perfiles', true], ['valoraciones', true]]);
});

test('anon no puede leer ni escribir tablas; sí ejecuta las funciones de lectura pública', async () => {
  await como('anon', null, async () => {
    for (const t of ['perfiles', 'valoraciones', 'comentarios', 'moderadores']) await falla(() => q(`select * from public.${t}`), /permission denied/);
    await falla(() => q(`insert into public.valoraciones (user_id, tarea_id, tarea_version, puntaje) values ('${U.ana}', '${T}', 1, 5)`), /permission denied/);
    assert.deepEqual((await q('select * from public.resumen_valoraciones()')).rows, []);
    assert.deepEqual((await q('select * from public.comentarios_aprobados($1)', [T])).rows, []);
    await falla(() => q('select public.moderar_comentario(gen_random_uuid(), $1)', ['aprobado']), /permission denied/);
  });
});

test('valoraciones: 1-5, una por usuario y tarea, solo a nombre propio; agregados públicos', async () => {
  await como('authenticated', U.ana, async () => {
    await q(`insert into public.valoraciones (tarea_id, tarea_version, puntaje) values ($1, 1, 4)`, [T]); // user_id = auth.uid()
    await falla(() => q(`insert into public.valoraciones (tarea_id, tarea_version, puntaje) values ($1, 1, 5)`, [T]), /duplicate key/);
    await falla(() => q(`insert into public.valoraciones (tarea_id, tarea_version, puntaje) values ($1, 1, 6)`, ['2026-10-otra']), /violates check constraint/);
    await falla(() => q(`insert into public.valoraciones (user_id, tarea_id, tarea_version, puntaje) values ('${U.beto}', '2026-10-otra', 1, 5)`), /row-level security/);
    await q(`update public.valoraciones set puntaje = 2 where tarea_id = $1`, [T]);
  });
  await como('authenticated', U.beto, async () => {
    await q(`insert into public.valoraciones (tarea_id, tarea_version, puntaje) values ($1, 1, 5)`, [T]);
    assert.equal((await q('select * from public.valoraciones')).rows.length, 1, 'solo ve la suya');
    assert.equal((await q(`update public.valoraciones set puntaje = 1 where user_id = '${U.ana}'`)).affectedRows, 0, 'no edita la ajena');
    assert.equal((await q(`delete from public.valoraciones where user_id = '${U.ana}'`)).affectedRows, 0, 'no borra la ajena');
  });
  await como('anon', null, async () => {
    const r = (await q('select * from public.resumen_valoraciones()')).rows[0];
    assert.equal(r.tarea_id, T); assert.equal(Number(r.n), 2); assert.equal(Number(r.promedio), 3.5);
    assert.deepEqual([r.n1, r.n2, r.n3, r.n4, r.n5].map(Number), [0, 1, 0, 0, 1]);
  });
});

test('el upsert de PostgREST (ON CONFLICT DO UPDATE SET user_id, …) choca con el UPDATE por columnas: el adaptador no lo usa', async () => {
  await como('authenticated', U.ana, async () => {
    await falla(() => q(`insert into public.valoraciones (user_id, tarea_id, tarea_version, puntaje) values ('${U.ana}', '2026-10-upsert', 1, 3)
      on conflict (user_id, tarea_id) do update set user_id = excluded.user_id, tarea_id = excluded.tarea_id, tarea_version = excluded.tarea_version, puntaje = excluded.puntaje`), /permission denied/);
    await falla(() => q(`insert into public.perfiles (user_id, aviso_version) values ('${U.ana}', 'v1')
      on conflict (user_id) do update set user_id = excluded.user_id, aviso_version = excluded.aviso_version`), /permission denied/);
  });
});

let idComentario;
test('comentarios: nacen pendientes, no son públicos, no se puede saltar la moderación', async () => {
  await como('authenticated', U.ana, async () => {
    await falla(() => q(`insert into public.comentarios (tarea_id, tarea_version, texto, estado, aviso_version) values ($1, 1, 'x', 'aprobado', 'v')`, [T]), /row-level security/);
    await falla(() => q(`insert into public.comentarios (tarea_id, tarea_version, texto, aviso_version) values ($1, 1, '   ', 'v')`, [T]), /violates check constraint/);
    await falla(() => q(`insert into public.comentarios (user_id, tarea_id, tarea_version, texto, aviso_version) values ('${U.beto}', $1, 1, 'suplanta', 'v')`, [T]), /row-level security/);
    const r = await q(`insert into public.comentarios (tarea_id, tarea_version, texto, nivel_implementado, aviso_version) values ($1, 1, 'Funcionó bien', 'S', 'v1') returning id, estado`, [T]);
    assert.equal(r.rows[0].estado, 'pendiente');
    idComentario = r.rows[0].id;
    // no puede autoaprobarse (privilegio por columna)
    await falla(() => q(`update public.comentarios set estado = 'aprobado' where id = $1`, [idComentario]), /permission denied/);
  });
  await como('anon', null, async () => assert.equal((await q('select * from public.comentarios_aprobados($1)', [T])).rows.length, 0));
  await como('authenticated', U.beto, async () => {
    assert.equal((await q('select * from public.comentarios')).rows.length, 0, 'otro docente no ve el pendiente');
    assert.equal((await q(`update public.comentarios set texto = 'hack' where id = $1`, [idComentario])).affectedRows, 0);
    assert.equal((await q(`delete from public.comentarios where id = $1`, [idComentario])).affectedRows, 0);
    await falla(() => q('select * from public.comentarios_pendientes()'), /solo moderadores/);
    await falla(() => q('select public.moderar_comentario($1, $2)', [idComentario, 'aprobado']), /solo moderadores/);
  });
});

test('moderación: solo moderadores aprueban; el público ve el comentario sin identidad', async () => {
  await como('authenticated', U.mod, async () => {
    assert.equal((await q('select * from public.comentarios_pendientes()')).rows.length, 1);
    await falla(() => q('select public.moderar_comentario($1, $2)', [idComentario, 'publicado']), /estado inválido/);
    await q('select public.moderar_comentario($1, $2, $3)', [idComentario, 'aprobado', 'ok']);
  });
  await como('anon', null, async () => {
    const r = (await q('select * from public.comentarios_aprobados($1)', [T])).rows;
    assert.equal(r.length, 1);
    assert.equal(r[0].texto, 'Funcionó bien');
    assert.equal(r[0].rotulo, 'Docente');
    assert.ok(!('user_id' in r[0]));
  });
  const fila = (await q('select estado, moderado_por from public.comentarios where id = $1', [idComentario])).rows[0];
  assert.deepEqual([fila.estado, fila.moderado_por], ['aprobado', U.mod]);
});

test('editar un comentario aprobado lo devuelve a pendiente y lo oculta; retirar lo borra', async () => {
  await como('authenticated', U.ana, async () => {
    await q(`update public.comentarios set texto = 'Funcionó muy bien' where id = $1`, [idComentario]);
    const f = (await q('select estado, moderado_por from public.comentarios where id = $1', [idComentario])).rows[0];
    assert.deepEqual([f.estado, f.moderado_por], ['pendiente', null]);
  });
  await como('anon', null, async () => assert.equal((await q('select * from public.comentarios_aprobados($1)', [T])).rows.length, 0));
  await como('authenticated', U.mod, async () => {
    await q('select public.moderar_comentario($1, $2, $3)', [idComentario, 'rechazado', 'prueba']);
  });
  await como('authenticated', U.ana, async () => {
    assert.equal((await q('select estado from public.comentarios where id = $1', [idComentario])).rows[0].estado, 'rechazado');
    assert.equal((await q('delete from public.comentarios where id = $1', [idComentario])).affectedRows, 1);
  });
});

test('perfil: opcional (campos nulos), validado, solo propio, retirable; país no existe', async () => {
  await como('authenticated', U.ana, async () => {
    await q(`insert into public.perfiles (aviso_version, user_id) values ('v1', '${U.ana}')`); // todo vacío es válido en el piloto
    await q(`update public.perfiles set nivel_ensenanza = 'S', tipo_establecimiento = 'municipal', region = 'Valparaíso', anios_experiencia = 12 where user_id = '${U.ana}'`);
    await falla(() => q(`update public.perfiles set nivel_ensenanza = 'X' where user_id = '${U.ana}'`), /violates check constraint/);
    await falla(() => q(`update public.perfiles set anios_experiencia = 99 where user_id = '${U.ana}'`), /violates check constraint/);
    await falla(() => q(`insert into public.perfiles (user_id, aviso_version) values ('${U.beto}', 'v1')`), /row-level security/);
  });
  await como('authenticated', U.beto, async () => assert.equal((await q('select * from public.perfiles')).rows.length, 0));
  await como('anon', null, async () => {
    // el perfil no se expone, pero el rótulo público usa el nivel si existe
  });
  const cols = (await q(`select column_name from information_schema.columns where table_name = 'perfiles'`)).rows.map((r) => r.column_name);
  assert.ok(!cols.includes('pais'), 'país se agrega en la versión final [D], no en el piloto');
  for (const c of ['nivel_ensenanza', 'tipo_establecimiento', 'region', 'anios_experiencia']) assert.ok(cols.includes(c));
});

test('el rótulo público usa el nivel del perfil; retirar_mis_datos borra todo lo propio', async () => {
  let id;
  await como('authenticated', U.ana, async () => {
    id = (await q(`insert into public.comentarios (tarea_id, tarea_version, texto, aviso_version) values ($1, 1, 'otro', 'v1') returning id`, [T])).rows[0].id;
  });
  await como('authenticated', U.mod, async () => { await q('select public.moderar_comentario($1, $2)', [id, 'aprobado']); });
  await como('anon', null, async () => {
    assert.equal((await q('select rotulo from public.comentarios_aprobados($1)', [T])).rows[0].rotulo, 'Docente · nivel S');
  });
  await como('authenticated', U.ana, async () => {
    await q('select public.retirar_mis_datos()');
    for (const t of ['perfiles', 'valoraciones', 'comentarios']) assert.equal((await q(`select * from public.${t}`)).rows.length, 0, t);
  });
  await como('authenticated', U.beto, async () => assert.equal((await q('select * from public.valoraciones')).rows.length, 1, 'no toca lo de otros'));
  await como('anon', null, async () => await falla(() => q('select public.retirar_mis_datos()'), /permission denied/));
});

test('la tabla de moderadores no es accesible ni escribible desde la API', async () => {
  await como('authenticated', U.ana, async () => {
    await falla(() => q('select * from public.moderadores'), /permission denied/);
    await falla(() => q(`insert into public.moderadores (user_id) values ('${U.ana}')`), /permission denied/);
  });
});
