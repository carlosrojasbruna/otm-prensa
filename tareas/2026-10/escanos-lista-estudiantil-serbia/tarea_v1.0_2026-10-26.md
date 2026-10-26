# ¿Cuántos escaños tendría la lista estudiantil?

Tarea `2026-10-escanos-lista-estudiantil-serbia` · versión 1 · 2026-10-26 · nivel S · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-10-escanos-lista-estudiantil-serbia
titulo: ¿Cuántos escaños tendría la lista estudiantil?
estado: verificada
version: 1
fecha: '2026-10-26'
noticia:
  noticia_id: 2026-10-26-bbc-celebrations-in-serbia-after-veteran-ruler
  medio: BBC News
  titulo: Celebrations in Serbia after veteran ruler Vučić loses election to student-led protest movement
  fecha: '2026-10-26'
  url: https://www.bbc.co.uk/news/articles/cw5yn3xlprpmo?at_medium=RSS&at_campaign=rss
  resumen_propio: Serbia's long-serving leader conceded snap parliamentary elections to a movement that grew out of student protests after a deadly canopy collapse at a railway station. Preliminary counts gave the students a clear lead over his governing party, and celebrations spread through major cities. The movement, which fielded candidates from doctors to athletes, now faces forming a government, while a presidential vote is scheduled for December.
  cifras_usadas:
  - valor: 97%
    unidad: porcentaje de mesas escrutadas
    que_es: Proporción de casillas contadas cuando la comisión electoral informó los votos de los estudiantes y del partido de gobierno.
    localizador:
      fuente: noticia
      ubicacion: párrafo 54
  - valor: 2.25 million
    unidad: votos
    que_es: Votos obtenidos por la lista de los estudiantes según la comisión electoral.
    localizador:
      fuente: noticia
      ubicacion: párrafo 54
  - valor: 1.67 million
    unidad: votos
    que_es: Votos obtenidos por el antiguo partido gobernante según la comisión electoral.
    localizador:
      fuente: noticia
      ubicacion: párrafo 54
  - valor: 52.7%
    unidad: porcentaje de votos
    que_es: Porcentaje de votos de la lista de los estudiantes según cifras preliminares del movimiento.
    localizador:
      fuente: noticia
      ubicacion: párrafo 55
  - valor: 39.2%
    unidad: porcentaje de votos
    que_es: Porcentaje de votos del Partido Progresista Serbio (SNS) según cifras preliminares.
    localizador:
      fuente: noticia
      ubicacion: párrafo 55
  - valor: 250
    unidad: escaños del parlamento
    que_es: Tamaño del parlamento al que aspiraban los candidatos del movimiento estudiantil.
    localizador:
      fuente: noticia
      ubicacion: párrafo 71
nivel_principal: S
variantes:
  abajo: P
  arriba: U
area: sociedad_datos
contenidos_matematicos:
- proporcionalidad y porcentajes
- estimación y proyección
- comparación de escenarios
- reparto proporcional de escaños
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
En Serbia hubo elecciones parlamentarias anticipadas, y la lista de un movimiento nacido de protestas estudiantiles enfrentó al partido que gobernaba desde hacía años. Cuando la comisión electoral había contado el 97 % de las mesas, informó 2,25 millones de votos para la lista de los estudiantes y 1,67 millones para el antiguo partido de gobierno. El parlamento tiene 250 escaños. Ustedes son parte del equipo de datos de un medio que quiere publicar esa misma noche cuántos escaños tendría cada bando y si la lista estudiantil podría formar gobierno sin aliados. ¿Qué estimación publicarían y con qué grado de seguridad? Pueden pedir información adicional.
```

```text foto_descripcion
Ícono sencillo de un hemiciclo de parlamento con filas de asientos, sin números ni colores asignados.
```

### 1.1 Variante hacia abajo (tramo P)

Se informa de entrada que solo compiten las dos listas y que cada escaño corresponde a una parte igual de los votos. La pregunta pasa a ser cuántos escaños aproximados tendría cada lista y cuál de las dos tendría más. Se omiten umbral y mesas pendientes.

### 1.2 Variante hacia arriba (tramo U)

Se quitan los porcentajes preliminares y se pide modelar el reparto de escaños con un método explícito entre varias listas, con incertidumbre en las mesas pendientes, simulando escenarios, analizando la sensibilidad a los supuestos y criticando el modelo.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Datos del conteo parcial entregados al grupo al comenzar | Con el 97 % de las mesas escrutadas, la lista de los estudiantes tenía 2,25 millones de votos y el antiguo partido de gobierno 1,67 millones. El parlamento tiene 250 escaños. | de_entrada | P1-MRS | noticia, párrafo 54; noticia, párrafo 71 |
| R2 | Porcentajes preliminares de votos de las dos fuerzas principales | Según cifras preliminares, la lista de los estudiantes tiene 52,7 % de los votos y el Partido Progresista Serbio (SNS) tiene 39,2 %. | a_solicitud | P3-MM | noticia, párrafo 55 |
| R3 | Condición del sistema de reparto sobre listas pequeñas | Supuesto del escenario: para recibir escaños, una lista debe superar un porcentaje mínimo de los votos válidos; las listas que no lo superan quedan fuera del reparto. El porcentaje exacto es parte de lo que el equipo debe averiguar o suponer. | a_solicitud | P2-RM | supuesto del escenario |
| R4 | Información sobre las mesas que faltan por contar | Supuesto del escenario: la comisión no ha informado en qué zonas están las mesas que faltan ni cuántos votantes tiene cada una. | a_solicitud | P2-RM | supuesto del escenario |
| R5 | Resultado oficial final para contrastar la estimación | Cuando el grupo entregue su estimación, se le muestra el reparto final oficial de escaños publicado por la comisión electoral. | a_solicitud | P6-VAL | otra fuente: Comisión Electoral Republicana de Serbia, resultados oficiales |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender qué significa que el 97 % de las mesas estén escrutadas y distinguir votos de escaños y mayoría; decidir qué datos faltan y pedirlos. | El grupo reformula con sus palabras qué se estima y pide datos sobre otras listas, mesas pendientes y reglas de reparto. | B12 |
| P2-RM Simplificar | Decidir qué simplificar: reparto proporcional, mesas pendientes parecidas a las contadas, qué hacer con las listas pequeñas. | Lista escrita de supuestos del grupo con su justificación. | B23 |
| P3-MM Matematizar | Expresar los escaños de una lista como su proporción de los votos que cuentan para el reparto multiplicada por el total de escaños. | Expresión o esquema que relaciona votos, porcentaje y escaños. | B34 |
| P4-WM Trabajar | Obtener el total de votos a partir de un votos y su porcentaje, proyectar el conteo final y calcular escaños en cada escenario. | Tabla de cálculos con al menos dos escenarios y los escaños obtenidos. | B45 |
| P5-INT Interpretar | Traducir los resultados a un rango de escaños y compararlo con la mayoría necesaria para gobernar solos. | Frase que da el rango y responde si la lista podría gobernar sin aliados. | B56 |
| P6-VAL Validar | Contrastar la estimación con el reparto final oficial y revisar la coherencia entre votos y porcentajes informados. | Comparación escrita entre la estimación y el dato oficial, con ajuste de supuestos. | B67 |
| P7-EXP Exponer | Redactar el aviso para el medio con el rango, el grado de seguridad y los supuestos clave. | Texto breve o cartel con la estimación, los supuestos y su incertidumbre. | — |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- Los escaños se reparten de forma proporcional a los votos de las listas que pasan el umbral.
- Las mesas que faltan por contar se parecen a las ya contadas.
- Se debe suponer o averiguar un porcentaje mínimo para obtener escaños.
- Gobernar sin aliados significa tener más de la mitad de los escaños.
- Los votos nulos o en blanco no entran en el reparto.

### Solución de referencia

1) Con 2,25 millones de votos y 52,7 %, el total de votos contados es cerca de 4,27 millones (coherente con 1,67 millones y 39,2 %). Quedan fuera de las dos listas cerca de 8,1 % de los votos. 2) Mayoría propia: más de la mitad de 250, es decir, al menos 126 escaños. 3) Escenario base sin umbral: 52,7 % de 250, cerca de 132 escaños. 4) Escenario con umbral: si la mitad de ese 8,1 % corresponde a listas bajo el umbral, la lista estudiantil tiene cerca de 54,9 % de los votos que cuentan, o sea cerca de 137 escaños. Si todo el resto queda bajo el umbral, 2,25 de 3,92 es cerca de 57,4 %, o sea cerca de 143 escaños. 5) Sensibilidad al 3 % de mesas pendientes: el total final sería cerca de 4,40 millones; en el caso extremo en que todo lo pendiente fuera de otras listas, la lista estudiantil tendría 2,25 de 4,40, cerca de 51,1 %, o sea cerca de 128 escaños. 6) Comunicar un rango y la conclusión de que lo más probable es una mayoría propia.

**Resultado.** Entre cerca de 132 y 143 escaños según el umbral y las listas pequeñas (estimación central cerca de 137), por encima de los 126 necesarios; incluso en el peor caso para las mesas pendientes serían cerca de 128.

**Rango aceptable.** Se aceptan estimaciones centrales entre 130 y 145 escaños con supuestos explícitos y una conclusión coherente sobre la mayoría; el resultado depende del umbral y de lo que se suponga sobre las mesas pendientes.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Escaños según porcentaje sobre todos los votos | S1 | Escaños = porcentaje preliminar de la lista × 250 escaños; incógnita lineal con regla de tres. | Cerca de 132 escaños, más que los 126 de la mayoría. |
| R2 | Reparto entre las dos listas principales | S1 | Proporción de votos de la lista estudiantil entre las dos listas: 2,25 / (2,25 + 1,67) por 250 escaños; tratada como cota superior. | Cerca de 57,4 %, o sea cerca de 143 escaños. |
| R3 | Escenarios con umbral y mesas pendientes | S2 | Se proyecta el total de votos con el 97 % y se calcula la proporción de la lista sobre los votos que cuentan, probando varios escenarios de listas bajo el umbral y de mesas pendientes. | Rango de 128 a 143 escaños con central cerca de 137. |
| R4 | Reparto con método de cifra mayor y simulación | U | Reparto por cifra mayor (D'Hondt) con varias listas pequeñas simuladas y mesas pendientes aleatorias; análisis de sensibilidad. | Distribución de escaños con rango similar y probabilidad alta de superar 126. |

### Modelo inadecuado (R5)

Suponer que la lista con más votos se lleva todos los escaños, o que el escaño es la diferencia de votos entre listas, ignora que el reparto es proporcional; así la estimación sería 250 o un número sin sentido en vez de cerca de 132 a 143.

### Evidencia de validación (independiente del modelo)

Reparto final oficial de escaños publicado por la comisión electoral, que no se usa para construir el modelo; además se puede revisar la coherencia entre los votos informados y los porcentajes preliminares.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | La tarea plantea una necesidad real: publicar una estimación esa misma noche. No entrega ninguna regla de reparto ni modelo para convertir votos en escaños. | — |
| 2 | abierta | 2 | La pregunta no prescribe procedimiento. Admite varios modelos defendibles: proporción simple, reparto con umbral, método de cocientes o escenarios para las mesas restantes. Tampoco hay instrucciones posteriores que encaucen la ruta. | — |
| 3 | decisiones | 2 | Resolver exige varias decisiones de modelación: suponer el umbral y el método de reparto, decidir cómo tratar el 8 % restante de votos y las mesas sin contar, y estimar la incertidumbre. | — |
| 4 | realismo | 2 | Proyectar escaños a partir de un conteo parcial es una práctica real de los equipos de datos de los medios en noches electorales. | — |
| 5 | autenticidad | 2 | El tema y las cifras del conteo parcial provienen de un hecho noticioso informado por la comisión electoral, y son el núcleo de la tarea. Según la regla, se toma como cierta la procedencia declarada. | — |
| 6 | contexto | 2 | El contexto condiciona decisiones clave: el umbral, la mayoría de 126 escaños y las mesas faltantes. También es necesario para interpretar si hay gobierno sin aliados y para juzgar el grado de seguridad. | — |
| 7 | ciclo | 2 | Responder obliga a recorrer todo el ciclo: comprender el sistema electoral, simplificar con supuestos, matematizar el reparto, calcular, interpretar respecto de la mayoría y juzgar la seguridad. Ninguna fase queda hecha en el enunciado. | — |
| 8 | validacion | 2 | Existe evidencia independiente, no usada en la construcción del modelo, para contrastar la estimación: el resultado oficial final (R5). | — |
| 9 | nivel | 2 | El contexto electoral y el lenguaje son comprensibles para S. La matemática requerida (porcentajes, razones, reparto proporcional, comparación de escenarios) está al alcance de las herramientas esperables del nivel. | — |
| 10 | autodiferenciacion | 2 | El piso es accesible: un reparto proporcional simple con los votos dados. El techo es alto, porque la tarea misma admite soluciones más refinadas: umbral, método de cocientes, escenarios para el 3 % restante y análisis de sensibilidad del margen respecto de la mayoría. | — |
| 11 | fecundidad | 2 | Los distintos supuestos producen proyecciones distintas, lo que permite comparar soluciones. La tarea abre preguntas sobre umbrales, métodos de reparto, la prima de escaños de los partidos grandes y los límites de proyectar con datos incompletos. | — |
| 12 | recursos | 2 | La información necesaria se entrega de entrada o a solicitud (R1–R4), sin revelar el método de reparto. El umbral y el sistema electoral pueden obtenerse con una búsqueda simple o suponerse, como indica R3. | — |
| | **Total** | **24/24** | | |
