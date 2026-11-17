# Corrida N4_VV_r1

Nivel N4 · estilos V/V · rep 1 · 8 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo me imagino la fila en el puesto, miles de caras comparadas contra 3,5 millones. Creo que la clave son las alertas falsas: depende de la tasa de error y de cuánta gente buscada hay de verdad en la fila, ¿pedimos esos datos?  
**2. Fran:** Sí, es el clásico de la prevalencia baja: dibujo la fila con 10.000 personas y solo 1 buscada, y aunque el sistema falle solo 1%, salen unas 100 alertas falsas contra 1 verdadera. Pidamos la tasa de falsos positivos, la de falsos negativos y cuántos buscados hay de verdad, ¿te parece?  
**3. Cami:** Sí, y ojo que además el 1% puede ser por comparación y no por persona: si cada cara se compara contra 3,5 millones, el error se multiplica y saldrían miles de falsas por persona. Pidamos también el umbral de confianza y si esos 3,5 millones son fotos de gente buscada o de población en general.  
**4. Fran:** Buen punto, Cami. Si la tasa fuera 1 en un millón por comparación, igual saldrían 1e-6 × 3.500.000 ≈ 3,5 falsos candidatos por persona. [dibujo: una cara a la izquierda con flechas hacia una nube enorme de caras, varias flechas marcadas en rojo] Entonces tendríamos que pedir el error por comparación y también por persona.  
**5. Cami:** Exacto, y con 10.000 personas serían unas 35.000 falsas alertas por día, así que sin más datos ni una segunda verificación humana no la tomaría en serio. Propongo recomendar tomarla en serio solo si el umbral es muy alto, la lista es chica y hay otra evidencia además del rostro. ¿Armamos la respuesta así?  
**6. Fran:** Armémosla así, pero aclarando que las 35.000 salen de suponer 1e-6 por comparación, y que el error puede ser mayor según la calidad de la foto o el grupo de personas. Y que la alerta sirva solo como pista, nunca como prueba.  
**7. Cami:** ENTREGAMOS: Una alerta sola es poco confiable: con 1e-6 de error por comparación salen unos 3,5 falsos candidatos por persona, o sea ~35.000 falsas alertas al día con 10.000 personas, y más si la foto es mala. Solo la tomaríamos en serio con umbral alto, lista chica, tasas de error conocidas y otra evidencia, siempre como pista y no como prueba.  
**8. Fran:** DE ACUERDO  
