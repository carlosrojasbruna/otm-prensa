"""Agente verificador (7): rechaza guías y tareas con cifras o escenarios sin respaldo.

Diseño: comprobaciones deterministas en código (invariantes 1, 3, 4, 5, coherencia de ids,
notebook de escenarios) y, solo si no hay hallazgos críticos de código, una llamada al modelo
para contrastar semánticamente cada cifra con su localizador y detectar afirmaciones sin respaldo.
El modelo nunca levanta un hallazgo crítico de código.

Uso:
    python pipeline/agentes/verificador/run.py --tarea t.json --guia g.json --trazas z.json \
        [--noticia n.json] [--texto-noticia t.txt] [--notebook escenarios.ipynb] [--salida informe.json]
    (sin argumentos usa los ejemplos de contratos/ejemplos/)
Código de salida: 0 aprobado, 2 rechazado.

`texto_noticia` solo se lee en memoria para la invariante 3; nunca se guarda ni se envía al modelo.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from pipeline import invariantes as inv  # noqa: E402
from pipeline.llm import llamar  # noqa: E402

AQUI = Path(__file__).resolve().parent
CONFIG = yaml.safe_load((AQUI / "config.yaml").read_text(encoding="utf-8"))
PROMPT = (AQUI / CONFIG["prompt"]).read_text(encoding="utf-8")
ESQUEMA_SALIDA = json.loads((AQUI / CONFIG["esquema_salida"]).read_text(encoding="utf-8"))

ESQUEMA_MODELO = {
    "type": "object",
    "additionalProperties": False,
    "required": ["cifras", "afirmaciones_no_respaldadas"],
    "properties": {
        "cifras": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["indice", "coincide", "valor_en_fuente", "nota"],
            "properties": {"indice": {"type": "integer"}, "coincide": {"type": "boolean"},
                           "valor_en_fuente": {"type": "string"}, "nota": {"type": "string"}}}},
        "afirmaciones_no_respaldadas": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["ubicacion", "afirmacion", "motivo", "severidad"],
            "properties": {"ubicacion": {"type": "string"}, "afirmacion": {"type": "string"},
                           "motivo": {"type": "string"}, "severidad": {"enum": ["critico", "advertencia"]}}}},
    },
}

_NUM = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)*")
_PRELUDIO_SIN_RED = (
    "import socket as _s\n"
    "def _bloq(*a, **k):\n    raise OSError('red bloqueada por el verificador')\n"
    "_s.socket = _bloq; _s.create_connection = _bloq; _s.getaddrinfo = _bloq\n"
)


# --------------------------------------------------------------------------- utilidades
def parsear_numero(x) -> float | None:
    """'38 %' -> 38.0; '1.234,5' -> 1234.5; 220 -> 220.0; sin número -> None."""
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    m = _NUM.search(str(x))
    return _a_float(m.group(0)) if m else None


def _a_float(tok: str) -> float:
    if "." in tok and "," in tok:
        return float(tok.replace(".", "").replace(",", "."))
    if "," in tok:
        return float(tok.replace(",", "."))
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", tok):
        return float(tok.replace(".", ""))
    return float(tok)


def numeros_en(texto: str) -> list[float]:
    return [_a_float(t) for t in _NUM.findall(texto)]


def _iguales(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


class _Informe:
    def __init__(self):
        self.hallazgos: list[dict] = []

    def add(self, invariante, severidad, ubicacion, descripcion, origen="codigo"):
        self.hallazgos.append({"invariante": invariante, "severidad": severidad, "ubicacion": ubicacion,
                               "descripcion": descripcion, "origen": origen})

    def criticos(self, origen=None):
        return [h for h in self.hallazgos if h["severidad"] == "critico" and (origen is None or h["origen"] == origen)]


# --------------------------------------------------------------------------- notebook
def ejecutar_notebook(ruta: Path | None, timeout_s: int) -> dict:
    """Ejecuta las celdas de código en un subproceso aislado (-I), sin red, cwd temporal y con
    tiempo límite. Devuelve {estado, ruta, salida_resumen, stdout}."""
    if ruta is None:
        return {"estado": "no_encontrado", "ruta": None, "salida_resumen": "", "stdout": ""}
    ruta = Path(ruta)
    if not ruta.exists():
        return {"estado": "no_encontrado", "ruta": str(ruta), "salida_resumen": "", "stdout": ""}
    try:
        nb = json.loads(ruta.read_text(encoding="utf-8"))
        celdas = ["".join(c["source"]) if isinstance(c["source"], list) else c["source"]
                  for c in nb["cells"] if c.get("cell_type") == "code"]
    except (ValueError, KeyError, TypeError) as e:
        return {"estado": "error", "ruta": str(ruta), "salida_resumen": f"notebook ilegible: {e}", "stdout": ""}
    codigo = "\n".join(
        "\n".join(ln for ln in c.splitlines() if not ln.lstrip().startswith(("%", "!"))) for c in celdas)
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "nb.py"
        script.write_text(_PRELUDIO_SIN_RED + codigo, encoding="utf-8")
        try:
            p = subprocess.run([sys.executable, "-I", str(script)], cwd=tmp, capture_output=True, text=True,
                               timeout=timeout_s, encoding="utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            return {"estado": "tiempo_agotado", "ruta": str(ruta), "salida_resumen": f"> {timeout_s} s", "stdout": ""}
    if p.returncode != 0:
        return {"estado": "error", "ruta": str(ruta), "salida_resumen": p.stderr[-500:], "stdout": p.stdout}
    return {"estado": "ejecutado", "ruta": str(ruta), "salida_resumen": p.stdout[:1500], "stdout": p.stdout}


# --------------------------------------------------------------------------- comprobaciones de código
def _esquemas(inf, tarea, guia, trazas, noticia):
    for nombre, art in (("tarea", tarea), ("guia", guia), ("trazas_resumen", trazas), ("noticia", noticia)):
        if art is None:
            continue
        for e in inv.validar_contra_esquema(art, nombre).errores:
            inf.add("1", "critico", nombre, e)


def _coherencia(inf, tarea, guia, trazas, noticia):
    tid = tarea.get("id")
    if guia.get("tarea_id") != tid:
        inf.add("coherencia", "critico", "guia.tarea_id", f"guía de {guia.get('tarea_id')!r}, tarea {tid!r}")
    if trazas.get("tarea_id") != tid:
        inf.add("coherencia", "critico", "trazas.tarea_id", f"trazas de {trazas.get('tarea_id')!r}, tarea {tid!r}")
    ficha, nt = guia.get("ficha", {}), tarea.get("noticia", {})
    if ficha.get("noticia", {}).get("url") != nt.get("url"):
        inf.add("coherencia", "critico", "guia.ficha.noticia.url", "la URL de la guía no es la de la tarea")
    if guia.get("trazabilidad", {}).get("noticia_url") != nt.get("url"):
        inf.add("coherencia", "critico", "guia.trazabilidad.noticia_url", "no coincide con la URL de la tarea")
    for campo, a, b in (("nivel_principal", ficha.get("nivel_principal"), tarea.get("nivel_principal")),
                        ("titulo", ficha.get("titulo"), tarea.get("titulo"))):
        if a != b:
            inf.add("coherencia", "advertencia", f"guia.ficha.{campo}", f"{a!r} ≠ {b!r} de la tarea")
    rub = tarea.get("rubrica_rub01")
    if rub and ficha.get("puntaje_rub01") != rub.get("total"):
        inf.add("coherencia", "critico", "guia.ficha.puntaje_rub01",
                f"{ficha.get('puntaje_rub01')} ≠ RUB01 de la tarea {rub.get('total')}")
    sim = guia.get("trazabilidad", {}).get("simulacion") or {}
    if sim.get("diseno") != trazas.get("diseno") or sim.get("n_grupos") != trazas.get("corridas"):
        inf.add("coherencia", "critico", "guia.trazabilidad.simulacion",
                f"guía ({sim.get('diseno')}, {sim.get('n_grupos')}) ≠ trazas ({trazas.get('diseno')}, {trazas.get('corridas')})")
    pct = (trazas.get("agregado") or {}).get("pct_bloqueo_por_transicion", {})
    tabla = guia.get("tabla_bloqueos", {})
    for t in sorted(set(pct) | set(tabla)):
        if t not in pct or t not in tabla or abs(pct[t] - tabla[t]) > 0.01:
            inf.add("coherencia", "critico", f"guia.tabla_bloqueos.{t}",
                    f"guía {tabla.get(t)} ≠ trazas {pct.get(t)}")
    if noticia is not None and noticia.get("id") != nt.get("noticia_id"):
        inf.add("coherencia", "critico", "noticia.id",
                f"{noticia.get('id')!r} ≠ tarea.noticia.noticia_id {nt.get('noticia_id')!r}")
    corridas = {c["id"]: c for c in trazas.get("por_corrida", [])}
    for esc in guia.get("escenarios", []):
        citadas = [corridas[i] for i in esc.get("corridas", []) if i in corridas]
        if not citadas:
            continue
        trans = {b["transicion"] for c in citadas for b in c.get("bloqueos", [])}
        for b in esc.get("bloqueos", []):
            if b.get("transicion") not in trans:
                inf.add("coherencia", "critico", f"guia.escenarios.{esc.get('id')}.bloqueos",
                        f"{b.get('transicion')} no ocurre en las corridas citadas {esc.get('corridas')}")
        if esc.get("modelo") not in {c.get("modelo") for c in citadas}:
            inf.add("coherencia", "advertencia", f"guia.escenarios.{esc.get('id')}.modelo",
                    f"modelo {esc.get('modelo')!r} distinto de los de las corridas citadas")
        if not any(esc.get("ruta") == c.get("ruta") for c in citadas):
            inf.add("coherencia", "advertencia", f"guia.escenarios.{esc.get('id')}.ruta",
                    "la ruta no es idéntica a la de ninguna corrida citada")


def _invariante5(inf, guia, trazas):
    for e in inv.consistencia_trazas(trazas).errores + inv.escenarios_respaldados(guia, trazas).errores:
        inf.add("5", "critico", "guia.escenarios", e)


def _invariante3(inf, tarea, guia, noticia, texto_noticia):
    if not texto_noticia:
        return
    for nombre, art in (("tarea", tarea), ("guia", guia), ("noticia", noticia)):
        if art is None:
            continue
        for e in inv.cumple_limite_literal(art, texto_noticia).errores:
            inf.add("3", "critico", nombre, e)


def _cifras(inf, tarea, noticia, nb) -> list[dict]:
    """Invariante 4 en código: localizador presente, existente y con el mismo valor."""
    out = []
    por_ubic = {}
    if noticia is not None:
        por_ubic = {(c.get("localizador") or {}).get("ubicacion"): c for c in noticia.get("cifras", [])}
    nums_nb = numeros_en(nb["stdout"]) if nb["estado"] == "ejecutado" else []
    cifras = tarea.get("noticia", {}).get("cifras_usadas", [])
    for i, c in enumerate(cifras):
        loc = c.get("localizador")
        base = {"indice": i, "que_es": c.get("que_es", ""), "valor_tarea": c.get("valor", ""),
                "localizador": loc if loc and loc.get("fuente") and loc.get("ubicacion") else None,
                "metodo": "codigo", "valor_fuente": None}
        ub = f"tarea.noticia.cifras_usadas[{i}]"
        if base["localizador"] is None:
            inf.add("4", "critico", ub, f"cifra {c.get('valor')!r} ({c.get('que_es')}) sin localizador")
            out.append({**base, "resultado": "sin_localizador", "nota": "falta localizador"})
            continue
        v = parsear_numero(c.get("valor"))
        if loc["fuente"] == "noticia":
            if noticia is None:
                inf.add("4", "advertencia", ub,
                        "no se entregó la noticia: no se puede contrastar el localizador en código")
                out.append({**base, "resultado": "no_verificable", "nota": "noticia no entregada"})
                continue
            f = por_ubic.get(loc["ubicacion"])
            if f is None:
                inf.add("4", "critico", ub, f"el localizador «{loc['ubicacion']}» no existe en la noticia")
                out.append({**base, "resultado": "localizador_inexistente",
                            "nota": "ubicación ausente en noticia.cifras"})
                continue
            vf = parsear_numero(f.get("valor"))
            base["valor_fuente"] = f.get("valor")
            if v is None or vf is None or not _iguales(v, vf):
                inf.add("4", "critico", ub,
                        f"valor {c.get('valor')!r} en la tarea, {f.get('valor')!r} en la noticia ({loc['ubicacion']})")
                out.append({**base, "resultado": "distinto", "nota": "valor distinto del de la noticia"})
            else:
                out.append({**base, "resultado": "coincide", "nota": "valor igual al de la noticia"})
        else:  # notebook
            if nb["estado"] != "ejecutado":
                inf.add("4", "critico", ub, f"localizador en notebook, pero el notebook está «{nb['estado']}»")
                out.append({**base, "resultado": "localizador_inexistente", "nota": f"notebook {nb['estado']}"})
            elif v is not None and any(_iguales(v, n) for n in nums_nb):
                out.append({**base, "resultado": "coincide", "nota": "el valor aparece en la salida del notebook"})
            else:
                inf.add("4", "critico", ub, f"valor {c.get('valor')!r} no aparece en la salida del notebook")
                out.append({**base, "resultado": "distinto", "nota": "valor ausente en la salida del notebook"})
    # cifras en el texto que ve el estudiante sin entrada en cifras_usadas
    permitidas = [p for p in (parsear_numero(c.get("valor")) for c in cifras) if p is not None]
    est = tarea.get("estudiante", {})
    textos = [("estudiante.enunciado_es", est.get("enunciado_es", ""))]
    textos += [(f"estudiante.recursos_a_solicitud[{r.get('id')}]", r.get("contenido", ""))
               for r in est.get("recursos_a_solicitud", [])]
    for ub, t in textos:
        for n in numeros_en(t):
            if not any(_iguales(n, p) for p in permitidas):
                inf.add("4", "critico", ub, f"cifra {n:g} sin localizador (no figura en noticia.cifras_usadas)")
    return out


# --------------------------------------------------------------------------- modelo
def _contraste_semantico(inf, tarea, guia, trazas, noticia, nb, cifras, cliente):
    n = noticia or {}
    ficha = tarea.get("noticia") or {}
    # El título forma parte de la cita (medio, título, fecha, URL): sin él, afirmaciones que solo están en el
    # titular se marcaban como no respaldadas (caso 2026-10-anticipo-renta-vitalicia, ver decisiones.md).
    fuentes = {
        "noticia": {"medio": n.get("medio") or ficha.get("medio"), "titulo": n.get("titulo") or ficha.get("titulo"),
                    "fecha": n.get("fecha") or ficha.get("fecha"),
                    "resumen_propio": n.get("resumen_propio") or ficha.get("resumen_propio"),
                    "cifras": n.get("cifras") or tarea["noticia"].get("cifras_usadas")},
        "notebook": {"estado": nb["estado"], "salida": nb["stdout"][:4000]},
    }
    cif = [{"indice": c["indice"], "que_es": c["que_es"], "valor": c["valor_tarea"], "localizador": c["localizador"]}
           for c in cifras]
    afirmaciones = {"tarea": {"estudiante": tarea.get("estudiante"), "task_space": tarea.get("task_space")},
                    "guia": {k: guia.get(k) for k in ("analisis_a_priori", "escenarios", "tabla_bloqueos",
                                                      "intervenciones", "puesta_en_comun")}}
    user = json.dumps({"cifras": cif, "fuentes": fuentes, "afirmaciones": afirmaciones, "trazas": trazas},
                      ensure_ascii=False)
    r = llamar(agente="verificador", system=PROMPT, user=user, schema=ESQUEMA_MODELO,
               max_tokens=CONFIG["max_tokens"], esfuerzo=CONFIG["esfuerzo"], cliente=cliente)
    sal = r["salida"]
    por_indice = {c["indice"]: c for c in cifras}
    for m in sal["cifras"]:
        c = por_indice.get(m["indice"])
        if c is None:
            continue
        c["metodo"] = "codigo+modelo"
        c["nota"] = f"{c['nota']}; modelo: {m['nota']}"
        if c["valor_fuente"] is None and m["valor_en_fuente"]:
            c["valor_fuente"] = m["valor_en_fuente"]
        if not m["coincide"]:
            if c["resultado"] == "coincide":
                c["resultado"] = "distinto"
            inf.add("semantica", "critico", f"tarea.noticia.cifras_usadas[{m['indice']}]",
                    f"el modelo no encuentra respaldo para la cifra: {m['nota']}", "modelo")
    for a in sal["afirmaciones_no_respaldadas"]:
        inf.add("semantica", a["severidad"], a["ubicacion"], f"{a['afirmacion']} — {a['motivo']}", "modelo")
    return r["meta"]


# --------------------------------------------------------------------------- API
def verificar(tarea: dict, guia: dict, trazas: dict, noticia: dict | None = None,
              texto_noticia: str | None = None, notebook_ruta: str | Path | None = None,
              cliente=None) -> dict:
    """Devuelve el informe (valida contra salida.schema.json). `texto_noticia` solo en memoria."""
    inf = _Informe()
    _esquemas(inf, tarea, guia, trazas, noticia)
    nb = {"estado": "no_declarado", "ruta": None, "salida_resumen": "", "stdout": ""}
    declarado = (guia.get("materiales") or {}).get("notebook")
    cifras: list[dict] = []
    try:
        if notebook_ruta is not None:
            nb = ejecutar_notebook(Path(notebook_ruta), CONFIG["notebook"]["timeout_s"])
        elif declarado:
            nb = {"estado": "no_encontrado", "ruta": declarado, "salida_resumen": "", "stdout": ""}
        if nb["estado"] == "no_declarado":
            inf.add("notebook", "advertencia", "guia.materiales.notebook", "no hay notebook de escenarios declarado")
        elif nb["estado"] != "ejecutado":
            inf.add("notebook", "advertencia", "guia.materiales.notebook",
                    f"notebook {nb['ruta']} {nb['estado'].replace('_', ' ')}: {nb['salida_resumen'][:200]}")
        _coherencia(inf, tarea, guia, trazas, noticia)
        _invariante5(inf, guia, trazas)
        _invariante3(inf, tarea, guia, noticia, texto_noticia)
        cifras = _cifras(inf, tarea, noticia, nb)
    except (KeyError, TypeError, AttributeError) as e:
        inf.add("1", "critico", "(estructura)", f"artefacto con estructura inesperada ({type(e).__name__}: {e})")
    meta_llm, llamado = None, False
    if not inf.criticos("codigo"):
        meta_llm = _contraste_semantico(inf, tarea, guia, trazas, noticia, nb, cifras, cliente)
        llamado = True
    aprobado = not inf.criticos()
    meta = {"agente": "verificador", "version_prompt": CONFIG["version_prompt"],
            "modelo": meta_llm["modelo"] if meta_llm else None,
            "request_id": meta_llm["request_id"] if meta_llm else None,
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "costo_usd": meta_llm["costo_usd"] if meta_llm else 0.0,
            "modelo_llamado": llamado, "texto_noticia_recibido": bool(texto_noticia),
            "uso": meta_llm["uso"] if meta_llm else None}
    informe = {"tarea_id": tarea.get("id", ""), "aprobado": aprobado,
               "estado_destino": CONFIG["estado_si_aprueba"] if aprobado else CONFIG["estado_si_rechaza"],
               "hallazgos": inf.hallazgos, "cifras_contrastadas": cifras,
               "notebook": {k: nb[k] for k in ("estado", "ruta", "salida_resumen")}, "meta": meta}
    errores = list(Draft202012Validator(ESQUEMA_SALIDA).iter_errors(informe))
    if errores:
        raise ValueError("informe no valida contra salida.schema.json: " + "; ".join(e.message for e in errores[:3]))
    return informe


def aplicar_mutaciones(base: dict, mutaciones: list[dict]) -> dict:
    """Utilidad para los casos de evals: {'ruta': 'guia/escenarios/1/corridas', 'valor': ...}."""
    base = copy.deepcopy(base)
    for m in mutaciones:
        partes = m["ruta"].split("/")
        obj = base
        for p in partes[:-1]:
            obj = obj[int(p)] if isinstance(obj, list) else obj[p]
        k = partes[-1]
        k = int(k) if isinstance(obj, list) else k
        if m.get("eliminar"):
            del obj[k]
        else:
            obj[k] = m["valor"]
    return base


def _leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8")) if ruta else None


def main(argv=None) -> int:
    ej = RAIZ / "contratos" / "ejemplos"
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tarea", default=ej / "tarea_ejemplo.json")
    ap.add_argument("--guia", default=ej / "guia_ejemplo.json")
    ap.add_argument("--trazas", default=ej / "trazas_resumen_ejemplo.json")
    ap.add_argument("--noticia", default=ej / "noticia_ejemplo.json")
    ap.add_argument("--texto-noticia", default=None)
    ap.add_argument("--notebook", default=None)
    ap.add_argument("--salida", default=None)
    a = ap.parse_args(argv)
    texto = Path(a.texto_noticia).read_text(encoding="utf-8") if a.texto_noticia else None
    informe = verificar(_leer(a.tarea), _leer(a.guia), _leer(a.trazas), _leer(a.noticia), texto, a.notebook)
    s = json.dumps(informe, ensure_ascii=False, indent=2)
    if a.salida:
        Path(a.salida).write_text(s, encoding="utf-8")
    else:
        sys.stdout.buffer.write((s + "\n").encode("utf-8"))
    return 0 if informe["aprobado"] else 2


if __name__ == "__main__":
    sys.exit(main())
