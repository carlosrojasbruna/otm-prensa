# CP3 – Informe de cierre de la fase 5 (Producción)

Fecha: 2026-10-21 · Preparado por Claude (sesión con Carlos) y actualizado por build-lead el mismo día (simulador privado, `publicar.yml`, cierre del PR #3). El detalle de cada decisión está en `pipeline/state/decisiones.md`, sección «Fase 5 (Producción)». **CP3 no está aprobado**: lo aprueba Carlos (`/otm-approve CP3`).

## 1. Qué pide CP3 y en qué estado está

| Criterio (CLAUDE.md) | Estado | Evidencia |
|---|---|---|
| Sitio en staging | **Cumple** | `deploy.yml` 39593763840 (ffafd34): los 4 jobs en verde. El job de staging creó una cuenta, valoró, comentó y moderó contra Supabase real, con la interfaz en Chrome, y borró lo que creó. Lighthouse sobre la URL pública: 100 en las 4 categorías, en móvil y escritorio, para la home y para una tarea |
| Primer lote de 6 tareas | **No cumple: 4 publicadas** (faltan 2; completarlo cuesta ≈ 5–7 USD) | Sección 3 |
| Cron semanal | **Cumple** | `semanal.yml`, `0 9 * * 1` (06:00 Chile en verano). La prueba de aceptación 39593513149 pasó y abrió el PR #3, que se revisó y se cerró sin merge |
| Ciclo completo desde la web | **Cumple, salvo un paso** | `tramo_b.yml` llega al simulador privado (`solo_comprobar`, 39600145692) y `publicar.yml` rechaza bien (39600906331, 39601072403). Falta automatizar la transición a `publicada` después del merge (sección 7) |
| Costo por ciclo | **Medido** | Sección 5 |

## 2. Entregables y commits

| Tarea | Entregable | Commits principales |
|---|---|---|
| `devops` | Workflows `ci.yml`, `deploy.yml` (migraciones → build → Pages → staging → Lighthouse), `semanal.yml` (jobs `medios` y `ciclo`, tramo A) y `tramo_b.yml` (simulador desde el repo privado `otm-simulador`; input `solo_comprobar`). Hook `.claude/hooks/otm_hook.py` (Claude Code, pre-commit y CI). `pipeline/verificar_medios.py`, `pipeline/gasto_ramas.py`, `sitio/db/aplicar_todo.sql`, `docs/secrets.md` | e0c50bf, d33f87d, 79cb779, 588f0e7, bc6986f |
| Corrección del sitio | `valorar()` y `guardarPerfil()` dejan de usar `upsert` (error 42501 por el GRANT UPDATE por columnas); tests de regresión | b11bfc7 |
| Publicación desde Actions | `.github/workflows/publicar.yml` y `pipeline/publicar.py` (envoltorio del bibliotecario: exige `verificada`, registra la revisión humana 2, relee la noticia y abre un PR); `tests/test_publicar.py` | 9864b32 (`solo_comprobar`), (este cierre) |
| «Tarea de la semana» | Regla de Carlos: la publicada con mayor RUB01; si empatan, la más reciente; el moderador puede fijarla en `sitio/web/src/config/tarea_semana.json` (con fecha `hasta`). 10 tests en `semana.test.mjs` | (fase 5) |
| `docs-writer` | `README.md` ampliado, `docs/operacion.md`, `docs/contribuir.md` | sin commit (sección 6) |

`insumos/` no cambió en la fase. El contrato `catalogo` pasó a v1.1 por autorización expresa de Carlos (1654aab).

## 3. Lote inicial

| Tarea | Versión | Nivel | Estado | PR |
|---|---|---|---|---|
| `adelantar-compras-queso` | v3 | U | publicada | #1 (mergeado) |
| `viaje-barco-ida-vuelta` | v2 | P | publicada | #1 (mergeado) |
| `pagar-trasladar-o-esperar` | v5 | U | publicada | #2 (mergeado) |
| `anticipo-renta-vitalicia` | v7 | U | publicada | #2 (mergeado) |
| `2026-10-ciclovia-vale-la-pena` | v1 | S | `evaluada`; noticia sintética, no se publica | #3 (cerrado sin merge) |

**El lote queda en 4 tareas publicadas, no en 6.** La quinta fila sale de una noticia **sintética** (`example.org`), así que no sirve para publicar: solo prueba el pipeline. Por eso su único criterio bajo es `autenticidad` = 1. Siguiendo la instrucción de Carlos («4 publicadas + las que quepan en el tope semanal, sin subirlo»), no se lanzó un segundo ciclo. Hay 3 de 4 publicadas en nivel U; ninguna publicada es S.

**Costo de completar el lote (2 tareas más).** Cada tarea nueva con noticia real cuesta ≈ 2,5–3,5 USD: tramo A 0,6–0,9 por noticia y tramo B con simulación 1,7–2,5. Para las 2 que faltan son **≈ 5–7 USD**, o hasta ≈ 8 si el verificador rechaza una guía y hay que rehacerla. A eso se suman dos revisiones humanas por tarea. En la W43 quedan ≈ 3,8 USD antes del 90 % del tope (27,67 de 31,50), lo que alcanza para una tarea justa. Lo razonable es que salgan del cron del lunes 2026-10-26 (W44, con el tope renovado): `semanal.yml` con `max_tareas=2`, después `tramo_b.yml` y `publicar.yml`.

### Verificación del PR #3 (cerrado sin merge el 2026-10-21; veredicto en el PR)

- **Ejecución 39593513149** (`workflow_dispatch` sobre b11bfc7): los jobs `medios` y `ciclo` en verde. El paso de invariantes se cumplió, porque el PR trae expedientes y tareas, no solo el gasto.
- **CI sobre el PR** (b6c21a4): `pytest`, `contratos-e-invariantes`, `secrets-scan` y `sitio` en verde, tanto en push como en pull_request. `mergeable_state: clean`.
- **Hook**: lo volví a correr en local sobre los 11 archivos del PR (`otm_hook.py archivos`): sin violaciones.
- **Contenido**: dos candidatos. Quedó elegida `ciclovia-vale-la-pena` (RUB01 23, 23, 23; rango 0, estable). La otra, `ampliar-ciclovia-cuantos-km` (22, 23, 22), quedó archivada. Ningún criterio está en 0. `resumen_propio` tiene 48 palabras. R1 tiene localizador («noticia, párrafo 2 y párrafo 4») y los demás recursos están marcados como «supuesto del escenario». `evaluacion.reproducibilidad` incluye diseñador (Sonnet, prompt 1.1), evaluador (Opus, prompt 1.3), RUB01 4.0, MAR03 1.0, MED01 1.4, fecha y costo. `diseno_simulador` es `null`, como corresponde al tramo A.
- **Invariante 3**: la noticia sintética no tiene cuerpo, así que la comparación literal se cumple trivialmente. En Actions no se define `OTM_TEXTOS_NOTICIAS`, de modo que esta prueba **no ejercita** la invariante 3 con un texto real.
- **Gasto**: 0,651 USD en el ciclo, con 7 llamadas. Semana 2026-W43: 27,67 USD. El tope es 35 y el ciclo se detiene al 90 % (31,50). La rama `semanal/2026-W43` se conserva para que el cálculo de gasto siga contando esos 0,65 USD, que no están en main.
- **Observaciones del veredicto**: el fixture sintético lleva `medio: "Emol / El Mercurio"` (conviene un medio ficticio) y la marca `evaluacion_corridas` guarda una ruta absoluta del runner.

## 4. Supabase y despliegue

- Migraciones: Carlos las aplicó en el SQL Editor. El 2026-10-21 la URL local del Session pooler conectó y se reaplicó `aplicar_todo.sql`, que es idempotente. Después se comprobó: 4 tablas con RLS activo, 12 políticas, 8 funciones y 0 filas. Con el secret actualizado, el job `migraciones` del deploy 39593763840 aplicó sin aviso.
- El sitio usa solo la clave publicable. La de servicio no va al cliente ni al repo.
- Avisos de Actions sin efecto hoy: Node 20 obsoleto en `actions/*@v4` (se fuerza Node 24) y `ubuntu-latest` migrará a Ubuntu 26. Conviene subir las acciones a versiones con Node 24.

## 5. Costo

| Concepto | USD |
|---|---|
| Acumulado al cierre de CP2 | 47,97 |
| Fase 5, después de CP2: nuevas versiones v5/v7 (0,69), tramo B de v5 y v7 (1,28), prueba en Actions (0,65) | 2,62 |
| **Acumulado** | **≈ 50,6** (precios de `pipeline/config.yaml`; verificar en la Console) |

Los jobs de deploy, staging, Lighthouse y `medios` no usan la API, ni tampoco `tramo_b.yml` con `solo_comprobar` ni `publicar.yml`. Este cierre no tuvo gasto de API.

**Costo por ciclo (medido).**

| Tipo | USD |
|---|---|
| Ciclo semanal en Actions, tramo A, 1 noticia, 2 candidatos, 3 corridas del evaluador | **0,65** (diseñador 0,18 por candidato; evaluador 0,19 por candidato, por 3 corridas) |
| Tramo A local, por noticia (prototipo) | 0,6 – 0,9 |
| Tramo B con simulación / reutilizándola | 1,7 – 2,5 / 0,55 – 1,0 |
| Tarea nueva completa | ≈ 2,5 – 3,5 |

Con `max_tareas = 1`, el ciclo semanal de Actions cuesta menos de 1 USD. Un ciclo con 6 noticias rondaría 4–5 USD en el tramo A, y cada tarea que siga al tramo B suma 1,7–2,5 USD. Con el tope de 35 USD caben unas 6 tareas completas por semana. El cuello de botella son las dos revisiones humanas.

**Costo por tarea publicada (medido en el lote).** 50,6 USD acumulados / 4 publicadas ≈ 12,6 USD por tarea. La cifra está inflada por la construcción: calibración, matriz modelo × agente y 7 versiones de anticipo. En operación, una tarea que pasa todo a la primera cuesta ≈ 2,5–3,5 USD. Si se cuentan las noticias que el filtro o el evaluador descartan, conviene presupuestar ≈ 4 USD por tarea publicada.

## 6. Documentación (`docs-writer`)

Se relanzó el 2026-10-21 para reflejar el ciclo hecho completo desde la web.

- `README.md` (145 líneas): qué es, estado al 2026-10-21, flujo, estructura, invariantes, instalación, simulador, pruebas y enlaces.
- `docs/operacion.md` (≈ 325 líneas): tabla de inputs de cada workflow (verificada contra los `.yml`) y el ciclo paso a paso. El lunes llega el PR semanal → revisión humana 1 y merge → `tramo_b.yml` (`revisor`, `ids`) → revisión humana 2 y merge del PR del tramo B → `publicar.yml` (primero con `dry_run`) → merge → `deploy.yml`. También: costos, `solo_comprobar`, moderación, tabla de fallos y pendientes.
- `docs/contribuir.md` (183 líneas): hooks, pruebas, nombres, commits y ramas, agentes, contratos e insumos (versión nueva) y qué revisa CI.

docs-writer no ejecuta comandos: lo que escribió sale de leer el código. Hallazgos suyos y qué se hizo con cada uno:

- **`publicar.yml` publica desde main.** Los expedientes `verificada` tienen que estar en main, así que el PR del tramo B se mergea antes de publicar. Quedó documentado como parte del flujo.
- **Faltaba una guarda contra dos PR de publicación del mismo id.** **Corregido**: un paso nuevo de `publicar.yml` falla si el id ya tiene un PR `publicar/*` abierto.
- **Sin comando para descartar un expediente `evaluada`**, y `--rehacer-guia`/`--nueva-version` no tienen workflow: hoy se hace en local. Pendiente.
- **`tramo_b.yml` exige `revisor` incluso con `solo_comprobar`.** Es menor; se deja así.
- **`presupuesto_ciclo` actúa como un mínimo** (`min(0,9 × tope, previo + presupuesto)`) y no como un tope adicional. Los docs lo describen según el código.
- **Fuera de su alcance, sin corregir:** `sitio/README.md` menciona un `.env.example` que no existe, dice `npm install` y tiene una sección «Qué falta para staging» obsoleta.
- **No está hecha la prueba con una persona ajena** (reproducir la instalación solo con los docs).

## 7. Qué debe decidir Carlos

1. **Aprobar o no CP3** con el lote en 4 publicadas (sección 3). Otra opción: dejar CP3 abierto hasta que el cron de la W44 complete 6 (≈ 5–7 USD).
2. **Transición a `publicada` después del merge del PR de `publicar.yml`**: hoy es manual (orquestador en local, como en los PR #1 y #2). Sin ese paso, el sitio se actualiza pero el expediente queda en `verificada`. Propuesta: un workflow `on: pull_request: closed` (merged, rama `publicar/*`) que haga la transición y commitee en main. No se construyó porque escribe en main sin PR.
3. **Fixture sintético**: cambiar `medio` de `noticia_prueba_actions.json` a un medio ficticio (observación del PR #3).
4. **Invariante 3, titular**: CLAUDE.md lo deja fuera del conteo, pero `cumple_limite_literal` aún compara todas las cadenas. Hay que ajustar el código y el contrato `noticia` (versión nueva).
5. **Pendientes de investigación** (vienen de CP2 y siguen abiertos):
   - el techo del evaluador: todo lo que llega puntúa 23–24/24, así que discrimina poco por arriba. El kappa sigue siendo provisional, porque cinco puntajes de oro son de Claude;
   - la sobre-competencia del simulador: casi no aparecen bloqueos (queso v2: 0 en 6 corridas; Sugarloaf: 6 de 6 con Pitágoras);
   - la ruta no determinista al re-simular (caso 1 de sim-integrator);
   - `escenarios.ipynb`: el ciclo no lo genera, aunque la invariante 4 y el verificador lo esperan;
   - la invariante 3 en `--continuar` (tramo B), que no relee la noticia. `publicar.yml` sí la relee antes de publicar, así que la puerta final queda cubierta;
   - el retroceso del verificador a `borrador`;
   - el desempate de candidatos;
   - la invariante 3 con texto real en Actions: la prueba del cron usó una noticia sintética;
   - el monto definitivo del tope semanal **[D]**.
6. **GOB01**:
   - la consulta al CEC UC por el sitio docente (**[D, antes de CP3]**) está en curso; el perfil docente sigue opcional;
   - la rotación de la revisión humana 1 **[D]**.
