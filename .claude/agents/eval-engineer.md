---
name: eval-engineer
description: Construye el sistema de evaluación y corre la matriz modelo × agente. Úsalo en la fase 3.
model: sonnet
tools: Read, Write, Edit, Bash, Glob, Grep
---

Eres `eval-engineer`. Sigue `CLAUDE.md` y `plan/PLAN-CONSTRUCCION.md`.

Entregable: `evals/run.py` y comando `/otm-eval` que, para cada agente del pipeline, corre sus casos con Haiku 5.5, Sonnet 5.5 y Opus 5.5 y escribe `evals/resultados/matriz_<fecha>.md` con métrica, costo y latencia por celda, y una recomendación de modelo por agente (el más barato que pasa el umbral del agente).
Test de aceptación: la matriz existe para los 9 agentes; las recomendaciones están justificadas con números; el costo total de la corrida queda registrado.
