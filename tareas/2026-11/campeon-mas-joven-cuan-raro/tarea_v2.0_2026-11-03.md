# ¿Cuán raro es un campeón mundial de veinte años?

Tarea `2026-11-campeon-mas-joven-cuan-raro-v2` · versión 2 · 2026-11-02 · nivel U · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-11-campeon-mas-joven-cuan-raro-v2
titulo: ¿Cuán raro es un campeón mundial de veinte años?
estado: verificada
version: 2
fecha: '2026-11-02'
noticia:
  noticia_id: 2026-11-02-latercera-aprendizaje-y-adaptacion-las-claves-que
  medio: La Tercera
  titulo: 'Aprendizaje y adaptación: las claves que llevaron a Kimi Antonelli a ser el campeón más joven en la historia de la Fórmula 1'
  fecha: '2026-11-02'
  url: https://www.latercera.com/el-deportivo/noticia/aprendizaje-y-adaptacion-las-claves-que-llevaron-a-kimi-antonelli-a-ser-el-campeon-mas-joven-en-la-historia-de-la-formula-1/
  resumen_propio: Crónica del título mundial del piloto italiano de Mercedes, Kimi Antonelli, quien se convirtió en el campeón más joven del automovilismo de élite tras una temporada 2026 dominante. La nota muestra cómo aprendió de su irregular año de debut, se acomodó al nuevo reglamento y a los monoplazas más livianos, y manejó la presión frente a su compañero Russell. Además, compara su récord con los de Vettel, Hamilton y Alonso.
  cifras_usadas:
  - valor: 20 años
    unidad: años
    que_es: edad del piloto al ser coronado campeón
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 23 años y 134 días
    unidad: años y días
    que_es: edad de Vettel al coronarse campeón en 2010
    localizador:
      fuente: noticia
      ubicacion: párrafo 14
  - valor: 23 años y 300 días
    unidad: años y días
    que_es: edad de Hamilton al coronarse campeón en 2008
    localizador:
      fuente: noticia
      ubicacion: párrafo 14
  - valor: 24 años y 58 días
    unidad: años y días
    que_es: edad de Alonso al coronarse campeón en 2005
    localizador:
      fuente: noticia
      ubicacion: párrafo 14
  - valor: 134 días
    unidad: días
    que_es: días, además de los años cumplidos, de la edad de Vettel al coronarse en 2010
    localizador:
      fuente: noticia
      ubicacion: párrafo 14
  - valor: 300 días
    unidad: días
    que_es: días, además de los años cumplidos, de la edad de Hamilton al coronarse en 2008
    localizador:
      fuente: noticia
      ubicacion: párrafo 14
  - valor: 58 días
    unidad: días
    que_es: días, además de los años cumplidos, de la edad de Alonso al coronarse en 2005
    localizador:
      fuente: noticia
      ubicacion: párrafo 14
nivel_principal: U
variantes:
  abajo: S
  arriba: null
area: deporte
contenidos_matematicos:
- inferencia con muestras pequeñas
- distribuciones de cola pesada
- incertidumbre de medición
- modelos de mezcla y cambio de régimen
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
Un programa deportivo de radio debate si el título mundial de Kimi Antonelli, piloto de Mercedes, es una rareza irrepetible o el comienzo de una época de campeones cada vez más jóvenes. El piloto fue coronado con 20 años. La crónica de La Tercera lo compara con tres campeones anteriores, que ganaron su título a los 23 años y 134 días (Vettel), 23 años y 300 días (Hamilton) y 24 años y 58 días (Alonso). El periodista a cargo quiere decir al aire qué tan excepcional es esa marca y con qué frecuencia podría repetirse algo así, y tiene que justificar su respuesta frente a oyentes críticos. ¿Qué dirían ustedes, con qué modelo lo respaldarían y qué tan seguros pueden estar? Pueden pedir información adicional.
```

```text foto_descripcion
Ícono de un trofeo de campeonato con un reloj de arena al lado.
```

### 1.1 Variante hacia abajo (tramo S2)

Se entregan las edades convertidas a años con decimales y se explica que la edad de Antonelli solo se conoce en años cumplidos. La pregunta se reduce a cuánto se aleja la marca del récord anterior y de la dispersión de los otros tres, sin exigir modelo de probabilidad.

### 1.2 Variante hacia arriba

No hay.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Edades de los campeones, incluidas en el enunciado | Edad al coronarse: Antonelli, 20 años; Vettel, 23 años y 134 días; Hamilton, 23 años y 300 días; Alonso, 24 años y 58 días. | de_entrada | P1-MRS | noticia, párrafos 3 y 14 |
| R2 | Precisión de la edad del piloto actual | La edad de Antonelli se informa solo en años cumplidos, sin los días; la de los otros tres campeones se informa en años y días. | a_solicitud | P2-RM | noticia, párrafos 3 y 14 |
| R3 | Edad mínima para competir | Existe una edad mínima reglamentaria para obtener la licencia que habilita a correr en la máxima categoría. La noticia no la entrega; el grupo debe buscarla o suponerla. | a_solicitud | P2-RM | otra fuente: Código Deportivo Internacional de la FIA, reglas de licencias |
| R4 | Alcance de la comparación | Supuesto del escenario: los tres campeones comparados son los que cita la crónica como referencia; hay otros campeones más antiguos que no aparecen en la lista. | a_solicitud | P2-RM | supuesto del escenario |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Aclarar qué significa «excepcional» y «repetirse», y notar que las edades vienen en años y días o solo en años. | El grupo reescribe la pregunta con sus palabras y señala qué dato es impreciso. | — |
| P2-RM Simplificar | Decidir qué se modela (la edad al título como variable aleatoria), cómo tratar los 20 años (entre 20 y 21) y si los tres campeones forman una muestra representativa. | Lista de supuestos con una frase sobre el sesgo de selección y sobre la edad mínima de licencia. | B12 |
| P3-MM Matematizar | Convertir edades a años con decimales y elegir una distribución (normal, t, mezcla de dos poblaciones) para la edad al título. | Tabla de edades en años decimales y la distribución elegida con sus parámetros. | B23 |
| P4-WM Trabajar | Calcular media, dispersión y la probabilidad de una edad igual o menor bajo cada modelo, para ambos extremos del intervalo de la edad. | Cálculos con al menos dos modelos y dos valores para la edad de Antonelli. | B34 |
| P5-INT Interpretar | Traducir las probabilidades a una frase para la radio y explicar por qué los modelos discrepan tanto. | Texto para el aire con una cifra aproximada de frecuencia y una advertencia sobre su fiabilidad. | B45 |
| P6-VAL Validar | Contrastar con la lista completa de campeones históricos, que no se usó para construir el modelo, y juzgar el sesgo de selección y la edad mínima. | Comparación entre lo que predice cada modelo y la distribución histórica real de edades. | B56 |
| P7-EXP Exponer | Presentar la conclusión con un gráfico de las edades y la cola de cada modelo, indicando los límites. | Guion breve y gráfico con las distribuciones comparadas. | B67 |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- La edad de Antonelli se conoce solo en años cumplidos: se trata como un valor entre 20 y 21 años.
- Las edades se convierten a años decimales dividiendo los días por 365.
- Los tres campeones de referencia se tratan como una muestra de la población de campeones, reconociendo que no es aleatoria.
- Existe una edad mínima de licencia que limita la cola inferior de la distribución.
- Se acepta un modelo de cola pesada o de dos poblaciones como alternativa a la normal.

### Solución de referencia

1) Pasar a años decimales: Vettel 23,367; Hamilton 23,822; Alonso 24,159; media 23,783 y desviación muestral cercana a 0,40; Antonelli entre 20,0 y 21,0. 2) Brecha con el récord previo: entre 2,4 y 3,4 años, de 3 a 4 veces el rango observado de los otros tres (0,79). 3) Modelo normal con esos parámetros: z entre -7 y -9,5, probabilidad prácticamente cero, lo que rechaza que Antonelli salga de la misma población. 4) Modelo con cola pesada (predictiva t con dos grados de libertad y escala 0,46): probabilidad entre 0,7 % y 1,3 % por título. 5) Modelo de mezcla: con una observación temprana de cuatro y previa uniforme, la proporción de campeones tempranos tendría media cercana a 0,33, pero la muestra está seleccionada. 6) Sensibilidad: las conclusiones sobre frecuencia dependen fuertemente del modelo y del tamaño muestral; considerar también la edad mínima de licencia (en torno a 18 años, a verificar), que acota cuánto más joven puede ser un campeón.

**Resultado.** La marca es muy excepcional: queda fuera de lo observado en la referencia. Su frecuencia estimada varía de casi cero (normal) a cerca de 1 % por título (cola pesada) o a una fracción mucho mayor si se supone un cambio de régimen. Una afirmación honesta indica un rango y las limitaciones por la muestra pequeña y seleccionada.

**Rango aceptable.** Se acepta cualquier conclusión que trate la incertidumbre de la edad, explicite el modelo y reconozca el sesgo de selección y el piso de edad. Una probabilidad de un solo valor sin discusión de sensibilidad no es suficiente.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Brecha respecto del récord y de la dispersión | S1 | Diferencia de edades en años decimales y comparación con el rango de los tres campeones, con los dos extremos de la edad de Antonelli. | Brecha de 2,4 a 3,4 años, de 3 a 4 veces el rango observado: marca fuera de lo visto. |
| R2 | Puntaje z con distribución normal | S2 | Media y desviación de los tres campeones; z para la edad de Antonelli en ambos extremos. | z entre -7 y -9,5, probabilidad casi nula: no pertenece a la misma población. |
| R3 | Predictiva de cola pesada | U | Distribución t predictiva con muestra pequeña para la edad al título de un nuevo campeón. | Probabilidad por título entre 0,7 % y 1,3 %, con gran dependencia del modelo. |
| R4 | Cambio de régimen con mezcla bayesiana | U | Mezcla de campeones tardíos y tempranos con proporción desconocida; actualización beta con previa uniforme. | Proporción posterior de campeones tempranos con media cercana a 0,33 y un intervalo muy ancho, a discutir por el sesgo de selección. |

### Modelo inadecuado (RX: suponer una distribución normal con la media y desviación de los tres campeones y concluir que un título a los 20 años es imposible.)

Con solo tres datos, la desviación es muy incierta y la normal subestima las colas. La muestra es seleccionada, porque son los tres campeones que la crónica eligió como referencia. Además, el piso de edad de licencia y la edad de Antonelli en años cumplidos ya muestran que el modelo no refleja la realidad del problema.

### Evidencia de validación (independiente del modelo)

Después de modelar, el grupo consigue la lista completa de edades de todos los campeones mundiales históricos (registro oficial de campeones, formula1.com), que no se usó para construir los modelos. Contrasta la frecuencia observada de títulos antes de cierta edad con lo que predice cada modelo, la forma de la distribución real y la edad mínima de licencia como restricción.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | Hay una necesidad comunicativa real: justificar ante oyentes críticos. El enunciado no entrega ningún modelo ni regla para medir rareza o frecuencia. | — |
| 2 | abierta | 2 | La pregunta deja al grupo la elección del modelo. Admite varios caminos defendibles, como una distribución de edades de campeones, valores extremos, tendencia temporal o frecuencia por temporada, sin prescribir el procedimiento. | — |
| 3 | decisiones | 2 | Resolver exige varias decisiones: definir qué significa «raro», reconocer que la muestra de tres campeones es sesgada y buscar más datos. También hay que suponer la edad mínima y elegir el horizonte de frecuencia, todo lo cual son decisiones de modelación sustantivas. | — |
| 4 | realismo | 2 | Un debate radial sobre un récord de edad en la Fórmula 1 es una situación claramente plausible fuera de la escuela. | — |
| 5 | autenticidad | 2 | Los datos provienen de una crónica de prensa citada y son el núcleo de la tarea. Ese componente auténtico está integrado de manera sustantiva. | — |
| 6 | contexto | 2 | El contexto condiciona el modelo: la cota inferior de edad, un campeón por temporada y el universo de campeones. También es necesario para interpretar la frecuencia y validar ante los oyentes. | — |
| 7 | ciclo | 2 | Responder obliga a recorrer todo el ciclo. Hay que comprender el debate, simplificar (definir rareza y elegir datos), matematizar, calcular, interpretar para la audiencia y evaluar la confianza, sin que el enunciado deje ninguna fase hecha. | — |
| 8 | validacion | 2 | Existe evidencia independiente accesible para contrastar el modelo: la lista histórica completa de edades de campeones, otras categorías y temporadas futuras. | — |
| 9 | nivel | 2 | El contexto es comprensible y pertinente para estudiantes universitarios. La demanda requiere probabilidad y modelos estadísticos, coherentes con las herramientas esperables en U según MAR03. | — |
| 10 | autodiferenciacion | 2 | El piso es accesible: basta comparar diferencias de edad o calcular promedios. El techo es alto, porque la tarea admite distribuciones ajustadas, teoría de extremos, análisis de tendencia o inferencia con incertidumbre cuantificada. | — |
| 11 | fecundidad | 2 | La tensión entre rareza y tendencia abre preguntas nuevas: el efecto de la edad mínima, el sesgo de la muestra o cambios en la formación de pilotos. Además permite comparar modelos y sus límites. | — |
| 12 | recursos | 2 | Los recursos aportan matices sin revelar el modelo. Los datos faltantes, como la lista completa de campeones y la edad mínima de la licencia, se obtienen con una búsqueda simple a nivel universitario. | — |
| | **Total** | **24/24** | | |
