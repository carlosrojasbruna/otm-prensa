# Corrida N1_AA_r1

Nivel N1 · estilos A/A · rep 1 · 18 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Mmm, a ver, yo no sé bien por dónde partir, pero creo que primero tendríamos que definir qué es el anticipo, ¿no? Como 10% de la renta vitalicia... ¿10% de la pensión mensual o de todo lo que va a recibir en la vida?  
**2. Fran:** Yo creo que sería 10% de la pensión mensual, pero no estoy segura. Si le ponemos P a la pensión, el anticipo sería A = 0,1·P, ¿o puede ser del total que va a recibir en la vida?  
**3. Cami:** Mmm, no sé, 10% de una sola pensión se me hace poquito para llamarlo anticipo. Pero partamos con A = 0,1·P y después vemos cuánto bajar: x por mes durante n meses, con n·x = A, ¿te parece?  
**4. Fran:** Ya, n·x = 0,1·P. Pero ahí tenemos dos incógnitas y una sola ecuación, ¿no? Tendríamos que fijar n o x para despejar el otro, ¿o falta algún dato?  
**5. Cami:** Sí, falta un dato, así que probemos con n = 12 meses: x = 0,1·P / 12 ≈ 0,0083·P por mes. Pero ¿no habría que considerar que la persona se puede morir antes de los 12 meses y la compañía no alcanza a recuperar todo?  
**6. Fran:** Ah, cierto, eso de "en promedio" del enunciado debe tener que ver con eso. Entonces habría que tener la probabilidad p_k de que siga vivo en el mes k, y que la suma de x·p_k para k=1 hasta n sea igual a A, ¿o me estoy complicando?  
**7. Cami:** No creo que te estés complicando, tiene sentido: x·(p_1 + p_2 + ... + p_n) = 0,1·P, así que x = 0,1·P / (suma de p_k). Pero ahí necesitaríamos los p_k, ¿no? ¿Pedimos una tabla de mortalidad?  
**8. Fran:** Sí, pidámosla, una tabla de mortalidad para alguien recién pensionado, por ejemplo de 65 años. Y también ¿no habría que descontar por interés, porque la plata de hoy no vale lo mismo que la de dentro de unos meses?  
**9. Cami:** Ah, buena, el interés también cuenta. Entonces sería x·(p_1/(1+i) + p_2/(1+i)² + ... + p_n/(1+i)^n) = 0,1·P, con i la tasa mensual, ¿o la tasa no se pone así?  
**10. Fran:** Yo creo que sí, con i mensual, porque los pagos son cada mes y cada p_k/(1+i)^k lleva el exponente en meses. Pero ¿qué hacemos con la tasa, si no la tenemos? ¿La pedimos también, o probamos con algún valor como 0,3% mensual?  
**11. Cami:** Pidámosla también, pero mientras tanto probemos con 0,3% mensual para ver cómo queda. Y ojo que hay que ver cuánto cambia x si la tasa es otra, porque eso diría qué tan firme es la regla, ¿no?  
**12. Fran:** Sí, y también cambiaría con la tabla de mortalidad y con el n que elijamos, así que habría que probar varios valores de i y de n para ver cuánto se mueve x. Pero con p_k no tenemos números todavía, ¿usamos p_k = 1 para ver cómo queda de simple?  
**13. Cami:** Dale, con p_k = 1 y n = 12 queda x·(1/1,003 + 1/1,003² + ... + 1/1,003¹²) = 0,1·P, y esa suma me da como 11,8, así que x ≈ 0,0085·P. Pero ojo que con p_k = 1 estamos asumiendo que nadie se muere, así que eso sería el mínimo de x, ¿no?  
**14. Fran:** Sí, porque si p_k < 1 la suma del denominador baja y x = 0,1·P / suma sube, así que 0,0085·P sería el piso. Aunque ojo, con 12 meses la diferencia con la tabla real debería ser chica, ¿probamos con un n más grande, como 60, para ver cuánto se mueve?  
**15. Cami:** Con la calculadora, para n = 60 y p_k = 1 la suma es (1 − 1,003⁻⁶⁰)/0,003 ≈ 54,8, así que x ≈ 0,1·P / 54,8 ≈ 0,0018·P por mes. Pero a 60 meses ya no podemos ignorar que algunos se mueren, ¿no? Ahí sí necesitaríamos la tabla.  
**16. Fran:** Entonces la regla sería x = 0,1·P / Σ [p_k/(1+i)^k], sumando de k=1 hasta n, y ahí lo que falta pedir es la tabla de mortalidad, la tasa i y qué n máximo se permite. Y para ver qué tan firme es, calculamos x con dos o tres tablas y tasas distintas, ¿te parece?  
**17. Cami:** ENTREGAMOS: x = 0,1·P / Σ[p_k/(1+i)^k], con k de 1 a n, y pedimos la tabla de mortalidad, la tasa y el n máximo. Para ver qué tan firme es, recalculamos x con distintas tablas, tasas y n; con p_k = 1, i = 0,3% y n = 12 da 0,0085·P, que sería el mínimo.  
**18. Fran:** DE ACUERDO  
