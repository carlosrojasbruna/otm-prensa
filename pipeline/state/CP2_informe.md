# CP2 – Informe de cierre de la fase 3 (Evaluación y prototipo)

Fecha: 2026-10-20 · Preparado por `build-lead`. Detalle de cada decisión en `pipeline/state/decisiones.md` (secciones "Fase 3" y "Decisiones del humano en la fase 3").

## 1. Entregables y commits

| Tarea | Entregable | Commits principales |
|---|---|---|
| `eval-engineer` | `evals/run.py`, comando `/otm-eval`, matriz `evals/resultados/matriz_2026-10-20.{md,json}`, `forzar_modelo` en `pipeline/llm.py` | 40fa237 |
| `orquestador` (architect) | `pipeline/ciclo.py`: tramo A (explorador → filtro → diseñador → evaluador ×3 con mediana) y tramo B (simulador → redactor → ilustrador → verificador → bibliotecario en dry-run) sobre la máquina de estados; tope de gasto; `requirements.txt` | 84e88ca |
| `explorador-med01-v1.1` | Explorador con las reglas de MED01 v1.1 (robots.txt, XML tolerante, gnews, filtro DOI) | 5a16708, 3593880 |
| `prototipo` | 4 tareas en `verificada` (sección 4) | 122ad41, 04b662f y anteriores |
| Ciclo, extensiones surgidas del prototipo | Relectura de la noticia en memoria para la invariante 3; `--rehacer-guia` (revisión humana 2); `--nueva-version` (v+1 con simulación reutilizable y guía base) | e978ee7, 3af930d, c37a070, 67a2be9 |
| Diseñador v1.1 (decisión de Carlos) | Coma decimal es-CL; afirmaciones de recursos con localizador, fuente concreta o supuesto marcado; chequeos en código alineados con el verificador | cdb3d52, 41fb271 |
| Verificador v1.1 (decisión de Carlos) | Clasifica la fuente de cada recurso y contrasta con los párrafos citados (enviados solo en memoria); recibe título, medio y fecha | 8518ade, e75e464 |
| Redactor | Normaliza el código de bloqueo; recibe observaciones de la revisión humana 2 y la guía base de la versión anterior | 01b26a6, 2980e5b |

`insumos/` y `contratos/` sin cambios en toda la fase (`git diff 3582ad4 HEAD`). Búsqueda de secretos: solo el token falso de un test que ya existía (`ghp_SECRETO_DE_PRUEBA_123`). `main` va **30 commits por delante de `origin`**; no se hizo push.

## 2. Tests

- `python -m pytest -q` → **378 passed** (267 al empezar la fase).
- Tests de aceptación por tarea:
  - matriz para los 9 agentes, con recomendación justificada y costo registrado;
  - ciclo de punta a punta sin red (feliz, iteración, mediana e inestabilidad, rechazo del verificador, tope, aislamiento, invariante 3 con texto releído, revisión 2, nueva versión);
  - 4 tareas reales en `verificada`.

## 3. Matriz modelo × agente (`evals/resultados/matriz_2026-10-20.md`, 9,68 USD)

| Agente | Partida | Recomendado | Métrica | Reserva |
|---|---|---|---|---|
| explorador | Haiku | Haiku | 5/5 casos | solo contrato, no calidad |
| filtro | Haiku | Haiku | κ 1,00 | Sonnet y Opus menos estables |
| diseñador | Sonnet | **Opus** | 5/5 ≥ 20/24 | Sonnet cortó por `max_tokens` en 2 casos; en el prototipo perdió 3 noticias por eso |
| evaluador | Opus | Sonnet (provisional) | κ 0,78 en 1 corrida | dentro del ruido de Opus (0,71–0,80); ver hallazgo 5.4 |
| simulador | Sonnet | Sonnet | — | sobre-competencia (hallazgo 5.3) |
| redactor | Sonnet | Haiku | 3/3 casos | solo contrato; en el prototipo las guías de Sonnet aún sobreinterpretan las trazas |
| ilustrador | Sonnet | Haiku | 5/5 | solo validez del SVG |
| verificador | Opus | Opus | 4/5 | el caso 1 está mal planteado |
| bibliotecario | script | — | 10 tests | — |

`pipeline/config.yaml: modelos` **no se cambió**: elegir los modelos es una aprobación de CP2.

## 4. Prototipo: 4 tareas en `verificada`

| Tarea final | Nivel | RUB01 (3 corridas) | Simulación | Verificador | Revisión humana 2 |
|---|---|---|---|---|---|
| `adelantar-compras-queso-v3` | U | 24, 24, 24 | 6/6 validan; **0 bloqueos** (reutilizada de v2) | aprobada, 3 advertencias | **aprobada** (Carlos) |
| `viaje-barco-ida-vuelta-v2` | P | 24, 24, 24 | 5/6 validan; **0 bloqueos** (re-simulada) | aprobada, 1 advertencia | **aprobada** (Carlos) |
| `pagar-trasladar-o-esperar-v4` | U | 24, 24, 24 | 4/6 validan; **0 bloqueos** (reutilizada de v2) | aprobada, 1 advertencia | **pendiente** (la guía v3 se aprobó; la v4 corrige la elasticidad en la tarea) |
| `anticipo-renta-vitalicia-v6` | U | 24, 24, 24 | 6/6 validan; B23 33 %, B34 17 %, B45 17 % (re-simulada) | aprobada, 4 advertencias | **pendiente** (enunciado reescrito: el oficio fue anulado) |

Fuentes: CIPER (anticipo), BBC (aranceles, barco, queso). La noticia de queso es la misma que la de aranceles. No hay tarea S: las 3 noticias que iban a nivel S se perdieron por `max_tokens` del diseñador.

**Versiones y archivos.** Cada versión de una tarea tiene su expediente; las anteriores se conservan.

- Archivadas por el verificador: `anticipo-renta-vitalicia` v1 (falso positivo, el verificador solo veía el resumen) y `pagar-trasladar-o-esperar-v2` (R3 sin localizador; error de la revisión técnica de build-lead).
- Archivados como candidatos no elegidos: 3, dos de ellos por empate 24–24 decidido por orden de llegada.
- Las v1 de aranceles y barco siguen en `verificada` como respaldo.

## 5. Hallazgos principales

1. **La invariante 3 no se comprobaba.** El ciclo no tenía el texto de la noticia en las transiciones. Se corrigió: el texto se relee en memoria; los títulos de más de 25 palabras se citan abreviados (decisión de Carlos); hay un evento cuando no se puede leer. El titular completo de CIPER (34 palabras) **sigue en el historial local** (a3920d7). Ver punto 7.9.
2. **Errores de contenido detectados tarde.** El evaluador y el diseñador no ven el texto de la noticia, y el verificador sí, pero recién después de simular. Así pasaron hasta la guía:
   - un error de hecho en el enunciado (anticipo v1–v5: el oficio estaba anulado);
   - un error matemático en la solución (aranceles v1–v3: traslado con elasticidad constante);
   - una ruta incoherente (anticipo v1, R1);
   - recursos con afirmaciones sin fuente.

   Las propuestas de Carlos (7.4) atacan exactamente esto.
3. **Los estudiantes simulados casi no se traban.** En 3 de las 4 tareas finales hubo 0 bloqueos en 6 corridas, y en Sugarloaf (matriz) aparece Pitágoras en N1. Las intervenciones de esas guías salen del mapa a priori y no de lo observado.
4. **El evaluador no discrimina.** Todas las versiones de todas las tareas sacaron 23–24/24, con las 3 corridas idénticas, también las que tenían errores de hecho o de matemática. Es un techo, no una medida: hoy el control de calidad lo hacen el verificador y las revisiones humanas.
5. **El redactor sobreinterpreta las trazas.** En casi todas las guías el verificador marcó `que_aprende` que afirma más de lo que registra la corrida: correcciones que no ocurrieron, "ningún otro grupo", fin "por límite de turnos". Son advertencias, pero sistemáticas.
6. **Un rechazo por defecto de la tarea no tiene salida útil.** El verificador manda la tarea a `simulada`, se rehace la guía (≈ 0,5 USD) y se archiva. Hoy se rodea con `--nueva-version`.
7. **Falta el notebook de escenarios.** El ciclo no genera `escenarios.ipynb`, que la invariante 4 y el verificador esperan; las cifras se respaldan con las transcripciones.

## 6. Costo

| Concepto | USD |
|---|---|
| Matriz modelo × agente | 9,68 |
| Pipeline del prototipo (todos los ciclos, `gasto_semanal.json`, semana 2026-W43) | 25,05 |
| Pruebas vivas de agentes (explorador v1.1, diseñador v1.1) | 0,18 |
| **Fase 3** | **≈ 34,9** |
| Fases 1–2 | 13,06 |
| **Acumulado** | **≈ 48,0** (precios de `pipeline/config.yaml`; verificar en la Console) |

Del pipeline, ≈ 7 USD fueron retrabajo: versiones v2–v6, dos tareas archivadas en el tramo B, guías rehechas y re-simulaciones.

**Costo por tipo de versión** (tabla completa en `decisiones.md`):

| Tipo | USD por tarea |
|---|---|
| Tramo A, por noticia | 0,6 – 0,9 |
| Nueva versión de tarea | 0,29 – 0,50 |
| Tramo B con simulación | 1,7 – 2,5 |
| Tramo B reutilizando simulación | 0,55 – 1,0 |
| Guía v2 por revisión humana 2 | ≈ 0,50 |
| Tarea completa nueva | ≈ 2,5 – 3,5 |

**Topes.** Carlos fijó el tope semanal provisional en 35 USD; el gasto de la semana va en 25,05. El tope de construcción de la fase 3 que fijó build-lead (25 USD) se superó con aprobación expresa de Carlos (re-simulaciones y versiones v2–v6).

## 7. Qué debe aprobar Carlos

1. **Modelos por agente** (sección 3). Mi lectura: subir el diseñador a Opus (o mantener Sonnet con más `max_tokens` y 1 candidato por llamada); mantener Opus en el evaluador hasta medir Sonnet con 3 corridas; no bajar el redactor a Haiku sin una medida de calidad.
2. **Revisión humana 2** de `pagar-trasladar-o-esperar-v4` y `anticipo-renta-vitalicia-v6`.
3. **Publicación** de las tareas aprobadas (`adelantar-compras-queso-v3`, `viaje-barco-ida-vuelta-v2`) y de las que se aprueben en 7.2. Publicar abre el PR y no se hace sin orden explícita. El bibliotecario espera dos definiciones: si `publicada` va antes o después del merge, y si se agrega el prefijo `tareas:` a CLAUDE.md.
4. **Para la fase siguiente (propuesto por Carlos, registrado):**
   - el diseñador recibe en memoria los párrafos citados de la noticia;
   - el verificador corre también antes de simular y ejecuta numéricamente el `task_space`;
   - PLT02 marca escenarios e intervenciones como *observado* o *a priori*.
5. **Máquina de estados y contratos (congelados en CP1):**
   - retroceso del verificador a `borrador` cuando el defecto es de la tarea;
   - un lugar en `evaluacion` (v1.1) para las 3 corridas y la marca `evaluacion_inestable` (hoy en un archivo hermano que el bibliotecario no publica);
   - aclarar en `noticia` que el título cuenta para la invariante 3 (ya decidido por Carlos);
   - desempate entre candidatos (hoy, orden de llegada).
6. **Simulador:**
   - reformular SIM01 §5 caso 1 ("codificación comparable + bloqueos ±1");
   - servir los recursos a solicitud a los estudiantes simulados (exige tocar `sim.py` más allá de `llamar()`);
   - corregir la sobre-competencia (perfiles N1–N3);
   - auditar los niveles N2/N3 interpolados.
7. **Evaluador:** el techo de 23–24 (5.4) refuerza la recalibración v1.4 con doble codificación humana (condición 2 de CP1) y ejemplos 0/1/2 para validación y autenticidad.
8. **Redactor:** regla explícita para que `que_aprende` no afirme nada que no esté en la traza; o que el verificador lo trate como crítico.
9. **Historial local:** reescribir los commits locales posteriores a `3582ad4` para quitar el titular completo de CIPER **antes del primer push** (no se puede deshacer; no se hace sin orden).
10. **Pendientes técnicos:**
    - MED01 v1.2 (URLs de DW, enlaces `CBMi…` de gnews, bloqueo anti-bot de Nature);
    - el ciclo no persiste el gasto cuando lo corta una excepción ajena al tope;
    - `escenarios.ipynb`;
    - el caso 1 del verificador;
    - el monto definitivo del tope semanal [D].
