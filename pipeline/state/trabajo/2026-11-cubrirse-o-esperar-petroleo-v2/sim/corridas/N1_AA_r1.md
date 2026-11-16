# Corrida N1_AA_r1

Nivel N1 · estilos A/A · rep 1 · 16 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Mmm, no sé bien por dónde partir, porque no nos dan ni cuánto cuesta la cobertura ni cuántos barriles compra la empresa. ¿Te parece si primero anotamos qué datos tenemos, como el 93,74 y el 4,67%, y vemos qué falta?  
**2. Fran:** Ya, dale. Anotemos: precio actual 93,74, bajó 4,67% en un día, y en el año sube 52%. Con eso podría calcular el precio de ayer: 93,74 / (1 − 0,0467), ¿cierto?  
**3. Cami:** Sí, porque 93,74 es el 95,33% del precio de ayer. Me da 93,74 / 0,9533 ≈ 98,33, o sea que bajó como 4,59 dólares, pero ¿eso de qué nos sirve para decidir?  
**4. Fran:** Mmm, no sé si nos sirve mucho para decidir, pero al menos nos dice cuánto se mueve en un día: 4,59 dólares. Si eso se repitiera todos los días, en un mes ¿no podría moverse un montón? ¿Cómo calculamos eso?  
**5. Cami:** Podríamos hacer 4,59 × 30 = 137,7, pero eso supone que baja todos los días, y no creo que sea así. ¿Habrá alguna fórmula para la variación en un mes, o pedimos algún dato de cuánto suele variar?  
**6. Fran:** Yo creo que mejor pedimos el dato de cuánto suele variar al mes, porque inventar una fórmula sin eso nos va a salir mal. Y también el costo de la cobertura y cuántos barriles compra, así podemos comparar los dos casos con números.  
**7. Cami:** Ya, pidamos esos tres datos: volatilidad mensual, costo de la cobertura y barriles. Mientras tanto, supongamos algo para probar, por ejemplo que el precio varía ±10% en un mes: 93,74 × 0,10 ≈ 9,37 dólares por barril, ¿te parece?  
**8. Fran:** Ya, probemos con ±10%: el precio quedaría entre 93,74 − 9,37 = 84,37 y 93,74 + 9,37 = 103,11. Pero ¿cómo comparamos eso con el costo de la cobertura si no sabemos cuánto cuesta, supongamos 2 dólares por barril?  
**9. Cami:** Entonces con cobertura pagaríamos 93,74 + 2 = 95,74 por barril seguro, y sin cobertura entre 84,37 y 103,11. O sea, la cobertura conviene solo si el precio sube sobre 95,74, ¿o lo estoy mirando mal?  
**10. Fran:** Yo creo que está bien: el punto de equilibrio es 95,74, y sin cobertura el peor caso sería 103,11, o sea 7,37 más por barril que con cobertura. Pero entonces la decisión depende de cuántos barriles son y de cuánta pérdida aguanta la empresa, ¿no?  
**11. Cami:** Sí, eso mismo. Pongámosle un ejemplo: si fueran 100.000 barriles, el peor caso sería 7,37 × 100.000 = 737.000 dólares más caro, ¿y el mejor caso? 95,74 − 84,37 = 11,37 por barril, o sea 1.137.000 dólares de ahorro sin cobertura.  
**12. Fran:** Me cuadran las cuentas, pero esos extremos son solo si el precio llega justo al ±10%, y no sabemos qué tan probable es cada caso. ¿Recomendamos cobertura si la empresa no aguanta perder 737.000, y decimos que es poco segura porque supusimos todo?  
**13. Cami:** Sí, escribámoslo como condición: si 7,37 × barriles es más de lo que aguanta la empresa, recomendamos cobertura, y si no, esperar. Y decimos que es poco segura porque el ±10% y los 2 dólares los inventamos nosotros, ¿lo anotamos así?  
**14. Fran:** Ya, pero fíjate que además hay que decir qué datos faltan: volatilidad, costo real de la cobertura y barriles. ¿Escribimos ENTREGAMOS con la condición 7,37 × barriles > lo que aguanta la empresa → cobertura, y aclaramos que es poco segura porque los números son supuestos?  
**15. Cami:** ENTREGAMOS: si 7,37 × barriles supera lo que aguanta la empresa, cobertura; si no, esperar. Es poco segura porque el ±10% y los 2 dólares son supuestos, y faltan volatilidad, costo real y barriles.  
**16. Fran:** DE ACUERDO  
