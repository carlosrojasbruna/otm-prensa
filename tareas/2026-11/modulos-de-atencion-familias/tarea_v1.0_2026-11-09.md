# ¿Cuántos módulos hacen falta para atender a todas las familias?

Tarea `2026-11-modulos-de-atencion-familias` · versión 1 · 2026-11-09 · nivel P · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-11-modulos-de-atencion-familias
titulo: ¿Cuántos módulos hacen falta para atender a todas las familias?
estado: verificada
version: 1
fecha: '2026-11-09'
noticia:
  noticia_id: 2026-11-09-latercera-inician-desalojo-de-toma-nuevo-amanecer
  medio: La Tercera
  titulo: 'Inician desalojo de toma “Nuevo Amanecer” en Cerrillos: más de 800 personas viven en el sector'
  fecha: '2026-11-09'
  url: https://www.latercera.com/nacional/noticia/inician-desalojo-de-toma-nuevo-amanecer-en-cerrillos-mas-de-800-personas-viven-en-el-sector/
  resumen_propio: Autoridades comenzaron la primera etapa de retiro de un asentamiento irregular en Cerrillos, Región Metropolitana, con apoyo de policías y funcionarios municipales y estatales. La medida cubre una franja de terreno y responde a órdenes judiciales vinculadas a delitos y a obras viales. El ministro de Seguridad defendió la estrategia de desalojos semanales como forma de recuperar el espacio público.
  cifras_usadas:
  - valor: 3
    unidad: hectáreas
    que_es: Superficie de la franja prioritaria incluida en la primera fase del desalojo
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 300
    unidad: viviendas
    que_es: Cantidad de casas emplazadas en el sector que será desalojado
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 800
    unidad: personas
    que_es: Cantidad aproximada de habitantes que viven en las viviendas del sector
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
nivel_principal: P
variantes:
  abajo: null
  arriba: S
area: sociedad_datos
contenidos_matematicos:
- multiplicación y división
- tasas y proporcionalidad
- tablas de valores
- estimación de tiempo
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
Las autoridades de Cerrillos, en la Región Metropolitana, comenzaron a retirar un asentamiento irregular en una franja de 3 hectáreas, donde hay 300 viviendas y viven unas 800 personas. Imaginen que ustedes forman parte de un equipo municipal que, durante ese operativo, instala módulos de atención para registrar a las familias y entregarles información sobre ayudas. Cada módulo es una mesa con un funcionario, y cada familia se atiende una sola vez. La jefa del equipo debe decidir cuántos módulos instalar y por cuántas horas funcionarán, para que las familias no esperen demasiado. ¿Qué plan de atención le recomendarían y cuánto tiempo estiman que se necesita? Pueden pedir información adicional.
```

```text foto_descripcion
Dibujo simple de varias mesas de atención con carteles numerados y una fila de personas dibujadas con trazos sencillos frente a ellas.
```

### 1.1 Variante hacia abajo

No hay.

### 1.2 Variante hacia arriba (tramo S1)

Se pide comparar dos planes (más módulos por menos horas frente a menos módulos por más horas) considerando que las familias llegan más en las primeras horas de la jornada, y se pide ver cómo cambia el plan si el tiempo de atención varía por encima o por debajo de lo estimado. La validación incluye contrastar el tiempo estimado con una entrevista a un funcionario de atención al público.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Datos de la noticia que se entregan desde el inicio | La primera etapa cubre una franja de 3 hectáreas, con 300 viviendas y unas 800 personas. | de_entrada | P1-MRS | noticia, párrafo 3 |
| R2 | Aclaración sobre quién se registra | Supuesto del escenario: se registra una persona adulta por hogar, y cada vivienda corresponde a un hogar. La atención consiste en llenar una ficha con datos y entregar un papel con información. | a_solicitud | P2-RM | supuesto del escenario |
| R3 | Aclaración sobre el funcionamiento de la jornada | Supuesto del escenario: los módulos funcionan al mismo tiempo, cada uno con un funcionario. Las familias llegan repartidas a lo largo de la jornada, sin hora fija, y el equipo hace una pausa de colación que no se cuenta como atención. | a_solicitud | P2-RM | supuesto del escenario |
| R4 | Ficha de ejemplo para practicar el registro | Supuesto del escenario: ficha de registro de ejemplo con los campos nombre de la persona responsable, dirección, cantidad de integrantes del hogar y teléfono de contacto. El grupo puede llenarla entre compañeros con un cronómetro para estimar cuánto demora una atención. | a_solicitud | P3-MM | supuesto del escenario |
| R5 | Simulacro en la sala para contrastar el plan | Supuesto del escenario: el profesor puede organizar que un grupo de compañeros haga el papel de familias y que el grupo atienda con los módulos de su plan, cronometrando el tiempo total. | a_solicitud | P6-VAL | supuesto del escenario |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender que hay que decidir cuántos módulos y cuántas horas para atender a todas las familias de una jornada. | El grupo reformula la meta como atender a todas las familias sin esperas largas. | — |
| P2-RM Simplificar | Elegir qué dato sirve (viviendas, personas o hectáreas), suponer una atención por hogar y suponer un tiempo por familia. | Lista de supuestos y de datos descartados, por ejemplo las hectáreas. | B12 |
| P3-MM Matematizar | Relacionar familias, tiempo por familia, número de módulos y horas de jornada, y estimar el tiempo de atención con la ficha. | Tabla o esquema que relaciona módulos con horas necesarias; tiempos medidos con cronómetro. | B23 |
| P4-WM Trabajar | Calcular el tiempo total de atención y repartirlo entre módulos que trabajan a la vez, y probar varias opciones. | Tabla de valores con distintas cantidades de módulos y las horas resultantes. | B34 |
| P5-INT Interpretar | Traducir los cálculos a una recomendación con un número de módulos y una duración de jornada, y juzgar cuál es razonable. | Recomendación escrita con módulos, horas y justificación. | B45 |
| P6-VAL Validar | Hacer un simulacro en la sala y comparar el tiempo observado con el tiempo previsto por el plan. | Registro de tiempos del simulacro y comparación con la predicción, con un ajuste del plan si hace falta. | B56 |
| P7-EXP Exponer | Presentar el plan a la jefa del equipo con sus supuestos y su margen de error. | Cartel o informe breve con tabla, recomendación y supuestos. | B67 |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- Una vivienda corresponde a un hogar y se atiende una persona adulta por hogar.
- El tiempo de atención por familia se estima midiéndolo con una ficha de ejemplo y con un cronómetro.
- Los módulos trabajan al mismo tiempo y con la misma rapidez.
- La jornada tiene una duración definida por el grupo, y las pausas no cuentan como atención.
- Las familias llegan repartidas durante la jornada.

### Solución de referencia

1) Elegir 300 hogares como cantidad de atenciones, porque se registra un hogar por vivienda; las hectáreas no influyen. 2) Estimar el tiempo por familia con la ficha, por ejemplo 10 minutos. 3) Tiempo total de trabajo: 300 × 10 = 3.000 min = 50 horas de módulo. 4) Repartir entre módulos que trabajan a la vez: con 5 módulos, 10 horas; con 6 módulos, unas 8,3 horas; con 8 módulos, unas 6,3 horas. 5) Para una jornada de 8 horas se necesitan al menos 7 módulos; añadiendo un margen por esperas, un plan razonable es 8 módulos funcionando 8 horas. 6) Variante: si se atiende a cada una de las 800 personas con 5 minutos cada una, son 4.000 min, unas 67 horas de módulo.

**Resultado.** Plan de unos 7 a 8 módulos funcionando una jornada de 8 horas, con unas 50 horas de trabajo total de atención si se usan 10 minutos por familia.

**Rango aceptable.** Entre 40 y 75 horas de módulo en total, y entre 5 y 9 módulos para una jornada de 8 horas, según el tiempo por familia (de 8 a 15 minutos), si se atiende por hogar o por persona, y el margen por esperas.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Tiempo total repartido entre módulos | P | Familias × minutos por familia = tiempo total; dividir entre el número de módulos. | 50 horas de módulo; 7 módulos para 8 horas. |
| R2 | Tabla de prueba de módulos | P | Armar una tabla con 4, 6 y 8 módulos y calcular cuántas familias atiende cada uno en la jornada. | Con 8 módulos y un ritmo de 6 familias por hora cada uno, se atienden 384 familias en 8 horas, más que las 300 necesarias. |
| R3 | Atención por persona en vez de por hogar | P | Usar 800 personas con un tiempo menor por atención individual y repartir entre módulos. | Unas 67 horas de módulo y 9 módulos para 8 horas (plan más exigente). |
| R4 | Tasa de atención por módulo con margen | S1 | Tasa de familias por hora por módulo, con un factor de eficiencia menor que 1 por esperas e interrupciones; resolver una ecuación para el número de módulos. | Con 6 familias por hora y 80 % de eficiencia, hacen falta unos 8 módulos para 8 horas. |

### Modelo inadecuado (RX)

Decidir el número de módulos a partir de las 3 hectáreas, por ejemplo uno por hectárea. Falla porque el tiempo de atención depende de cuántas familias hay y cuánto demora cada una, no del tamaño del terreno; además deja el plan sin relación con la jornada.

### Evidencia de validación (independiente del modelo)

Un simulacro en la sala donde compañeros que no participaron en la estimación hacen de familias y son atendidos con los módulos del plan. Se cronometra el tiempo total y se compara con el predicho, escalando la cantidad de familias. También se puede entrevistar a un funcionario de una oficina de atención al público sobre cuánto demora una atención típica. Estos datos no se usan para construir el modelo.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | Plantea una necesidad real de planificación (cuántos módulos y cuántas horas) sin entregar ninguna regla ni modelo para calcularla. | — |
| 2 | abierta | 2 | Admite varios planes defendibles, por ejemplo más módulos con menos horas o al revés, y la pregunta no prescribe el procedimiento. | — |
| 3 | decisiones | 2 | Hay que decidir si se atiende por vivienda o por persona, estimar la duración de una atención, interpretar «no esperen demasiado» y solicitar información. Son decisiones de modelación sustantivas. | — |
| 4 | realismo | 2 | El operativo es un hecho real, y que un equipo municipal registre a las familias durante él es claramente plausible fuera de la escuela. | — |
| 5 | autenticidad | 2 | Los datos de la noticia (300 viviendas, unas 800 personas) son el insumo central del modelo, de modo que el componente auténtico está integrado de manera sustantiva. | — |
| 6 | contexto | 2 | El contexto condiciona las decisiones (familias o personas, jornada, colación, espera aceptable). También es necesario para interpretar y juzgar si el plan es razonable. | — |
| 7 | ciclo | 2 | Responder obliga a comprender la situación, simplificarla y estimar tiempos, calcular el tiempo total según el número de módulos, y volver al contexto para recomendar y juzgar el plan. Las aclaraciones R2 y R3 solo se entregan a solicitud y no dejan hecha ninguna fase. | — |
| 8 | validacion | 2 | El simulacro cronometrado es una medición independiente que permite contrastar el plan con un caso nuevo. | — |
| 9 | nivel | 2 | El contexto y el lenguaje son comprensibles para 10–12 años. La matemática requerida (operatoria, reparto, estimación, conversión de minutos a horas) está entre las herramientas esperables del nivel P. | — |
| 10 | autodiferenciacion | 2 | Se puede entrar con una división simple de 300 atenciones entre módulos. La tarea admite soluciones más sofisticadas que consideran la llegada repartida, la colación, la variabilidad de tiempos y el equilibrio entre módulos y horas. | — |
| 11 | fecundidad | 2 | La relación entre módulos y horas permite comparar planes distintos y abre preguntas sobre la espera, los costos y los límites del modelo. | — |
| 12 | recursos | 2 | El dato clave (la duración de una atención) puede medirse en clase, y las aclaraciones a solicitud precisan el escenario sin revelar la relación entre módulos, horas y familias. | — |
| | **Total** | **24/24** | | |
