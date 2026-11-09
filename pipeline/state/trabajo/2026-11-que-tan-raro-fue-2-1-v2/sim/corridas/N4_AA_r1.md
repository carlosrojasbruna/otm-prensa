# Corrida N4_AA_r1

Nivel N4 · estilos A/A · rep 1 · 9 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo diría que modelemos los goles de cada equipo con una Poisson, con promedio λ cerca de 1,3 por equipo en partidos parejos. Pero necesitamos el promedio de goles por partido de la liga; ¿les pedimos ese dato?  
**2. Fran:** Dale, Poisson me parece bien, con P(k) = e^(-λ)·λ^k / k!. Pidamos el total de goles y partidos de toda la liga para sacar λ de ahí en vez de asumir 1,3, y supongamos que los dos equipos son independientes.  
**3. Cami:** Perfecto, pidamos el total de goles y de partidos. Mientras tanto, con λ = 1,3 calculo P(2-1) = P(2)·P(1) = [e^(-1,3)·1,3²/2]·[e^(-1,3)·1,3], que da más o menos 0,23·0,35 ≈ 0,08.  
**4. Fran:** Me cuadra, 0,08 para el 2-1; pero compáralo con el 1-1, que da 0,35² ≈ 0,126, así que el empate 1-1 sería más probable que el 2-1. Para los partidos de un gol hay que sumar P(k+1)·P(k) y duplicarlo por la simetría, o sea 2·Σ P(k)·P(k+1) desde k=0.  
**5. Cami:** Hice la suma con λ = 1,3: P(0)=0,2725, P(1)=0,3543, P(2)=0,2303, P(3)=0,0998, P(4)=0,0324, P(5)=0,0084. Entonces Σ P(k)·P(k+1) ≈ 0,0966 + 0,0816 + 0,0230 + 0,0032 + 0,0003 ≈ 0,205, y al duplicar da ≈ 0,41, o sea cerca de 4 de cada 10 partidos se decidirían por un gol.  
**6. Fran:** Revisé tus productos y me dan igual, así que 0,41 cuadra. Ojo que el 2-1 exacto es 0,08, pero un "resultado como 2-1" incluye también el 1-2, o sea ≈ 0,16. Cuando llegue el dato real de la liga rehacemos todo con ese λ y probamos con 1,1 y 1,5 para ver cuánto se mueve el 0,41.  
**7. Cami:** Hice la sensibilidad: con λ = 1,1 me da ≈ 0,42 y con λ = 1,5 ≈ 0,39, así que el 0,41 casi no se mueve. Lo que sí podría cambiar es el supuesto de independencia, así que cuando llegue el dato real habría que ver si los empates salen más seguido que en el modelo.  
**8. Fran:** ENTREGAMOS: con Poisson independiente y λ≈1,3 por equipo (a confirmar con el promedio real de la liga), el 2-1 exacto tiene P≈0,08 (≈0,16 con el 1-2), menos que el 1-1 (≈0,126). Esperaríamos ≈41% de partidos decididos por un gol (0,39 a 0,42 con λ entre 1,1 y 1,5), y habría que revisar la independencia con los empates reales.  
**9. Cami:** DE ACUERDO. Me cuadran los números, y quedó claro que λ = 1,3 es un supuesto que hay que confirmar con el dato real de la liga.  
