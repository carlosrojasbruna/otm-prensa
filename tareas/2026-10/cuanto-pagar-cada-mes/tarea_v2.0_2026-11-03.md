# ¿Cuánto pagar cada mes: convenio antiguo o nuevo?

Tarea `2026-10-cuanto-pagar-cada-mes-v2` · versión 2 · 2026-10-26 · nivel P · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-10-cuanto-pagar-cada-mes-v2
titulo: '¿Cuánto pagar cada mes: convenio antiguo o nuevo?'
estado: verificada
version: 2
fecha: '2026-10-26'
noticia:
  noticia_id: 2026-10-26-latercera-ley-de-reconstruccion-tesoreria-destaca-que
  medio: La Tercera
  titulo: 'Ley de Reconstrucción: Tesorería destaca que en sus diez primeros días se han realizado 4 mil consultas o simulaciones de convenios'
  fecha: '2026-10-26'
  url: https://www.latercera.com/nacional/noticia/ley-de-reconstruccion-tesoreria-destaca-que-en-sus-diez-primeros-dias-se-han-realizado-4-mil-consultas-o-simulaciones-de-convenios/
  resumen_propio: Tesorería informó que, en los primeros diez días de la nueva ley de reconstrucción, la plataforma de convenios registró miles de simulaciones y casi dos mil acuerdos de pago. Explica que los deudores del CAE podrán pagar en 48 cuotas, sin el tope de ingresos anterior, y estima cuánto dinero y deuda podrían moverse el próximo año.
  cifras_usadas:
  - valor: 48
    unidad: cuotas
    que_es: Número de cuotas del nuevo convenio para deudores del CAE
    localizador:
      fuente: noticia
      ubicacion: párrafo 5
  - valor: 24
    unidad: cuotas
    que_es: Número máximo de cuotas que existía antes de la ley
    localizador:
      fuente: noticia
      ubicacion: párrafo 7
  - valor: 10%
    unidad: de la deuda
    que_es: Porcentaje de deuda pagado al contado como ejemplo de pie
    localizador:
      fuente: noticia
      ubicacion: párrafo 10
nivel_principal: P
variantes:
  abajo: null
  arriba: S
area: economia
contenidos_matematicos:
- proporcionalidad directa
- división y reparto equitativo
- porcentajes simples
- tablas de comparación
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
    nivel: 1
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
Muchas personas pidieron un crédito para estudiar en la educación superior, llamado CAE, y todavía lo están pagando. Tesorería, el organismo del Estado que cobra esas deudas, ofrece convenios de pago: la persona se compromete a pagar su deuda en cuotas mensuales. Antes de una nueva ley, el máximo era de 24 cuotas. Ahora los deudores del CAE pueden elegir un convenio de 48 cuotas. Además, quien quiera puede pagar al contado un pie, por ejemplo el 10% de la deuda, y repartir el resto en cuotas. Imaginen a una persona que tiene una deuda del CAE cuyo monto ustedes eligen como ejemplo. ¿Qué le conviene más a esa persona: el convenio antiguo o el nuevo, con pie o sin pie? Expliquen su decisión. Pueden pedir información adicional.
```

```text foto_descripcion
Ilustración sencilla de un calendario con casillas de meses y, al lado, una alcancía con monedas.
```

### 1.1 Variante hacia abajo

No hay.

### 1.2 Variante hacia arriba (tramo S1)

Se pide además incorporar un interés mensual que el grupo debe buscar o estimar, comparar el total pagado en cada opción y expresar el total como función del plazo y del pie. Se agrega la pregunta de qué pasa si cambia el porcentaje del pie. El contexto es el mismo.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Plazo máximo que existía antes de la ley | Plazo máximo anterior: 24 cuotas. | de_entrada | P1-MRS | noticia, párrafo 7 |
| R2 | Plazo del nuevo convenio para deudores del CAE | Nuevo convenio para deudores del CAE: 48 cuotas. | de_entrada | P1-MRS | noticia, párrafo 5 |
| R3 | Ejemplo de pie al contado | Ejemplo de pie: 10% de la deuda pagado al contado. | de_entrada | P1-MRS | noticia, párrafo 10 |
| R4 | Condiciones simplificadoras del convenio, si el grupo pregunta por intereses o por el monto de las cuotas | Supuesto del escenario: para esta tarea no se consideran intereses ni reajustes, y todas las cuotas de un convenio son del mismo monto. | a_solicitud | P2-RM | supuesto del escenario |
| R5 | Información sobre la situación de la persona, si el grupo pregunta cuánto gana o cuánto puede pagar | Supuesto del escenario: lo que una persona puede pagar cada mes depende de sus ingresos y de sus otros gastos; el grupo puede elegir un ejemplo y justificarlo. No hay un único monto correcto. | a_solicitud | P2-RM | supuesto del escenario |
| R6 | Dato independiente para contrastar después de modelar | Supuesto del escenario: cuando el grupo tenga sus resultados, el docente entrega la cuota que muestra el simulador de convenios de Tesorería para la misma deuda que el grupo eligió, para que la comparen con la suya. | a_solicitud | P6-VAL | supuesto del escenario |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender qué es un convenio, una cuota y un pie, y que deben comparar tres formas de pagar la misma deuda: plazo antiguo, plazo nuevo y plazo nuevo con pie. | El grupo explica con sus palabras qué paga la persona cada mes y por cuánto tiempo, y anota qué quiere saber. | B12 |
| P2-RM Simplificar | Elegir una deuda de ejemplo, acordar si hay o no intereses y definir qué significa que algo le convenga a la persona (cuota baja, menos tiempo endeudada, ingreso). | Lista escrita de supuestos acordados y del criterio de conveniencia elegido. | B23 |
| P3-MM Matematizar | Representar el reparto de la deuda en cuotas iguales, con y sin pie, mediante una tabla o una operación de división. | Tabla o esquema con deuda, pie, plazo y cuota para cada opción. | B34 |
| P4-WM Trabajar | Calcular las cuotas de las tres opciones y el pie, con calculadora o a mano, y revisar que las cuotas sumadas y el pie reconstruyan la deuda. | Cuadro de resultados con las cuotas calculadas y la comprobación de la suma. | B45 |
| P5-INT Interpretar | Interpretar los resultados: la cuota baja con más cuotas pero la persona se endeuda por más tiempo; el pie baja la cuota pero exige dinero hoy. | Recomendación escrita a la persona con una razón que usa los números obtenidos. | B56 |
| P6-VAL Validar | Contrastar la cuota calculada con la que entrega el simulador de Tesorería y explicar las diferencias, por ejemplo intereses u otros cargos. | Comparación anotada entre la cuota del grupo y la del simulador, con una explicación de la diferencia. | B67 |
| P7-EXP Exponer | Presentar la recomendación y el procedimiento en un cartel o una exposición breve a otro grupo. | Cartel o exposición con la deuda elegida, la tabla, la decisión y las limitaciones. | — |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- El grupo elige un monto de deuda de ejemplo y lo justifica como plausible.
- Se ignoran intereses y reajustes (o se acuerda cómo tratarlos).
- Todas las cuotas de un convenio son iguales.
- El pie se paga al contado, de una vez, y el resto se reparte en cuotas.
- El criterio de conveniencia se acuerda en el grupo: cuota mensual baja, tiempo total en deuda o relación con el ingreso.

### Solución de referencia

1) Elegir una deuda de ejemplo, por ejemplo 6 millones de pesos. 2) Convenio antiguo: deuda dividida en 24 cuotas. 3) Convenio nuevo: deuda dividida en 48 cuotas. 4) Nuevo con pie: pie igual al 10% de la deuda; lo que queda se divide en 48 cuotas (y, si se quiere, también en 24). 5) Comparar cuotas y tiempo total. 6) Decidir según el criterio acordado, que depende del ingreso de la persona. 7) Contrastar con el simulador de Tesorería.

**Resultado.** Con una deuda de 6 millones de pesos: 24 cuotas de 250.000 pesos; 48 cuotas de 125.000 pesos; con pie de 600.000 pesos, 48 cuotas de 112.500 pesos (o 24 cuotas de 225.000 pesos). Pasar de 24 a 48 cuotas reduce la cuota a la mitad, pero duplica el tiempo de pago. La opción más conveniente depende de cuánto puede pagar la persona cada mes y de cuánto le pesa estar endeudada más tiempo.

**Rango aceptable.** La cuota es proporcional a la deuda elegida: con el doble de cuotas es la mitad y con pie del 10% es un 10% menor que sin pie. Son defendibles tanto el nuevo convenio sin pie (cuota más baja) como el nuevo con pie (cuota aún menor, pero con pago inicial) o el antiguo (menos tiempo), siempre que se justifique con el ingreso y los números.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Tabla de cuotas por opción | P | Cuota = deuda dividida en el número de cuotas, calculada para cada opción y ordenada en una tabla. | Para 6 millones de pesos: 250.000, 125.000 y 112.500 pesos por mes, según la opción. |
| R2 | Razonamiento proporcional | P | Al duplicar las cuotas, la cuota se reduce a la mitad; el pie quita un décimo de la deuda y reduce la cuota en ese mismo décimo. | La cuota nueva es la mitad de la antigua; con pie es nueve décimos de la cuota nueva. |
| R3 | Gráfico de barras de pagos mensuales | P | Barras con la cuota y la duración de cada opción, para ver la relación entre cuota y tiempo (área igual a la deuda). | Barras altas y cortas para el convenio antiguo, bajas y largas para el nuevo; el área total es igual a la deuda, salvo el pie. |
| R4 | Cuota como fracción del ingreso | S1 | Cuota = (1 − p) · D / n, comparada con una fracción del ingreso mensual elegido para decidir qué plan es sostenible. | Se elige el plan cuya cuota queda bajo la fracción del ingreso que el grupo considera razonable. |

### Modelo inadecuado (R5)

Concluir que más cuotas siempre conviene porque la cuota mensual es menor. Falla porque ignora que la persona está endeudada el doble de tiempo, que el criterio depende de la capacidad de pago y que en la realidad puede haber intereses; mirar solo la cuota no responde qué le conviene a esa persona.

### Evidencia de validación (independiente del modelo)

Después de modelar, el grupo recibe la cuota que muestra el simulador de convenios de Tesorería para la misma deuda elegida y la compara con la suya; además verifica que cuotas por número de cuotas más el pie reconstruyan la deuda. Las diferencias permiten discutir intereses y otros cargos que el modelo ignoró.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | La tarea plantea una necesidad de decisión real y no entrega ninguna regla ni modelo. El criterio de conveniencia, como la capacidad de pago o el total pagado, debe construirlo el grupo. | — |
| 2 | abierta | 2 | La pregunta no prescribe procedimiento y admite varios caminos defendibles. Según el monto, los ingresos supuestos y el criterio elegido, se puede llegar a distintas conclusiones. | — |
| 3 | decisiones | 2 | Resolver exige suponer el monto de la deuda y la capacidad de pago, decidir si considerar intereses y definir qué significa «convenir». Son decisiones de modelación sustantivas. | — |
| 4 | realismo | 2 | La situación de elegir un convenio de pago de una deuda CAE con o sin pie existe fuera de la escuela. | — |
| 5 | autenticidad | 2 | Las condiciones reales del convenio (24 y 48 cuotas, el pie) y el simulador de Tesorería del R6 son componentes extraescolares no creados para enseñar. Están integrados como núcleo de la tarea. | — |
| 6 | contexto | 2 | El contexto condiciona las decisiones, porque la conveniencia depende de la situación de la persona. Además es necesario para interpretar el resultado: la misma cuota puede ser conveniente o no según el caso. | — |
| 7 | ciclo | 2 | Responder obliga a comprender la situación, simplificar (monto, intereses, capacidad de pago), calcular las cuotas, interpretar cuál conviene y contrastar con el simulador. El enunciado no deja hecha ninguna fase; las simplificaciones solo se entregan si el grupo las solicita. | — |
| 8 | validacion | 2 | Existe evidencia independiente, no usada en la construcción del modelo, para contrastar la cuota calculada. Esa comparación también permite ver los límites del supuesto sin intereses. | — |
| 9 | nivel | 1 | La matemática (división y 10%) está al alcance de las herramientas del nivel P. Sin embargo, un crédito universitario, los convenios con Tesorería y el «pie al contado» son comprensibles pero poco significativos para estudiantes de 10 a 12 años. Hay duda entre 1 y 2, y se asigna el menor. | — |
| 10 | autodiferenciacion | 2 | El piso es bajo: basta elegir un monto redondo y dividir. La tarea admite además soluciones más sofisticadas, como comparar varios montos, relacionar la cuota con ingresos y gastos, variar el pie o generalizar un criterio. | — |
| 11 | fecundidad | 2 | Los grupos que eligen montos e ingresos distintos pueden comparar soluciones. El contraste con el simulador abre preguntas nuevas, como por qué la cuota real difiere, el efecto de los intereses y cuánto pie conviene. | — |
| 12 | recursos | 2 | La información necesaria está en el enunciado o puede solicitarse (R4, R5, R6). Los datos de monto e ingreso los elige el grupo, y ningún material revela cómo decidir qué conviene. | — |
| | **Total** | **23/24** | | |
