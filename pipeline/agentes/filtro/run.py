"""Agente filtro de modelabilidad: noticia -> noticia con bloque `filtro` (RUB01 v4.0 versión corta).

Uso:
    from pipeline.agentes.filtro.run import filtrar
    r = filtrar(noticia)            # r["noticia"] (con `filtro`, validada) y r["meta"]
CLI:
    python -m pipeline.agentes.filtro.run evals/casos/filtro/<caso>.json

Decisiones (ver DECISIONES.md): el total y `pasa` se calculan aquí, nunca los da el modelo; los
modelos 5.5 no admiten `temperature`; la clave la gestiona pipeline.llm / pipeline.apikey.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from pipeline import invariantes as inv  # noqa: E402
from pipeline.llm import llamar  # noqa: E402

DIR = Path(__file__).resolve().parent
CFG = yaml.safe_load((DIR / "config.yaml").read_text(encoding="utf-8"))
RUB01_PATH = RAIZ / "insumos" / "rubricas" / "RUB01_calidad-tarea_v4.0_2026-10-20.json"
CRITERIOS = CFG["criterios"]
UMBRAL = CFG["umbral"]
VERSION_PROMPT = CFG["version_prompt"]
VERSION_RUBRICA = CFG["version_rubrica"]
_PALABRAS_JUSTIF = 80


def _rub01() -> dict:
    return json.loads(RUB01_PATH.read_text(encoding="utf-8"))


def verificar_config() -> None:
    """La config no puede divergir de RUB01 (fuente única) ni de GOB01 §1."""
    r = _rub01()
    corta = r["version_corta_filtro"]
    if r["version"] != VERSION_RUBRICA:
        raise ValueError(f"RUB01 es v{r['version']}, la config dice v{VERSION_RUBRICA}")
    if corta["criterios"] != CRITERIOS:
        raise ValueError("criterios de config.yaml distintos de RUB01.version_corta_filtro")
    if corta["umbral_propuesto"] != UMBRAL or corta["puntaje_maximo"] != CFG["puntaje_maximo"]:
        raise ValueError("umbral/máximo de config.yaml distintos de RUB01.version_corta_filtro")
    gob = next(RAIZ.joinpath("insumos").glob("GOB01_*.md")).read_text(encoding="utf-8")
    if not re.search(r"Filtro de modelabilidad[^\n]*\|\s*≥\s*%d/10" % UMBRAL, gob):
        raise ValueError("el umbral de config.yaml no coincide con GOB01 §1")


def construir_system() -> str:
    verificar_config()
    r = _rub01()
    crit = []
    for c in r["criterios"]:
        if c["id"] in CRITERIOS:
            crit.append(f"**{c['id']} — {c['nombre']}**\n- 2: {c['2']}\n- 1: {c['1']}\n- 0: {c['0']}")
    texto = (DIR / CFG["prompt"]).read_text(encoding="utf-8")
    return (texto.replace("{{VERSION_RUBRICA}}", r["version"])
                 .replace("{{RUB01_CORTA}}", json.dumps(r["version_corta_filtro"], ensure_ascii=False, indent=1))
                 .replace("{{CRITERIOS}}", "\n\n".join(crit)))


def esquema_salida() -> dict:
    crit = {"type": "object",
            "properties": {"justificacion": {"type": "string"},
                           "puntaje": {"type": "integer", "enum": [0, 1, 2]}},
            "required": ["justificacion", "puntaje"], "additionalProperties": False}
    return {"type": "object",
            "properties": {"criterios": {"type": "object", "properties": {c: crit for c in CRITERIOS},
                                         "required": CRITERIOS, "additionalProperties": False},
                           "justificacion_global": {"type": "string"}},
            "required": ["criterios", "justificacion_global"], "additionalProperties": False}


def calcular(puntajes: dict) -> tuple[int, bool]:
    """Total y decisión: en código, no en el modelo."""
    total = sum(int(puntajes[c]) for c in CRITERIOS)
    return total, total >= UMBRAL


def _recortar(texto: str, n: int = _PALABRAS_JUSTIF) -> str:
    return " ".join(texto.split()[:n])


def construir_mensaje(noticia: dict) -> str:
    campos = ["id", "medio", "titulo", "fecha", "idioma", "area", "resumen_propio", "cifras"]
    return json.dumps({k: noticia[k] for k in campos}, ensure_ascii=False, indent=1)


def filtrar(noticia: dict, cliente=None) -> dict:
    """Devuelve {"noticia": noticia + filtro (validada contra `noticia`), "meta": {...}}."""
    base = copy.deepcopy(noticia)
    base.pop("filtro", None)
    for r in (inv.validar_contra_esquema(base, "noticia"), inv.medio_en_lista_blanca(base["medio_id"])):
        if not r:
            raise ValueError("noticia de entrada inválida: " + "; ".join(r.errores))
    res = llamar(agente="filtro", system=construir_system(), user=construir_mensaje(base),
                 schema=esquema_salida(), max_tokens=CFG["max_tokens"], cliente=cliente)
    sal = res["salida"]
    puntajes = {c: sal["criterios"][c]["puntaje"] for c in CRITERIOS}
    total, pasa = calcular(puntajes)
    por_criterio = {c: sal["criterios"][c]["justificacion"] for c in CRITERIOS}
    salida = copy.deepcopy(base)
    salida["filtro"] = {"version_rubrica": VERSION_RUBRICA, "puntajes": puntajes, "total": total,
                        "pasa": pasa, "justificacion": _recortar(sal["justificacion_global"])}
    # Invariante 3: la justificación no copia texto de la noticia.
    lit = inv.cumple_limite_literal(salida["filtro"]["justificacion"],
                                    base["resumen_propio"] + " " + base["titulo"])
    if not lit:
        raise ValueError("justificación copia texto de la noticia: " + "; ".join(lit.errores))
    v = inv.validar_contra_esquema(salida, "noticia")
    if not v:
        raise ValueError("salida del filtro inválida: " + "; ".join(v.errores))
    meta = dict(res["meta"], version_prompt=VERSION_PROMPT, version_rubrica=VERSION_RUBRICA,
                umbral=UMBRAL, justificaciones_criterio=por_criterio)
    return {"noticia": salida, "meta": meta}


def main(argv: list[str]) -> int:
    caso = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    r = filtrar(caso["noticia"] if "noticia" in caso else caso)
    print(json.dumps({"filtro": r["noticia"]["filtro"], "costo_usd": r["meta"]["costo_usd"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
