# Corrida N1_AA_r1

Nivel N1 · estilos A/A · rep 1 · 19 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Uf, esto no trae datos como los problemas de siempre... ¿Te parece si primero anotamos qué sabemos: arancel de 50%, 30 días de espera, y la bodega que cuesta y se echa a perder?  
**2. Fran:** Sí, dale, anotemos eso. Pero yo diría que ya hay un dato que falta: ¿cuánto queso compra al mes? Sin eso no podemos calcular nada, ¿o inventamos un número?  
**3. Cami:** Mmm, la tarea dice que podemos pedir información, pero no tenemos a quién... Yo diría que pongamos una letra, como Q toneladas al mes y un precio p, y armamos las fórmulas con eso, y después vemos si le damos un número.  
**4. Fran:** Dale, Q toneladas al mes y p el precio por tonelada. Entonces sin arancel el gasto mensual sería Q·p, y con arancel Q·p·(1+0,5) = 1,5·Q·p, ¿te parece?  
**5. Cami:** Sí, eso está bien: 1,5·Q·p. Entonces comprar antes del arancel te ahorra 0,5·Q·p por cada mes que adelantas, pero ahí la bodega cobra, ¿le ponemos una letra c por tonelada al mes para el costo de guardar?  
**6. Fran:** Dale, c por tonelada al mes. Entonces si adelanto un mes de compra, ahorro 0,5·Q·p pero pago c·Q de bodega, así que conviene adelantar mientras 0,5·p > c, ¿no?  
**7. Cami:** Sí, pero falta lo que se echa a perder: pongamos una fracción s por mes, entonces perdés s·p por tonelada y la condición sería 0,5·p > c + s·p, ¿no? Y además el queso que adelantas dos meses se guarda dos meses, así que el costo se acumula: 2c + 2s·p.  
**8. Fran:** Ojo, creo que el ahorro no se multiplica: por cada tonelada que compro antes me ahorro 0,5·p una sola vez, pero el costo sí crece con los meses k, o sea k·(c + s·p). Entonces conviene adelantar mientras k·(c + s·p) < 0,5·p, o sea k < 0,5·p / (c + s·p), ¿lo ves igual?  
**9. Cami:** Ah sí, tienes razón, el ahorro de 0,5·p se gana una sola vez y el costo es el que crece con k. Dividiendo por p queda k < 0,5/(c/p + s), ¿probamos con c/p = 2% y s = 3% al mes para ver cuánto da?  
**10. Fran:** Dale: 0,5/(0,02+0,03) = 0,5/0,05 = 10 meses, pero eso me parece demasiado, ¿no? La bodega tiene poco espacio y el arancel arranca en 30 días, así que quizás el límite real es la capacidad y no esta fórmula.  
**11. Cami:** Puede ser, porque el 10 es solo si la bodega no tiene límite, así que pongamos una capacidad B toneladas y compramos adelantado min(k·Q, B). Pero además los pedidos cambian cada mes, ¿no? Entonces quizás Q no es fijo y hay que usar una demanda promedio.  
**12. Fran:** Dale, usemos Q como el promedio mensual, pero ojo que si un mes piden menos de Q me queda queso sobrando pagando bodega y echándose a perder. Entonces adelantaría min(k·Q, B), y k tendría que ser chico, ¿no?  
**13. Cami:** Sí, y además hay que ver la segunda parte: si todas las importadoras hacen lo mismo, ¿cuánto sería en plata? Podríamos usar los 20 mil millones de la noticia, y si el queso fuera una fracción f de eso, el adelanto total sería f·20.000 millones por k meses, ¿te parece?  
**14. Fran:** Ojo, creo que los 20 mil millones no son por mes, probablemente son por año, así que lo mensual sería f·20.000/12 millones y el adelanto sería k·f·20.000/12. ¿Y el ahorro total no sería 0,5 por eso, o sea 0,5·k·f·20.000/12?  
**15. Cami:** Puede ser anual, aunque la noticia no lo dice, así que lo suponemos. Con f = 5% y k = 2: 0,5·2·0,05·20.000/12 ≈ 83 millones de dólares, ¿te parece?  
**16. Fran:** Me da igual, 83 millones, pero eso es el ahorro bruto: falta restar bodega y pérdida, o sea 2·0,05 = 0,10 del valor adelantado, 0,10·166,7 ≈ 17 millones, y quedaría como 67 millones netos. ¿Lo ponemos como "decenas de millones de dólares", aclarando que f = 5% lo inventamos?  
**17. Cami:** Sí, "decenas de millones" con f = 5% inventado me parece bien. Y en lo del comercio pongamos que antes del arancel las compras se disparan y después caen unos k meses porque usan el stock, ¿armamos el ENTREGAMOS con eso?  
**18. Fran:** ENTREGAMOS: antes del arancel, adelantar min(k·Q, B) con k < 0,5/(c/p + s), y después comprar solo lo necesario usando el stock. Si todas lo hacen, las compras se disparan y luego caen unos k meses, con un ahorro neto de decenas de millones de dólares (supusimos f = 5%, k = 2 y 20.000 millones anuales).  
**19. Cami:** DE ACUERDO  
