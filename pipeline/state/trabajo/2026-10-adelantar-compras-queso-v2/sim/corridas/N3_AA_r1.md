# Corrida N3_AA_r1

Nivel N3 · estilos A/A · rep 1 · 10 turnos · término: acuerdo · modelo claude-sonnet-5-5

**1. Cami:** Okey, entonces lo primero sería definir variables: precio base p, arancel 50% o sea 1,5p después de los 30 días, y costo de bodega por unidad por mes h. ¿Te parece si armamos un modelo de cuánto conviene adelantar compras contra lo que cuesta guardarlo?  
**2. Fran:** Sí, me parece. Agreguemos la fracción de queso que se echa a perder por mes, d, y la demanda mensual D, porque el ahorro por comprar antes es 0,5p por unidad y hay que compararlo con h + d·p por cada mes que se guarda.  
**3. Cami:** Dale, entonces comprar adelantado k meses conviene si 0,5p > k·(h + d·p), o sea k < 0,5p/(h + d·p). Pero ojo, la bodega tiene tope de capacidad, así que habría que agregar una restricción C y ver qué nos dan de datos para h, d y C.  
**4. Fran:** Como no nos dan h, d ni C, supongamos h = 2% de p y d = 3% al mes: k < 0,5/(0,02+0,03) = 10 meses. Pero el arancel rige en 30 días y la bodega tiene tope, así que el límite real lo pone C.  
**5. Cami:** Entonces en la ventana de 30 días compraría Q = min(C, 10·D) menos lo que ya tiene en bodega, y después del arancel compraría solo lo justo cada mes. Para el efecto en el sector, ¿te parece que pidamos qué parte de los 20 mil millones es queso?  
**6. Fran:** Sí, pidamos la fracción de queso y si los 20 mil millones son anuales. Con eso, si todos adelantan n meses, el pico sería n·(V/12) y después vendría una caída parecida.  
**7. Cami:** Mientras nos responden, supongamos que el queso es el 5% de los 20.000 M, o sea V = 1.000 M al año, y que adelantan n = 3 meses: pico extra ≈ 3·(1.000/12) = 250 M. Después cae parecido, así que hablamos de cientos de millones, y los 10 meses no me cuadran porque la demanda cambia.  
**8. Fran:** Tienes razón, los 10 meses salen de suponer demanda fija y h y d inventados. Con el tope C y pedidos que cambian, yo adelantaría solo 2 o 3 meses de demanda esperada, y el efecto sería un pico de unos 250 M y una caída parecida después, o sea que se mueve el calendario más que el total anual.  
**9. Cami:** ENTREGAMOS: antes del día 30 adelantar 2-3 meses de demanda esperada, sin pasar el tope C, y después comprar lo justo. Si todas lo hacen, hay un pico de ~250 M y una caída parecida, suponiendo queso 5%, h = 2% y d = 3%.  
**10. Fran:** DE ACUERDO. Solo dejemos claro que el 5% de queso, h y d son supuestos nuestros, y que si nos dieran los datos reales habría que recalcular el 250 M.  
