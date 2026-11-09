# Corrida N3_AA_r1

Nivel N3 · estilos A/A · rep 1 · 17 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Mmm, esto no trae todos los datos como siempre... Yo diría que primero necesitamos el promedio de goles por partido en la liga, ¿te parece si pedimos la tabla completa con goles a favor y en contra?  
**2. Fran:** Sí, me parece bien, con goles a favor y en contra de todos los equipos sacamos el promedio de goles por partido. Y después podríamos suponer que los goles de cada equipo siguen una distribución de Poisson con ese promedio, para calcular P(2-1) y P(diferencia de 1 gol), ¿te tinca?  
**3. Cami:** Poisson no la hemos visto en clase, pero si la fórmula es P(k) = e^(-λ)·λ^k / k!, la puedo usar. Entonces P(2-1) sería P(2)·P(1), suponiendo que los goles de cada equipo son independientes, ¿cierto?  
**4. Fran:** Sí, exacto, asumimos independencia y que los dos equipos tienen el mismo λ, que sería la mitad del promedio de goles totales por partido. Por ejemplo, si el promedio fuera 2,6 goles por partido, λ = 1,3 y P(2-1) = e^(-1,3)·1,3²/2 · e^(-1,3)·1,3 ≈ 0,0.  
**5. Cami:** Pará, ese «≈ 0,0» no me cuadra: yo calculo P(2) = 0,2725·1,69/2 ≈ 0,230 y P(1) = 0,2725·1,3 ≈ 0,354, así que P(2-1) ≈ 0,230·0,354 ≈ 0,082, o sea como 8%. ¿Lo revisas tú también con la calculadora?  
**6. Fran:** Tienes razón, me equivoqué al poner «≈ 0,0»: lo recalculé y también me da 0,230·0,354 ≈ 0,082. Ojo que el 1-2 tiene la misma probabilidad, así que un 2-1 en cualquier sentido sería como 16%.  
**7. Cami:** Ahora la diferencia de 1 gol: sumo P(k)·P(k+1) para k = 0, 1, 2, 3, 4 y multiplico por 2 por los dos sentidos. Con λ = 1,3 me da 2·(0,097 + 0,082 + 0,023 + 0,003 + 0,0003) ≈ 0,41, o sea como 41%. Pero el 2,6 era un ejemplo, ¿pedimos el promedio real de la tabla?  
**8. Fran:** Sí, pidamos los goles totales de la tabla para sacar el λ real, y revisé tu suma y me da igual, ≈ 0,41. Ojo que con Colo Colo en +29 no todos los equipos son parejos, así que el mismo λ para ambos sirve solo para el caso de equipos parejos.  
**9. Cami:** Perfecto, pidamos la tabla con goles a favor y en contra y, si se puede, los marcadores reales de las 27 fechas para ver si Poisson ajusta. Para comparar marcadores, con λ = 1,3 el 1-1 sería 0,354² ≈ 0,125, bastante más probable que un 2-1 en un sentido.  
**10. Fran:** Cierto, 0,354² ≈ 0,125, y el 1-0 sería 0,354·0,2725 ≈ 0,096, así que con λ = 1,3 el 1-1 sale como el marcador más probable. Como U de Chile y Cobresal no eran tan parejos, ¿pedimos también los goles a favor y en contra de cada uno para estimar un λ distinto para cada equipo?  
**11. Cami:** Sí, pidamos los de ambos equipos. Así estimaríamos λ_U = (GF_U/27)·(GC_Cobresal/27) / (promedio de goles por equipo por partido), y lo mismo para Cobresal, y con esos λ recalculamos P(2-1).  
**12. Fran:** Dale, esa fórmula combina ataque y defensa, pero hay que confirmar que ambos jugaron 27 partidos para dividir bien. También pidamos quién era local, porque la localía podría subir el λ de ese equipo.  
**13. Cami:** Buena, la localía también la pedimos. Anotemos el pedido: tabla completa, goles a favor y en contra de U y Cobresal, partidos jugados, quién era local y los marcadores reales para comparar con el 41%.  
**14. Fran:** Dale, y mientras llegan los datos dejemos anotado que con λ = 1,3, un 2-1 en cualquier sentido da ≈ 16% y un partido decidido por un gol ≈ 41%, y que eso supone Poisson e independencia. Después lo ajustamos con el λ real de la tabla, ¿te parece?  
**15. Cami:** Dale, anotémoslo así, pero aclarando que el 8% es para el 2-1 de U de Chile en particular y el 16% es sumando ambos sentidos. Cuando lleguen los datos reemplazamos λ = 1,3 y comparamos con la frecuencia real de partidos de un gol de las 27 fechas.  
**16. Fran:** Dale, queda claro: 8% para el 2-1 de la U, 16% sumando ambos sentidos y 41% para partidos de un gol, con λ = 1,3. ENTREGAMOS: estos valores provisorios (supuestos Poisson e independencia) más el pedido de datos para ajustar λ.  
**17. Cami:** DE ACUERDO. Dejemos claro en la respuesta que λ = 1,3 era solo un ejemplo y que lo cambiamos apenas tengamos los goles reales de la tabla.  
