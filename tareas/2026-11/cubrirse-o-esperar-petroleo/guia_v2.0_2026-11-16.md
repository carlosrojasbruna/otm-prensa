# Guía docente · ¿Cerrar el precio hoy o esperar al barril de mañana?

Tarea `2026-11-cubrirse-o-esperar-petroleo-v2` · guía versión 2 · 2026-11-16. Licencia CC BY-NC-SA 4.0. Generado desde `guia` (JSON, fuente de verdad).

## 0. Ficha

| Campo | Valor |
|---|---|
| Título | ¿Cerrar el precio hoy o esperar al barril de mañana? |
| Noticia | La Tercera, «Precio del petróleo registra otra fuerte caída y el barril se aleja cada vez más de los US$ 100», 2026-11-09, https://www.latercera.com/pulso/noticia/precio-del-petroleo-registra-otra-fuerte-caida-y-el-barril-se-aleja-cada-vez-mas-de-los-us-100/ |
| Nivel principal | U |
| Variantes | S |
| Contenidos | procesos estocásticos discretos y caminata aleatoria; distribución lognormal y cuantiles; estimación de volatilidad; simulación Monte Carlo; decisión bajo incertidumbre |
| Tiempo | 2 sesiones de 90 min |
| Puntaje RUB01 | 24/24 |
| Versión y fecha | v2 · 2026-11-16 |
| Cambios | rev. 2 de la guía: correcciones de texto de la revisión humana 2 (Carlos Rojas Bruna): rutas y diferencias por corrida en E1 y E3, correspondencia de E3 con R1 y decisiones de E4 |

## 1. Meta de la clase (C1)

Observar si el grupo convierte la pregunta de la empresa importadora (cerrar el precio hoy o esperar) en un modelo que trata el precio del Brent como incierto, con supuestos explícitos y un criterio propio de riesgo, y si condiciona la recomendación al costo de la cobertura y a la volatilidad supuesta. Interesa especialmente cómo tratan la caída de un solo día de crisis como dato para estimar la variabilidad, y si contrastan el modelo con la evolución posterior del precio.

**Contenido.** Procesos estocásticos discretos y caminata aleatoria, distribución lognormal y cuantiles, estimación de volatilidad, simulación Monte Carlo y decisión bajo incertidumbre.

**Subcompetencias de modelación.**

- Comprender la situación y distinguir los datos de la noticia que sirven de los que faltan (costo de cobertura, variabilidad típica), P1-MRS
- Simplificar: tratar el precio como variable aleatoria, fijar el horizonte en días hábiles, decidir qué se ignora (tipo de cambio, deriva, saltos) y definir un criterio de riesgo, P2-RM
- Matematizar: elegir entre escenarios, caminata lognormal, reversión a la media o regímenes de tensión y calma, y estimar la volatilidad con pocos datos, P3-MM
- Trabajar el modelo: obtener rango, cuantiles, costo esperado y cola de riesgo, de forma analítica o por simulación, P4-WM
- Interpretar los resultados como una recomendación condicionada al costo de cobertura y a la aversión al riesgo, P5-INT
- Validar contra la trayectoria posterior del Brent y criticar la volatilidad estimada con solo un día extremo, P6-VAL
- Comunicar al gerente separando lo estimado de lo supuesto, P7-EXP

**Meta social.** Trabajo cooperativo en grupos pequeños: justificar oralmente cada supuesto ante los compañeros y llegar a una recomendación común, aceptando que grupos distintos pueden recomendar cosas distintas si su razonamiento es explícito.

**Evidencia que se recoge.**

- Lista escrita de supuestos con su justificación y criterio de riesgo explícito (P2-RM)
- Expresión matemática del precio a un mes, con cada parámetro y su fuente (P3-MM)
- Hoja de cálculo o código con la distribución del precio y la comparación de costos entre cubrir y esperar (P4-WM)
- Recomendación condicionada, redactada en lenguaje del gerente (P5-INT)
- Registro de la comparación entre el precio observado y el intervalo del modelo, con los ajustes que el grupo hace y su explicación (P6-VAL)
- Informe o exposición de una página que separa lo estimado de lo supuesto y señala los límites del modelo (P7-EXP)

## 2. Análisis a priori del espacio de soluciones (C2)

### Rutas

| Ruta | Nombre | Nivel | Modelo |
|---|---|---|---|
| R1 | Escenarios discretos | S2 | Tres escenarios para el precio del Brent a un mes (vuelve al nivel anterior a la caída, se mantiene, sigue bajando) con movimientos de tamaño dado por el porcentaje de la noticia; comparación de costo en cada uno con y sin cobertura. |
| R2 | Caminata aleatoria lognormal | U | ln(S_T) = ln(S_0) + mu*T + sigma*raíz(T)*Z con sigma estimada a partir de datos diarios y deriva cero. |
| R3 | Reversión a la media | U | Proceso de Ornstein-Uhlenbeck sobre el logaritmo del precio, con nivel de largo plazo cercano al precio de comienzos de año (como máximo unos 61,7 dólares por barril, obtenido de 93,74/1,52, porque el alza es de más de 52%) y velocidad de reversión supuesta. |
| R4 | Regímenes de tensión y calma | U | Cadena de Markov de dos estados con volatilidades distintas y probabilidades de transición supuestas; simulación Monte Carlo del precio a un mes. |

### Modelo inadecuado (R5)

Extrapolar la caída diaria de 4,67% durante un mes compuesto (93,74*0,9533^21 ≈ 34 dólares por barril) o prolongar linealmente el alza anual de más de 52% trata un movimiento extremo de un día o un acumulado de diez meses como una tendencia estable. Conduce a precios absurdos, ignora la incertidumbre y no sirve para decidir si cubrirse.

### Solución de referencia

1) Con la caída diaria del Brent de 4,67% se toma una volatilidad diaria extrema cercana a 4,7%. Como es un día de crisis, un valor de calma más razonable es cercano a 2%. 2) Para un mes (unos veintiún días hábiles) la volatilidad mensual es sigma*raíz(21): cerca de 21,4% (caso extremo) o 9,2% (caso calmo). 3) Con deriva cero y precio lognormal, el intervalo central de 90% a un mes es 93,74*exp(±1,645*sigma_mensual): aproximadamente entre 66 y 133 dólares por barril (caso extremo) o entre 81 y 109 (caso calmo). 4) El costo esperado de esperar es cercano al de cubrir si la cobertura es justa; la decisión depende del costo de la cobertura y del riesgo tolerable. Como referencia, el valor de una cobertura tipo opción en el precio actual es aproximadamente 0,4*sigma_mensual*93,74, es decir cerca de 3,4 a 8,0 dólares por barril. 5) Se recomienda cubrir si el costo de cobertura es menor que ese orden de magnitud o si el exceso sobre el precio tolerable tiene probabilidad apreciable; esperar si la cobertura es cara. 6) Contrastar con la trayectoria real posterior del precio del Brent. Resultado: Recomendación condicionada: cubrir si el costo de la cobertura queda por debajo de aproximadamente 3 a 8 dólares por barril (según la volatilidad supuesta) o si la empresa no tolera un precio del orden de 109 a 133 dólares por barril; esperar en caso contrario. Rango de precio a un mes: entre 66 y 133 dólares por barril con volatilidad extrema, y entre 81 y 109 con volatilidad moderada.

**Rango aceptable.** Se aceptan recomendaciones distintas (cubrir o esperar) si dependen explícitamente de la volatilidad estimada, del costo de cobertura y del criterio de riesgo, con un rango de precio a un mes coherente con una volatilidad diaria de entre 2% y 4,7%. No se acepta una proyección determinista única sin incertidumbre.

### Barreras anticipadas por fase

| Fase | Barrera |
|---|---|
| P1-MRS | Los estudiantes pueden quedarse con las cifras de la noticia (caída de 4,67%, 93,74 dólares por barril, alza anual de más de 52%) y no ver que el problema es una decisión con precio futuro incierto a un mes. Es probable que no noten que faltan el costo de la cobertura y las condiciones de pago, y que no pidan esa información (B12). |
| P2-RM | Cuesta pasar de la situación a un problema matemático: tratar el precio como variable aleatoria, fijar el horizonte en días hábiles y decidir qué ignorar (tipo de cambio, almacenamiento, deriva). Suele faltar un criterio de riesgo propio de la empresa; sin él, el grupo no sabe qué calcular y la comparación entre cubrir y esperar queda vacía (B23). |
| P3-MM | Hay un modelo inadecuado muy tentador: extrapolar la caída diaria de 4,67% durante todo el mes, o prolongar el alza anual de más de 52%. Ambos tratan un movimiento extremo de un día, o un acumulado de varios meses, como tendencia estable y dan precios absurdos sin incertidumbre. Además, estimar la volatilidad con un único día de crisis obliga a decidir qué valor de calma usar, y esa decisión suele dejarse implícita (B34). |
| P4-WM | Aun con un modelo bien elegido, el paso a cuantiles, costo esperado y cola de riesgo exige manejar la lognormal o programar una simulación. Es frecuente confundir la volatilidad diaria con la del horizonte completo, o mezclar el costo esperado con el riesgo, y concluir que cubrir y esperar son equivalentes (B45). |
| P5-INT | Los grupos tienden a entregar un número o un intervalo sin decir qué hacer. Les cuesta pasar a una recomendación condicionada al costo de la cobertura y a la tolerancia al riesgo, y explicar cómo cambia con la volatilidad supuesta; también pueden dar una respuesta única y absoluta (B56). |
| P6-VAL | Un solo precio observado un mes después no confirma ni refuta el modelo. El riesgo es leer que 'acertó' o 'falló' sin discutir la volatilidad estimada con un único día extremo, sin comparar modelos alternativos y sin ajustar de forma justificada (B67). |
| P7-EXP | Mezclar en el informe lo estimado con lo supuesto, de modo que el gerente no distinga qué parte descansa en datos y qué parte en decisiones del grupo, y omitir los límites del modelo. |

## 3. Organización (C3, C4, C7)

| Momento | Tiempo | Qué hacen los estudiantes | Qué hace el docente |
|---|---|---|---|
| Comprensión y trabajo grupal (sesión 1: P1-MRS a P3-MM) | 80 min | Leen el enunciado, parafrasean la decisión de la empresa y listan los datos útiles y los que faltan. Piden los recursos que necesiten (costo de cobertura, condiciones de pago). Escriben supuestos con su justificación y un criterio de riesgo. Eligen un modelo y estiman sus parámetros dejando por escrito la fuente de cada uno. | Presenta la situación sin resolverla. Circula y diagnostica: pregunta qué han hecho y por qué, y registra qué ruta sigue cada grupo (escenarios, caminata lognormal, reversión a la media o regímenes) y dónde se traban. No interviene aún con ayudas; entrega los recursos a solicitud solo cuando el grupo los pide. |
| Cierre de la sesión 1 | 10 min | Dejan por escrito su lista de supuestos, el criterio de riesgo y el modelo elegido, y anotan qué cálculo harán en la sesión siguiente. | Recoge las hojas de supuestos para leerlas antes de la sesión 2. Selecciona qué contrastes de modelo conviene exponer en la puesta en común. |
| Comprensión y trabajo grupal (sesión 2: P4-WM y P5-INT) | 35 min | Retoman su modelo, calculan rango, cuantiles, costo esperado y cola de riesgo (analítica o por simulación) y comparan los costos de cubrir y esperar. Redactan una recomendación condicionada al costo de cobertura y a la volatilidad supuesta. | Circula y diagnostica con preguntas sobre lo hecho (qué parámetro usaron, cómo definieron el riesgo). Anota los bloqueos B45 y B56 que observa y no corrige resultados en este momento. |
| Puesta en común | 20 min | Algunos grupos con rutas distintas presentan brevemente su modelo, sus supuestos y su recomendación. Comparan en qué se parecen y en qué difieren las recomendaciones y por qué. | Modera y ordena la comparación entre rutas. Pide que cada grupo justifique la volatilidad usada y el criterio de riesgo. No declara cuál recomendación es correcta. |
| Validación y cierre | 35 min | Solicitan la evolución posterior del precio, la obtienen de la serie diaria de la EIA y comparan el precio observado con el intervalo de su modelo. Discuten qué ajustarían (volatilidad o modelo) y por qué. Entregan un informe o exposición de una página que separa lo estimado de lo supuesto. | Entrega el recurso de contraste solo cuando el modelo está construido. Plantea la discusión sobre los límites de validar con un único precio observado y con volatilidad estimada de un día extremo. Cierra recogiendo qué decisiones de modelación tomaron los grupos. |

**Agrupamiento.** Grupos pequeños de trabajo cooperativo, que se mantienen en las dos sesiones, para favorecer la discusión de supuestos y la autonomía en la elección del modelo.

**Roles.** Dentro de cada grupo, rotar entre quien lleva el registro escrito de supuestos y parámetros, quien hace los cálculos o la simulación y quien verbaliza ante el docente y el curso qué se ha decidido y por qué. Quien verbaliza debe poder explicar el modelo sin leer las fórmulas.

**Producciones que se registran.**

- Hoja de supuestos con justificación y criterio de riesgo
- Expresión matemática del modelo con la fuente de cada parámetro
- Hoja de cálculo o código con la distribución del precio y la comparación entre cubrir y esperar
- Recomendación condicionada para el gerente
- Registro de la contrastación con el precio observado y de los ajustes realizados
- Informe o exposición de una página que separa lo estimado de lo supuesto

**Tecnología.** Se permite hoja de cálculo o código para los cálculos y la simulación Monte Carlo en P4-WM, y para ordenar los datos de contraste en P6-VAL. La serie diaria de la EIA se consulta solo en P6-VAL, una vez construido el modelo. La tecnología no decide por el grupo: elegir el modelo, estimar la volatilidad y definir el criterio de riesgo (P2-RM y P3-MM) se hace sin herramientas automáticas que propongan o ejecuten esas decisiones.

## 4. Escenarios simulados (C2, C6)

Derivados de las trazas del simulador; cada escenario cita las corridas que lo respaldan.

### E1 · ruta esperada

| Campo | Valor |
|---|---|
| Corridas | N3_AA_r1, N4_AA_r1 |
| Perfil del grupo | N3_AA_r1: tramo U, nivel N3, estilo AA. N4_AA_r1: tramo U, nivel N4, estilo AA. Ruta: la de N3_AA_r1; N4_AA_r1 siguió P3-MM → P2-RM → P4-WM → P5-INT → P4-WM → P5-INT → P7-EXP (no pasa por P1-MRS ni por P6-VAL). |
| Ruta observada | P1-MRS → P3-MM → P2-RM → P4-WM → P6-VAL → P5-INT → P4-WM → P7-EXP → P6-VAL |
| Supuestos que emergieron | precio lognormal (P₁ = P₀·e^X con X normal); volatilidad anual 40%, con sensibilidad 30% y 50% (N3_AA_r1); precio esperado a un mes igual al actual (sin tendencia); se ignoran la caída diaria de 4,67% y el alza anual de 52% (N3_AA_r1); volatilidad 60% anual por semana brusca (N4_AA_r1); sin saltos por Medio Oriente (N4_AA_r1) |
| Modelo al que llegaron | lognormal |
| Dónde se trabaron y cómo se destrabaron | sin bloqueos |

**Qué aprende el curso.** Es el escenario más cercano a la ruta R2: precio lognormal, deriva cero, cola superior como medida de riesgo y recomendación condicionada al costo de la cobertura y a la pérdida tolerable. Al compararlo con los demás, el curso ve que la sensibilidad a la volatilidad (probar varios valores) reemplaza a un único número inventado. También deja una pregunta abierta para discutir: en las dos corridas la volatilidad se supone en vez de estimarse a partir del movimiento diario de la noticia. N3_AA_r1 declara que no usa la caída de 4,67%; N4_AA_r1 sí la toma en cuenta, pero solo de forma cualitativa: repite la cuenta con 60% porque, con una semana tan brusca, el 40% podría quedarse corto. Contrastar ambas decisiones con la ruta de referencia, que trata ese día como observación extrema y lo compara con un valor de calma.

**Extracto de diálogo simulado.**

> **Fran:** Sí, me parece, pero ojo que comparar solo con E[P₁] no basta, porque el riesgo está en la cola. Yo supondría P₁ = P₀·e^X con X normal y pediría la volatilidad y el costo c como información adicional, ¿tienes idea de qué volatilidad anual usar?  
> **Cami:** Yo diría que podemos suponer una volatilidad anual como 40%, que para petróleo en una semana tan movida no suena exagerada, y pasarla a un mes: σ_mes = 0,40·√(1/12) ≈ 0,115. Así el precio a un mes tendría una desviación de más o menos 11,5%, o sea unos 10,8 dólares por barril, ¿te cuadra?  
> **Fran:** DE ACUERDO. Solo un detalle: el 4,67% y el 52% anual no los usamos, pero no cambian la recomendación porque el supuesto es que el precio sigue una caminata sin tendencia.  

### E2 · bloqueo en matematizar

| Campo | Valor |
|---|---|
| Corridas | N1_AA_r1 |
| Perfil del grupo | Tramo U, nivel N1, estilo AA. |
| Ruta observada | P1-MRS → P4-WM → P3-MM → P2-RM → P4-WM → P3-MM → P5-INT → P4-WM → P6-VAL → P7-EXP |
| Supuestos que emergieron | el precio no baja igual todos los días; variación de ±10% del precio en un mes; costo de cobertura de 2 dólares por barril; 100.000 barriles como ejemplo |
| Modelo al que llegaron | escenarios discretos |
| Dónde se trabaron y cómo se destrabaron | B23: Resolución entre pares (peer). El grupo no sabe cómo pasar del movimiento de un día a un mes; Cami esboza multiplicar la caída diaria por los días del mes y ella misma lo descarta porque supondría que el precio baja todos los días. Fran propone pedir el dato de variación mensual en lugar de inventar una fórmula, y Cami destraba el avance con un supuesto provisorio de ±10% para seguir calculando mientras llega la información. |

**Qué aprende el curso.** Muestra el modelo inadecuado (extrapolar el movimiento de un día durante todo el mes) asomándose y siendo rechazado por los propios estudiantes. Comparado con E1, el curso ve que, sin una herramienta para escalar la variabilidad en el tiempo, el grupo cae en un rango fijo supuesto y en escenarios sin probabilidades. Aun así, el grupo declara explícitamente que sus supuestos son inventados y condiciona la recomendación a la pérdida tolerable.

**Extracto de diálogo simulado.**

> **Fran:** Mmm, no sé si nos sirve mucho para decidir, pero al menos nos dice cuánto se mueve en un día: 4,59 dólares. Si eso se repitiera todos los días, en un mes ¿no podría moverse un montón? ¿Cómo calculamos eso?  
> **Cami:** Podríamos hacer 4,59 × 30 = 137,7, pero eso supone que baja todos los días, y no creo que sea así. ¿Habrá alguna fórmula para la variación en un mes, o pedimos algún dato de cuánto suele variar?  
> **Fran:** Yo creo que mejor pedimos el dato de cuánto suele variar al mes, porque inventar una fórmula sin eso nos va a salir mal. Y también el costo de la cobertura y cuántos barriles compra, así podemos comparar los dos casos con números.  
> **Cami:** Ya, pidamos esos tres datos: volatilidad mensual, costo de la cobertura y barriles. Mientras tanto, supongamos algo para probar, por ejemplo que el precio varía ±10% en un mes: 93,74 × 0,10 ≈ 9,37 dólares por barril, ¿te parece?  

### E3 · escenarios con números inventados

| Campo | Valor |
|---|---|
| Corridas | N2_VV_r1, N1_VV_r1 |
| Perfil del grupo | N2_VV_r1: tramo U, nivel N2, estilo VV. N1_VV_r1: tramo U, nivel N1, estilo VV. Ruta: la de N2_VV_r1; N1_VV_r1 siguió P1-MRS → P2-RM → P4-WM → P6-VAL → P5-INT → P6-VAL → P5-INT → P7-EXP (pasa dos veces por P6-VAL y omite P3-MM). |
| Ruta observada | P1-MRS → P2-RM → P3-MM → P4-WM → P5-INT → P7-EXP |
| Supuestos que emergieron | rango de precio a un mes entre 80 y 110 US$/barril (inventado); cargamento de 10.000 barriles (provisorio); costo de cobertura de 1 US$/barril (provisorio); 110 como peor caso y 80 como caso bueno; la tensión en Medio Oriente puede volver y hacer más probable el alza; variación de ±10 dólares por barril en un mes |
| Modelo al que llegaron | escenarios discretos |
| Dónde se trabaron y cómo se destrabaron | sin bloqueos |

**Qué aprende el curso.** Se aproxima a la ruta R1 sin corresponder del todo: R1 arma tres escenarios con movimientos del tamaño del porcentaje de la noticia, y aquí hay un caso bueno y un caso malo dibujados a partir de un rango imaginado (80 y 110 en N2_VV_r1; ±10 dólares en N1_VV_r1), sin probabilidades. Al compararlo con E1 y E4, el curso discute que la recomendación depende de dónde salen los extremos del rango: aquí el grupo reconoce que el peor caso lo inventó y que podría ser peor. La ruta de N2_VV_r1 no pasa por validar. La de N1_VV_r1 sí: el grupo corrige un error de cálculo (un millón por cien mil) y contrasta su salto de 10 dólares con la caída de 4,67% en un día. La diferencia permite preguntar qué faltaría para contrastar el rango de N2_VV_r1.

**Extracto de diálogo simulado.**

> **Fran:** Sí, dibujémoslo. [dibujo: una línea horizontal con el 93,74 marcado al medio, y a los lados 80 y 110 como los extremos posibles]. Pero ¿de dónde sacamos que son 80 y 110? ¿No habría que pedir cuánto suele variar el precio en un mes?  
> **Cami:** Tienes razón, esos números me los imaginé yo, no están en la tarea. Podríamos pedir la volatilidad mensual del Brent, y también cuánto cobra el banco por la cobertura y cuántas lucas de pérdida aguanta la empresa.  
> **Cami:** Sí, la balanza queda pareja, así que me inclino a cubrir si la empresa no aguanta perder unos 150 mil dólares, porque la tensión puede volver y el 110 podría ser peor. Pero como usamos números inventados, la seguridad es baja, ¿lo escribimos así en la recomendación?  

### E4 · normal con riesgo sesgado al alza

| Campo | Valor |
|---|---|
| Corridas | N4_VV_r1 |
| Perfil del grupo | Tramo U, nivel N4, estilo VV. |
| Ruta observada | P1-MRS → P2-RM → P3-MM → P4-WM → P5-INT → P4-WM → P6-VAL → P7-EXP → P6-VAL |
| Supuestos que emergieron | volatilidad anual de 40% (inventada); volatilidad escala con raíz del tiempo (40%/√12); distribución normal de la variación del precio; intervalo de dos desviaciones estándar como escenario malo; riesgo sesgado al alza si vuelve la tensión en Medio Oriente; al importador solo le perjudica la subida del precio |
| Modelo al que llegaron | normal (caminata aleatoria) |
| Dónde se trabaron y cómo se destrabaron | sin bloqueos |

**Qué aprende el curso.** Usa una caminata aleatoria con distribución normal en vez de lognormal y razona sobre la asimetría del riesgo para un importador. Comparado con E1, el curso puede discutir si una normal simétrica es adecuada para un precio y por qué el grupo dibuja el abanico más largo hacia arriba. Además lleva más lejos dos ideas que también asoman en N4_AA_r1 (E1), que recomienda cubrir al menos una parte del cargamento y pide el tipo de cobertura: aquí el grupo propone cubrir cerca de la mitad como punto de partida y explica por qué importa si la cobertura es forward u opción (con un forward, si el precio baja, igual se paga lo fijado).

**Extracto de diálogo simulado.**

> **Fran:** Ojo que ese ±11,5% es una sola desviación estándar, o sea cubre como 68% de los casos; con dos serían unos 72 a 116 dólares. Y como la tensión en Medio Oriente puede volver, dibujaría el abanico más largo hacia arriba, que es justo donde le duele a un importador.  
> **Fran:** Agreguemos preguntar si la cobertura es un forward o una opción, porque con forward, si el precio baja a 72, igual pagas lo fijado y pierdes ese ahorro. Y que nos den la volatilidad real del mercado, no la que nos inventamos.  
> **Cami:** DE ACUERDO. Solo agregaría una nota: la confianza es media porque los 72 a 116 salen de una volatilidad que inventamos, así que si la real es mucho mayor, cubrimos más.  


Tabla agregada de bloqueos (6 grupos simulados):

| Transición | Grupos que se trabaron | % |
|---|---|---|
| B23 | 1/6 | 17 % |

## 5. Intervenciones graduadas por bloqueo anticipado (C5, C6)

La ayuda mínima primero; diagnosticar antes de intervenir. Ninguna ayuda entrega la regla.

| Bloqueo | Z1–Z2 motivación / retroalimentación | Z3 estratégica general | Z4 estratégica de contenido | Z5 contenido (último recurso) |
|---|---|---|---|---|
| B12 | Pregunten: «¿Con sus palabras, qué tiene que decidir la empresa y para cuándo? ¿Qué datos de la noticia usarían y cuáles les faltan?». Reconozcan lo que ya identificaron antes de añadir nada. | Pidan que separen en dos listas lo que la noticia dice y lo que necesitarían saber para decidir, y que hagan un dibujo simple de hoy y de dentro de un mes. | Pregunten: «¿Qué le preocupa al gerente: el precio de hoy o el que habrá el día de la compra? ¿Qué información pedirían para comparar las dos opciones?». | Ofrezcan los recursos a solicitud: el R2 (costo de la cobertura) y el R3 (condiciones de pago). Que el grupo diga qué cambia en su lista de datos útiles. No sugieran ningún modelo. |
| B23 | Diagnostiquen preguntando: «¿Qué han intentado para pasar del movimiento de un día al de un mes? ¿Qué no los convence de eso?». Si el grupo ya descartó algo, reconózcanlo, como hizo Cami en E2 al rechazar repetir la caída todos los días. | Propongan escribir en una lista qué cosas del precio saben y cuáles son supuestos, y probar con un dibujo cómo se vería el precio en un mes si no se mueve igual cada día. | Pregunten: «Si el precio no baja igual todos los días, ¿qué dato de variación mensual les serviría y dónde podrían conseguirlo? ¿Cómo cambia la incertidumbre entre un día y un mes?». Así el grupo orienta su búsqueda sin recibir la fórmula. | Como último recurso, sugieran lo que destrabó a E2: fijar un valor provisorio de variación mensual, declararlo como supuesto inventado y seguir calculando mientras piden el dato. Al terminar, que lo revisen con otros valores. No entreguen cómo se escala la variabilidad ni el resultado. |
| B34 | Pregunten: «¿Qué modelo tienen en mente para el precio a un mes y de dónde sale cada número que usan?». Escuchen antes de sugerir. | Pidan que escriban en una línea qué cantidad desconocida quieren calcular y qué parámetros necesitan, marcando cuáles tienen y cuáles faltan. | Pregunten: «¿Cómo tratarían el día de la caída fuerte: como lo normal o como algo extremo? ¿Qué valor usarían en una semana calmada y cómo comprobarían si cambia su conclusión?». | Sugieran probar más de un valor para el parámetro incierto y comparar las conclusiones, como hizo E1 con sus distintas volatilidades. No indiquen el valor ni la expresión del modelo. |
| B56 | Pregunten: «¿Qué le dirían hoy al gerente con lo que tienen? ¿Qué parte de su resultado cambia si cambian los supuestos?». | Pidan que redacten la recomendación en una frase, como si el gerente no supiera de matemática, y que subrayen de qué depende. | Pregunten: «¿Hasta qué costo de cobertura les convendría pagar, según el riesgo que puede soportar la empresa? ¿Y si la variabilidad del precio fuera mayor?». | Muestren la estructura de una recomendación condicionada, del tipo «cubrir si el costo es menor que…, de lo contrario esperar», y pidan que ellos completen la condición. No den el valor ni la conclusión. |
| B67 | Pregunten: «¿Cómo sabrían si su rango para el precio a un mes fue razonable? ¿Qué evidencia no han usado todavía?». | Pidan que anoten qué esperarían ver si el modelo fuera bueno y qué los haría desconfiar de él. | Pregunten: «Si el precio observado queda fuera de su intervalo, ¿qué revisarían primero: la volatilidad supuesta o el tipo de modelo?». | Ofrezcan el recurso a solicitud R4: la serie diaria de la EIA, que consultan solo una vez construido el modelo. Que comparen el precio observado con su intervalo y expliquen qué ajustarían. No digan si el modelo acertó. |

## 6. Puesta en común: orquestar soluciones múltiples (C8)

### Selección y orden

1. Primero E3 (escenarios con números inventados): monitorear y partir de lo más accesible. Muestra un rango dibujado sin probabilidades y el propio grupo admite que los extremos son imaginados. Anticipa la discusión sobre de dónde salen los números.
2. Segundo E2 (bloqueo en matematizar): seleccionar un caso que hace visible el bloqueo B23. Aquí aparece y se rechaza la extrapolación del movimiento de un día a todo el mes. Conecta con E3: en ambos se usan supuestos provisorios y declarados.
3. Tercero E4 (normal con riesgo sesgado al alza): secuenciar hacia un modelo con incertidumbre explícita. Permite discutir la asimetría del riesgo para un importador, la normal frente al precio y las decisiones de cubrir solo una parte y de preguntar si la cobertura es forward u opción.
4. Cuarto E1 (ruta esperada): conectar con la ruta de caminata aleatoria lognormal. Se ve cómo la sensibilidad a la volatilidad reemplaza a un único número. Se deja abierta la decisión de suponer la volatilidad en lugar de estimarla con el movimiento diario de la noticia. El docente no parte de su propia ruta: llega a ella después de comparar las de los grupos.

### Preguntas

- ¿Qué supuestos hizo cada grupo y cuáles son inventados y cuáles vienen de la tarea?
- ¿Por qué ningún grupo proyectó la caída de un día durante todo el mes? ¿Qué pasaría si lo hicieran?
- ¿Qué pasa con la recomendación si cambia la volatilidad supuesta? ¿Qué grupo probó varios valores?
- ¿Es adecuada una distribución simétrica para un precio? ¿Por qué dibujar el abanico más largo hacia arriba?
- ¿Cómo definió cada grupo el riesgo que la empresa puede soportar y cómo cambia su recomendación según ese criterio?
- ¿Qué grupo pasó por validar y cuál no? ¿Qué faltaría para contrastar un rango con la realidad?
- ¿Qué diferencia hay entre decir «cubrir» a secas y decir «cubrir si el costo es menor que cierto valor»?
- ¿Qué tan segura es la recomendación de cada grupo y qué la hace más o menos segura?

### Contraste con la evidencia independiente

Pidan a cada grupo que, después de presentar su intervalo y sus supuestos, consulte la serie diaria de precios spot del Brent de la EIA (recurso a solicitud R4), que no usaron para construir el modelo. Que miren si el precio observado un mes después de la fecha de la noticia cae dentro de su intervalo. Que revisen si la variabilidad realizada de esas semanas es compatible con la volatilidad que supusieron o estimaron. Si el precio cae fuera, que expliquen si ajustarían la volatilidad o el tipo de modelo. Hagan notar que los grupos con supuestos inventados (E2, E3, E4) y el que supuso la volatilidad (E1) tienen aquí la prueba de si esos supuestos eran razonables. No agreguen datos fuera de la serie ni de la tarea.

## 7. Evaluación del trabajo del estudiante

Pendiente en PLT02 v0.1 (rúbrica por fase del ciclo); esta versión de la guía no la incluye.

## 8. Variantes y continuidad (P3, C9)

**Uso de variantes.** Variante hacia abajo (S2): úsese si el grupo no maneja distribución lognormal, cuantiles ni simulación, o si se aplica en secundaria alta. El grupo define sus propios escenarios (por ejemplo, el precio vuelve al nivel anterior a la caída, se mantiene o sigue bajando) y usa el porcentaje de caída de la noticia como tamaño de los movimientos. Se pide la diferencia de costo entre cubrir y esperar en cada escenario y un criterio informal de riesgo; no se exige estimar volatilidad ni construir una distribución. La validación consiste en comparar con el precio observado un mes después. Corresponde a la ruta de escenarios discretos y obliga a que la decisión final dependa de supuestos del grupo, porque sin probabilidades no hay decisión única. Variante hacia arriba: no existe (es null) y no debe improvisarse una; si el grupo avanza rápido, la profundización natural dentro de la tarea es comparar rutas de nivel universitario (reversión a la media, regímenes de tensión y calma) y criticar la sensibilidad de cada una.

**Acostumbramiento.** Si el grupo nunca ha modelado, conviene una actividad previa breve con otra decisión bajo incertidumbre en la que deban escribir supuestos, justificar qué ignoran y definir su propio criterio de riesgo, sin buscar aún un cálculo exacto. Si el grupo no ha usado hoja de cálculo o código para simular, practicar eso antes con un ejemplo sencillo y ajeno a esta tarea. Esta tarea, por su duración de dos sesiones y su exigencia en estimación de volatilidad y simulación, no sirve como primer contacto con el ciclo de modelación en nivel universitario: funciona mejor como parte de una secuencia, después de al menos una tarea de iniciación. Con la variante hacia abajo puede servir como iniciación en secundaria alta.

**Tarea siguiente.** No definida.

## 9. Materiales

| Material | Archivo |
|---|---|
| tarea_pdf | tarea.pdf |
| recursos_tarjetas | recursos.pdf |
| notebook | escenarios.ipynb |
| icono | icono.svg |

## 10. Trazabilidad

| Paso | Registro |
|---|---|
| Noticia | https://www.latercera.com/pulso/noticia/precio-del-petroleo-registra-otra-fuerte-caida-y-el-barril-se-aleja-cada-vez-mas-de-los-us-100/ |
| Diseño | claude-sonnet-5-5, prompt 1.1 |
| RUB01 | 24/24 |
| Revisión humana 1 | Carlos Rojas Bruna (2026-11-16) |
| Simulación | 6 grupos, diseño diseno_otm |
| Guía | redactor: claude-sonnet-5-5, redactor_escenarios: claude-opus-5-5, version_prompt: 1.0 |
| Revisión humana 2 | Carlos Rojas Bruna (2026-11-16) |
| Commit | — |
