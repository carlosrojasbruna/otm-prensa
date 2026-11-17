# Corrida N1_VV_r1

Nivel N1 · estilos V/V · rep 1 · 16 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo me imagino la fila de gente en el puesto de control y la cámara marcando a uno con el recuadro... pero no sé cómo medir qué tan confiable es eso. ¿Será que necesitamos saber cuántas veces se equivoca el sistema?  
**2. Fran:** Sí, yo creo que sí, porque si se equivoca poquito pero pasa muchísima gente, igual salen un montón de alertas falsas. [dibujo: una fila larga de monitos y un par marcados con recuadro, casi todos "inocentes"] ¿Y cuánta gente pasa por día, lo podemos pedir?  
**3. Cami:** Sí, pidámoslo, y también cuánta de esa gente es realmente la que buscan, porque me imagino que casi nadie de la fila es el buscado. [dibujo: la misma fila, con una sola silueta pintada de negro entre cientos] ¿Y si inventamos un número, tipo 1000 personas por día y el sistema se equivoca 1%, o sea 10 alertas falsas?  
**4. Fran:** Ya, pero ese 1% ¿es de qué, de la gente inocente que pasa o de todas las alertas? Porque si de 1000 hay uno solo buscado, esas 10 falsas serían mucho más que la alerta verdadera, ¿no?  
**5. Cami:** Mmm, creo que sería el 1% de la gente inocente, o sea de los 999 que no son, y ahí saldrían como 10 falsas contra 1 verdadera, si es que el sistema lo pilla. [dibujo: 10 recuadros sobre monitos blancos y 1 sobre el negro] Entonces de 11 alertas, solo 1 sería de verdad, ¿no?  
**6. Fran:** Ya, o sea que de 11 alertas solo 1 sería de verdad, como un 9%, y eso con 1000 por día. Pero ojo, si el sistema a veces no pilla al buscado, sería menos aún, ¿no? Y con una base de 3,5 millones, ¿eso cambiaría algo o no?  
**7. Cami:** Mmm, me imagino cada cara de la fila comparándose con 3,5 millones de fotos, o sea hay muchísimas más chances de confundirla con alguien, así que las falsas subirían, ¿no? Pero no sé si ese 1% ya incluye eso, ¿lo pedimos?  
**8. Fran:** Sí, pidámoslo, porque si ese 1% es por cada comparación y no por persona, con 3,5 millones de fotos saldrían muchísimas más falsas. [dibujo: una cara en el centro con flechas hacia una nube enorme de fotos] ¿Anotamos qué datos pedir: cuánta gente pasa, cuántos buscados hay, y cómo miden el error?  
**9. Cami:** Sí, anotemos eso, y también cuántas veces el sistema sí pilla al buscado cuando pasa. Y para la recomendación, yo diría que una alerta sola no basta: que el agente la verifique con otra cosa antes de actuar, ¿te parece?  
**10. Fran:** Sí, me parece, y que el agente no actúe solo porque el sistema avisó, sino que lo vea como una pista y la compruebe con otra cosa, como el documento o una persona que lo revise. ¿Armamos la respuesta con el ejemplo de 11 alertas y 1 verdadera, aclarando que son números inventados?  
**11. Cami:** Sí, armémosla así: pedimos los datos (gente por día, cuántos buscados y cómo miden el error) y con el ejemplo inventado mostramos que de 11 alertas solo 1 sería verdadera. Y la recomendación sería tomarla solo como pista y confirmarla con otra cosa, ¿la escribo yo?  
**12. Fran:** Sí, escríbela tú y yo te voy revisando. Pon también que si el buscado es más raro o la base es más grande, salen todavía más falsas y menos confiable es la alerta.  
**13. Cami:** Escribo: "Pedimos gente por día, cuántos buscados y cómo miden el error. Con números inventados salen 10 falsas por 1 verdadera, así que la alerta es solo una pista que se confirma con otra cosa." ¿Le agrego lo de la base más grande?  
**14. Fran:** Sí, agrégalo: que con una base más grande o un buscado más raro salen más falsas, y la alerta vale menos. Y pon que son 10 falsas por 1 verdadera, o sea como un 9% de acierto, y ahí la entregamos, ¿ya?  
**15. Cami:** ENTREGAMOS: Pedimos gente por día, cuántos buscados y cómo miden el error. Con números inventados salen 10 falsas por 1 verdadera (como 9% de acierto), y con base más grande o buscado más raro, peor; por eso la alerta es solo una pista que se confirma con otra cosa.  
**16. Fran:** DE ACUERDO  
