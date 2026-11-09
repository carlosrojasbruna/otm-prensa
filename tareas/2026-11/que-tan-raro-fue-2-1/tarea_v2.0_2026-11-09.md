# ¿Qué tan sorprendente fue un 2-1?

Tarea `2026-11-que-tan-raro-fue-2-1-v2` · versión 2 · 2026-11-09 · nivel S · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-11-que-tan-raro-fue-2-1-v2
titulo: ¿Qué tan sorprendente fue un 2-1?
estado: verificada
version: 2
fecha: '2026-11-09'
noticia:
  noticia_id: 2026-11-09-latercera-la-tabla-tras-el-titulo-de
  medio: La Tercera
  titulo: 'La tabla tras el título de Colo Colo: revisa cómo queda la lucha por el Chile 2 y por la permanencia tras la Fecha 27'
  fecha: '2026-11-09'
  url: https://www.latercera.com/el-deportivo/noticia/la-tabla-tras-el-titulo-de-colo-colo-revisa-como-queda-la-lucha-por-el-chile-2-y-por-la-permanencia-tras-la-fecha-27/
  resumen_propio: Repaso de la jornada 27 del fútbol chileno, con los marcadores de todos los partidos y la tabla de posiciones actualizada tras el título de Colo Colo. Describe cómo quedan las pugnas por el segundo puesto, que da acceso a la Chile 2, y por evitar el descenso, con equipos que se acercan en puntos.
  cifras_usadas:
  - valor: 27
    unidad: partidos jugados
    que_es: Partidos disputados por cada equipo en la tabla tras la fecha 27
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: '+29'
    unidad: diferencia de goles
    que_es: Diferencia de goles de Colo Colo, la mejor de la tabla
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: 2-1
    unidad: goles (marcador)
    que_es: Resultado del partido entre Universidad de Chile y Cobresal
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: 1
    unidad: goles
    que_es: goles de Cobresal en la derrota 2-1 ante Universidad de Chile (segundo número del marcador)
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
nivel_principal: S
sub_tramo: S2
variantes:
  abajo: S
  arriba: U
area: deporte
contenidos_matematicos:
- probabilidad
- modelos de conteo (distribución de goles)
- estadística descriptiva
- sensibilidad de supuestos
tiempo_estimado: 2 sesiones de 90 min
rubrica_rub01:
  total: 23
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
    recursos: 1
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
En la fecha 27 del fútbol chileno, Universidad de Chile venció a Cobresal por 2-1. La misma tabla muestra que Colo Colo, ya campeón, ha disputado 27 partidos con una diferencia de goles de +29, la mejor del torneo. Un programa deportivo de radio quiere decir en el aire si un resultado como el 2-1 es algo común o raro en esta liga, y qué marcadores debería esperar un hincha antes de un partido entre equipos parejos. Ayúdenlo: ¿qué tan probable era un 2-1 en ese partido, comparado con otros marcadores, y qué tan seguido esperarían partidos decididos por un solo gol? Expliquen con qué datos y supuestos llegaron a su respuesta. Pueden pedir información adicional.
```

```text foto_descripcion
Ícono de un micrófono de radio frente a un marcador electrónico de fútbol con casillas vacías.
```

### 1.1 Variante hacia abajo (tramo S1)

En lugar de una distribución de goles, se pide estimar frecuencias con un árbol o tabla de doble entrada de goles de cada equipo (cero, uno, dos o más) con probabilidades asignadas por el grupo, y comparar el 2-1 con 1-1 y 1-0. Sin sensibilidad.

### 1.2 Variante hacia arriba (tramo U)

Se pide ajustar el modelo de goles con ventaja de local y fuerzas distintas, usar la diferencia de goles de Colo Colo para calibrar un equipo dominante, hacer sensibilidad formal al promedio de goles y juzgar si la independencia entre equipos es razonable; se comparan al menos dos modelos.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Datos de partida (también escritos en el enunciado) | Universidad de Chile 2-1 Cobresal en la fecha 27. Colo Colo: 27 partidos jugados y diferencia de goles de +29, la mejor de la tabla. | de_entrada | P1-MRS | noticia, párrafo 13 |
| R2 | Tarjeta de simplificación sobre los equipos del partido | Supuesto del escenario: para este análisis se puede tratar a Universidad de Chile y a Cobresal como equipos de fuerza parecida, sin ventaja especial de local, y los goles de cada equipo como independientes entre sí. | a_solicitud | P2-RM | supuesto del escenario |
| R3 | Marcadores de los demás partidos de la fecha, para contrastar el modelo | Resultados de los otros partidos de la fecha 27 tal como figuran en la noticia. Se entrega solo cuando el grupo ya tiene sus probabilidades calculadas. | a_solicitud | P6-VAL | noticia, párrafo 13 |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender qué significa 'raro' o 'común' para un marcador y qué datos entrega la noticia (un marcador, una diferencia de goles). | El grupo explica con sus palabras qué probabilidad quiere calcular y para qué audiencia. | B12 |
| P2-RM Simplificar | Estimar cuántos goles anota un equipo típico por partido, decidir si los equipos son parejos y si los goles son independientes. | Lista de supuestos y valor estimado del promedio de goles con justificación; pedido de la tarjeta de supuestos. | B23 |
| P3-MM Matematizar | Elegir cómo representar los goles de cada equipo: distribución de conteo (por ejemplo Poisson) o tabla de probabilidades asignadas por el grupo. | Fórmula o tabla de probabilidades por cantidad de goles de cada equipo. | B34 |
| P4-WM Trabajar | Combinar las probabilidades de ambos equipos para obtener la del marcador 2-1 y la de partidos con un gol de diferencia. | Cálculos de probabilidad de varios marcadores y de la suma de los casos con diferencia de un gol. | B45 |
| P5-INT Interpretar | Traducir probabilidades a frases para la radio ('de cada cien partidos...') y decidir si el 2-1 es común o raro. | Frase final con la comparación entre 2-1, 1-1, 1-0 y otros marcadores. | B56 |
| P6-VAL Validar | Contrastar con los marcadores de los demás partidos de la fecha y revisar el promedio de goles supuesto (sensibilidad). | Pedido de marcadores de la fecha; tabla comparando frecuencia observada y esperada; ajuste del promedio. | B56 |
| P7-EXP Exponer | Presentar el resultado al locutor con límites: pocos partidos, equipos no idénticos. | Texto o guion breve con respuesta, supuestos y advertencias. | B67 |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- Promedio de goles por equipo y por partido estimado por el grupo (por ejemplo entre uno y uno coma cinco).
- Los goles de ambos equipos son independientes.
- Los equipos del partido tienen fuerza parecida y no hay ventaja de local.
- Los goles de cada equipo siguen una distribución de conteo del tipo Poisson o una tabla equivalente.

### Solución de referencia

1) Estimar el promedio de goles por equipo, por ejemplo 1,3. 2) Con Poisson: P(0) = 0,273; P(1) = 0,354; P(2) = 0,230; P(3) = 0,100; P(4) = 0,032. 3) P(2-1 exacto, con orden fijado) = P(2)·P(1) = 0,230 · 0,354, cerca de 0,082. 4) Comparar: 1-1 cerca de 0,125, 1-0 cerca de 0,097, 0-0 cerca de 0,074. 5) P(diferencia exacta de un gol) = 2·Σ P(k)·P(k+1), cerca de 0,41. 6) Sensibilidad: con promedio 1,1 y con 1,5 los resultados cambian poco. 7) Contrastar con los marcadores de la fecha. 8) Usar la diferencia de goles de +29 en 27 partidos (cerca de 1,07 por partido) como referencia de un equipo dominante, que desplaza las probabilidades hacia márgenes mayores.

**Resultado.** Con promedio de 1,3 goles por equipo, un 2-1 exacto tenía cerca de 8 % de probabilidad y partidos con un gol de diferencia cerca de 41 %: 2-1 es un resultado habitual, aunque 1-1 es más probable.

**Rango aceptable.** Probabilidad del marcador 2-1 exacto entre 7 % y 9 % para promedios de goles entre 1,1 y 1,5; partidos con diferencia exacta de un gol entre 38 % y 43 %. Otros valores son aceptables si el supuesto del promedio está justificado y los cálculos son coherentes.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Tabla de probabilidades asignadas | S1 | Probabilidades por cantidad de goles (cero, uno, dos, tres o más) elegidas por el grupo y producto para cada marcador | Probabilidad de 2-1 entre 6 % y 10 % según el reparto elegido; comparación con 1-1 y 1-0 |
| R2 | Goles independientes con distribución Poisson | S2 | Probabilidad de k goles con promedio estimado; marcador como producto de dos probabilidades | 2-1 cerca de 8 % y diferencia de un gol cerca de 41 % con promedio de 1,3 |
| R3 | Modelo por diferencia de goles | S2 | Distribución de la diferencia de goles centrada en cero para equipos parejos y desplazada hacia cerca de 1,07 para un equipo dominante, usando la cifra de Colo Colo como referencia | Un gol de diferencia es el margen más frecuente entre equipos parejos; para un equipo dominante los márgenes de dos o más goles son más probables |
| R4 | Simulación con ventaja de local | U | Simulación de muchos partidos con promedios distintos para local y visita y comparación con la frecuencia de marcadores de la fecha | Frecuencia de 2-1 sensible al promedio de goles y a la ventaja de local; intervalos de variación de varios puntos porcentuales |

### Modelo inadecuado (R5)

Suponer que todos los marcadores posibles hasta un máximo de goles son equiprobables hace que 2-1 y 7-6 parezcan igual de probables; ignora que los goles altos son raros y que 0-0, 1-0 y 1-1 son más frecuentes.

### Evidencia de validación (independiente del modelo)

Marcadores de los demás partidos de la fecha 27 en la noticia (párrafo 8), no usados para construir el modelo: se compara la frecuencia observada de empates, partidos de un gol de diferencia y marcadores altos con la esperada, y se ve si el promedio de goles supuesto es razonable.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | La situación plantea una necesidad real: el programa quiere informar a la audiencia. El enunciado no entrega ninguna regla, distribución ni modelo para calcular la probabilidad de un marcador. | — |
| 2 | abierta | 2 | La pregunta no prescribe el método. Admite varios caminos defendibles: frecuencias empíricas de la liga, productos de distribuciones de goles por equipo o simulación. | — |
| 3 | decisiones | 2 | Resolver la tarea exige varias decisiones de modelación. Hay que decidir qué hacer con el dato de Colo Colo, que no informa el total de goles, obtener el promedio de goles de la liga y suponer cómo se distribuyen los goles de cada equipo. | — |
| 4 | realismo | 2 | Que un programa deportivo comente qué tan raro es un marcador es una situación plausible fuera de la escuela. Los partidos y la tabla de posiciones son reales. | — |
| 5 | autenticidad | 2 | La tarea usa como núcleo resultados y datos reales de la liga tomados de una noticia: el 2-1 que motiva la pregunta y los marcadores para contrastar. Estos datos no fueron creados para enseñar el contenido. | — |
| 6 | contexto | 2 | El contexto condiciona decisiones de modelación: fuerza de los equipos, localía y nivel goleador de la liga. También es necesario para interpretar el resultado y validarlo con los marcadores reales de la fecha. | — |
| 7 | ciclo | 2 | Responder obliga a recorrer todo el ciclo: comprender la situación, simplificar, construir un modelo probabilístico, calcular, interpretar y contrastar con otros marcadores. El enunciado no deja hecha ninguna fase. Hay una duda: la tarjeta R2 entrega los supuestos si se solicita; eso se descuenta en el criterio de recursos. | — |
| 8 | validacion | 2 | El modelo puede contrastarse con evidencia independiente que no se usó para construirlo: los marcadores de los demás partidos de la fecha. También pueden usarse datos públicos de la temporada. | — |
| 9 | nivel | 2 | El fútbol chileno y el lenguaje son comprensibles y significativos para S2. La tarea puede resolverse con estadística descriptiva y probabilidad elemental de eventos independientes, al alcance del nivel. | — |
| 10 | autodiferenciacion | 2 | Tiene un piso razonable: contar frecuencias de marcadores en la liga. Tiene techo alto: distribuciones de goles por equipo, ventaja de local o sensibilidad al promedio de goles. | — |
| 11 | fecundidad | 2 | Los distintos supuestos y modelos permiten comparar soluciones y discutir límites, como la independencia de los goles o los equipos dispares. También abren nuevas preguntas sobre otros marcadores y otros partidos. | — |
| 12 | recursos | 1 | La tarjeta R2 entrega ya formulados los supuestos clave del modelo (fuerza pareja, sin localía, independencia), lo que es una sobreorientación parcial hacia la estructura de la solución. Además, el dato imprescindible de goles promedio de la liga no figura entre los recursos declarados. | — |
| | **Total** | **23/24** | | |
