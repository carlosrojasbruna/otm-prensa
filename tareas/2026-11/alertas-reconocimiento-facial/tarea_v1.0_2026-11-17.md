# ¿Cuánto creerle a una alerta de reconocimiento facial?

Tarea `2026-11-alertas-reconocimiento-facial` · versión 1 · 2026-11-16 · nivel U · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-11-alertas-reconocimiento-facial
titulo: ¿Cuánto creerle a una alerta de reconocimiento facial?
estado: verificada
version: 1
fecha: '2026-11-16'
noticia:
  noticia_id: 2026-11-16-latercera-como-israel-cargo-3-5-millones
  medio: La Tercera
  titulo: Cómo Israel cargó 3,5 millones de fotografías en plataforma de Amazon para rastrear a palestinos
  fecha: '2026-11-16'
  url: https://www.latercera.com/mundo/noticia/como-israel-cargo-35-millones-de-fotografias-en-plataforma-de-amazon-para-rastrear-a-palestinos/
  resumen_propio: Una investigación periodística describe que un área militar israelí habría subido a la nube de Amazon un gran volumen de fotos de palestinos para probar reconocimiento facial, con posibles usos de vigilancia en puestos de control de Gaza y Cisjordania. Amazon afirma que no ve el contenido de las cargas de sus clientes y que sus reuniones con ellos son rutinarias. El texto reconoce que no está claro si esas imágenes se tomaron en los controles.
  cifras_usadas:
  - valor: 3,5 millones
    unidad: imágenes
    que_es: Cantidad de imágenes subidas a la plataforma Rekognition de Amazon, cuya procedencia no está clara
    localizador:
      fuente: noticia
      ubicacion: párrafo 8
nivel_principal: U
variantes:
  abajo: S
  arriba: null
area: sociedad_datos
contenidos_matematicos:
- probabilidad condicional y teorema de Bayes
- distribución binomial y aproximación de Poisson
- tasas de error y curvas ROC
- análisis de sensibilidad
- órdenes de magnitud
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
Una investigación periodística informó que un área militar israelí habría subido 3,5 millones de imágenes de palestinos a Rekognition, el servicio de reconocimiento facial de Amazon, para probar esa tecnología con posible uso en puestos de control. Todavía no está claro de dónde salieron esas imágenes. Una organización de derechos digitales debe asesorar a un grupo de ciudadanos sobre cuánto confiar en un sistema así. Imaginen un puesto de control donde el rostro de cada persona que pasa se compara con una base del tamaño de esa colección, y el sistema avisa a un agente cuando cree reconocer a alguien. ¿Qué tan confiable es una alerta de ese sistema y bajo qué condiciones recomendarían tomarla en serio? Pueden pedir información adicional.
```

```text foto_descripcion
Ícono de una cámara apuntando a una fila de siluetas de personas, con una de ellas marcada por un recuadro y un signo de exclamación.
```

### 1.1 Variante hacia abajo (tramo S)

Se pide solo estimar cuántas falsas alertas esperaría el puesto en una jornada, sin exigir la probabilidad de que una alerta sea correcta; el grupo estima por su cuenta la tasa de error y compara dos o tres valores (comparación de escenarios, sin Bayes formal). El contexto no cambia.

### 1.2 Variante hacia arriba

No hay.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Dato central de la noticia sobre el tamaño de la colección | Se habrían subido 3,5 millones de imágenes a la plataforma Rekognition de Amazon; su procedencia no está clara. | de_entrada | P1-MRS | noticia, párrafo 8 |
| R2 | Descripción del funcionamiento supuesto del puesto de control | Supuesto del escenario: cada persona que llega se fotografía y su rostro se compara con la base; si el sistema declara una coincidencia, se emite una alerta que un agente debe atender. | a_solicitud | P1-MRS | supuesto del escenario |
| R3 | Respuesta a la consulta sobre flujo de personas y proporción de personas buscadas | Supuesto del escenario: no hay cifras públicas confiables sobre cuántas personas pasan por el puesto ni cuántas son realmente buscadas; el grupo debe proponer rangos plausibles y justificarlos. | a_solicitud | P2-RM | supuesto del escenario |
| R4 | Referencia externa sobre desempeño medido de algoritmos de reconocimiento facial | El NIST publica evaluaciones independientes de algoritmos comerciales de reconocimiento facial, con tasas de error medidas en pruebas controladas, que cambian según la calidad de la imagen y el grupo de personas. | a_solicitud | P6-VAL | otra fuente: NIST, Face Recognition Vendor Test (FRVT) |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Distinguir las imágenes de la base de las personas que pasan, y precisar qué significa que una alerta sea confiable (probabilidad de que la persona sea realmente la buscada). | Reformulan la pregunta con sus palabras y piden tasa de error del sistema, flujo de personas y proporción de buscadas. | B12 |
| P2-RM Simplificar | Simplificar: comparaciones independientes, tasa de falsa coincidencia constante, relación entre imágenes y personas distintas, rango de proporción de buscadas. | Lista escrita de supuestos con valores o rangos justificados. | B23 |
| P3-MM Matematizar | Modelar la probabilidad de al menos una falsa coincidencia entre muchas comparaciones y la probabilidad condicional de que una alerta sea acierto. | Expresiones con símbolos definidos para tasa de error, número de comparaciones y tasa base. | B34 |
| P4-WM Trabajar | Calcular para varios valores de la tasa de error y de la tasa base, usando aproximaciones o software. | Tabla o gráfico de la confiabilidad de la alerta según los parámetros. | B45 |
| P5-INT Interpretar | Traducir resultados: de cada cien alertas cuántas serían ciertas y qué condiciones harían razonable confiar. | Frases en contexto que dicen qué debería cumplir el sistema y qué decisión se recomienda. | B56 |
| P6-VAL Validar | Contrastar las tasas de error supuestas con evaluaciones independientes y discutir los límites del modelo (imágenes versus personas distintas, calidad de captura). | Comparación explícita entre sus rangos y la referencia externa, con ajuste de supuestos. | B67 |
| P7-EXP Exponer | Redactar la recomendación a la organización con rangos y advertencias. | Informe breve o presentación con la recomendación, supuestos y sensibilidad. | — |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- Cada persona que pasa se compara con la base completa y la comparación es independiente entre imágenes
- Existe una tasa de falsa coincidencia por comparación (o por persona) constante, que el grupo debe estimar o variar
- La proporción de personas realmente buscadas entre quienes pasan es pequeña y debe estimarse
- La sensibilidad del sistema (probabilidad de reconocer a una persona buscada) es alta pero no perfecta
- Se debe decidir si las imágenes corresponden a personas distintas o hay varias imágenes por persona

### Solución de referencia

1) Sea N el número de comparaciones por persona (como máximo 3,5 millones si cada imagen cuenta como una identidad) y f la probabilidad de falsa coincidencia por comparación. 2) Probabilidad de falsa alerta para una persona no buscada: q = 1-(1-f)^N, aproximadamente 1-exp(-N f). 3) Sea pi la proporción de personas buscadas entre quienes pasan y s la sensibilidad. 4) Valor predictivo de la alerta (Bayes): VPP = s·pi / (s·pi + (1-pi)·q). 5) Variar f, pi y N (sensibilidad) y observar que VPP es muy bajo si q es mayor que pi. 6) Condición para VPP mayor o igual a 0,5: q menor o igual a s·pi/(1-pi), o sea f aproximadamente menor que s·pi/N.

**Resultado.** Ejemplo ilustrativo: con f = 10^-7, N = 3,5 millones, q aproximadamente 0,29; con pi = una persona buscada cada diez mil y s = 0,9, el VPP es aproximadamente 0,0003, es decir, casi todas las alertas serían falsas. Para que la mitad de las alertas fueran ciertas, f debería ser del orden de 10^-11 o menor. La conclusión robusta: la confiabilidad de una alerta depende más de la tasa base y del número de comparaciones que de la exactitud declarada.

**Rango aceptable.** Cualquier conclusión cualitativa que muestre VPP bajo cuando la tasa de falsa alerta por persona supera la tasa base es aceptable; los valores numéricos dependen de los rangos supuestos para f (varios órdenes de magnitud), pi y s. Si se supone una sola identidad por persona y menos identidades que imágenes, N baja y el VPP sube, pero sigue siendo bajo para tasas base pequeñas.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Estimación por órdenes de magnitud | S | Falsas alertas esperadas = (personas que pasan) × N × f, comparando con el número esperado de personas realmente buscadas. | Para varios f plausibles, las falsas alertas superan por mucho a las verdaderas cuando N es del orden de millones. |
| R2 | Probabilidad de al menos una falsa coincidencia | S2 | q = 1-(1-f)^N con aproximación de Poisson 1-exp(-N f); tabla según f. | q pasa de casi 0 a casi 1 al subir f unas pocas potencias de diez; el punto de quiebre es N f del orden de uno. |
| R3 | Teorema de Bayes con tasa base | U | VPP = s·pi / (s·pi + (1-pi)·q), con análisis de sensibilidad en pi, q y s. | VPP muy bajo en el escenario base; condición cuantitativa sobre f para que la alerta sea confiable. |
| R4 | Modelo de umbral con distribuciones de puntajes | U | Puntajes de similitud con distribuciones para pares iguales y distintos; el umbral fija f y s (curva ROC); se optimiza el umbral con costos asimétricos de error. | Existe un umbral que equilibra falsas alertas y omisiones, pero con tasa base pequeña exige umbral muy estricto y sacrifica sensibilidad. |

### Modelo inadecuado (RX)

Tomar la exactitud alta declarada de un sistema como la probabilidad de que una alerta sea correcta: confunde sensibilidad o exactitud global con valor predictivo, ignora la tasa base y que cada persona se compara con millones de imágenes.

### Evidencia de validación (independiente del modelo)

Evaluaciones independientes publicadas de algoritmos de reconocimiento facial (NIST FRVT) con tasas de falsa coincidencia medidas en pruebas controladas; el grupo contrasta sus rangos de f con esas tasas y con una simulación en computador con distribuciones de puntajes, dato no usado al construir el modelo.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | Plantea una necesidad real de asesoría sin entregar regla, fórmula ni modelo. El razonamiento sobre falsos positivos y tasas base debe construirlo el grupo. | — |
| 2 | abierta | 2 | La pregunta no prescribe procedimiento. Admite varios modelos defendibles, como un conteo esperado de falsas alertas, un enfoque bayesiano o un análisis de umbrales y escenarios. | — |
| 3 | decisiones | 2 | Resolver exige estimar el flujo, la proporción de personas buscadas y las tasas de error, formular supuestos y solicitar información pertinente. | — |
| 4 | realismo | 2 | Se trata de una situación real reportada por la prensa. El puesto de control con comparación 1:N es claramente plausible. | — |
| 5 | autenticidad | 2 | El dato de la noticia fija el tamaño de la base, que es central para la comparación 1:N. La referencia a las evaluaciones del NIST es otro componente extraescolar auténtico integrado. | — |
| 6 | contexto | 2 | El contexto condiciona las decisiones de modelación: tamaño de la base, flujo y proporción de buscados. También es necesario para interpretar en qué condiciones conviene tomar en serio una alerta. | — |
| 7 | ciclo | 2 | Responder obliga a comprender el escenario, simplificarlo con supuestos, matematizarlo en términos de probabilidad condicional, calcular y volver a la situación para recomendar. El enunciado no deja ninguna fase hecha. | — |
| 8 | validacion | 2 | Existe evidencia independiente accesible para contrastar el modelo: datos publicados del NIST y despliegues reales documentados que sirven como caso nuevo. Hay una duda menor, porque el puesto concreto carece de datos públicos, pero la validación externa es posible. | — |
| 9 | nivel | 2 | Para el nivel U, el contexto es comprensible y significativo. La matemática requerida (probabilidad, razonamiento bayesiano, análisis de escenarios) corresponde a las herramientas esperables en MAR03. | — |
| 10 | autodiferenciacion | 2 | El piso es razonable: basta estimar falsas alertas multiplicando el flujo por una tasa de error. El techo es alto: admite modelos 1:N dependientes del tamaño de la base, umbrales, sensibilidad y sesgos por grupo. | — |
| 11 | fecundidad | 2 | Las decisiones y los resultados abren preguntas nuevas, por ejemplo sobre umbrales, sesgos demográficos, tamaño de la base y costos de los errores. También permiten comparar recomendaciones entre grupos. | — |
| 12 | recursos | 2 | La información necesaria se solicita o se obtiene con búsquedas al alcance del nivel U, como los informes públicos del NIST. Ningún material revela el modelo de solución. | — |
| | **Total** | **24/24** | | |
