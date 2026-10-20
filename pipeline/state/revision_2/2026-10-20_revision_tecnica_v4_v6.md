# Revisión técnica previa a la revisión humana 2 · aranceles v4 y anticipo v6

Fecha: 2026-10-20 · Hecha por: Claude (sesión de Carlos) · **No es la revisión humana 2**: Carlos la firma o la rechaza (decisiones.md, «build-lead no firma»).

Alcance (GOB01 §2, revisión 2): escenarios contra trazas, cifras contra noticia, secciones de la guía. Además se comprueba que la v4 y la v6 aplican las mejoras de `2026-10-20_cp2_v4_v6.json`.

Método: (1) script que compara cada `extracto_dialogo` con la transcripción de su corrida, la `ruta` con `trazas_resumen.json` y los `supuestos` con los de la traza; (2) lectura completa de las corridas citadas por los `que_aprende`; (3) recálculo de todas las cifras de la solución de referencia y de los diálogos; (4) lectura de `verificacion_1.json`. El texto de la noticia no está en el repo (invariante 3): las cifras se contrastan con lo que registró el verificador, que sí lo recibió (`texto_noticia_recibido: true`).

---

## 1. `2026-10-pagar-trasladar-o-esperar-v4` · **Recomendación: aprobar**

**Mejora de la v3 (elasticidad constante): aplicada.** Solución de referencia, ruta R3, rango aceptable, RX y barrera de P5 distinguen demanda lineal (traslado = ½ del aumento del costo) y elasticidad constante (p* = k_ef·ε/(ε−1), traslado ε/(ε−1) veces el arancel). El rango prohíbe afirmar que el traslado sea siempre menor que el arancel. Enunciado, foto y recursos sin cambios; simulación reutilizada de la v2 (las 6 corridas están en `trabajo/2026-10-pagar-trasladar-o-esperar-v2/sim/corridas`).

**Cifras recalculadas, todas correctas.** c = 100: lineal A = 200 → 150 / 175; ε = 3 → 150 / 225, volumen 1,5⁻³ ≈ 0,30; ε = 6 → 120 / 180; q·δ = 0,5 → k_ef = 125, 162,5 y 187,5; umbral q·δ > 1/ε. Diálogos: E1 150 / 123,75 / 97,5 (factor de interés 1,05); E3 venta 125 mil, −25 / +25 mil.

**Cifras contra la noticia.** $20bn (párr. 49) y 50% (párr. 53): coinciden según el verificador.

**Escenarios contra trazas.** Los 15 extractos están en la corrida que se cita. Las 6 corridas aparecen en algún escenario. Los supuestos son literales. Las afirmaciones de los `que_aprende` coinciden con las transcripciones, y cada escenario dice cuándo la traza registra P6-VAL sin que haya contraste con datos.
- Advertencia del verificador sobre E2 («N1_VV_r1 duda de que los clientes aguanten el recargo»): **falsa alarma.** La duda está en el turno 2 de N1_VV_r1 («no sé si los clientes lo aguantan»).

**Observaciones menores (no bloquean):**
1. `solucion_referencia`, paso 7, y `result`: «mantener el precio previo / absorber todo solo es óptimo si q·δ ≥ 1». Con q·δ > 1 el óptimo es *bajar* el precio. Lo exacto es «solo si q·δ = 1», pero el sentido didáctico no cambia.
2. Están solo en `tarea.task_space`, no en la guía, así que no los ve el docente:
   - `routes[R4].resultado` afirma que el plazo mueve la recomendación más que la probabilidad, pero q y δ entran como producto.
   - `validation_evidence` dice «traslado completo o más sugiere elasticidad constante alta», cuando un traslado mayor que el completo indica ε *baja*. La guía (`contraste_validacion`) no repite el error.
   - No ameritan una v5. Conviene anotarlos para el diseñador.
3. E1 cita una sola `ruta` (la de N4_AA_r1) aunque agrupa dos corridas. Lo mismo ocurre en E2. Es el patrón habitual del redactor.
4. `materiales.notebook = escenarios.ipynb` no existe (hueco (b) conocido, decisiones.md l. 129). Afecta a las dos tareas.

---

## 2. `2026-10-anticipo-renta-vitalicia-v6` · **Recomendación: no aprobar todavía. Un defecto de la tarea; la guía está bien**

**Mejora de la v5 (oficio anulado): aplicada solo en parte.**
- Aplicada: el enunciado dice que la Suprema declaró ilegal el oficio. El tope de 10% se atribuye a la ley. R1 ahora cita «párrafos 31 y 32». `mapa_ciclo.P1` separa ley, oficio anulado y vacío abierto. Se añadió el supuesto «no hay método oficial vigente».
- **No aplicada: `noticia.cifras_usadas[0]`** sigue diciendo `que_es: "monto máximo de anticipo de las rentas vitalicias fijado por el oficio de la CMF"`, con `localizador: párrafo 31`. Tu revisión pedía expresamente «El tope de 10% viene de la ley, no del oficio: corregir R1 **y la cifra** (localizador: párrafo 32; y párrafo 31)». La cifra contradice el enunciado y se publica con la tarea. El verificador no lo detectó porque solo comprueba que el valor (10%) coincida.
- Arreglo mínimo: `que_es` → «tope del adelanto de las rentas vitalicias fijado por la ley del tercer retiro» y `ubicacion` → «párrafos 31 y 32». No toca enunciado, recursos ni guía, así que la simulación y la guía pueden reutilizarse.

**Cifras recalculadas, todas correctas.** Horizonte cierto de 20 años al 3%: a(20)/a(10) = 1,744 → 17%, y a(20)/a(5) = 3,25 → 32%. RX: 20% y 40%. Interpretación alternativa (10% de un año): ≈ 1–2%. Diálogos: E1 0,182 / 0,168 (2% / 4%) y 0,127 (n = 15); E4 7,2 M / 240 = 30.000, 1,003⁻²⁴⁰ = 0,487, factor 171, 42.105, 14%; E2 40 mil = 10% de 400 mil.

**Escenarios contra trazas.** Los 15 extractos están en la corrida que se cita. Las 6 corridas aparecen en algún escenario. Los supuestos son literales. Contraste con las cuatro advertencias del verificador:

| Advertencia | Veredicto |
|---|---|
| E1: «las tres notan que descontar de por vida devuelve el 10%» | **Parcialmente cierta.** N4_AA_r1 y N3_AA_r1 lo notan (N3, turno 4); N4_VV_r1 no, porque trabaja con un A inventado. El verificador se equivoca al decir que N3 no lo menciona. Debería decir «dos de las tres». |
| E1: «los números salen de un horizonte cierto de 20 años» | **Cierta en parte.** El 13% de N3_AA_r1 viene de factores con mortalidad estimados a ojo (ä₆₅ ≈ 14, ä₆₅:₁₅ ≈ 11), no de un horizonte cierto. «Ninguna obtiene la tabla» sí es correcto. |
| E3: «corrige una confusión: 10% de un mes en vez del pozo» | **Falsa alarma.** Está en N2_VV_r1, turnos 15–16. |
| E4: «termina por límite de turnos» | **Falsa alarma.** El encabezado de N1_AA_r1 dice `término: max_turnos`. |

Las dos imprecisiones de E1 son de detalle. El docente no toma decisiones distintas por ellas, así que solas no justificarían rehacer la guía. Si igual se genera la v7 por la cifra, conviene pasarlas al redactor como observaciones.

**Secciones.** Barreras P1–P7, intervenciones B12–B56, puesta en común y contraste de validación son coherentes con la corrección de la v5: la regla es una propuesta del grupo y no el método anulado; R4 lleva un certificado anonimizado o, si no hay, las tasas de venta. La variante S2 es coherente con la ruta R1.

---

## Resumen para decidir

| Tarea | Recomendación | Acción |
|---|---|---|
| aranceles v4 | Aprobar revisión 2 | Firmar (Carlos) |
| anticipo v6 | No aprobar aún | v7 con `--nueva-version` solo para `cifras_usadas[0]` (borrador abajo); pasa por evaluador y revisión 1. Alternativa, si la decides tú: aprobar con la corrección como nota para el PR, a sabiendas de que la cifra publicada contradiría el enunciado |

Borrador de mejoras para `--nueva-version` (no ejecutado):

```json
{
  "2026-10-anticipo-renta-vitalicia-v6": [
    {
      "criterio": "contexto",
      "mejora_minima": "Corregir solo noticia.cifras_usadas[0]: el tope de 10% lo fijó la ley del tercer retiro, no el oficio de la CMF (que fue anulado). que_es: 'tope del adelanto de las rentas vitalicias fijado por la ley del tercer retiro'; localizador: noticia, párrafos 31 y 32. No cambiar enunciado_es, foto_descripcion ni los recursos (la simulación se reutiliza)."
    }
  ]
}
```
