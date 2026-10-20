"""Agente ilustrador de OTM-Prensa: tarea -> SVG plano validado.

Uso:
    python -m pipeline.agentes.ilustrador.run contratos/ejemplos/tarea_ejemplo.json [salida_dir]

Aislamiento (invariante 6): al modelo solo llegan titulo, area y la vista de estudiante
(enunciado_es, foto_descripcion); nunca task_space, noticia ni cifras.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import yaml
from defusedxml import ElementTree as DET
from jsonschema import Draft202012Validator

from pipeline.llm import llamar

DIR = Path(__file__).resolve().parent
CFG = yaml.safe_load((DIR / "config.yaml").read_text(encoding="utf-8"))
ESQUEMA_SALIDA = json.loads((DIR / "salida.schema.json").read_text(encoding="utf-8"))
PROMPT = (DIR / "prompt.md").read_text(encoding="utf-8")

VIEWBOX = CFG["svg"]["viewBox"]
MAX_BYTES = CFG["svg"]["max_bytes"]
MAX_ELEMENTOS = CFG["svg"]["max_elementos"]
MAX_PAL_TD = CFG["svg"]["max_palabras_title_desc"]

# Paleta extraída de insumos/diseno/*.svg (home v1, interfaz v2, pipeline v2).
PALETA = frozenset("""
#f3f4f6 #ffffff #e5e7eb #f5f3ff #ede9fe #ddd6fe #fff7ed #fef3c7 #fef9c3 #fee2e2 #ecfdf5 #dcfce7 #dbeafe
#eff6ff #e0f2fe #bae6fd #bfdbfe #f3e8ff #e0e7ff #fde68a #7c3aed #6d28d9 #4c1d95 #c4b5fd #f97316 #ea580c
#c2410c #f59e0b #d97706 #b45309 #92400e #10b981 #047857 #15803d #86efac #4ade80 #22c55e #3b82f6 #1d4ed8
#1e40af #1e3a8a #60a5fa #93c5fd #6366f1 #ef4444 #111827 #1f2937 #374151 #4b5563 #6b7280 #9ca3af #d1d5db
""".split())
ELEMENTOS = frozenset("svg g rect circle ellipse line polyline polygon path title desc".split())
ATRIBUTOS = frozenset("x y width height rx ry cx cy r x1 y1 x2 y2 points d fill stroke stroke-width "
                      "stroke-linecap stroke-linejoin opacity transform viewBox".split())
NUMERICOS = frozenset("x y width height rx ry cx cy r x1 y1 x2 y2 stroke-width opacity".split())
NS_SVG = "http://www.w3.org/2000/svg"
RE_D = re.compile(r"^[MmLlHhVvCcSsQqTtAaZz0-9eE.,\s+-]*$")
RE_TRANSFORM = re.compile(r"^(?:\s*(?:translate|scale|rotate)\([0-9eE.,\s+-]*\)\s*)*$")
RE_NUM = re.compile(r"^-?[0-9]+(\.[0-9]+)?$")
RE_NUMS = re.compile(r"^[0-9eE.,\s+-]*$")


def validar_svg(svg: str) -> list[str]:
    """Devuelve la lista de errores (vacía = válido): estructura, seguridad, paleta y tamaño."""
    err: list[str] = []
    if not isinstance(svg, str) or not svg.strip():
        return ["svg vacío"]
    if len(svg.encode("utf-8")) > MAX_BYTES:
        err.append(f"svg excede {MAX_BYTES} bytes")
    if re.search(r"<!(?:DOCTYPE|ENTITY|\[CDATA)|<\?(?!xml )", svg, re.I):
        err.append("DOCTYPE/ENTITY/CDATA/instrucciones de proceso no permitidos")
    try:
        raiz = DET.fromstring(svg)
    except Exception as e:  # noqa: BLE001 — XML mal formado o entidades rechazadas por defusedxml
        return err + [f"XML inválido: {type(e).__name__}: {str(e)[:120]}"]
    if raiz.tag != f"{{{NS_SVG}}}svg":
        err.append('la raíz debe ser <svg xmlns="http://www.w3.org/2000/svg">')
    n = 0
    for el in raiz.iter():
        n += 1
        if not isinstance(el.tag, str):
            err.append("nodo no elemento (comentario/instrucción)")
            continue
        if not el.tag.startswith(f"{{{NS_SVG}}}"):
            err.append(f"elemento fuera del namespace SVG: {el.tag[:40]}")
            continue
        nombre = el.tag.split("}", 1)[1]
        if nombre not in ELEMENTOS:
            err.append(f"elemento no permitido: <{nombre}>")
        if nombre in ("title", "desc"):
            t = "".join(el.itertext())
            if len(t.split()) > MAX_PAL_TD:
                err.append(f"<{nombre}> excede {MAX_PAL_TD} palabras")
            if re.search(r"[0-9]", t):
                err.append(f"<{nombre}> contiene dígitos")
            if len(list(el)):
                err.append(f"<{nombre}> no admite hijos")
        elif (el.text or "").strip():
            err.append(f"texto suelto dentro de <{nombre}>")
        for k, v in el.attrib.items():
            if k.startswith("{"):
                err.append(f"atributo con namespace no permitido: {k[:50]}")
                continue
            if k not in ATRIBUTOS:
                err.append(f"atributo no permitido: {k}")
                continue
            if re.search(r"url\s*\(|javascript:|data:|https?:|//", v, re.I):
                err.append(f"valor con enlace/url en {k}")
            if k in ("fill", "stroke"):
                if v != "none" and v.lower() not in PALETA:
                    err.append(f"color fuera de paleta en {k}: {v[:20]}")
            elif k == "d" and not RE_D.match(v):
                err.append("path d con caracteres no permitidos")
            elif k == "transform" and not RE_TRANSFORM.match(v):
                err.append("transform no permitido")
            elif k == "points" and not RE_NUMS.match(v):
                err.append("points inválido")
            elif k in NUMERICOS and not RE_NUM.match(v.strip()):
                err.append(f"valor numérico inválido en {k}: {v[:20]}")
            elif k == "stroke-linecap" and v not in ("butt", "round", "square"):
                err.append("stroke-linecap inválido")
            elif k == "stroke-linejoin" and v not in ("miter", "round", "bevel"):
                err.append("stroke-linejoin inválido")
        if (el.tail or "").strip():
            err.append("texto suelto entre elementos")
    if n > MAX_ELEMENTOS:
        err.append(f"más de {MAX_ELEMENTOS} elementos")
    if raiz.attrib.get("viewBox") != VIEWBOX:
        err.append(f"viewBox debe ser '{VIEWBOX}'")
    return err


def paleta_usada(svg: str) -> list[str]:
    return sorted({c.lower() for c in re.findall(r'(?:fill|stroke)="(#[0-9a-fA-F]{6})"', svg)})


def _esquema_modelo() -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["svg", "foto_descripcion"],
            "properties": {"svg": {"type": "string"}, "foto_descripcion": {"type": "string"}}}


def construir_mensaje(tarea: dict) -> str:
    """Solo lo que ve un estudiante (invariante 6) más título y área; nunca task_space ni noticia."""
    est = tarea["estudiante"]
    return json.dumps({"titulo": tarea["titulo"], "area": tarea["area"],
                       "enunciado_es": est["enunciado_es"], "foto_descripcion": est["foto_descripcion"]},
                      ensure_ascii=False, indent=2)


def validar_salida(salida: dict) -> list[str]:
    """Esquema local + validador SVG + coherencia de foto_descripcion."""
    errs = [f"{'/'.join(map(str, e.path))}: {e.message}"
            for e in Draft202012Validator(ESQUEMA_SALIDA).iter_errors(salida)]
    errs += validar_svg(salida.get("svg", ""))
    if re.search(r"[0-9]", salida.get("foto_descripcion", "")):
        errs.append("foto_descripcion contiene dígitos")
    return errs


def ilustrar(tarea: dict, cliente=None) -> dict:
    mensaje = construir_mensaje(tarea)
    costo, ultimo = 0.0, []
    for intento in range(CFG["reintentos_reparacion"] + 1):
        user = mensaje if not ultimo else (
            mensaje + "\n\nTu SVG anterior fue rechazado por estos errores; corrígelos:\n- " + "\n- ".join(ultimo[:10]))
        r = llamar(agente="ilustrador", system=PROMPT, user=user, schema=_esquema_modelo(),
                   esfuerzo=CFG["esfuerzo"], max_tokens=CFG["max_tokens"], cliente=cliente)
        costo += r["meta"]["costo_usd"]
        svg = r["salida"]["svg"].strip()
        salida = {
            "tarea_id": tarea["id"], "svg": svg, "foto_descripcion": r["salida"]["foto_descripcion"].strip(),
            "paleta_usada": paleta_usada(svg), "viewBox": VIEWBOX, "bytes": len(svg.encode("utf-8")),
            "meta": {"agente": "ilustrador", "modelo": r["meta"]["modelo"], "version_prompt": CFG["version_prompt"],
                     "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "costo_usd": round(costo, 6), "intentos_reparacion": intento},
        }
        ultimo = validar_salida(salida)
        if not ultimo:
            return salida
    raise ValueError("el ilustrador no produjo un SVG válido: " + "; ".join(ultimo[:5]))


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    tarea = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    out = Path(argv[1]) if len(argv) > 1 else RAIZ / "evals" / "resultados"
    out.mkdir(parents=True, exist_ok=True)
    s = ilustrar(tarea)
    (out / f"ilustrador_{tarea['id']}.svg").write_text(s["svg"], encoding="utf-8")
    (out / f"ilustrador_{tarea['id']}.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"tarea_id": s["tarea_id"], "bytes": s["bytes"], "costo_usd": s["meta"]["costo_usd"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
