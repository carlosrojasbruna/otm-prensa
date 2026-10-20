# INV00 – Inventario de insumos para OTM-Prensa

| Campo | Valor |
|---|---|
| Versión | v0.4 (v0.3: 4 tareas de BF18; v0.4: puntajes provisionales, decisiones de Carlos en GOB01/MED01/MAR03 v1.0) |
| Fecha | 2026-10-20 |
| Origen | Revisión de las carpetas `IPRE INVIERNO 2026`, `IDEA MODELAMIENTO` y `modelamiento` (OneDrive UC) |
| Uso | Mapa de qué existe, dónde está y qué falta para llegar al Checkpoint 1 (contratos congelados) del plan de construcción |

Estado: **LISTO** = se usa tal cual · **ADAPTAR** = existe pero hay que reescribirlo para el pipeline · **FALTA** = hay que crearlo · **DECIDIR** = requiere una decisión de Carlos o del equipo.

## 1. Marcos conceptuales

| Insumo requerido | Fuente encontrada | Estado | Nota |
|---|---|---|---|
| Ciclo de modelamiento (7 fases) con códigos operativos | `IDEA MODELAMIENTO/insumos/INS04` §2 (P1-MRS … P7-EXP, EMK, OFF) | LISTO | Ya tiene ejemplos y regla de fase dominante. Se reutiliza como vocabulario del diseñador, del simulador y de la guía |
| Bloqueos en transiciones (B12…B56, B-LEX) y resolución (peer/self/teacher) | INS04 §3.1 | LISTO | Base de los "escenarios" de la guía docente |
| Intervenciones docentes (Zech Z1–Z5; Leiß nivel/objetivo/activador) | INS04 §4 | LISTO | Base de las preguntas de andamiaje por fase |
| Estilos de pensamiento (V/A/I) y niveles de competencia (N1–N4) | INS04 §5, INS08 §2–3 | ADAPTAR | Los textos de N1–N4 mencionan Pitágoras (específicos de Sugarloaf). Hay que parametrizarlos por tramo de edad y contenido de cada tarea |
| Definición de tarea de modelamiento (vs. ejercicio contextualizado) | Rúbrica de calidad v4 (IPRE, Abiam) + Borromeo Ferri 2018 cap. 3 | LISTO | La definición operativa **es** la rúbrica: 12 criterios |
| Panorama teórico general (Kaiser & Sriraman, Niss & Blum, PCK, GenAI) | `modelamiento/Mathematical Modeling_ Definitions, Frameworks, Contexts.md` | LISTO | Sirve para el marco del documento investigativo, no para los agentes |
| Referencias verificadas en APA 7 con localizadores | INS01 | LISTO | BL07, BF06, BF18, Galbraith & Stillman, etc. |
| Niveles por edad | `MAR03 v1.0`: P (10–12), S (13–18, sub-tramos S1/S2), U (18–20) | LISTO (decidido 2026-10-20) | Ligado al criterio 9 de la rúbrica y a los niveles N1–N4 de INS08 |
| Estándares disciplinares (FID, Chile) | `modelamiento/mediaestandares.md.txt` | LISTO | Útil para la variante 18–20 (pedagogía) y para `P1 ajuste curricular` |

## 2. Rúbricas

| Insumo requerido | Fuente encontrada | Estado | Nota |
|---|---|---|---|
| Rúbrica de calidad de la tarea (¿es modelación?) | `IPRE/Problema Modelamiento y Rubrica revisada Abiam Muñoz.pdf` §2.1, **v4**, 12 criterios × (0,1,2), máx. 24 | LISTO | Reemplaza la de 7 criterios/21 puntos que propuse en el plan. Se codifica en `RUB01` (md + json) |
| Rúbrica de adecuación del problema al curso y grupo (P1–P5, máx. 10) | mismo PDF | LISTO | Se codifica en `RUB02`. Es la que decide el **nivel de edad recomendado** y las variantes |
| Rúbrica de diseño de la clase (C1–C9, máx. 18) + ficha mínima | mismo PDF | LISTO | Se codifica en `RUB03`. Es el **contrato de la guía docente**: la guía debe permitir puntuar C1–C9 |
| Calibración humana de la rúbrica de calidad | mismo PDF: Giant's shoes 24, vapes 24, plástico 22, población belga 16, con puntaje por criterio (se descarta el puntaje de la tarea propia) | LISTO | Son las **tareas-oro** iniciales (4). Ver `tareas-oro/puntajes_v0.4.csv` |
| Rúbrica de evaluación del estudiante por fase | — | FALTA | Se construye desde cero por fase del ciclo (INS04 §2), tres niveles |
| Versión corta para el filtro de modelabilidad | — | FALTA | Se propone en `RUB01` §4: criterios 1, 3, 4, 5, 8 aplicados a la noticia, umbral 7/10 |

## 3. Tareas-oro (grupo de referencia)

**Decisión (2026-10-20):** el grupo de referencia se construye **solo con tareas de la literatura**. Las tareas propias del equipo no se reciclan como tareas-oro ni como insumo del banco; el banco parte de cero desde la prensa.

| Tarea | Fuente | Tramo probable | Puntaje humano (RUB01) | Estado |
|---|---|---|---|---|
| Giant's shoes (Blum 2011) | PDF rúbrica Abiam | S | 24/24 | LISTO |
| Vapes/litio (Wiegand & BF 2026) | PDF rúbrica Abiam | S | 24/24 | LISTO |
| Residuos plásticos (Bulut & BF 2025) | PDF rúbrica Abiam | P | 22/24 | LISTO (caso descrito) |
| Población belga (Deprez 2011) – control de borde | PDF rúbrica Abiam | U | 16/24 | LISTO |
| Sugarloaf (Blum & Leiß 2007) | INS02 v0.2 | S | 20/24 (prov.) | LISTO |
| **Port of Hamburg** (BF 2018, p. 44) | Extraído 2026-10-20, literal | S | 24/24 (prov.) | LISTO. Texto tomado de un boletín: el caso más parecido a una tarea desde prensa |
| **Lighthouse** (BF 2018, p. 106) | Extraído 2026-10-20, literal | S | 20/24 (prov.) | LISTO. Trae escenarios de estudiantes publicados (modelo para PLT02 §4) |
| **St. Michael's Church** (BF 2018, p. 53) | Extraído 2026-10-20, literal | P | 21/24 (prov.) | LISTO. Piso del nivel P |
| **A Clear Day at the Ocean** (BF 2018, p. 43) | Extraído 2026-10-20, literal | S | 7/24 (prov.) | LISTO. **Control negativo**: la autora dice que no es modelación |

Total: 9 tareas puntuadas: 4 por Abiam (humano) y 5 por Claude (**provisional**, ver `PUNTUACION-PROVISIONAL_claude_v0.1`), con dos controles (borde 16 y negativo 7). Suficiente para lanzar el builder; recalibrar con doble codificación humana antes de reportar. Todas con enunciado literal y localizador de página, salvo residuos plásticos (caso descrito).

## 4. Simulador

| Insumo requerido | Fuente | Estado | Nota |
|---|---|---|---|
| Código | `IDEA MODELAMIENTO/simulacion/sim.py` + README | LISTO | Usa `claude -p` sin API key; lee bloques ```json id``` / ```text id``` de los INS |
| Contrato de entrada: tarea | INS02 §7 (`task_module` YAML) + bloques `enunciado_es`, `foto_descripcion` | LISTO | El pipeline debe producir exactamente estos bloques por tarea |
| Contrato de entrada: perfiles y diseño | INS08 bloques `niveles`, `estilos`, `contexto_base`, `diseno_*` | ADAPTAR | Niveles por tramo de edad en vez de "9° grado con Pitágoras" |
| Contrato de entrada: prompts | INS09 (`student_system`, `student_turn`, `coder_system`, `coder_user`, `coder_schema`) | LISTO | Se reutiliza; el `coder_schema` es el **contrato de salida de trazas** |
| Contrato de salida: trazas codificadas | `corridas/piloto_v0.1/*_cod.json` | LISTO | Fase por turno, bloqueos, F1–F6, ruta, respuesta final |
| Regla de aislamiento (estudiantes no ven solución ni fenómenos) | INS02 §7 `agent_visibility` | LISTO | Se convierte en hook del pipeline |
| Corridas de ejemplo y hallazgos | `corridas/piloto_v0.1/` (16 corridas + HALLAZGOS) | LISTO | Casos de prueba del adapter |
| Codificación humana del piloto (Hugo, Mahsa) | `codificacion_humana/*.xlsx`, INS16, ACUERDO | LISTO | Evidencia de validez para el documento investigativo |

## 5. Plantillas

| Insumo requerido | Fuente | Estado |
|---|---|---|
| Plantilla de tarea | Estructura: enunciado → recursos no reveladores → mapa a priori del ciclo → espacio de soluciones → rúbrica aplicada (RUB01 criterio 12 y RUB03 C2) | `PLT01` en esta entrega |
| Plantilla de guía docente | Ficha mínima C1–C9 (RUB03) + reporte al profesor INS04 §6 | `PLT02` en esta entrega |
| Ejemplo de guía "ideal" | — | FALTA: la primera guía completa la produce el prototipo (CP2) y el equipo la corrige; esa versión corregida pasa a ser el ejemplo |

## 6. Medios, ética y gobernanza

| Insumo requerido | Fuente | Estado |
|---|---|---|
| Lista blanca de medios | `MED01 v1.0`: es/en; Emol, CNN Chile, CIPER, Canal 13, Reuters, BBC | LISTO (decidido 2026-10-20); URLs de RSS chilenos por verificar por devops, con respaldo Google News RSS |
| Consentimiento informado y comité de ética | `TAREA MODELAMIENTO/Etica/` (Protocolo CEC UC revisión expedita, carta de compromiso) | LISTO para producciones de estudiantes; FALTA el aviso de uso de datos del sitio docente |
| Campos del perfil docente (piloto vs. final) | GOB01 v1.0 §5 | LISTO para el piloto; país [D] para la versión final |
| Gobernanza | `GOB01 v1.0`: API key y GitHub de Carlos, simulador vía API, umbral 20/24, CC BY-NC-SA + MIT | LISTO (decidido 2026-10-20); quedan [D] no bloqueantes |

## 7. Entregas

- `RUB01_calidad-tarea_v4.0` (md + json): rúbrica de calidad codificada, con versión corta para el filtro.
- `RUB02_adecuacion-problema_v1.0` (md + json) y `RUB03_diseno-clase_v1.0` (md + json).
- `tareas-oro/puntajes_v0.4.csv` + fichas de las 4 tareas puntuadas y 5 por puntuar (solo literatura; 4 extraídas literalmente de Borromeo Ferri 2018).
- `MAR03_niveles-por-edad_v1.0` (P/S/U).
- `PLT01_plantilla-tarea_v0.1`, `PLT02_plantilla-guia-docente_v0.1`.
- `SIM01_contrato-adapter_v0.1`: qué recibe y qué entrega el simulador dentro del pipeline.
- `MED01_medios_v1.0.yaml`.
- `GOB01_gobernanza_v1.0`.

## 8. Estado de CP1 (2026-10-20)

Insumos: **completos para lanzar el builder.** Quedan de parte de Carlos:
- [ ] Crear el repo `otm-prensa` en su GitHub y cargar los secrets `ANTHROPIC_API_KEY` y `GH_TOKEN` (GOB01 §7).
- [ ] Definir el tope de gasto mensual en la Console.

Recalibraciones posteriores (no bloquean):
- [ ] Doble codificación humana de Sugarloaf, Port of Hamburg, Lighthouse, St. Michael's Church y Clear Day para reemplazar los puntajes provisionales.
- [ ] Rúbrica del estudiante por fase (PLT02 §7), antes de CP2.
- [ ] Aviso de uso de datos del sitio y campos finales del perfil, antes de CP3.
