# Corrida N4_AA_r1

Nivel N4 · estilos A/A · rep 1 · 8 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Yo plantearía una equivalencia: el anticipo, 0,1·P, tiene que ser igual al valor presente de lo que le descontamos cada mes, ajustado por la probabilidad de que siga vivo. ¿Partimos así y pedimos la tasa y una tabla de mortalidad?  
**2. Fran:** Sí, parto igual: 0,1·P = d·Σₖ₌₁ⁿ vᵏ·ₖpₓ, con v = 1/(1+i) mensual. Ojo que es una ecuación con dos incógnitas, d y n, así que hay que fijar una, por ejemplo n, y despejar d.  
**3. Cami:** Exacto, fijemos n, por ejemplo 12 o 24 meses, y despejamos d = 0,1·P / Σ vᵏ·ₖpₓ. Ojo que si n es corto el factor de supervivencia casi es 1 y d ≈ 0,1·P/n, pero igual la regla depende de i y de la tabla.  
**4. Fran:** Sí, y con n = 12 y una tasa mensual chica, d queda un poco sobre 0,1·P/12 ≈ 0,0083·P. Para ver qué tan firme es, habría que hacer sensibilidad a i y a la tabla, y ver si la persona puede salirse antes de terminar el descuento.  
**5. Cami:** Buen punto lo de la sensibilidad: con i anual de 3% y n = 12, el factor Σ vᵏ·ₖpₓ da casi 11,8, así que d ≈ 0,1·P/11,8 ≈ 0,0085·P. Pero ojo, "no perder en promedio" supone muchas pensiones, y para una sola persona el riesgo no se diversifica.  
**6. Fran:** Concuerdo, y sumaría que la fórmula d = 0,1·P / Σ vᵏ·ₖpₓ es firme como estructura, pero los números dependen de i, de la tabla y de que nadie se salga antes. Además, una renta vitalicia suele tener beneficiarios, así que habría que pedir si ₖpₓ debe considerar la sobrevivencia del grupo familiar y no solo de la persona.  
**7. Cami:** ENTREGAMOS: la regla es 0,1·P = d·Σₖ₌₁ⁿ vᵏ·ₖpₓ, fijando n (por ejemplo 12 meses) y despejando d, que con i = 3% anual da d ≈ 0,0085·P. La estructura es firme, pero los números dependen de i, de la tabla, de los beneficiarios y de que nadie se salga antes, y solo vale en promedio.  
**8. Fran:** DE ACUERDO. Revisé la cuenta: con i = 3% anual, la tasa mensual es ≈ 0,247%, la suma da ≈ 11,8 y 0,1/11,8 ≈ 0,0085, así que cuadra.  
