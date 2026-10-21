# Operación de OTM-Prensa

Esta guía describe cómo corre el pipeline cada semana, cómo se lanza cada workflow desde la web de GitHub, cómo se revisa lo que produce y cómo se recalibra el evaluador. Todo lo que aparece aquí como workflow, input, flag o archivo existe en el repositorio. Lo que no está implementado o espera una decisión humana se marca como **pendiente**. Las decisiones tomadas y las pendientes están en `pipeline/state/decisiones.md`, que se lee en cada checkpoint.

Quien opera el sistema es Carlos Rojas Bruna, revisor humano (GOB01 §2). Los agentes no preguntan entre checkpoints: anotan la lectura conservadora en `decisiones.md` y siguen.

Estado al 2026-10-21: piloto, CP3 aprobado (`pipeline/state/CP3_informe.md`).

## 0. Antes de empezar

### Cómo lanzar un workflow desde la web

1. Entra en la pestaña **Actions** del repositorio.
2. En la lista de la izquierda, elige el workflow (`semanal`, `tramo_b`, `publicar` o `deploy`). `publicada.yml` no tiene botón: corre solo tras el merge de un PR de publicación (sección 5.6).
3. Pulsa **Run workflow**.
4. En **Use workflow from**, deja **Branch: main**. Lanza siempre desde `main`, salvo que esta guía indique otra cosa.
5. Rellena los inputs y pulsa **Run workflow**.

Los workflows que aceptan inputs (`workflow_dispatch`) son estos:

| Workflow | Cuándo corre | Inputs | Qué hace | Estado de los expedientes al terminar |
|---|---|---|---|---|
| `semanal.yml` | Cron los lunes 09:00 UTC, y a mano | `max_tareas` (3), `presupuesto_ciclo` (vacío), `noticia_prueba` (vacío), `ejecutar_ciclo` (`true`) | Verifica MED01 y corre el tramo A. Abre o actualiza el PR `semanal/AAAA-WW` | `evaluada` |
| `tramo_b.yml` | A mano | `revisor` (obligatorio), `ids` (obligatorio salvo con `solo_comprobar`), `presupuesto_ciclo` (vacío), `solo_comprobar` (`false`) | Corre el tramo B. Abre o actualiza el PR `semanal/AAAA-WW` | `verificada` |
| `publicar.yml` | A mano | `ids` (obligatorio), `revisor` (obligatorio), `dry_run` (`false`) | Ejecuta el bibliotecario y abre el PR `publicar/<fecha>-<n>` | Sigue en `verificada`. Tras el merge de su PR, `publicada.yml` lo pasa a `publicada` (sección 5.6) |
| `deploy.yml` | Cada push a `main`, y a mano | Ninguno | Aplica migraciones, construye el sitio, lo publica en Pages y corre el staging | Sitio en producción |
| `ci.yml` | Cada push y cada pull request | Ninguno | Pruebas, contratos, invariantes y escaneo de secretos | Solo informa |

`publicada.yml` no acepta inputs. Se dispara al cerrar un PR hacia `main` que fue mergeado y cuya rama empieza por `publicar/`. Cualquier otro cierre no hace nada.

`semanal.yml` y `tramo_b.yml` comparten una rama por semana (`semanal/AAAA-WW`). `semanal`, `tramo_b`, `publicar` y `publicada` declaran el mismo grupo de concurrencia `semanal`, así que no escriben a la vez.

## 1. Cómo corre la semana (automático)

### Programación

`.github/workflows/semanal.yml` tiene el cron `0 9 * * 1`: los lunes a las 09:00 UTC. Eso es 06:00 en Chile durante el horario de verano. En invierno corre a las 05:00 hora local, el mismo lunes. GitHub puede retrasar los cron unos minutos. Si el cron no aparece en Actions o no corre, revisa que los workflows estén habilitados; GitHub puede deshabilitarlos en repositorios sin actividad.

El workflow tiene dos jobs:

- **`medios`**: ejecuta `python -m pipeline.verificar_medios`. Revisa `robots.txt` y los RSS de MED01 (la versión más alta de `insumos/medios/`). No llama a ningún modelo y su costo es cero. Escribe `pipeline/state/medios/verificacion_<AAAA-MM-DD>.json` y lo sube como artefacto. Sale con código 0 aunque haya medios caídos, porque el flag `--estricto` no se usa.
- **`ciclo`** (espera a `medios`): ejecuta `python -m pipeline.ciclo --max-tareas <n>`, que corre solo el **tramo A**: explorador, filtro, diseñador (dos candidatos por noticia) y evaluador (tres corridas por candidato, mediana por criterio). Cada tarea llega como máximo a `evaluada`, con la marca `pendiente: revision_humana_1`. El tramo B no corre aquí.

### Ramas y PR

- Cada semana ISO usa **una rama**, `semanal/<AAAA-WW>` (por ejemplo, `semanal/2026-W43`), y **un PR** hacia `main`. Si ya hay un PR abierto para esa rama, el workflow agrega un comentario en vez de abrir otro. Todos los ciclos de la semana, incluidas las pruebas manuales, van a esa rama.
- El PR contiene solo `pipeline/state/`: expedientes, carpetas de trabajo, registros de ciclo, `gasto_semanal.json` e informe de medios. **El PR no publica nada.**
- El PR lo abre `GH_TOKEN`, no el `GITHUB_TOKEN` de fábrica, porque los PR creados con este último no disparan `ci.yml`.

### Tope de gasto

El tope está en `pipeline/config.yaml`: `tope_semanal_usd: 35.0` (provisional, fijado por Carlos; el monto definitivo es **pendiente**) y `fraccion_detencion: 0.9`. Antes de cada llamada a la API, el ciclo comprueba que el gasto de la semana previo más el del ciclo no llegue a 31,50 USD. La última llamada puede pasar ese límite, porque su costo no se conoce de antemano.

- El gasto previo se lee de `origin/main` y se suma, con `python -m pipeline.gasto_ramas`, a lo que ya tiene la rama `semanal/<AAAA-WW>`. Así cuentan también los ciclos de PR abiertos o sin mergear.
- `presupuesto_ciclo` (input de los workflows; `--presupuesto-ciclo` en local) pone un límite adicional a esa corrida. El límite efectivo es el menor de los dos.

### Códigos de salida de `pipeline.ciclo`

| Código | Significado | Efecto en Actions |
|---|---|---|
| `0` | El ciclo terminó | Job verde |
| `3` | Se detuvo por el tope. Es un resultado previsto, no un fallo | El PR se publica con la nota «El ciclo se detuvo por el tope de gasto». Job verde con una advertencia. Los expedientes quedan en su último estado válido |
| Otro | Error de un agente o de la API. El cierre de emergencia ya guardó el gasto | El estado se commitea igual, el PR se abre con el error anotado y el job queda en rojo |

Si una invariante queda violada en el estado generado, el workflow commitea solo `gasto_semanal.json` y `pipeline/state/ciclos/`, abre el PR y marca el job en rojo.

## 2. Lanzar el tramo A a mano

Usa `semanal.yml` con **Run workflow**. Para una prueba de aceptación con una noticia sintética y un tope de 2 USD, pon:

- `max_tareas` = `1`
- `presupuesto_ciclo` = `2`
- `noticia_prueba` = `evals/casos/ciclo/noticia_prueba_actions.json`
- `ejecutar_ciclo` = `true`

En `noticia_prueba` escribe **solo la ruta**. El 2026-10-21 una ejecución se detuvo en «Validar entradas» porque el valor llevaba el prefijo `noticia_prueba=`. Ese fallo ocurre antes de gastar. `ejecutar_ciclo` = `false` deja solo el job `medios`, sin gasto de API.

Las comprobaciones de secrets (`ANTHROPIC_API_KEY` y `GH_TOKEN`) y la validación de entradas ocurren antes de cualquier llamada. El mensaje indica qué falta sin imprimir valores.

Una prueba con noticia sintética deja sus expedientes en el PR de la semana. **No mergees esa prueba.** Así se hizo con el PR #3: se revisó y se cerró sin merge, y la rama `semanal/2026-W43` se conservó porque su gasto (0,65 USD) sigue contando.

**Prueba de aceptación en Actions: pasó.** La ejecución 39593513149 (2026-10-21) completó `medios` y `ciclo`, gastó 0,65 USD y abrió el PR #3 con una tarea en `evaluada` (RUB01 23/24 en las tres corridas). CI pasó en verde sobre el PR.

## 3. Revisión humana 1 (PR semanal)

La revisión humana 1 decide si una tarea pasa al tramo B. Se hace sobre cada expediente `evaluada` que trae el PR.

### 3.1 Qué mirar

Los archivos están en `pipeline/state/`:

1. **`expedientes/<tarea_id>.json`**: estado, número de evaluaciones (`iteraciones`) y `marcas`. Revisa `marcas.pendiente` (debe decir `revision_humana_1`), `marcas.evaluacion_inestable` y `marcas.ultimo_error`. Un candidato no elegido de una noticia aparece como `archivada` con el motivo «candidato no elegido»; no requiere acción.
2. **`trabajo/<tarea_id>/tarea.json`**: el nivel declarado (`nivel`: P, S o U, según MAR03), el bloque `estudiante` (`enunciado_es` y `foto_descripcion`), los recursos con su fuente y localizador, y la cita de la noticia. Compara el enunciado con lo que un estudiante recibe. Lo que no está en el enunciado no existe para el simulador.
3. **`trabajo/<tarea_id>/evaluacion.json`**: el total RUB01 (`rub01.total`, máximo 24) y los 12 criterios, cada uno con su justificación y su cita. El tramo A solo lleva una tarea a `evaluada` si el total es de al menos 20 y ningún criterio vale 0.
4. **`trabajo/<tarea_id>/evaluacion_corridas.json`**: las tres corridas del evaluador. Si el rango del total entre corridas es de 4 puntos o más (`evaluador.rango_inestable` en `config.yaml`), la tarea lleva `evaluacion_inestable`. Mira esos criterios con más atención.
5. **El nivel frente al total**: MAR03 fija P 10–12, S 13–18 y U 18–20. Un nivel que no encaja con el total es motivo para no avanzar.

### 3.2 Qué no hacer

- **No mergear a ciegas.** Lee el enunciado y los recursos, no solo el número. Un RUB01 alto no garantiza que la tarea sea modelable. Los criterios débiles documentados (autenticidad, validación y fecundidad, según `decisiones.md`) requieren juicio humano.
- **Desconfiar de los totales altos.** CP3 deja como pendiente el techo del evaluador (23–24/24). Contrasta el puntaje con tu propia lectura.
- **No editar expedientes a mano sin registrarlo.** Si corriges una cifra o un campo, anótalo en `decisiones.md` con su motivo, como se hizo con la v7 de anticipo (marca `correccion_manual_cifra`).

### 3.3 Qué significa aprobar

- **Aprobar** significa mergear el PR. El merge no publica nada. Es necesario, además, porque `tramo_b.yml` toma los expedientes de `main`: su input `ids` exige que estén en `evaluada` **y en main**. Por eso el merge incluye también los expedientes que no avanzan. Quedan en `evaluada`; anota el motivo en `decisiones.md`. No hay comando para descartar un `evaluada` (**pendiente**).
- Cada push a `main` dispara `deploy.yml`. Como el catálogo no cambia con este merge, el sitio queda igual.
- Después del merge, lanza el tramo B (sección 4) con el nombre de quien hizo esta revisión en `revisor`.

## 4. Tramo B (manual, desde la web)

El tramo B lleva un expediente de `evaluada` a `verificada`: `evaluada → revisada → simulada → con_guia → verificada`. Corre el simulador (seis corridas por tarea, `simulador.corridas_por_tarea`), el redactor (la guía por secciones), el ilustrador (no bloqueante) y el verificador (contrasta cifras y afirmaciones con la noticia). Si el verificador rechaza la guía, el ciclo la rehace una vez; al segundo rechazo, la tarea queda `archivada`. El tramo B nunca publica.

### 4.1 Lanzarlo

Lanza `tramo_b.yml` desde `main` con:

- `revisor`: nombre y apellido de quien hizo la revisión humana 1. Es obligatorio, debe tener al menos 3 caracteres y el ciclo no lo inventa.
- `ids`: los ids de expediente separados por espacios, todos en `evaluada` y en `main`. Usa el id exacto del expediente (formato `AAAA-MM-slug`, por ejemplo `2026-10-<slug>`). Solo letras, números, puntos, guiones bajos, guiones y espacios.
- `presupuesto_ciclo`: opcional, en USD. Vacío significa solo el 90 % del tope semanal.
- `solo_comprobar`: `false`. Para comprobar el acceso al simulador, ver la sección 8.

El workflow hace checkout de `SIM_REPO` (el repositorio privado del simulador) en `_sim/`, lo enlaza donde `config.yaml` lo espera, instala dependencias y ejecuta `python -m pipeline.ciclo --continuar <ids> --revisor <revisor>`. El PR `semanal/AAAA-WW` se crea, o se actualiza con un comentario si ya existe.

Si el PR semanal de la misma semana todavía no está mergeado, los ids no están en `main` y el tramo B falla.

### 4.2 Qué leer en el PR del tramo B

- El resumen del ciclo (el mismo texto que el log, con el enlace a la ejecución).
- El estado de cada expediente: debe decir `verificada`.
- Las cuentas: el gasto del tramo B va en `gasto_semanal.json`.

Lee la guía en el propio PR (sección 5.1).

### 4.3 Resultados posibles

- **Código 0:** job verde, expedientes en `verificada`, PR con la nota.
- **Código 3:** advertencia de tope. Los expedientes quedan en su último estado válido. Para reanudarlos, vuelve a lanzar `tramo_b.yml` con los mismos `ids` y `revisor`: `--continuar` retoma cada expediente desde su último estado válido.
- **Otro código:** job rojo. Lee el log y la marca `ultimo_error` del expediente.
- **Invariantes violadas:** job rojo. El PR contiene solo el gasto y los ciclos.

Costo: un tramo B con simulación nueva cuesta entre 1,7 y 2,5 USD. Si reutiliza una simulación ya hecha, cuesta entre 0,55 y 1,0 USD.

## 5. Revisión humana 2, publicación y verificación

### 5.1 Revisar la guía

Revisa en el PR del tramo B. Los archivos de cada expediente están en `pipeline/state/trabajo/<tarea_id>/`:

- `guia.json`: la guía. Cada escenario debe citar corridas (invariante 5) y cada cifra debe tener localizador (invariante 4).
- `evaluacion.json`, `tarea.json`: que la guía siga a la tarea que se evaluó.
- `trazas_resumen.json` y `sim/manifiesto.json`: las corridas del simulador que respaldan los escenarios.
- `icono.svg`: el ícono que la publicación va a usar.

Comprueba que el enunciado de `tarea.json` no haya cambiado respecto de la revisión 1, que no haya texto copiado de la noticia (invariante 3) y que las citas apunten a la noticia real. Para la invariante 3, el titular de cada cita queda fuera del conteo de 25 palabras desde el contrato `noticia` v1.2 (lo aplica `pipeline/invariantes.py::cumple_limite_literal`). El resto de la guía y de la tarea sí cuenta.

### 5.2 Si hay defectos (solo en local)

Hoy ningún workflow corrige la guía ni la tarea. Estos comandos corren en tu máquina, con `OTM_API_KEY`, y dejan sus cambios de estado en tu copia del repositorio. Para que lleguen a `main`, commitéalos en una rama y abre un PR:

- **Defecto de la guía** (redacción, escenario mal respaldado):

  ```bash
  python -m pipeline.ciclo --rehacer-guia OBSERVACIONES.json --revisor "Nombre Apellido"
  ```

  El JSON tiene la forma `{tarea_id: [observaciones]}`. El expediente debe estar en `verificada`. Reutiliza la simulación. La guía sube a la versión siguiente y pasa de nuevo por el ilustrador y el verificador.

- **Defecto de la tarea** (enunciado, cifras, supuestos): una guía nueva no lo corrige.

  ```bash
  python -m pipeline.ciclo --nueva-version MEJORAS.json
  ```

  El JSON tiene la forma `{tarea_id: [{criterio, mejora_minima}]}`. Crea `<id>-v<n>` como expediente propio, sin tocar la v1. La nueva versión se evalúa con tres corridas y vuelve a la revisión humana 1. La simulación se reutiliza solo si `enunciado_es` y `foto_descripcion` no cambian.

Un rechazo del verificador por un defecto de la tarea vuelve el expediente a `simulada` y gasta una guía inútil. Es un hueco conocido (`decisiones.md`); **pendiente de decisión** cambiar la máquina de estados congelada.

### 5.3 Publicar con `publicar.yml`

Publicar exige la orden explícita de Carlos. Antes de lanzar el workflow:

- **Los expedientes deben estar en `verificada` dentro de `main`.** `publicar.yml` no fija `ref`: usa la rama desde la que lo lanzas, que por defecto es `main`. Por eso el PR del tramo B debe estar mergeado antes. Mergearlo no publica nada. (Esto sale de leer el workflow y el código; no hay un caso probado de lanzarlo desde la rama `semanal/AAAA-WW`. Si lo haces, el PR de publicación arrastraría toda esa rama.)

Luego lanza `publicar.yml` desde `main`:

1. **Primero, un ensayo.** `ids` = los ids a publicar, `revisor` = quien hizo la revisión humana 2, `dry_run` = `true`. El log muestra, por cada id, la versión, la ruta y los archivos que escribiría. No escribe nada, no hace push y no necesita `GH_TOKEN`.
2. **Después, la publicación real.** Lo mismo con `dry_run` = `false`. El workflow:
   - ejecuta `python -m pipeline.publicar`, que valida todas las tareas antes de escribir la primera (todo o nada);
   - escribe `tareas/AAAA-MM/<slug>/` y `tareas/catalogo.json`, y marca la revisión humana 2 en cada expediente;
   - commitea en la rama `publicar/<AAAA-MM-DD>-<run_number>`, comprueba la invariante sobre los archivos cambiados, hace push y abre el PR con título «Publicar: <ids>».

`publicar.py` rechaza todo el lote (código 2, sin escribir nada) si:

- un expediente no está en `verificada` (por ejemplo, está `publicada`: una tarea publicada no se edita, se versiona);
- `revisor` tiene menos de 3 caracteres, o hay ids repetidos, o dos ids son versiones de la misma tarea;
- la guía con la revisión humana 2 no valida contra su esquema;
- la noticia no se puede releer para comprobar la invariante 3. Sin texto no se publica;
- el bibliotecario rechaza la tarea: RUB01 menor que 20 o con un criterio en 0, escenarios sin corrida, o una versión que ya existe en el catálogo.

El job queda en rojo y el log muestra las líneas «RECHAZADO». Corrige la causa y lanza de nuevo.

**Un id con un PR de publicación abierto se rechaza.** Antes de publicar, el workflow busca PR abiertos de ramas `publicar/*` cuyo título contenga el id y, si encuentra uno, falla sin escribir nada. Para volver a publicar ese id, primero mergea o cierra el PR anterior.

### 5.4 Revisar y mergear el PR de publicación

Revisa en el PR los archivos de `tareas/AAAA-MM/<slug>/` (la tarea, la guía en JSON y en Markdown, la evaluación, las trazas y el ícono) y el diff de `tareas/catalogo.json`. CI corre sobre el PR. Si todo está bien, mergea. Las tareas publicadas no se editan: un cambio posterior es una versión nueva en la misma carpeta.

Al mergear, `publicada.yml` corre solo y pasa a `publicada` los expedientes de ese PR (sección 5.6). No hace falta ninguna acción manual. Si cierras el PR sin mergear, `publicada.yml` no hace nada y los expedientes siguen en `verificada`.

### 5.5 Despliegue

Cada push a `main`, incluido el merge del PR de publicación, dispara `deploy.yml` (sección 6). El sitio lee `tareas/catalogo.json` al construirse, así que la tarea nueva aparece con ese despliegue. El commit que `publicada.yml` hace en `main` también es un push a `main`: dispara `deploy.yml` y `ci.yml` como cualquier otro.

### 5.6 Paso automático: `verificada` → `publicada` (`publicada.yml`)

Tras el merge de un PR de `publicar.yml`, `.github/workflows/publicada.yml` pasa a `publicada` los expedientes de ese PR. Se dispara con `pull_request` `closed` hacia `main`, y solo corre si el PR fue mergeado y su rama empieza por `publicar/`. Un PR cerrado sin merge, o de otra rama, no hace nada.

El workflow hace checkout de `main` (que ya incluye el merge) y ejecuta `python -m pipeline.marcar_publicadas --rama <rama> --pr <n> --merge <sha>`:

1. Busca en `pipeline/state/expedientes/` de `main` los expedientes en `verificada` cuya marca `publicacion_propuesta.rama` es la rama del PR. Si no hay ninguno, sale con código 3: el workflow emite un aviso y no falla.
2. Comprueba que `tareas/catalogo.json` de `main` tenga la versión de cada tarea. Si falta alguna, rechaza el lote con código 2 y no escribe nada.
3. Hace la transición `verificada → publicada` con el orquestador, que valida cada artefacto contra `contratos/`. El revisor es el de la marca `revision_humana_2` del expediente, y la guía debe tener `trazabilidad.revision_humana_2`.
4. Escribe solo el estado: `estado` del expediente, su espejo `tarea.estado` en `pipeline/state/trabajo/<id>/tarea.json` y la entrada de `historial` (de, a, fecha, revisor y el motivo `PR #<n> mergeado (<sha>); publicada.yml`). No toca `tareas/`, ni las marcas, ni la guía. Si un expediente no pasa, no escribe ninguno.
5. Pasa el hook de invariantes sobre `pipeline/state` (`python .claude/hooks/otm_hook.py staged`) y commitea en `main` como `otm-prensa-bot`, con el mensaje `pipeline: publicada <ids> (PR #<n>, merge <sha12>)`, usando `GH_TOKEN` para el push.

No hay marca `publicacion` en el expediente: el PR, el merge y el sha quedan en el motivo del historial y en el mensaje del commit. El catálogo ya tenía la tarea desde el merge del PR, así que el sitio no cambia con este paso.

El job usa el grupo de concurrencia `semanal`, así que espera si otro workflow de ese grupo está corriendo.

**Relanzarlo a mano.** Si `publicada.yml` falló y la causa ya está corregida (sección 11), el paso se puede hacer en local. Desde `main` actualizado, con las dependencias de `requirements.txt` instaladas y sin `OTM_API_KEY` (el comando no llama a ningún modelo):

```bash
git checkout main && git pull
python -m pipeline.marcar_publicadas --rama publicar/<AAAA-MM-DD>-<n> --pr <n> --merge <sha12>
git add pipeline/state
python .claude/hooks/otm_hook.py staged
git commit -m "pipeline: publicada <ids> (PR #<n>, merge <sha12>)"
git push origin main
```

`--merge` acepta el sha del merge (el workflow usa sus 12 primeros caracteres). Si el comando responde código 3, ningún expediente de esa rama está en `verificada`: ya se hizo, o nunca estuvo listo. No lo repitas. Para comprobar el resultado, `python -m pipeline.ciclo --estado` lista el estado de cada expediente.

## 6. Despliegue del sitio

`.github/workflows/deploy.yml` corre con cada push a `main` y a mano (`workflow_dispatch`, sin inputs). Sus jobs, en orden:

1. **`migraciones`**: comprueba el secret `SUPABASE_DB_URL` y que `sitio/db/aplicar_todo.sql` esté al día con las migraciones (`node sitio/db/generar_aplicar_todo.mjs --check`). Después aplica el SQL con `psql`. Ese paso tiene `continue-on-error`: si falla, deja un aviso y el despliegue sigue. El SQL es idempotente y va en una transacción. `SUPABASE_DB_URL` debe ser la cadena del **Session pooler** de Supabase; la conexión directa es solo IPv6 y los runners de GitHub no la alcanzan.
2. **`sitio`** (espera a `migraciones`): build de Astro en `sitio/web` con la clave publicable. Nunca usa la clave de servicio. El checkout de este job no trae el historial completo, así que el desempate de «Tarea de la semana» por fecha de commit no se aplica en producción (ver `sitio/README.md`).
3. **`publicar`**: despliega en GitHub Pages. Este job es el de Pages, no el workflow `publicar.yml`.
4. **`staging`**: `npm run staging` contra el proyecto real de Supabase. Crea un usuario de prueba, valora y comenta, comprueba que el comentario pendiente no se ve, lo modera con una cuenta temporal y borra lo creado. Si falla, el job falla. Después, Lighthouse sobre la URL pública corre como informativo.

**Bloquea:** falta `SUPABASE_DB_URL` (el job `migraciones` falla en su primer paso y `sitio` no corre); `aplicar_todo.sql` desactualizado; faltan `SUPABASE_URL` o `SUPABASE_PUBLISHABLE_KEY` en el build; faltan los secrets de staging; falla la verificación de staging.

**No bloquea:** un fallo de `psql` al aplicar migraciones (aparece el aviso «Migraciones no aplicadas»); el resultado de Lighthouse.

Respaldo si `psql` no funciona: copia `sitio/db/aplicar_todo.sql` en el SQL Editor de Supabase y ejecútalo. Si cambian las migraciones, regenera el archivo con `node sitio/db/generar_aplicar_todo.mjs` antes de commitear.

## 7. Costos de referencia

Cifras medidas en 2026-10-20 y 2026-10-21 (`CP3_informe.md`, sección 5). Los precios vienen de `pipeline/config.yaml` (`precios_modelos`), que son supuestos hasta que Carlos los confirme en la Console de Anthropic.

| Concepto | USD |
|---|---|
| Tramo A semanal en Actions, 1 noticia, 2 candidatos, 3 corridas del evaluador | 0,65 (medido) |
| Tramo A en local, por noticia | 0,6 – 0,9 |
| Tramo B con simulación nueva | 1,7 – 2,5 |
| Tramo B reutilizando la simulación | 0,55 – 1,0 |
| Tarea nueva completa | 2,5 – 3,5 |

- Tope semanal: 35 USD, con detención al 90 % (31,50).
- Semana 2026-W43: 27,02 USD en `main` (`gasto_semanal.json`), más 0,65 USD de la rama `semanal/2026-W43` (PR #3 cerrado sin merge). Total cercano a 27,67 USD.
- Con el tope de 35 USD caben unas seis tareas completas por semana. El cuello de botella son las dos revisiones humanas.
- Los jobs `medios`, `deploy`, `staging`, `publicada` y Lighthouse no usan la API.

## 8. Comprobar el acceso al simulador

`tramo_b.yml` con `solo_comprobar` = `true` hace checkout de `SIM_REPO`, verifica `simulacion/sim.py` e `insumos/` en la raíz del repositorio privado, importa el adapter contra ese `sim.py` y comprueba que exponga `simular`, `codificar`, `bloques`, `llamar` y `cargar_insumos`. No usa la API, no escribe nada y no necesita `ids`.

- El formulario obliga a rellenar `revisor`, aunque esta comprobación no lo usa. Escribe cualquier nombre.
- Éxito: el log termina con `OK: el adapter importa sim.py del repo externo; no se llamó a la API.`
- Sin los secrets, esta comprobación **falla** (en el modo normal, la ausencia de secrets solo deja un aviso «Tramo B deshabilitado» y no hace nada).
- Comprobación de referencia: ejecución 39600145692, con éxito.
- Si cambia el token, `SIM_REPO_TOKEN` se renueva con el mismo alcance (solo lectura de `contents`) y se vuelve a lanzar esta comprobación.

## 9. Moderación de comentarios

La moderación está descrita en [`sitio/db/README.md`](../sitio/db/README.md): cómo designar un moderador (una fila en `public.moderadores`, desde el SQL Editor), la página `/moderacion/` del sitio, las funciones `comentarios_pendientes()` y `moderar_comentario(...)`, y cómo quitar permisos. Los comentarios nacen `pendiente` y solo se ven `aprobado`. El moderador del piloto es Carlos (`decisiones.md`, 2026-10-20).

## 10. Recalibrar el evaluador

El evaluador vive en `pipeline/agentes/evaluador/` (`evaluador.py` y los prompts `prompt_sistema_v<versión>.md`). Puntúa RUB01 v4.0 (12 criterios de 0 a 2, máximo 24) con un prompt versionado. La versión vigente del prompt es `VERSION_PROMPT = "1.3"`.

### Qué medir contra qué

- **Tareas-oro:** los textos están en `insumos/tareas-oro/` y los puntajes en `evals/oro/puntajes_v0.4_2026-10-20.csv` (9 tareas por 12 criterios).
- **Cinco de los nueve puntajes son provisionales**, puestos por Claude (`insumos/tareas-oro/PUNTUACION-PROVISIONAL_claude_v0.1_2026-10-20.md`). Un kappa contra ellos **no es validez**. El kappa reportable requiere la doble codificación humana (Hugo y Mahsa), que está **pendiente** y debe hacerse antes de CP3.
- **Kappa:** `evals/kappa.py` calcula el kappa ponderado cuadrático, sin scikit-learn. El umbral del script es 0,7.

### Procedimiento

1. Lee el informe vigente, `evals/resultados/calibracion_evaluador_v1.0_2026-10-20.md`, y el historial de cambios de prompt (`CAMBIOS_PROMPT` en `evals/calibrar_evaluador.py`).
2. **Copia el informe vigente** antes de seguir. El script fija `FECHA = "2026-10-20"`, así que una corrida nueva sobrescribe ese archivo. Parametrizar la fecha es **pendiente**.
3. Cambia el prompt: crea el nuevo `prompt_sistema_v<nueva>.md` en `pipeline/agentes/evaluador/` (siguiendo la convención de los existentes) y sube `VERSION_PROMPT` en `evaluador.py`. **No edites RUB01**: es una versión fija (`insumos/rubricas/RUB01_*_v4.0_*`). Una RUB01 nueva es otra versión, con su propio contrato.
4. Corre la calibración en local:

   ```bash
   python evals/calibrar_evaluador.py --prompt <versión>
   ```

   Flags verificados en el código: `--prompt` (por defecto, `VERSION_PROMPT`), `--corridas` (3), `--presupuesto` (tope en USD, 15,0 por defecto), `--paralelo` (3) y `--solo-informe`. Gasta API con Opus, tres corridas por tarea, y escribe `evals/resultados/evaluador_corridas/prompt_v<versión>_<fecha>.json`. Revisa el costo en la Console de Anthropic: los precios del script son supuestos.
5. Para regenerar el informe desde las corridas guardadas, sin gasto: `python evals/calibrar_evaluador.py --solo-informe`.
6. Registra en `pipeline/state/decisiones.md` la versión del prompt, el kappa por criterio y la decisión. La versión del prompt queda también registrada en `evaluacion.json` (invariante 8).

Cambiar un modelo de partida (`pipeline/config.yaml`, `modelos:`) exige evidencia en `evals/resultados/`. La decide `build-lead` o Carlos. La matriz no cambia la configuración por sí sola.

### Matriz modelo × agente

`python evals/run.py` mide los nueve agentes (`AGENTES` en el script) con Haiku, Sonnet y Opus, con un tope de 12 USD por defecto. Escribe `evals/resultados/matriz_<fecha>.md` y `.json`. Flags principales: `--agentes`, `--modelos` (`haiku,sonnet,opus` o ids completos), `--sin-red` (usa `ClienteFalso`: prueba la tubería sin gasto ni medición real), `--tope`, `--reanudar`, `--rehacer`, `--tope-agente AGENTE=USD`, `--paralelo` y `--fecha`. `/otm-eval` lo envuelve desde Claude Code.

## 11. Qué hacer cuando algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `semanal` falla en «Comprobar secrets» con «Faltan secrets» | Falta `ANTHROPIC_API_KEY` o `GH_TOKEN` | Créalos en Settings > Secrets and variables > Actions (ver `docs/secrets.md`). No se gastó nada |
| `semanal` falla en «Validar entradas» | Un input tiene un valor inválido, por ejemplo `noticia_prueba` con el prefijo `noticia_prueba=` | Corrige el valor y vuelve a lanzar. No hubo gasto |
| `semanal` termina con aviso «Tope de gasto» (código 3) | Se alcanzó el 90 % del tope semanal o de `presupuesto_ciclo` | Es esperado. Revisa el PR. Espera a la semana siguiente o reanuda en local. No subas el tope sin decisión de Carlos |
| `semanal` falla con «Ciclo con error» (código distinto de 0 y 3) | Error de un agente o de la API | El expediente conserva `marcas.ultimo_error`. Corrige la causa y reanuda en local con `python -m pipeline.ciclo --continuar <id>`. El gasto ya quedó registrado |
| Job falla con «Invariantes violadas en el estado generado» | El estado generado viola una invariante | El PR contiene solo el gasto y los ciclos. Lee el log del paso «Invariantes». No cierres el PR sin entender el error |
| `tramo_b` falla con «El input revisor es obligatorio» o «El input ids es obligatorio» | Falta el dato en el formulario | Rellena el input y vuelve a lanzar |
| `tramo_b` falla con «SIM_REPO no contiene simulacion/sim.py en su raíz» | El repositorio privado tiene otra estructura, o el secret apunta a otro repo | Revisa `SIM_REPO` (debe ser `carlosrojasbruna/otm-simulador`) y que su raíz sea la carpeta `IDEA MODELAMIENTO` |
| `tramo_b` termina con aviso «Tramo B deshabilitado» | Faltan `SIM_REPO` o `SIM_REPO_TOKEN` | Crea los dos secrets (ver `docs/secrets.md`). Sin ellos no se hace nada |
| `tramo_b` falla porque los ids no existen | Los expedientes no están en `evaluada` dentro de `main` | Mergea primero el PR semanal (revisión humana 1) |
| `publicar` termina con «RECHAZADO» (código 2) | Alguna validación no pasó (sección 5.3). Nada se escribió | Lee el motivo en el log, corrige y vuelve a lanzar |
| `publicar` rechaza con «no se pudo releer la noticia» | La URL de la noticia no responde, o cambió | Comprueba la URL. Mientras no haya texto, no se publica (invariante 3) |
| `publicar` falla en «Ningún id con un PR de publicación abierto» | Ese id ya tiene un PR `publicar/*` abierto | Mergea o cierra ese PR y relanza |
| `publicada` falla en «Comprobar secrets» con «Faltan secrets» (`GH_TOKEN`) | Falta el secret | Créalo (ver `docs/secrets.md`). Nada se escribió. Relanza a mano (sección 5.6) |
| `publicada` sale con código 2 y «el catálogo de main no tiene la v<n>» | El merge no dejó en `main` la versión que el expediente declara, o el catálogo no tiene esa tarea | Revisa el diff de `tareas/catalogo.json` en `main`. Si el PR está bien, corrige la causa y relanza a mano. Nada se escribió |
| `publicada` sale con código 2 y «publicada requiere `revisor`» | El expediente no tiene la marca `revision_humana_2` con `revisor` | Revisa `marcas.revision_humana_2` del expediente en `main`. Si falta, regístrala con la revisión humana 2 correspondiente y relanza a mano. Nada se escribió |
| `publicada` sale con código 2 y «publicada requiere guia.trazabilidad.revision_humana_2» | La guía no tiene la revisión humana 2 registrada | Lo mismo que el caso anterior, en `guia.trazabilidad`. Nada se escribió |
| `publicada` sale con código 2 y un error de validación contra el contrato | Un artefacto del expediente no valida (invariante 1) | Corrige el artefacto por la vía que corresponda y relanza a mano. Nada se escribió |
| `publicada` falla en «Invariantes y commit en main» | El hook de invariantes rechaza `pipeline/state` | No se commiteó nada. Lee el log, corrige el estado y relanza a mano |
| `publicada` falla en el push a `main` | `main` avanzó desde el checkout, o el token no puede escribir en `main` | Relanza a mano desde `main` actualizado. Si la protección de la rama impide el push de `GH_TOKEN`, el repositorio no documenta cómo resolverlo (**pendiente**) |
| `publicada` termina con aviso «Ningún expediente de <rama> en verificada» (código 3) | No hay expedientes de esa rama en `verificada`: ya pasaron a `publicada`, o el PR no traía expedientes | Es un aviso, no un fallo. Comprueba con `python -m pipeline.ciclo --estado` y no repitas el paso |
| El PR de un workflow no dispara CI | El commit lo creó el `GITHUB_TOKEN` de fábrica | Los workflows usan `GH_TOKEN`. Si pasa, revisa el secret |
| `deploy` muestra «Migraciones no aplicadas» | `SUPABASE_DB_URL` mal configurado (usuario o contraseña), o conexión directa | Usa la cadena del Session pooler, actualiza el secret, o aplica `sitio/db/aplicar_todo.sql` en el SQL Editor |
| El job `migraciones` falla antes de `psql` | Falta el secret, o `aplicar_todo.sql` no está al día | Si falta el secret, créalo. Si no está al día, regenera el archivo con `node sitio/db/generar_aplicar_todo.mjs` y commitea |
| El job `staging` falla | Migraciones sin aplicar, RLS o el flujo de cuentas | Mira el log. El script borra lo que creó aunque falle. Si queda un usuario de prueba, bórralo a mano en Supabase > Authentication |

## 12. Pendientes que afectan la operación

- **Corregir o rechazar desde la web:** `--rehacer-guia`, `--nueva-version` y el descarte de un `evaluada` no tienen workflow. Requieren la máquina local.
- **Rechazo del verificador por un defecto de la tarea:** vuelve a `simulada` y gasta la guía (`decisiones.md`).
- **Monto definitivo del tope semanal** (**[D]**, 35 USD es provisional).
- **Kappa reportable:** doble codificación humana pendiente (sección 10).
- **Push de `publicada.yml` si `main` tiene protección:** el repositorio no documenta cómo se resuelve (sección 11).
- **Pendientes de CP3** (aprobado el 2026-10-21): ver `pipeline/state/CP3_informe.md`, sección 7.
