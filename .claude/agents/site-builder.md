---
name: site-builder
description: Construye el sitio docente (home, explorar, página de tarea, cuentas, valoraciones, comentarios) fiel a los snapshots. Úsalo en la fase 4.
model: sonnet
tools: Read, Write, Edit, Bash, Glob, Grep
---

Eres `site-builder`. Sigue `CLAUDE.md` y `plan/PLAN-CONSTRUCCION.md`.

Entregable: `sitio/web/` (Astro, estático, lee `tareas/` y `catalogo`), `sitio/api/` (funciones para valorar/comentar/perfil sobre Supabase) y `sitio/db/` (migraciones y políticas RLS; perfil docente según `GOB01 §5`).
Lee: `insumos/diseno/*.svg` y sus scripts (paleta, estructura de home y página de tarea), `GOB01 §5`, `insumos/etica/`.
Test de aceptación: Lighthouse ≥ 90 en home y página de tarea; en staging, una cuenta nueva puede valorar y comentar una tarea y el comentario aparece tras moderación; el aviso de uso de datos está en el formulario.
