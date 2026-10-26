# ¿Qué tan reñida fue la elección en Brasil?

Tarea `2026-10-que-tan-renida-fue` · versión 1 · 2026-10-26 · nivel P · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-10-que-tan-renida-fue
titulo: ¿Qué tan reñida fue la elección en Brasil?
estado: verificada
version: 1
fecha: '2026-10-26'
noticia:
  noticia_id: 2026-10-26-latercera-exembajador-depolo-y-postura-de-bolsonaro
  medio: La Tercera
  titulo: 'Exembajador Depolo y postura de Bolsonaro de desconocer triunfo de Lula: “Expresa su prontuario antidemocrático”'
  fecha: '2026-10-26'
  url: https://www.latercera.com/politica/noticia/exembajador-depolo-y-postura-de-bolsonaro-de-desconocer-triunfo-de-lula-expresa-su-prontuario-antidemocratico/
  resumen_propio: Un exembajador chileno en Brasil comenta el balotaje en que Lula superó a Flávio Bolsonaro y el desconocimiento del resultado por parte del bando opositor. Según su visión, esa postura refleja rasgos antidemocráticos, y los partidos de centro podrían acercarse al nuevo gobierno para formar mayorías parlamentarias. También destaca la movilización de la campaña de Lula y ve en el resultado una lección para Chile.
  cifras_usadas:
  - valor: 51,79 %
    unidad: porcentaje de votos
    que_es: Proporción de votos obtenida por Lula en el balotaje
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 64.256.232
    unidad: votos
    que_es: Votos obtenidos por Lula en el balotaje
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 48,21 %
    unidad: porcentaje de votos
    que_es: Proporción de votos obtenida por Flávio Bolsonaro en el balotaje
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 59.826.041
    unidad: votos
    que_es: Votos obtenidos por Flávio Bolsonaro en el balotaje
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 50,9 %
    unidad: porcentaje de votos
    que_es: Proporción de votos obtenida por Lula en la elección de 2022
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 49,1 %
    unidad: porcentaje de votos
    que_es: Proporción de votos obtenida por Jair Bolsonaro en la elección de 2022
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
nivel_principal: P
variantes:
  abajo: null
  arriba: S
area: sociedad_datos
contenidos_matematicos:
- operatoria con números grandes
- comparación y diferencia
- porcentajes simples
- estimación y redondeo
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
En Brasil se hizo una segunda vuelta para elegir presidente. Lula obtuvo 64.256.232 votos, que son el 51,79 % de los votos. Flávio Bolsonaro obtuvo 59.826.041 votos, el 48,21 %. En un programa de radio, una persona dijo que fue una elección muy pareja y otra dijo que Lula ganó con claridad. Ustedes forman el equipo de datos de un diario escolar y deben escribir una nota breve que explique qué tan reñida fue esta elección y cómo lo saben. Decidan qué comparaciones hacer y qué datos les sirven para apoyar su opinión. ¿Fue una elección pareja o clara? Pueden pedir información adicional.
```

```text foto_descripcion
Dibujo sencillo de una urna de votación y, al lado, dos barras horizontales de colores distintos, sin números.
```

### 1.1 Variante hacia abajo

No hay.

### 1.2 Variante hacia arriba (tramo S)

Se entregan solo los votos (sin porcentajes). Se pide además comparar con la elección anterior discutiendo si conviene medir el margen en votos o en porcentaje, y estimar cuántos votantes habrían tenido que cambiar de bando para llegar a un empate.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Resultados de la segunda vuelta que el grupo recibe de entrada | Lula: 64.256.232 votos (51,79 %). Flávio Bolsonaro: 59.826.041 votos (48,21 %). | de_entrada | P1-MRS | noticia, párrafo 3 |
| R2 | Resultado de la elección presidencial anterior, como punto de comparación | En la elección presidencial anterior, Lula obtuvo el 50,9 % de los votos y Jair Bolsonaro el 49,1 %. | a_solicitud | P6-VAL | noticia, párrafo 3 |
| R3 | Aclaración sobre qué votos se cuentan | Supuesto del escenario: para esta nota solo se consideran los votos de los dos candidatos de la segunda vuelta; no se toman en cuenta votos en blanco ni nulos. | a_solicitud | P2-RM | supuesto del escenario |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Decidir qué significa 'reñida' y qué datos de la situación hablan de eso (no basta saber quién ganó). | El grupo explica con sus palabras qué sería una elección pareja y subraya los datos que usará. | B12 |
| P2-RM Simplificar | Elegir entre mirar votos o porcentajes, aceptar que solo cuentan dos candidatos y fijar un criterio propio de 'pareja'. | Lista escrita de supuestos y de datos usados o descartados. | B23 |
| P3-MM Matematizar | Expresar la ventaja como resta de votos, como parte del total o como diferencia de porcentajes. | Operaciones planteadas en el cuaderno antes de calcular. | B34 |
| P4-WM Trabajar | Restar, sumar para obtener el total y relacionar la diferencia con el total, con números grandes y redondeos. | Cálculos con resultados redondeados y unidades. | B45 |
| P5-INT Interpretar | Traducir 'unos cuatro millones de votos' a 'mucho' o 'poco' según el total de votos. | Frase de la nota que relaciona el resultado numérico con la palabra pareja o clara. | B56 |
| P6-VAL Validar | Pedir la elección anterior y comparar márgenes; recalcular el porcentaje a partir de los votos y contrastarlo con el informado. | Tabla con las dos elecciones y comprobación de que el porcentaje calculado coincide con el publicado. | B67 |
| P7-EXP Exponer | Escribir la nota y elegir una representación (barras o frase) que respalde su conclusión. | Nota breve con una conclusión, dos cifras y el criterio usado. | — |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- Solo cuentan los votos de los dos candidatos de la segunda vuelta.
- El grupo acuerda un criterio para decir que una elección es pareja (por ejemplo, una diferencia pequeña respecto del total).
- La elección anterior sirve como referencia de comparación.

### Solución de referencia

1) Diferencia de votos: 64.256.232 − 59.826.041 = 4.430.191. 2) Total de votos de los dos: 64.256.232 + 59.826.041 = 124.082.273. 3) Diferencia respecto del total: 4.430.191 ÷ 124.082.273 ≈ 0,036, es decir unos 3,6 puntos porcentuales (51,79 − 48,21 = 3,58). 4) Elección anterior: 50,9 − 49,1 = 1,8 puntos. 5) Conclusión según criterio acordado: aunque la diferencia supera los cuatro millones de votos, equivale a menos de cuatro de cada cien votos; fue ajustada, pero más amplia que la elección anterior.

**Resultado.** Diferencia de unos 4,4 millones de votos, equivalente a unos 3,6 puntos porcentuales; elección ajustada, con un margen cercano al doble del de la elección anterior (1,8 puntos).

**Rango aceptable.** Diferencia de votos entre 4,4 y 4,5 millones; diferencia relativa entre 3,5 y 3,6 puntos; son defendibles conclusiones como 'bastante pareja' o 'ganó con claridad moderada', siempre que expliciten el criterio y comparen con el total.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Resta de votos y comparación con el total | P | Aditivo: diferencia de votos y luego comparación con el total de votos (estimación con millones redondeados). | Unos 4,4 millones de diferencia sobre unos 124 millones de votos: aproximadamente 4 de cada 100. |
| R2 | Diferencia de porcentajes y comparación con la elección anterior | P | Aditivo con porcentajes: 51,79 − 48,21 frente a 50,9 − 49,1. | 3,58 puntos frente a 1,8 puntos: margen cercano al doble. |
| R3 | Razón entre votos | S1 | Proporcional: 64.256.232 ÷ 59.826.041 ≈ 1,074, o sea unos 107 votos de Lula por cada 100 de Bolsonaro. | Razón de aproximadamente 1,07; ventaja de unos 7 votos por cada 100 del otro candidato. |
| R4 | Cuántos votantes tendrían que cambiar para empatar | S1 | Aditivo: la mitad de la diferencia de votos, 4.430.191 ÷ 2. | Unos 2.215.096 votantes tendrían que cambiar de bando. |

### Modelo inadecuado (RX)

Decir que fue clara solo porque la diferencia es de millones de votos, sin relacionarla con el total, ignora que una cifra grande puede ser pequeña respecto del total y no permite comparar con otra elección.

### Evidencia de validación (independiente del modelo)

Dato independiente de la construcción del modelo: los porcentajes publicados y los de la elección anterior (50,9 % y 49,1 %). El grupo contrasta el porcentaje calculado a partir de los votos con el publicado (coinciden al redondear) y compara el margen actual con el de la elección anterior.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | La tarea plantea una necesidad real: dirimir si la elección fue pareja o clara para una nota de prensa. No entrega ninguna regla ni criterio para medir qué tan reñida fue. | — |
| 2 | abierta | 2 | Hay varios caminos defendibles: diferencia de votos, diferencia en puntos porcentuales, votos que habría que cambiar o comparación con la elección anterior. La pregunta no prescribe ningún procedimiento. | — |
| 3 | decisiones | 2 | Resolver exige definir qué significa «reñida» y elegir qué medida y qué referencia usar. También se puede decidir si solicitar información adicional (elección anterior, tratamiento de blancos y nulos). | — |
| 4 | realismo | 2 | El debate público sobre la estrechez de un resultado electoral es una situación que existe fuera de la escuela, y la nota de un diario escolar es plausible. | — |
| 5 | autenticidad | 2 | Los resultados electorales y el tema son componentes extraescolares no creados para enseñar, y constituyen el núcleo de la tarea. La verificación de la fuente corresponde a otro agente. | — |
| 6 | contexto | 2 | El contexto electoral condiciona qué medida tiene sentido usar. También es necesario para interpretar si una diferencia de unos 4,4 millones de votos o 3,58 puntos es «pareja» o «clara». | — |
| 7 | ciclo | 2 | Responder exige recorrer todas las fases: comprender la disputa, elegir un criterio de comparación, calcular diferencias o proporciones y volver a la situación para juzgar y justificar la respuesta. Ninguna fase queda hecha por el enunciado. | — |
| 8 | validacion | 2 | El juicio sobre qué tan reñida fue puede contrastarse con evidencia independiente. Sirven la elección anterior (50,9 % vs 49,1 %) u otras elecciones públicas, no usadas para construir la medida. | — |
| 9 | nivel | 2 | El contexto y el lenguaje son comprensibles para 10–12 años. La matemática requerida (restas, porcentajes simples, comparación de cantidades grandes) está dentro de las herramientas esperables en P. | — |
| 10 | autodiferenciacion | 2 | El piso es bajo, porque basta restar votos o porcentajes. El techo admite soluciones más sofisticadas: votos que habría que trasladar para empatar, diferencia relativa o comparación con elecciones anteriores. | — |
| 11 | fecundidad | 2 | Las distintas medidas pueden llevar a conclusiones diferentes y permiten comparar soluciones. Además abren preguntas sobre qué umbral define una elección reñida o cómo cambia el juicio con blancos y nulos. | — |
| 12 | recursos | 2 | La información necesaria está dada o disponible a solicitud (R2, R3), y ningún material indica qué comparación hacer ni revela el criterio de solución. | — |
| | **Total** | **24/24** | | |
