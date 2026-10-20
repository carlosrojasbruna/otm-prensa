"""Lanza las corridas del simulador para una tarea PLT01 sin modificar sim.py.

Mecanismo (decisión build-lead): se importa `sim` desde la ruta de config y, en tiempo de ejecución,
se sustituyen sus globales `F_TAREA`, `F_PERFILES`, `F_PROMPTS`, `OUT` y `llamar` (parchear_sim).
Se llama a `sim.simular` y `sim.codificar` directamente: `sim.main()` no se usa porque exige el bloque
`diseno_piloto` y un diseño producto (niveles x composiciones), mientras diseno_otm es una lista de 6 corridas.

Salidas bajo `dir_tarea`:
  sim/TAREA.md, PERFILES.md, PROMPTS.md, manifiesto.json     insumos generados
  sim/corridas/<id>.json|.md|_cod.json                       salidas de sim.py
  trazas/trazas_resumen.json                                  traducción validada
"""
from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from typing import Mapping

from . import _comun, generar, llamar_api, niveles, traductor
from .hooked import crear_llamar

_LOCK = threading.RLock()   # el parche es global al módulo sim: una tarea a la vez por proceso


@contextmanager
def parchear_sim(sim, *, f_tarea: Path, f_perfiles: Path, f_prompts: Path, out: Path, llamar):
    with _LOCK:
        previo = {k: getattr(sim, k) for k in ("F_TAREA", "F_PERFILES", "F_PROMPTS", "OUT", "llamar")}
        sim.F_TAREA, sim.F_PERFILES, sim.F_PROMPTS = Path(f_tarea), Path(f_perfiles), Path(f_prompts)
        sim.OUT, sim.llamar = Path(out), llamar
        try:
            yield sim
        finally:
            for k, v in previo.items():
                setattr(sim, k, v)


def cargar_bloques(sim, dir_sim: Path) -> dict:
    """Equivalente de sim.cargar_insumos() para los archivos generados (diseno_otm en vez de diseno_piloto)."""
    b: dict = {}
    for nombre in ("TAREA.md", "PERFILES.md", "PROMPTS.md"):
        b.update(sim.bloques(Path(dir_sim) / nombre))
    faltan = {"enunciado_es", "foto_descripcion", "niveles", "estilos", "contexto_base", "diseno_otm",
              "student_system", "student_turn", "coder_system", "coder_user", "coder_schema"} - b.keys()
    if faltan:
        raise ValueError(f"Faltan bloques en los insumos generados: {sorted(faltan)}")
    b["_diseno"], b["_diseno_id"] = b["diseno_otm"], "diseno_otm"
    return b


def corridas_del_diseno(d: Mapping) -> list[dict]:
    runs = []
    for c in d["corridas"]:
        for rep in range(1, d["repeticiones"] + 1):
            runs.append({"id": f"{c['nivel']}_{c['composicion']}_r{rep}", "nivel": c["nivel"],
                         "composicion": c["composicion"], "rep": rep,
                         "estilos": d["composiciones"][c["composicion"]], "empieza": (rep - 1) % 2})
    return runs


def _manifiesto(tarea: Mapping, diseno: Mapping, sim, backend: str) -> dict:
    return {
        "tarea_id": tarea["id"], "version_tarea": tarea["version"], "tramo": diseno["tramo"],
        "backend": backend, "diseno": "diseno_otm", "corridas": len(corridas_del_diseno(diseno)),
        "modelo_estudiantes": diseno["modelo_estudiantes"], "modelo_codificador": diseno["modelo_codificador"],
        "insumos_simulador": {"INS08": Path(sim.F_PERFILES).name, "INS09": Path(sim.F_PROMPTS).name},
        "marco_niveles": "MAR03 v1.0 §3", "fecha": _comun.fecha_hora_utc(),
    }


def lanzar(tarea: Mapping, dir_tarea: Path, *, backend: str | None = None, cliente=None, solo: list[str] | None = None,
           workers: int = 3, presupuesto_usd: float | None = None, traducir: bool = True,
           modelo_estudiantes: str | None = None, modelo_codificador: str | None = None, sim=None) -> dict:
    """Genera los insumos, corre las corridas (`solo` limita a ciertos ids), codifica y traduce.

    Devuelve {"trazas", "avisos", "errores", "costo_usd", "llamadas", "dir_corridas", "ids"}. Las corridas
    ya existentes se omiten (comportamiento de sim.py), de modo que se puede reanudar."""
    backend = backend or _comun.config_sim()["backend"]
    sim = sim or _comun.cargar_sim()
    dir_tarea = Path(dir_tarea)
    dir_sim = dir_tarea / "sim"
    out = dir_sim / "corridas"
    diseno = generar.generar_todo(tarea, dir_sim, sim, modelo_estudiantes=modelo_estudiantes,
                                  modelo_codificador=modelo_codificador)
    f_tarea, f_perfiles, f_prompts = (dir_sim / n for n in ("TAREA.md", "PERFILES.md", "PROMPTS.md"))
    dir_tarea.mkdir(parents=True, exist_ok=True)
    gasto = llamar_api.Gasto(presupuesto_usd, ledger=dir_tarea / 'gasto.jsonl')
    original = sim.llamar   # versión `claude -p` de sim.py (el parche se revierte al salir)
    with parchear_sim(sim, f_tarea=f_tarea, f_perfiles=f_perfiles, f_prompts=f_prompts, out=out,
                      llamar=original):
        hook = crear_llamar(tarea, backend=backend, cliente=cliente, gasto=gasto, llamar_claude_p=original)
        sim.llamar = hook
        b = cargar_bloques(sim, dir_sim)
        (dir_sim / "manifiesto.json").write_text(
            json.dumps(_manifiesto(tarea, diseno, sim, backend), ensure_ascii=False, indent=2), encoding="utf-8")
        runs = [r for r in corridas_del_diseno(b["_diseno"]) if not solo or r["id"] in solo]
        errores: list[str] = []

        def una(run):
            try:
                sim.simular(run, b)
                sim.codificar(out / f"{run['id']}.json", b)
            except Exception as e:  # noqa: BLE001 - una corrida fallida no tira las demás
                errores.append(f"{run['id']}: {type(e).__name__}: {e}")
                if type(e).__name__ == "AislamientoError":
                    raise

        with ThreadPoolExecutor(max_workers=workers) as ex:
            for fut in [ex.submit(una, r) for r in runs]:
                fut.result()
    res = {"errores": errores, "costo_usd": round(gasto.total, 4), "llamadas": gasto.llamadas,
           "dir_corridas": out, "ids": [r["id"] for r in runs], "trazas": None, "avisos": []}
    if traducir:
        trazas, avisos = traductor.traducir(
            out, tarea_id=tarea["id"], nivel_edad=niveles.tramo_de(dict(tarea)), diseno="diseno_otm",
            modelo=diseno["modelo_estudiantes"], fecha=_comun.fecha_hora_utc(), ids=[r["id"] for r in runs])
        d_tr = dir_tarea / "trazas"
        d_tr.mkdir(parents=True, exist_ok=True)
        (d_tr / "trazas_resumen.json").write_text(json.dumps(trazas, ensure_ascii=False, indent=2), encoding="utf-8")
        res["trazas"], res["avisos"] = trazas, avisos
    return res

