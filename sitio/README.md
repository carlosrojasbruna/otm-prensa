# Sitio OTM-Prensa (`sitio/`)

Sitio estático (Astro) para docentes, con una capa de cuentas sobre Supabase. El código es MIT; el contenido de las tareas es CC BY-NC-SA 4.0 (`tareas/LICENSE.md`).

**Estado (2026-10-21):** en producción en https://carlosrojasbruna.github.io/otm-prensa/ (GitHub Pages, desplegado por `.github/workflows/deploy.yml`). Las migraciones de Supabase las aplica el job `migraciones` de ese workflow, y el job `staging` verifica el flujo de cuentas en cada despliegue. Lighthouse corre como informe y no bloquea. Los pendientes están al final de este documento.

## Estructura

```
sitio/
  package.json          workspaces: web, api. Se instala con `npm ci` (ver Instalación)
  package-lock.json     versionado; CI instala con `npm ci`
  .env.example          plantilla de variables públicas (ver «Variables de entorno»)
  .gitignore            excluye api/.local-data/ (datos del backend local)
  web/                  Astro: home, explorar, tareas/<mes>/<slug>, cuenta, moderación, cómo usar, acerca, 404
    src/lib/catalogo.js            lee tareas/catalogo.json y tareas/<ruta>/* en build (no codifica ids)
    src/lib/semana.js              regla de «Tarea de la semana»
    src/config/tarea_semana.json   fijación manual de la tarea de la semana (moderador)
    src/scripts/cliente.js         elige el backend según las variables públicas
    scripts/                       local.mjs, lighthouse.mjs, staging.mjs, test.mjs, chrome.mjs
    tests/                         node:test, con fixtures sintéticos en tests/fixtures
  api/                  adaptadores de backend con la misma interfaz
    src/index.js          fábrica: resolverModo() y crearBackend()
    src/supabase.js       modo supabase (@supabase/supabase-js; solo URL y clave publicable)
    src/local.js          cliente del backend simulado
    src/local/server.mjs  backend simulado (Node, sin dependencias; datos en un JSON) y servidor estático
    src/comun.js          validaciones, AVISO_USO_DATOS y AVISO_VERSION
  db/                   migraciones SQL (0001 tablas, 0002 RLS, 0003 funciones), aplicar_todo.sql y su generador. Ver db/README.md
```

## Requisitos

- **Node 22** (la versión que usa CI).
- **Chrome o Edge** instalado, para las pruebas de navegador, Lighthouse y el staging con `--url`. Ningún script descarga un navegador. Si no está en una ruta típica, define `CHROME_PATH` con su ubicación. En GitHub Actions se usa el `google-chrome` del runner.

## Instalación

```bash
cd sitio
npm ci          # instala web y api según package-lock.json
```

`npm ci` es el comando que usan `ci.yml` y `deploy.yml`. `npm install` también funciona, pero puede cambiar `package-lock.json`; úsalo solo cuando cambies dependencias.

## Comandos

Todos se corren desde `sitio/web`, salvo la instalación:

```bash
cd sitio/web
npm run build        # genera dist/: home, explorar, una página por tarea del catálogo
npm run dev          # servidor de desarrollo (astro dev)
npm run preview      # sirve dist/ (astro preview)
npm test             # pruebas (ver «Pruebas»)
npm run lighthouse   # Lighthouse sobre dist/ (móvil y escritorio); escribe web/lighthouse/
npm run local        # build con backend simulado y servidor en http://127.0.0.1:8787
npm run staging      # verificación contra Supabase real (ver «Staging»)
```

`npm run lighthouse` acepta `--dir <carpeta>` (por defecto `dist`), `--umbral <n>` (por defecto 90) y `--url <URL>` para auditar el sitio publicado en lugar de `dist/`.

## Variables de entorno

`sitio/.env.example` es una plantilla con las variables públicas. No se lee sola: Astro lee el `.env` de la raíz del proyecto, que es `sitio/web`. Para usarla en local, cópiala a `sitio/web/.env` (el patrón `.env` está en `.gitignore`). En GitHub Pages las variables no vienen de un archivo: `deploy.yml` las define en el paso de build.

| Variable | Dónde se usa | Qué hace |
|---|---|---|
| `PUBLIC_SUPABASE_URL` | build (`web/src/scripts/cliente.js`, `api/src/index.js`) | URL del proyecto Supabase. Junto con la clave publicable, activa el modo `supabase`. Es pública por diseño |
| `PUBLIC_SUPABASE_ANON_KEY` | igual | Clave publicable de Supabase. El nombre es el heredado («anon»); en GitHub el secret se llama `SUPABASE_PUBLISHABLE_KEY`. Nunca se usa la clave de servicio |
| `PUBLIC_BACKEND` | build | `supabase`, `local` o `none`. Si se define, gana sobre la deducción por URL y clave (ver «Selección de backend») |
| `PUBLIC_LOCAL_API_URL` | build | URL base del backend local. Vacía significa el mismo origen. La fijan `npm run local` y las pruebas |
| `PUBLIC_REPO_URL` | build (`tareas/[mes]/[slug]`) | Enlace «Ver en repositorio», sin barra final. Opcional |
| `SITE_URL` | `web/astro.config.mjs` | URL pública del sitio (canonical y sitemap). En Pages: `https://<dueño>.github.io` |
| `SITE_BASE` | `web/astro.config.mjs` | Ruta base. En Pages: `/otm-prensa/` (el nombre del repositorio) |
| `OTM_OUT_DIR` | `web/astro.config.mjs` | Carpeta de salida del build. Por defecto `dist` |
| `OTM_REPO_ROOT` | `web/src/lib/catalogo.js` | Raíz del repositorio que contiene `tareas/`. Por defecto, dos niveles por encima de `sitio/web` |
| `OTM_LOCAL_PORT` | `npm run local` y `api/src/local/server.mjs` | Puerto del backend local. Por defecto 8787 |
| `OTM_LOCAL_MODERADORES` | igual | Correos de moderadores, separados por coma. Si no se define, `npm run local` usa `moderador@ejemplo.cl` |
| `OTM_LOCAL_DATA` | igual | Archivo JSON del backend local. Por defecto `sitio/api/.local-data/db.json` |
| `CHROME_PATH` | pruebas, Lighthouse y staging con `--url` | Ruta o nombre del ejecutable de Chrome o Edge |
| `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SERVICE_KEY` | solo `npm run staging` | Credenciales del staging. La clave de servicio no entra nunca al build ni a las pruebas |

## Selección de backend

La decide `resolverModo()` en `api/src/index.js`:

- `PUBLIC_BACKEND=local` usa el backend simulado. `PUBLIC_BACKEND=none` no usa backend.
- `PUBLIC_BACKEND=supabase` usa Supabase si hay URL y clave publicable; si faltan, queda en `none`.
- Sin `PUBLIC_BACKEND`, el modo es `supabase` cuando existen `PUBLIC_SUPABASE_URL` y `PUBLIC_SUPABASE_ANON_KEY`, y `none` en otro caso.

En modo `none` la lectura y la descarga funcionan, y los formularios avisan de que las cuentas no están habilitadas.

Cada adaptador tiene la misma interfaz. `supabase.js` lanza `sin_configuracion` si faltan la URL o la clave.

## Backend local simulado

`npm run local` (desde `sitio/web`) construye el sitio con `PUBLIC_BACKEND=local`, en `dist-local/`, y sirve sitio y API en el mismo puerto: <http://127.0.0.1:8787/>.

- Para moderar, regístrate con un correo listado en `OTM_LOCAL_MODERADORES` y entra a `/moderacion/`.
- Datos en `sitio/api/.local-data/db.json` (ignorado por git).
- Reglas que reproduce el backend simulado (según su cabecera en `api/src/local/server.mjs`): cuenta requerida; una valoración por docente y tarea; los comentarios nacen `pendiente` y solo se ven `aprobado`; editar un comentario lo devuelve a moderación; solo los moderadores moderan; cada cual puede retirar sus propios datos.

## Build y despliegue

`npm run build` lee `tareas/catalogo.json` y `tareas/<ruta>/` al construirse. Una tarea nueva aparece en el sitio con el build siguiente, que corre al hacer push a `main`.

`.github/workflows/deploy.yml` corre con cada push a `main` y a mano. Sus jobs, en orden:

1. **`migraciones`** comprueba que `sitio/db/aplicar_todo.sql` esté al día (`node sitio/db/generar_aplicar_todo.mjs --check`) y aplica el SQL con `psql` usando `SUPABASE_DB_URL` (la cadena del Session pooler). Si `psql` falla, deja un aviso y el despliegue sigue.
2. **`sitio`** instala con `npm ci` y construye `sitio/web` con `PUBLIC_SUPABASE_URL` y `PUBLIC_SUPABASE_ANON_KEY` tomadas de los secrets `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY`, además de `SITE_URL`, `SITE_BASE=/<nombre del repositorio>/` y `PUBLIC_REPO_URL`. Nunca usa la clave de servicio.
3. **`publicar`** despliega `dist/` en GitHub Pages. La fuente de Pages debe ser «GitHub Actions» (Settings > Pages).
4. **`staging`** corre `npm run staging -- --url <URL pública>` y, después, Lighthouse sobre la URL pública como informe (sube el artefacto `lighthouse-publico`). Si Lighthouse queda bajo 90 o falla, deja un aviso y no bloquea.

Para regenerar `aplicar_todo.sql` después de cambiar una migración, corre `node sitio/db/generar_aplicar_todo.mjs` desde la raíz del repositorio y commitea el resultado. CI y `deploy.yml` fallan si el archivo no coincide con las migraciones. Los secrets y su alcance están en [`docs/secrets.md`](../docs/secrets.md).

## Staging

`npm run staging` (desde `sitio/web`) lee `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` y `SUPABASE_SERVICE_KEY` del entorno. Si falta alguna, sale con código 3.

No hay un proyecto de staging separado en el repositorio: la verificación corre contra el proyecto Supabase real que usa el sitio. Crea un usuario temporal (`otm-staging+<marca>@example.invalid`), inicia sesión con la clave publicable, valora y comenta una tarea, comprueba que el comentario queda `pendiente` y no es visible al público, lo aprueba con una cuenta moderadora temporal y comprueba que ya se ve. Al final borra todo lo que creó, aunque falle a mitad.

Con `--url <URL pública>` la valoración y el comentario se hacen por la interfaz en Chrome headless. Sin `--url`, se hacen por API.

Códigos de salida: `0` todo bien; `1` falla una comprobación; `2` las migraciones no están aplicadas; `3` faltan variables. Si la limpieza falla, el script avisa del usuario que queda por borrar a mano en Supabase > Authentication.

## Tarea de la semana

La regla está en `web/src/lib/semana.js`. Entre las tareas del catálogo (todas están publicadas):

1. Si el moderador fijó una tarea en `web/src/config/tarea_semana.json` que existe y no está vencida, gana esa.
2. Si no, la de mayor `rub01_total`.
3. Empate: la de `fecha_publicacion` más reciente.
4. Empate: la de fecha de commit de publicación (campo `commit` de la entrada, leído de git en el build) más reciente.
5. Empate, o si git no tiene el historial: el `id` en orden alfabético.

El build imprime qué tarea eligió y con qué criterio (`[tarea de la semana] <id> (<criterio>)`), y avisa cuando una fijación no se puede aplicar.

**Fijarla a mano (moderador).** Edita `web/src/config/tarea_semana.json` por commit o PR. El sitio es estático: la fijación no se lee de Supabase.

```json
{ "fijada": "2026-10-pagar-trasladar-o-esperar", "fijada_por": "Carlos Rojas Bruna",
  "fecha": "2026-10-21", "hasta": "2026-10-28", "motivo": "Coincide con la noticia del día" }
```

`fijada` es el `id` del catálogo. `hasta` (AAAA-MM-DD, inclusivo) puede ser `null`, que significa sin vencimiento. Para desfijarla, pon `"fijada": null` o deja que venza `hasta`. Si `fijada` no existe en el catálogo o `hasta` ya pasó, el build la ignora y aplica la regla. Para que el cambio se vea hay que reconstruir y publicar el sitio.

**Problema conocido:** `deploy.yml` hace checkout sin `fetch-depth: 0`, así que el build de producción no tiene el historial de git. El paso 4 no puede leer las fechas de commit y, si hay empate en `rub01_total` y `fecha_publicacion`, la tarea sale por el paso 5. Los workflows de tramo A, tramo B y publicación sí traen el historial completo.

## Pruebas

`npm test` (desde `sitio/web`) tarda cerca de un minuto y corre los archivos de `tests/` en serie.

| Archivo | Cubre |
|---|---|
| `catalogo.test.mjs` | cada tarea del catálogo real tiene página, cita completa, licencia, descargas existentes e idénticas a `tareas/`; el HTML de la tarea solo contiene texto que ya está en `tareas/` |
| `versiones.test.mjs` | fixtures (no toca `tareas/`): `versiones_anteriores` con archivos, catálogo 1.0 sin `tarea_md` ni `guia_md`, dos tareas |
| `semana.test.mjs` | regla de «Tarea de la semana» con fixtures sintéticos: mayor RUB01, desempates, fijación válida, inexistente y vencida |
| `e2e.test.mjs` | Chrome headless: cuenta, valorar, comentar, invisible hasta moderar, moderar, visible; aviso de uso de datos en los formularios |
| `api-local.test.mjs` | semántica del backend simulado |
| `db-rls.test.mjs` | migraciones y RLS reales sobre PGlite (Postgres embebido, con el esquema `auth` simulado) |
| `db-aplicar-todo.test.mjs` | `aplicar_todo.sql` coincide con el generador, va en una transacción y se puede aplicar dos veces sin error |
| `supabase-adapter.test.mjs` | el adaptador Supabase contra un `fetch` simulado |
| `staging.test.mjs` | `verificarStaging` contra un Supabase simulado en memoria: flujo completo, limpieza aunque falle, migraciones no aplicadas, ninguna clave impresa |

CI corre `npm test` en el job `sitio` de `ci.yml`, después de `npm ci` y de la comprobación de `aplicar_todo.sql`.

## Moderación

Los comentarios de Supabase nacen `pendiente` y solo se ven cuando un moderador los aprueba. Un moderador es una fila en `public.moderadores`, que se agrega desde el SQL Editor. Las funciones `comentarios_pendientes()` y `moderar_comentario(...)` y la página `/moderacion/` están descritas en [`db/README.md`](db/README.md). La moderación en local está en «Backend local simulado».

## Pendientes

1. **Aviso de uso de datos.** El texto final (`AVISO_USO_DATOS` en `api/src/comun.js`, versión `AVISO_VERSION`) requiere revisión de ética y, si corresponde, una enmienda al protocolo del CEC UC. Está marcado como pendiente antes de CP3 (`pipeline/state/CP3_informe.md`). Cambiar el texto obliga a subir la versión.
2. **Configuración de Auth en Supabase.** La Site URL, las Redirect URLs y la protección contra abuso (límite de tasa o CAPTCHA) están en el panel de Supabase y no se pueden comprobar desde el repositorio. Revísalas antes de abrir las cuentas al público.
3. **Tarea de la semana en producción** (ver el problema conocido de arriba): falta `fetch-depth: 0` en `deploy.yml`.
