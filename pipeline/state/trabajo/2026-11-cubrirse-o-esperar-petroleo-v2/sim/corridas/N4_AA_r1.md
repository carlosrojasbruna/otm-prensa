# Corrida N4_AA_r1

Nivel N4 · estilos A/A · rep 1 · 10 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo partiría modelando el precio a un mes como P₁ = 93,74·exp(σ√T·Z), con T = 1/12, pero nos falta la volatilidad σ y el costo de la cobertura. ¿Te parece si primero listamos qué datos pediríamos al gerente?  
**2. Fran:** Sí, dale. Pediría σ implícita o histórica del Brent, el costo exacto de la cobertura, el tamaño del cargamento en barriles y cuánta pérdida aguanta la empresa, o sea su límite de riesgo.  
**3. Cami:** Perfecto, y yo agregaría el tipo de cobertura (forward u opción) y el precio al que lo cierran. Mientras tanto, supongamos σ ≈ 40% anual: σ√T = 0,40·√(1/12) ≈ 0,115, o sea un desvío de ±11,5% al mes, ¿lo probamos?  
**4. Fran:** Dale: con σ = 40%, el desvío a un mes es 93,74·0,115 ≈ 10,8 dólares, y al 95% unilateral llegaría a 93,74·e^(1,65·0,115) ≈ 113. Ojo, eso supone drift cero y lognormal, así que no captura saltos por Medio Oriente.  
**5. Cami:** Cuadra: e^0,19 ≈ 1,21, o sea unos 113, así que el peor caso al 95% son unos +19,6 USD por barril sobre hoy. Multipliquemos eso por los barriles y lo comparamos con el costo de la cobertura y con lo que aguanta la empresa.  
**6. Fran:** Pongámosle N barriles: el peor caso al 95% es 19,6·N USD de más, y cubrimos si eso supera lo que aguanta la empresa. Y repetiría la cuenta con σ = 60%, porque con una semana tan brusca el 40% se podría quedar corto.  
**7. Cami:** Con σ = 60%: σ√T = 0,60·0,289 ≈ 0,173, y e^(1,65·0,173) = e^0,286 ≈ 1,33, o sea unos 125 USD, +31 por barril sobre hoy. Entonces la recomendación depende mucho de σ, y yo diría que cubrimos salvo que 31·N USD sea poco para lo que aguanta la empresa.  
**8. Fran:** Ojo, con drift cero esperar cuesta en promedio lo mismo que cubrir, así que la cobertura es solo un seguro: conviene si su costo c·N es razonable frente a 19,6·N o 31·N. Yo diría cubrir al menos una parte, pero con poca seguridad, porque falta σ, el costo c y el límite de la empresa.  
**9. Cami:** ENTREGAMOS: recomendamos cubrir al menos una parte, porque con σ entre 40% y 60% el peor caso al 95% es +20 a +31 USD por barril. La seguridad es baja mientras no sepamos σ, el costo c y cuánta pérdida aguanta la empresa.  
**10. Fran:** DE ACUERDO. Solo agregaría que esos +20 a +31 USD son un peor caso con drift cero y lognormal, así que los saltos por Medio Oriente podrían superarlos.  
