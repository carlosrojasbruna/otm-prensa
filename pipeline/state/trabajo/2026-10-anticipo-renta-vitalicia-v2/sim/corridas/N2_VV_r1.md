# Corrida N2_VV_r1

Nivel N2 · estilos V/V · rep 1 · 20 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Mmm, yo me imagino a una señora que recibe una plata de golpe y después le llega la pensión más chiquita cada mes, como pagando una cuota. ¿Será como un préstamo, Fran? Porque el 10% sería... ¿10% de qué, de la pensión mensual o de todo lo que va a recibir?  
**2. Fran:** Yo también lo veo como un préstamo, sí, tipo cuota. Y creo que el 10% sería de la renta vitalicia, pero no sé si es de la pensión mensual o del total, ¿lo dibujamos con una línea de tiempo y la plata que entra y sale cada mes?  
**3. Cami:** Ya, dibujémoslo. [dibujo: una línea horizontal con meses, una flecha grande hacia arriba al inicio, que es el anticipo, y flechitas más chicas hacia abajo cada mes, que son la pensión rebajada]. ¿Te parece que supongamos primero que el 10% es de la pensión mensual, para tener un número con qué probar?  
**4. Fran:** Ya, probemos con un número: si la pensión es $300.000 al mes, el anticipo sería $30.000, y si lo recuperamos bajando $10.000 por mes, nos demoraríamos 3 meses, ¿cierto? Pero igual me da cosa, porque la persona sigue viva muchos años y eso no es como un préstamo normal.  
**5. Cami:** Mira el dibujo, la línea de la pensión sigue y sigue, así que podríamos bajar una cantidad chiquita por más tiempo, no solo 3 meses. Pero ahí necesitaríamos saber cuántos años vive en promedio una persona pensionada y si hay que sumar algún interés, ¿no?  
**6. Fran:** Sí, y el promedio de años no sería igual para todos: no es lo mismo una persona de 60 que una de 70. Podríamos suponer algo como 20 años, o sea 240 meses, y probar cuánto bajar por mes, ¿te parece?  
**7. Cami:** Ya, probemos con 240 meses: $30.000 ÷ 240 = $125 al mes, pero eso sería sin interés. ¿Y si la compañía tiene que ganarle algo a esa plata, no debería ser un poquito más?  
**8. Fran:** Sí, yo creo que tiene que ser un poquito más, porque si la compañía te da $30.000 hoy, esa plata podría estar ganando algo en otra parte. Probemos con un interés chiquito, como 0,3% mensual, ¿y vemos cuánto sube la cuota de los $125?  
**9. Cami:** Ya, el primer mes el interés sería $30.000 × 0,003 = $90, así que la cuota tendría que ser más que $125, ¿no? Pero no me acuerdo bien de la fórmula de la cuota fija de un préstamo, ¿tú sí?  
**10. Fran:** Me acuerdo vagamente de algo como cuota = P·i / (1 − (1+i)^−n), pero no estoy segura. Probémosla con la calculadora: P = 30.000, i = 0,003 y n = 240, y si da un poco más que $125, al menos tiene sentido.  
**11. Cami:** Ya, con la calculadora (1,003)^-240 me da más o menos 0,487, así que 1 − 0,487 = 0,513 y la cuota es 90 ÷ 0,513 ≈ $175 al mes. Es más que los $125 y más que los $90 de interés del primer mes, así que en el dibujo la deuda sí iría bajando, ¿no?  
**12. Fran:** Sí, como $175 es más que los $90 de interés, la deuda baja mes a mes, y en el dibujo las flechitas van tapando la grande. Pero ¿y si la persona vive solo 10 años, o 35? Los 20 años son un supuesto nuestro, así que la regla no sería tan firme.  
**13. Cami:** Probemos con 10 años: n = 120, (1,003)^-120 ≈ 0,698, así que 90 ÷ 0,302 ≈ $298 al mes, casi el doble. ¿Y si la regla fuera un promedio entre varios años posibles, según cuántos viven cada cantidad?  
**14. Fran:** Ahí se ve la balanza del ícono: lo que la compañía espera recuperar en promedio tiene que quedar igual a los $30.000. Probemos con 10, 20 y 35 años, con probabilidades inventadas de 25%, 50% y 25%, y buscamos la cuota que haga que ese promedio dé $30.000, ¿ya?  
**15. Cami:** Ya, para 35 años n = 420 y (1,003)^-420 ≈ 0,284, así que (1 − 0,284)/0,003 ≈ 239. Con 10 y 20 años salen 101 y 171, ¿promediamos con 25-50-25 y dividimos $30.000 por eso?  
**16. Fran:** Ya, calculo: 0,25·101 + 0,5·171 + 0,25·239 = 25,25 + 85,5 + 59,75 = 170,5, y $30.000 ÷ 170,5 ≈ $176 al mes. Casi igual a los $175 de los 20 años, pero igual depende de las probabilidades que inventamos, ¿no?  
**17. Cami:** Sí, depende de lo inventado, pero me gusta que dé casi igual que con 20 años. ¿Y si probamos 50% a 10 años y 25-25 en los otros, a ver cuánto se mueve, y después pedimos tablas de mortalidad y la tasa real?  
**18. Fran:** Ya, calculo: 0,5·101 + 0,25·171 + 0,25·239 = 50,5 + 42,75 + 59,75 = 153, y $30.000 ÷ 153 ≈ $196 al mes. Subió como $20 respecto de los $176, así que la regla se mueve con las probabilidades, y sí, pidamos las tablas de mortalidad y la tasa real.  
**19. Cami:** ENTREGAMOS: cuota = anticipo ÷ promedio de [(1−(1+i)^−n)/i] según cuántos años vive la gente. Con nuestros supuestos da ≈ $175 a $196, pero no es firme sin tablas de mortalidad ni la tasa real.  
**20. Fran:** DE ACUERDO  
