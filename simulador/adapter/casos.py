"""Casos de aceptación de SIM01 §5 (Sugarloaf). Salidas en evals/resultados/sim_adapter/, nunca en corridas/.

tarea_sugarloaf(): tarea PLT01 (S1) armada con enunciado_es y foto_descripcion de INS02 v0.2 (leídos del repo
del simulador en tiempo de ejecución) y un task_space en palabras propias a partir de INS02 §2-§4.
"""
from __future__ import annotations

import json
from pathlib import Path

from pipeline.invariantes import validar_contra_esquema

from . import _comun, generar, lanzador, llamar_api, traductor
from .hooked import crear_llamar

DIR_RESULTADOS = _comun.RAIZ / "evals" / "resultados" / "sim_adapter"


def _ins02() -> Path:
    rutas = sorted(_comun.insumos_simulador().glob("INS02_analisis-a-priori_sugarloaf_v0.2_*.md"))
    if not rutas:
        raise FileNotFoundError("INS02 v0.2 no está en el repo del simulador")
    return rutas[-1]


def tarea_sugarloaf() -> dict:
    b = generar.bloques_de(_ins02())
    ruta = lambda i, n, nv, m, r: {"id": i, "nombre": n, "nivel": nv, "modelo": m, "resultado": r}  # noqa: E731
    fila = lambda d, bl=None: {"decision": d, "evidencia": "registro escrito del par", "bloqueo_probable": bl}  # noqa: E731
    tarea = {
        "id": "2026-10-sugarloaf",
        "titulo": "Sugarloaf (Pan de Azúcar)",
        "estado": "borrador",
        "version": 1,
        "fecha": "2026-10-20",
        "noticia": {
            "medio": "Blum y Leiß (2007), tarea Sugarloaf",
            "titulo": "How do students and teachers deal with modelling problems? (tarea Sugarloaf, p. 224)",
            "fecha": "2007-01-01",
            "url": "https://example.org/blum-leiss-2007-sugarloaf",
            "resumen_propio": "Tarea de modelación de la literatura didáctica: un teleférico sube un cerro en un tiempo y a una velocidad dadas, con un desnivel conocido, y se pide estimar la distancia horizontal hasta el pie del cerro. Incluye un dato de tiempo que no es necesario.",
            "cifras_usadas": [
                {"valor": 3, "unidad": "min", "que_es": "duración del viaje en teleférico",
                 "localizador": {"fuente": "noticia", "ubicacion": "BL07 p. 224"}},
                {"valor": 30, "unidad": "km/h", "que_es": "velocidad del teleférico",
                 "localizador": {"fuente": "noticia", "ubicacion": "BL07 p. 224"}},
                {"valor": 180, "unidad": "m", "que_es": "desnivel del cerro",
                 "localizador": {"fuente": "noticia", "ubicacion": "BL07 p. 224"}},
            ],
        },
        "nivel_principal": "S",
        "sub_tramo": "S1",
        "variantes": {"abajo": None, "arriba": None},
        "area": "transporte_ciudad",
        "contenidos_matematicos": ["conversión de unidades", "velocidad y tiempo", "teorema de Pitágoras"],
        "tiempo_estimado": "1 sesión de 60 min",
        "estudiante": {"enunciado_es": b["enunciado_es"], "foto_descripcion": b["foto_descripcion"],
                       "recursos_a_solicitud": []},
        "variantes_detalle": {"abajo": None, "arriba": None},
        "recursos_de_entrada": [],
        "mapa_ciclo": {
            "P1-MRS": fila("imaginar el teleférico, el cerro y la llanura e identificar la incógnita", None),
            "P2-RM": fila("suponer cable recto, velocidad constante, cerro sin ancho; descartar el dato de tiempo de escalada", "B12"),
            "P3-MM": fila("representar el trayecto como un triángulo rectángulo", "B23"),
            "P4-WM": fila("convertir unidades, obtener el recorrido y calcular el cateto horizontal", None),
            "P5-INT": fila("interpretar el resultado como distancia hasta el pie del cerro", None),
            "P6-VAL": fila("discutir el ancho del cerro, la forma del cable y la velocidad no constante", "B56"),
            "P7-EXP": fila("comunicar una respuesta aproximada con sus supuestos", None),
        },
        "task_space": {
            "required_assumptions": [
                "el cable es recto", "la velocidad del teleférico es constante",
                "el cerro no tiene ancho (la cima está sobre el pie del cerro)",
                "la estación del valle está a la altura del pie del cerro",
            ],
            "reference_solution": {
                "steps": "El recorrido del teleférico es velocidad por tiempo (30 km/h por 0,05 h = 1,5 km) y hace de hipotenusa; el desnivel de 0,18 km es un cateto; el otro cateto es la raíz de 1,5 al cuadrado menos 0,18 al cuadrado. El tiempo de escalada no se usa.",
                "result": "aproximadamente 1,49 km, es decir cerca de 1,5 km",
                "acceptable_range": "1,2 a 1,5 km, con supuestos explícitos",
            },
            "routes": [
                ruta("R1", "regla de tres sin modelo de la situación", "S1", "velocidad por tiempo", "1,5 km"),
                ruta("R2", "Pitágoras sin validación", "S1", "triángulo rectángulo", "1,49 km"),
                ruta("R3", "Pitágoras con validación", "S1", "triángulo rectángulo y revisión de supuestos", "cerca de 1,4 km"),
                ruta("R4", "bloqueo y destrabe del ángulo recto, luego Pitágoras", "S1", "triángulo rectángulo", "1,49 km"),
                ruta("R5", "intento de usar el tiempo de escalada", "S1", "combinación de datos", "valores incoherentes"),
                ruta("R6", "Pitágoras mal aplicado (suma de cuadrados)", "S1", "triángulo rectángulo", "cerca de 1,51 km"),
                ruta("R7", "error de unidades", "S1", "velocidad por tiempo sin convertir", "valores absurdos"),
                ruta("R8", "trigonometría", "S1", "razón trigonométrica", "1,49 km"),
            ],
            "modelo_inadecuado": {"id": "R1", "por_que_falla": "Toma el recorrido del teleférico como la distancia horizontal, sin construir la geometría de la situación."},
            "validation_evidence": "Considerar que el cerro tiene un ancho de unas decenas de metros reduce el resultado hacia 1,4 km; una velocidad menor al inicio y al final también lo reduce.",
            "agent_visibility": {"students": ["enunciado_es", "foto_descripcion", "recursos_a_solicitud"],
                                 "coder": ["enunciado_es", "task_space"], "guide": ["all"]},
        },
        "rubrica_rub01": None,
        "rubrica_rub02": {"P": None, "S": None, "U": None},
        "modelo_y_prompt": {"diseñador": "tarea-oro (no generada)", "version_prompt": "0", "version_rubrica": "4.0"},
    }
    r = validar_contra_esquema(tarea, "tarea")
    if not r:
        raise ValueError("tarea_sugarloaf no valida: " + "; ".join(r.errores))
    return tarea


# --------------------------------------------------------------------------- caso 1
def comparar(piloto_cod: dict, repro_cod: dict) -> dict:
    """Comparación de dos codificaciones (formato piloto o pipeline): ruta y bloqueos (±1)."""
    a, b = traductor.traducir_codificacion(piloto_cod["codificacion"]), traductor.traducir_codificacion(repro_cod["codificacion"])
    rp, rr = piloto_cod["codificacion"].get("ruta_principal"), repro_cod["codificacion"].get("ruta_principal")
    return {
        "ruta_principal": {"piloto": rp, "repro": rr, "igual": rp == rr},
        "rutas": {"piloto": piloto_cod["codificacion"].get("rutas"), "repro": repro_cod["codificacion"].get("rutas")},
        "bloqueos_piloto": [(x["transicion"], x["turnos"], x["resolucion"]) for x in a["bloqueos"]],
        "bloqueos_repro": [(x["transicion"], x["turnos"], x["resolucion"]) for x in b["bloqueos"]],
        "n_bloqueos": {"piloto": len(a["bloqueos"]), "repro": len(b["bloqueos"]),
                       "dentro_de_1": abs(len(a["bloqueos"]) - len(b["bloqueos"])) <= 1},
        "ruta_fases": {"piloto": a["ruta"], "repro": b["ruta"]},
    }


def caso1_reproducir(run_id: str = "N1_AA_r1", *, dir_salida: Path | None = None, backend: str | None = None,
                     cliente=None, presupuesto_usd: float | None = None, sufijo: str = "") -> dict:
    """Corre la corrida `run_id` del piloto con los insumos originales (INS02/08/09 de sim.py) vía API."""
    sim = _comun.cargar_sim()
    backend = backend or _comun.config_sim()["backend"]
    tarea = tarea_sugarloaf()
    out = Path(dir_salida or DIR_RESULTADOS / "caso1_reproduccion") / f"{run_id}{sufijo}"
    out.mkdir(parents=True, exist_ok=True)
    b = sim.cargar_insumos()   # rutas originales; solo lectura
    b["_diseno_id"], b["_diseno"] = "piloto", b["diseno_piloto"]
    run = next(r for r in sim.corridas_del_diseno(b) if r["id"] == run_id)
    gasto = llamar_api.Gasto(presupuesto_usd, ledger=DIR_RESULTADOS / 'gasto_caso1.jsonl')
    original = sim.llamar
    hook = crear_llamar(tarea, backend=backend, cliente=cliente, gasto=gasto, llamar_claude_p=original)
    with lanzador.parchear_sim(sim, f_tarea=sim.F_TAREA, f_perfiles=sim.F_PERFILES, f_prompts=sim.F_PROMPTS,
                               out=out, llamar=hook):
        msg1 = sim.simular(run, b)
        msg2 = sim.codificar(out / f"{run_id}.json", b)
    piloto_cod = json.loads((Path(sim.__file__).parent / "corridas" / b["diseno_piloto"]["carpeta"] / f"{run_id}_cod.json").read_text(encoding="utf-8"))
    repro_cod = json.loads((out / f"{run_id}_cod.json").read_text(encoding="utf-8"))
    cmp = comparar(piloto_cod, repro_cod)
    cmp["mensajes"] = [msg1, msg2]
    cmp["costo_usd"] = round(gasto.total, 4)
    (out / "comparacion_con_piloto.json").write_text(json.dumps(cmp, ensure_ascii=False, indent=2), encoding="utf-8")
    return cmp


# --------------------------------------------------------------------------- caso 2
def caso2_sugarloaf(*, dir_salida: Path | None = None, backend: str | None = None, cliente=None,
                    presupuesto_usd: float | None = None, solo: list[str] | None = None, workers: int = 3) -> dict:
    """Sugarloaf en S1 con el diseño de 6 corridas; escribe trazas_resumen.json y lo valida."""
    out = Path(dir_salida or DIR_RESULTADOS / "caso2_sugarloaf")
    return lanzador.lanzar(tarea_sugarloaf(), out, backend=backend, cliente=cliente, solo=solo,
                           presupuesto_usd=presupuesto_usd, workers=workers)


def caso1_recodificar_transcripcion_piloto(run_id: str = "N1_AA_r1", *, dir_salida: Path | None = None,
                                           backend: str | None = None, cliente=None,
                                           presupuesto_usd: float | None = None) -> dict:
    """Variante determinista del caso 1: toma la transcripción del piloto (sin volver a simular a los
    estudiantes) y la codifica vía API con los insumos originales. Aísla el port del codificador."""
    import shutil
    sim = _comun.cargar_sim()
    backend = backend or _comun.config_sim()["backend"]
    tarea = tarea_sugarloaf()
    out = Path(dir_salida or DIR_RESULTADOS / "caso1_recodificacion_piloto") / run_id
    out.mkdir(parents=True, exist_ok=True)
    b = sim.cargar_insumos()
    b["_diseno_id"], b["_diseno"] = "piloto", b["diseno_piloto"]
    carpeta = Path(sim.__file__).parent / "corridas" / b["diseno_piloto"]["carpeta"]
    shutil.copy(carpeta / f"{run_id}.json", out / f"{run_id}.json")   # solo se lee del repo del simulador
    gasto = llamar_api.Gasto(presupuesto_usd, ledger=DIR_RESULTADOS / "gasto_caso1.jsonl")
    hook = crear_llamar(tarea, backend=backend, cliente=cliente, gasto=gasto, llamar_claude_p=sim.llamar)
    with lanzador.parchear_sim(sim, f_tarea=sim.F_TAREA, f_perfiles=sim.F_PERFILES, f_prompts=sim.F_PROMPTS,
                               out=out, llamar=hook):
        sim.codificar(out / f"{run_id}.json", b)
    piloto_cod = json.loads((carpeta / f"{run_id}_cod.json").read_text(encoding="utf-8"))
    cmp = comparar(piloto_cod, json.loads((out / f"{run_id}_cod.json").read_text(encoding="utf-8")))
    cmp["costo_usd"] = round(gasto.total, 4)
    (out / "comparacion_con_piloto.json").write_text(json.dumps(cmp, ensure_ascii=False, indent=2), encoding="utf-8")
    return cmp
