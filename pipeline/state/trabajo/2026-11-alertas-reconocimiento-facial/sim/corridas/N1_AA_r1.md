# Corrida N1_AA_r1

Nivel N1 · estilos A/A · rep 1 · 20 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Uf, esto no trae ningún dato, ¿no? Yo creo que primero habría que saber qué tan preciso es el sistema, como un porcentaje de acierto, ¿pedimos ese dato?  
**2. Fran:** Sí, pidamos el porcentaje, pero ¿acierto de qué? Porque no es lo mismo que reconozca bien a alguien que está en la base que que no se equivoque con alguien que no está, ¿no?  
**3. Cami:** Ah, tienes razón, son como dos porcentajes distintos... ¿Entonces pedimos uno de "reconoce bien a los que sí están" y otro de "se equivoca con los que no están"? Igual no sé cómo juntarlos para saber si la alerta es confiable.  
**4. Fran:** Sí, esos dos. Y creo que también falta saber cuánta gente de las que pasan está realmente buscada, porque si son muy pocas, igual la mayoría de las alertas podrían ser errores, ¿no?  
**5. Cami:** Ah, o sea que hay que pedir un tercer dato, la proporción de gente buscada entre los que pasan. ¿Y si probamos con números inventados, tipo 1 de cada 10.000 buscado y 1% de falsas alarmas, a ver qué sale?  
**6. Fran:** Dale, pero falta el de reconocer bien a los buscados, pongamos 90%. Si pasan 100.000, buscados serían 10, o sea 9 alertas bien, y falsas alarmas 1% de 99.990 ≈ 1.000, así que 9/(9+1000) ≈ 0,9%, ¿no?  
**7. Cami:** A ver, 1% de 99.990 es 999,9 y 9/1009 me da 0,0089, o sea casi 0,9%, me sale igual que a ti. ¿Entonces de cada 100 alertas solo 1 sería real, aunque el sistema acierte 90%?  
**8. Fran:** Sí, de cada 100 alertas solo como 1 sería real, y eso con puros números inventados. Entonces la confianza depende de esos tres datos: si la falsa alarma baja a 0,01% o hay más buscados entre los que pasan, ¿no debería subir ese porcentaje? ¿Lo probamos con esos valores?  
**9. Cami:** Dale, con 0,01% de falsas alarmas serían 0,0001 × 99.990 ≈ 10, y 9/(9+10) = 9/19 ≈ 0,47, o sea casi 47%. ¿O sea que igual casi la mitad de las alertas serían errores?  
**10. Fran:** Sí, casi la mitad serían errores, 9/19 ≈ 47%. Probemos ahora con 1 de cada 1.000 buscados y 0,01% de falsas alarmas: serían 100 buscados, 90 alertas buenas y 0,0001 × 99.900 ≈ 10 falsas, o sea 90/100 = 90%, ¿no?  
**11. Cami:** Sí, 90/(90+10) = 0,9, o sea 90%, subió desde 47% con la misma falsa alarma. ¿Entonces recomendamos tomarla en serio solo si hay bastantes buscados y pocas falsas alarmas?  
**12. Fran:** Sí, pero me quedé pensando que la base es de 3,5 millones de caras, y si el 0,01% fuera por cada comparación, serían 0,0001 × 3.500.000 = 350 falsos candidatos por persona, ¿no? Habría que preguntar si la falsa alarma se cuenta por comparación o por persona.  
**13. Cami:** Ay, a ver: 0,0001 × 3.500.000 = 350, sí me da igual. Entonces si es por comparación, sería un desastre y lo que calculamos antes no valdría, así que pidamos también ese dato, ¿no?  
**14. Fran:** Sí, pidamos ese cuarto dato también, porque si son 350 falsos candidatos por persona, casi ninguna alerta sería real. ¿Armamos la respuesta con los cuatro datos y la condición de pocas falsas alarmas y más buscados?  
**15. Cami:** Dale, armémosla: pedimos acierto con buscados, falsas alarmas (por comparación o por persona), proporción de buscados y la base. ¿Ponemos que la alerta solo vale si la probabilidad de que sea real pasa, no sé, 90%?  
**16. Fran:** Lo del 90% no sé, es medio arbitrario; yo diría que depende de qué se haga con la alerta, y que siempre la verifique una persona. ¿Escribimos la fórmula P(real) = acertados/(acertados + falsas) con los cuatro datos?  
**17. Cami:** Ya, tienes razón, mejor no inventar el 90% y que dependa de qué se haga con la alerta y de que siempre la verifique una persona. Pongamos P(real) = a·p / (a·p + f·(1−p)), con a = acierto con buscados, f = falsas alarmas y p = proporción de buscados, ¿te parece?  
**18. Fran:** Sí, la probé con los primeros números: 0,9·0,0001 / (0,9·0,0001 + 0,01·0,9999) ≈ 0,0089, igual que antes. Anotemos que f tiene que ser por persona, y que si el dato viene por comparación hay que multiplicarlo por los 3.500.000 de la base, ¿armamos el ENTREGAMOS así?  
**19. Cami:** ENTREGAMOS: Pedimos acierto con buscados (a), falsas alarmas por persona (f; si viene por comparación, multiplicar por 3.500.000), proporción de buscados (p). P(real) = a·p/(a·p + f·(1−p)); la alerta se toma en serio solo si P(real) es alta y siempre la verifica una persona.  
**20. Fran:** DE ACUERDO  
