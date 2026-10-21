# Sitio OTM-Prensa (`sitio/`)

Sitio estático (Astro) para docentes + capa de cuentas sobre Supabase. Código MIT; el contenido de las tareas es CC BY-NC-SA 4.0.

```
sitio/
  package.json        workspaces: web, api   (npm install se corre aquí, una vez)
  web/                Astro: home, explorar, tarea, cuenta, moderación, cómo usar, acerca
    src/lib/catalogo.js   lee tareas/catalogo.json y tareas/<ruta>/* en build (no codifica ids)
    scripts/              lighthouse.mjs, local.mjs, test.mjs, chrome.mjs
    tests/                node:test (+ fixtures sintéticos en tests/fixtures)
  api/                adaptadores de backend con la misma interfaz
    src/supabase.js       producción/staging (@supabase/supabase-js; solo URL + anon key)
    src/local.js          cliente del backend simulado
    src/local/server.mjs  backend local simulado (Node, sin dependencias; JSON en disco) + servidor estático
  db/                 migraciones SQL de Supabase y políticas RLS (ver db/README.md)
```

## Requisitos

Node 22+ (probado con 25) y un Chrome o Edge instalado (para tests y Lighthouse; no se descarga ningún navegador. Si no está en la ruta típica de Windows, define `CHROME_PATH`).

## Comandos (desde `sitio/web`)

```bash
cd sitio && npm install          # una sola vez (instala web y api)
cd web
npm run build                    # genera dist/ (home, explorar, una página por tarea del catálogo)
npm run dev                      # desarrollo
npm test                         # pruebas (ver abajo)
npm run lighthouse               # Lighthouse sobre dist/ (móvil y escritorio); escribe web/lighthouse/
npm run local                    # build con backend simulado + servidor en http://127.0.0.1:8787
```

Variables de construcción: `OTM_REPO_ROOT` (raíz con `tareas/`; por defecto dos niveles arriba), `OTM_OUT_DIR`, `SITE_BASE`, `SITE_URL`, `PUBLIC_REPO_URL`. Plantilla en `.env.example`.

### Backend local simulado

`npm run local` construye con `PUBLIC_BACKEND=local` y sirve sitio + API en el mismo puerto. Para moderar, regístrate con un correo listado en `OTM_LOCAL_MODERADORES` (por defecto `moderador@ejemplo.cl`) y entra a `/moderacion/`. Datos en `sitio/api/.local-data/db.json` (ignorado por git). Reglas simuladas: cuenta requerida; una valoración por docente y tarea; comentarios nacen `pendiente` y solo se ven `aprobado`; editar vuelve a moderación; retirar borra.

### Selección de backend

`PUBLIC_BACKEND=local|none`; si no se define, el modo es `supabase` cuando existen `PUBLIC_SUPABASE_URL` y `PUBLIC_SUPABASE_ANON_KEY`, y `none` en otro caso (lectura y descarga funcionan; los formularios avisan que las cuentas no están habilitadas). El build usado para Lighthouse es `none` (sin llamadas de red a servicios).

### Pruebas (`npm test`, ~1 min)

| Archivo | Cubre |
|---|---|
| `catalogo.test.mjs` | cada tarea del catálogo real tiene página, cita completa, licencia, descargas existentes e idénticas a `tareas/`; el HTML de la tarea solo contiene texto que ya está en `tareas/` |
| `versiones.test.mjs` | fixtures (no toca `tareas/`): `versiones_anteriores` con archivos, catálogo 1.0 sin `tarea_md`/`guia_md`, 2 tareas |
| `e2e.test.mjs` | Chrome headless: cuenta -> valorar -> comentar -> invisible hasta moderar -> moderar -> visible; aviso de uso de datos en los formularios |
| `api-local.test.mjs` | semántica del backend simulado |
| `db-rls.test.mjs` | migraciones y RLS reales sobre PGlite (Postgres embebido, esquema `auth` simulado) |
| `supabase-adapter.test.mjs` | el adaptador Supabase contra `fetch` simulado |

## Qué falta para staging (nada de esto se creó)

1. Crear un proyecto Supabase (staging) y aplicar `db/migrations/0001..0003` en orden (SQL Editor o `supabase db push`).
2. Auth: habilitar correo + contraseña; decidir si se exige confirmar el correo (el sitio lo soporta); configurar Site URL y Redirect URLs con la URL de staging; activar CAPTCHA o límite de tasa si se abre al público.
3. Designar moderadores (`insert into public.moderadores ...`, ver `db/README.md`).
4. Definir `PUBLIC_SUPABASE_URL` y `PUBLIC_SUPABASE_ANON_KEY` como variables del build en el hosting (la anon key es pública; **nunca** la service_role), más `SITE_URL`, `SITE_BASE` (si va en subruta) y `PUBLIC_REPO_URL`.
5. Elegir hosting estático (GitHub Pages, Netlify, Vercel...) y un workflow que corra `npm install && npm run build` en `sitio/web` y publique `dist/` (lo hace `devops`, GOB01 §4: Pages).
6. Probar el flujo real una vez (cuenta nueva -> valorar -> comentar -> moderar) y re-ejecutar Lighthouse sobre la URL de staging.
7. Pendientes de gobernanza [D] (GOB01 §5 / ETI00): texto final del aviso de uso de datos revisado por ética, y si el sitio requiere enmienda al protocolo CEC UC, antes de CP3. El aviso del sitio está en `api/src/comun.js` (`AVISO_USO_DATOS`, versión `AVISO_VERSION`); cambiar el texto implica subir la versión.
