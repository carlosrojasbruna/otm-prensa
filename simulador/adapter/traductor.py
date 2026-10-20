"""Traduce `<id>_cod.json` del simulador a `trazas_resumen` (contrato contratos/trazas_resumen.schema.json).

Acepta dos formatos de codificación:
- pipeline (generar.CODER_SCHEMA): turnos, bloqueos, supuestos, modelo, validacion, ruta_principal, ...
- piloto (INS09 v0.2): con fenómenos F1-F6 y riesgos; supuestos = respuesta_final.supuestos_explicitos,
  modelo = ruta_principal (R1...R8), validacion = hay un turno P6-VAL y F5 no es "R".

El resultado se valida contra el esquema (invariante 1) y consistencia_trazas.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from pipeline.invariantes import consistencia_trazas, validar_contra_esquema

FASES = ("P1-MRS", "P2-RM", "P3-MM", "P4-WM", "P5-INT", "P6-VAL", "P7-EXP")
_TRANSICION = re.compile(r"^B[1-6][2-7]$")
_RESOLUCION = {"unresolved": "sin_resolver"}


class TrazasInvalidas(ValueError):
    pass


def ruta_de_fases(turnos: list[Mapping]) -> list[str]:
    """Secuencia de fases dominantes por turno, sin repeticiones consecutivas; descarta EMK y OFF."""
    ruta: list[str] = []
    for t in sorted(turnos, key=lambda t: t["n"]):
        f = t.get("fase")
        if f in FASES and (not ruta or ruta[-1] != f):
            ruta.append(f)
    return ruta


def traducir_codificacion(cod: Mapping, *, avisos: list[str] | None = None, id_: str = "") -> dict:
    """Campos de trazas por corrida (ruta, bloqueos, supuestos, modelo, respuesta_final, validacion)."""
    avisos = avisos if avisos is not None else []
    legado = "fenomenos" in cod
    ruta = ruta_de_fases(cod.get("turnos", []))
    bloqueos = []
    for b in cod.get("bloqueos", []):
        if not _TRANSICION.match(b.get("codigo", "")):
            avisos.append(f"{id_}: bloqueo {b.get('codigo')!r} fuera de B12-B67, omitido")
            continue
        if not b.get("turnos"):
            avisos.append(f"{id_}: bloqueo {b['codigo']} sin turnos, omitido")
            continue
        res = b.get("resolucion", "sin_resolver")
        bloqueos.append({"transicion": b["codigo"], "turnos": [int(x) for x in b["turnos"]],
                         "resolucion": _RESOLUCION.get(res, res)})
    rf = cod.get("respuesta_final", {})
    if legado:
        supuestos = list(rf.get("supuestos_explicitos", []))
        modelo = cod.get("ruta_principal", "")
        validacion = "P6-VAL" in ruta and cod["fenomenos"]["F5"]["codigo"] != "R"
    else:
        supuestos = list(cod.get("supuestos", []))
        modelo = cod.get("modelo", "")
        validacion = bool(cod.get("validacion", False))
    return {
        "ruta": ruta,
        "bloqueos": bloqueos,
        "supuestos": [s for s in supuestos if s],
        "modelo": modelo.strip().lower() or "no_identificado",
        "respuesta_final": rf.get("texto", ""),
        "validacion": validacion,
    }


def agregar(por_corrida: list[Mapping]) -> dict:
    n = len(por_corrida)
    con_bloqueo = Counter()
    for c in por_corrida:
        for tr in {b["transicion"] for b in c["bloqueos"]}:
            con_bloqueo[tr] += 1
    return {
        "pct_bloqueo_por_transicion": {tr: round(k / n, 2) for tr, k in sorted(con_bloqueo.items())},
        "modelos_observados": dict(Counter(c["modelo"] for c in por_corrida)),
        "pct_validan": round(sum(c["validacion"] for c in por_corrida) / n, 2),
    }


def traducir(dir_corridas: Path, *, tarea_id: str, nivel_edad: str, diseno: str, modelo: str,
             fecha: str | None = None, ids: list[str] | None = None) -> tuple[dict, list[str]]:
    """Lee `*_cod.json` de `dir_corridas` y devuelve (trazas_resumen validado, avisos).
    Lanza TrazasInvalidas si no valida contra el esquema o consistencia_trazas."""
    dir_corridas = Path(dir_corridas)
    avisos: list[str] = []
    por_corrida, costo_total = [], 0.0
    archivos = sorted(dir_corridas.glob("*_cod.json"))
    if ids is not None:
        archivos = sorted((a for a in archivos if a.name[:-len("_cod.json")] in ids),
                          key=lambda a: ids.index(a.name[:-len("_cod.json")]))   # orden del diseño
    for p in archivos:
        c = json.loads(p.read_text(encoding="utf-8"))
        run = c["run"]
        base_path = p.with_name(run["id"] + ".json")
        base = json.loads(base_path.read_text(encoding="utf-8")) if base_path.exists() else {}
        t = traducir_codificacion(c["codificacion"], avisos=avisos, id_=run["id"])
        costo = round((base.get("costo_usd") or 0) + (c.get("costo_usd") or 0), 6)
        costo_total += costo
        por_corrida.append({
            "id": run["id"],
            "perfil": {"nivel_edad": nivel_edad, "nivel": run["nivel"], "estilo": run["composicion"]},
            **t,
            "archivo": f"{run['id']}.json",
            "costo_usd": costo,
        })
    if not por_corrida:
        raise TrazasInvalidas(f"no hay *_cod.json en {dir_corridas}")
    trazas: dict[str, Any] = {
        "tarea_id": tarea_id, "diseno": diseno, "corridas": len(por_corrida), "modelo": modelo,
        "costo_usd": round(costo_total, 4), "por_corrida": por_corrida, "agregado": agregar(por_corrida),
    }
    if fecha:
        trazas["fecha"] = fecha
    errores = list(validar_contra_esquema(trazas, "trazas_resumen").errores) + list(consistencia_trazas(trazas).errores)
    if errores:
        raise TrazasInvalidas("trazas_resumen inválido: " + "; ".join(errores[:6]))
    return trazas, avisos
