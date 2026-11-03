# Corrida N3_AA_r1

Nivel N3 · estilos A/A · rep 1 · 12 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Mmm, a ver, esto no trae todos los datos como siempre. Yo diría que primero necesitamos la lista completa de campeones con su edad, porque con solo tres comparaciones no podemos decir mucho de frecuencia, ¿qué piensas tú?  
**2. Fran:** Sí, estoy de acuerdo: con tres datos no podemos estimar una frecuencia. Pidamos la lista completa de campeones con su edad al título y, con eso, calculamos media y desviación estándar para ver dónde cae el 20.  
**3. Cami:** Dale, y de paso pidamos cuántas temporadas hay en total, porque la frecuencia es campeones jóvenes sobre campeonatos disputados. Además, con una media y una desviación habría que ver si los datos son más o menos simétricos, porque las edades no tienen por qué ser normales.  
**4. Fran:** Buen punto, Cami. Si no es normal, mejor no usar solo z-score: miraríamos un histograma o el percentil del 20 en los datos, y con eso diríamos qué porcentaje de campeones fue menor de 23.  
**5. Cami:** Ojo que "menor de 23" no es lo mismo que 20: si el 20 queda como el mínimo de toda la lista, el percentil dice poco. Pidamos también el año de cada título para graficar edad contra año y ver si hay tendencia o es solo una rareza.  
**6. Fran:** Tiene sentido, Cami: con edad contra año podemos ajustar una recta y ver si la pendiente es negativa de verdad o es ruido. Pero ojo, con una sola observación en 20 años estaríamos extrapolando, así que habría que decir con cuánta incertidumbre.  
**7. Cami:** Además, como lo que importa es un mínimo, más que la media habría que mirar la cola: cuántos campeones bajo 23 hubo y en qué años. Y con n chico, el intervalo de confianza de la pendiente va a salir bien ancho, así que al aire no podemos sonar tan seguros.  
**8. Fran:** Entonces armemos el plan: con la lista ajustamos edad = a + b·año y vemos si el 20 cae dentro del intervalo de predicción de la recta, o sea si es rareza o tendencia. Al aire diríamos algo como "el más joven de la historia, pero con n chico no se puede prometer que se repita".  
**9. Cami:** Otro modelo: si las edades fueran iid, la probabilidad de que el último de n campeones sea el más joven es 1/n, o sea con n≈70 saldría como 1,4%. Comparemos eso con la recta, ¿y entregamos con los dos modelos?  
**10. Fran:** Dale, pero ojo que 1/n supone iid, o sea cero tendencia, así que sería nuestro modelo base: si la recta da una probabilidad bien distinta, ahí hay evidencia de época. Entonces entregamos con los dos modelos, diciendo que n≈70 es un supuesto hasta tener la lista real.  
**11. Cami:** ENTREGAMOS: Pediríamos la lista completa de campeones con edad y año. Con n≈70 supuesto, bajo iid sería un 1/n ≈ 1,4% de que el último sea el más joven, y lo compararíamos con la recta edad vs. año. Al aire diríamos "récord histórico, pero con una sola observación no se puede prometer una época".  
**12. Fran:** DE ACUERDO  
