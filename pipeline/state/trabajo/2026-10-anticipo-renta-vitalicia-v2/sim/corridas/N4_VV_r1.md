# Corrida N4_VV_r1

Nivel N4 · estilos V/V · rep 1 · 11 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo me imagino la balanza del dibujo: en un plato el anticipo que le dan hoy y en el otro los descuentos mensuales futuros, que deberían pesar lo mismo en promedio. Ojo que "en promedio" depende de cuánto viva la persona y de una tasa de interés, así que habría que pedir esos datos.  
**2. Fran:** Me gusta la balanza, pero yo la veo como una línea de tiempo: el anticipo llega hoy y después van flechitas chicas cada mes, cada una más liviana por el interés y por la probabilidad de que siga vivo. Entonces anticipo = suma de (descuento × prob. de estar vivo × 1/(1+i)^t), así que pidamos la tabla de mortalidad y la tasa.  
**3. Cami:** Dale, entonces con anticipo 0,1·R, el descuento d sale de 0,1·R = d · Σ (prob. vivo_t / (1+i)^t). ¿Probamos con una tasa mensual y un n inventados para ver qué tanto cambia d?  
**4. Fran:** Dale, probemos: supongamos una tasa anual de 3%, o sea i ≈ 0,25% mensual, y por simplificar que sobrevive seguro durante n = 24 meses, así que la suma ≈ 23,3 y d ≈ 0,1·R/23,3 ≈ 0,43% de R. Después la repetimos con 36 y 48 meses y con una tasa más alta para ver qué tanto se mueve.  
**5. Cami:** Con n=36 la suma da ≈34,4 y d ≈ 0,29% de R, y con n=48 da ≈45,2 y d ≈ 0,22%. O sea, no hay un único par (d, n), sino una curva de combinaciones.  
**6. Fran:** [dibujo: curva que baja como hipérbola, con una banda alrededor] Mira, d·n da casi siempre 10% de R, así que la tasa casi no mueve la curva, pero la mortalidad sí, porque con la probabilidad de sobrevida la suma baja y d sube. Probemos con 0,999 mensual.  
**7. Cami:** Con 0,999 mensual y n=36, q = 0,999/1,0025 ≈ 0,9965 y la suma da ≈ 33,8, así que d ≈ 0,296% de R, que apenas sube desde 0,291%. O sea, en plazos cortos la mortalidad pesa poco, y habría que probar plazos largos como 120 meses para ver si ahí sí se nota.  
**8. Fran:** Dale, con n=120 y sin mortalidad la suma da ≈103,6 y d ≈ 0,097% de R; con 0,999 mensual q^120 ≈ 0,657, la suma baja a ≈97,8 y d ≈ 0,102%, o sea un 6% más. Igual 0,999 es una mortalidad muy suave para un pensionado, así que habría que pedir la tabla real, porque ahí la diferencia crecería.  
**9. Cami:** Entonces la regla sería elegir un plazo n y poner d = 0,1·R dividido por esa suma con sobrevida y descuento, o sea la balanza igualada en valor presente. A 2 o 3 años es bien firme, pero a plazos largos depende harto de la mortalidad y la tasa, así que daría una banda y no un número único.  
**10. Fran:** ENTREGAMOS: la regla es 0,1·R = d · Σ (prob. vivo_t / (1+i)^t), o sea la balanza igualada en valor presente. A 2 o 3 años da d ≈ 0,2–0,4% de R y es bastante firme, pero a plazos largos es una banda que depende de la mortalidad y la tasa, así que pediríamos la tabla real.  
**11. Cami:** DE ACUERDO  
