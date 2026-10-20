# MAR03 – Niveles de uso (10–20 años)

| Campo | Valor |
|---|---|
| Versión | v1.0 (v0.1: cuatro tramos A–D; v1.0: tres niveles P/S/U por decisión de Carlos, 2026-10-20, con sub-tramos de edad dentro de S) |
| Fecha | 2026-10-20 |
| Uso | (1) El diseñador declara `nivel_principal` y `variantes`; (2) el evaluador aplica el criterio 9 de RUB01 y P1–P5 de RUB02 contra el descriptor del nivel; (3) el adapter del simulador genera los textos de perfil `niveles` (INS08) desde §3 |
| Relación | INS08 §2 (N1–N4 son niveles de competencia *dentro* de un curso; se cruzan con P/S/U) |
| Principio | Se declara por edad para no amarrar el banco a un sistema educativo. Las correspondencias con Chile son orientativas |

## 1. Niveles

| Nivel | Edad | Orientativo (Chile) | Herramientas matemáticas esperables | Demanda típica de la tarea | Supuestos | Validación esperable |
|---|---|---|---|---|---|---|
| **P** Primaria | 10–12 | 5°–7° básico | Operatoria, proporcionalidad directa, porcentajes simples, gráficos de barras, estimación y unidades | Un modelo aditivo o proporcional con datos dados en la noticia; una incógnita clara | Uno, explícito y acordado en grupo | Comparar con una cifra de la noticia o con una medición simple |
| **S** Secundaria | 13–18 | 8° básico – 4° medio | Ver sub-tramos | Elegir qué datos usar; comparar escenarios; elegir entre modelos | Dos o más, formulados por el grupo | Contrastar con otra fuente o dato posterior |
| S1 | 13–15 | 8° básico – 1° medio | Razones y tasas, función lineal, ecuaciones de primer grado, promedio, escala | Modelo lineal o de tasa; comparar dos escenarios | Dos o tres | Un segundo dato u otra fuente |
| S2 | 16–18 | 2°–4° medio | Funciones no lineales (exponencial, cuadrática), estadística descriptiva, optimización simple, trigonometría | Varios supuestos en competencia; lineal vs. exponencial; análisis de qué pasa si | Varios, jerarquizados | Evidencia independiente; sensibilidad informal |
| **U** Universitario | 18–20 | 1°–2° año | Álgebra lineal, cálculo, probabilidad, modelos dinámicos discretos, optimización con restricciones, programación | Modelo dinámico, probabilístico o de optimización; sensibilidad; crítica del modelo | Explícitos, discutidos y revisados tras validar | Datos nuevos; límites del modelo; comparación de modelos alternativos |

Una tarea declara **P, S o U** como nivel principal. Dentro de S, el diseñador indica el sub-tramo (S1 o S2) solo cuando la demanda matemática lo exige; si la tarea funciona en todo S, no se subdivide.

## 2. Reglas para el diseñador

1. Toda tarea declara un nivel principal y, si es posible, una variante hacia abajo y otra hacia arriba. Una variante cambia los datos entregados, la pregunta o la demanda de validación, **no** el contexto.
2. Una tarea cuyo contexto es inaccesible para un nivel (vocabulario, experiencia de vida) no se "baja" con andamiaje: se declara solo para los niveles donde el criterio 9 puntúa 2.
3. En U, la exigencia de contenido curricular va en la consigna del curso, nunca dentro del enunciado (Borromeo Ferri, 2018, cap. 3: la tarea no prescribe el método).
4. Las tareas-oro ubican los extremos: St. Michael's Church (P), Port of Hamburg / Lighthouse / Sugarloaf (S), población belga (U).

## 3. Perfiles de estudiante simulado por nivel (semillas para INS08 `niveles`)

Plantilla: "Tienes {edad} años. {frase de confianza según N1–N4}. Manejas {herramientas del nivel, versión N}. {Experiencia con problemas abiertos según contexto_base}."

| Nivel | N1 (bajo) | N4 (alto) |
|---|---|---|
| P | Operaciones básicas con errores en decimales; porcentajes solo con calculadora; te cuesta leer tablas | Operaciones y porcentajes con soltura; lees gráficos y tablas; estimas antes de calcular |
| S1 | Proporciones con ayuda; confundes tasa con cantidad; sin fórmulas de memoria | Proporciones, función lineal y ecuaciones con soltura; interpretas pendiente como tasa |
| S2 | Funciones solo como fórmulas; no distingues lineal de exponencial en datos | Eliges modelo según los datos; usas estadística descriptiva; haces análisis de qué pasa si |
| U | Cálculo y álgebra lineal mecánicos; sin experiencia en modelar | Modelas con herramientas del curso; discutes supuestos; conoces límites de un modelo |

## 4. Abierto (no bloquea)

- Si U se separa más adelante en U-general y U-pedagogía (estándares FID como referencia de P1), se hace como etiqueta adicional, sin cambiar los niveles.
