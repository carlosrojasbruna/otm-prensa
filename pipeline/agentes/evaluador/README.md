# Agente evaluador (RUB01 v4.0)

Puntúa una tarea con los 12 criterios de RUB01 (0/1/2, máx. 24) y devuelve el bloque `rub01` de `evaluacion.json` (`contratos/evaluacion_rub01.schema.json`), más `meta` (modelo, versión de prompt, uso de tokens, costo, avisos) para que el orquestador lo mapee a `reproducibilidad`.

## Archivos

| Archivo | Qué es |
|---|---|
| `prompt_sistema_v1.3.md` | Prompt vigente. Incluye RUB01 v4.0 completa (JSON literal, con `instrucciones_evaluador`) y MAR03 §1. Se envía como system con `cache_control: ephemeral` |
| `prompt_sistema_v1.0.md` … `v1.2.md` | Versiones anteriores (no se editan; historial en `evals/resultados/calibracion_evaluador_v1.0_2026-10-20.md`) |
| `evaluador.py` | `evaluar(tarea, version_prompt="1.3")` → `{"rub01", "meta"}` |

## Uso

```python
from pipeline.agentes.evaluador.evaluador import evaluar
res = evaluar({"titulo": "...", "nivel_declarado": {"nivel": "S", "sub_tramo": "S1"},
               "forma_texto": "enunciado para estudiantes", "texto": "...",
               "recursos": ["..."], "mapa_ciclo": None})
```

CLI: `python -m pipeline.agentes.evaluador.evaluador evals/casos/evaluador/giants-shoes.json`.
Calibración: `python evals/calibrar_evaluador.py --prompt 1.3` (3 corridas × 9 tareas-oro; tope `--presupuesto 15`).

## Decisiones

- Modelo `claude-opus-5-5`. No acepta `temperature`, `tool_choice` forzado ni `thinking.disabled`: se usa el default, pensamiento adaptativo con `effort="high"` y salida forzada con `output_config.format` (json_schema).
- El total se recalcula en código. Una mejora faltante para un criterio en 0/1 es un error (reintento); la salida se valida contra el contrato y `pipeline.invariantes.consistencia_rub01` antes de devolverse. Citas de más de 25 palabras se recortan (invariante 3).
- La clave se obtiene solo con `pipeline.apikey.api_key` (`OTM_API_KEY` local, `ANTHROPIC_API_KEY` en Actions).
- Calibración v1.3: κ ponderado = 0,71 / 0,80 / 0,75 (acepta), pero contra las 4 tareas humanas κ = 0,62 / 0,68 / 0,68. **5 de los 9 puntajes de referencia son provisionales (Claude); no reportar el κ como validez hasta la doble codificación humana.**
