# ¿Más seguras o más peligrosas? Dos números que se contradicen

Tarea `2026-11-carceles-mas-seguras-o-peligrosas` · versión 1 · 2026-11-16 · nivel S · 2 sesiones de 90 min. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).

```yaml frontmatter
id: 2026-11-carceles-mas-seguras-o-peligrosas
titulo: ¿Más seguras o más peligrosas? Dos números que se contradicen
estado: verificada
version: 1
fecha: '2026-11-16'
noticia:
  noticia_id: 2026-11-16-latercera-informe-unab-homicidios-en-carceles-caen
  medio: La Tercera
  titulo: 'Informe UNAB: homicidios en cárceles caen a su mínimo, pero agresiones y amenazas alcanzan récord en última década'
  fecha: '2026-11-16'
  url: https://www.latercera.com/nacional/noticia/informe-unab-homicidios-en-carceles-caen-a-su-minimo-pero-agresiones-y-amenazas-alcanzan-record-en-ultima-decada/
  resumen_propio: Un observatorio universitario actualizó su estudio sobre seis delitos al interior de cárceles chilenas, incorporando datos de 2025. Los homicidios bajaron a su nivel más bajo del periodo, mientras las amenazas y agresiones contra internos llegaron a máximos. También se reportan descensos en sobornos y alzas en decomisos de droga, con diferencias entre regiones y recintos.
  cifras_usadas:
  - valor: 27
    unidad: homicidios en 2025
    que_es: Homicidios al interior de penales en 2025, la cifra más baja del periodo analizado
    localizador:
      fuente: noticia
      ubicacion: párrafo 3
  - valor: 491
    unidad: homicidios
    que_es: Total de homicidios en cárceles entre 2015 y 2025
    localizador:
      fuente: noticia
      ubicacion: párrafo 4
  - valor: 56
    unidad: homicidios en 2015
    que_es: Homicidios en cárceles registrados en 2015
    localizador:
      fuente: noticia
      ubicacion: párrafo 4
  - valor: 61
    unidad: homicidios en 2020
    que_es: Máximo de homicidios en cárceles del periodo, registrado en 2020
    localizador:
      fuente: noticia
      ubicacion: párrafo 4
  - valor: 48
    unidad: homicidios en 2024
    que_es: Homicidios en cárceles registrados en 2024
    localizador:
      fuente: noticia
      ubicacion: párrafo 4
  - valor: '2.322'
    unidad: amenazas a internos
    que_es: Registros de amenazas entre 2015 y 2025
    localizador:
      fuente: noticia
      ubicacion: párrafo 7
  - valor: 62
    unidad: amenazas en 2015
    que_es: Casos de amenazas a internos en 2015
    localizador:
      fuente: noticia
      ubicacion: párrafo 7
  - valor: 235
    unidad: amenazas en 2024
    que_es: Casos de amenazas a internos en 2024
    localizador:
      fuente: noticia
      ubicacion: párrafo 7
  - valor: 548
    unidad: amenazas en 2025
    que_es: Casos de amenazas a internos en 2025
    localizador:
      fuente: noticia
      ubicacion: párrafo 7
  - valor: '6.365'
    unidad: agresiones en 2025
    que_es: Agresiones a internos registradas en 2025, máximo histórico
    localizador:
      fuente: noticia
      ubicacion: párrafo 10
  - valor: 9,3%
    unidad: porcentaje
    que_es: Aumento de agresiones en 2025 respecto de 2024
    localizador:
      fuente: noticia
      ubicacion: párrafo 10
nivel_principal: S
sub_tramo: S1
variantes:
  abajo: null
  arriba: S
area: sociedad_datos
contenidos_matematicos:
- variación porcentual
- comparación de escenarios
- ecuaciones de primer grado
- índices ponderados
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
Un observatorio universitario revisó los delitos ocurridos dentro de las cárceles de Chile a lo largo de una década de registros. Entre sus datos hay dos que parecen contar historias distintas: los homicidios, que son hechos gravísimos y menos frecuentes, y las amenazas a internos, que ocurren mucho más seguido. Los números son estos: 56 homicidios en el primer año de la década y 27 homicidios en el último año; 62 casos de amenazas en el primer año y 548 casos de amenazas en el último año. Un medio escolar quiere publicar una nota que responda si, entre el primer y el último año de esa década, las cárceles se volvieron más seguras o más peligrosas para quienes están dentro. ¿Qué conclusión sostendrían ustedes y cómo la justificarían ante alguien que piensa lo contrario? Pueden pedir información adicional.
```

```text foto_descripcion
Ícono de una balanza con dos platillos: en uno hay un candado y en el otro una burbuja de diálogo con un signo de exclamación.
```

### 1.1 Variante hacia abajo

No hay.

### 1.2 Variante hacia arriba (tramo S2)

Se entregan de entrada las agresiones del último año y su aumento respecto del año anterior, y se pide comparar cómo cambia la conclusión al incluir ese indicador. Se exige además justificar por escrito el criterio usado y analizar la sensibilidad de la conclusión frente a la cantidad de internos, que el grupo debe estimar o buscar.

## 2. Datos y recursos no reveladores

| Recurso | Qué es | Contenido | Disponibilidad | Fase que alimenta | Fuente |
|---|---|---|---|---|---|
| R1 | Tabla de partida con los datos de homicidios y amenazas del primer y el último año de la década (la misma que aparece en el enunciado). | Homicidios: 56 en el primer año y 27 en el último año. Amenazas a internos: 62 casos en el primer año y 548 casos en el último año. | de_entrada | P1-MRS | noticia, párrafo 4; noticia, párrafo 3; noticia, párrafo 7 |
| R2 | Dato de agresiones a internos, un tercer indicador de violencia. | Agresiones a internos en el último año: 6.365, el máximo histórico del registro. Es 9,3% más que en el año anterior. | a_solicitud | P2-RM | noticia, párrafo 10 |
| R3 | Datos de otros años de las series de homicidios y amenazas. | Homicidios: 61 en el año de máximo del periodo y 48 en el año anterior al último. Amenazas a internos: 235 casos en el año anterior al último. | a_solicitud | P2-RM | noticia, párrafo 4; noticia, párrafo 7 |
| R4 | Totales acumulados de la década, para contrastar la serie que el grupo haya supuesto. | En toda la década hubo 491 homicidios en cárceles y 2.322 casos de amenazas a internos. | a_solicitud | P6-VAL | noticia, párrafo 4; noticia, párrafo 7 |

Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, la regla ni la estructura de la solución.

## 3. Mapa a priori del ciclo

| Fase | Decisión o actividad esperable | Evidencia observable | Bloqueo probable |
|---|---|---|---|
| P1-MRS Comprender | Entender qué mide cada indicador y qué significa 'más seguras o más peligrosas'; notar que un homicidio y una amenaza no son hechos equivalentes. | El grupo reformula con sus palabras qué entiende por seguridad dentro de una cárcel y escribe qué compara (el primer año con el último de la década). | B12 |
| P2-RM Simplificar | Decidir qué indicadores y años usar, si piden las agresiones o los otros años, y si la gravedad de los hechos cuenta. | Lista escrita de supuestos (por ejemplo, que el registro de amenazas se hace con el mismo criterio cada año; que un homicidio es más grave que una amenaza). | B23 |
| P3-MM Matematizar | Traducir la comparación a matemática: variaciones porcentuales por indicador o un índice que combine homicidios y amenazas con un peso elegido. | Expresión escrita tipo índice = peso x homicidios + amenazas, o tabla de variaciones por indicador. | B34 |
| P4-WM Trabajar | Calcular los cambios, el índice de cada año y probar distintos pesos; buscar el peso a partir del cual cambia la conclusión. | Cálculos con varios valores del peso y, si lo hacen, planteo de una igualdad entre el índice del primer año y el del último. | — |
| P5-INT Interpretar | Traducir los resultados a una conclusión sobre seguridad y decir bajo qué condición vale. | Frase del tipo 'si un homicidio pesa más que X amenazas, el último año es menos violento'. | B56 |
| P6-VAL Validar | Contrastar el criterio con los totales acumulados y con los otros años, y revisar si la conclusión se sostiene al cambiar el peso. | Comparación entre la serie supuesta y los totales de 491 homicidios y 2.322 amenazas; anotación de qué cambia en la conclusión. | B67 |
| P7-EXP Exponer | Redactar la nota para el medio escolar con una conclusión condicionada y una forma de mostrar los datos. | Texto breve o gráfico que muestra ambos indicadores y declara el criterio elegido. | — |

## 4. Espacio de soluciones

> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.

### Supuestos necesarios

- El registro de homicidios y amenazas se hizo con el mismo criterio en el primer y en el último año.
- Hay que acordar cuánto más grave es un homicidio que una amenaza (un peso, que puede variar).
- La cantidad de internos no cambió mucho en la década; si el grupo cree lo contrario, debe estimarla y corregir.
- Las cifras entregadas representan lo ocurrido, aunque la denuncia o el registro pueda haber cambiado.

### Solución de referencia

1) Variaciones por indicador: homicidios (27-56)/56 = -51,8%; amenazas (548-62)/62 = +784%. Las tendencias son opuestas, así que sin criterio la conclusión es 'mixta'. 2) Para decidir hay que ponderar. Sea w las amenazas que 'pesa' un homicidio; índice = w·H + A. Primer año: 56w + 62; último año: 27w + 548. 3) Igualando: 29w = 486, w ≈ 16,8. Si un homicidio pesa más que unas 17 amenazas, el índice del último año es menor (menos violento); si pesa menos, es mayor. Ejemplos: w = 10 da 622 y 818; w = 30 da 1.742 y 1.358. 4) Opcional: incluir agresiones (6.365 en el último año, +9,3% sobre el anterior; sin dato del primer año) y corregir por población de internos (si creció en razón p, el equilibrio es w = (548-62p)/(56p-27); con p = 1,2 queda w ≈ 11,8). 5) Concluir con el criterio explícito y su umbral.

**Resultado.** No hay respuesta única: la violencia letal bajó (-51,8%) y las amenazas subieron (+784%). El punto de equilibrio sin corregir por población es un peso de cerca de 17 amenazas por homicidio; con peso mayor, las cárceles serían menos violentas en el último año; con peso menor, más. Una conclusión defendible es que bajó la violencia letal pero aumentó la violencia no letal.

**Rango aceptable.** Cualquier conclusión que explicite el criterio de ponderación y el umbral (cercano a 17 si no se corrige por población; menor si se supone que la población creció) con cálculos correctos. También es aceptable concluir 'mixto' con evidencia de ambas tendencias.

### Rutas

| Ruta | Nombre | Nivel | Modelo | Resultado |
|---|---|---|---|---|
| R1 | Variaciones porcentuales por indicador | S1 | Cambio porcentual de cada indicador entre el primer y el último año, comparados sin unificarlos. | Homicidios -51,8% y amenazas +784%; conclusión mixta: más seguro frente a muertes, menos frente a amenazas. |
| R2 | Índice ponderado con peso de gravedad | S1 | Índice = w·homicidios + amenazas para cada año; igualar los índices del primer y del último año para hallar w. | w ≈ 16,8; si un homicidio pesa más que ese valor, el último año es menos violento. |
| R3 | Índice por población corregida y con agresiones | S2 | Dividir por una población de internos estimada y supuesta distinta entre el primer y el último año (razón p); sumar agresiones como tercer indicador con otro peso. | Con p = 1,2 el equilibrio baja a w ≈ 11,8; la conclusión depende de p y de los pesos, y el grupo debe informar la sensibilidad. |

### Modelo inadecuado (R4)

Sumar los casos brutos de homicidios y amenazas (118 en el primer año contra 575 en el último) y concluir que hay casi cinco veces más violencia trata un homicidio igual que una amenaza, ignora la gravedad y deja que los casos más frecuentes dominen el resultado.

### Evidencia de validación (independiente del modelo)

Después de proponer su criterio, el grupo recibe los totales acumulados de la década (491 homicidios y 2.322 amenazas) y los otros años que pidió. Con ellos comprueba si su lectura de la serie es consistente: tras restar el primer año, el año de máximo, el año anterior al último y el último, los otros siete años suman 299 homicidios (cerca de 43 por año), y las amenazas de los ocho años no informados suman 1.477. Además contrasta su conclusión con la lectura del propio observatorio (homicidios en su mínimo, amenazas y agresiones en máximos), que no usó para construir su criterio.

## 5. Rúbrica aplicada (RUB01)

| # | Criterio | Puntaje | Justificación | Mejora mínima si < 2 |
|---|---|---|---|---|
| 1 | genuino | 2 | Plantea una necesidad real: decidir y comunicar una conclusión. No entrega ninguna regla ni modelo para combinar indicadores que van en sentidos opuestos. | — |
| 2 | abierta | 2 | La pregunta admite varias conclusiones y caminos defendibles: cambio absoluto o relativo, ponderación por gravedad, tendencia de la serie. No hay instrucciones que prescriban el método. | — |
| 3 | decisiones | 2 | Resolver exige decidir qué significa «más seguro», cómo comparar hechos de distinta gravedad y frecuencia y qué información adicional pedir. Son supuestos y selecciones sustantivas. | — |
| 4 | realismo | 2 | La situación existe fuera de la escuela: hay datos reales de violencia carcelaria y un medio que quiere informar sobre ellos. | — |
| 5 | autenticidad | 2 | Los datos provienen de un registro declarado de un observatorio universitario y son el núcleo de la tarea. El componente auténtico está integrado de manera sustantiva. | — |
| 6 | contexto | 2 | El contexto condiciona cómo ponderar homicidios frente a amenazas. También es necesario para interpretar la conclusión y defenderla ante quien piensa lo contrario; no puede abandonarse tras calcular. | — |
| 7 | ciclo | 2 | Responder obliga a recorrer el ciclo completo: comprender la situación, definir un criterio de seguridad, matematizarlo (variaciones, ponderaciones), calcular, interpretar y defender la conclusión. Ninguna fase queda hecha por el enunciado. | — |
| 8 | validacion | 2 | Hay evidencia independiente para contrastar el modelo: un tercer indicador (R2), datos de años intermedios (R3) y totales de la década (R4), ninguno usado en su construcción inicial. | — |
| 9 | nivel | 2 | El contexto es comprensible y de relevancia cívica para estudiantes de 13 a 15 años. La matemática requerida (razones, variación porcentual, promedios ponderados simples) está al alcance de las herramientas de S1. | — |
| 10 | autodiferenciacion | 2 | El piso es razonable: basta comparar diferencias o razones con operatoria elemental. El techo es alto, porque la tarea admite índices ponderados por gravedad, análisis de tendencia con los datos intermedios y discusión de varios indicadores. | — |
| 11 | fecundidad | 2 | La tensión entre indicadores abre preguntas de fondo: cómo medir la seguridad, efectos del registro de denuncias y qué indicador privilegiar. También permite comparar conclusiones opuestas entre grupos. | — |
| 12 | recursos | 2 | Los datos necesarios están en el enunciado y la información complementaria se puede solicitar (R2–R4) sin que ningún material revele una forma de combinar los indicadores. La población penal no se entrega, pero la conclusión puede sostenerse sin ese dato. | — |
| | **Total** | **24/24** | | |
