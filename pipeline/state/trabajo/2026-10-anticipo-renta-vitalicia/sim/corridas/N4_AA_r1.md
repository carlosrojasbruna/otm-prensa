# Corrida N4_AA_r1

Nivel N4 · estilos A/A · rep 1 · 11 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo lo plantearía como equivalencia actuarial: el anticipo, que sería 10% de la renta vitalicia, tiene que ser igual al valor presente esperado de los descuentos, o sea d·Σ v^t·tpx durante n meses. ¿Te parece si primero definimos qué es "la renta vitalicia" acá, si anual o mensual, y pedimos una tasa de descuento y una tabla de mortalidad?  
**2. Fran:** Sí, y ojo: si "10% de la renta" fuera 10% de la pensión mensual, el anticipo sería mínimo, así que yo lo tomaría como 10% del valor presente de la renta, A = 0,1·R·ä_x. Entonces la regla sería d·ä_{x:n} = A, con una sola ecuación y dos incógnitas, d y n.  
**3. Cami:** Ahí hay que tener cuidado: con d·ä_{x:n} = 0,1·R·ä_x, el descuento mensual sale d = 0,1·R·ä_x / ä_{x:n}, así que fijando n despejamos d. Pero ojo, d no puede pasar de R, entonces n tiene un mínimo, y ahí aparece la restricción de que la persona no se quede sin pensión.  
**4. Fran:** Claro, y el mínimo de n sale de d < R, o sea ä_{x:n} > 0,1·ä_x; con eso ya tenemos el piso, pero en la práctica pondría un tope más bajo, tipo d ≤ 20% de R. Y la firmeza depende de la tasa de descuento y de la tabla de mortalidad, así que habría que hacer sensibilidad, ¿te parece?  
**5. Cami:** Sí, hagamos sensibilidad: con d ≤ 0,2·R sale ä_{x:n} ≥ 0,5·ä_x, y ahí n cambia harto según la tasa i y la tabla. Además, la tabla debería ser la del pensionado, no la general, porque los pensionados viven más y eso mueve el equilibrio, ¿lo probamos con i = 3% y otro valor?  
**6. Fran:** Probemos con un modelo simple: mortalidad constante, con supervivencia anual p = 0,96, así ä_{x:n}/ä_x = 1 − q^n con q = v·p. Entonces d ≤ 0,2R pide q^n ≤ 0,5, o sea n ≥ ln2/(−ln q), que da unos 9,8 años con i = 3% y 7,7 años con i = 5%.  
**7. Cami:** Me cuadran tus números: d/R = 0,1/(1−q^n) no depende de R, y que n cambie casi 2 años entre 3% y 5% ya muestra que la regla es sensible. Pero p = 0,96 constante es muy grosero para un pensionado, así que probemos con p = 0,98 y vemos cuánto se mueve n.  
**8. Fran:** Con p = 0,98 me sale q = 0,98/1,03 = 0,951, o sea ln q ≈ −0,0499 y n ≈ 0,693/0,0499 ≈ 13,9 años con i = 3%. Con i = 5%, q = 0,933 y n ≈ 10,0 años. Ahora la brecha entre tasas es de casi 4 años, así que la regla es aún más sensible.  
**9. Cami:** Al revés, con n = 10 años y p = 0,98, d/R = 0,1/(1−q¹⁰) sale 25% con i = 3% y 20% con i = 5%. La regla es sensible, así que la entregaría con la tasa y la tabla oficiales como supuestos explícitos, ¿te parece?  
**10. Fran:** De acuerdo. ENTREGAMOS: d = 0,1·R/(1−qⁿ), con q = p/(1+i) y n tal que d ≤ 0,2R, y es sensible a la tasa, a la tabla del pensionado y a que el anticipo sea 10% del valor presente.  
**11. Cami:** DE ACUERDO. Dejaría anotado que el 20% de tope es un criterio nuestro, no viene de la norma, y que con p constante el modelo es solo una aproximación.  
