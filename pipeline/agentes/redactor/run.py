"""Agente redactor de OTM-Prensa: tarea + trazas_resumen + transcripciones -> guía docente (PLT02).

Uso como módulo:
    from pipeline.agentes.redactor.run import redactar
    r = redactar(tarea, trazas, transcripciones, contexto)
    r["guia"]    # valida contra contratos/guia.schema.json
    r["meta"]    # modelos, versión de prompt, llamadas, costo (invariante 8)

Uso por línea de comandos (desde la raíz del repo):
    python -m pipeline.agentes.redactor.run --tarea T.json --trazas Z.json \
        --transcripciones DIR --contexto C.json --salida S.json

Diseño (ver DECISIONES.md):
- Se redacta por secciones: base (Sonnet), escenarios (Opus), intervenciones y puesta en común (Sonnet).
- Lo que es copia (ficha, rutas, tabla de bloqueos, materiales, trazabilidad) lo arma el código, no el modelo.
- Cada sección se verifica en código antes de aceptarse (esquema, invariante 5, extractos textuales,
  cifras con fuente, límite de palabras literales) y tiene una reparación; si no, falla con la causa.
- Los escenarios nunca se completan: con trazas insuficientes el agente falla (TrazasInsuficientes).
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from pipeline.invariantes import (  # noqa: E402
    DIR_CONTRATOS, consistencia_trazas, cumple_limite_literal, escenarios_respaldados,
    palabras_normalizadas, textos_de, validar_contra_esquema,
)
from pipeline.llm import llamar, modelo_de  # noqa: E402

DIR = Path(__file__).resolve().parent
CONFIG = yaml.safe_load((DIR / "config.yaml").read_text(encoding="utf-8"))
VERSION_PROMPT = CONFIG["version_prompt"]


# --------------------------------------------------------------------------- errores
class RedactorError(Exception):
    """Base. `costo_usd` es lo gastado hasta el fallo."""
    costo_usd: float = 0.0


class EntradaInvalida(RedactorError):
    pass


class TrazasInsuficientes(RedactorError):
    pass


class RedaccionRechazada(RedactorError):
    def __init__(self, seccion: str, errores: list[str], costo: float = 0.0):
        super().__init__(f"sección {seccion!r} rechazada: " + " | ".join(errores))
        self.seccion, self.errores, self.costo_usd = seccion, errores, costo


# --------------------------------------------------------------------------- prompt
def cargar_prompt() -> dict[str, str]:
    texto = (DIR / CONFIG["prompt"]).read_text(encoding="utf-8")
    partes = re.split(r"<!-- SECCION: (\w+) -->", texto)
    return {partes[i]: partes[i + 1].strip() for i in range(1, len(partes), 2)}


def system_de(seccion: str) -> str:
    p = cargar_prompt()
    return p["comun"] + "\n\n" + p[seccion]


# --------------------------------------------------------------------------- esquemas de salida
_CLAVES_ESQUEMA = ("type", "enum", "const", "properties", "required", "items", "additionalProperties")


def _puntero(doc: dict, ptr: str):
    nodo = doc
    for p in ptr.lstrip("#/").split("/") if ptr.strip("#/") else []:
        nodo = nodo[p]
    return nodo


def _simplificar(nodo, contrato: str):
    """Esquema apto para salida estructurada: resuelve $ref y deja solo palabras clave básicas
    (las cotas y patrones se comprueban después contra el contrato real)."""
    if isinstance(nodo, dict) and "$ref" in nodo:
        archivo, _, ptr = nodo["$ref"].partition("#")
        c = archivo.replace(".schema.json", "") if archivo else contrato
        doc = json.loads((DIR_CONTRATOS / f"{c}.schema.json").read_text(encoding="utf-8"))
        return _simplificar(_puntero(doc, ptr), c)
    if not isinstance(nodo, dict):
        return nodo
    sal = {}
    for k in _CLAVES_ESQUEMA:
        if k not in nodo:
            continue
        v = nodo[k]
        if k == "properties":
            sal[k] = {n: _simplificar(s, contrato) for n, s in v.items()}
        elif k == "items":
            sal[k] = _simplificar(v, contrato)
        else:
            sal[k] = v
    for k in ("oneOf", "anyOf"):
        if k in nodo:
            sal["anyOf"] = [_simplificar(s, contrato) for s in nodo[k]]
    return sal


def _guia() -> dict:
    return json.loads((DIR_CONTRATOS / "guia.schema.json").read_text(encoding="utf-8"))


def _prop(nombre: str) -> dict:
    return _simplificar(_guia()["properties"][nombre], "guia")


def esquema_base() -> dict:
    g = _guia()["properties"]
    campos = {
        "meta": _prop("meta"),
        "barreras_por_fase": _simplificar(g["analisis_a_priori"]["properties"]["barreras_por_fase"], "guia"),
        "organizacion": _prop("organizacion"),
        "uso_variantes": {"type": "string"},
        "acostumbramiento": {"type": "string"},
    }
    return {"type": "object", "additionalProperties": False, "required": list(campos), "properties": campos}


def esquema_escenarios() -> dict:
    esc = _simplificar({"$ref": "#/$defs/escenario"}, "guia")
    campos = {"estado": {"enum": ["ok", "insuficiente"]}, "motivo": {"type": "string"},
              "escenarios": {"type": "array", "items": esc}}
    return {"type": "object", "additionalProperties": False, "required": list(campos), "properties": campos}


def esquema_intervenciones() -> dict:
    campos = {"intervenciones": _prop("intervenciones"), "puesta_en_comun": _prop("puesta_en_comun")}
    return {"type": "object", "additionalProperties": False, "required": list(campos), "properties": campos}


# --------------------------------------------------------------------------- verificaciones
_NUM = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)*(?!\w)")
_NUM_LAX = re.compile(r"\d+(?:[.,]\d+)*")
_TIEMPO = re.compile(r"^\s*(min|minutos?|horas?|h|sesi[oó]n|sesiones|clases?|segundos?)\b", re.I)


def _norm_num(s: str) -> str:
    s = s.rstrip(".,")
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    s = s.replace(",", ".")
    try:
        return format(float(s), "g")
    except ValueError:
        return s


def _numeros_de(obj) -> set[str]:
    sal = set()
    def rec(o):
        if isinstance(o, bool):
            return
        if isinstance(o, (int, float)):
            sal.add(_norm_num(str(o)))
        elif isinstance(o, str):
            sal.update(_norm_num(m) for m in _NUM_LAX.findall(o))
        elif isinstance(o, dict):
            for v in o.values():
                rec(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                rec(v)
    rec(obj)
    return sal


def numeros_permitidos(tarea: dict, trazas: dict, transcripciones: dict[str, str]) -> set[str]:
    """Cifras con fuente: las de la tarea (cifras_usadas con localizador, recursos con fuente,
    task_space), las de las trazas (también los porcentajes como 0-100 y como conteo de grupos) y
    las de las transcripciones."""
    ok = _numeros_de(tarea) | _numeros_de(trazas) | _numeros_de(list(transcripciones.values()))
    n = trazas.get("corridas", 0)
    pcts = list(trazas.get("agregado", {}).get("pct_bloqueo_por_transicion", {}).values())
    pcts.append(trazas.get("agregado", {}).get("pct_validan", 0))
    for p in pcts:
        ok.add(_norm_num(str(round(p * 100, 2))))
        ok.add(_norm_num(str(round(p * n))))
    return ok


def cifras_sin_localizador(obj, permitidos: set[str], exentos_tiempo: bool = True) -> list[str]:
    """Invariante 4 en la guía: cada número del texto redactado debe estar en una fuente permitida.
    Se ignoran números dentro de identificadores (P4, B12, N4_VV_r1) y duraciones de clase."""
    errores = []
    for t in textos_de(obj):
        for m in _NUM.finditer(t):
            if exentos_tiempo and _TIEMPO.match(t[m.end():]):
                continue
            if _norm_num(m.group()) not in permitidos:
                errores.append(f"cifra sin localizador: «{m.group()}» en «{t[max(0, m.start()-30):m.end()+30]}»")
    return errores


def _en_transcripcion(turno: str, transcripcion: str) -> bool:
    a, b = " ".join(palabras_normalizadas(turno)), " ".join(palabras_normalizadas(transcripcion))
    return bool(a) and f" {a} " in f" {b} "


def verificar_escenarios(escenarios: list[dict], trazas: dict, transcripciones: dict[str, str]) -> list[str]:
    """Todo escenario es copia fiel de sus corridas: ruta, supuestos, modelo, transiciones de bloqueo,
    y diálogo textual de una transcripción citada."""
    por_id = {c["id"]: c for c in trazas["por_corrida"]}
    errores = []
    ids = [e.get("id") for e in escenarios]
    if len(set(ids)) != len(ids):
        errores.append(f"ids de escenario repetidos: {ids}")
    for e in escenarios:
        eid, citadas = e.get("id"), e.get("corridas", [])
        if not citadas:
            errores.append(f"{eid}: sin id de corrida (invariante 5)")
            continue
        if falta := [c for c in citadas if c not in por_id]:
            errores.append(f"{eid}: cita corridas inexistentes {falta} (invariante 5)")
            continue
        cs = [por_id[c] for c in citadas]
        if e["ruta"] != cs[0]["ruta"]:
            errores.append(f"{eid}: la ruta no coincide con la de {citadas[0]}")
        sup_ok = {s.casefold().strip() for c in cs for s in c["supuestos"]}
        if extra := [s for s in e["supuestos"] if s.casefold().strip() not in sup_ok]:
            errores.append(f"{eid}: supuestos que no están en las corridas citadas: {extra}")
        if e["modelo"].casefold().strip() not in {c["modelo"].casefold().strip() for c in cs}:
            errores.append(f"{eid}: modelo {e['modelo']!r} no es el de ninguna corrida citada")
        trans_ok = {b["transicion"] for c in cs for b in c["bloqueos"]}
        trans_e = [b["transicion"] for b in e["bloqueos"]]
        if set(trans_e) != trans_ok or len(trans_e) != len(set(trans_e)):
            errores.append(f"{eid}: bloqueos {sorted(trans_e)} ≠ los de las corridas citadas {sorted(trans_ok)}")
        fuentes = [transcripciones[c] for c in citadas if c in transcripciones]
        if not fuentes:
            errores.append(f"{eid}: ninguna corrida citada tiene transcripción")
            continue
        for t in e["extracto_dialogo"]:
            if not any(_en_transcripcion(t["texto"], f) for f in fuentes):
                errores.append(f"{eid}: turno que no está en las transcripciones citadas: «{t['texto'][:80]}»")
    return errores


def verificar_intervenciones(salida: dict, tarea: dict, trazas: dict, escenarios: list[dict]) -> list[str]:
    errores = []
    observados = {t for t, p in trazas["agregado"]["pct_bloqueo_por_transicion"].items() if p > 0}
    dados = [i["bloqueo"] for i in salida["intervenciones"]]
    if falta := sorted(observados - set(dados)):
        errores.append(f"faltan intervenciones para bloqueos observados: {falta}")
    if len(dados) != len(set(dados)):
        errores.append("bloqueo repetido en intervenciones")
    res = tarea["task_space"]["reference_solution"]["result"]
    nres = " ".join(palabras_normalizadas(res))
    for i in salida["intervenciones"]:
        for z in ("z1_z2", "z3", "z4", "z5"):
            if nres and len(nres.split()) >= 3 and nres in " ".join(palabras_normalizadas(i[z])):
                errores.append(f"{i['bloqueo']}.{z}: entrega el resultado de la solución de referencia")
    ids_esc = {e["id"] for e in escenarios}
    for linea in salida["puesta_en_comun"]["seleccion_y_orden"]:
        for ref in re.findall(r"\bE[1-9]\b", linea):
            if ref not in ids_esc:
                errores.append(f"puesta en común cita {ref}, que no es un escenario de la guía")
    return errores


# --------------------------------------------------------------------------- entradas
def cargar_transcripciones(directorio: str | Path) -> dict[str, str]:
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted(Path(directorio).glob("*.md"))}


def validar_entradas(tarea: dict, trazas: dict, transcripciones: dict[str, str], contexto: dict) -> None:
    errores = []
    for art, nombre in ((tarea, "tarea"), (trazas, "trazas_resumen")):
        r = validar_contra_esquema(art, nombre)
        if not r:
            errores += list(r.errores)
    if errores:
        raise EntradaInvalida("; ".join(errores))
    r = consistencia_trazas(trazas)
    if not r:
        raise EntradaInvalida("; ".join(r.errores))
    if tarea["id"] != trazas["tarea_id"]:
        raise EntradaInvalida(f"la tarea {tarea['id']!r} no corresponde a las trazas de {trazas['tarea_id']!r}")
    puntaje = contexto.get("puntaje_rub01") or (tarea.get("rubrica_rub01") or {}).get("total")
    if puntaje is None:
        raise EntradaInvalida("falta puntaje_rub01 (contexto o tarea.rubrica_rub01)")
    if not contexto.get("revision_humana_1"):
        raise EntradaInvalida("falta contexto.revision_humana_1 (GOB01 §2: no hay guía sin tarea revisada)")
    con_transcripcion = [c["id"] for c in trazas["por_corrida"] if c["id"] in transcripciones]
    if len(trazas["por_corrida"]) < CONFIG["min_corridas"] or len(con_transcripcion) < CONFIG["min_corridas"]:
        raise TrazasInsuficientes(
            f"{len(trazas['por_corrida'])} corridas ({len(con_transcripcion)} con transcripción); se necesitan "
            f"al menos {CONFIG['min_corridas']} para {CONFIG['min_escenarios']} escenarios con id de corrida. "
            "No se inventan escenarios.")


# --------------------------------------------------------------------------- llamadas
class _Cuenta:
    def __init__(self):
        self.llamadas, self.costo = [], 0.0

    def registrar(self, seccion: str, meta: dict):
        self.llamadas.append({"seccion": seccion, **meta})
        self.costo = round(self.costo + meta["costo_usd"], 6)


def _generar(seccion: str, user: str, schema: dict, verificar, cuenta: _Cuenta, cliente=None) -> dict:
    cfg = CONFIG["secciones"][seccion]
    modelo = modelo_de(cfg["modelo_clave"])
    system = system_de(seccion)
    prompt_usuario, errores, previa = user, [], None
    for intento in range(CONFIG["reparaciones_por_seccion"] + 1):
        try:
            r = llamar(agente="redactor", system=system, user=prompt_usuario, schema=schema, modelo=modelo,
                       esfuerzo=cfg["esfuerzo"], max_tokens=cfg["max_tokens"], cliente=cliente)
        except RuntimeError as e:
            cuenta.costo = round(cuenta.costo + getattr(e, "costo_usd", 0.0), 6)
            raise
        cuenta.registrar(seccion, r["meta"])
        previa = r["salida"]
        errores = verificar(previa)
        if not errores:
            return previa
        prompt_usuario = (user + "\n\n# Corrección requerida\nTu salida anterior fue rechazada por estas razones; "
                          "corrígelas sin cambiar lo demás:\n- " + "\n- ".join(errores[:12])
                          + "\n\nSalida anterior:\n" + json.dumps(previa, ensure_ascii=False))
    err = RedaccionRechazada(seccion, errores, cuenta.costo)
    err.salida = previa
    raise err


def _j(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=1)


# --------------------------------------------------------------------------- guía
def redactar(tarea: dict, trazas: dict, transcripciones: dict[str, str], contexto: dict | None = None,
             cliente=None, texto_noticia: str | None = None) -> dict:
    """Devuelve {"guia", "meta", "validacion"}. Lanza EntradaInvalida, TrazasInsuficientes o
    RedaccionRechazada (con `.costo_usd`). `contexto`: puntaje_rub01, revision_humana_1 {revisor, fecha},
    fecha, version, cambios, tarea_siguiente (opcionales salvo los dos primeros si la tarea no los trae)."""
    contexto = contexto or {}
    validar_entradas(tarea, trazas, transcripciones, contexto)
    cuenta = _Cuenta()
    permitidos = numeros_permitidos(tarea, trazas, transcripciones)
    ts = tarea["task_space"]

    # 1. base: meta, barreras, organización, variantes
    def v_base(s):
        return cifras_sin_localizador(s, permitidos)
    base = _generar("base", "# Tarea\n" + _j(tarea), esquema_base(), v_base, cuenta, cliente)

    # 2. escenarios: solo desde trazas y transcripciones
    resumen_tarea = {k: tarea[k] for k in ("id", "titulo", "nivel_principal", "contenidos_matematicos", "mapa_ciclo")}
    resumen_tarea["enunciado_es"] = tarea["estudiante"]["enunciado_es"]
    resumen_tarea["task_space"] = ts
    user_esc = ("# Tarea\n" + _j(resumen_tarea) + "\n\n# trazas_resumen\n" + _j(trazas) + "\n\n# Transcripciones\n"
                + "\n".join(f"## {i}.md\n{t}" for i, t in transcripciones.items()))

    def v_esc(s):
        if s["estado"] == "insuficiente":
            return []
        e = []
        if not CONFIG["min_escenarios"] <= len(s["escenarios"]) <= CONFIG["max_escenarios"]:
            e.append(f"se esperan {CONFIG['min_escenarios']}–{CONFIG['max_escenarios']} escenarios, hay {len(s['escenarios'])}")
        return e + verificar_escenarios(s["escenarios"], trazas, transcripciones) + cifras_sin_localizador(
            [{k: v for k, v in x.items() if k not in ("id", "corridas")} for x in s["escenarios"]], permitidos)
    esc = _generar("escenarios", user_esc, esquema_escenarios(), v_esc, cuenta, cliente)
    if esc["estado"] == "insuficiente":
        err = TrazasInsuficientes(f"el redactor declara trazas insuficientes: {esc['motivo']}")
        err.costo_usd = cuenta.costo
        raise err
    escenarios = esc["escenarios"]

    # 3. intervenciones y puesta en común
    tabla = dict(trazas["agregado"]["pct_bloqueo_por_transicion"])
    user_int = ("# Tarea\n" + _j({k: tarea[k] for k in ("titulo", "mapa_ciclo", "variantes_detalle")}
                                 | {"enunciado_es": tarea["estudiante"]["enunciado_es"], "task_space": ts,
                                    "recursos_a_solicitud": tarea["estudiante"]["recursos_a_solicitud"]})
                + "\n\n# Tabla de bloqueos observados (proporción de grupos simulados)\n" + _j(tabla)
                + "\n\n# Escenarios redactados\n" + _j(escenarios))

    def v_int(s):
        return verificar_intervenciones(s, tarea, trazas, escenarios) + cifras_sin_localizador(s, permitidos)
    inter = _generar("intervenciones", user_int, esquema_intervenciones(), v_int, cuenta, cliente)

    # 4. ensamble (lo determinístico lo pone el código)
    fecha = contexto.get("fecha") or date.today().isoformat()
    puntaje = contexto.get("puntaje_rub01") or tarea["rubrica_rub01"]["total"]
    ficha = {
        "titulo": tarea["titulo"],
        "noticia": {k: tarea["noticia"][k] for k in ("medio", "titulo", "fecha", "url") if k in tarea["noticia"]},
        "nivel_principal": tarea["nivel_principal"],
        "variantes": [v for v in (tarea["variantes"]["abajo"], tarea["variantes"]["arriba"]) if v],
        "contenidos": tarea["contenidos_matematicos"],
        "tiempo": tarea["tiempo_estimado"],
        "puntaje_rub01": puntaje,
        "version": contexto.get("version", 1),
        "fecha": fecha,
        "cambios": contexto.get("cambios", ""),
    }
    if "sub_tramo" in tarea:
        ficha["sub_tramo"] = tarea["sub_tramo"]
    guia = {
        "tarea_id": tarea["id"],
        "version": ficha["version"],
        "fecha": fecha,
        "ficha": ficha,
        "meta": base["meta"],
        "analisis_a_priori": {
            "rutas": [{k: r[k] for k in ("id", "nombre", "nivel", "modelo")} for r in ts["routes"]],
            "modelo_inadecuado": copy.deepcopy(ts["modelo_inadecuado"]),
            "solucion_referencia": f"{ts['reference_solution']['steps']} Resultado: {ts['reference_solution']['result']}",
            "rango_aceptable": ts["reference_solution"]["acceptable_range"],
            "barreras_por_fase": base["barreras_por_fase"],
        },
        "organizacion": base["organizacion"],
        "escenarios": escenarios,
        "tabla_bloqueos": tabla,
        "intervenciones": inter["intervenciones"],
        "puesta_en_comun": inter["puesta_en_comun"],
        "variantes_y_continuidad": {"uso_variantes": base["uso_variantes"],
                                    "acostumbramiento": base["acostumbramiento"],
                                    "tarea_siguiente": contexto.get("tarea_siguiente")},
        "materiales": dict(CONFIG["materiales"]),
        "trazabilidad": {
            "noticia_url": tarea["noticia"]["url"],
            "diseno": {"modelo": tarea["modelo_y_prompt"]["diseñador"],
                       "version_prompt": tarea["modelo_y_prompt"]["version_prompt"]},
            "rub01_total": puntaje,
            "revision_humana_1": contexto["revision_humana_1"],
            "simulacion": {"n_grupos": trazas["corridas"], "diseno": trazas["diseno"]},
            "revision_humana_2": None,
            "commit": None,
        },
        "modelo_y_prompt": {"redactor": modelo_de("redactor"), "redactor_escenarios": modelo_de("redactor_escenarios"),
                            "version_prompt": VERSION_PROMPT},
    }

    errores = []
    r = validar_contra_esquema(guia, "guia")
    if not r:
        errores += list(r.errores)
    r = escenarios_respaldados(guia, trazas)
    if not r:
        errores += list(r.errores)
    errores += cifras_sin_localizador(
        {k: v for k, v in guia.items() if k not in ("ficha", "trazabilidad", "materiales", "modelo_y_prompt",
                                                    "tabla_bloqueos", "fecha", "tarea_id")}, permitidos)
    if texto_noticia is not None:
        r = cumple_limite_literal(guia, texto_noticia)
        if not r:
            errores += list(r.errores)
    if errores:
        raise RedaccionRechazada("guia", errores, cuenta.costo)

    meta = {"agente": "redactor", "version_prompt": VERSION_PROMPT, "modelos": {
                "redactor": modelo_de("redactor"), "redactor_escenarios": modelo_de("redactor_escenarios")},
            "llamadas": cuenta.llamadas, "costo_usd": cuenta.costo}
    return {"guia": guia, "meta": meta,
            "validacion": {"esquema_guia": True, "escenarios_respaldados": True, "cifras_con_fuente": True,
                           "literal_noticia": None if texto_noticia is None else True}}


# --------------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tarea", required=True)
    ap.add_argument("--trazas", required=True)
    ap.add_argument("--transcripciones", required=True, help="directorio con <id>.md")
    ap.add_argument("--contexto", help="JSON con puntaje_rub01, revision_humana_1, fecha...")
    ap.add_argument("--noticia", help="texto de la noticia (txt) para el control de 25 palabras")
    ap.add_argument("--salida", required=True)
    a = ap.parse_args(argv)
    leer = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))  # noqa: E731
    try:
        res = redactar(leer(a.tarea), leer(a.trazas), cargar_transcripciones(a.transcripciones),
                       leer(a.contexto) if a.contexto else {},
                       texto_noticia=Path(a.noticia).read_text(encoding="utf-8") if a.noticia else None)
    except RedactorError as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        return 2
    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.salida).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"ok · costo {res['meta']['costo_usd']} USD · {a.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
