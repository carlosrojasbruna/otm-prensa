-- OTM-Prensa · sitio docente · migración 0001: tablas
-- Fuente de reglas: GOB01 §5 (cuenta requerida para valorar y comentar; perfil docente
-- opcional en el piloto; aviso de uso de datos; moderación previa; derecho a editar o retirar).
-- Requiere un proyecto Supabase (esquema `auth` y roles `anon`/`authenticated`).

-- ---------------------------------------------------------------- perfiles
-- Perfil docente. Piloto: todos los campos son OPCIONALES (nulos permitidos).
-- Versión final: pasarán a requeridos y se agregará `pais` [D]; ver db/README.md.
-- `aviso_version` registra la versión del aviso de uso de datos que la persona aceptó.
create table public.perfiles (
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
create table public.valoraciones (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users (id) on delete cascade default auth.uid(),
  tarea_id       text not null check (tarea_id ~ '^[0-9]{4}-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$'),
  tarea_version  integer not null check (tarea_version >= 1),
  puntaje        smallint not null check (puntaje between 1 and 5),
  creado         timestamptz not null default now(),
  actualizado    timestamptz not null default now(),
  unique (user_id, tarea_id)           -- una valoración vigente por docente y tarea
);
create index valoraciones_tarea_idx on public.valoraciones (tarea_id);

-- --------------------------------------------------------------- comentarios
create table public.comentarios (
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
create index comentarios_tarea_estado_idx on public.comentarios (tarea_id, estado);
create index comentarios_user_idx on public.comentarios (user_id);

-- --------------------------------------------------------------- moderadores
-- Quienes pueden aprobar o rechazar comentarios. Se agregan a mano desde el editor SQL
-- (rol postgres); ninguna política permite escribirla desde la API pública.
create table public.moderadores (
  user_id  uuid primary key references auth.users (id) on delete cascade,
  creado   timestamptz not null default now()
);

-- ---------------------------------------------------------- marca de tiempo
create function public.tocar_actualizado() returns trigger
language plpgsql set search_path = '' as $$
begin
  new.actualizado := now();
  return new;
end $$;

create trigger perfiles_actualizado before update on public.perfiles
  for each row execute function public.tocar_actualizado();
create trigger valoraciones_actualizado before update on public.valoraciones
  for each row execute function public.tocar_actualizado();
create trigger comentarios_actualizado before update on public.comentarios
  for each row execute function public.tocar_actualizado();
