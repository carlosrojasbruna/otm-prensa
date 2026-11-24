# Corrida N1_AA_r1

Nivel N1 · estilos A/A · rep 1 · 13 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Uf, no nos dan ningún dato del hospital, ¿cómo vamos a calcular cuántas muertes se evitan? ¿Será que 12 % de los pacientes se salvan, o hay que partir de otra cosa?  
**2. Fran:** Mmm, yo creo que no es que se salve el 12 % de los pacientes, sino que baja 12 % el riesgo de muerte, o sea es 12 % de las muertes que ya hay. Pero igual necesitaríamos saber cuántos mueren hoy, ¿no? ¿Y si ponemos una letra, como N pacientes y p la mortalidad?  
**3. Cami:** Ya, me gusta lo de las letras. Entonces muertes hoy = N·p, y con el extracto serían N·p·(1 − 0,12) = 0,88·N·p, así que las evitadas serían 0,12·N·p, ¿cierto?  
**4. Fran:** Sí, me cuadra: evitadas = 0,12·N·p. Pero ojo, no sé si ese 12 % es riesgo relativo o absoluto, ¿y qué tan seguro es? Yo pediría al hospital el N y la p, y ver si el estudio da un intervalo de confianza.  
**5. Cami:** Ya, probemos con números inventados: N = 100 y p = 0,40, entonces 0,12·100·0,40 = 4,8 evitadas, pero si fuera absoluto serían 12. ¿Cuál sería, y cómo vemos la seguridad?  
**6. Fran:** Creo que es relativo, porque decir "12 % de reducción de riesgo" es como un 0,88 multiplicando. Si fuera absoluto, con p = 0,40 bajaríamos de 40 a 28 muertes cada 100, y eso sería enorme. Para la seguridad pediría el intervalo de confianza del 12 %, ¿te parece?  
**7. Cami:** Ya, relativo me hace sentido, 0,12·N·p. Si el intervalo fuera, por ejemplo, de 5 % a 18 %, las evitadas irían de 0,05·N·p a 0,18·N·p, ¿o eso no basta para saber qué tan segura es la cifra?  
**8. Fran:** Creo que el intervalo ayuda, pero no basta: con N = 100 y p = 0,40 iría de 0,05·40 = 2 a 0,18·40 = 7,2 muertes evitadas. Además no sabemos si sus pacientes se parecen a los del estudio, ¿lo ponemos como otra duda?  
**9. Cami:** Sí, pongámoslo como duda: si sus pacientes son más graves o distintos, el 0,12 podría no servir, y ahí la cifra sería menos segura. Y también habría que pedir el costo y los efectos secundarios, porque la recomendación depende de eso, ¿no?  
**10. Fran:** Sí, el costo y los efectos secundarios también. Armemos la respuesta: evitadas ≈ 0,12·N·p, con un rango según el intervalo de confianza, y recomendamos pedir N, p, costo, efectos secundarios y si los pacientes se parecen antes de decidir, ¿te parece?  
**11. Cami:** Me parece, y pondría el ejemplo N = 100, p = 0,40, que da 4,8 evitadas (entre 2 y 7,2 según el intervalo), para que se entienda. ¿Lo escribimos así y entregamos?  
**12. Fran:** ENTREGAMOS: muertes evitadas ≈ 0,12·N·p. Por ejemplo, con N = 100 y p = 0,40 da 4,8, y entre 2 y 7,2 si el intervalo fuera 5 %–18 % (inventado). Recomendamos pedir N, p, el intervalo real, costo, efectos secundarios y si los pacientes se parecen, antes de decidir.  
**13. Cami:** DE ACUERDO. Aunque ahora que lo leo, ¿no deberíamos aclarar que el 5 %–18 % es inventado y que el 0,12 viene del estudio de 8.009 pacientes? Si no, puede parecer que son datos reales.  
