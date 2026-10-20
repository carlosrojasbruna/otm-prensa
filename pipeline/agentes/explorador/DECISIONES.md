# Decisiones del explorador

| Fecha | Agente | Decisión | Alternativa descartada | Por qué |
|---|---|---|---|---|
| 2026-10-20 | explorador | Llamadas síncronas con `pipeline.llm.llamar`, una por candidata | Message Batches API (el plan dice "batch") | `llamar()` es la base común obligatoria y no expone batch; con ≤ 30 candidatas/ciclo con Haiku el costo ya es de centavos. Batch queda como optimización si el costo lo pide. |
| 2026-10-20 | explorador | RSS leído con `urllib` + `xml.etree`; sin `feedparser` | Agregar dependencia | No está instalada; el RSS/Atom simple se parsea con la biblioteca estándar. |
| 2026-10-20 | explorador | Cuerpo = `description`/`content:encoded` del feed; si es < 400 caracteres se intenta bajar la página y extraer `<p>`. El cuerpo vive solo en memoria | Guardar el cuerpo para auditoría | Invariante 3: el texto real nunca se guarda. |
| 2026-10-20 | explorador | Cada cifra debe verificarse en código contra el párrafo `[n]` que el modelo cita (comparación numérica tras quitar separadores); si no está, se descarta. Sin cifras verificadas, la noticia se descarta | Confiar en el modelo | Invariante 4 y `filtro_previo.requiere: al_menos_una_cifra`. Más conservador: valores escritos en palabras ("dos millones") se pierden. |
| 2026-10-20 | explorador | El localizador siempre es `{fuente: noticia, ubicacion: "párrafo n"}` | Gráficos/tablas | No hay estructura fiable de gráficos en RSS/HTML plano. |
| 2026-10-20 | explorador | Resumen rechazado si > 80 palabras o > 25 consecutivas comunes con el cuerpo **o con el título+cuerpo**; hasta 3 intentos con aviso de corrección; si no, la noticia se descarta | Truncar el resumen | Truncar o recortar el literal no lo vuelve propio. |
| 2026-10-20 | explorador | Medios con feed `gnews` (Reuters) solo entregan título y enlace; el cuerpo se intenta bajar de la página. Si no hay cuerpo suficiente, se descarta (sin cifras no pasa el filtro previo) | Resumir solo desde el título | Evita inventar cifras. |
| 2026-10-20 | explorador | Si falla la URL principal de un medio se usa `respaldo` de MED01 | Abortar | MED01 marca `url_verificar: true`. |
| 2026-10-20 | explorador | Tope de gasto por corrida (`--tope-usd`, 1.0 por defecto); se detiene al alcanzarlo | Sin tope | Cuidado de costos. |
| 2026-10-20 | explorador | `valor` de cifra: número si es entero/decimal puro, si no cadena tal cual aparece | Siempre cadena | El contrato admite ambos; conserva el símbolo (`38 %`). |
