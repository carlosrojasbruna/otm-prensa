# Corrida N1_AA_r1

Nivel N1 · estilos A/A · rep 1 · 15 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Uf, este problema no trae datos como los de siempre... ¿Será que primero tenemos que calcular a cuánto estaba el barril antes de que bajara el 4,67%? Yo partiría por ahí, paso a paso.  
**2. Fran:** Ya, dale. Si bajó 4,67% y quedó en 93,74, entonces x·(1 − 0,0467) = 93,74, o sea x = 93,74 / 0,9533, ¿lo calculo con la calculadora?  
**3. Cami:** Sí, calcúlalo: 93,74 / 0,9533, que debería dar como 98,33. Pero igual no sé si eso nos sirve para recomendar algo, ¿qué más necesitaríamos, cuánto cuesta la cobertura?  
**4. Fran:** Dale, me dio 98,33 igual que tú. Y sí, necesitamos saber cuánto cuesta la cobertura y cuánto es el cargamento, porque sin eso no podemos comparar nada; también habría que ver cuánto puede variar el precio en un mes, pero no sé cómo sacar eso.  
**5. Cami:** Pensé que quizás podríamos usar el 4,67% como cuánto se mueve el precio en un día, y para un mes multiplicarlo por 30, que da como 140%. Pero eso suena exagerado, ¿no? No sé si se hace así.  
**6. Fran:** Yo tampoco creo que sirva multiplicar por 30, porque ese 4,67% fue un día excepcional, o sea la peor semana desde la pandemia. ¿Y si usamos el 52% del año dividido en 12, que da 52/12 ≈ 4,33% al mes, como una variación típica?  
**7. Cami:** Ya, hagamos 93,74 · 0,0433 ≈ 4,06, o sea el barril estaría entre 89,68 y 97,80 en un mes. Pero ojo, ese 52% es lo que subió en el año, no cuánto se mueve para arriba y para abajo, ¿no te parece que mezcla cosas distintas?  
**8. Fran:** Mmm, tienes razón, el 52% es una tendencia de subida y no cuánto oscila, así que ese rango de 89,68 a 97,80 no sirve mucho. Quizás podríamos pedirle al gerente datos de cómo ha variado el precio mes a mes, o armar escenarios como "sube 10%" y "baja 10%" para ver cuánto pierde la empresa en cada caso.  
**9. Cami:** Me gusta lo de los escenarios, porque así al menos podemos calcular algo: 93,74 · 1,10 = 103,11 y 93,74 · 0,90 = 84,37 por barril. Pero igual no sé de dónde sacamos el 10%, ¿y si pedimos también cuántos barriles son y cuánto cobra el banco?  
**10. Fran:** Sí, pidámosle eso al gerente, y también cuánta pérdida aguanta la empresa. Mientras, podemos dejar los barriles como "N": si sube 10% pagarían N·(103,11 − 93,74) = N·9,37 más, y si baja ahorrarían N·9,37.  
**11. Cami:** Entonces si el banco cobra c por barril, cubrirse cuesta N·c seguro, y el riesgo sin cubrirse sería hasta N·9,37 más. ¿Armamos la recomendación como "depende": si c es menor que 9,37 conviene cubrirse, y aclaramos que el 10% es un supuesto?  
**12. Fran:** Mmm, no sé si "c menor que 9,37" sea tan directo, porque si el precio baja igual ahorrarían N·9,37 sin cobertura, y con 10% arriba o abajo en promedio quedan parejos, así que la cobertura sería solo pagar por tranquilidad. Yo diría que depende de cuánta pérdida aguanta la empresa, y que el 10% es supuesto, ¿lo escribimos así?  
**13. Cami:** Ya, entiendo: cubrirse es pagar N·c seguro para evitar perder hasta N·9,37. ¿Escribimos que recomendamos cubrir solo si la empresa no aguanta esa pérdida, con seguridad baja porque el 10% es supuesto?  
**14. Fran:** ENTREGAMOS: Recomendamos cubrirse solo si la empresa no aguanta perder hasta N·9,37 (supuesto de ±10%) y el costo N·c le parece razonable; si aguanta esa pérdida, conviene esperar. Seguridad baja, porque el 10% es supuesto y falta saber N, c y cuánto riesgo tolera, así que se los pedimos al gerente.  
**15. Cami:** DE ACUERDO. Solo agregaría, si te parece, que con N·9,37 estamos suponiendo que el precio de hoy es el de referencia, y eso también es un supuesto.  
