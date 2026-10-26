# OTM-Prensa

Observatorio de Tareas de Modelamiento desde la Prensa. Un pipeline de agentes toma noticias de medios reconocidos y las convierte en tareas de modelamiento matemático. Cada tarea se evalúa con una rúbrica (RUB01: 12 criterios, máximo 24 puntos), se prueba con un simulador multiagente de estudiantes y recibe una guía docente cuyos escenarios se respaldan con corridas del simulador. Las tareas publicadas quedan versionadas en `tareas/` y se muestran en un sitio para docentes, donde se valoran y comentan.

Proyecto de Carlos Rojas Bruna, Facultad de Matemáticas, Pontificia Universidad Católica de Chile.

Sitio publicado: https://carlosrojasbruna.github.io/otm-prensa/

## Estado (2026-10-21)

Piloto. CP3 aprobado por Carlos el 2026-10-21 (informe: `pipeline/state/CP3_informe.md`).

- **Sitio:** en producción en GitHub Pages. El despliegue `deploy.yml` (ejecución 39593763840) completó sus cuatro jobs, incluido el de staging contra Supabase.
- **Tareas publicadas:** 4, en `tareas/2026-10/` (índice en `tareas/catalogo.json`): `adelantar-compras-queso` (v3), `viaje-barco-ida-vuelta` (v2), `pagar-trasladar-o-esperar` (v5) y `anticipo-renta-vitalicia` (v7). Entraron por los PR #1 y #2.
- **Ciclo semanal:** `semanal.yml` corre el tramo A (hasta `evaluada`) los lunes a las 09:17 UTC. La prueba de aceptación en Actions (ejecución 39593513149) pasó con una tarea y 0,65 USD. Su PR (#3) se revisó y se cerró sin merge. La rama `semanal/2026-W43` se conserva porque su gasto sigue contando para el tope semanal.
- **Tramo B:** `tramo_b.yml` necesita los secrets `SIM_REPO` y `SIM_REPO_TOKEN`, que apuntan al repositorio privado `carlosrojasbruna/otm-simulador` (el simulador no es público). La comprobación `solo_comprobar` pasó en Actions (ejecución 39600145692). Hasta hoy, los tramos B se corrieron en local.
- **Publicación:** `publicar.yml` abre el PR que agrega una tarea a `tareas/`. Se probó con un dry-run y con rechazos reales. Aún no ha publicado una tarea nueva. Al mergear ese PR, `publicada.yml` pasa sus expedientes de `verificada` a `publicada` (implementado; el repositorio no registra todavía una ejecución real de este paso). Detalle en `docs/operacion.md`, sección 5.6.

## Cómo funciona

1. **Tramo A (automático, lunes).** El explorador lee los medios de `insumos/medios/` (MED01), el filtro descarta lo no modelable, el diseñador propone dos candidatos por noticia y el evaluador puntúa cada uno tres veces (mediana por criterio). La tarea llega a `evaluada`.
2. **Revisión humana 1.** Quien revisa lee la tarea y su evaluación en el PR semanal y decide si pasa al tramo B.
3. **Tramo B (manual).** El simulador corre seis corridas con estudiantes que solo reciben el enunciado. El redactor escribe la guía por secciones, el ilustrador genera el ícono y el verificador contrasta cifras y afirmaciones con la noticia. La tarea llega a `verificada`.
4. **Revisión humana 2.** Quien revisa lee la guía y la verificación.
5. **Publicación.** `publicar.yml` (lanzado a mano) ejecuta el bibliotecario, un script sin modelo que escribe `tareas/AAAA-MM/<slug>/` y actualiza `tareas/catalogo.json`, y abre un PR. Al hacer merge, `publicada.yml` pasa los expedientes del PR a `publicada` y `deploy.yml` reconstruye el sitio.

Estados de un expediente: `evaluada → revisada → simulada → con_guia → verificada → publicada`, con `archivada` como salida. El detalle de cada paso y de cada workflow está en [`docs/operacion.md`](docs/operacion.md).

## Estructura del repositorio

| Carpeta | Contenido |
|---|---|
| `CLAUDE.md` | Reglas del repositorio: invariantes, convenciones y checkpoints |
| `plan/` | Plan de construcción por fases (`PLAN-CONSTRUCCION.md`) |
| `insumos/` | Fuente única de verdad, de solo lectura: rúbricas, marcos, plantillas, tareas-oro, medios (MED01), gobernanza y contrato del simulador |
| `contratos/` | Esquemas JSON de los artefactos (`noticia`, `tarea`, `evaluacion`, `evaluacion_rub01`, `guia`, `trazas_resumen`, `catalogo`) y ejemplos válidos e inválidos |
| `pipeline/` | Orquestador (`orquestador.py`), ciclo (`ciclo.py`), invariantes (`invariantes.py`), publicación (`publicar.py`), marca de publicadas (`marcar_publicadas.py`), agentes (`agentes/`), configuración (`config.yaml`) y estado (`state/`) |
| `simulador/adapter/` | Adaptador del simulador externo. `sim.py` no está en este repositorio |
| `evals/` | Calibración del evaluador (`calibrar_evaluador.py`), matriz modelo × agente (`run.py`), casos de prueba y resultados |
| `tareas/` | Tareas publicadas (`AAAA-MM/<slug>/`) y el catálogo. Licencia CC BY-NC-SA 4.0 (`tareas/LICENSE.md`) |
| `sitio/` | Sitio docente: `web/` (Astro y pruebas), `api/` (adaptadores de backend) y `db/` (migraciones SQL y RLS). Ver `sitio/README.md` |
| `.claude/` | Agentes de construcción, comandos de Claude Code y el hook que aplica las invariantes |
| `.githooks/` | Hook de `pre-commit` (opcional, se activa por clon) |
| `.github/workflows/` | `semanal.yml`, `tramo_b.yml`, `publicar.yml`, `publicada.yml`, `ci.yml` y `deploy.yml` |
| `tests/` | Pruebas de Python (`pytest`) |
| `docs/` | Guías: `operacion.md`, `contribuir.md` y `secrets.md` |

## Invariantes

El pipeline se rige por ocho invariantes. El texto completo está en [`CLAUDE.md`](CLAUDE.md). En resumen:

1. Ningún artefacto cambia de estado sin validar contra su esquema en `contratos/`.
2. Ninguna tarea llega a `revisada` con RUB01 menor que 20/24 o con algún criterio en 0.
3. Ningún archivo del repositorio contiene más de 25 palabras consecutivas del cuerpo de una noticia. Las noticias se citan (medio, título, fecha, URL) y se resumen en 80 palabras o menos. El titular se cita completo y queda fuera del conteo desde la versión 1.2 del contrato `noticia` (decisión del 2026-10-20; lo aplica `pipeline/invariantes.py::cumple_limite_literal`).
4. Ninguna cifra de una tarea aparece sin localizador en la noticia o en el notebook de escenarios.
5. Ningún escenario de guía docente existe sin el id de una corrida del simulador que lo respalde.
6. Los agentes-estudiante del simulador reciben solo `enunciado_es`, `foto_descripcion` y los recursos a solicitud; nunca `task_space`.
7. Ningún commit contiene secretos. Las claves se leen de variables de entorno.
8. Cada ejecución del pipeline registra en `evaluacion.json` el modelo y la versión de cada agente, la versión de prompt, de rúbrica, de MAR03 y de MED01, el diseño del simulador, la fecha y el costo.

Las invariantes se comprueban con el hook `.claude/hooks/otm_hook.py`, que reutiliza el código del orquestador. CI las revisa sobre todo el repositorio.

## Instalación local

Requisitos: Python 3.12 (la versión de CI), Node 22 (la versión de CI), Git y Chrome o Edge instalado, solo para las pruebas de navegador y Lighthouse. Ningún script descarga un navegador. Si Chrome no está en una ruta típica, define `CHROME_PATH` con su ubicación.

```bash
git clone https://github.com/carlosrojasbruna/otm-prensa.git
cd otm-prensa
python -m pip install -r requirements.txt
git config core.hooksPath .githooks
```

Para el sitio:

```bash
cd sitio
npm ci
```

`npm ci` desde `sitio/` instala los dos workspaces (`web` y `api`).

### Variables de entorno

Los valores nunca van en el repositorio. Los nombres son:

- `OTM_API_KEY`: clave de la API de Anthropic en la máquina local. Todo script del pipeline la lee primero. No definas `ANTHROPIC_API_KEY` en la máquina local: Claude Code dejaría de usar el plan de claude.ai. Comprueba la clave sin imprimirla con `python pipeline/apikey.py` (responde `ok` o `falta`).
- `ANTHROPIC_API_KEY`: solo en GitHub Actions, como secret del repositorio con ese nombre.
- `CHROME_PATH`: opcional. Ruta o nombre del ejecutable de Chrome para las pruebas de navegador.
- `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` y `SUPABASE_SERVICE_KEY`: solo para `npm run staging`. La clave de servicio no se usa nunca en el sitio ni en las pruebas. La plantilla de las variables públicas del sitio está en `sitio/.env.example`.

La lista completa de secrets, quién los crea y qué los usa está en [`docs/secrets.md`](docs/secrets.md).

### El simulador

El simulador (`sim.py`, con sus `insumos/`) vive en un repositorio privado y no es necesario para el tramo A ni para las pruebas. Solo lo necesita el tramo B en local. `pipeline/config.yaml` lo busca en `simulador.repo: "../../IDEA MODELAMIENTO/simulacion"`, relativo a la raíz del repositorio: la carpeta `IDEA MODELAMIENTO` debe estar dos niveles por encima de la raíz, con `simulacion/sim.py` dentro.

## Pruebas

```bash
python -m pytest -q                  # desde la raíz; clientes falsos: sin red y sin costo
cd sitio/web
npm test                             # pruebas del sitio (node:test)
```

Las pruebas de navegador necesitan Chrome o Edge (`CHROME_PATH`). Si no se encuentra, `sitio/web/scripts/chrome.mjs` lanza «No se encontró Chrome/Edge». CI ejecuta las pruebas de Python y del sitio, y además valida los contratos y las invariantes sobre todo el repositorio (ver [`docs/contribuir.md`](docs/contribuir.md), sección 7).

## Una corrida de prueba

**Prueba 1: sin red y sin costo.** Comprueba que la instalación funciona y que la noticia de prueba cumple su contrato:

```bash
python -m pipeline.invariantes esquema noticia evals/casos/ciclo/noticia_prueba_actions.json
python .claude/hooks/otm_hook.py repo
python -m pipeline.ciclo --estado
```

- El primer comando no imprime nada si el archivo cumple. Si no cumple, imprime los errores y sale con código 2.
- El segundo recorre el repositorio con las invariantes. Debe terminar con `[otm-hook] invariantes ok (repositorio)`.
- El tercero lista un expediente por línea, con su estado.

**Prueba 2: con la API (cuesta dinero, entre 0,6 y 0,9 USD).** Corre el tramo A sobre la noticia sintética de prueba, con una tarea y un tope de 2 USD para el ciclo. Requiere `OTM_API_KEY`:

```bash
python -m pipeline.ciclo --noticia evals/casos/ciclo/noticia_prueba_actions.json --max-tareas 1 --presupuesto-ciclo 2
```

Resultado esperado: el expediente llega a `evaluada` con la marca `revision_humana_1` pendiente y no se publica nada. Es normal que aparezca el aviso `invariante3_sin_texto`: la noticia de prueba apunta a `example.org` y el ciclo no puede releerla, así que sigue sin comprobar la invariante 3 con texto real.

La prueba 2 escribe en `pipeline/state/` (expedientes, carpeta de trabajo, registro del ciclo y `gasto_semanal.json`). Esos archivos están versionados. No los commitees salvo que la prueba sea parte de un cambio que quieras proponer.

## Documentación

- [`docs/operacion.md`](docs/operacion.md): cómo corre la semana, cómo se lanza cada workflow desde la web de GitHub, cómo se revisa cada paso, la publicación y el paso automático a `publicada`, costos, despliegue, moderación, recalibración del evaluador y qué hacer cuando algo falla.
- [`docs/contribuir.md`](docs/contribuir.md): convenciones de nombres y commits, cómo activar los hooks, cómo cambiar un agente, cómo proponer una tarea o corregir una guía por PR, y qué revisa CI.
- [`docs/secrets.md`](docs/secrets.md): secrets, variables de entorno y rotación.
- [`sitio/README.md`](sitio/README.md): el sitio: instalación, variables, backends, despliegue, staging, «Tarea de la semana», pruebas y pendientes.
- [`sitio/db/README.md`](sitio/db/README.md): migraciones de Supabase y moderación.
- [`CLAUDE.md`](CLAUDE.md): reglas del repositorio.
- [`plan/PLAN-CONSTRUCCION.md`](plan/PLAN-CONSTRUCCION.md): fases, agentes de construcción y checkpoints.

## Licencias

Código bajo licencia MIT (`LICENSE`). Las tareas y los materiales de `tareas/` bajo CC BY-NC-SA 4.0 (`tareas/LICENSE.md`).
