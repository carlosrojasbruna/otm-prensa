# Corrida N3_AA_r1

Nivel N3 · estilos A/A · rep 1 · 10 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Oye, este problema es raro porque no nos dan ni la volatilidad ni cuánto cuesta la cobertura. Yo partiría definiendo variables: P₀ = 93,74 hoy, P₁ el precio en un mes, y comparar el costo de cerrar hoy, P₀ + c, contra E[P₁] con su variabilidad, ¿te parece?  
**2. Fran:** Sí, me parece, pero ojo que comparar solo con E[P₁] no basta, porque el riesgo está en la cola. Yo supondría P₁ = P₀·e^X con X normal y pediría la volatilidad y el costo c como información adicional, ¿tienes idea de qué volatilidad anual usar?  
**3. Cami:** Yo diría que podemos suponer una volatilidad anual como 40%, que para petróleo en una semana tan movida no suena exagerada, y pasarla a un mes: σ_mes = 0,40·√(1/12) ≈ 0,115. Así el precio a un mes tendría una desviación de más o menos 11,5%, o sea unos 10,8 dólares por barril, ¿te cuadra?  
**4. Fran:** Sí, me cuadra: 0,40/√12 ≈ 0,115. Para la cola, el percentil 95 de arriba sería P₁ = 93,74·e^(1,645·0,115) ≈ 93,74·1,21 ≈ 113 dólares, o sea unos 19 más que hoy, así que la cobertura conviene si c es menor que eso y la empresa no aguanta ese golpe.  
**5. Cami:** Ojo que comparar c con los 19 dólares no es tan directo: cubrirme me deja pagando 93,74 + c siempre, así que en el escenario malo ahorro 113 − (93,74 + c), pero si el precio baja pierdo c más lo que bajó. Entonces hay que pedir c y cuánta pérdida aguanta la empresa, porque ese 40% es un supuesto nuestro.  
**6. Fran:** Tienes razón, lo correcto es comparar 93,74 + c fijo contra P₁ variable. Si E[P₁] ≈ 93,74, cubrirse nos cuesta c en promedio a cambio de acotar la cola; probemos también con σ = 30% y 50%.  
**7. Cami:** Con σ = 30% el P95 da como 108 y con 50% como 119, o sea entre 14 y 25 dólares sobre hoy. Igual necesitamos el c real y cuánta pérdida aguanta la empresa.  
**8. Fran:** Propongo recomendar cubrirse si c es bastante menor que esos 14 a 25 dólares y la empresa no aguanta ese golpe multiplicado por el volumen del cargamento. La seguridad es media-baja, porque σ es supuesto y la normal subestima los saltos si la tensión vuelve, ¿lo dejamos así?  
**9. Cami:** Dale, solo agreguemos que pedimos volumen, c y pérdida máxima tolerable. ENTREGAMOS: Cubrirse si c es bastante menor que el alza de cola (14 a 25 US$/barril, σ 30-50%) y la empresa no la aguanta; seguridad media-baja.  
**10. Fran:** DE ACUERDO. Solo un detalle: el 4,67% y el 52% anual no los usamos, pero no cambian la recomendación porque el supuesto es que el precio sigue una caminata sin tendencia.  
