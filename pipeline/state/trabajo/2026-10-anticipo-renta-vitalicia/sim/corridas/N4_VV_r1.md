# Corrida N4_VV_r1

Nivel N4 · estilos V/V · rep 1 · 14 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo me imagino una balanza: en un plato el anticipo de hoy, y en el otro los descuentos mensuales, que solo llegan mientras la persona viva. [dibujo: línea de tiempo con una flecha grande al inicio y flechitas chicas que se van apagando] ¿Qué datos nos faltan, como edad, tasa y probabilidad de seguir vivo?  
**2. Fran:** Me gusta la balanza, y yo la haría con valor esperado: anticipo = suma de (descuento mensual × probabilidad de seguir vivo en el mes t) / (1+i)^t. Faltan edad, sexo, tabla de mortalidad, tasa de descuento y si el 10% es de la renta anual o mensual, porque eso cambia todo.  
**3. Cami:** Supongamos una renta de 1.000.000: el anticipo es 100.000, y la regla sería 100.000 = d · Σ p_t/(1+i)^t, con t de 1 a n. ¿Probamos con i = 0,3% mensual y sobrevida casi 1 para tener un primer número, y después vemos qué pasa si la persona vive menos?  
**4. Fran:** Dale: con n = 12, el factor es (1 − 1,003⁻¹²)/0,003 ≈ 11,77, así que d ≈ 100.000/11,77 ≈ 8.500 al mes, menos del 1% de la pensión. [dibujo: barra de 1.000.000 mensual con un pedacito chico recortado durante 12 meses] Después metemos p_t menor a 1 y vemos cuánto sube d.  
**5. Cami:** A 12 meses la mortalidad casi no mueve nada: con p_t ≈ 0,99 el factor baja a ~11,6 y d sube a ~8.600. Probemos n = 120 con una persona de 65 años, porque ahí p_t sí cae harto y la regla debería ser mucho más sensible.  
**6. Fran:** Con n = 120 y p_t = 1: 1,003⁻¹²⁰ ≈ 0,698, el factor es (1 − 0,698)/0,003 ≈ 100,7 y d ≈ 100.000/100,7 ≈ 990 al mes. [dibujo: curva de sobrevida bajando desde 1 a los 65] Ahora hay que ponerle una tabla de mortalidad real a p_t, y ahí d debería subir bastante.  
**7. Cami:** Sin tabla, supongamos que a los 10 años sigue vivo ~88%, o sea p promedio ≈ 0,94: factor ≈ 95 y d ≈ 1.050, apenas 6% más que con p = 1. Entonces parece que la regla es más sensible a la tasa i que a la mortalidad, ¿probamos moviendo i?  
**8. Fran:** Con p = 1, i = 0,1% da d ≈ 885 e i = 0,5% da d ≈ 1.110, un 25% de diferencia contra el 6% de la mortalidad. Igual lo que más mueve d es n: de 12 a 120 meses baja de 8.500 a 990.  
**9. Cami:** Entonces n lo elegimos nosotros: d(n) = 100.000 / Σ p_t/(1+i)^t, con tope de d en 1% de la pensión. A 12 meses la regla es firme, pero a 10 años depende harto de i y p.  
**10. Fran:** Ojo, que d(n) da una familia de reglas, porque cualquier par (d, n) que cuadre sirve, y nos falta un criterio para elegir n. Yo iría por el plazo corto, porque ahí casi no pesan i ni p, y "cobrar de más" depende de qué i usamos, la de la compañía o la de un crédito para la persona.  
**11. Cami:** Concuerdo con ir por el plazo corto. Como criterio para elegir n, propongo que lo que paga la persona, d·n, no pase del anticipo más el interés de un crédito de consumo, o sea con i = 12 meses ≈ 102.000 en total y no 120.000. ¿Lo dejamos como regla, con n ≤ 12 o 24 meses?  
**12. Fran:** Con i = 0,3% a 12 meses ya da ~102.000, así que el techo solo muerde si subimos i. A 24 meses d ≈ 4.300 y el total es ≈ 104.000, que se pasa un poco, así que me quedo con 12.  
**13. Cami:** ENTREGAMOS: anticipo del 10%, d = anticipo / Σ p_t/(1+i)^t con n = 12 meses (≈0,85% de la pensión), y total pagado ≤ anticipo + interés de un crédito. Es firme a 12 meses, pero si n sube pasa a depender de i y p.  
**14. Fran:** DE ACUERDO. Solo agregaría que el "firme" vale para una persona de 65 con i ≈ 0,3% mensual; con alguien de 80 años y p_t más bajo habría que volver a calcular.  
