# ¿Cuántas muertes evitaría un extracto de hongo en nuestro hospital?

Tarea `2026-11-extracto-hongo-cirugia-gastrica-v2` · versión 2 · 2026-11-24 · nivel U · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-11-extracto-hongo-cirugia-gastrica-v2
titulo: ¿Cuántas muertes evitaría un extracto de hongo en nuestro hospital?
estado: verificada
version: 2
fecha: '2026-11-24'
noticia:
  noticia_id: 2026-11-23-npr-mushroom-supplements-promise-health-benefits-what
  medio: NPR
  titulo: Mushroom supplements promise health benefits. What does the science say?
  fecha: '2026-11-23'
  url: https://www.npr.org/2026/11/23/nx-s1-6047791/mushroom-supplements-health-research
  resumen_propio: Un reportaje de ciencia examina las promesas de los suplementos de hongos (salud intestinal, concentración, inmunidad) y las contrasta con la escasa evidencia clínica. Describe un extracto del hongo cola de pavo, estudiado en Japón en pacientes operados de cáncer gástrico, que un metaanálisis asoció con menor mortalidad, y una revisión de 2023 que examinó miles de estudios, conservó solo una pequeña parte y obtuvo resultados mixtos.
  cifras_usadas:
  - valor: 8,009
    unidad: pacientes
    que_es: pacientes incluidos en el metaanálisis sobre PSK tras cirugía de tumor gástrico
    localizador:
      fuente: noticia
      ubicacion: párrafo 97
  - valor: 12%
    unidad: porcentaje de reducción del riesgo de muerte
    que_es: reducción del riesgo de muerte en pacientes que recibieron PSK
    localizador:
      fuente: noticia
      ubicacion: párrafo 97
nivel_principal: U
variantes:
  abajo: S
  arriba: null
area: salud
contenidos_matematicos:
- riesgo relativo y absoluto
- número necesario a tratar
- incertidumbre y simulación
- análisis de sensibilidad
- decisión bajo incertidumbre
tiempo_estimado: 2 sesiones de 90 min
rubrica_rub01:
  total: 24
  por_criterio:
    genuino: 2
    abierta: 2
    decisiones: 2
    realismo: 2
    autenticidad: 2
    contexto: 2
    ciclo: 2
    validacion: 2
    nivel: 2
    autodiferenciacion: 2
    fecundidad: 2
    recursos: 2
rubrica_rub02:
  P: null
  S: null
  U: null
modelo_y_prompt:
  diseñador: claude-sonnet-5-5
  version_prompt: '1.1'
  version_rubrica: '4.0'
```

## 1. Enunciado para estudiantes (nivel principal)

```text enunciado_es
El PSK es un extracto purificado del hongo cola de pavo, estudiado en Japón en personas operadas de un tumor gástrico. Un metaanálisis que reunió a 8.009 pacientes, que recibieron en casi todos los casos quimioterapia, asoció el extracto con una reducción de 12 % en el riesgo de muerte. El comité de un hospital chileno debe decidir si lo incorpora al tratamiento posterior a la cirugía. Nadie en el comité sabe cuántos de sus pacientes mueren hoy, cuánto costaría el extracto ni si sus pacientes se parecen a los del estudio. Pueden pedir información adicional. ¿Cuántas muertes podría evitar el extracto en los pacientes del hospital, qué tan segura es esa cifra y qué le recomendarían al comité?
```

```text foto_descripcion
Ícono de un hongo junto a una balanza que compara un frasco de cápsulas con una silueta de paciente en camilla.
```

### 1.1 Variante hacia abajo (tramo S2)

Se pide estimar cuántas muertes se evitarían en un grupo de pacientes del hospital con una sola mortalidad basal acordada, sin intervalo de incertidumbre; la cuestión central es distinguir reducción relativa de absoluta y comparar dos mortalidades basales.

### 1.2 Variante hacia arriba

No hay.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Datos del metaanálisis tal como se entregan en el enunciado | El PSK es un extracto purificado del hongo cola de pavo, estudiado en Japón. El metaanálisis incluyó a 8.009 pacientes operados de tumor gástrico, que recibieron en casi todos los casos quimioterapia, y asoció el extracto con una reducción de 12 % en el riesgo de muerte. | de_entrada | P1-MRS | noticia, párrafo 97 |
| R2 | Tarjeta con la mortalidad del hospital | Supuesto del escenario: el hospital tiene registros de la mortalidad observada de sus pacientes operados de tumor gástrico en años anteriores, medida como proporción que fallece dentro de un plazo. El comité pide que el grupo decida qué plazo usar y qué valor adoptar, o que lo estime con estadísticas públicas de cáncer gástrico. | a_solicitud | P2-RM | supuesto del escenario |
| R3 | Tarjeta sobre la comparabilidad de los pacientes | Supuesto del escenario: los pacientes del metaanálisis fueron tratados principalmente en Japón y recibieron además el tratamiento complementario habitual de su centro. Se desconoce si los pacientes del hospital chileno tienen etapas de enfermedad similares. | a_solicitud | P2-RM | supuesto del escenario |
| R4 | Ficha de un ensayo aleatorizado de seguimiento largo con PSK; se entrega después de que el grupo presente su estimación | Ensayo aleatorizado hecho en hospitales del centro de Japón con pacientes operados de cáncer gástrico con intención curativa. Todos recibieron quimioterapia y a un grupo se le añadió PSK. El seguimiento duró varios años. La supervivencia fue mayor en el grupo con PSK, y la diferencia absoluta observada es bastante mayor que la que resulta de aplicar la reducción relativa del metaanálisis a la mortalidad del grupo sin PSK. Fue un ensayo pequeño frente al metaanálisis y su intervalo de confianza es amplio e incluye la reducción del metaanálisis. Sus pacientes estaban seleccionados (tumores de extensión intermedia, límite de edad y una prueba cutánea que indicaba respuesta inmune conservada) y no hubo placebo. Las cifras están en el resumen público del artículo y el docente las entrega desde ahí. | a_solicitud | P6-VAL | otra fuente: Nakazato H. y colaboradores, «Efficacy of immunochemotherapy as adjuvant treatment after curative resection of gastric cancer», The Lancet 343(8906):1122-1126, 1994 |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender que la reducción de 12 % es relativa al riesgo de partida y que depende del plazo y de la población; precisar qué decide el comité. | Reformulación escrita de la cifra y de las variables que faltan (mortalidad basal, tamaño del grupo, costo). | B12 |
| P2-RM Simplificar | Elegir mortalidad basal y plazo, suponer comparabilidad con los pacientes del estudio, suponer reparto entre tratados y controles y eventos. | Supuestos explícitos con valores o rangos y tarjetas solicitadas (R2, R3). | B23 |
| P3-MM Matematizar | Construir el modelo de riesgo: riesgo tratado = riesgo basal por el factor de reducción; muertes evitadas = pacientes por diferencia de riesgo; número necesario a tratar; incertidumbre con el error del logaritmo del riesgo relativo. | Expresiones con parámetros definidos y distribución elegida para el riesgo basal y el efecto. | B34 |
| P4-WM Trabajar | Calcular muertes evitadas por cada mil pacientes, el número necesario a tratar, un intervalo y la sensibilidad a la mortalidad basal, con simulación si lo desean. | Tabla o gráfico de muertes evitadas en función del riesgo basal, con banda de incertidumbre. | B45 |
| P5-INT Interpretar | Interpretar el resultado para el hospital, separando beneficio esperado, incertidumbre y límites de transferir el estudio. | Frase que traduce el resultado a pacientes del hospital y declara qué no se sabe. | B56 |
| P6-VAL Validar | Pedir R4 tras presentar la estimación y comprobar la coherencia: comparar la reducción absoluta que predice el modelo con la diferencia de supervivencia que informa el ensayo, y verificar la cota lógica de que no se pueden evitar más muertes que las esperadas sin tratamiento. Si no calzan, explicar la discrepancia con lo que R4 dice del ensayo antes de cambiar la mortalidad basal. | Comparación escrita entre muertes evitadas predichas y diferencia observada, con una explicación de la discrepancia (tamaño, intervalo, selección de pacientes, plazo, ausencia de placebo) y revisión de supuestos. | B67 |
| P7-EXP Exponer | Recomendar al comité con criterio explícito (por ejemplo, costo por muerte evitada) y con sensibilidad a la mortalidad basal. | Informe breve con tabla de escenarios y recomendación condicional. | — |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- La reducción de 12 % se interpreta como reducción relativa del riesgo de muerte en un plazo común.
- La mortalidad basal del hospital debe estimarse o solicitarse; no se entrega.
- El tamaño del grupo de pacientes del hospital debe estimarse.
- Los pacientes del hospital se parecen a los del metaanálisis, supuesto discutible.
- Para el intervalo se supone un solo ensayo de dos grupos iguales, un mismo plazo de seguimiento y un número de muertes derivado de la mortalidad basal.

### Solución de referencia

1) Interpretar 12 % como reducción relativa: riesgo tratado = 0,88 por riesgo basal p0. 2) Reducción absoluta ARR = 0,12 por p0; número necesario a tratar NNT = 1/ARR. 3) Con p0 = 0,40 (supuesto): ARR = 0,048, NNT ≈ 21 y por cada mil pacientes ≈ 48 muertes evitadas. Con p0 = 0,20: ARR = 0,024, NNT ≈ 42, 24 por mil. Con p0 = 0,60: ARR = 0,072, NNT ≈ 14, 72 por mil. 4) Incertidumbre: se supone, de forma simplificada, un solo ensayo con los 8.009 pacientes repartidos en mitades de unos 4.005 y p0 = 0,40. Las muertes son ≈ 1.602 en el control (a) y ≈ 1.410 en los tratados (c). El error estándar del log del riesgo relativo es sqrt(1/a − 1/n1 + 1/c − 1/n2) ≈ sqrt(0,000624 − 0,000250 + 0,000709 − 0,000250) ≈ 0,029. El RR queda entre 0,83 y 0,93 al 95 %, y la reducción absoluta entre 0,027 y 0,067, es decir, 27 a 67 muertes evitadas por mil (NNT entre 15 y 36). Este intervalo sale de supuestos simplificadores (un solo ensayo de dos grupos iguales, un mismo plazo) y subestima la incertidumbre real, porque el metaanálisis reúne varios ensayos distintos: es una cota optimista de qué tan segura es la cifra. 5) Después de presentar la estimación, se compara con la ficha R4 y con la cota lógica, y se añaden costo y comparabilidad para la recomendación.

**Resultado.** Con una mortalidad basal intermedia (por ejemplo 40 % en el plazo elegido) se evitarían unas 48 muertes por cada mil pacientes tratados (NNT ≈ 21), con un intervalo, bajo supuestos simplificadores, de entre 27 y 67 por mil. Esa banda es una cota optimista de la incertidumbre real. El resultado es proporcional a la mortalidad basal y cae si los pacientes del hospital difieren de los del estudio. La recomendación debe ser condicional al costo, a la comparabilidad y a la mortalidad basal real.

**Rango aceptable.** Muertes evitadas entre ≈ 24 y 72 por mil para mortalidad basal entre 0,20 y 0,60; cualquier cifra coherente con el supuesto de mortalidad basal declarado y con la lógica relativa vs. absoluta es aceptable. Con mortalidad basal de 0,40 y el intervalo simplificado, entre ≈ 27 y 67 por mil. Resultados que usen 12 puntos porcentuales no son aceptables.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Conversión directa de riesgo relativo a absoluto | S2 | Muertes evitadas = pacientes por mortalidad basal por 0,12, para dos o tres mortalidades basales | Por cada mil pacientes: 24, 48 y 72 muertes evitadas con mortalidad basal de 0,20, 0,40 y 0,60 |
| R2 | NNT con intervalo por aproximación normal del log RR | U | ARR = p0(1 − RR), NNT = 1/ARR; error estándar del log RR = sqrt(1/a − 1/n1 + 1/c − 1/n2), con eventos supuestos en cada brazo de igual tamaño | Con p0 = 0,40: NNT ≈ 21, ARR entre 0,027 y 0,067 (27 a 67 muertes evitadas por mil), intervalo que subestima la incertidumbre real |
| R3 | Simulación de Monte Carlo con incertidumbre en riesgo basal y efecto | U | Distribuciones para p0 (según registros del hospital) y RR (normal en escala log, con error estándar cercano a 0,029 como piso optimista) y simulación de muertes evitadas en un grupo del hospital | Distribución de muertes evitadas con mediana y percentiles 2,5 y 97,5; probabilidad de superar un umbral de decisión |
| R4 | Análisis de decisión con costo | U | Costo por muerte evitada = costo por paciente por NNT, comparado con un umbral del comité y con sensibilidad a p0 | Recomendación condicionada: el extracto es atractivo si el costo por paciente por NNT es menor que el umbral aceptado por el comité |

### Modelo inadecuado (RX: restar 12 puntos porcentuales a la mortalidad (por ejemplo, de 40 % a 28 %).)

Confunde reducción relativa con absoluta: el 12 % se aplica al riesgo de partida, por lo que con 40 % de mortalidad el riesgo baja a 35,2 % y no a 28 %. Sobrestima el beneficio unas 2,5 veces y ignora la incertidumbre y la dependencia de la mortalidad basal.

### Evidencia de validación (independiente del modelo)

Comprobación de coherencia con la ficha que entrega R4 después de que el grupo presente su estimación: comparar la reducción absoluta que predice el modelo (con su rango de mortalidad basal y su intervalo) con la diferencia de supervivencia que observó el ensayo descrito en R4, y mantener la cota lógica de que las muertes evitadas no pueden exceder las muertes esperadas sin tratamiento. Si las cifras no calzan, el grupo primero explica la discrepancia con lo que R4 informa del ensayo (su tamaño, la amplitud de su intervalo de confianza, la selección de pacientes, el plazo de seguimiento y la ausencia de placebo) y solo después revisa su mortalidad basal o su supuesto de comparabilidad. El contraste sirve para discutir el alcance y los límites del modelo, no para ajustarlo a ese resultado.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | Hay una necesidad real de decisión y no se entrega ningún modelo. Quien resuelve debe pasar por su cuenta de la reducción relativa a muertes absolutas. Que el enunciado nombre lo que se desconoce (mortalidad, costo, comparabilidad) orienta, pero no fija la estructura del cálculo. | — |
| 2 | abierta | 2 | La pregunta no prescribe ningún procedimiento. Admite varios modelos defendibles: distintos plazos, valores basales, ajustes por comparabilidad y formas de expresar la incertidumbre. | — |
| 3 | decisiones | 2 | Resolver exige varias decisiones: elegir un plazo y una mortalidad basal, estimar el volumen de pacientes, suponer cuánto se trasladan los resultados japoneses y pedir información (R2, R3). Son decisiones de modelación sustantivas. | — |
| 4 | realismo | 2 | Que un comité hospitalario evalúe incorporar un tratamiento a partir de evidencia publicada es una situación claramente plausible fuera de la escuela. | — |
| 5 | autenticidad | 2 | Los datos del metaanálisis y del ensayo aleatorizado (R4, cuyas cifras salen de un resumen público) son componentes auténticos. Constituyen el núcleo de la tarea y no fueron creados para enseñar. | — |
| 6 | contexto | 2 | El contexto clínico condiciona las decisiones, como el plazo, la mortalidad basal y la transferibilidad. También es indispensable para juzgar la seguridad de la cifra y formular la recomendación. | — |
| 7 | ciclo | 2 | Responder obliga a recorrer todo el ciclo: comprender la situación clínica, simplificar con supuestos, matematizar el paso de riesgo relativo a muertes absolutas, calcular con incertidumbre, interpretar para el comité y validar. Ninguna fase viene hecha por el enunciado. | — |
| 8 | validacion | 2 | R4 aporta un ensayo independiente, no usado en la construcción del modelo, para contrastar la estimación y discutir sus límites. A eso se suman las estadísticas públicas de mortalidad. | — |
| 9 | nivel | 2 | El contexto y el lenguaje son comprensibles para estudiantes universitarios. La demanda corresponde a la descrita en MAR03 para U: modelo probabilístico, análisis de sensibilidad y crítica del modelo frente a datos nuevos. | — |
| 10 | autodiferenciacion | 2 | El piso es accesible: basta multiplicar una mortalidad basal estimada por el 12 % y por un número de pacientes. El techo es alto, con intervalos de incertidumbre, ajustes por heterogeneidad, análisis de sensibilidad y comparación de escenarios. | — |
| 11 | fecundidad | 2 | La discrepancia con R4 abre preguntas sobre selección de pacientes, generalizabilidad, costo y límites del modelo. También permite comparar las soluciones de distintos grupos. | — |
| 12 | recursos | 2 | La información necesaria se obtiene a solicitud o mediante estadísticas públicas accesibles para el nivel U. R4, que contiene una pista sobre el modelo, se entrega solo después de la estimación, así que no revela la solución. El volumen de pacientes no se entrega, pero puede suponerse como parte del modelo. | — |
| | **Total** | **24/24** | | |
