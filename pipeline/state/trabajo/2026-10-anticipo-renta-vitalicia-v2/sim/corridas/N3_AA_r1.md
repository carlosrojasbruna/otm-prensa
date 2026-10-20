# Corrida N3_AA_r1

Nivel N3 · estilos A/A · rep 1 · 12 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo plantearía una equivalencia: el anticipo tiene que ser igual al valor presente de los descuentos mensuales, ponderados por la probabilidad de que siga vivo. Nos faltarían la tasa y la tabla de mortalidad, ¿partimos así?  
**2. Fran:** Sí, me parece bien: anticipo = Σ d·v^t·ₜp_x, con d el descuento mensual, v = 1/(1+i) y ₜp_x la probabilidad de seguir vivo. Pero antes habría que definir qué es "10% de la renta": ¿10% de una mensualidad o de la pensión de un año?  
**3. Cami:** Buen punto. Yo diría que es 10% de una mensualidad, pero no estoy segura, así que pidamos el dato. Mientras, supongamos pensión mensual P, anticipo A = 0,1·P, y veamos cuántos meses n necesitamos: 0,1·P = d·Σ_{t=1}^{n} v^t·ₜp_x.  
**4. Fran:** Para tener un orden de magnitud, supongamos v≈1 y ₜp_x≈1: queda n = 0,1·P/d, así que con d = 0,01·P serían 10 meses. Después metemos la tasa y la mortalidad, que lo alargan un poquito.  
**5. Cami:** Ojo que esa ecuación tiene infinitos pares (d, n), así que hay que elegir uno, por ejemplo fijando d como porcentaje de P. Para ver qué tan firme es, probemos con i = 0,3% mensual y otra tasa, y miremos cuánto se mueve n al cambiar la tasa y la tabla de mortalidad.  
**6. Fran:** Dale: con d = 0,01·P necesito a_n = (1−vⁿ)/i = 10, o sea vⁿ = 1 − 10·0,003 = 0,97, y n = −ln(0,97)/ln(1,003) ≈ 10,2 meses, casi lo mismo que sin tasa. Ahora probemos i = 1% mensual y ver cuánto cambia n, y después metemos la mortalidad con una tabla.  
**7. Cami:** Con i = 1%: vⁿ = 0,90, así que n = −ln(0,9)/ln(1,01) ≈ 10,6 meses, o sea la tasa mueve n menos de un mes. Falta la mortalidad, pero a los 65 ₜp_x en un año debería ser como 0,98, así que sospecho que tampoco cambia mucho.  
**8. Fran:** Con q ≈ 0,02 al año, ₜp_x baja como 0,17% por mes, entonces Σ ₜp_x en 10 meses ≈ 10 − 0,0017·55 ≈ 9,9, y n sube apenas unos 0,1 meses. O sea que la tasa y la mortalidad casi no mueven n, y lo que sí pesa es qué entendemos por 10% y qué d elegimos, ¿te parece?  
**9. Cami:** Sí, me cuadra: la regla A = d·Σ vᵗ·ₜpₓ es firme frente a la tasa y la mortalidad, pero no frente a qué es el 10% ni a qué d elegimos. Ojo que si el 10% fuera de la pensión anual, n sería como 120 meses y ahí la tasa y la mortalidad sí pesarían.  
**10. Fran:** Cierto, con 120 meses ya no sirve v≈1: con i = 1% mensual, a₁₂₀ = (1−1,01⁻¹²⁰)/0,01 ≈ 70 en vez de 120, así que ahí d tendría que subir bastante. ¿Armamos el ENTREGAMOS con la regla de equivalencia, diciendo que es firme si el 10% es de una mensualidad y sensible a la definición del 10% y al d elegido?  
**11. Cami:** ENTREGAMOS: La regla es que el anticipo iguale el valor presente esperado de los descuentos, A = d·Σ vᵗ·ₜpₓ. Si A es 10% de una mensualidad y d = 1% de P, n ≈ 10-11 meses, poco sensible a tasa y mortalidad, pero muy sensible a qué es el 10% y al d elegido.  
**12. Fran:** DE ACUERDO  
