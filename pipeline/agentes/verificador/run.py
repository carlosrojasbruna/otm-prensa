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

`texto_noticia` solo se lee en memoria: para la invariante 3 y para extraer los párrafos que citan los
recursos y las cifras (v1.1). Al modelo solo llegan esos párrafos; el texto completo nunca se envía,
se guarda ni se cita (> 25 palabras) en el informe.
"""
from __future__ import annotations

import argparse
import copy
import html
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
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
    "required": ["cifras", "afirmaciones_no_respaldadas", "recursos"],
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
        "recursos": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "juicio", "nota"],
            "properties": {"id": {"type": "string"},
                           "juicio": {"enum": ["respaldado", "no_respaldado", "contradicho",
                                               "plausible", "no_plausible", "no_verificable"]},
                           "nota": {"type": "string"}}}},
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
    out = []
    for t in _NUM.findall(texto):
        try:
            out.append(_a_float(t))
        except ValueError:   # «0.5.8» (versiones, fechas con puntos): no es una cifra
            continue
    return out


def _iguales(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


MAX_PALABRAS_CITA = 25  # invariante 3
_CITA = re.compile(r"«([^»]*)»")


def _recortar(texto: str, max_palabras: int = MAX_PALABRAS_CITA, corte: int = 20) -> str:
    """Si `texto` supera `max_palabras`, lo abrevia a `corte` palabras + « …» (como la cita de títulos)."""
    pal = texto.split()
    return texto if len(pal) <= max_palabras else " ".join(pal[:corte]) + " …"


def _recortar_citas(desc: str) -> str:
    """Recorta cada tramo entre « » a ≤ 25 palabras: un hallazgo nunca reproduce la noticia."""
    return _CITA.sub(lambda m: "«" + _recortar(m.group(1)) + "»", desc)


def _sin_literal(texto: str, texto_noticia: str | None) -> str:
    """Texto del modelo apto para el informe: nunca > 25 palabras consecutivas de la noticia."""
    texto = _recortar_citas(texto)
    if texto_noticia and inv.max_palabras_consecutivas_comunes(texto, texto_noticia)[0] > MAX_PALABRAS_CITA:
        return " ".join(texto.split()[:20]) + " …"
    return texto


class _Informe:
    def __init__(self):
        self.hallazgos: list[dict] = []

    def add(self, invariante, severidad, ubicacion, descripcion, origen="codigo"):
        descripcion = _recortar_citas(descripcion)
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


TOLERANCIA_PARRAFOS = 1   # un localizador corrido en ±1 párrafo se corrige como advertencia (ciclo 2026-10-26)


def _en_parrafo(valor: float, parrafo: str) -> bool:
    """`valor` aparece en el párrafo, también escrito en unidades («4 mil» = 4.000, «5 millones» = 5.000.000)."""
    return any(_iguales(valor * f, x) for x in numeros_en(parrafo) for f in (1, 1e3, 1e6, 1e9))


def parrafos_alineados(texto: str, cifras: list[dict]) -> tuple[list[str], int]:
    """Párrafos del texto numerados como los numeró el explorador. El explorador numera el cuerpo que leyó (en
    La Tercera, el del feed RSS); el ciclo relee la página completa, con menús y avisos antes del cuerpo, y la
    numeración se corre (2026-10-cuanto-pagar-cada-mes: «párrafo 5» del feed = párrafo 151 de la página). Se
    estima el desfase k con las cifras de la noticia (el k que más cifras pone en su párrafo; 0 en empate o con
    menos de 2 votos) y se devuelve la lista desplazada para que el índice visible siga partiendo en 1."""
    ps = parrafos_de(texto)
    votos: dict[int, int] = {}
    for c in cifras:
        ns = _numeros_parrafo(_norm(str((c.get("localizador") or {}).get("ubicacion", ""))))
        v = parsear_numero(c.get("valor"))
        if len(ns) != 1 or v is None:
            continue
        for k in {i - ns[0] for i, p in enumerate(ps, start=1) if _en_parrafo(v, p)}:
            votos[k] = votos.get(k, 0) + 1
    k = max(votos, key=lambda d: (votos[d], -abs(d)), default=0)
    if votos.get(k, 0) < 2 or votos[k] <= votos.get(0, 0):
        k = 0
    return (ps[k:] if k >= 0 else [""] * (-k) + ps), k


def _parrafos(texto_noticia: str | None, tarea: dict, noticia: dict | None) -> list[str] | None:
    if not texto_noticia:
        return None
    cifras = (noticia or {}).get("cifras") or tarea.get("noticia", {}).get("cifras_usadas", [])
    return parrafos_alineados(texto_noticia, cifras)[0]


def buscar_cifra(valor: float, parrafos: list[str], citados: list[int]) -> tuple[str, int | None]:
    """Busca `valor` en toda la nota. Devuelve ("citado", n) si está en un párrafo citado, ("vecino", n) si está a
    ±TOLERANCIA_PARRAFOS de uno citado, ("lejos", n) si está en otro párrafo y ("ausente", None) si no aparece."""
    donde = [i for i, p in enumerate(parrafos, start=1) if _en_parrafo(valor, p)]
    for n in citados:
        if n in donde:
            return "citado", n
    for d in range(1, TOLERANCIA_PARRAFOS + 1):
        for n in citados:
            for m in (n - d, n + d):
                if m in donde:
                    return "vecino", m
    return ("lejos", donde[0]) if donde else ("ausente", None)


def _cifras(inf, tarea, noticia, nb, parrafos: list[str] | None = None) -> list[dict]:
    """Invariante 4 en código: localizador presente, existente y con el mismo valor.

    Con el texto de la noticia, además se busca la cifra en toda la nota: si está a ±1 párrafo del citado, el
    localizador se corrige como advertencia (`localizador_corregido`); si está más lejos o no está, es crítico."""
    out = []
    por_ubic: dict = {}
    if noticia is not None:
        # varias cifras pueden compartir párrafo: antes se guardaba solo la última y «48 cuotas (párrafo 5)» se
        # comparaba con «5 millones (párrafo 5)» (2026-10-cuanto-pagar-cada-mes)
        for c in noticia.get("cifras", []):
            por_ubic.setdefault((c.get("localizador") or {}).get("ubicacion"), []).append(c)
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
            candidatas = por_ubic.get(loc["ubicacion"], [])
            f = next((x for x in candidatas if v is not None and parsear_numero(x.get("valor")) is not None
                      and _iguales(v, parsear_numero(x.get("valor")))), None)
            citados = _numeros_parrafo(_norm(str(loc["ubicacion"])))
            if parrafos is not None and v is not None and citados:
                donde, n = buscar_cifra(v, parrafos, citados)
                if donde == "citado":
                    base["valor_fuente"] = c.get("valor")
                    out.append({**base, "resultado": "coincide", "nota": f"valor presente en el párrafo {n} de la noticia"})
                    continue
                if donde == "vecino":
                    corregido = {"fuente": "noticia", "ubicacion": f"párrafo {n}"}
                    inf.add("4", "advertencia", ub,
                            f"localizador corrido: {c.get('valor')!r} no está en «{loc['ubicacion']}» sino en el "
                            f"párrafo {n}; se corrige el localizador")
                    base["valor_fuente"] = c.get("valor")
                    out.append({**base, "resultado": "coincide", "localizador_corregido": corregido,
                                "nota": f"valor presente en el párrafo {n} (localizador corregido desde «{loc['ubicacion']}»)"})
                    continue
                if donde == "lejos":
                    inf.add("4", "critico", ub,
                            f"localizador erróneo: {c.get('valor')!r} no está en «{loc['ubicacion']}» (ni a ±"
                            f"{TOLERANCIA_PARRAFOS} párrafo) sino en el párrafo {n}")
                    out.append({**base, "resultado": "distinto",
                                "nota": f"valor en el párrafo {n}, lejos del localizador"})
                    continue
                if f is not None:   # ausente del texto (p. ej. escrito con palabras) pero registrado por el explorador
                    inf.add("4", "advertencia", ub,
                            f"{c.get('valor')!r} no se encontró como número en el texto; se acepta por noticia.cifras")
                    base["valor_fuente"] = f.get("valor")
                    out.append({**base, "resultado": "coincide", "nota": "no hallado en el texto; igual a noticia.cifras"})
                    continue
                inf.add("4", "critico", ub, f"{c.get('valor')!r} no aparece en ningún párrafo de la noticia")
                out.append({**base, "resultado": "distinto", "nota": "valor ausente del texto de la noticia"})
                continue
            if not candidatas:
                inf.add("4", "critico", ub, f"el localizador «{loc['ubicacion']}» no existe en la noticia")
                out.append({**base, "resultado": "localizador_inexistente",
                            "nota": "ubicación ausente en noticia.cifras"})
                continue
            if f is None:
                otras = ", ".join(repr(x.get("valor")) for x in candidatas)
                base["valor_fuente"] = candidatas[0].get("valor")
                inf.add("4", "critico", ub,
                        f"valor {c.get('valor')!r} en la tarea; en la noticia ({loc['ubicacion']}): {otras}")
                out.append({**base, "resultado": "distinto", "nota": "valor distinto del de la noticia"})
            else:
                base["valor_fuente"] = f.get("valor")
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


# --------------------------------------------------------------------------- recursos (v1.1)
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


_MARCA_SUPUESTO = "supuesto del escenario"
_RE_PARRAFOS = re.compile(r"parrafos?\s+(\d+(?:\s*(?:-|–|a|y|,|e)\s*\d+)*)")
_RE_LOC_NOTICIA = re.compile(r"\b(titular|titulo|grafico|tabla|figura|imagen|recuadro|infografia|cifra)\b")
_RE_GENERICA = re.compile(
    r"conocimiento (general|comun)|sentido comun|\binternet\b|\bweb\b|fuentes? (publicas?|oficiales|diversas?|varias)"
    r"|datos (oficiales|publicos|de mercado)|elaboracion propia|estimacion|experiencia|estudios|expertos|literatura"
    r"|diversas|varias|generica|no especificada|\bn/?a\b")
_RE_ACRONIMO = re.compile(r"\b[A-ZÁÉÍÓÚÑ]{2,}\b")


def _numeros_parrafo(texto_norm: str) -> list[int]:
    """'párrafo 3' -> [3]; 'párrafos 2-4' -> [2,3,4]; 'párrafos 2 y 5' -> [2,5]."""
    out: list[int] = []
    for m in _RE_PARRAFOS.finditer(texto_norm):
        trozo = m.group(1)
        if re.search(r"\d\s*(?:-|–|a)\s*\d", trozo) and not re.search(r"[,y]|\be\b", trozo):
            a, b = (int(x) for x in re.findall(r"\d+", trozo)[:2])
            out += list(range(a, b + 1)) if 0 < b - a <= 20 else [a, b]
        else:
            out += [int(x) for x in re.findall(r"\d+", trozo)]
    return sorted(set(out))


def _otra_fuente_concreta(fuente: str) -> bool:
    """'otra fuente: <X>' es concreta si X nombra un organismo o publicación: un nombre propio (palabra con
    mayúscula inicial que no abre la frase, o sigla de ≥ 2 letras) o una URL/año. Si X es solo una
    descripción genérica ('datos oficiales', 'conocimiento general') no lo es."""
    texto = fuente.split(":", 1)[1].strip() if ":" in fuente else ""
    if len(texto.split()) < 1 or not texto:
        return False
    toks = re.findall(r"[\wÁÉÍÓÚÑáéíóúñ./-]+", texto)
    propio = bool(_RE_ACRONIMO.search(texto)) or any(t[:1].isupper() for t in toks[1:]) \
        or bool(re.search(r"https?://|www\.|\.(cl|org|gov|com|int)\b|\b(19|20)\d\d\b", texto))
    if not propio:
        return False
    return not (_RE_GENERICA.search(_norm(texto)) and len(toks) <= 2)


def clasificar_fuente(fuente: str, contenido: str = "") -> dict:
    """Clasifica el campo `fuente` de un recurso (determinista). Reglas, en este orden:
    1. «supuesto del escenario» en `fuente` o `contenido` que empieza con «Supuesto del escenario» -> supuesto.
    2. empieza con «otra fuente» -> otra_fuente si nombra un organismo/publicación concreta; si no, generica.
    3. empieza con «noticia» (o «la noticia») -> noticia; con `parrafos` si cita «párrafo N», o con otro
       localizador (titular, gráfico, tabla...). «noticia» a secas es generica.
    4. cualquier otra cosa -> generica."""
    s = _norm(fuente).strip()
    marca_f = _MARCA_SUPUESTO in s
    marca_c = _norm(contenido).lstrip().startswith(_MARCA_SUPUESTO)
    if marca_f or marca_c:
        return {"clase": "supuesto", "parrafos": [], "marca_completa": marca_f and marca_c}
    if re.match(r"otra fuente\b", s):
        return {"clase": "otra_fuente" if _otra_fuente_concreta(fuente) else "generica", "parrafos": []}
    if re.match(r"(la )?noticia\b", s):
        parrafos = _numeros_parrafo(s)
        if parrafos or _RE_LOC_NOTICIA.search(s):
            return {"clase": "noticia", "parrafos": parrafos}
    return {"clase": "generica", "parrafos": []}


def parrafos_de(texto: str) -> list[str]:
    """Párrafos no vacíos del texto (HTML <p> o texto con saltos de línea); el índice visible parte en 1.
    Misma convención que el explorador (`parrafos_de`), que es la que numera los localizadores."""
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", texto)
    t = re.sub(r"(?i)</p>|<br\s*/?>|</li>|</h[1-6]>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    partes = [re.sub(r"\s+", " ", p).strip() for p in t.split("\n")]
    return [p for p in partes if len(p) > 3]


def _recursos(inf, tarea, texto_noticia, parrafos: list[str] | None = None):
    """Clasifica la fuente de cada recurso y levanta los hallazgos deterministas. Devuelve
    (recursos a contrastar con el modelo, {n: párrafo citado}). Los párrafos salen del texto en memoria
    y son únicamente los citados por los recursos y por `cifras_usadas`."""
    lista = [(f"tarea.estudiante.recursos_a_solicitud[{r.get('id')}]", r)
             for r in (tarea.get("estudiante") or {}).get("recursos_a_solicitud", [])]
    lista += [(f"tarea.recursos_de_entrada[{r.get('id')}]", r)
              for r in tarea.get("recursos_de_entrada", [])]
    a_modelo, pedidos = [], set()
    for ub, r in lista:
        cl = clasificar_fuente(r.get("fuente", ""), r.get("contenido", ""))
        clase = cl["clase"]
        if clase == "generica":
            inf.add("semantica", "critico", ub,
                    f"fuente genérica o sin localizador ({r.get('fuente')!r}): toda afirmación factual de un recurso "
                    "debe venir de la noticia con «párrafo N», de «otra fuente: <organismo/publicación>» o estar "
                    "marcada como «supuesto del escenario»")
            continue
        if clase == "supuesto":
            if not cl["marca_completa"]:
                inf.add("semantica", "advertencia", ub,
                        "supuesto marcado solo en `fuente` o solo en `contenido`: márcalo en ambos")
            continue
        if clase == "noticia":
            pedidos.update(cl["parrafos"])
        a_modelo.append({"ubicacion": ub, "id": r.get("id"), "que_es": r.get("que_es"),
                         "contenido": r.get("contenido"), "fuente": r.get("fuente"),
                         "clase": clase, "parrafos": cl["parrafos"]})
    for c in tarea.get("noticia", {}).get("cifras_usadas", []):
        loc = c.get("localizador") or {}
        if loc.get("fuente") == "noticia":
            pedidos.update(_numeros_parrafo(_norm(str(loc.get("ubicacion", "")))))
    citados: dict[str, str] = {}
    if texto_noticia:
        todos = parrafos if parrafos is not None else parrafos_de(texto_noticia)
        for n in sorted(pedidos):
            if 1 <= n <= len(todos):
                citados[str(n)] = todos[n - 1]
            else:
                inf.add("semantica", "advertencia", "tarea.recursos",
                        f"el párrafo {n} no existe en el texto de la noticia ({len(todos)} párrafos)")
    else:
        for r in a_modelo:
            if r["clase"] == "noticia":
                inf.add("semantica", "advertencia", r["ubicacion"],
                        "no se pudo contrastar con el texto: el ciclo no entregó `texto_noticia`; la afirmación "
                        "del recurso solo se juzgó contra título, resumen y cifras")
    return a_modelo, citados


# --------------------------------------------------------------------------- modelo
def _contraste_semantico(inf, tarea, guia, trazas, noticia, nb, cifras, cliente,
                         recursos=None, parrafos_citados=None, texto_noticia=None):
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
    if parrafos_citados:  # solo los párrafos citados por localizadores; nunca el texto completo
        fuentes["noticia"]["parrafos_citados"] = parrafos_citados
    cif = [{"indice": c["indice"], "que_es": c["que_es"], "valor": c["valor_tarea"], "localizador": c["localizador"]}
           for c in cifras]
    afirmaciones = {"tarea": {"estudiante": tarea.get("estudiante"), "task_space": tarea.get("task_space")},
                    "guia": {k: guia.get(k) for k in ("analisis_a_priori", "escenarios", "tabla_bloqueos",
                                                      "intervenciones", "puesta_en_comun")}}
    user = json.dumps({"cifras": cif, "fuentes": fuentes, "afirmaciones": afirmaciones, "trazas": trazas,
                       "recursos_a_contrastar": recursos or []}, ensure_ascii=False)
    r = llamar(agente="verificador", system=PROMPT, user=user, schema=ESQUEMA_MODELO,
               max_tokens=CONFIG["max_tokens"], esfuerzo=CONFIG["esfuerzo"], cliente=cliente)
    sal = r["salida"]
    por_indice = {c["indice"]: c for c in cifras}
    for m in sal["cifras"]:
        c = por_indice.get(m["indice"])
        if c is None:
            continue
        c["metodo"] = "codigo+modelo"
        c["nota"] = f"{c['nota']}; modelo: {_sin_literal(m['nota'], texto_noticia)}"
        if c["valor_fuente"] is None and m["valor_en_fuente"]:
            c["valor_fuente"] = _sin_literal(m["valor_en_fuente"], texto_noticia)
        if not m["coincide"]:
            if c["resultado"] == "coincide":
                c["resultado"] = "distinto"
            inf.add("semantica", "critico", f"tarea.noticia.cifras_usadas[{m['indice']}]",
                    f"el modelo no encuentra respaldo para la cifra: {_sin_literal(m['nota'], texto_noticia)}", "modelo")
    for a in sal["afirmaciones_no_respaldadas"]:
        inf.add("semantica", a["severidad"], a["ubicacion"],
                _sin_literal(f"{a['afirmacion']} — {a['motivo']}", texto_noticia), "modelo")
    ubic = {x["id"]: x for x in recursos or []}
    for j in sal.get("recursos", []):
        rec = ubic.get(j["id"])
        if rec is None or j["juicio"] == "respaldado" or j["juicio"] == "plausible":
            continue
        nota = _sin_literal(j["nota"], texto_noticia)
        if rec["clase"] == "noticia":
            if j["juicio"] == "contradicho":
                inf.add("semantica", "critico", rec["ubicacion"],
                        f"el recurso contradice los párrafos citados de la noticia: {nota}", "modelo")
            else:  # no_respaldado / no_verificable: los párrafos citados no lo dicen (localizador dudoso)
                inf.add("semantica", "advertencia", rec["ubicacion"],
                        f"afirmación no respaldada por los párrafos citados ({rec['fuente']}): {nota}", "modelo")
        else:  # otra fuente concreta: solo advertencia si el modelo no la ve plausible/verificable
            inf.add("semantica", "advertencia", rec["ubicacion"],
                    f"la otra fuente citada ({rec['fuente']}) no parece plausible o verificable: {nota}", "modelo")
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
    recursos_modelo, parrafos_citados = [], {}
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
        parrafos = _parrafos(texto_noticia, tarea, noticia)
        cifras = _cifras(inf, tarea, noticia, nb, parrafos)
        recursos_modelo, parrafos_citados = _recursos(inf, tarea, texto_noticia, parrafos)
    except (KeyError, TypeError, AttributeError) as e:
        inf.add("1", "critico", "(estructura)", f"artefacto con estructura inesperada ({type(e).__name__}: {e})")
    meta_llm, llamado = None, False
    if not inf.criticos("codigo"):
        meta_llm = _contraste_semantico(inf, tarea, guia, trazas, noticia, nb, cifras, cliente,
                                       recursos_modelo, parrafos_citados, texto_noticia)
        llamado = True
    aprobado = not inf.criticos()
    meta = {"agente": "verificador", "version_prompt": CONFIG["version_prompt"],
            "modelo": meta_llm["modelo"] if meta_llm else None,
            "request_id": meta_llm["request_id"] if meta_llm else None,
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "costo_usd": meta_llm["costo_usd"] if meta_llm else 0.0,
            "modelo_llamado": llamado, "texto_noticia_recibido": bool(texto_noticia),
            "uso": meta_llm["uso"] if meta_llm else None}
    # Un hallazgo crítico sobre la TAREA no se arregla reescribiendo la guía: la tarea vuelve a `evaluada`.
    destino = (CONFIG["estado_si_aprueba"] if aprobado
               else CONFIG["estado_si_rechaza_tarea"] if hallazgos_sobre_tarea(inf.hallazgos)
               else CONFIG["estado_si_rechaza"])
    informe = {"tarea_id": tarea.get("id", ""), "aprobado": aprobado,
               "estado_destino": destino,
               "hallazgos": inf.hallazgos, "cifras_contrastadas": cifras,
               "notebook": {k: nb[k] for k in ("estado", "ruta", "salida_resumen")}, "meta": meta}
    errores = list(Draft202012Validator(ESQUEMA_SALIDA).iter_errors(informe))
    if errores:
        raise ValueError("informe no valida contra salida.schema.json: " + "; ".join(e.message for e in errores[:3]))
    return informe


def hallazgos_sobre_tarea(hallazgos: list[dict]) -> list[dict]:
    """Hallazgos críticos cuya ubicación está en la tarea (no en la guía, las trazas ni el notebook)."""
    return [h for h in hallazgos if h["severidad"] == "critico" and str(h["ubicacion"]).split(".")[0] == "tarea"]


def localizadores_corregidos(informe: dict) -> dict[int, dict]:
    """{índice en cifras_usadas: localizador corregido} de un informe (advertencias de ±1 párrafo)."""
    return {c["indice"]: c["localizador_corregido"] for c in informe.get("cifras_contrastadas", [])
            if c.get("localizador_corregido")}


def aplicar_localizadores(tarea: dict, correcciones: dict[int, dict], noticia: dict | None = None) -> tuple[dict, dict | None]:
    """Copias de la tarea (y de la noticia) con los localizadores corregidos. En la noticia se corrige la cifra
    con el mismo `que_es` y valor, para que una nueva versión del diseñador copie ya el localizador bueno."""
    t = json.loads(json.dumps(tarea))
    n = json.loads(json.dumps(noticia)) if noticia is not None else None
    for i, loc in correcciones.items():
        c = t["noticia"]["cifras_usadas"][int(i)]
        if n is not None:
            for x in n.get("cifras", []):
                if x.get("que_es") == c.get("que_es") and x.get("valor") == c.get("valor") \
                        and x.get("localizador") == c.get("localizador"):
                    x["localizador"] = dict(loc)
        c["localizador"] = dict(loc)
    return t, n


def verificar_tarea(tarea: dict, noticia: dict | None = None, texto_noticia: str | None = None) -> dict:
    """Verificación previa a la simulación (decisión de Carlos para CP2): solo comprobaciones de código sobre la
    tarea, sin modelo y sin guía ni trazas: contrato, invariante 3, cifras con su localizador (buscadas en toda la
    nota, ±1 párrafo) y fuentes de los recursos. Costo 0. Si hay hallazgos críticos no se gasta en simular.
    Pendiente de la misma decisión: ejecutar numéricamente el task_space (solución, rutas y rango)."""
    inf = _Informe()
    for nombre, art in (("tarea", tarea), ("noticia", noticia)):
        if art is not None:
            for e in inv.validar_contra_esquema(art, nombre).errores:
                inf.add("1", "critico", nombre, e)
    nb = {"estado": "no_declarado", "ruta": None, "salida_resumen": "", "stdout": ""}
    cifras: list[dict] = []
    try:
        if texto_noticia:
            for nombre, art in (("tarea", tarea), ("noticia", noticia)):
                if art is not None:
                    for e in inv.cumple_limite_literal(art, texto_noticia).errores:
                        inf.add("3", "critico", nombre, e)
        parrafos = _parrafos(texto_noticia, tarea, noticia)
        cifras = _cifras(inf, tarea, noticia, nb, parrafos)
        _recursos(inf, tarea, texto_noticia, parrafos)
    except (KeyError, TypeError, AttributeError) as e:
        inf.add("1", "critico", "(estructura)", f"tarea con estructura inesperada ({type(e).__name__}: {e})")
    informe = {"tarea_id": tarea.get("id", ""), "aprobado": not inf.criticos(), "alcance": "tarea",
               "hallazgos": inf.hallazgos, "cifras_contrastadas": cifras,
               "meta": {"agente": "verificador", "version_prompt": CONFIG["version_prompt"], "modelo_llamado": False,
                        "costo_usd": 0.0, "texto_noticia_recibido": bool(texto_noticia),
                        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds")}}
    informe["localizadores_corregidos"] = {str(k): v for k, v in localizadores_corregidos(informe).items()}
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
