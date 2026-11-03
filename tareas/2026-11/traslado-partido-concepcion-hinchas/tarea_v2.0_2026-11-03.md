# ¿Cuántos hinchas más habrían entrado si el partido se jugaba en Concepción?

Tarea `2026-11-traslado-partido-concepcion-hinchas-v2` · versión 2 · 2026-11-02 · nivel P · 2 sesiones de 45 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-11-traslado-partido-concepcion-hinchas-v2
titulo: ¿Cuántos hinchas más habrían entrado si el partido se jugaba en Concepción?
estado: verificada
version: 2
fecha: '2026-11-02'
noticia:
  noticia_id: 2026-11-02-latercera-la-estrella-35-a-la-vista
  medio: La Tercera
  titulo: 'La estrella 35 a la vista: la limitada fiesta que tendrá Colo Colo en Chillán en la visita a Ñublense'
  fecha: '2026-11-02'
  url: https://www.latercera.com/el-deportivo/noticia/la-estrella-35-a-la-vista-la-limitada-fiesta-que-tendra-colo-colo-en-chillan-en-la-visita-a-nublense/
  resumen_propio: Colo Colo, tras golear 6-1 a Universidad de Concepción, podría coronarse campeón con una victoria sobre Ñublense en Chillán. La Delegación Presidencial local redujo el aforo del estadio y se discute cómo repartir los sectores entre hinchas de ambos equipos. También se evaluó trasladar el partido a Concepción, pero esa solicitud no se tramitó a tiempo.
  cifras_usadas:
  - valor: 6-1
    unidad: resultado del partido
    que_es: marcador con que Colo Colo goleó a Universidad de Concepción
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 35ª
    unidad: corona
    que_es: título de liga que aseguraría Colo Colo con una victoria sobre Ñublense
    localizador:
      fuente: noticia
      ubicacion: párrafo 2
  - valor: 12 mil
    unidad: espectadores
    que_es: capacidad del estadio Nelson Oyarzún
    localizador:
      fuente: noticia
      ubicacion: párrafo 6
  - valor: 7.5
    unidad: fanáticos
    que_es: aforo autorizado por la Delegación Presidencial para el partido
    localizador:
      fuente: noticia
      ubicacion: párrafo 6
  - valor: 30 mil
    unidad: espectadores
    que_es: capacidad autorizada del estadio de Concepción
    localizador:
      fuente: noticia
      ubicacion: párrafo 11
  - valor: 1
    unidad: goles
    que_es: goles de Universidad de Concepción en la derrota 6-1 (segundo número del marcador)
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
nivel_principal: P
variantes:
  abajo: null
  arriba: S
area: deporte
contenidos_matematicos:
- proporcionalidad directa
- porcentajes simples
- comparación de cantidades
- estimación
tiempo_estimado: 2 sesiones de 45 min
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
Colo Colo, que goleó 6-1 a Universidad de Concepción, puede asegurar su 35ª corona con un triunfo en Chillán. Allí la autoridad permitió solo 7,5 mil fanáticos en un estadio con capacidad para 12 mil. Se habló de jugar el partido en Concepción, cuyo estadio tiene una capacidad autorizada de 30 mil espectadores, pero el trámite no se alcanzó a hacer a tiempo. Imaginen que lo hubieran pedido a tiempo. Ustedes son periodistas de un diario deportivo y deben explicar a los lectores si el traslado habría cambiado mucho la fiesta de los hinchas. ¿Cuántos hinchas más habrían podido ver el partido y qué otras cosas habría que considerar para decidir si convenía trasladarlo? Pueden pedir información adicional.
```

```text foto_descripcion
Dibujo sencillo de un mapa con dos estadios marcados con íconos de balón, uno al norte y otro al sur, unidos por una línea de ruta, sin distancias ni números.
```

### 1.1 Variante hacia abajo

No hay.

### 1.2 Variante hacia arriba (tramo S1)

Se pide además comparar dos formas de estimar el aforo en Concepción (misma cantidad que en Chillán, misma proporción de la capacidad) y expresar la cantidad de hinchas más en función del porcentaje de ocupación permitido; se agrega estimar cuántos buses harían falta para llevar a los hinchas de Chillán. Se mantiene el contexto.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Datos de capacidad y aforo de los dos estadios | Estadio de Chillán: capacidad 12 mil espectadores y aforo autorizado de 7,5 mil fanáticos. Estadio de Concepción: capacidad autorizada de 30 mil espectadores. | de_entrada | P1-MRS | noticia, párrafos 6 y 11 |
| R2 | Tarjeta sobre el aforo posible en Concepción | Supuesto del escenario: la autoridad de Concepción aún no ha informado cuánto público autorizaría para este partido; el grupo debe decidir cómo estimarlo. | a_solicitud | P2-RM | supuesto del escenario |
| R3 | Tarjeta sobre el viaje de los hinchas | Supuesto del escenario: viajar entre Chillán y Concepción en bus toma un rato largo, pero se puede hacer en el día. | a_solicitud | P2-RM | supuesto del escenario |
| R4 | Tarjeta sobre el transporte de hinchas | Supuesto del escenario: los buses que llevarían hinchas tienen una cantidad de asientos parecida a la de un bus interurbano común. | a_solicitud | P3-MM | supuesto del escenario |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender que se compara lo que se permitió en Chillán con lo que podría permitirse en Concepción, no solo las capacidades. | El grupo explica con sus palabras qué cantidades compara y por qué la capacidad no es lo mismo que el aforo autorizado. | B12 |
| P2-RM Simplificar | Elegir el criterio para estimar el público en Concepción (todo el estadio, misma fracción de ocupación u otro) y qué factores dejar de lado. | Lista de supuestos y de tarjetas pedidas. | B23 |
| P3-MM Matematizar | Escribir una relación proporcional o aditiva entre capacidad y público permitido. | Esquema o regla de tres escrita para pasar de Chillán a Concepción. | B34 |
| P4-WM Trabajar | Calcular el público posible en Concepción y la diferencia con Chillán. | Cálculos con porcentajes, multiplicaciones y restas. | B45 |
| P5-INT Interpretar | Decir qué significa la diferencia para los hinchas y si convenía trasladar el partido, considerando viaje y seguridad. | Frase de conclusión que incluye al menos un factor no matemático. | B56 |
| P6-VAL Validar | Contrastar la estimación con asistencias reales de otros partidos y revisar los supuestos. | Comparación entre su estimación y asistencias reales informadas en prensa, con ajuste razonado. | B67 |
| P7-EXP Exponer | Escribir la nota periodística con el resultado y sus límites. | Nota breve con las cantidades, los supuestos y la recomendación. | — |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- La cifra de aforo autorizado (idx 3, valor 7,5) se interpreta como 7,5 mil fanáticos, coherente con la capacidad de 12 mil.
- El grupo supone qué parte de la capacidad de Concepción se habría autorizado, por ejemplo la misma fracción que en Chillán o todo el estadio.
- Se supone que los hinchas llenarían las entradas permitidas.
- El grupo decide qué factores no matemáticos considerar, como viaje o seguridad.

### Solución de referencia

1) Distinguir capacidad y aforo en Chillán: 7.500 de 12.000 = 62,5%. 2) Elegir un criterio para Concepción: (a) mismo porcentaje: 62,5% x 30.000 = 18.750; (b) estadio completo: 30.000; (c) un porcentaje menor, por ejemplo la mitad: 15.000. 3) Diferencia con Chillán: 18.750 - 7.500 = 11.250 más; 30.000 - 7.500 = 22.500 más; 15.000 - 7.500 = 7.500 más. 4) Interpretar con factores como viaje, seguridad y que muchos hinchas viajarían desde Chillán. 5) Contrastar con asistencias reales.

**Resultado.** Con la misma fracción de ocupación (62,5%), unos 18.750 hinchas en Concepción, es decir 11.250 más que en Chillán, aproximadamente 2,5 veces el público.

**Rango aceptable.** Entre 7.500 y 22.500 hinchas más, según el aforo supuesto para Concepción; la respuesta debe ser coherente con el criterio elegido.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Misma fracción de ocupación | P | Proporción 7.500/12.000 = 62,5% aplicada a 30.000. | 18.750 hinchas; 11.250 más que en Chillán. |
| R2 | Razón entre capacidades | P | 30.000/12.000 = 2,5; el público permitido se multiplica por 2,5. | 7.500 x 2,5 = 18.750. |
| R3 | Estadio completo | P | Aforo igual a la capacidad de Concepción y resta con el aforo de Chillán. | 22.500 hinchas más. |
| R4 | Función del porcentaje de ocupación | S1 | Hinchas más = p x 30.000 - 7.500, con p variable. | Tabla o gráfico de la ganancia según p; la ganancia es cero cuando p vale 0,25. |

### Modelo inadecuado (RX)

Restar capacidades (30.000 - 12.000 = 18.000 más) ignora que en Chillán el público permitido era solo 7.500 y que en Concepción tampoco necesariamente se llenaría; compara capacidades en lugar de público realmente autorizado.

### Evidencia de validación (independiente del modelo)

Después de modelar, el grupo busca en prensa la asistencia informada de otros partidos de Colo Colo en estadios de distinto tamaño y compara, en cada caso, el porcentaje de ocupación real con el que usó en su modelo.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | La tarea plantea una necesidad real: informar si convenía el traslado. No entrega ninguna regla ni modelo; «cuántos más» es el sentido natural de la pregunta y no una pista de procedimiento, porque el aforo efectivo en Concepción queda por estimar. | — |
| 2 | abierta | 2 | La pregunta no prescribe el método. Admite varios caminos defendibles: estimar el aforo de distintas formas y ponderar distintos factores (viaje, buses). | — |
| 3 | decisiones | 2 | Resolver exige formular supuestos y estimar el aforo posible, por ejemplo con la proporción de Chillán. También exige decidir qué factores considerar y solicitar información. | — |
| 4 | realismo | 2 | Restringir el aforo y evaluar el cambio de sede de un partido decisivo son situaciones reales del fútbol chileno. El escenario contrafactual es claramente plausible. | — |
| 5 | autenticidad | 2 | La noticia deportiva y sus cifras de capacidad y aforo son el núcleo de la tarea. Constituyen un componente auténtico integrado de manera sustantiva. | — |
| 6 | contexto | 2 | Las restricciones de aforo de la autoridad condicionan cómo estimar el público. El contexto es necesario para interpretar si el cambio sería «mucho» y para juzgar la conveniencia del traslado. | — |
| 7 | ciclo | 2 | Responder obliga a recorrer el ciclo completo: comprender la diferencia entre capacidad y aforo, suponer el aforo posible, calcular la diferencia o la proporción e interpretar el resultado para los lectores. También obliga a validar contra la cota de 30 mil y el caso de Chillán. Ninguna fase queda hecha. | — |
| 8 | validacion | 2 | La estimación puede contrastarse con una restricción del contexto (la capacidad máxima). También puede contrastarse con datos públicos de asistencia a partidos en el estadio de Concepción, accesibles con una búsqueda simple. | — |
| 9 | nivel | 2 | El contexto futbolístico es comprensible y significativo para estudiantes de 10 a 12 años. La matemática requerida (resta, proporcionalidad directa, división para buses) corresponde a las herramientas del nivel P. | — |
| 10 | autodiferenciacion | 2 | El piso es bajo: se puede empezar con una resta usando las cifras dadas. El techo es alto: la tarea admite estimar el aforo por proporción y calcular la cantidad de buses y la logística del viaje. | — |
| 11 | fecundidad | 2 | Las decisiones sobre el aforo supuesto y los factores logísticos generan soluciones distintas que pueden compararse. Además abren preguntas sobre los límites de la estimación. | — |
| 12 | recursos | 2 | La información necesaria está en el enunciado, en las tarjetas a solicitud o es estimable con conocimiento cotidiano. Ninguna tarjeta revela el modelo; el mapa sin números no orienta la solución. | — |
| | **Total** | **24/24** | | |
