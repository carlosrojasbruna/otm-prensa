# Guía docente · ¿Invertir ya o esperar el permiso?

Tarea `2026-11-invertir-o-esperar-permiso` · guía versión 1 · 2026-11-09. Licencia CC BY-NC-SA 4.0. Generado desde `guia` (JSON, fuente de verdad).

## 0. Ficha

| Campo | Valor |
|---|---|
| Título | ¿Invertir ya o esperar el permiso? |
| Noticia | La Tercera, «Navarro de Empresas Copec dice que no esperaba un 2026 con “malas cifras económicas”, pero tiene optimismo sobre 2027», 2026-11-09, https://www.latercera.com/pulso/noticia/navarro-de-empresas-copec-dice-que-no-esperaba-un-2026-con-malas-cifras-economicas-pero-tiene-optimismo-sobre-2027/ |
| Nivel principal | U |
| Variantes | S |
| Contenidos | probabilidad y variables aleatorias de tiempo de espera; valor esperado y descuento; optimización con restricciones; análisis de sensibilidad |
| Tiempo | 2 sesiones de 90 min |
| Puntaje RUB01 | 23/24 |
| Versión y fecha | v1 · 2026-11-09 |
| Cambios | rev. 2 de la guía: correcciones de texto de la revisión humana 2 (Carlos Rojas Bruna): nota sobre la cifra de utilidades |

## 1. Meta de la clase (C1)

Cómo el grupo convierte una decisión de inversión con permiso incierto en un modelo: si pasa de las utilidades a septiembre a un presupuesto anual explícito, si representa la espera del permiso como algo aleatorio y no como un plazo fijo, y si recomienda cuánto comprometer y cuándo empezar con una condición de validez que contrasta con plazos reales.

**Contenido.** Probabilidad y variables aleatorias de tiempo de espera, valor esperado y descuento, optimización con restricciones y análisis de sensibilidad.

**Subcompetencias de modelación.**

- Comprender la decisión del directorio y su escala de presupuesto (P1-MRS)
- Simplificar: anualizar las utilidades, fijar la fracción comprometible y reducir el proyecto a costo, ingresos mensuales y duración de construcción (P2-RM)
- Matematizar la espera del permiso como variable aleatoria y definir el valor esperado de esperar o preparar antes, con descuento (P3-MM)
- Trabajar el modelo de forma analítica o por simulación (P4-WM)
- Interpretar el resultado como recomendación en dólares y plazos (P5-INT)
- Validar con plazos reales de tramitación y con sensibilidad (P6-VAL)
- Comunicar la recomendación, sus riesgos y sus límites (P7-EXP)

**Meta social.** Trabajo cooperativo en grupos pequeños: justificar los supuestos ante los compañeros y defender ante el curso una recomendación dirigida a un directorio.

**Evidencia que se recoge.**

- Reformulación escrita de la decisión, con los costos e ingresos en juego, y las solicitudes de información sobre el proyecto y el trámite
- Hoja de supuestos con valores propuestos y justificados
- Fórmulas o árbol que comparan esperar y preparar antes, con parámetros nombrados
- Cálculo analítico o simulación con tabla de resultados por estrategia
- Recomendación escrita con cifras en dólares, plazos y condición de validez
- Comparación entre la distribución de plazos supuesta y la real, y tabla de sensibilidad
- Informe o presentación al directorio con estrategia recomendada, riesgos y límites del modelo

## 2. Análisis a priori del espacio de soluciones (C2)

### Rutas

| Ruta | Nombre | Nivel | Modelo |
|---|---|---|---|
| R1 | Valor esperado con tiempo de espera exponencial | U | Valor presente esperado con descuento y tiempo hasta el permiso exponencial; condición cerrada para preparar antes: λ e^(−ρτ)(e^(ρΔ) − 1)V > c. |
| R2 | Simulación de plazos con distribución empírica | U | Simulación de muchos plazos de permiso con una distribución de cola larga (por ejemplo lognormal); se compara el valor medio y la pérdida en el peor decil de cada estrategia. |
| R3 | Árbol de decisión con escenarios discretos | S2 | Dos o más escenarios de plazo (permiso rápido o lento) con probabilidades supuestas; valor esperado de esperar frente a preparar antes. |
| R4 | Optimización de la fracción comprometida | U | Maximizar el valor esperado en función de la fracción de utilidades comprometida, con restricción de capital disponible y de pérdida máxima tolerable si el permiso se retrasa. |

### Modelo inadecuado (R5)

Comparar el costo del proyecto con las utilidades a septiembre usando un plazo fijo igual al promedio, mediante un valor neto determinista, oculta la dispersión del plazo del permiso: no distingue entre trámites que se resuelven pronto y casos de demora larga donde el gasto de preparación se pierde o el proyecto se posterga, y tampoco considera que las utilidades a septiembre son un ritmo parcial del año.

### Solución de referencia

1) Anualizar utilidades: 1.000 millones × 12/9 ≈ 1.333 millones de dólares. 2) Supuestos ilustrativos: se compromete 30%, es decir C ≈ 400 millones; el valor neto al entrar en operación es V = 25% de C = 100 millones; tasa mensual ρ = 0,008; construcción τ = 24 meses; tiempo hasta el permiso T exponencial con tasa λ = 1/18 por mes. 3) Esperar: valor = [λ/(λ + ρ)] e^(−ρτ) V ≈ 0,874 × 0,825 × 100 ≈ 72 millones. 4) Preparar antes, con costo mensual c, y acortar la construcción en Δ = 6 meses: valor = [λ/(λ + ρ)] e^(−ρ(τ − Δ)) V − c/(λ + ρ). 5) Diferencia (preparar − esperar) = [λ/(λ + ρ)] e^(−ρτ)(e^(ρΔ) − 1)V − c/(λ + ρ). Conviene preparar si λ e^(−ρτ)(e^(ρΔ) − 1)V > c, es decir c < ≈ 0,23 millones por mes. 6) Con trámites más rápidos (λ doble) el umbral sube a ≈ 0,45 millones por mes. 7) Optimización de la fracción de utilidades: maximizar el valor esperado por dólar comprometido sujeto a una pérdida máxima tolerable si el permiso se demora demasiado. 8) Sensibilidad a ρ, λ, c, Δ. Resultado: Con los valores ilustrativos, esperar vale unos 72 millones de dólares y preparar antes solo conviene si el costo mensual de preparación es menor que unos 0,23 millones de dólares; con trámites el doble de rápidos el umbral sube a unos 0,45 millones. La recomendación depende de costo de preparación, tiempo ahorrado y plazo esperado del permiso.

**Rango aceptable.** Se aceptan recomendaciones distintas si se derivan de supuestos explícitos y coherentes: fracción comprometida entre 10% y 50% de las utilidades anualizadas, plazos esperados de varios meses a pocos años, y un criterio claro (valor esperado, pérdida máxima o ambos). El umbral de costo mensual para preparar debe ser consistente con la estructura del modelo.

### Barreras anticipadas por fase

| Fase | Barrera |
|---|---|
| P1-MRS | Leer la pregunta como un sí o no a invertir, sin ver que se decide cuánto comprometer y cuándo empezar a gastar. Además, tratar las utilidades a septiembre como el presupuesto completo, sin notar que son el avance de una parte del año (bloqueo B12). |
| P2-RM | Dejar el proyecto sin valores (costo, ingresos mensuales, duración de construcción) o fijarlos sin justificar. También cuesta decidir cómo pasar de las utilidades a septiembre a un presupuesto anual y qué fracción es comprometible. Algunos grupos pueden esperar que el dato del proyecto se les entregue, cuando el escenario dice que lo estima el grupo (bloqueo B23). |
| P3-MM | Representar la espera con un plazo fijo igual al promedio y un valor neto determinista. Es el modelo inadecuado de la tarea: oculta la dispersión del plazo, no distingue los trámites rápidos de los de demora larga y no considera que las utilidades a septiembre son un ritmo parcial del año. También cuesta combinar descuento, espera aleatoria y costo mensual de preparar en un solo valor esperado por estrategia (bloqueo B34). |
| P4-WM | Plantear bien el modelo pero no poder calcular el valor esperado con el tiempo de espera aleatorio. La salida es una simulación, pero entonces hay que decidir cuántos escenarios generar y cómo leer la tabla. Buscar la fracción óptima con restricciones agrega otra dificultad (bloqueo B45). |
| P5-INT | Quedarse en el número o en la fórmula sin traducirlo a una recomendación sobre cuánto comprometer y cuándo empezar. También cuesta decir qué cambia si los trámites fueran más rápidos y bajo qué condición la recomendación deja de valer (bloqueo B56). |
| P6-VAL | Los plazos reales llegan después de presentar el modelo. Puede haber resistencia a revisar un modelo ya defendido, o contrastar solo el promedio y no la forma de la distribución. También cuesta decidir qué parámetros someter a sensibilidad (descuento, plazo medio, costo de preparación) (bloqueo B67). |

## 3. Organización (C3, C4, C7)

| Momento | Tiempo | Qué hacen los estudiantes | Qué hace el docente |
|---|---|---|---|
| Comprensión y trabajo grupal (sesión 1: P1 a P3) | 70 min | Leen el enunciado y reformulan por escrito qué decide el directorio. Piden los recursos que necesiten (descripción del proyecto, descripción del trámite). Elaboran su lista de supuestos con valores justificados y proponen cómo representar la espera del permiso. | Circula y diagnostica: pregunta qué han hecho y por qué, y qué piensan de la espera del permiso. Entrega los recursos a solicitud solo cuando el grupo los pide. No interviene aún sobre el modelo ni entrega la regla, la fórmula o el resultado. Sobre la cifra del enunciado: la noticia indica que las utilidades superan los 1.000 millones de dólares; el enunciado usa la cifra redonda. |
| Puesta en común (sesión 1) | 20 min | Cada grupo muestra sus supuestos y cómo representa la espera. Comparan diferencias entre grupos y las justifican. | Modera, ordena las propuestas en la pizarra sin evaluarlas y pregunta qué supone cada una sobre la espera. No valida ni descarta un modelo. |
| Comprensión y trabajo grupal (sesión 2: P4 y P5) | 35 min | Calculan o simulan el valor esperado de cada estrategia, buscan la condición o la fracción que maximiza el valor y redactan una recomendación con cifras en dólares, plazos y condición de validez. Analizan qué cambia si los trámites fueran más rápidos. | Circula y pregunta qué han calculado y cómo leen el resultado. La ayuda mínima va primero: una pregunta sobre qué representa cada parámetro. No entrega la condición ni el valor de referencia. |
| Puesta en común (sesión 2) | 20 min | Presentan su modelo y su recomendación. Contrastan las rutas usadas (valor esperado con espera exponencial, simulación con distribución empírica, árbol de decisión, optimización de la fracción comprometida) y los supuestos distintos. | Pide a cada grupo que explique su criterio de decisión y qué la haría cambiar. Al terminar cada presentación entrega la información pública sobre tiempos reales de evaluación (R4). |
| Validación y cierre | 35 min | Comparan los plazos que supusieron con los reales, hacen una tabla de sensibilidad (descuento, plazo medio, costo de preparación), ajustan la recomendación si corresponde y preparan el informe o presentación al directorio con riesgos, supuestos y la información nueva que la cambiaría. | Pregunta qué cambió al contrastar con los datos reales y qué parte del modelo resistió. Cierra destacando que distintas recomendaciones pueden ser válidas si sus supuestos son explícitos y coherentes, y que el modelo de plazo fijo promedio pierde la dispersión del plazo. |

**Agrupamiento.** Grupos pequeños, que se mantienen las dos sesiones, para que el grupo discuta y justifique sus supuestos en voz alta. Conviene que cada grupo tenga una sola hoja de trabajo.

**Roles.** Quien lee la decisión y vigila que el grupo responda a la pregunta; quien registra supuestos y parámetros; quien revisa cálculos y unidades; quien presenta. Los roles rotan entre la sesión 1 y la sesión 2 para que todos verbalicen.

**Producciones que se registran.**

- Reformulación escrita de la decisión y solicitudes de información
- Hoja de supuestos con valores justificados
- Fórmulas o árbol de decisión con parámetros nombrados
- Tabla de resultados por estrategia (cálculo o simulación)
- Recomendación escrita con cifras en dólares, plazos y condición de validez
- Comparación entre plazos supuestos y reales, y tabla de sensibilidad
- Informe o presentación al directorio con riesgos y límites del modelo

**Tecnología.** Se permite calculadora y hoja de cálculo o un software de simulación solo en el trabajo de cálculo (P4-WM) y en la tabla de sensibilidad (P6-VAL). La comprensión, los supuestos y la representación de la espera (P1 a P3) se hacen en papel. La herramienta calcula, pero el grupo decide la distribución del plazo, la fracción comprometida y el criterio de decisión.

## 4. Escenarios simulados (C2, C6)

Derivados de las trazas del simulador; cada escenario cita las corridas que lo respaldan.

### E1 · valor esperado con descuento

| Campo | Valor |
|---|---|
| Corridas | N4_AA_r1 |
| Perfil del grupo | Tramo U, nivel N4, estilo AA. |
| Ruta observada | P1-MRS → P3-MM → P6-VAL → P4-WM → P6-VAL → P4-WM → P6-VAL → P7-EXP |
| Supuestos que emergieron | probabilidad de aprobación p (0,6; 0,3 en sensibilidad); tiempo de tramitación fijo T = 2 años; descuento exponencial continuo r = 10%; valor del proyecto V = 3.000 millones; retraso L = 1 año si se prepara después; el gasto de preparación C se pierde si no sale el permiso; al esperar, C solo se gasta si se aprueba; trámites rápidos: T = 1 año y p = 0,8; C como porcentaje de los 1.000 millones (sin anualizar) |
| Modelo al que llegaron | valor esperado descontado |
| Dónde se trabaron y cómo se destrabaron | sin bloqueos |

**Qué aprende el curso.** Es la corrida más cercana a la ruta R1: compara esperar y preparar antes con valor esperado y descuento, y alterna trabajar y validar con sensibilidad a la probabilidad del permiso. El curso ve que el grupo separa el punto de indiferencia del tope que recomienda, porque el riesgo de perder el gasto manda sobre el cálculo. Al compararla con E2 y E4 se discute lo que todavía falta: el plazo del permiso queda fijo (no es una variable aleatoria) y las utilidades a septiembre no se anualizan.

**Extracto de diálogo simulado.**

> **Fran:** Dale, pero ojo con que el valor esperado solo no basta, porque si el permiso no sale el gasto C se pierde entero. Yo plantearía VE(empezar) = p·V·e^(-rT') − C contra VE(esperar) = p·V·e^(-r(T+L)), donde L es el retraso de preparar después. ¿Te parece?  
> **Cami:** Me parece, pero ojo que en "esperar" tampoco gastas C si el permiso no sale: deberías restar p·C·e^(-rT), porque solo lo gastas si lo aprueban. Entonces empezar conviene si p·V·e^(-rT)(1−e^(-rL)) > C(1−p·e^(-rT)), ¿lo revisamos?  
> **Fran:** Los números me cuadran, pero 275 es solo el punto de indiferencia, no un tope. Con p = 0,3 me da C < ~93 millones, o sea 9%, así que es muy sensible a p y yo pondría un tope de 10-15%.  

### E2 · modelo inadecuado

| Campo | Valor |
|---|---|
| Corridas | N3_AA_r1 |
| Perfil del grupo | Tramo U, nivel N3, estilo AA. |
| Ruta observada | P2-RM → P3-MM → P5-INT → P4-WM → P3-MM → P7-EXP → P6-VAL → P7-EXP |
| Supuestos que emergieron | costo de preparación C que se pierde si el permiso no sale; probabilidad p de que salga el permiso; ingresos del proyecto constantes B por mes; plazo del trámite T fijo; prepararse adelanta el proyecto s meses; tasa de descuento r mencionada pero no usada; monto comprometido como fracción chica de los 1.000 millones, sin anualizar; gasto por etapas |
| Modelo al que llegaron | lineal determinista |
| Dónde se trabaron y cómo se destrabaron | sin bloqueos |

**Qué aprende el curso.** Muestra el modelo inadecuado que describe la tarea: un plazo fijo y una comparación determinista, sin anualizar las utilidades a septiembre y con la tasa de descuento nombrada pero sin usar. El curso puede ver qué se pierde: no hay forma de distinguir un trámite rápido de una demora larga en que el gasto de preparación se pierde. Contrasta con E1, que sí descuenta, y con E4, que al menos prueba varios plazos. Rescata dos buenas decisiones: separar el tiempo realmente ahorrado (s) del plazo del trámite y proponer gastar por etapas.

**Extracto de diálogo simulado.**

> **Fran:** Sí, me parece, pero faltaría el tiempo: T, los meses que demora el trámite, y quizás una tasa de descuento r. Así comparamos esperar, que cuesta B·T en ingresos retrasados, contra prepararnos ya, que cuesta C y se pierde si el permiso no sale.  
> **Fran:** Me cuadra, y el umbral sale de despejar T: T* = C/(p·B) = 20/(0,6·10) ≈ 3,3 meses, o sea que bajo eso conviene esperar. Pero ojo que prepararse antes quizás no adelanta los T meses completos, así que habría que pedir cuánto tiempo se ahorra realmente.  
> **Cami:** Claro, llamemos s a los meses que realmente se adelanta el proyecto, y la condición queda C < p·B·s, o sea s > 3,3 con esos números. Con C = 20 serían solo un 2% de los 1.000 millones, así que el monto no sería el problema.  

### E3 · bloqueo en matematizar

| Campo | Valor |
|---|---|
| Corridas | N1_AA_r1 |
| Perfil del grupo | Tramo U, nivel N1, estilo AA. |
| Ruta observada | P1-MRS → P2-RM → P3-MM → P4-WM → P5-INT → P6-VAL → P7-EXP |
| Supuestos que emergieron | costo de prepararse C fijo, en millones de USD; ganancia del proyecto G; probabilidad p de que salga el permiso, igual en ambas estrategias; pérdida lineal D por cada mes de retraso (D·t); plazo del permiso t fijo; D como parámetro aparte, no necesariamente G dividido en meses; monto comprometido = C, fracción C/1000 de las utilidades (sin anualizar) |
| Modelo al que llegaron | valor esperado lineal |
| Dónde se trabaron y cómo se destrabaron | B23: Se resolvió entre pares (peer). Cami nombra C, G y p pero no sabe cómo meter el tiempo; Fran propone una pérdida D por mes de retraso; Cami objeta que la estrategia de esperar también debe llevar la probabilidad p y duda de cómo se relacionan D y G; Fran corrige la expresión de esperar incluyendo p y deja D como parámetro aparte. Con eso pasan a despejar la condición. |

**Qué aprende el curso.** Es el único bloqueo registrado en las corridas y ocurre al pasar de los supuestos a las fórmulas: cómo representar el tiempo y dónde va la probabilidad. El curso ve que una pregunta de un compañero (¿la p no debería ir también en esperar?) destraba el paso sin ayuda externa. Al compararlo con E1 se discute que la pérdida lineal por mes y el plazo fijo reemplazan al descuento y a la incertidumbre del plazo, y que el monto comprometido se mide contra utilidades sin anualizar.

**Extracto de diálogo simulado.**

> **Cami:** Ya, dale: C el costo de prepararse, G lo que gana el proyecto y p la probabilidad del permiso. Entonces si preparamos antes, ¿sería G·p − C? Pero no sé cómo meter el tiempo ahí.  
> **Fran:** Tal vez agregamos una letra más: D, lo que se pierde por cada mes de retraso. Entonces esperar sería G − D·t, donde t son los meses que demora el permiso, y comparamos con G·p − C, ¿te parece?  
> **Cami:** Ya, pero ojo: si esperamos, ¿G − D·t no supone que el permiso sale igual? ¿Y la probabilidad p no debería ir también ahí? Aunque no sé si D·t y G se pueden restar así, ¿D no sería lo mismo que G dividido en meses?  
> **Fran:** Tienes razón, a esperar también hay que ponerle la p: sería p·(G − D·t), y se compara con p·G − C. Y lo de D, puede ser G dividido en los meses de vida del proyecto, pero no estoy segura, ¿lo dejamos como letra aparte por ahora?  

### E4 · árbol con escenarios de plazo

| Campo | Valor |
|---|---|
| Corridas | N2_VV_r1 |
| Perfil del grupo | Tramo U, nivel N2, estilo VV. |
| Ruta observada | P1-MRS → P2-RM → P3-MM → P4-WM → P5-INT → P3-MM → P6-VAL → P4-WM → P5-INT → P4-WM → P6-VAL → P3-MM → P7-EXP |
| Supuestos que emergieron | escenarios discretos de plazo del permiso (3, 6, 12 meses); costo de estudios inventado de 50 millones; ingresos de 20 millones por mes; preparación de 6 meses tras el permiso; probabilidad de que salga el permiso (50%, 20%, 80%); el gasto de preparación se pierde si el permiso no sale; costo de esperar = ingresos atrasados; tiempo ahorrado = mínimo entre plazo del permiso y preparación |
| Modelo al que llegaron | árbol de decisión |
| Dónde se trabaron y cómo se destrabaron | sin bloqueos |

**Qué aprende el curso.** Se acerca a la ruta R3: en vez de un plazo único, prueba varios escenarios de plazo y varias probabilidades, y vuelve varias veces a matematizar a partir de su dibujo de línea de tiempo. El curso ve cómo el dibujo lleva a corregir el tiempo ahorrado como el mínimo entre plazo del permiso y preparación, una decisión que E2 dejó como dato a pedir. Al compararlo con E1 se nota que el árbol no descuenta y que los escenarios de plazo no tienen probabilidades propias.

**Extracto de diálogo simulado.**

> **Fran:** Ya, pidamos eso. Mirando mi dibujo, creo que lo que ahorras al empezar antes es el menor entre lo que demora el permiso y lo que demora preparar, así que con permiso a 3 meses y preparación de 6, el 3 estaría bien, ¿o me estoy enredando?  
> **Cami:** No creo que te estés enredando: en el dibujo, con permiso a 3 y preparación de 6, empezando antes estás listo en el mes 6 y esperando recién en el 9, o sea que ahorras 3. Y si el permiso demorara 12 y preparar 6, ahorrarías solo 6 porque igual tienes que esperar el permiso, ¿cierto?  
> **Fran:** Sí, en el dibujo con permiso a 12 la preparación de 6 meses queda "tapada" por la espera, así que ahorras 6. Entonces anoto 50(1 − p) = 20 · mín(permiso, preparación) · p, ¿te parece que armemos la respuesta con eso?  


Tabla agregada de bloqueos (6 grupos simulados):

| Transición | Grupos que se trabaron | % |
|---|---|---|
| B23 | 1/6 | 17 % |

## 5. Intervenciones graduadas por bloqueo anticipado (C5, C6)

La ayuda mínima primero; diagnosticar antes de intervenir. Ninguna ayuda entrega la regla.

| Bloqueo | Z1–Z2 motivación / retroalimentación | Z3 estratégica general | Z4 estratégica de contenido | Z5 contenido (último recurso) |
|---|---|---|---|---|
| B23 | Pregunten al grupo: «¿Qué letras o supuestos ya tienen escritos y qué les falta para compararlas?». Pidan que lean en voz alta qué hace cada letra en su expresión. Reconozcan que ya tienen supuestos antes de pedirles fórmulas. | Pidan una línea de tiempo con tres marcas: hoy, cuando sale el permiso y cuando el proyecto empieza a dar ingresos. Que dibujen una para esperar y otra para preparar antes, y que ubiquen en cada una dónde cae el gasto y dónde los ingresos. | Pregunten: «¿En qué casos se gasta la preparación aunque el permiso no salga, y en qué casos no? ¿Cómo aparece eso en cada estrategia?». Si el grupo ya puso la incertidumbre en una sola estrategia, pregunten: «¿La estrategia de esperar no depende también de que el permiso salga?». Esa pregunta destrabó a los pares en E3. Si el grupo usa un plazo único, pregunten: «¿Qué pasaría con su comparación si el trámite demora mucho más o mucho menos?». | Entreguen el recurso R3, la descripción del trámite del permiso. Señala que el permiso puede resolverse en cualquier mes sin saberse cuándo, que preparar antes tiene un costo mensual y que puede acortar la construcción. Dejen que el grupo decida cómo representar la espera y cómo comparar las dos estrategias. No escriban la expresión por ellos. |
| B12 | Pidan que reformulen con sus palabras qué decide el directorio. Pregunten: «¿Qué costos y qué ingresos están en juego?» y «¿qué han entendido por utilidades a septiembre?». | Que hagan un esquema de la decisión con dos opciones, empezar a preparar ahora o esperar el permiso. Que anoten qué se gasta y qué se gana en cada una. | Pregunten: «Las utilidades son a septiembre, pero el presupuesto es de todo el año. ¿Qué implica eso para usarlas como escala del monto a comprometer?». Pregunten también: «¿Qué parte de esas utilidades podría ir al proyecto?». | Entreguen el recurso R2 (descripción del proyecto hipotético) y el recurso R3 (descripción del trámite del permiso). Recuérdenles que el tamaño, el costo y los ingresos los estiman ellos, y que ninguno de los recursos trae esos valores. |
| B34 | Pregunten: «¿Qué fórmula o árbol tienen hasta ahora y qué parámetros nombraron?». Pidan que expliquen qué representa cada parámetro antes de seguir. | Que prueben su planteamiento con una situación concreta en que el permiso sale pronto y otra en que se demora mucho. Que anoten qué ocurre con el gasto y con los ingresos en cada una. | Pregunten: «¿Cómo muestra su planteamiento que el plazo del permiso no se conoce de antemano?». Si dibujaron una línea de tiempo, como en E4, pregunten: «¿Cuánto tiempo ahorra de verdad prepararse antes cuando el permiso demora poco y cuando demora mucho?». | Entreguen el recurso R3 si aún no lo tienen. Pidan que expliquen con sus propios parámetros por qué el tiempo ahorrado no es siempre el mismo. Pídanles también que escriban la comparación entre estrategias en términos de lo que esperan ganar o perder. No les den la expresión. |
| B56 | Pregunten: «¿Qué recomendación escribirían hoy al directorio y con qué cifras la sostienen?». Pidan que lean la recomendación junto con los supuestos que usaron. | Que reescriban el resultado como una frase para alguien que no vio el cálculo, con monto, momento de inicio y qué tendría que cumplirse para que siga valiendo. | Pregunten: «¿Qué cambia en su recomendación si el trámite fuera más rápido? ¿Y si el permiso demora mucho?». Pregunten también: «¿Qué supuesto, si fuera falso, la haría cambiar?». | Pidan que identifiquen cuál de sus supuestos pesa más en el resultado y que repitan el cálculo cambiando solo ese supuesto. Que comparen ambas recomendaciones y expliquen por qué cambió o no. No indiquen cuál debería ser el resultado. |

## 6. Puesta en común: orquestar soluciones múltiples (C8)

### Selección y orden

1. Primero E3 (anticipar y monitorear): es el modelo más simple y deja a la vista el paso de los supuestos a las fórmulas. Se ve cómo se resolvió el bloqueo en matematizar y que un plazo fijo con pérdida lineal por mes esconde la incertidumbre. Así se parte de lo que muchos grupos tendrán a mano, sin privilegiar la ruta del docente.
2. Luego E2 (seleccionar): es el modelo inadecuado de la tarea, con plazo fijo y comparación determinista. Se discute qué no puede distinguir: un trámite rápido de una demora larga en que se pierde el gasto de preparación. También se rescata su separación entre el tiempo realmente ahorrado y el plazo del trámite.
3. Después E4 (secuenciar): prueba varios escenarios de plazo y corrige el tiempo ahorrado con su dibujo. Responde a la limitación de E2 y se acerca a la ruta R3. Queda pendiente que no descuenta y que los escenarios no tienen probabilidades propias.
4. Al final E1 (conectar): incorpora descuento, sensibilidad a la probabilidad del permiso y la diferencia entre el punto de indiferencia y el tope que recomienda el grupo. Es la más cercana a la ruta R1. Conecta con lo anterior, y deja abiertas dos carencias: el plazo sigue fijo y las utilidades a septiembre no se anualizan.

### Preguntas

- ¿Qué supuesto de su modelo pesa más en la recomendación y cómo lo justificaron?
- ¿Qué pasa en su modelo si el permiso demora mucho? ¿Y si sale pronto? ¿El modelo distingue ambos casos?
- En E3 y E2 el plazo es fijo. ¿Qué se pierde al tratarlo así?
- ¿Cómo usaron las utilidades a septiembre para fijar el monto comprometido? ¿Tuvieron en cuenta que son solo una parte del año?
- En E1, ¿por qué el punto de indiferencia no es lo mismo que el tope recomendado?
- ¿Qué decisión les costó más, representar el tiempo o ubicar la incertidumbre? ¿Qué los destrabó?
- ¿Qué modelo comparado es más simple y cuál más fiel a la situación? ¿Qué se gana y qué se pierde en cada caso?
- ¿Hasta dónde vale su recomendación? ¿Qué información nueva la cambiaría?

### Contraste con la evidencia independiente

Después de que cada grupo presente su modelo, entreguen el recurso R4: estadísticas e informes públicos del Servicio de Evaluación Ambiental sobre cuánto demoran los trámites en el Sistema de Evaluación de Impacto Ambiental. Pidan que comparen los plazos que supusieron con los observados y que revisen si su recomendación se mantiene. Esos datos no se usan para construir el modelo, solo para contrastarlo. No traigan cifras adicionales a las que aporten esas fuentes. Si la recomendación cambia, pidan que identifiquen qué supuesto del plazo la movió. Si se mantiene, que expliquen por qué resiste. Cierren con los límites de cada modelo presentado.

## 7. Evaluación del trabajo del estudiante

Pendiente en PLT02 v0.1 (rúbrica por fase del ciclo); esta versión de la guía no la incluye.

## 8. Variantes y continuidad (P3, C9)

**Uso de variantes.** La variante hacia abajo (tramo S2) conviene con estudiantes de secundaria superior o con un grupo universitario que no maneja variables aleatorias continuas. En ese caso se entregan como datos los plazos posibles del permiso (rápido o lento) con sus probabilidades. La pregunta pide comparar dos estrategias con un árbol de decisión y valor esperado, que corresponde a la ruta R3. No se pide optimizar la fracción de utilidades ni modelar la espera como variable aleatoria continua. Al entregar los plazos y las probabilidades, el grupo ya no decide cómo representar la espera, así que se reduce la decisión de P3-MM. Úsela desde el inicio de la sesión 1, o tras observar en la puesta en común que el grupo no logra representar la espera. La variante hacia arriba es null: la tarea no define una. Para un grupo avanzado se pueden usar las rutas R2 (simulación con cola larga) y R4 (optimización de la fracción comprometida), que ya forman parte de la tarea principal.

**Acostumbramiento.** Si el grupo nunca ha modelado, conviene una actividad breve previa: una decisión con dos escenarios y supuestos explícitos que el grupo escriba antes de calcular, y que cada grupo explique qué simplificó y por qué. Así practican la lista de supuestos y la verbalización, que esta tarea exige en P2-RM. La tarea es parte de una secuencia y no un diagnóstico: exige supuestos abiertos, espera aleatoria y validación con datos posteriores. Con grupos sin experiencia, la variante hacia abajo puede servir de iniciación y dejar la tarea completa para una segunda ocasión.

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
| Noticia | https://www.latercera.com/pulso/noticia/navarro-de-empresas-copec-dice-que-no-esperaba-un-2026-con-malas-cifras-economicas-pero-tiene-optimismo-sobre-2027/ |
| Diseño | claude-sonnet-5-5, prompt 1.1 |
| RUB01 | 23/24 |
| Revisión humana 1 | Carlos Rojas Bruna (2026-11-09) |
| Simulación | 6 grupos, diseño diseno_otm |
| Guía | redactor: claude-sonnet-5-5, redactor_escenarios: claude-opus-5-5, version_prompt: 1.0 |
| Revisión humana 2 | Carlos Rojas Bruna (2026-11-09) |
| Commit | — |
