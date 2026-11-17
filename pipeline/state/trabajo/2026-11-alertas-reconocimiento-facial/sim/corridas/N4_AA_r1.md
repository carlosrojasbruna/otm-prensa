# Corrida N4_AA_r1

Nivel N4 · estilos A/A · rep 1 · 10 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Esto me suena a un problema de falsos positivos con la base de 3,5 millones: la confiabilidad de una alerta depende de la tasa de falsos positivos y de cuántas personas buscadas hay realmente. ¿Les pedimos esos datos, o armamos primero P(buscado | alerta) con Bayes y vemos qué necesitamos?  
**2. Fran:** Armemos Bayes primero: P(B|A) = P(A|B)P(B) / [P(A|B)P(B) + P(A|¬B)P(¬B)], donde P(A|B) es la sensibilidad y P(A|¬B) la tasa de falsos positivos. Lo que más pesa es la prevalencia P(B), o sea cuántos de los que pasan están realmente en la base, así que esa sería la primera que pediría.  
**3. Cami:** Ojo, que cada persona se compara contra 3,5 millones de caras, así que los falsos positivos se multiplican: con FPR = 0,001 por comparación serían 0,001 · 3.500.000 = 3.500 por persona. ¿Qué FPR y qué umbral usa el sistema?  
**4. Fran:** Ahí 3.500 es el número esperado de coincidencias falsas por persona, así que con f = 0,001 casi siempre habría alerta: P(alerta falsa) = 1 − (1−f)^N ≈ 1. Para tener 1% de falsa alarma por persona necesitaríamos f ≈ 0,01 / 3,5·10⁶ ≈ 3·10⁻⁹, y aun así seguiría mandando P(B).  
**5. Cami:** Probemos con números: P(B) = 1/10.000, sensibilidad 0,9 y falsa alarma por persona 1%, entonces P(B|A) = 9·10⁻⁵ / (9·10⁻⁵ + 0,01) ≈ 0,9%. O sea, ~99 de cada 100 alertas serían falsas, aun con un sistema bastante bueno.  
**6. Fran:** Cuadra, y como P(B) baja tanto, la alerta sola solo serviría si hay corroboración independiente, tipo verificación humana o un umbral mucho más estricto. Además, supusimos errores independientes y uniformes, y eso es dudoso; habría que pedir la FPR por grupo y con la calidad de imagen del puesto de control.  
**7. Cami:** Entonces la alerta sirve solo como pista y no como prueba: con P(B) baja, P(B|A) queda bajo salvo que la falsa alarma por persona sea mucho menor que P(B), digamos ≤10⁻⁶, y que haya verificación independiente. ¿Armamos así la respuesta, pidiendo además FPR por grupo y prevalencia real?  
**8. Fran:** Chequeo tu 10⁻⁶: 9·10⁻⁵/(9·10⁻⁵+10⁻⁶) ≈ 98,9%, así que sirve, pero solo si P(B) es realmente ~10⁻⁴ y el agente no confirma por sesgo. Sí, armemos así, y pidamos también qué significa estar en la base: ¿buscados o simplemente fotografiados?  
**9. Cami:** ENTREGAMOS: la alerta es solo una pista, no prueba; la tomaríamos en serio si la falsa alarma por persona es mucho menor que P(B) (≈10⁻⁶ con P(B) ≈ 10⁻⁴) y hay verificación humana independiente. Antes pediríamos la FPR por grupo y calidad de imagen, la prevalencia real y qué significa estar en la base.  
**10. Fran:** DE ACUERDO  
