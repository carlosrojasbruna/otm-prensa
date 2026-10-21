# Cómo contribuir a OTM-Prensa

Esta guía explica cómo preparar un cambio, qué nombres y commits usar, qué protegen los hooks, qué revisa CI y cómo proponer una tarea o corregir una guía. Lo que no está implementado se marca como **pendiente**.

Antes de cambiar nada, lee [`CLAUDE.md`](../CLAUDE.md). Son las reglas del repositorio y prevalecen sobre esta guía. El repositorio lo opera Carlos Rojas Bruna. Los artefactos de `tareas/` los produce el pipeline y los publica el bibliotecario tras dos revisiones humanas. Por eso casi todo cambio de contenido sigue ese camino (sección 5).

## 1. Antes de empezar

### 1.1 Activar los hooks de git

Una vez por clon:

```bash
git config core.hooksPath .githooks
```

El hook `.githooks/pre-commit` ejecuta `python3 .claude/hooks/otm_hook.py staged`. Si no existe `python3`, usa `python`. Puedes fijar el intérprete con la variable `PYTHON`. Revisa lo que vas a commitear contra las invariantes 1, 2, 3, 5, 6, 7 y 8, y bloquea modificar o borrar archivos de `insumos/`. La invariante 4 la impone el esquema de cada artefacto. Para desactivar el hook: `git config --unset core.hooksPath`.

La invariante 3 se comprueba contra el texto de las noticias solo si defines `OTM_TEXTOS_NOTICIAS` con una carpeta **fuera del repositorio** que contenga los `.txt`. El repositorio nunca guarda el cuerpo de una noticia.

### 1.2 El hook de Claude Code

`.claude/settings.json` registra un hook `PreToolUse` para `Write`, `Edit` y `MultiEdit`. Antes de escribir, comprueba el resultado contra las invariantes y bloquea la edición de un insumo existente en `insumos/`. Si el propio hook falla por un error interno, deja pasar la edición en la sesión; en commit y en CI, el fallo cierra el paso.

El hook no bloquea el borrado de archivos desde la sesión. Ese caso lo cubre el commit.

## 2. Pruebas y validaciones locales

```bash
python -m pip install -r requirements.txt
python -m pytest -q                       # pipeline, contratos, hooks, tope de gasto, publicación
cd sitio && npm ci                        # instala los workspaces web y api
cd web && npm test                        # pruebas del sitio; las de navegador necesitan Chrome o Edge (CHROME_PATH)
```

Para validar un artefacto suelto contra su contrato, sin red:

```bash
python -m pipeline.invariantes esquema <contrato> <archivo.json>
```

`<contrato>` es uno de estos: `noticia`, `tarea`, `evaluacion`, `evaluacion_rub01`, `guia`, `trazas_resumen` o `catalogo`. El comando no imprime nada si el archivo cumple. Si no cumple, imprime los errores y sale con código 2.

Para comprobar las invariantes:

```bash
python .claude/hooks/otm_hook.py repo                        # todo el repositorio (lo que corre CI)
python .claude/hooks/otm_hook.py archivos <ruta> [<ruta>...]  # solo esas rutas
```

## 3. Nombres de archivos y carpetas

- **Entregables e insumos:** `nombre_vX.Y_AAAA-MM-DD.ext`, por ejemplo `tarea_v3.0_2026-10-20.json`. La versión y la fecha van en el nombre. El bibliotecario valida el patrón `^[a-z0-9_]+_vN.N_AAAA-MM-DD\.(json|md|svg)$`.
- **Insumos (`insumos/`):** son de solo lectura. Un cambio es una **versión nueva** con su propia fecha (por ejemplo, `RUB01_calidad-tarea_v4.1_AAAA-MM-DD.json`). Nunca se edita un insumo in situ. Ver la sección 9.
- **Tareas publicadas (`tareas/AAAA-MM/<slug>/`):** la carpeta lleva el **slug base**, sin sufijo `-vN`. Todas las versiones de una tarea viven en esa carpeta, distinguidas por el nombre del archivo: `tarea_v2.0_…json`, `guia_v2.0_…json`, `guia_v2.0_…md`, `evaluacion_v2.0_…json`, `trazas_v2.0_…json` e `icono_v2.0_…svg`.
- **Id de tarea:** `AAAA-MM-slug`, con el patrón `^([0-9]{4})-([0-9]{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$`. El sufijo `-vN` solo aparece en los expedientes del pipeline (`<id>-v<n>`), no en la carpeta publicada.
- **Catálogo:** `tareas/catalogo.json`, validado contra el contrato `catalogo`. Lo escribe el bibliotecario; no se edita a mano.

## 4. Commits y ramas

Los mensajes de commit van en español, con prefijo por área:

| Prefijo | Área |
|---|---|
| `insumos:` | Insumos (nuevas versiones) |
| `contratos:` | Esquemas en `contratos/` |
| `agente/<nombre>:` | Un agente del pipeline (por ejemplo, `agente/evaluador:`) |
| `pipeline:` | Orquestador, ciclo, publicación, configuración y estado del pipeline |
| `tareas:` | Publicación de tareas (lo usa el bibliotecario) |
| `sitio:` | Sitio docente (`sitio/`) |
| `devops:` | Workflows, hooks y secrets |
| `docs:` | Documentación |

Ramas:

- `semanal/<AAAA-WW>`: ciclo semanal (`semanal.yml` y `tramo_b.yml`). Una rama por semana ISO.
- `publicar/<AAAA-MM-DD>-<n>`: PR de publicación lanzado desde `publicar.yml`.
- `tareas/semana-<AAAA-Www>`: prefijo de rama del bibliotecario en su ejecución local (`pipeline/agentes/bibliotecario/config.yaml`). Hoy la publicación desde Actions usa `publicar/`.
- Un cambio manual va en su propia rama y entra a `main` por PR.

## 5. Proponer una tarea

**No hay un canal definido para que personas externas propongan tareas.** En `.github/` no hay plantillas de issue ni `CONTRIBUTING.md`. Es **pendiente de decisión humana**.

Hoy las tareas nacen así:

1. **Por el ciclo semanal (ruta normal).** El explorador lee los medios de `insumos/medios/` (MED01, la versión más alta). El tramo A produce las tareas, que llegan a `evaluada` y pasan por la revisión humana 1 (`docs/operacion.md`, secciones 1 y 3).
2. **Con una noticia ya preparada.** Una noticia como JSON del contrato `noticia` entra con `python -m pipeline.ciclo --noticia <archivo.json>`. Corre en local, con `OTM_API_KEY`, y el ciclo intenta releer la noticia para la invariante 3. Hoy es una vía que opera Carlos.
3. **Revisiones y publicación.** La tarea pasa por la revisión humana 1, el tramo B, la revisión humana 2 y el bibliotecario (`docs/operacion.md`, secciones 4 y 5).

Un PR que agregue a mano una carpeta en `tareas/` **no** pasa por ese camino. El catálogo no se edita a mano, y la publicación exige un expediente en `verificada`, con la revisión humana 2 registrada. CI puede validar el contenido (sección 10), pero no sustituye a las revisiones.

Para proponer un **medio** o una **noticia**, el canal previsto es una versión nueva de MED01 (`insumos/medios/MED01_medios_vX.Y_AAAA-MM-DD.yaml`), que decide una persona.

No hay una vía escrita para que alguien ajeno al equipo proponga una noticia o una tarea. Es **pendiente**: hasta que Carlos lo decida, el repositorio no ofrece un flujo para eso.

## 6. Corregir una guía o una tarea publicada

Las tareas publicadas **no se editan**. La corrección es una **versión nueva en la misma carpeta**, y la v1 se conserva.

El camino que existe hoy es el del pipeline, y corre en local:

- **Defecto de la guía** (redacción, escenario mal respaldado): `python -m pipeline.ciclo --rehacer-guia OBSERVACIONES.json --revisor "Nombre Apellido"`. Exige el expediente en `verificada`. Genera la guía en la versión siguiente.
- **Defecto de la tarea** (enunciado, cifras, supuestos): `python -m pipeline.ciclo --nueva-version MEJORAS.json`. Crea `<id>-v<n>`, lo evalúa de nuevo y lo devuelve a la revisión humana 1.

En ambos casos, después vienen las revisiones humanas y el bibliotecario, que publica la nueva versión en la misma carpeta. El bibliotecario rechaza sobrescribir un archivo existente y rechaza una tarea cuya versión publicada ya exista (`pipeline/agentes/bibliotecario/run.py`). Los comandos y el detalle están en `docs/operacion.md`, sección 5.

**Un PR manual** que edite una guía o tarea publicada no pasa por el bibliotecario. El hook no lo impide: solo protege `insumos/` y revisa las invariantes. **Pendiente:** definir si los PR manuales sobre `tareas/` están permitidos y cómo se revisan. Mientras tanto, trátalos como un cambio de contenido publicado que requiere revisión de Carlos.

## 7. Reglas de contenido

Estas son las invariantes que afectan a quien escribe contenido. Están en `CLAUDE.md`; aquí va cómo aplican.

- **Límite de 25 palabras (invariante 3).** Ningún archivo del repositorio contiene más de 25 palabras consecutivas del cuerpo de una noticia. El resumen propio de la noticia tiene un máximo de 80 palabras. Cada noticia se cita con medio, título, fecha y URL.
- **Titular.** Según `CLAUDE.md` (decisión humana del 2026-10-20) y el contrato `noticia` v1.2, el titular se cita completo y queda fuera del conteo: `cumple_limite_literal` (`pipeline/invariantes.py`) omite el `titulo` de toda cita de noticia (objeto con `medio`, `titulo` y `url`). Copiado fuera de la cita, por ejemplo en el enunciado, sí cuenta. El explorador todavía abrevia a 20 palabras y « …» los titulares de más de 25 (`cita_titulo` en `pipeline/agentes/explorador/run.py`), algo que ya no hace falta (pendiente en `decisiones.md`).
- **No guardes el cuerpo de una noticia.** El hook bloquea nombres de archivo como `texto_noticia*.txt`, `cuerpo_noticia*` o `noticia_texto*` (`.txt` o `.md`). El texto de la noticia solo existe en memoria durante el ciclo.
- **Cifras con localizador (invariante 4).** Toda cifra de una tarea lleva `localizador` (`{fuente: noticia|notebook, ubicacion}`), y toda fuente de `recursos[]` es obligatoria. Lo impone el esquema.
- **Lo que el estudiante recibe de entrada** debe estar escrito en `enunciado_es`, porque el simulador de estudiantes no recibe otros recursos (invariante 6).
- **Secretos (invariante 7).** Ninguna clave va al repositorio: ni de Anthropic, ni de GitHub, ni de Supabase, ni una URL de base con contraseña. Las claves se leen de variables de entorno (`docs/secrets.md`). Los archivos `*.env` están en `.gitignore`. El hook y CI lo bloquean, pero no son el único control.

## 8. Cómo agregar o cambiar un agente

Los agentes viven en `pipeline/agentes/<nombre>/`. Cada carpeta tiene, como mínimo, `run.py` y `config.yaml`. Muchas tienen además `prompt.md` (o `prompt_vX.Y.md` cuando el prompt se versiona), `DECISIONES.md` y un esquema de salida (`salida.schema.json`). El evaluador es la excepción: su lógica está en `evaluador.py` y sus prompts en `prompt_sistema_v<versión>.md`.

Para **cambiar un agente**:

1. **Modelo.** El modelo de cada agente está en `pipeline/config.yaml`, en `modelos:`. Los agentes lo leen a través de `pipeline/llm.py` (`modelo_de(agente)`). No copies el modelo en el código del agente. Un cambio de modelo exige evidencia en `evals/resultados/` y lo decide `build-lead` o Carlos.
2. **Prompt.** Crea una versión nueva del archivo de prompt (`prompt_vX.Y.md`) y sube la versión que el agente registra. La invariante 8 exige que `evaluacion.json` lleve la versión de prompt de cada agente que corrió.
3. **Salida.** Si cambia la forma de la salida, cambia el esquema del agente o el contrato correspondiente. Ver la sección 9.
4. **Precios.** Si entra un modelo nuevo, agrégalo a `precios_modelos` en `pipeline/config.yaml`. Los precios son supuestos hasta que Carlos los confirme.
5. **Pruebas.** Las pruebas de agentes usan clientes falsos: sin red y sin costo. Hoy hay archivos `tests/test_agente_<nombre>.py` para disenador, explorador, filtro, ilustrador, redactor, verificador y bibliotecario. Añade o ajusta las pruebas del agente y corre `python -m pytest -q`.
6. **Matriz.** Si el agente debe medirse con los tres modelos, agrégalo a la lista `AGENTES` de `evals/run.py` y deja sus casos en `evals/casos/<nombre>/`. Prueba la tubería sin gasto con `python evals/run.py --sin-red --agentes <nombre>`.
7. **Decisión.** Anota el cambio en `pipeline/state/decisiones.md` (fecha, agente y alternativa descartada) y en `DECISIONES.md` del agente.

El commit usa el prefijo `agente/<nombre>:`.

## 9. Cambiar un contrato o un insumo

Los **insumos** (`insumos/`) son de solo lectura. Un cambio es un archivo nuevo con versión nueva y fecha (`nombre_vX.Y_AAAA-MM-DD.ext`). Nunca se edita el archivo existente. El hook de commit bloquea modificar o borrar un insumo.

Los **contratos** (`contratos/*.schema.json`) validan los artefactos del pipeline. Su `$id` no lleva versión. Cuando el contrato prevé versiones, la versión se declara dentro del artefacto. Por ejemplo, el catálogo tiene el campo `version_contrato`, con valores `1.0` y `1.1`. El contrato `catalogo` pasó a v1.1 por autorización expresa de Carlos (commit `1654aab`). Un cambio de contrato requiere autorización de Carlos, y debe ir con:

- el esquema actualizado y los ejemplos válidos e inválidos de `contratos/ejemplos/` (los nuevos casos inválidos van en `contratos/ejemplos/invalidos/`);
- las pruebas de `tests/test_contratos.py` en verde;
- una nota en `pipeline/state/decisiones.md`.

Un cambio que hace inválidos los artefactos ya publicados es una versión nueva del contrato, no una edición in situ.

## 10. Qué revisa CI

`.github/workflows/ci.yml` corre en cada `push` y en cada `pull_request`. No usa secrets ni llama a la API de pago: los tests de agentes usan clientes falsos.

| Job | Qué comprueba |
|---|---|
| `secrets-scan` | Busca claves de Anthropic (`sk-ant-…`) y de GitHub (`github_pat_…`, `ghp_…`) en todo el repositorio. Carga todos los JSON de `insumos/` y `contratos/` |
| `contratos-e-invariantes` | Cada `contratos/ejemplos/*_ejemplo.json` contra su esquema. La noticia de prueba `evals/casos/ciclo/noticia_prueba_actions.json`. `python .claude/hooks/otm_hook.py repo`: invariantes 1–3 y 5–8 sobre todo el repositorio, más secretos de Supabase y de bases de datos |
| `pytest` | `python -m pytest -q` |
| `sitio` | `node sitio/db/generar_aplicar_todo.mjs --check` (el SQL de migraciones está al día), `npm ci` y `npm test` en `sitio/web` con `CHROME_PATH=google-chrome` |

Límites que conviene conocer:

- CI no define `OTM_TEXTOS_NOTICIAS`. La comparación literal de la invariante 3 contra el cuerpo de las noticias **no se hace en CI**. CI revisa nombres de archivo y esquemas. El cuerpo se relee en memoria durante el ciclo y la publicación, y el verificador contrasta con la fuente.
- Los tests del simulador se omiten si el repositorio externo del simulador no está.
- `deploy.yml` no es CI. Corre con cada push a `main` y despliega el sitio (`docs/operacion.md`, sección 6).

## 11. Lista para abrir un PR

1. Rama propia. Commits con prefijo y mensaje en español.
2. `python -m pytest -q` en verde. Si tocaste `sitio/`, también `npm test` en `sitio/web`.
3. `python .claude/hooks/otm_hook.py repo` sin violaciones (es lo que corre CI).
4. Ningún secreto, ningún `.env` y ningún cuerpo de noticia en los archivos.
5. Ningún archivo de `insumos/` modificado ni borrado: si algo cambia, es una versión nueva.
6. Si el cambio toma una decisión (de diseño, de costo o de gobernanza), anótala en `pipeline/state/decisiones.md` con fecha, agente y alternativa descartada.
7. Describe en el PR qué cambia, qué revisa CI y si tocas `pipeline/state/`. Un PR que incluye estado del pipeline no debe mergearse por accidente.

Quién aprueba un PR manual sigue **pendiente de confirmar**. `CLAUDE.md` reserva las aprobaciones de contenido a Carlos como revisor humano, y no hay una regla escrita para PR de otras personas.

## 12. Pendientes

- Canal para que docentes o terceros propongan tareas (plantilla de issue, formulario o similar).
- Definir si los PR manuales sobre `tareas/` están permitidos y cómo se revisan (sección 6).
- Regla de aprobación para PR de terceros (sección 11).
