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
create function public.es_moderador() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.moderadores m where m.user_id = (select auth.uid()));
$$;
revoke all on function public.es_moderador() from public;
grant execute on function public.es_moderador() to authenticated;

-- ---------------------------------------------------------------- perfiles
grant select, insert, delete on public.perfiles to authenticated;
grant update (nivel_ensenanza, tipo_establecimiento, region, anios_experiencia, aviso_version)
  on public.perfiles to authenticated;

create policy perfiles_leer_propio on public.perfiles
  for select to authenticated using (user_id = (select auth.uid()));
create policy perfiles_crear_propio on public.perfiles
  for insert to authenticated with check (user_id = (select auth.uid()));
create policy perfiles_editar_propio on public.perfiles
  for update to authenticated
  using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
create policy perfiles_retirar_propio on public.perfiles
  for delete to authenticated using (user_id = (select auth.uid()));

-- ------------------------------------------------------------ valoraciones
grant select, insert, delete on public.valoraciones to authenticated;
grant update (puntaje, tarea_version) on public.valoraciones to authenticated;

create policy valoraciones_leer_propia on public.valoraciones
  for select to authenticated using (user_id = (select auth.uid()));
create policy valoraciones_crear_propia on public.valoraciones
  for insert to authenticated with check (user_id = (select auth.uid()));
create policy valoraciones_editar_propia on public.valoraciones
  for update to authenticated
  using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
create policy valoraciones_retirar_propia on public.valoraciones
  for delete to authenticated using (user_id = (select auth.uid()));

-- ------------------------------------------------------------- comentarios
-- Lectura: el autor ve todos los suyos (con su estado); moderadores ven todos.
-- El público NO lee esta tabla: usa public.comentarios_aprobados() (0003).
grant select, insert, delete on public.comentarios to authenticated;
grant update (texto, nivel_implementado) on public.comentarios to authenticated;

create policy comentarios_leer_propio on public.comentarios
  for select to authenticated
  using (user_id = (select auth.uid()) or (select public.es_moderador()));
-- Alta: siempre `pendiente` y sin datos de moderación.
create policy comentarios_crear_propio on public.comentarios
  for insert to authenticated
  with check (user_id = (select auth.uid())
              and estado = 'pendiente'
              and moderado_por is null and moderado_en is null and motivo_moderacion is null);
-- Edición: solo texto y nivel (privilegio por columna). El trigger devuelve el comentario
-- a `pendiente` para que una edición vuelva a pasar por moderación.
create policy comentarios_editar_propio on public.comentarios
  for update to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));
create policy comentarios_retirar_propio on public.comentarios
  for delete to authenticated using (user_id = (select auth.uid()));

create function public.comentario_reinicia_moderacion() returns trigger
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
create trigger comentarios_reinicia_moderacion before update on public.comentarios
  for each row execute function public.comentario_reinicia_moderacion();

-- -------------------------------------------------------------- moderadores
-- Sin política ni privilegios: tabla invisible para la API pública.
