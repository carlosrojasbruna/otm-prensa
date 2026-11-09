# Corrida N4_VV_r1

Nivel N4 · estilos V/V · rep 1 · 13 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo me imagino una tablita de doble entrada, goles de local contra goles de visita, y que cada casilla (0-0, 1-0, 2-1...) tiene su probabilidad. Para armarla necesitamos el promedio de goles por partido en la liga, ¿lo tenemos o lo pedimos?  
**2. Fran:** Pidámoslo: goles totales de local y de visita en todos los partidos de la liga, porque el local suele meter más. Con esos dos promedios dibujo la tabla suponiendo que los goles de cada equipo siguen una Poisson independiente, y de ahí sale cada casilla.  
**3. Cami:** Dale, pidámoslos, y también cuántos partidos reales terminaron 2-1 o por un gol, para ver si la Poisson calza con la liga. Mientras tanto probemos con local 1,5 y visita 1,1 y vemos qué pasa si cambian.  
**4. Fran:** Con λ local = 1,5 y λ visita = 1,1, el 2-1 sale P(2)·P(1) = 0,251 · 0,366 ≈ 0,092, o sea como 9%. Ahora armo el resto de la tabla para comparar, porque el 1-1 me da cerca de 12% y el 1-0 cerca de 11%.  
**5. Cami:** Me cuadran tus números. Para los partidos por un gol sumo las dos diagonales al lado de los empates: 1-0, 2-1, 3-2, 4-3 y los de visita 0-1, 1-2, 2-3, 3-4, y me da como 0,23 + 0,17 ≈ 40%. ¿Te sale parecido con tu tabla?  
**6. Fran:** Sí, me da lo mismo: local por uno ≈ 0,232 y visita por uno ≈ 0,170, así que ≈ 0,40 en total. Los empates me suman como 26%, así que el 2-1 (9%) es común, pero queda detrás del 1-1 y del 1-0.  
**7. Cami:** Calza, el 2-1 queda tercero, y como 40% por un gol me parece estable. Probemos con λ más bajos, 1,3 y 1,0, para ver si se mueve mucho, y ojo que la Poisson independiente puede fallar con los empates, por eso igual necesitamos los datos reales de la liga.  
**8. Fran:** Con 1,3 y 1,0 el 2-1 baja a 0,230·0,368 ≈ 0,085, o sea 8,5%, y el 1-0 y el 1-1 me dan 13% cada uno. Los partidos por un gol suben un poco, a ≈ 0,235 + 0,181 ≈ 42%, así que el orden casi no cambia y el 40% parece bastante robusto.  
**9. Cami:** Me cuadra, el 2-1 queda entre 8,5% y 9% y los partidos por un gol entre 40% y 42%, así que la conclusión es estable. Falta probar "equipos parejos" con λ iguales, por ejemplo 1,2 y 1,2, y después armamos la respuesta aclarando que depende de que la Poisson calce con los datos reales de la liga.  
**10. Fran:** Con λ = 1,2 para los dos, el 2-1 es 0,217·0,361 ≈ 0,078, o sea casi 8%, y el 1-1 sale 13% y el 1-0 casi 11%. Los partidos por un gol suman 2·(0,109 + 0,078 + 0,019 + 0,002) ≈ 42%, así que sigue en el mismo rango.  
**11. Cami:** Con 1,2 y 1,2 el 2-1 queda en 8%, más abajo en el ranking que con 1,5 y 1,1, y los partidos por un gol en 42%. Entregamos 2-1 entre 8 y 9% y por un gol entre 40 y 42%, aclarando que es Poisson y falta contrastar con datos reales, ¿te parece?  
**12. Fran:** Me parece, y agrego que con equipos parejos un 2-1 o 1-2 juntos sería cerca de 16%. ENTREGAMOS: con Poisson independiente y promedios supuestos (λ entre 1,0 y 1,5), el 2-1 tenía 8-9%, detrás del 1-1 y el 1-0, y los partidos por un gol serían 40-42%, pero hay que confirmarlo con los goles reales de la liga.  
**13. Cami:** DE ACUERDO, me cuadra todo: revisé los números y salen. Queda claro que depende de confirmar con los goles reales de la liga.  
