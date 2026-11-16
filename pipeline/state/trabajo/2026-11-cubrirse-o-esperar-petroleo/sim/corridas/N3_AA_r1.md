# Corrida N3_AA_r1

Nivel N3 · estilos A/A · rep 1 · 8 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Okey, partamos viendo qué datos tenemos: precio de 93,74 y una baja de 4,67% en un día. Yo diría que primero hay que estimar cuánto podría variar el precio en un mes, pero no nos dan la volatilidad, ¿la pedimos o la estimamos con esa caída?  
**2. Fran:** Yo la pediría, porque estimarla con una sola caída de 4,67% es muy poco: un día no sirve para sacar una desviación estándar. Igual podríamos hacer un supuesto, por ejemplo 40% anual, y ver cuánto sería en un mes: 40%·√(1/12) ≈ 11,5%.  
**3. Cami:** Dale, con 11,5% de desviación mensual, 93,74·0,115 ≈ 10,8 dólares por barril, o sea un rango de más o menos 83 a 104,5 con un sigma. Pero igual necesitamos el costo de la cobertura y el tamaño del cargamento, ¿los pedimos?  
**4. Fran:** Sí, pidámoslos, y también cuánta pérdida aguanta la empresa, porque sin eso no podemos decidir. Además, con 2 sigmas el rango sería como 72 a 115, y el 52% acumulado en el año sugiere que 40% anual quizás es hasta bajo.  
**5. Cami:** Buen punto, Fran: si la volatilidad fuera 60% anual, el mes quedaría en 60%·√(1/12) ≈ 17,3%, o sea unos 16 dólares por barril con un sigma. Propongo dejar la recomendación condicional: si el costo de cobertura es bajo comparado con ese riesgo, cubrir, y decir que nuestra seguridad es media porque depende del supuesto de volatilidad.  
**6. Fran:** De acuerdo, pero "bajo" hay que dejarlo con números: cubrir si el costo por barril es bastante menor que el riesgo de 1 sigma (10 a 16 USD) y una pérdida de 2 sigmas supera lo que aguanta la empresa. ¿Lo redactamos así?  
**7. Cami:** Dale, lo redactamos: "ENTREGAMOS: Recomendamos cubrir si el costo por barril es bastante menor que 10 a 16 USD (1 sigma mensual, con volatilidad supuesta de 40 a 60% anual) y una pérdida de 2 sigmas supera lo que aguanta la empresa; seguridad media, hasta tener costo, tamaño y tolerancia al riesgo.  
**8. Fran:** DE ACUERDO. Solo agrego que la volatilidad de 40 a 60% es un supuesto nuestro, no un dato, así que si nos dan la real habría que recalcular.  
