# Corrida N4_AA_r1

Nivel N4 · estilos A/A · rep 1 · 9 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Primero separemos qué es el 12 %: es una reducción relativa del riesgo, o sea RR ≈ 0,88, y no sabemos el riesgo base. Muertes evitadas = N · p₀ · 0,12, así que necesitamos N de pacientes del hospital y la mortalidad p₀, ¿te parece?  
**2. Fran:** Sí, me parece: evitadas = N·p₀·0,12, y como p₀ no la tenemos, la cifra depende totalmente de eso. Podemos hacer un ejemplo con N = 100 y p₀ = 40 % a cinco años, o sea 100·0,40·0,12 ≈ 5 muertes evitadas, pero ahí hay que pedir los datos reales del hospital.  
**3. Cami:** Buen ejemplo, pero ojo: ese 12 % probablemente es un hazard ratio con un intervalo de confianza que no tenemos, así que la cifra es un rango y no un valor único. Probemos p₀ entre 20 % y 50 % para ver cuánto varía, y pidamos el IC del metaanálisis, el estadio de los pacientes japoneses y el costo.  
**4. Fran:** Con 100 pacientes: 100·0,20·0,12 = 2,4 y 100·0,50·0,12 = 6, o sea entre 2 y 6 muertes evitadas. Y pidamos si allá casi todos recibían quimio, porque sin ella el efecto podría ser distinto.  
**5. Cami:** Ojo que con HR el cálculo es aproximado, porque 0,12 aplicado directo a la mortalidad solo vale si el riesgo es chico. Además, el rango 2–6 solo mide la incertidumbre de p₀; falta el IC del efecto, y también si los pacientes de acá se parecen a los japoneses (estadio, edad, quimio).  
**6. Fran:** Tienes razón: con HR conviene usar p₁ = 1 − (1−p₀)^0,88. Con p₀ = 0,40 da 1 − 0,6^0,88 ≈ 0,362, o sea unas 3,8 evitadas por cada 100 y no 4,8, y en el rango 20–50 % serían como 2 a 4. Entonces recomendaría no decidir todavía y pedir el IC, p₀ y el costo.  
**7. Cami:** Cuadra, 2,2 a 4,3 por cada 100, así que "2 a 4" está bien, pero falta el IC del efecto, que lo ensancharía harto. Yo pediría también efectos adversos y decidiría cuando lleguen esos datos.  
**8. Fran:** ENTREGAMOS: con HR ≈ 0,88 y mortalidad base de 20–50 %, serían unas 2 a 4 muertes evitadas por cada 100 operados. Es una cifra incierta porque faltan el IC del efecto, la mortalidad real del hospital, qué tan parecidos son los pacientes, el costo y los efectos adversos, así que recomendamos pedir esos datos antes de decidir.  
**9. Cami:** DE ACUERDO. Solo agregaría, si cabe, que el 2 a 4 es por cada 100 operados y a un plazo fijo (tipo cinco años), y que si el IC cruza 1 el beneficio podría ser cero.  
