# Corrida N1_AA_r1

Nivel N1 · estilos A/A · rep 1 · 17 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Mmm, yo no sé bien por dónde partir... ¿Será que primero hay que ponerle letras, algo como P la pensión mensual y el anticipo es 0,1·P? ¿Pero 10% de la renta vitalicia es de un mes o de todo lo que va a recibir?  
**2. Fran:** Ya, pongámosle letras. Yo pensaría que es 10% de una pensión mensual, así que el anticipo A = 0,1·P, y después la rebaja x por n meses tendría que cumplir x·n = A, ¿o eso es muy simple?  
**3. Cami:** Mmm, no sé... el 10% podría ser de todo el valor de la renta vitalicia, no de un mes, y eso cambiaría todo. Y si x·n = A, ¿no estamos ignorando que la plata vale distinto en el tiempo, o que la persona se puede morir antes?  
**4. Fran:** Mmm, tienes razón, lo de que se puede morir antes no lo había pensado. ¿Y si usamos una probabilidad p de que siga vivo cada mes, así lo que recupera la compañía sería x·(p₁ + p₂ + ... + p_n) = A?  
**5. Cami:** Ya, pero ahí p₁, p₂... serían la probabilidad de seguir vivo hasta el mes 1, 2, etc., ¿no? Entonces habría que pedir una tabla de mortalidad, porque no sabemos esos números.  
**6. Fran:** Sí, po, pidámosla, pero mientras tanto dejemos la fórmula escrita: x·(p₁ + ... + p_n) = A, y de ahí despejo x = A / (p₁ + ... + p_n). ¿Y qué hacemos con lo de que la plata vale distinto en el tiempo, le ponemos una tasa de interés r?  
**7. Cami:** Ya, pongámosle una tasa r mensual y dividamos cada término por (1+r)^k, o sea x·(p₁/(1+r) + p₂/(1+r)² + ... + p_n/(1+r)^n) = A. ¿Pero la tasa r la sabemos o también hay que pedirla?  
**8. Fran:** Yo creo que también hay que pedirla, porque no sabemos qué tasa usa la aseguradora, y ahí quedaría x = A / (p₁/(1+r) + ... + p_n/(1+r)^n). ¿Y qué tan firme es la regla? Porque si cambia la tabla o la r, cambia el x, ¿no?  
**9. Cami:** Sí, o sea, la regla depende harto de esos datos: si r sube o la gente vive menos, el denominador baja y x tiene que ser más grande. ¿Probamos con números inventados, como r = 0,3% mensual y n = 12, para ver cuánto cambia x?  
**10. Fran:** Ya, para partir pongamos p = 1 en todos los meses, o sea sin mortalidad: la suma es (1 − 1,003⁻¹²)/0,003 ≈ 11,77, así que x = 0,1·P/11,77 ≈ 0,0085·P. ¿Te parece que da como 0,85% de la pensión, o me equivoqué en algo?  
**11. Cami:** Lo hice en la calculadora y también me da 11,77, así que 0,1/11,77 ≈ 0,0085·P está bien. Comparado con el caso simple, 0,1/12 ≈ 0,0083·P, sube un poquito por la tasa; ¿probamos ahora con una p menor a 1, por ejemplo p = 0,99 cada mes?  
**12. Fran:** Ojo, si 0,99 es la probabilidad de seguir vivo cada mes, entonces p_k = 0,99^k, o sea el término k queda (0,99/1,003)^k. Con q ≈ 0,987 me da la suma ≈ 11,04 y x ≈ 0,1·P/11,04 ≈ 0,0091·P, ¿te sale lo mismo?  
**13. Cami:** Sí, usé q = 0,99/1,003 ≈ 0,987 y a mí también me da 11,04, o sea x ≈ 0,0091·P. Pero 0,99^12 ≈ 0,886 sería que se muere como el 11% en un año, ¿no es demasiado para alguien recién pensionado? ¿No habría que sacar ese número de la tabla de mortalidad?  
**14. Fran:** Tienes razón, 0,99 mensual era solo para probar; seguro en la tabla la mortalidad de un recién pensionado es bastante menor, así que la pedimos. Dejemos la regla como x = 0,1·P / Σ p_k/(1+r)^k y anotemos que de 11,77 a 11,04 el x subió como 7%, para mostrar qué tan sensible es.  
**15. Cami:** Sí, 11,77 a 11,04 es como 6 o 7% más, así que más o menos cuadra. Falta decir que n lo elige la aseguradora (mientras más meses, más chica la rebaja), y que pedimos la tabla, la tasa r y si el 10% es de un mes o de todo; ¿escribimos eso como respuesta?  
**16. Fran:** Sí, escribámoslo. ENTREGAMOS: x = A / Σ p_k/(1+r)^k, con A = 10% de la renta; n lo elige la aseguradora, y pedimos tabla de mortalidad, r y a qué se aplica el 10%; si cambian, x cambia (ej. ~7%).  
**17. Cami:** DE ACUERDO  
