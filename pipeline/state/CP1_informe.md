# CP1 – Informe de cierre de la fase 1 (Contratos y calibración)

Fecha: 2026-10-20 · Preparado por `build-lead`.

## 1. Entregables y commits

| Tarea | Entregable | Commit |
|---|---|---|
| `architect` | `contratos/` (7 esquemas: noticia, tarea, evaluacion, evaluacion_rub01, trazas_resumen, guia, catalogo; 7 ejemplos válidos y 17 inválidos), `pipeline/orquestador.py` (máquina de estados), `pipeline/invariantes.py` (invariantes 1, 2, 3, 5 y 6 como funciones puras + CLI para hooks) | a8803a1 |
| `rubric-encoder` | `pipeline/agentes/evaluador/` (prompt v1.0–v1.3, vigente v1.3; `evaluador.py`), `evals/casos/evaluador/` (9 casos), `evals/kappa.py`, `evals/calibrar_evaluador.py`, `evals/resultados/calibracion_evaluador_v1.0_2026-10-20.{md,json}` | 3ef26fe |

`insumos/` sin cambios (verificado con `git diff`). Búsqueda de secretos en el árbol: sin hallazgos.

## 2. Tests (corridos por build-lead)

- `python -m pytest tests -q` → **139 passed**.
- Transición ilegal `borrador → publicada` lanza `TransicionIlegal`; `revisada` con 19/24 o con un criterio en 0 falla; con 20/24 pasa.
- CLI de hook: `python -m pipeline.invariantes esquema evaluacion contratos/ejemplos/evaluacion_ejemplo.json` → exit 0.
- Las 27 salidas del evaluador (v1.3, 3 corridas × 9 tareas) validan contra `contratos/evaluacion_rub01.schema.json`; 0 errores de API.

## 3. Calibración del evaluador

> **Advertencia:** 5 de los 9 puntajes de referencia (Sugarloaf, Port of Hamburg, Lighthouse, St. Michael's Church, Clear Day) son provisionales y los puso Claude. El kappa **no se reporta como validez** hasta la doble codificación humana.

Kappa ponderado cuadrático, prompt v1.3 (recalculado de forma independiente por build-lead a partir de las salidas guardadas; coincide):

| Corrida | Global (108 pares) | Solo humanas, Abiam (48) | Solo provisionales (60) |
|---|---|---|---|
| 1 | 0,706 | 0,620 | 0,729 |
| 2 | 0,802 | 0,676 | 0,844 |
| 3 | 0,745 | 0,684 | 0,757 |

- Umbral 0,7 alcanzado en las 3 corridas, **por poco** en la corrida 1. Contra las 4 tareas humanas queda **bajo 0,7** en las tres.
- Consistencia del evaluador consigo mismo entre corridas: kappa 0,84–0,89.
- Criterios débiles: autenticidad (0,36), validación (0,46), fecundidad (0,50). Realismo y nivel tienen referencia casi constante, así que su kappa no es informativo.
- Tareas con |total − referencia| ≥ 3: lighthouse (23 vs 20, las 3 corridas), sugarloaf (24 y 17 vs 20), poblacion-belga (13 vs 16, corrida 2), st-michaels-church (24 vs 21, corrida 3). En la corrida 3 Sugarloaf quedaría bajo el umbral de publicación.
- Los ajustes v1.0 → v1.3 se decidieron mirando estas mismas 9 tareas (sin conjunto de prueba aparte): el kappa final es optimista.

## 4. Decisiones tomadas (detalle en `decisiones.md`)

- `architect` y `rubric-encoder` en paralelo, con forma fija del bloque `rub01` dada por build-lead.
- Retroceso permitido `evaluada → borrador` (máx. 3 evaluaciones), `con_guia/verificada → simulada`; estado terminal `archivada` con motivo.
- `revisada` y `publicada` exigen `revisor`; invariante 2 se re-verifica en todo estado desde `revisada`.
- Áreas temáticas con los ids de MED01, no la lista de PLT01 (PLT01 debería pasar a v0.2).
- Recursos de entrada no llegan al simulador (invariante 6 lista solo 3 campos): lo que el estudiante tenga desde el inicio va en `enunciado_es`.
- `claude-opus-5-5` rechaza `temperature`, `tool_choice` forzado y `thinking.disabled`: el evaluador usa temperatura por defecto, pensamiento adaptativo `effort=high` y salida con `output_config.format` (json_schema). La regla de "temperatura 0" del plan no se puede cumplir con este modelo.
- Una mejora faltante para un criterio en 0/1 es error (reintento y luego falla), no advertencia.
- Kappa calculado sin scikit-learn, con test de valor conocido.

## 5. Costo

- Calibración: **10,73 USD** + ~0,17 USD de sondeos, con precio supuesto de 5/25 USD por millón de tokens (el repo no documenta el precio de Opus 5.5). Cota pesimista (15/75): 32,2 USD.
- Construcción: con el plan de Claude Code (sin costo de API).
- **Acumulado registrado: 10,90 USD (verificar en la Console).**

## 6. Qué debe aprobar Carlos

1. **Contratos congelados**: los 7 esquemas en `contratos/` y la máquina de estados (incluidos retrocesos, `archivada` y `revisor` obligatorio).
2. **Evaluador calibrado con reservas**: aceptar kappa 0,706–0,802 (provisional) sabiendo que contra las 4 tareas humanas queda en 0,62–0,68, o pedir otra ronda de prompt / un conjunto de prueba aparte antes de la fase 2.
3. **Falta de temperatura 0** en Opus 5.5: aceptar la variabilidad medida (kappa entre corridas 0,84–0,89, Sugarloaf 17–24) o pedir que el evaluador agregue varias corridas (p. ej. mediana de 3) en producción.
4. **PLT01 v0.2**: alinear áreas temáticas con MED01 y la lista de estados de la tarea.
5. **Costo real**: confirmar el gasto en la Console y el precio de Opus 5.5 para `pipeline/config.yaml`.
6. Pendiente de siempre: doble codificación humana de las 5 tareas-oro provisionales.
