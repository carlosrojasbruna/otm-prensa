# Plan de construcción con agentes en Claude Code

Versión 1.0 · 2026-10-20. Resume el plan acordado con Carlos; los detalles de insumos están en `insumos/INV00`.

## Fases y checkpoints

| Semana | Trabajo | Checkpoint |
|---|---|---|
| 1 | `architect` (contratos, máquina de estados), `rubric-encoder` (evaluador calibrado contra tareas-oro) | **CP1** |
| 2 | `agent-smith` ×7 en paralelo; `sim-integrator` | — |
| 3 | `eval-engineer` corre la matriz modelo × agente; orquestador completo; 3 tareas de prueba | **CP2** |
| 4 | `site-builder` (home, explorar, página de tarea, cuentas, DB) | — |
| 5 | `devops` (Actions, cron, staging), `docs-writer`; primer lote de 6 | **CP3** |
| 6+ | Operación semanal autónoma; recalibración mensual del evaluador | PR semanal |

## Agentes de construcción

| Agente | Entregable | Test de aceptación |
|---|---|---|
| `build-lead` | Orquesta; mantiene `pipeline/state/build.json` y `decisiones.md` | Cada fase cierra con sus tests en verde |
| `architect` | `contratos/*.schema.json`, `pipeline/orquestador.py` (máquina de estados) | Artefactos de ejemplo validan; transiciones ilegales fallan |
| `rubric-encoder` | `pipeline/agentes/evaluador/` (prompt + salida estructurada) | kappa ≥ 0,7 contra `evals/oro/puntajes_v0.4` en 3 corridas; reporta kappa por criterio |
| `agent-smith` | Un agente del pipeline por invocación (explorador, filtro, diseñador, simulador-adapter, redactor, ilustrador, verificador, bibliotecario), con 5 casos de prueba cada uno | Casos pasan; salida valida contra contrato |
| `sim-integrator` | `simulador/adapter/` según `insumos/simulador/SIM01`; port de `llamar()` a API | Reproduce una corrida del piloto; Sugarloaf en S1 produce `trazas_resumen` válido; hook de aislamiento rechaza `task_space` |
| `eval-engineer` | `evals/` y comando `/otm:eval` | Matriz modelo × agente × métrica en `evals/resultados/` |
| `site-builder` | `sitio/` fiel a los snapshots en `insumos/diseno/` | Lighthouse ≥ 90; flujo cuenta → valorar → comentar en staging |
| `devops` | Workflows, hooks pre-commit, README de secrets | Pipeline completo corre en Actions con 1 noticia de prueba |
| `docs-writer` | README, guía de operación, guía de contribución | Una persona ajena reproduce la instalación |

## Agentes del pipeline y modelos de partida

| Agente | Modelo | Técnicas |
|---|---|---|
| Explorador de prensa | Haiku 5.5 | Batch, salida estructurada, resumen ≤ 80 palabras |
| Filtro de modelabilidad | Haiku 5.5 (→ Sonnet si kappa < 0,6) | RUB01 corta en caché; temperatura 0 |
| Diseñador de tarea | Sonnet 5.5 | Marcos y PLT01 en caché; 2 candidatos por noticia |
| Evaluador | Opus 5.5 | Temperatura 0; puntaje por criterio con justificación citando el enunciado |
| Simulador | Sonnet 5.5 por agente-estudiante | Perfiles por nivel en caché; 6 corridas; límite de turnos |
| Redactor de guía | Sonnet 5.5 (Opus para escenarios) | Por secciones; escenarios solo desde trazas |
| Ilustrador | Sonnet 5.5 (SVG plano) | Paleta e íconos de referencia en caché |
| Verificador | Opus 5.5 | Ejecuta el notebook; contrasta cifras con la fuente |
| Bibliotecario | Haiku 5.5 / script | Commit, PR, catálogo |

Regla: cada agente parte con el modelo más barato que pase su eval; sube de nivel solo con evidencia en `evals/resultados/`.

## Estructura del repositorio

```
CLAUDE.md · plan/ · insumos/ (solo lectura) · contratos/ · pipeline/{orquestador.py, agentes/, state/}
simulador/adapter/ · evals/{oro, casos, resultados} · tareas/AAAA-MM/slug/ · sitio/{web, api, db}
.claude/{agents, hooks, commands} · .github/workflows/{semanal, ci, deploy}.yml
```
