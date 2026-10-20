# ¿Ida y vuelta en un día al mar abierto?

Tarea `2026-10-viaje-barco-ida-vuelta-v2` · versión 2 · 2026-10-20 · nivel P · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-10-viaje-barco-ida-vuelta-v2
titulo: ¿Ida y vuelta en un día al mar abierto?
estado: verificada
version: 2
fecha: '2026-10-20'
noticia:
  noticia_id: 2026-10-20-bbc-uk-government-to-make-jackdaw-gas
  medio: BBC News
  titulo: UK government to make Jackdaw gas field announcement
  fecha: '2026-10-20'
  url: https://www.bbc.co.uk/news/articles/cvze4wx3elj1o?at_medium=RSS&at_campaign=rss
  resumen_propio: The UK government is expected to decide soon whether to approve the Jackdaw gas field in the North Sea, a choice delayed for months. Jackdaw lies a considerable distance east of Aberdeen and could feed the national grid within months, while the Rosebank oil site off Shetland is expected to wait longer. Environmental groups and industry bodies disagree about the climate and energy-security effects, and a court earlier ruled previous approvals unlawful.
  cifras_usadas:
  - valor: 241.4km
    unidad: kilómetros
    que_es: distancia de Jackdaw al este de Aberdeen (equivalente en km)
    localizador:
      fuente: noticia
      ubicacion: párrafo 57
  - valor: 128.7km
    unidad: kilómetros
    que_es: distancia de Rosebank al noroeste de Shetland (equivalente en km)
    localizador:
      fuente: noticia
      ubicacion: párrafo 58
nivel_principal: P
variantes:
  abajo: null
  arriba: S
area: medio_ambiente
contenidos_matematicos:
- rapidez, distancia y tiempo
- proporcionalidad directa
- estimación
- unidades de tiempo
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
En el mar del Norte hay yacimientos de gas y petróleo muy lejos de la costa, y el gobierno del Reino Unido discute si aprobar algunos. Jackdaw, un yacimiento de gas, queda a 241,4 km al este de Aberdeen. Rosebank, un yacimiento de petróleo, queda a 128,7 km al noroeste de las islas Shetland. Una empresa que lleva repuestos y alimentos a instalaciones en alta mar debe decidir si un barco de apoyo puede salir de la costa, llegar a cada lugar, descargar y volver en una misma jornada, o si la tripulación tendría que pasar la noche en el mar. ¿Qué le recomendarían a la empresa para cada yacimiento? Pueden pedir información adicional.
```

```text foto_descripcion
Dibujo sencillo de un barco de apoyo navegando entre la costa y una plataforma en alta mar.
```

### 1.1 Variante hacia abajo

No hay.

### 1.2 Variante hacia arriba (tramo S2)

Mismo contexto. Se pide además determinar a partir de qué rapidez cambia la recomendación para cada yacimiento, cómo cambia si el mar está agitado o si el tiempo de descarga se alarga, y comparar un barco con otro medio de transporte más rápido, con análisis de sensibilidad informal.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Datos de partida: distancias en kilómetros de los dos yacimientos | Jackdaw: 241,4 km al este de Aberdeen. Rosebank: 128,7 km al noroeste de las islas Shetland. | de_entrada | P1-MRS | noticia, párrafo 57 y párrafo 58 |
| R2 | Tarjeta sobre cómo se mueve un barco de apoyo | Supuesto del escenario: un barco de apoyo avanza más despacio que un auto en carretera, más o menos al ritmo de una bicicleta que va a buen paso. Si el mar está agitado, avanza todavía más lento. Al llegar a la plataforma necesita un rato para descargar antes de volver. | a_solicitud | P2-RM | supuesto del escenario |
| R3 | Tarjeta sobre la jornada de la tripulación | Supuesto del escenario: la tripulación trabaja por turnos y necesita descanso. Una jornada en el mar no puede ocupar todas las horas del día. | a_solicitud | P2-RM | supuesto del escenario |
| R4 | Tarjeta de calibración con un viaje conocido | Supuesto del escenario: el grupo puede elegir un viaje que conozca, en bus o auto, con su distancia aproximada y lo que demoró, y comparar con lo que su modelo diría para ese mismo viaje. | a_solicitud | P6-VAL | supuesto del escenario |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender qué significa ir y volver en una jornada y qué parte del viaje cuenta: ida, descarga y vuelta. | Explican con sus palabras qué debe decidir la empresa y qué tiempos intervienen. | B12 |
| P2-RM Simplificar | Suponer una rapidez razonable para el barco, un tiempo para descargar y la cantidad de horas de una jornada, y decidir si los cuentan con o sin descanso. | Lista escrita de supuestos con valores elegidos y su justificación a partir de las tarjetas. | B23 |
| P3-MM Matematizar | Relacionar distancia, rapidez y tiempo: el tiempo de un tramo sale de dividir la distancia por la rapidez, y el viaje completo incluye ida y vuelta más la descarga. | Esquema o expresión escrita del tiempo total para cada yacimiento. | B34 |
| P4-WM Trabajar | Calcular los tiempos para cada yacimiento, quizá con una tabla para varias rapideces. | Tabla o cálculos con tiempos de ida, de vuelta y total, con decimales escritos con coma. | B45 |
| P5-INT Interpretar | Traducir los tiempos a una recomendación: ir y volver el mismo día o pasar la noche, para cada yacimiento. | Frase de recomendación para la empresa que cita los tiempos calculados. | B56 |
| P6-VAL Validar | Probar la rapidez supuesta con un viaje conocido en bus o auto, y revisar cuánto cambia la recomendación si el barco es más lento por mar agitado. | Comparación escrita entre el tiempo que da su modelo para un viaje conocido y el tiempo real, y una nota con lo que cambia si baja la rapidez. | B56 |
| P7-EXP Exponer | Presentar la recomendación diciendo qué supuestos la sostienen y en qué caso cambiaría. | Informe breve o exposición con la tabla, la recomendación y los supuestos. | — |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- Rapidez media del barco de apoyo, por ejemplo entre veinte y treinta kilómetros por hora, elegida y justificada por el grupo (por ejemplo, comparándola con una bicicleta rápida o con un viaje conocido).
- Tiempo de descarga en destino, de pocas horas.
- Largo de la jornada máxima que se permite al barco en el mar.
- El barco va en línea recta, sale y regresa a la costa mencionada en la noticia y mantiene la misma rapidez.

### Solución de referencia

1) Fijar supuestos: rapidez v, tiempo de descarga c y largo de jornada H. 2) Tiempo de ida = distancia ÷ v. 3) Tiempo total = 2 × distancia ÷ v + c. 4) Calcular para 241,4 km y 128,7 km, con una o varias rapideces. 5) Comparar con H y recomendar. 6) Verificar la rapidez usada con un viaje conocido.

**Resultado.** Con una rapidez de veinticinco kilómetros por hora y dos horas de descarga: Jackdaw requiere cerca de 21 h en total y Rosebank cerca de 12 h. Rosebank cabe en una jornada larga, mientras que Jackdaw ocupa casi todo el día y conviene planificar pasar la noche en el mar, o usar un medio más rápido.

**Rango aceptable.** Para rapidez entre 20 y 30 km/h, el viaje de ida y vuelta (sin descarga) dura entre 16 y 24 h para Jackdaw y entre 9 y 13 h para Rosebank. Se acepta cualquier recomendación coherente con los supuestos declarados. En todos los casos, el viaje a Jackdaw demora casi el doble que el de Rosebank, porque 241,4 ÷ 128,7 ≈ 1,9.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Tabla de rapidez por horas | P | Proporcionalidad directa: cuánto avanza el barco en una hora, en dos, y así hasta llegar a la distancia. | Jackdaw: unas 10 h de ida con 25 km/h; Rosebank: unas 5 h de ida. |
| R2 | Comparar entre sí los dos viajes | P | Razón entre distancias: si el tiempo es proporcional a la distancia, Jackdaw toma casi el doble que Rosebank, sin necesidad de fijar la rapidez. | Si Rosebank llena la mitad de la jornada, Jackdaw la llena completa; la razón es cerca de 1,9. |
| R3 | Distancia máxima alcanzable | S1 | Función lineal del tiempo total t = 2d/v + c, o distancia máxima d = v·(H − c)/2, comparada con las dos distancias. | Con v = 25 km/h, c = 2 h y H = 14 h, la distancia máxima es 150 km: Rosebank sí cabe y Jackdaw no. |

### Modelo inadecuado (RX: contar solo el viaje de ida (241,4 ÷ v y 128,7 ÷ v) y compararlo con la jornada.)

El barco tiene que volver a la costa y además descargar; si solo se cuenta la ida, el tiempo se subestima casi a la mitad y se recomienda hacer viajes que en realidad no caben en el día.

### Evidencia de validación (independiente del modelo)

Dato independiente que no se usa para construir el modelo: el tiempo real de un viaje conocido (por ejemplo un trayecto en bus o auto de la propia ciudad, o de un transbordador de línea), que el grupo compara con lo que predice su relación distancia, rapidez y tiempo, ajustando la rapidez supuesta. Como contraste posterior, el profesor puede entregar el tiempo de un trayecto real en barco con distancia y duración conocidas.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | La tarea plantea una necesidad real de decisión logística y no entrega velocidades, tiempos ni una fórmula. Describir las etapas del viaje forma parte de la situación y no insinúa el procedimiento de cálculo. | — |
| 2 | abierta | 2 | La pregunta pide una recomendación sin prescribir el método. Admite distintos modelos defendibles según la velocidad, el tiempo de descarga y la duración de la jornada que se supongan. | — |
| 3 | decisiones | 2 | Para resolver hay que estimar la velocidad, el tiempo de descarga, la duración aceptable de la jornada y el efecto del mar agitado. Además se puede solicitar información, de modo que los supuestos son sustantivos. | — |
| 4 | realismo | 2 | Los yacimientos y la logística de barcos de apoyo a instalaciones en alta mar existen fuera de la escuela, y la pregunta de la empresa es plausible. | — |
| 5 | autenticidad | 2 | El tema (el debate sobre Jackdaw y Rosebank) y las distancias son componentes extraescolares reales y constituyen el núcleo de la tarea. No fueron fabricados para enseñar el contenido. | — |
| 6 | contexto | 2 | El contexto condiciona los supuestos: estado del mar, descarga y descanso de la tripulación. También es necesario para interpretar el resultado como recomendación de jornada única o de pernoctar en el mar. | — |
| 7 | ciclo | 2 | Responder obliga a recorrer las fases: comprender la situación, suponer velocidades y tiempos, plantear la relación entre distancia y tiempo, calcular, interpretar el resultado como recomendación y contrastarlo con la jornada y con un viaje conocido. Ninguna fase queda hecha por el enunciado. | — |
| 8 | validacion | 2 | El modelo puede contrastarse con un caso no usado en su construcción, un viaje conocido. También es accesible la velocidad real de los barcos de apoyo como evidencia independiente. | — |
| 9 | nivel | 2 | El contexto y el lenguaje son comprensibles para estudiantes de 10 a 12 años. La matemática requerida (proporcionalidad, operatoria con kilómetros y horas, estimación) corresponde a las herramientas esperables del nivel P. | — |
| 10 | autodiferenciacion | 2 | Hay un piso accesible: un cálculo aproximado con la velocidad de una bicicleta. La tarea también admite soluciones más refinadas: escenarios de mar agitado, márgenes de descarga y descanso, o la velocidad mínima necesaria. | — |
| 11 | fecundidad | 2 | Las recomendaciones dependen de los supuestos, lo que permite comparar soluciones entre grupos. Además abre preguntas sobre la distancia límite para una jornada o sobre el efecto del clima. | — |
| 12 | recursos | 2 | Las distancias se entregan, y la velocidad, la descarga y la jornada pueden estimarse con conocimiento cotidiano a partir de tarjetas cualitativas a solicitud. Ninguna tarjeta revela la regla de cálculo. | — |
| | **Total** | **24/24** | | |
