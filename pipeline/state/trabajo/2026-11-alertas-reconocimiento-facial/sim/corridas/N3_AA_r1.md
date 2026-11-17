# Corrida N3_AA_r1

Nivel N3 · estilos A/A · rep 1 · 15 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo lo veo como un problema de Bayes: la confiabilidad de una alerta es P(persona buscada | alerta), y eso depende de la tasa de falsos positivos, la sensibilidad y de cuántos buscados hay realmente entre los que pasan. ¿Pedimos esos tres datos antes de calcular?  
**2. Fran:** Sí, de acuerdo, pidamos esos tres datos. Mientras tanto planteo la fórmula: P(B|A) = S·p / (S·p + F·(1−p)), con p la proporción de buscados, y además hay que ver cuántas personas pasan por día.  
**3. Cami:** Perfecto, esa es la fórmula. Mientras llegan los datos, probemos con números inventados: S = 0,9, F = 0,001 y p = 1/100.000, o sea, uno buscado cada cien mil que pasan. ¿Te parece que calculemos cuánto da P(B|A)?  
**4. Fran:** Dale: numerador 0,9·0,00001 = 0,000009, denominador 0,000009 + 0,001·0,99999 ≈ 0,001009, así que P(B|A) ≈ 0,009, o sea menos del 1%. Eso quiere decir que más de 99 de cada 100 alertas serían falsas, aunque F sea solo 0,1%.  
**5. Cami:** Cuadra, me da ≈0,0089. Pero ojo: si cada cara se compara contra 3,5 millones de fotos, la F por persona sube con el tamaño de la base, así que ¿pedimos si F es por comparación o por persona?  
**6. Fran:** Buena, si f es por comparación, F por persona ≈ 1−(1−f)^N ≈ N·f, con N = 3,5·10⁶. Con f = 10⁻⁶ serían como 3,5 falsas coincidencias esperadas por persona, así que sí hay que pedir ese dato.  
**7. Cami:** Ojo, N·f = 3,5 es el número esperado de falsos, pero F es una probabilidad: 1−e^(−3,5) ≈ 0,97, así que casi todos dispararían alerta y N·f solo sirve si es mucho menor que 1. O sea que con f = 10⁻⁶ el sistema sería inútil, y hay que pedir f real, o el umbral que usan.  
**8. Fran:** Tienes razón, 1−e^(−3,5) ≈ 0,97, me pasé con la aproximación. Para que valga la pena necesitaríamos N·f ≪ 1, o sea f ~ 10⁻⁹ o menos, y aun así queda por ver p, porque con p chica la alerta igual sale falsa casi siempre.  
**9. Cami:** Con f = 10⁻⁹ me queda F ≈ 0,0035, y con p = 10⁻⁵ da P(B|A) ≈ 0,0026, o sea que sigue siendo casi todo falso. Yo solo la tomaría en serio con una lista corta de buscados y una verificación independiente.  
**10. Fran:** Cuadra, yo también obtengo ≈0,0026. Para que P(B|A) ≥ 0,5 necesitamos p ≥ F/(S+F) ≈ 0,0035/0,9035 ≈ 0,0039, o sea 1 buscado cada ~250 personas, muy lejos de 10⁻⁵. ¿Armamos la recomendación con eso?  
**11. Cami:** Sí, armémosla: ENTREGAMOS: una alerta no es una identificación; con base de 3,5 millones, F por persona alta y p ≈ 10⁻⁵, casi todas serían falsas (P(B|A) ≈ 0,003), y solo se toma en serio si f es ≲ 10⁻⁹, la lista de buscados es corta (p ≳ 1/250) y hay verificación independiente.  
**12. Fran:** Antes de entregar, ojo con que p ≳ 1/250 salió usando F ≈ 0,0035, que depende de N = 3,5·10⁶. Si la lista es corta, N baja y F también, así que ese umbral cambia. Yo agregaría que f, p y N son supuestos nuestros hasta que nos den los datos reales, ¿te parece?  
**13. Cami:** Tienes razón: el umbral es p ≳ F/(S+F) ≈ N·f/S, así que depende de N y mejor lo dejamos como fórmula, no como "1/250". Y sí, agreguemos que f, p y N son supuestos nuestros hasta que lleguen los datos reales.  
**14. Fran:** ENTREGAMOS: una alerta no es una identificación. P(B|A) = S·p/(S·p + F·(1−p)) con F ≈ 1−e^(−N·f); con N = 3,5·10⁶ y p ~ 10⁻⁵ casi todas serían falsas (≈0,003). Solo la tomaríamos en serio si N·f ≪ 1, p ≳ N·f/S y hay verificación independiente, con f, p y N como supuestos hasta tener datos reales.  
**15. Cami:** DE ACUERDO  
