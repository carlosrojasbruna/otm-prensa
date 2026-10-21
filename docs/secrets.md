# Secrets de OTM-Prensa

Ningún valor vive en el repo, en los insumos ni en los logs. En GitHub Actions se cargan como *repository secrets* (Settings > Secrets and variables > Actions). En la máquina local se leen de variables de entorno. Esta página dice cuáles son, quién los crea, qué los usa y con qué alcance. Referencia: GOB01 §7; invariante 7 de `CLAUDE.md`.

Los workflows comprueban **en tiempo de ejecución** que los secrets que necesitan existan (el token local no puede listarlos) y fallan con un mensaje claro (`::error title=Faltan secrets::...`) sin imprimir ningún valor.

## Tabla

| Secret | Qué es | Lo crea | Lo usan | Ámbito |
|---|---|---|---|---|
| `ANTHROPIC_API_KEY` | API key de Anthropic Console (cuenta de Carlos) | Carlos | `semanal.yml` (job `ciclo`), `tramo_b.yml`; scripts del pipeline vía `pipeline/apikey.py` | Solo el paso que corre `python -m pipeline.ciclo`; nunca en `ci.yml` ni `deploy.yml` |
| `GH_TOKEN` | Token fino de GitHub (GOB01 §4): `contents`, `pull_requests`, `actions`, `pages` (lectura/escritura) | Carlos | `semanal.yml` y `tramo_b.yml` (checkout con push, `gh pr create`/`comment`); bibliotecario | Repo `otm-prensa`. Se usa en lugar del `GITHUB_TOKEN` de fábrica porque los PR creados con este último no disparan `ci.yml` |
| `SUPABASE_URL` | URL del proyecto Supabase | Carlos | `deploy.yml` (build como `PUBLIC_SUPABASE_URL`; `staging`) | Pública por diseño (va en el sitio), pero se mantiene como secret por simetría |
| `SUPABASE_PUBLISHABLE_KEY` | Clave publicable (`sb_publishable_...`; antes "anon") | Carlos | `deploy.yml` (build como `PUBLIC_SUPABASE_ANON_KEY`; `staging`) | Pública por diseño: protegida por RLS (`sitio/db/migrations/0002_rls.sql`) |
| `SUPABASE_SERVICE_KEY` | Clave de servicio (`sb_secret_...` / `service_role`): se salta la RLS | Carlos | **Solo** el job `staging` de `deploy.yml` (crear/borrar el usuario de prueba y promoverlo a moderador) | **Nunca en el build del sitio** ni en tests. Si se filtra, rotarla en Supabase (Settings > API) |
| `SUPABASE_DB_URL` | Cadena de conexión Postgres (incluye la contraseña) | Carlos | Job `migraciones` de `deploy.yml` (`psql ... -f sitio/db/aplicar_todo.sql`) | Solo ese paso. Usar la cadena del **Session pooler** de Supabase: los runners de GitHub no tienen IPv6 y la conexión directa (`db.<ref>.supabase.co`) es solo IPv6 |
| `SIM_REPO` | `dueño/repo` del repo externo del simulador (su raíz es la carpeta `IDEA MODELAMIENTO/`) | Carlos (decisión pendiente: publicar código del equipo es irreversible) | `tramo_b.yml` | Opcional. Sin él (o sin `SIM_REPO_TOKEN`) el tramo B queda deshabilitado con un aviso |
| `SIM_REPO_TOKEN` | Token fino de solo lectura (`contents:read`) sobre el repo del simulador | Carlos | `tramo_b.yml` | Solo el checkout del simulador (`persist-credentials: false`) |
| `GITHUB_TOKEN` | Token efímero de cada ejecución (automático) | GitHub | `deploy.yml` (Pages, `id-token`), descargas de artefactos | Permisos mínimos por workflow (`permissions:`). No hay que crearlo |

Claves de medios: ninguna (MED01 usa RSS y Google News RSS, sin clave).

## `OTM_API_KEY` (local) frente a `ANTHROPIC_API_KEY` (Actions)

Todo script del pipeline obtiene la clave con `pipeline/apikey.py`: primero `OTM_API_KEY` y, si no existe, `ANTHROPIC_API_KEY`.

- **Máquina de Carlos**: definir `OTM_API_KEY`. Si se definiera `ANTHROPIC_API_KEY` en el entorno local, Claude Code dejaría de autenticarse con el plan de Carlos (claude.ai) y empezaría a cobrar a la API. Por eso en local nunca se define esa variable.
- **GitHub Actions**: el secret se llama `ANTHROPIC_API_KEY` y el workflow lo expone como variable de entorno con ese nombre; `apikey.py` lo encuentra porque `OTM_API_KEY` no existe allí.

Comprobación sin imprimir el valor: `python pipeline/apikey.py` imprime `ok` o `falta`.

## Variables de build del sitio (derivadas, no son secrets propios)

`deploy.yml` define `PUBLIC_SUPABASE_URL` y `PUBLIC_SUPABASE_ANON_KEY` solo para el paso `npm run build`, a partir de `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY`. Quedan embebidas en el sitio publicado, por eso solo se usan claves públicas. También se fijan `SITE_URL`, `SITE_BASE` y `PUBLIC_REPO_URL` (no sensibles).

## Staging local

`npm run staging` (en `sitio/web`) lee `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` y `SUPABASE_SERVICE_KEY` del entorno (nunca de archivos versionados; `*.env` está en `.gitignore`). Código de salida 3 si falta alguna.

## Protecciones contra fugas

- `ci.yml`: escaneo con `grep` (Anthropic, GitHub) y el hook de invariantes sobre todo el repo (además: JWT, `sb_secret_`, URLs de base de datos con contraseña).
- `.githooks/pre-commit` (opcional, local): mismos controles sobre lo que se va a commitear. Activar una vez por clon con `git config core.hooksPath .githooks`.
- Hook de Claude Code (`.claude/settings.json`): bloquea escribir un secreto en un archivo del repo.
- Los workflows no imprimen valores (`echo` de secrets prohibido por `tests/test_devops.py`); la URL de la base se enmascara con `::add-mask::`.

## Rotación

1. Crear el valor nuevo en el proveedor (Anthropic Console, GitHub, Supabase).
2. Reemplazar el secret en GitHub (y `OTM_API_KEY` en la máquina local, si corresponde).
3. Revocar el valor anterior.
4. Lanzar `deploy.yml` (workflow_dispatch) para comprobar que el entorno sigue sano.
