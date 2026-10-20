# Decisiones tomadas sin consultar y decisiones que requieren al humano

Formato: `AAAA-MM-DD · agente · decisión · alternativa descartada · por qué`.

## Decisiones autónomas

- 2026-10-20 · humano (Carlos) · Puntajes provisionales de 5 tareas-oro puestos por Claude para no bloquear el builder · esperar doble codificación humana · prioridad de lanzamiento; recalibrar después.
- 2026-10-20 · humano (Carlos) · Simulador vía API en Actions · `claude -p` local · reproducibilidad y automatización semanal.
- 2026-10-20 · build-lead · `architect` y `rubric-encoder` corren en paralelo con una forma común fijada por build-lead para el bloque `rub01` (derivada de RUB01.instrucciones_evaluador.salida); build-lead valida la salida del evaluador contra `contratos/evaluacion.schema.json` al cierre · correrlos en secuencia · ahorra un ciclo y la forma ya está definida en el insumo.
- 2026-10-20 · build-lead · kappa ponderado cuadrático calculado sin scikit-learn (no instalado) · instalar sklearn · evita dependencia; fórmula estándar, verificable con test.

## Requiere decisión humana

(vacío)
