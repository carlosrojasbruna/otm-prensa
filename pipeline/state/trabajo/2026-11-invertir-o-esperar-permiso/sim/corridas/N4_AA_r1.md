# Corrida N4_AA_r1

Nivel N4 · estilos A/A · rep 1 · 10 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Okey, esto es un problema abierto: no nos dan ni el costo del proyecto ni la probabilidad del permiso. Propongo definir variables: C = costo de preparación, p = probabilidad de aprobación, T = tiempo de tramitación, y comparar el valor esperado de empezar ahora versus esperar.  
**2. Fran:** Dale, pero ojo con que el valor esperado solo no basta, porque si el permiso no sale el gasto C se pierde entero. Yo plantearía VE(empezar) = p·V·e^(-rT') − C contra VE(esperar) = p·V·e^(-r(T+L)), donde L es el retraso de preparar después. ¿Te parece?  
**3. Cami:** Me parece, pero ojo que en "esperar" tampoco gastas C si el permiso no sale: deberías restar p·C·e^(-rT), porque solo lo gastas si lo aprueban. Entonces empezar conviene si p·V·e^(-rT)(1−e^(-rL)) > C(1−p·e^(-rT)), ¿lo revisamos?  
**4. Fran:** Lo revisé y cuadra: start − wait = p·V·e^(-rT)(1−e^(-rL)) − C(1−p·e^(-rT)). Si los trámites se aceleran, baja T y sube p, así que el lado izquierdo crece y el derecho se achica, o sea conviene empezar antes. Nos falta fijar C como porcentaje de los 1.000 millones, para no arriesgar demasiado si el permiso no sale.  
**5. Cami:** Pongamos números supuestos: V = 3.000 millones, r = 10%, T = 2 años, L = 1 año y p = 0,6. Entonces 0,6·3000·e^(-0,2)·(1−e^(-0,1)) ≈ 140 y 1−0,6·e^(-0,2) ≈ 0,51, así que empezar conviene si C < ~275 millones, o sea como un 27% de las utilidades. ¿Te parece tanto, o le ponemos un tope menor por el riesgo?  
**6. Fran:** Los números me cuadran, pero 275 es solo el punto de indiferencia, no un tope. Con p = 0,3 me da C < ~93 millones, o sea 9%, así que es muy sensible a p y yo pondría un tope de 10-15%.  
**7. Cami:** Concuerdo con el tope de 10-15%, porque ahí manda el riesgo y no el punto de indiferencia. Si los trámites se aceleran, con T = 1 y p = 0,8 me da 2400·e^(-0,1)·(1−e^(-0,1)) ≈ 207 y 1−0,8·e^(-0,1) ≈ 0,28, o sea C < ~750 millones, así que ahí el tope se haría más holgado. ¿Lo revisas?  
**8. Fran:** Revisé y me da igual: ≈207 y 0,28, o sea C < ~750 millones. Pero eso es 75% de las utilidades, así que yo no subiría el tope a ese nivel, quizás a 15-20%, porque seguimos con incertidumbre en p y en V.  
**9. Cami:** De acuerdo con 15-20%, y de paso pediríamos el costo real y la probabilidad del permiso. ENTREGAMOS: empezar si p·V·e^(-rT)(1−e^(-rL)) > C(1−p·e^(-rT)), con tope de 10-15% de las utilidades, y 15-20% si los trámites se aceleran.  
**10. Fran:** DE ACUERDO. Solo agregaría a la respuesta que los números salen de supuestos (V = 3.000, r = 10%, p, T) y que pedimos el costo real del proyecto y la probabilidad del permiso para afinar el tope.  
