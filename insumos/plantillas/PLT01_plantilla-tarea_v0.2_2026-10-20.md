# PLT01 – Plantilla de tarea de modelamiento desde prensa

| Campo | Valor |
|---|---|
| Versión | v0.2 (v0.1 → v0.2, 2026-10-20: áreas temáticas con los ids de MED01; lista completa de estados de la máquina de estados; recursos `de_entrada` van dentro de `enunciado_es` para el simulador) |
| Fecha | 2026-10-20 |
| Origen | `task_module` de INS02 §7 (Sugarloaf) + criterios 12 (RUB01) y C2 (RUB03) |
| Uso | Salida del agente 3 (diseñador). El evaluador puntúa RUB01 sobre las secciones 1–3; el adapter del simulador toma los bloques marcados |
| Regla | Lo que va en esta plantilla describe la **tarea**. Lo que depende de la clase va en PLT02 |

---

```yaml frontmatter
id: AAAA-MM-slug
titulo: ""
estado: borrador            # borrador | evaluada | revisada | simulada | con_guia | verificada | publicada | archivada
version: 1
fecha: AAAA-MM-DD
noticia:
  medio: ""
  titulo: ""
  fecha: AAAA-MM-DD
  url: ""
  resumen_propio: ""        # ≤ 80 palabras, sin texto literal de la noticia
  cifras_usadas: []         # cada cifra con su localizador en la noticia
nivel_principal: S          # P | S | U  (MAR03); si S, opcional sub_tramo: S1 | S2
variantes: {abajo: P, arriba: U}
area: ""                    # ids de MED01: medio_ambiente | economia | salud | ciencia_tecnologia | deporte | transporte_ciudad | sociedad_datos
contenidos_matematicos: []
tiempo_estimado: "2 sesiones de 90 min"
rubrica_rub01: {total: null, por_criterio: {}}
rubrica_rub02: {P: null, S: null, U: null}   # adecuación por nivel
modelo_y_prompt: {diseñador: "", version_prompt: "", version_rubrica: "4.0"}
```

## 1. Enunciado para estudiantes (nivel principal)

```text enunciado_es
[Situación real tomada de la noticia, en palabras propias. Termina en una pregunta abierta que no prescribe método. Incluye "pueden pedir información adicional" si aplica.]
```

```text foto_descripcion
[Descripción textual de la imagen o ícono de la tarea, para el simulador y para el ilustrador. "none" si no hay.]
```

### 1.1 Variante hacia abajo (tramo __)
[Qué datos se entregan además, qué se simplifica en la pregunta.]

### 1.2 Variante hacia arriba (tramo __)
[Qué se quita o qué se exige además: segundo conjunto de datos, sensibilidad, comparación de modelos.]

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|
| R1 | | a_solicitud / de_entrada | | noticia (localizador) / otra fuente |

Regla (decisión de architect, 2026-10-20): el simulador solo recibe `enunciado_es`, `foto_descripcion` y los recursos `a_solicitud`. Todo recurso `de_entrada` debe estar incorporado en el texto de `enunciado_es`.

Restricción: ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase (INS04) | Decisión o actividad esperable | Evidencia observable | Punto crítico / bloqueo probable (B12…B56) |
|---|---|---|---|
| P1-MRS Comprender | | | |
| P2-RM Simplificar | | | |
| P3-MM Matematizar | | | |
| P4-WM Trabajar | | | |
| P5-INT Interpretar | | | |
| P6-VAL Validar | | | |
| P7-EXP Exponer | | | |

## 4. Espacio de soluciones (para el evaluador, el simulador-codificador y la guía; **no** para estudiantes)

```yaml task_space
required_assumptions: []
reference_solution:
  steps: ""
  result: ""
  acceptable_range: ""
routes:                    # al menos 3 modelizaciones distintas (C2 de RUB03)
  - {id: R1, nombre: "", nivel: "", modelo: "", resultado: ""}
  - {id: R2, nombre: "", nivel: "", modelo: "", resultado: ""}
  - {id: R3, nombre: "", nivel: "", modelo: "", resultado: ""}
modelo_inadecuado: {id: RX, por_que_falla: ""}
validation_evidence: ""    # dato independiente, no usado para construir el modelo
agent_visibility:
  students: [enunciado_es, foto_descripcion, recursos_a_solicitud]   # nunca recursos de_entrada por separado ni task_space
  coder: [enunciado_es, task_space]
  guide: [all]
```

## 5. Rúbrica aplicada (la llena el evaluador)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1–12 | | | | |
| | **Total** | /24 | | |
