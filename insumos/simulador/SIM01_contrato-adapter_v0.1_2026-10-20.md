# SIM01 – Contrato del adapter entre el pipeline y el simulador

| Campo | Valor |
|---|---|
| Versión | v0.1 |
| Fecha | 2026-10-20 |
| Simulador | `IDEA MODELAMIENTO/simulacion/sim.py` v0.1 (README 2026-10-01) |
| Principio | **No se toca `sim.py`.** El adapter produce los tres archivos de insumo que `sim.py` ya sabe leer (bloques ```json id``` / ```text id```) y traduce las salidas al esquema común del repositorio |

## 1. Lo que el simulador necesita (entrada)

`sim.py` lee tres rutas fijas (`F_TAREA`, `F_PERFILES`, `F_PROMPTS`). El adapter genera, por tarea, una carpeta `sim/` con tres archivos del mismo formato y lanza `sim.py` apuntando a ellos (vía variables de entorno o copia temporal; decidir en `sim-integrator`).

| Archivo generado | Bloques obligatorios | De dónde salen |
|---|---|---|
| `TAREA.md` | ```text enunciado_es```, ```text foto_descripcion``` | PLT01 §1 (`enunciado_es`, `foto_descripcion`) |
| `PERFILES.md` | ```json niveles``` (N1–N4), ```json estilos``` (V/A/I), ```json contexto_base```, ```json diseno_otm``` | MAR03 §3 (niveles por P/S/U) · INS08 `estilos` sin cambios · contexto base por tramo · diseño: N grupos |
| `PROMPTS.md` | ```text student_system```, ```text student_turn```, ```text coder_system```, ```text coder_user```, ```json coder_schema``` | INS09 v0.2 sin cambios, salvo que el `coder_system` reciba el `task_space` de PLT01 §4 en lugar de INS02/INS03 |

Diseño por defecto para el pipeline (`diseno_otm`): 6 corridas = 3 niveles (N1, N2/N3, N4) × 2 composiciones (VV, AA), 1 repetición; pares. Se amplía a 12 si CP2 muestra que faltan rutas.

Regla de aislamiento (hook): los estudiantes simulados reciben **solo** `enunciado_es`, `foto_descripcion` y los recursos marcados "a solicitud". Nunca `task_space`.

## 2. Lo que el simulador entrega (salida)

Por corrida: `<id>.json` (transcripción, perfiles, costo), `<id>.md` y `<id>_cod.json` (codificación con `coder_schema`: fase por turno, bloqueos con transición y resolución, fenómenos, ruta, respuesta final).

## 3. Traducción al esquema del repositorio (`trazas/`)

```yaml trazas_resumen
tarea_id: AAAA-MM-slug
diseno: diseno_otm
corridas: 6
modelo: ""                      # el que use claude -p en esa máquina
por_corrida:
  - id: N1_VV_r1
    perfil: {nivel_edad: S2, nivel: N1, estilo: VV}
    ruta: [P1-MRS, P2-RM, P3-MM, P4-WM, P5-INT, P7-EXP]
    bloqueos: [{transicion: B12, turnos: [4,5,6], resolucion: peer}]
    supuestos: ["consumo constante", "sin lluvias"]
    modelo: "lineal"
    respuesta_final: ""
    validacion: false
agregado:
  pct_bloqueo_por_transicion: {B12: 0.67, B23: 0.33, B34: 0.17, B45: 0.33, B56: 0.50}
  modelos_observados: {lineal: 4, exponencial: 1, proporcional: 1}
  pct_validan: 0.33
```

El redactor de guía (PLT02 §4–5) construye los escenarios **solo** desde `trazas_resumen` y los `<id>.md`; el verificador comprueba que cada escenario cite un `id` de corrida.

## 4. Diferencias con el piloto que hay que resolver en `sim-integrator`

| Tema | Piloto (Sugarloaf) | Pipeline |
|---|---|---|
| Niveles N1–N4 | Texto con Pitágoras | Texto por nivel P/S/U (MAR03 §3) |
| Contexto base | 9° grado, pares, español | Por nivel P/S/U; el idioma sigue siendo español |
| Foto | Descripción textual de la foto original | Descripción del ícono/imagen de la tarea; puede ser "none" |
| Codificador | INS03 (fenómenos F1–F6 de Sugarloaf) | Sin fenómenos documentados; solo fases, bloqueos, supuestos, ruta (INS04) |
| Ejecución | `claude -p` local con sesión iniciada | Igual en la máquina del equipo, o API con `ANTHROPIC_API_KEY` en Actions. **Decidir**: si corre en Actions hay que portar `llamar()` a la API (único cambio en `sim.py`, aislado en una función) |
| Costo | 16 corridas | 6 por tarea × 2–3 tareas/semana |

## 5. Casos de prueba del adapter

1. Reproducir una corrida del piloto (`corridas/piloto_v0.1/N1_AA_r1.json`) con los mismos insumos y obtener una codificación comparable (misma ruta, mismos bloqueos ± 1).
2. Correr Sugarloaf (tareas-oro) en nivel S1 y comprobar que el `trazas_resumen` valida contra el esquema.
3. Hook de aislamiento: intentar pasar `task_space` al estudiante y verificar que el adapter lo rechaza.
