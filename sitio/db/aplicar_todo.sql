-- OTM-Prensa · sitio docente · TODAS las migraciones en un solo archivo (GENERADO).
-- No editar a mano: lo produce sitio/db/generar_aplicar_todo.mjs a partir de migrations/.
-- Migraciones incluidas: 0001_tablas.sql, 0002_rls.sql, 0003_funciones.sql.
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

-- ================================================================ 0001_tablas.sql
-- OTM-Prensa · sitio docente · migración 0001: tablas
-- Fuente de reglas: GOB01 §5 (cuenta requerida para valorar y comentar; perfil docente
-- opcional en el piloto; aviso de uso de datos; moderación previa; derecho a editar o retirar).
-- Requiere un proyecto Supabase (esquema `auth` y roles `anon`/`authenticated`).

-- ---------------------------------------------------------------- perfiles
-- Perfil docente. Piloto: todos los campos son OPCIONALES (nulos permitidos).
-- Versión final: pasarán a requeridos y se agregará `pais` [D]; ver db/README.md.
-- `aviso_version` registra la versión del aviso de uso de datos que la persona aceptó.
create table if not exists public.perfiles (
  user_id               uuid primary key references auth.users (id) on delete cascade,
  nivel_ensenanza       text check (nivel_ensenanza in ('P', 'S', 'U')),
  tipo_establecimiento  text check (tipo_establecimiento in
                          ('municipal', 'particular_subvencionado', 'particular_pagado',
                           'servicio_local', 'universidad', 'otro')),
  region                text check (char_length(region) between 1 and 80),
  anios_experiencia     smallint check (anios_experiencia between 0 and 60),
  aviso_version         text not null,
  creado                timestamptz not null default now(),
  actualizado           timestamptz not null default now()
);
comment on table public.perfiles is
  'Perfil docente opcional (GOB01 §5). Se usa anonimizado con fines de investigación. Nunca se expone con user_id.';

-- -------------------------------------------------------------- valoraciones
create table if not exists public.valoraciones (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users (id) on delete cascade default auth.uid(),
  tarea_id       text not null check (tarea_id ~ '^[0-9]{4}-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$'),
  tarea_version  integer not null check (tarea_version >= 1),
  puntaje        smallint not null check (puntaje between 1 and 5),
  creado         timestamptz not null default now(),
  actualizado    timestamptz not null default now(),
  unique (user_id, tarea_id)           -- una valoración vigente por docente y tarea
);
create index if not exists valoraciones_tarea_idx on public.valoraciones (tarea_id);

-- --------------------------------------------------------------- comentarios
create table if not exists public.comentarios (
  id                   uuid primary key default gen_random_uuid(),
  user_id              uuid not null references auth.users (id) on delete cascade default auth.uid(),
  tarea_id             text not null check (tarea_id ~ '^[0-9]{4}-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$'),
  tarea_version        integer not null check (tarea_version >= 1),
  texto                text not null check (char_length(btrim(texto)) between 1 and 2000),
  nivel_implementado   text check (nivel_implementado in ('P', 'S', 'U')),
  estado               text not null default 'pendiente'
                         check (estado in ('pendiente', 'aprobado', 'rechazado')),
  motivo_moderacion    text check (char_length(motivo_moderacion) <= 500),
  moderado_por         uuid references auth.users (id) on delete set null,
  moderado_en          timestamptz,
  aviso_version        text not null,
  creado               timestamptz not null default now(),
  actualizado          timestamptz not null default now()
);
create index if not exists comentarios_tarea_estado_idx on public.comentarios (tarea_id, estado);
create index if not exists comentarios_user_idx on public.comentarios (user_id);

-- --------------------------------------------------------------- moderadores
-- Quienes pueden aprobar o rechazar comentarios. Se agregan a mano desde el editor SQL
-- (rol postgres); ninguna política permite escribirla desde la API pública.
create table if not exists public.moderadores (
  user_id  uuid primary key references auth.users (id) on delete cascade,
  creado   timestamptz not null default now()
);

-- ---------------------------------------------------------- marca de tiempo
create or replace function public.tocar_actualizado() returns trigger
language plpgsql set search_path = '' as $$
begin
  new.actualizado := now();
  return new;
end $$;

drop trigger if exists perfiles_actualizado on public.perfiles;
create trigger perfiles_actualizado before update on public.perfiles
  for each row execute function public.tocar_actualizado();
drop trigger if exists valoraciones_actualizado on public.valoraciones;
create trigger valoraciones_actualizado before update on public.valoraciones
  for each row execute function public.tocar_actualizado();
drop trigger if exists comentarios_actualizado on public.comentarios;
create trigger comentarios_actualizado before update on public.comentarios
  for each row execute function public.tocar_actualizado();

-- ================================================================ 0002_rls.sql
-- OTM-Prensa · sitio docente · migración 0002: RLS y privilegios
-- Principio: las tablas están cerradas al público. La lectura pública pasa SOLO por las
-- funciones de 0003 (comentarios aprobados sin user_id; agregados de valoración).
-- Escritura: únicamente el propio usuario autenticado, sobre filas suyas.

alter table public.perfiles      enable row level security;
alter table public.valoraciones  enable row level security;
alter table public.comentarios   enable row level security;
alter table public.moderadores   enable row level security;

-- Privilegios base: nada para anon; lo mínimo para authenticated.
revoke all on public.perfiles, public.valoraciones, public.comentarios, public.moderadores
  from anon, authenticated;

-- ¿El usuario actual es moderador? (security definer para leer la tabla cerrada
-- `moderadores` sin darle acceso directo.)
create or replace function public.es_moderador() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.moderadores m where m.user_id = (select auth.uid()));
$$;
revoke all on function public.es_moderador() from public;
grant execute on function public.es_moderador() to authenticated;

-- ---------------------------------------------------------------- perfiles
grant select, insert, delete on public.perfiles to authenticated;
grant update (nivel_ensenanza, tipo_establecimiento, region, anios_experiencia, aviso_version)
  on public.perfiles to authenticated;

drop policy if exists perfiles_leer_propio on public.perfiles;
create policy perfiles_leer_propio on public.perfiles
  for select to authenticated using (user_id = (select auth.uid()));
drop policy if exists perfiles_crear_propio on public.perfiles;
create policy perfiles_crear_propio on public.perfiles
  for insert to authenticated with check (user_id = (select auth.uid()));
drop policy if exists perfiles_editar_propio on public.perfiles;
create policy perfiles_editar_propio on public.perfiles
  for update to authenticated
  using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
drop policy if exists perfiles_retirar_propio on public.perfiles;
create policy perfiles_retirar_propio on public.perfiles
  for delete to authenticated using (user_id = (select auth.uid()));

-- ------------------------------------------------------------ valoraciones
grant select, insert, delete on public.valoraciones to authenticated;
grant update (puntaje, tarea_version) on public.valoraciones to authenticated;

drop policy if exists valoraciones_leer_propia on public.valoraciones;
create policy valoraciones_leer_propia on public.valoraciones
  for select to authenticated using (user_id = (select auth.uid()));
drop policy if exists valoraciones_crear_propia on public.valoraciones;
create policy valoraciones_crear_propia on public.valoraciones
  for insert to authenticated with check (user_id = (select auth.uid()));
drop policy if exists valoraciones_editar_propia on public.valoraciones;
create policy valoraciones_editar_propia on public.valoraciones
  for update to authenticated
  using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
drop policy if exists valoraciones_retirar_propia on public.valoraciones;
create policy valoraciones_retirar_propia on public.valoraciones
  for delete to authenticated using (user_id = (select auth.uid()));

-- ------------------------------------------------------------- comentarios
-- Lectura: el autor ve todos los suyos (con su estado); moderadores ven todos.
-- El público NO lee esta tabla: usa public.comentarios_aprobados() (0003).
grant select, insert, delete on public.comentarios to authenticated;
grant update (texto, nivel_implementado) on public.comentarios to authenticated;

drop policy if exists comentarios_leer_propio on public.comentarios;
create policy comentarios_leer_propio on public.comentarios
  for select to authenticated
  using (user_id = (select auth.uid()) or (select public.es_moderador()));
-- Alta: siempre `pendiente` y sin datos de moderación.
drop policy if exists comentarios_crear_propio on public.comentarios;
create policy comentarios_crear_propio on public.comentarios
  for insert to authenticated
  with check (user_id = (select auth.uid())
              and estado = 'pendiente'
              and moderado_por is null and moderado_en is null and motivo_moderacion is null);
-- Edición: solo texto y nivel (privilegio por columna). El trigger devuelve el comentario
-- a `pendiente` para que una edición vuelva a pasar por moderación.
drop policy if exists comentarios_editar_propio on public.comentarios;
create policy comentarios_editar_propio on public.comentarios
  for update to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));
drop policy if exists comentarios_retirar_propio on public.comentarios;
create policy comentarios_retirar_propio on public.comentarios
  for delete to authenticated using (user_id = (select auth.uid()));

create or replace function public.comentario_reinicia_moderacion() returns trigger
language plpgsql set search_path = '' as $$
begin
  if new.texto is distinct from old.texto
     or new.nivel_implementado is distinct from old.nivel_implementado then
    new.estado := 'pendiente';
    new.motivo_moderacion := null;
    new.moderado_por := null;
    new.moderado_en := null;
  end if;
  return new;
end $$;
-- moderar_comentario() (security definer) no toca texto ni nivel: no dispara el reinicio.
drop trigger if exists comentarios_reinicia_moderacion on public.comentarios;
create trigger comentarios_reinicia_moderacion before update on public.comentarios
  for each row execute function public.comentario_reinicia_moderacion();

-- -------------------------------------------------------------- moderadores
-- Sin política ni privilegios: tabla invisible para la API pública.

-- ================================================================ 0003_funciones.sql
-- OTM-Prensa · sitio docente · migración 0003: funciones públicas y de moderación

-- ------------------------------------------------------------ lectura pública
-- Agregados de valoración por tarea (sin identificar a nadie).
create or replace function public.resumen_valoraciones()
returns table (tarea_id text, n bigint, promedio numeric, n1 bigint, n2 bigint, n3 bigint, n4 bigint, n5 bigint)
language sql stable security definer set search_path = '' as $$
  select v.tarea_id,
         count(*),
         round(avg(v.puntaje)::numeric, 2),
         count(*) filter (where v.puntaje = 1), count(*) filter (where v.puntaje = 2),
         count(*) filter (where v.puntaje = 3), count(*) filter (where v.puntaje = 4),
         count(*) filter (where v.puntaje = 5)
  from public.valoraciones v
  group by v.tarea_id;
$$;

-- Comentarios aprobados de una tarea. No devuelve user_id: el rótulo es solo
-- "Docente" o "Docente · nivel X" (si la persona declaró nivel en su perfil).
create or replace function public.comentarios_aprobados(p_tarea_id text)
returns table (id uuid, tarea_version integer, texto text, nivel_implementado text, rotulo text, creado timestamptz)
language sql stable security definer set search_path = '' as $$
  select c.id, c.tarea_version, c.texto, c.nivel_implementado,
         case when p.nivel_ensenanza is null then 'Docente'
              else 'Docente · nivel ' || p.nivel_ensenanza end,
         c.creado
  from public.comentarios c
  left join public.perfiles p on p.user_id = c.user_id
  where c.tarea_id = p_tarea_id and c.estado = 'aprobado'
  order by c.creado desc
  limit 200;
$$;

revoke all on function public.resumen_valoraciones() from public;
revoke all on function public.comentarios_aprobados(text) from public;
grant execute on function public.resumen_valoraciones() to anon, authenticated;
grant execute on function public.comentarios_aprobados(text) to anon, authenticated;

-- --------------------------------------------------------------- moderación
-- Cola de pendientes (solo moderadores).
create or replace function public.comentarios_pendientes()
returns table (id uuid, tarea_id text, tarea_version integer, texto text, nivel_implementado text, creado timestamptz)
language plpgsql stable security definer set search_path = '' as $$
begin
  if not public.es_moderador() then
    raise exception 'solo moderadores' using errcode = '42501';
  end if;
  return query
    select c.id, c.tarea_id, c.tarea_version, c.texto, c.nivel_implementado, c.creado
    from public.comentarios c where c.estado = 'pendiente' order by c.creado;
end $$;

-- Aprobar o rechazar (solo moderadores).
create or replace function public.moderar_comentario(p_id uuid, p_estado text, p_motivo text default null)
returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.es_moderador() then
    raise exception 'solo moderadores' using errcode = '42501';
  end if;
  if p_estado not in ('aprobado', 'rechazado') then
    raise exception 'estado inválido: %', p_estado using errcode = '22023';
  end if;
  update public.comentarios
     set estado = p_estado,
         motivo_moderacion = left(p_motivo, 500),
         moderado_por = (select auth.uid()),
         moderado_en = now()
   where id = p_id;
  if not found then
    raise exception 'comentario inexistente' using errcode = 'P0002';
  end if;
end $$;

revoke all on function public.comentarios_pendientes() from public;
revoke all on function public.moderar_comentario(uuid, text, text) from public;
grant execute on function public.comentarios_pendientes() to authenticated;
grant execute on function public.moderar_comentario(uuid, text, text) to authenticated;

-- ------------------------------------------------------- derecho a retirar
-- Borra todo lo de la persona (valoraciones, comentarios, perfil). No borra la cuenta de
-- autenticación (eso se hace desde el panel de Supabase si lo pide).
create or replace function public.retirar_mis_datos() returns void
language plpgsql security definer set search_path = '' as $$
declare
  yo uuid := (select auth.uid());
begin
  if yo is null then
    raise exception 'sin sesión' using errcode = '42501';
  end if;
  delete from public.comentarios where user_id = yo;
  delete from public.valoraciones where user_id = yo;
  delete from public.perfiles where user_id = yo;
end $$;
revoke all on function public.retirar_mis_datos() from public;
grant execute on function public.retirar_mis_datos() to authenticated;

commit;
