-- OTM-Prensa · sitio docente · migración 0003: funciones públicas y de moderación

-- ------------------------------------------------------------ lectura pública
-- Agregados de valoración por tarea (sin identificar a nadie).
create function public.resumen_valoraciones()
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
create function public.comentarios_aprobados(p_tarea_id text)
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
create function public.comentarios_pendientes()
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
create function public.moderar_comentario(p_id uuid, p_estado text, p_motivo text default null)
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
create function public.retirar_mis_datos() returns void
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
