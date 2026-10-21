# Base de datos del sitio (Supabase / Postgres)

Aplicar en orden en un proyecto Supabase (SQL Editor o `supabase db push`):

1. `migrations/0001_tablas.sql`: `perfiles`, `valoraciones`, `comentarios`, `moderadores`.
2. `migrations/0002_rls.sql`: RLS y privilegios (por columna).
3. `migrations/0003_funciones.sql`: lectura pública, moderación y retiro de datos.

Probadas con `sitio/web/tests/db-rls.test.mjs` (PGlite con un `auth` simulado; no sustituye una prueba en el proyecto real).

## Modelo de acceso (GOB01 §5)

| Qué | Quién | Cómo |
|---|---|---|
| Leer comentarios | público | solo `aprobado`, vía `comentarios_aprobados(tarea_id)`; sin `user_id`; rótulo "Docente" o "Docente · nivel X" |
| Leer valoraciones | público | solo agregados (`resumen_valoraciones()`: n, promedio, distribución) |
| Valorar / comentar | usuario autenticado | filas propias; el comentario nace `pendiente` (la política lo exige) |
| Editar lo suyo | usuario | solo `texto` y `nivel_implementado` del comentario; `puntaje` de la valoración; el comentario editado vuelve a `pendiente` (trigger) |
| Retirar lo suyo | usuario | `delete` de sus filas, o `retirar_mis_datos()` (comentarios, valoraciones, perfil) |
| Ver lo suyo | usuario | `select` de sus filas, con el estado de moderación |
| Moderar | `public.moderadores` | `comentarios_pendientes()` y `moderar_comentario(id, 'aprobado'\|'rechazado', motivo)`; las tablas no son escribibles para nadie más |

`anon` no tiene acceso a ninguna tabla. Ningún dato de perfil se expone con identidad.

## Perfil docente

Piloto: `nivel_ensenanza` (P/S/U), `tipo_establecimiento`, `region`, `anios_experiencia`, todos **opcionales**; `aviso_version` guarda qué aviso aceptó la persona. Versión final (GOB01 §5): los mismos campos pasan a `not null` y se agrega `pais` **[D]**; será una migración nueva (`0004`), no se edita ésta. Hasta que esa decisión se tome, `pais` no existe.

## Moderación

Designar a una persona (rol `postgres`, SQL Editor):

```sql
insert into public.moderadores (user_id)
select id from auth.users where email = 'moderador@ejemplo.cl';
```

Con esa cuenta, entrar a `/moderacion/` del sitio: lista los pendientes y permite aprobar o rechazar. Alternativa directa en SQL:

```sql
select id, tarea_id, texto from public.comentarios where estado = 'pendiente' order by creado;
select public.moderar_comentario('<id>', 'aprobado', null);  -- como usuario moderador
update public.comentarios set estado = 'aprobado', moderado_en = now() where id = '<id>';  -- como postgres
```

Quitar permisos: `delete from public.moderadores where user_id = (select id from auth.users where email = '...');`

## Seguridad

- El cliente solo usa `PUBLIC_SUPABASE_URL` y `PUBLIC_SUPABASE_ANON_KEY`. La `service_role` key no se usa ni se guarda en el repositorio.
- Funciones `security definer` con `search_path = ''` y `execute` concedido solo a los roles necesarios.
- Por revisar en staging: límites de tasa y CAPTCHA de Auth; correo de confirmación.
