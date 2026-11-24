# ¿Puede la izquierda dar vuelta el resultado?

Tarea `2026-11-izquierda-puede-alcanzar-derecha-v2` · versión 2 · 2026-11-24 · nivel S · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-11-izquierda-puede-alcanzar-derecha-v2
titulo: ¿Puede la izquierda dar vuelta el resultado?
estado: verificada
version: 2
fecha: '2026-11-24'
noticia:
  noticia_id: 2026-11-23-eldiario-el-pp-gana-por-la-minima
  medio: elDiario.es
  titulo: El PP gana por la mínima al PSOE y la derecha supera a la izquierda en la última encuesta antes del 29N
  fecha: '2026-11-23'
  url: https://www.eldiario.es/politica/pp-gana-minima-psoe-derecha-supera-izquierda-ultima-encuesta-29n_1_13684963.html
  resumen_propio: Un sondeo de Ateneo del Dato, con 2.000 entrevistas online hechas a días de las elecciones, sitúa al PP apenas por delante del PSOE y a las derechas por encima de la izquierda gracias a Vox. También recoge quién prefieren como presidente los votantes, cuánta gente repite su voto de 2023 en cada partido y cómo valoran a los principales candidatos.
  cifras_usadas:
  - valor: 32,1%
    unidad: porcentaje de votos
    que_es: intención de voto estimada para el PP en la encuesta de Ateneo del Dato
    localizador:
      fuente: noticia
      ubicacion: párrafo 7
  - valor: 30,8%
    unidad: porcentaje de votos
    que_es: intención de voto estimada para el PSOE en la encuesta de Ateneo del Dato
    localizador:
      fuente: noticia
      ubicacion: párrafo 7
  - valor: 2.000 entrevistas
    unidad: personas entrevistadas
    que_es: tamaño de la muestra de la encuesta
    localizador:
      fuente: noticia
      ubicacion: párrafo 8
  - valor: 17,6%
    unidad: porcentaje de votos
    que_es: intención de voto estimada para Vox
    localizador:
      fuente: noticia
      ubicacion: párrafo 10
  - valor: 49,7%
    unidad: porcentaje de votos
    que_es: suma de los votos estimados para las derechas (PP y Vox)
    localizador:
      fuente: noticia
      ubicacion: párrafo 10
  - valor: 37,5%
    unidad: porcentaje de votos
    que_es: suma de los votos estimados para la izquierda (PSOE, Frente Amplio y Podemos)
    localizador:
      fuente: noticia
      ubicacion: párrafo 10
  - valor: 86,6%
    unidad: porcentaje de votantes de 2023
    que_es: votantes de Vox en 2023 que repetirían su voto
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: 76,1%
    unidad: porcentaje de votantes de 2023
    que_es: votantes del PP en 2023 que repetirían su voto
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: ±2,2%
    unidad: margen de error
    que_es: error muestral para el conjunto de la muestra con nivel de confianza del 95,5%
    localizador:
      fuente: noticia
      ubicacion: párrafo 24
  - valor: 18,2%
    unidad: porcentaje de votantes de 2023
    que_es: votantes del PP en 2023 que ahora votarían a Vox
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: 1,2%
    unidad: porcentaje de votantes de 2023
    que_es: votantes del PP en 2023 que ahora votarían al PSOE
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: 6,1%
    unidad: porcentaje de votantes de 2023
    que_es: votantes de Vox en 2023 que ahora votarían al PP
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: 70,6%
    unidad: porcentaje de votantes de 2023
    que_es: votantes del PSOE en 2023 que repetirían su voto
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: 8%
    unidad: porcentaje de votantes de 2023
    que_es: votantes del PSOE en 2023 que ahora votarían al PP
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: 5,7%
    unidad: porcentaje de votantes de 2023
    que_es: votantes del PSOE en 2023 que ahora votarían a Vox
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
  - valor: 3,9%
    unidad: porcentaje de votantes de 2023
    que_es: votantes del PSOE en 2023 que ahora votarían al Frente Amplio
    localizador:
      fuente: noticia
      ubicacion: párrafo 13
nivel_principal: S
sub_tramo: S2
variantes:
  abajo: null
  arriba: U
area: sociedad_datos
contenidos_matematicos:
- porcentajes
- análisis de escenarios
- sensibilidad
- proporcionalidad
- margen de error
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
El veintitrés de noviembre de dos mil veintiséis, seis días antes de las elecciones generales del veintinueve de noviembre, se publicó una encuesta online de Ateneo del Dato que muestra a las derechas por delante de la izquierda: el PP tendría 32,1% y Vox 17,6%, lo que suma 49,7% de intención de voto, mientras que los partidos de izquierda (PSOE, Frente Amplio y Podemos) sumarían 37,5%. La misma encuesta indica que 86,6% de quienes votaron a Vox en las elecciones anteriores repetirían su voto, y 76,1% de quienes votaron al PP en esas mismas elecciones también. Un equipo de análisis político se pregunta si, con parte del electorado todavía móvil, la izquierda podría alcanzar a la derecha el día de la votación. Ustedes asesoran a ese equipo: ¿qué tendría que ocurrir con los votantes para que eso pase y les parece verosímil? Pueden pedir información adicional.
```

```text foto_descripcion
Una balanza inclinada hacia un lado con una pila de figuras de personas en cada platillo; algunas figuras están en el aire, entre los dos platillos.
```

### 1.1 Variante hacia abajo

No hay.

### 1.2 Variante hacia arriba (tramo U)

Se pide un modelo dinámico con matriz de transferencia entre partidos y abstención, análisis de sensibilidad de los resultados a cada fracción de traspaso, y crítica del supuesto de que el porcentaje de fidelidad de las elecciones anteriores se aplica a la intención de voto actual. La exigencia matemática no se escribe en el enunciado.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Datos de la encuesta que ya tiene el grupo (están escritos en el enunciado) | Intención de voto estimada: PP 32,1%, Vox 17,6%, suma de las derechas 49,7% y suma de los partidos de izquierda 37,5%. Repetirían su voto de las elecciones anteriores: 86,6% de los votantes de Vox y 76,1% de los votantes del PP. | de_entrada | P1-MRS | noticia, párrafos 7, 10 y 13 |
| R2 | Datos de contraste sobre el destino de quienes votaron en las elecciones anteriores. Se entrega solo después de que el grupo presente su primer modelo | Entre quienes votaron al PP en las elecciones anteriores: 76,1% repetiría su voto, 18,2% votaría ahora a Vox y 1,2% al PSOE. Entre quienes votaron a Vox: 86,6% repetiría su voto y 6,1% votaría al PP. Entre quienes votaron al PSOE: 70,6% repetiría su voto, 8% votaría al PP, 5,7% a Vox y 3,9% al Frente Amplio. | a_solicitud | P6-VAL | noticia, párrafo 13 |
| R3 | Intención de voto del PSOE en la misma encuesta | Intención de voto estimada para el PSOE: 30,8%. | a_solicitud | P1-MRS | noticia, párrafo 7 |
| R4 | Tamaño de la muestra y margen de error | La encuesta hizo 2.000 entrevistas y su margen de error para el conjunto de la muestra es ±2,2%. | a_solicitud | P6-VAL | noticia, párrafos 8 y 24 |
| R5 | Información sobre abstención y voto en blanco | Supuesto del escenario: el grupo no dispone de datos sobre cuántas de las personas que no repiten su voto irían a la abstención o al voto en blanco; tiene que fijar un supuesto propio y justificarlo. | a_solicitud | P2-RM | supuesto del escenario |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender qué significa que la izquierda alcance a la derecha y qué datos de la encuesta sirven: bloques, porcentajes y fidelidad de voto. | El grupo explica con sus palabras qué cantidad quiere conocer y lista los datos que usará y los que pedirá. | — |
| P2-RM Simplificar | Decidir adónde van quienes no repiten su voto (otro partido, otro bloque, blanco, abstención), si la fidelidad se aplica al tamaño actual de cada partido y si se considera al resto del electorado. | Lista de supuestos explícitos, por ejemplo que la fidelidad se aplica al porcentaje actual y que solo cambia el voto de las derechas. | B12 |
| P3-MM Matematizar | Construir un modelo de traspaso: diferencia entre bloques, cantidad de votantes móviles y fracción de ellos que va a la izquierda. | Expresión o tabla que relaciona la fracción de traspaso con la nueva diferencia entre bloques. | B23 |
| P4-WM Trabajar | Calcular el traspaso necesario para igualar, la cantidad de votantes móviles y la fracción que debe ir a la izquierda; probar varias fracciones. | Cálculos con la diferencia entre bloques, el traspaso necesario y una tabla de escenarios. | B34 |
| P5-INT Interpretar | Interpretar el resultado: qué proporción de quienes no repiten tendría que elegir izquierda y si eso parece razonable. | Frase en lenguaje cotidiano que compara lo necesario con lo que parece razonable. | B45 |
| P6-VAL Validar | Contrastar el modelo con el margen de error de la encuesta, con los traspasos observados entre partidos (que el grupo pide tras su primer modelo) y, cuando existan, con los resultados oficiales de la elección; distinguir cambiar de partido de cambiar de bloque. | Tabla que compara la fracción que su modelo hacía ir a la izquierda con la observada, y decisión explícita de ajustar o mantener sus supuestos, además de la comparación de la brecha con el error muestral. | B56 |
| P7-EXP Exponer | Presentar el escenario más plausible, sus supuestos, su sensibilidad y lo que cambió tras el contraste. | Cartel o informe breve con tabla de escenarios y una recomendación para el equipo. | B67 |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- El porcentaje de fidelidad y los traspasos medidos sobre quienes votaron en las elecciones anteriores se aplican a la intención de voto actual de cada partido, como aproximación de su tamaño.
- Quienes no repiten su voto van a un destino que el grupo debe decidir (otro partido, otro bloque, blanco o abstención).
- Solo se mueve el voto de la derecha en el escenario base; los demás votos quedan fijos.
- La intención de voto de la encuesta es una buena aproximación del voto real, con el margen de error informado y suponiendo una muestra aleatoria simple.
- Se ignora cómo se traducen los votos en cargos.

### Solución de referencia

1) Brecha entre bloques: 49,7 − 37,5 = 12,2 puntos. 2) Si x puntos pasan de la derecha a la izquierda, la brecha queda 12,2 − 2x; para igualar, x = 6,1 puntos. Si los puntos vienen del resto del electorado (100 − 49,7 − 37,5 = 12,8 puntos), cada punto reduce la brecha en 1; para igualar solo con el resto, la izquierda tendría que captar cerca de 12,2 de esos 12,8 puntos (cerca del 95%). Combinaciones: 2x + y = 12,2, con x desde la derecha e y desde el resto. 3) Votantes móviles de la derecha, aplicando 100 − fidelidad al porcentaje actual: PP, 23,9% de 32,1 ≈ 7,7 puntos; Vox, 13,4% de 17,6 ≈ 2,4 puntos; total ≈ 10,0 puntos. Fracción de móviles que debe ir a la izquierda: 6,1 / 10,0 ≈ 61%. 4) Sensibilidad: con 0%, 30%, 50% y 70% de los móviles yendo a la izquierda, la brecha queda cerca de 12,2; 6,2; 2,2 y −1,8. 5) Margen de error: el error de la brecha entre bloques es cerca de ±4,1 puntos con 95,5% de confianza, bastante menor que 12,2 puntos. 6) Contraste con R2, después del primer modelo, distinguiendo cambiar de partido de cambiar de bloque. De los cerca de 10,0 puntos móviles: del PP, 18,2% va a Vox (≈ 5,8 puntos) y 1,2% al PSOE (≈ 0,4 puntos), y el 4,5% restante (≈ 1,4 puntos) no tiene destino informado; de Vox, 6,1% va al PP (≈ 1,1 puntos) y el 7,3% restante (≈ 1,3 puntos) no tiene destino informado. Es decir, ≈ 6,9 puntos se quedan dentro del bloque de la derecha, ≈ 0,4 van al PSOE y ≈ 2,7 no tienen destino conocido. Solo ≈ 5% de quienes dejan el PP (1,2 de 23,9) va al PSOE, frente al 61% que exigía el modelo. En sentido contrario, del PSOE 8% va al PP y 5,7% a Vox (≈ 4,2 puntos hacia la derecha). 7) Cota extrema: aunque los ≈ 2,7 puntos no asignados y los ≈ 0,4 puntos al PSOE fueran todos a la izquierda (≈ 3,1 puntos), la brecha bajaría solo a ≈ 12,2 − 6,2 = 6,0 puntos; los votos que faltarían (≈ 6 puntos) tendrían que venir del resto del electorado, cerca del 47% de ese resto, o de una abstención muy desigual entre bloques. 8) Cuando existan, comparar con los resultados oficiales por bloques y con el traspaso real, sin usarlos para construir el modelo.

**Resultado.** Para igualar, la izquierda necesitaría ganar unos 6,1 puntos desde la derecha (cerca del 61% de quienes no repiten su voto, que son cerca de 10 puntos) o casi todo el resto del electorado. Según los traspasos observados, la mayoría de quienes dejan el PP o Vox se queda dentro del bloque de la derecha y solo cerca del 5% de quienes dejan el PP va al PSOE. Incluso en la cota extrema la brecha seguiría en cerca de 6 puntos. La ventaja de 12,2 puntos es unas tres veces el error de la brecha (cerca de ±4,1 puntos), por lo que que la izquierda alcance a la derecha es poco verosímil según esta encuesta.

**Rango aceptable.** Traspaso necesario entre 6 y 6,5 puntos; fracción necesaria de los móviles entre 55% y 70% según la base elegida para aplicar la fidelidad; móviles de la derecha entre 9,5 y 10,5 puntos; error de la brecha entre ±3,5 y ±4,5 puntos; brecha en la cota extrema entre 5,5 y 6,5 puntos. Cualquier respuesta con supuestos explícitos, sensibilidad y contraste que distinga cambio de partido de cambio de bloque es defendible.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Traspaso directo entre bloques | S1 | Con la diferencia de 12,2 puntos y un traspaso x de la derecha a la izquierda, resolver 12,2 − 2x = 0. | Se necesitan 6,1 puntos de traspaso para igualar. |
| R2 | Fidelidad como reserva de votantes móviles | S2 | Calcular los votantes móviles como (100 − fidelidad) por el porcentaje actual de cada partido y la fracción que debe ir a la izquierda. | Cerca de 10,0 puntos móviles; se necesita que cerca del 61% vaya a la izquierda. |
| R3 | Tabla de sensibilidad | S2 | Variar la fracción de móviles que va a la izquierda (por ejemplo 0%, 30%, 50%, 70%) y calcular la brecha resultante entre bloques. | La brecha queda cerca de 12,2; 6,2; 2,2 y −1,8; el empate aparece alrededor del 61%. |
| R4 | Balance con el resto del electorado | S2 | Calcular el resto (100 − 49,7 − 37,5) y combinar traspasos desde la derecha (x, que restan 2 por punto) y desde el resto (y, que restan 1 por punto) en 2x + y = 12,2. | El resto suma 12,8 puntos; solo desde el resto la izquierda necesitaría cerca del 95% de él, lo que es poco verosímil. |
| R5 | Flujos observados entre partidos y bloques | S2 | Con los traspasos de R2 aplicados al tamaño actual de cada partido, separar los votantes móviles en los que se quedan en el bloque, los que van a la izquierda y los sin destino informado, y calcular la brecha en el caso extremo en que todos los no asignados van a la izquierda. | Cerca de 6,9 puntos se quedan en el bloque de la derecha, 0,4 van al PSOE y 2,7 no tienen destino informado; en el caso extremo la brecha baja solo a cerca de 6,0 puntos. |

### Modelo inadecuado (R6)

Suponer que todos los votantes que no repiten su voto se pasan a la izquierda y concluir que la izquierda puede ganar porque sumaría cerca de 10 puntos. Es una cota máxima, no un escenario plausible: confunde cambiar de partido con cambiar de bloque (la mayoría de quienes dejan el PP se va a Vox, que sigue en la derecha) e ignora el voto en blanco y la abstención.

### Evidencia de validación (independiente del modelo)

Dos evidencias independientes que el grupo recibe o consigue después de modelar y que no usa para construir el modelo. Primera: los traspasos observados entre partidos (R2, noticia, párrafo 13), que se entregan tras su primer modelo y permiten comparar la fracción de móviles que este hacía ir a la izquierda con la que la encuesta observa (cerca del 5% de quienes dejan el PP van al PSOE). Segunda: los resultados oficiales de la elección del 29 de noviembre de 2026 por bloques (otra fuente: resultados oficiales publicados por el Ministerio del Interior de España), que solo existirán después de esa fecha y permiten comparar el traspaso real entre bloques con el que el modelo consideró verosímil y con el margen de error de la encuesta.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | Plantea una necesidad real de asesoría sin entregar una regla ni un modelo. Quien resuelve debe construir cómo se trasladarían los votos. | — |
| 2 | abierta | 2 | La pregunta no prescribe procedimiento. Admite varios modelos defendibles: diferencia de puntos, transferencias entre partidos, captación de indecisos o abstención. | — |
| 3 | decisiones | 2 | Resolver exige seleccionar datos, decidir qué hacer con el 12,8% restante, suponer transferencias y destino de quienes no repiten el voto, y solicitar información. | — |
| 4 | realismo | 2 | Analizar si una encuesta preelectoral puede revertirse es una situación que existe en el análisis político y periodístico. | — |
| 5 | autenticidad | 2 | Los datos de una encuesta publicada en prensa son el núcleo de la tarea y no fueron creados para enseñar matemática. | — |
| 6 | contexto | 2 | El contexto electoral condiciona los supuestos sobre fidelidad y transferencia de votos. También es necesario para juzgar la verosimilitud del escenario. | — |
| 7 | ciclo | 2 | Hay que comprender la encuesta, simplificar el electorado, matematizar los traspasos, calcular y volver a la situación para juzgar la verosimilitud. Ninguna fase viene hecha. | — |
| 8 | validacion | 2 | R2 ofrece evidencia independiente, no usada en la construcción, para contrastar el modelo. Además existirá el resultado real de la elección. | — |
| 9 | nivel | 2 | Los porcentajes, los escenarios en competencia y la interpretación del margen de error están al alcance de S2. El lenguaje es comprensible para ese nivel. | — |
| 10 | autodiferenciacion | 2 | Hay un piso accesible: calcular la brecha de 12,2 puntos y cuánto debe moverse. El techo es alto: matrices de transferencia, margen de error y sensibilidad a supuestos de abstención. | — |
| 11 | fecundidad | 2 | Los distintos escenarios de traspaso y abstención permiten comparar soluciones. También abren preguntas sobre la confiabilidad de las encuestas y los límites del modelo. | — |
| 12 | recursos | 2 | La información adicional está disponible a solicitud (R2 a R5) y no revela la estructura de la solución. R5 obliga a fijar un supuesto propio en lugar de entregarlo. | — |
| | **Total** | **24/24** | | |
