# OTM-Prensa — reglas del repositorio

Observatorio de Tareas de Modelamiento desde la Prensa. Pipeline de agentes que convierte noticias en tareas de modelamiento matemático con guía docente, publicadas en un repositorio y un sitio para docentes. Responsable: Carlos Rojas Bruna (PUC Chile).

## Lee primero

1. `insumos/INV00_inventario-de-insumos_v0.4_2026-10-20.md` — qué existe y en qué estado.
2. `insumos/GOB01_gobernanza_v1.0_2026-10-20.md` — umbrales, aprobaciones, secrets, licencias.
3. `plan/PLAN-CONSTRUCCION.md` — fases, agentes de construcción, checkpoints.
4. `pipeline/state/build.json` — dónde va la construcción (lo mantiene `build-lead`).

## Fuente única de verdad

- **Rúbricas:** `insumos/rubricas/RUB01_*.json` (calidad de tarea, 12 criterios, máx. 24), `RUB02-RUB03_*.json` (adecuación P1–P5; diseño de clase C1–C9). No se reescriben: se versionan.
- **Niveles:** `insumos/marcos/MAR03_*` — P (10–12), S (13–18; S1/S2 opcional), U (18–20).
- **Plantillas:** `insumos/plantillas/PLT01_*` (tarea), `PLT02_*` (guía docente).
- **Simulador:** repo externo del equipo (`IDEA MODELAMIENTO/simulacion/sim.py`); contrato en `insumos/simulador/SIM01_*`. No se modifica salvo `llamar()` (ver GOB01 §3).
- **Tareas-oro:** `insumos/tareas-oro/` + `evals/oro/puntajes_v0.4_2026-10-20.csv`. Cinco puntajes son provisionales (Claude); no reportar el kappa contra ellos como validez.
- **Medios:** `insumos/medios/MED01_*.yaml`.

Los archivos de `insumos/` son de solo lectura para los agentes de construcción y del pipeline. Un cambio a un insumo es una nueva versión (`nombre_vX.Y_AAAA-MM-DD`), nunca una edición in situ.

## Invariantes (se aplican como hooks; ningún agente puede saltarlas)

1. Ningún artefacto cambia de estado sin validar contra su esquema en `contratos/`.
2. Ninguna tarea llega a `revisada` con RUB01 < 20/24 o con algún criterio en 0.
3. Ningún archivo del repo contiene más de 25 palabras consecutivas del **cuerpo** de una noticia. Las noticias se citan (medio, título, fecha, URL) y se resumen en ≤ 80 palabras propias. El **titular se cita completo**: es parte de la cita y queda fuera del conteo (decisión humana 2026-10-20); el límite rige para `resumen_propio`, enunciado, recursos y guía.
4. Ninguna cifra en una tarea sin localizador en la noticia o en el notebook de escenarios.
5. Ningún escenario de guía docente sin `id` de corrida del simulador que lo respalde.
6. Los agentes-estudiante del simulador reciben solo `enunciado_es`, `foto_descripcion` y recursos "a solicitud"; nunca `task_space`.
7. Ningún commit con secretos (`ANTHROPIC_API_KEY`, `GH_TOKEN`, claves de medios o de Supabase). Se leen de variables de entorno.
   - **Clave de API en scripts:** todo script del pipeline obtiene la clave con `OTM_API_KEY` y, si no existe, con `ANTHROPIC_API_KEY` (helper: `pipeline/apikey.py`). En la máquina local se usa `OTM_API_KEY` para que Claude Code siga autenticado con el plan de Carlos (claude.ai); en GitHub Actions el secret se llama `ANTHROPIC_API_KEY`.
8. Cada ejecución del pipeline registra en `evaluacion.json`: modelo y versión de cada agente, versión de prompt, versión de rúbrica, de MAR03 y de MED01, diseño del simulador, fecha, costo.

## Convenciones

- Idioma de código, prompts y documentos: español; identificadores en inglés cuando son estándar (`task_space`, `coder_schema`).
- Nombres de archivos de insumos y entregables: `nombre_vX.Y_AAAA-MM-DD.ext`. Las tareas publicadas no se editan: se crea v2 en la misma carpeta y se conserva v1.
- Commits: mensaje en español, prefijo por área (`insumos:`, `contratos:`, `agente/<nombre>:`, `pipeline:`, `sitio:`, `devops:`, `docs:`).
- Modelos de partida por agente (GOB01 §3); `eval-engineer` puede cambiarlos solo con evidencia en `evals/resultados/`.
- Los agentes no preguntan entre checkpoints: toman la lectura más conservadora, la anotan en `pipeline/state/decisiones.md` y siguen. El humano lee ese archivo en cada checkpoint.

## Checkpoints humanos (solo tres)

| CP | Cuándo | Qué aprueba Carlos |
|---|---|---|
| CP1 | Fin de semana 1 | Contratos congelados; evaluador calibrado (kappa contra tareas-oro reportado) |
| CP2 | Fin de semana 3 | 3 tareas completas de punta a punta; matriz modelo × agente; elección de modelos |
| CP3 | Fin de semana 5 | Sitio en staging; primer lote de 6 tareas; cron semanal; costo por ciclo |

Entre checkpoints `build-lead` corre de manera autónoma. Si una decisión no se puede deshacer y podría ir en cualquier sentido, se detiene y la deja escrita en `decisiones.md`.
