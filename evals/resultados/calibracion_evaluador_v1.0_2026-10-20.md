# Calibración del agente evaluador (RUB01 v4.0) — informe v1.0, 2026-10-20

> **ADVERTENCIA.** 5 de los 9 puntajes de referencia (Sugarloaf, Port of Hamburg, Lighthouse, St. Michael's Church, A Clear Day at the Ocean) son **provisionales, puestos por Claude** (2026-10-20), un modelo de la misma familia que el evaluador. El acuerdo medido contra ellos está probablemente inflado. **Este kappa no se reporta como validez** hasta la doble codificación humana (Hugo/Mahsa). Se reporta por separado el kappa contra las 4 tareas codificadas por un humano (Abiam Muñoz).

## Resultado

- Prompt final: `pipeline/agentes/evaluador/prompt_sistema_v1.3.md` (sha256 `d8c55ac66c2b…`).
- Modelo: `claude-opus-5-5`, effort `high`, temperatura: no se envía (el modelo la rechaza: 'deprecated for this model'); salida: output_config.format json_schema.
- Criterio de aceptación: kappa ponderado cuadrático ≥ 0,7 en cada una de 3 corridas independientes (108 pares criterio × tarea por corrida).
- **ACEPTA** con prompt v1.3.
- Costo total de la calibración (todas las versiones): 10,73 USD (precio supuesto 5/25 USD por MTok; con precio pesimista 15/75: 32,20 USD).

## Kappa por corrida (prompt final)

| Corrida | κ global (108) | Acuerdo exacto | κ solo humanas (48) | Acuerdo exacto humanas | κ solo provisionales (60) | Costo USD |
|---|---|---|---|---|---|---|
| 1 | 0,706 | 0,80 | 0,620 | 0,85 | 0,729 | 1,09 |
| 2 | 0,802 | 0,85 | 0,676 | 0,85 | 0,844 | 0,81 |
| 3 | 0,745 | 0,82 | 0,684 | 0,88 | 0,757 | 0,81 |

κ global agrupado (3 corridas, 324 pares): 0,752.

## Kappa por criterio (prompt final, 27 pares = 9 tareas × 3 corridas)

| Criterio | κ agrupado | κ por corrida | Acuerdo exacto | Media evaluador | Media referencia |
|---|---|---|---|---|---|
| genuino | 0,959 | 1,000 / 1,000 / 0,880 | 0,96 | 1,63 | 1,67 |
| abierta | 0,807 | 0,769 / 0,769 / 0,883 | 0,81 | 1,63 | 1,44 |
| decisiones | 0,962 | 1,000 / 0,903 / 1,000 | 0,96 | 1,63 | 1,67 |
| realismo | 0,000 | 0,000 / indef. / 0,000 | 0,93 | 1,93 | 2,00 |
| autenticidad | 0,357 | 0,357 / 0,357 / 0,357 | 0,56 | 1,78 | 1,56 |
| contexto | 0,804 | 0,870 / 0,870 / 0,609 | 0,85 | 1,70 | 1,78 |
| ciclo | 0,959 | 1,000 / 1,000 / 0,880 | 0,96 | 1,63 | 1,67 |
| validacion | 0,462 | 0,308 / 0,308 / 0,769 | 0,74 | 1,67 | 1,56 |
| nivel | indef. | indef. / indef. / indef. | 1,00 | 2,00 | 2,00 |
| autodiferenciacion | 0,633 | 0,455 / 0,870 / 0,557 | 0,70 | 1,52 | 1,22 |
| fecundidad | 0,500 | 0,182 / 0,769 / 0,500 | 0,78 | 1,67 | 1,67 |
| recursos | 0,609 | 0,526 / 0,649 / 0,649 | 0,63 | 1,48 | 1,56 |

κ indefinido = la referencia y el evaluador son constantes en ese criterio (desacuerdo esperado 0). Con 9 tareas, el κ por criterio es muy inestable: un solo desacuerdo en un criterio casi constante lo hunde; léase junto al acuerdo exacto.

## Totales por tarea (prompt final)

| Tarea | Referencia | Codificador | Corrida 1 | Corrida 2 | Corrida 3 |
|---|---|---|---|---|---|
| clear-day-at-the-ocean | 7 | Claude (prov.) | 7 (+0) | 7 (+0) | 9 (+2) |
| giants-shoes | 24 | humano | 24 (+0) | 24 (+0) | 24 (+0) |
| lighthouse | 20 | Claude (prov.) | 23 (+3) | 23 (+3) | 23 (+3) |
| poblacion-belga | 16 | humano | 14 (-2) | 13 (-3) | 14 (-2) |
| port-of-hamburg | 24 | Claude (prov.) | 24 (+0) | 24 (+0) | 24 (+0) |
| residuos-plasticos | 22 | humano | 24 (+2) | 23 (+1) | 23 (+1) |
| st-michaels-church | 21 | Claude (prov.) | 23 (+2) | 21 (+0) | 24 (+3) |
| sugarloaf | 20 | Claude (prov.) | 24 (+4) | 22 (+2) | 17 (-3) |
| vapes-litio | 24 | humano | 23 (-1) | 23 (-1) | 23 (-1) |

### Tareas con |total − referencia| ≥ 3

- Corrida 1: **lighthouse** — evaluador 23, referencia 20 (+3).
- Corrida 1: **sugarloaf** — evaluador 24, referencia 20 (+4).
- Corrida 2: **lighthouse** — evaluador 23, referencia 20 (+3).
- Corrida 2: **poblacion-belga** — evaluador 13, referencia 16 (-3).
- Corrida 3: **lighthouse** — evaluador 23, referencia 20 (+3).
- Corrida 3: **st-michaels-church** — evaluador 24, referencia 21 (+3).
- Corrida 3: **sugarloaf** — evaluador 17, referencia 20 (-3).

### Decisión de publicación (≥ 20 y ningún 0)

- Corrida 1: publica giants-shoes, lighthouse, port-of-hamburg, residuos-plasticos, st-michaels-church, sugarloaf, vapes-litio.
- Corrida 2: publica giants-shoes, lighthouse, port-of-hamburg, residuos-plasticos, st-michaels-church, sugarloaf, vapes-litio.
- Corrida 3: publica giants-shoes, lighthouse, port-of-hamburg, residuos-plasticos, st-michaels-church, vapes-litio.
- Referencia: publican las 8 positivas; quedan fuera poblacion-belga y clear-day-at-the-ocean.

## Consistencia entre corridas (evaluador vs. evaluador, 108 pares)

- Corridas 1–2: κ 0,892, acuerdo exacto 0,93.
- Corridas 1–3: κ 0,837, acuerdo exacto 0,90.
- Corridas 2–3: κ 0,851, acuerdo exacto 0,90.

Avisos de post-proceso (citas no literales, mejoras sobrantes descartadas, total del modelo distinto): 2 — sugarloaf:cita_no_literal:abierta, sugarloaf:cita_no_literal:nivel

## Limitaciones (leer antes de usar el resultado)

- **El umbral se cumple por poco** (mínimo por corrida 0,706). Contra las 4 tareas humanas solamente, κ por corrida = 0,620 / 0,676 / 0,684 (bajo 0,7): el cumplimiento global descansa en parte sobre los puntajes provisionales de Claude.
- **Riesgo de sobreajuste:** los tres ajustes del prompt se decidieron mirando los desacuerdos en estas mismas 9 tareas (no hay conjunto de prueba separado). El prompt no contiene las tareas-oro ni sus puntajes, y cada ajuste es una lectura general de un descriptor de RUB01, pero el κ de la versión final es optimista. Recalibrar con tareas nuevas y con la doble codificación humana.
- **Variabilidad entre corridas:** el modelo no acepta temperatura 0; con el mismo prompt los totales de una tarea varían hasta en varios puntos (ver Sugarloaf: 24 / 22 / 17), y eso puede cambiar la decisión de publicar.
- **κ por criterio** con 9 tareas es inestable e indefinido donde la referencia es constante (nivel; realismo casi constante): no sirve para juzgar criterios individuales.
- **Costo:** el precio de Opus 5.5 no está documentado en el repo; se supuso 5/25 USD por MTok. Verificar en la Console. No incluye ~0,17 USD de sondeos de API y una prueba de humo previas a las corridas.

## Historial de versiones del prompt

| Versión | Cambio | κ por corrida | Acepta | Costo USD |
|---|---|---|---|---|
| 1.0 | Versión inicial: RUB01 v4.0 completa (JSON literal, incluidas instrucciones_evaluador) y MAR03 §1 literales; procedimiento por criterio; cita literal ≤ 25 palabras antes de justificación y puntaje; regla de independencia entre criterios. | 0,584 / 0,614 / 0,595 | no | 2,55 |
| 1.1 | Ajuste 1 (κ v1.0 = 0,58–0,61; evaluador sistemáticamente más severo, sobre todo en ciclo, nivel, validación y autenticidad). Se reemplaza la frase «el 2 exige cumplimiento pleno con evidencia» por una lectura de descriptores que no exige más de lo que dicen; se acota «ante duda, el menor» a dudas genuinas entre descriptores adyacentes; se agregan lecturas fijas de los criterios 5 (procedencia declarada se toma como cierta), 7 («exige» = la resolución obliga a recorrer las fases), 8 («posible» = evidencia accesible, no necesariamente entregada) y 9 (no descontar de nuevo apertura/supuestos/validación), y una regla para textos que relatan una tarea implementada. RUB01 y MAR03 sin cambios. | 0,719 / 0,688 / 0,725 | no | 2,75 |
| 1.2 | Ajuste 2 (κ v1.1 = 0,72/0,69/0,73: corrida 2 bajo el umbral; v1.1 corrigió la severidad pero pasó a sobrepuntuar autodiferenciación y recursos, y a poner 0 donde hay presencia parcial). Se agrega una frontera 0/1 simétrica a la del 2 (el 0 describe ausencia total) y lecturas fijas de los criterios 10 (piso = entrada sin una única idea clave; techo = la tarea misma admite soluciones más sofisticadas) y 12 (obtenibilidad real de la información para el nivel declarado). RUB01 y MAR03 sin cambios. | 0,711 / 0,680 / 0,738 | no | 2,73 |
| 1.3 | Ajuste 3, último permitido (κ v1.2 = 0,71/0,68/0,74: corrida 2 bajo el umbral). Se agrega la lectura del criterio 4 (realismo = la situación existe o es plausible; una pregunta de curiosidad o desafío sobre hechos reales no es un encuadre forzado; la necesidad se juzga en el criterio 1) y se precisa la regla para relatos de tareas implementadas: las fases que el relato recorre sin decir quién decidió se leen como proceso de los estudiantes; solo cuenta como entregado lo que el texto dice que se les dio. RUB01 y MAR03 sin cambios. | 0,706 / 0,802 / 0,745 | sí | 2,70 |

## Reproducibilidad

- `modelo`: claude-opus-5-5
- `effort`: high
- `max_tokens`: 16000
- `temperature`: no se envía (el modelo la rechaza: 'deprecated for this model')
- `salida_estructurada`: output_config.format json_schema
- `cache`: system prompt con cache_control ephemeral
- `prompt_archivo`: pipeline/agentes/evaluador/prompt_sistema_v1.3.md
- `prompt_sha256`: d8c55ac66c2b282127aad47b7e2919e9a21e623cd3aeedcfe41149535ca72751
- `version_rubrica`: 4.0
- `rubrica_sha256`: de11b63d71e4107e0622cc9f1cf5496ca1e939b096d16f574b2ca1a206ebc2d4
- `version_mar03`: 1.0
- `referencia`: evals/oro/puntajes_v0.4_2026-10-20.csv
- `referencia_sha256`: 2106220748164ae1af6eb41b5a777c82963d144aa0159bf56c5710f64a7722b5
- `sdk_anthropic`: 0.116.0
- `python`: 3.12.10
- `git_commit`: fb67480
- `precios_usd_mtok`: {'input': 5.0, 'output': 25.0, 'cache_write': 6.25, 'cache_read': 0.5}
- `precios_pesimistas_usd_mtok`: {'input': 15.0, 'output': 75.0, 'cache_write': 18.75, 'cache_read': 1.5}

## Notas de método

- Kappa ponderado cuadrático implementado a mano (`evals/kappa.py`, test en `tests/test_kappa.py`).
- Entrada al evaluador: nivel declarado, título, texto de la tarea (extraído de `insumos/tareas-oro/` con verificación sha256; Sugarloaf: traducción de trabajo de INS02 v0.2 §1.2 y descripción de foto §6.3) y recursos declarados. No recibe puntajes, rol de calibración ni las notas evaluativas de las autoras.
- Las tareas de Abiam (residuos-plasticos, vapes-litio, poblacion-belga) son descripciones o extractos de la fuente, no enunciados para estudiantes; el evaluador lo sabe por el campo «Tipo de texto».
- El total se recalcula en código; las mejoras se filtran a criterios en 0 o 1.
