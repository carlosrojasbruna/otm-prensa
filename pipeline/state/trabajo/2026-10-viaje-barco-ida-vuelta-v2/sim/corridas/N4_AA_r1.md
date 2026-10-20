# Corrida N4_AA_r1

Nivel N4 · estilos A/A · rep 1 · 9 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Fran, el problema no dice a qué velocidad va el barco ni cuántas horas dura una jornada. Yo diría que pidamos esos datos, porque con solo los kilómetros no podemos calcular el tiempo: tiempo = distancia ÷ velocidad.  
**2. Fran:** Sí, Cami, tienes razón, pero también hay que fijarse en que la distancia es de ida y vuelta, o sea el doble: 241,4 × 2 = 482,8 km para Jackdaw. ¿Y si pedimos la velocidad del barco, las horas de la jornada y cuánto se demora en descargar?  
**3. Cami:** Sí, y para Rosebank sería 128,7 × 2 = 257,4 km. Con la velocidad v calculamos 482,8 ÷ v y 257,4 ÷ v, les sumamos el tiempo de descarga y lo comparamos con las horas de la jornada.  
**4. Fran:** Podemos probar con una velocidad de ejemplo, digamos v = 20 km/h: 482,8 ÷ 20 ≈ 24,1 horas para Jackdaw y 257,4 ÷ 20 ≈ 12,9 horas para Rosebank. Ahí Jackdaw ya no cabe en una jornada. ¿Y si Rosebank sí, dependiendo de cuántas horas dure la jornada?  
**5. Cami:** Con v = 20, Rosebank da 12,9 h más la descarga, así que si la jornada es de 8 o incluso 12 horas tampoco cabría. Para que quepa, tendría que cumplirse 257,4 ÷ v + descarga ≤ jornada, así que deberíamos preguntar la velocidad real del barco.  
**6. Fran:** Probemos con otra velocidad, v = 30 km/h: 257,4 ÷ 30 = 8,58 h para Rosebank y 482,8 ÷ 30 ≈ 16,1 h para Jackdaw. Ahí Rosebank sí podría caber si la jornada es larga y la descarga es corta, pero Jackdaw no cabría casi nunca, ¿lo anotamos así?  
**7. Cami:** Sí, anotémoslo así, pero con la condición: Rosebank cabe solo si 257,4 ÷ v + descarga ≤ jornada, o sea que con 30 km/h y 8,58 h de navegación ya quedan casi sin tiempo en una jornada de 10 h. ¿Escribimos que la empresa nos diga la velocidad real, la jornada y la descarga antes de decidir?  
**8. Fran:** Sí, anotémoslo. ENTREGAMOS: Pedimos velocidad, horas de jornada y tiempo de descarga. Rosebank cabe si 257,4 ÷ v + descarga ≤ jornada, y Jackdaw (482,8 ÷ v) casi seguro requiere pasar la noche.  
**9. Cami:** DE ACUERDO. Además, para que Jackdaw cupiera en 10 horas, el barco tendría que ir a más de 48 km/h, y eso es mucho para un barco de carga.  
