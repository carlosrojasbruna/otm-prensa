# ¿Invertir ya o esperar el permiso?

Tarea `2026-11-invertir-o-esperar-permiso` · versión 1 · 2026-11-09 · nivel U · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-11-invertir-o-esperar-permiso
titulo: ¿Invertir ya o esperar el permiso?
estado: verificada
version: 1
fecha: '2026-11-09'
noticia:
  noticia_id: 2026-11-09-latercera-navarro-de-empresas-copec-dice-que
  medio: La Tercera
  titulo: Navarro de Empresas Copec dice que no esperaba un 2026 con “malas cifras económicas”, pero tiene optimismo sobre 2027
  fecha: '2026-11-09'
  url: https://www.latercera.com/pulso/noticia/navarro-de-empresas-copec-dice-que-no-esperaba-un-2026-con-malas-cifras-economicas-pero-tiene-optimismo-sobre-2027/
  resumen_propio: Un alto ejecutivo de Empresas Copec reconoce que el año económico va peor de lo previsto, por tensiones comerciales, encarecimiento de la energía, inflación y tasas altas que afectan a una economía exportadora como la chilena. Pese a ello, se muestra optimista para el próximo año gracias a leyes que buscan impulsar la inversión y los permisos, aunque advierte que hay que pasar de las señales a la acción, con un desempleo elevado y trámites más ágiles para destrabar inversiones.
  cifras_usadas:
  - valor: US$ 1.000 millones
    unidad: dólares (millones)
    que_es: Utilidades de Empresas Copec a septiembre
    localizador:
      fuente: noticia
      ubicacion: párrafo 2
nivel_principal: U
variantes:
  abajo: S
  arriba: null
area: economia
contenidos_matematicos:
- probabilidad y variables aleatorias de tiempo de espera
- valor esperado y descuento
- optimización con restricciones
- análisis de sensibilidad
tiempo_estimado: 2 sesiones de 90 min
rubrica_rub01:
  total: 23
  por_criterio:
    genuino: 2
    abierta: 2
    decisiones: 2
    realismo: 2
    autenticidad: 1
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
Un alto ejecutivo de Empresas Copec dijo que este año ha sido más débil de lo que esperaba, pero que ve con optimismo el próximo si las leyes que buscan agilizar permisos pasan de la promesa a la práctica. La empresa tuvo utilidades por 1.000 millones de dólares a septiembre. Imaginen que el directorio de una empresa de este tipo estudia un gran proyecto que depende de un permiso cuya tramitación es incierta. Si empieza a prepararse antes, gasta en estudios y personal sin saber si el permiso llegará; si espera, retrasa los ingresos futuros del proyecto. ¿Cuánto de sus utilidades debería comprometer, y cuándo conviene empezar? ¿Cómo cambiaría su recomendación si los trámites se hicieran más rápidos? Pueden pedir información adicional.
```

```text foto_descripcion
Ilustración sencilla de un semáforo en amarillo junto a un plano de obra con una grúa detenida.
```

### 1.1 Variante hacia abajo (tramo S2)

Se entregan como datos los plazos posibles del permiso (rápido o lento) con sus probabilidades, y la pregunta pide comparar dos estrategias con un árbol de decisión y valor esperado; no se pide optimizar la fracción de utilidades ni modelar la espera como variable aleatoria continua.

### 1.2 Variante hacia arriba

No hay.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Dato de partida sobre utilidades de la empresa | Empresas Copec tuvo utilidades por 1.000 millones de dólares a septiembre. | de_entrada | P1-MRS | noticia, párrafo 2 |
| R2 | Descripción del proyecto hipotético | Supuesto del escenario: una vez aprobado el permiso y construido el proyecto, este genera ingresos netos cada mes durante varios años. Mientras no se construye, no genera ingresos. El tamaño del proyecto, su costo y sus ingresos los debe estimar el grupo. | a_solicitud | P2-RM | supuesto del escenario |
| R3 | Descripción del trámite del permiso | Supuesto del escenario: el permiso puede resolverse favorablemente en cualquier mes, sin que se sepa de antemano cuándo. Preparar el proyecto antes de tener el permiso tiene un costo mensual, pero puede acortar la construcción una vez aprobado. El grupo debe decidir cómo representar la espera. | a_solicitud | P3-MM | supuesto del escenario |
| R4 | Información pública sobre tiempos reales de evaluación de proyectos (se entrega después de que el grupo presente su modelo) | Estadísticas e informes públicos sobre proyectos de inversión evaluados en el sistema de evaluación ambiental, con información sobre cuánto demoran sus trámites, para comparar con los plazos que supuso el grupo. | a_solicitud | P6-VAL | otra fuente: Servicio de Evaluación Ambiental (SEA), estadísticas e informes públicos del Sistema de Evaluación de Impacto Ambiental (SEIA) |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender qué decide el directorio: cuánto comprometer y cuándo empezar a gastar, y qué significa que las utilidades a septiembre sirvan de escala del presupuesto anual. | Reformulación por escrito de la decisión, con la pregunta de qué costos y qué ingresos están en juego; solicitud de información sobre el proyecto y el trámite. | B12 |
| P2-RM Simplificar | Decidir cómo pasar de las utilidades a septiembre a un presupuesto anual, qué fracción es comprometible, y simplificar el proyecto en costo, ingresos mensuales y duración de construcción. | Lista de supuestos con valores propuestos y justificados. | B23 |
| P3-MM Matematizar | Representar el tiempo de espera del permiso como variable aleatoria y definir el valor esperado de cada estrategia (esperar o preparar antes) con descuento. | Fórmulas o árbol que comparan ambas estrategias, con parámetros nombrados. | B34 |
| P4-WM Trabajar | Calcular o simular el valor esperado de cada estrategia y encontrar la condición o la fracción que maximiza el valor. | Cálculo analítico o simulación con tabla de resultados por estrategia. | B45 |
| P5-INT Interpretar | Traducir el resultado a una recomendación: cuánto comprometer, cuándo empezar y qué pasa si el trámite fuera más rápido. | Recomendación escrita con cifras en dólares y plazos, y con su condición de validez. | B56 |
| P6-VAL Validar | Contrastar los plazos supuestos con plazos reales de tramitación y probar sensibilidad a descuento, plazo medio y costo de preparación. | Comparación entre la distribución de plazos supuesta y la real; tabla de sensibilidad. | B67 |
| P7-EXP Exponer | Presentar al directorio la recomendación con riesgos, supuestos y qué información nueva la cambiaría. | Informe o presentación con estrategia recomendada y límites del modelo. | — |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- Las utilidades a septiembre se anualizan suponiendo un ritmo parecido en los meses restantes.
- Solo una fracción de las utilidades anuales puede destinarse al proyecto.
- El proyecto entrega ingresos netos mensuales constantes una vez construido, y el valor se mide con una tasa de descuento elegida por el grupo.
- El tiempo hasta obtener el permiso es aleatorio con una distribución propuesta (por ejemplo exponencial).
- Preparar antes del permiso tiene un costo mensual y acorta la construcción en un tiempo fijo.

### Solución de referencia

1) Anualizar utilidades: 1.000 millones × 12/9 ≈ 1.333 millones de dólares. 2) Supuestos ilustrativos: se compromete 30%, es decir C ≈ 400 millones; el valor neto al entrar en operación es V = 25% de C = 100 millones; tasa mensual ρ = 0,008; construcción τ = 24 meses; tiempo hasta el permiso T exponencial con tasa λ = 1/18 por mes. 3) Esperar: valor = [λ/(λ + ρ)] e^(−ρτ) V ≈ 0,874 × 0,825 × 100 ≈ 72 millones. 4) Preparar antes, con costo mensual c, y acortar la construcción en Δ = 6 meses: valor = [λ/(λ + ρ)] e^(−ρ(τ − Δ)) V − c/(λ + ρ). 5) Diferencia (preparar − esperar) = [λ/(λ + ρ)] e^(−ρτ)(e^(ρΔ) − 1)V − c/(λ + ρ). Conviene preparar si λ e^(−ρτ)(e^(ρΔ) − 1)V > c, es decir c < ≈ 0,23 millones por mes. 6) Con trámites más rápidos (λ doble) el umbral sube a ≈ 0,45 millones por mes. 7) Optimización de la fracción de utilidades: maximizar el valor esperado por dólar comprometido sujeto a una pérdida máxima tolerable si el permiso se demora demasiado. 8) Sensibilidad a ρ, λ, c, Δ.

**Resultado.** Con los valores ilustrativos, esperar vale unos 72 millones de dólares y preparar antes solo conviene si el costo mensual de preparación es menor que unos 0,23 millones de dólares; con trámites el doble de rápidos el umbral sube a unos 0,45 millones. La recomendación depende de costo de preparación, tiempo ahorrado y plazo esperado del permiso.

**Rango aceptable.** Se aceptan recomendaciones distintas si se derivan de supuestos explícitos y coherentes: fracción comprometida entre 10% y 50% de las utilidades anualizadas, plazos esperados de varios meses a pocos años, y un criterio claro (valor esperado, pérdida máxima o ambos). El umbral de costo mensual para preparar debe ser consistente con la estructura del modelo.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Valor esperado con tiempo de espera exponencial | U | Valor presente esperado con descuento y tiempo hasta el permiso exponencial; condición cerrada para preparar antes: λ e^(−ρτ)(e^(ρΔ) − 1)V > c. | Con los valores ilustrativos, esperar vale unos 72 millones de dólares; preparar conviene si c es menor que unos 0,23 millones por mes. |
| R2 | Simulación de plazos con distribución empírica | U | Simulación de muchos plazos de permiso con una distribución de cola larga (por ejemplo lognormal); se compara el valor medio y la pérdida en el peor decil de cada estrategia. | Rango del valor esperado por estrategia y de la pérdida en escenarios de demora larga; puede cambiar la recomendación respecto de R1 cuando la cola es pesada. |
| R3 | Árbol de decisión con escenarios discretos | S2 | Dos o más escenarios de plazo (permiso rápido o lento) con probabilidades supuestas; valor esperado de esperar frente a preparar antes. | Estrategia de mayor valor esperado según las probabilidades; punto de equilibrio en la probabilidad de permiso rápido. |
| R4 | Optimización de la fracción comprometida | U | Maximizar el valor esperado en función de la fracción de utilidades comprometida, con restricción de capital disponible y de pérdida máxima tolerable si el permiso se retrasa. | Fracción óptima intermedia (por ejemplo cerca de 30% de las utilidades anualizadas en el caso base); disminuye si aumenta la dispersión del plazo o la aversión al riesgo. |

### Modelo inadecuado (R5)

Comparar el costo del proyecto con las utilidades a septiembre usando un plazo fijo igual al promedio, mediante un valor neto determinista, oculta la dispersión del plazo del permiso: no distingue entre trámites que se resuelven pronto y casos de demora larga donde el gasto de preparación se pierde o el proyecto se posterga, y tampoco considera que las utilidades a septiembre son un ritmo parcial del año.

### Evidencia de validación (independiente del modelo)

Información pública y estadísticas de evaluación de proyectos en el Sistema de Evaluación de Impacto Ambiental (Servicio de Evaluación Ambiental, SEA) sobre plazos reales de tramitación, entregadas después de modelar: se contrasta la distribución de plazos supuesta por el grupo y se verifica si la recomendación se mantiene con los plazos observados; esos datos no se usan para construir el modelo.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | La situación plantea una decisión de inversión bajo incertidumbre que hay que resolver. Ni el enunciado ni los recursos entregan una regla o un modelo; R3 describe la mecánica del escenario, pero deja al grupo la representación. | — |
| 2 | abierta | 2 | La pregunta no prescribe procedimiento. Admite modelos deterministas por escenarios, de valor esperado o probabilísticos mes a mes, todos defendibles. | — |
| 3 | decisiones | 2 | Resolver exige estimar magnitudes, formular supuestos sobre la distribución del plazo del permiso y simplificar la estructura de costos e ingresos. | — |
| 4 | realismo | 2 | Decidir si invertir antes o esperar un permiso de tramitación incierta es una situación real y frecuente en empresas, ligada al debate de la noticia. | — |
| 5 | autenticidad | 1 | La noticia (declaraciones, utilidades, leyes de permisos) y las estadísticas de R4 son auténticas, pero el núcleo es un proyecto hipotético construido para la actividad: la cifra de utilidades sirve solo de escala y R4 de contraste posterior. Dudé entre 1 y 2 porque el tema de los permisos sí atraviesa la segunda pregunta; asigno el menor. | — |
| 6 | contexto | 2 | El contexto define el trade-off que estructura el modelo. También es necesario para interpretar la recomendación y validarla con los tiempos reales de tramitación. | — |
| 7 | ciclo | 2 | Responder obliga a recorrer el ciclo completo: comprender, suponer plazos y montos, matematizar la espera, calcular, interpretar una recomendación y revisarla. Ninguna fase la deja hecha el enunciado. | — |
| 8 | validacion | 2 | R4 aporta evidencia independiente, no usada en la construcción del modelo, para contrastar los plazos supuestos por el grupo. | — |
| 9 | nivel | 2 | El contexto empresarial y el lenguaje son comprensibles para universitarios. Modelar la espera con probabilidad, modelos discretos y optimización corresponde a las herramientas esperables del nivel U. | — |
| 10 | autodiferenciacion | 2 | Hay entrada elemental: comparar dos escenarios con plazos fijos. La tarea admite soluciones más sofisticadas, como valor esperado con distribución del plazo, decisión óptima de inicio o análisis de sensibilidad. | — |
| 11 | fecundidad | 2 | La tarea abre análisis de escenarios y permite comparar modelos y supuestos entre grupos. Además, la contrastación con R4 invita a discutir los límites del modelo. | — |
| 12 | recursos | 2 | La información se obtiene a solicitud o por estimación; montos de proyectos y plazos son buscables por universitarios. Los recursos describen el escenario sin revelar el modelo ni la regla de decisión. | — |
| | **Total** | **23/24** | | |
