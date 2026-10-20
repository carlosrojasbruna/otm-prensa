---
description: Corre la matriz modelo x agente (Haiku/Sonnet/Opus 5.5 por cada agente del pipeline) y escribe evals/resultados/matriz_<fecha>.md
argument-hint: "[--agentes a,b] [--modelos haiku,sonnet,opus] [--sin-red] [--tope USD] [--reanudar]"
---
Corre `python evals/run.py $ARGUMENTS` desde la raíz del repo y resume el resultado. Antes de lanzar una corrida real, lee `evals/DECISIONES.md` y `pipeline/state/decisiones.md` ("Fase 3").

Reglas:

1. **Sin argumentos = corrida real completa** (9 agentes x 3 modelos, tope de 12 USD, precios de `pipeline/config.yaml`). Gasta dinero: si el usuario no pidió explícitamente una corrida real, usa `--sin-red`.
2. **`--sin-red`** usa `ClienteFalso` con las respuestas scripteadas de los casos. Prueba la tubería (forma de la matriz, regla de recomendación, registro de costo) sin gastar ni medir modelos; escribe `matriz_<fecha>_sinred.{md,json}` y no pisa la matriz real.
3. **Opciones:** `--agentes explorador,filtro,disenador,evaluador,simulador,redactor,ilustrador,verificador,bibliotecario`; `--modelos haiku,sonnet,opus` (o ids completos); `--tope 12`; `--reanudar` (omite los agentes ya guardados en `evals/resultados/matriz_<fecha>_datos/`); `--corridas-filtro 3`; `--lanzadas-simulador 2`; `--dir` y `--sufijo` para escribir en otro lugar (una corrida parcial debería usar `--sufijo _parcial` para no pisar la matriz completa).
4. **Clave de API:** la lee `pipeline/apikey.py` (`OTM_API_KEY`, luego `ANTHROPIC_API_KEY`). Nunca exportes `ANTHROPIC_API_KEY` en la máquina local.
5. **Tope de gasto:** `run.py` reserva el peor caso de cada llamada y se detiene antes de superar el tope; las celdas que no alcanzan a correr quedan en la sección "Celdas no corridas". No lo evadas subiendo `--tope` sin que Carlos lo apruebe (el tope de la matriz en la fase 3 es 12 USD, `pipeline/state/decisiones.md`).
6. El evaluador con Opus **no se vuelve a correr**: reutiliza `evals/resultados/evaluador_corridas/prompt_v1.3_2026-10-20.json`.
7. No modifiques `pipeline/config.yaml` con el resultado: la matriz es evidencia para CP2; cambiar un modelo de partida lo decide `build-lead` citando `evals/resultados/matriz_<fecha>.md`.

Al terminar, informa: ruta de la matriz, tabla agente -> modelo recomendado (métrica, costo/unidad), costo total registrado frente al tope, celdas no corridas y cualquier celda que falló por error del agente (no por presupuesto).
