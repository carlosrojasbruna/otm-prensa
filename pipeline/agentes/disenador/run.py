"""Agente diseñador de OTM-Prensa: noticia filtrada + nivel -> 2 candidatos `tarea` en `borrador`.

Uso como módulo:
    from pipeline.agentes.disenador.run import disenar, iterar
    r = disenar(noticia, "S")                  # r["candidatos"]: lista de tareas (contrato `tarea`)
    r2 = iterar(tarea, evaluacion, noticia)    # r2["tarea"]: versión revisada; r2["atencion_mejoras"]

Línea de comandos (desde la raíz del repo):
    python -m pipeline.agentes.disenador.run diseno <noticia.json> <P|S|U> [salida.json]
    python -m pipeline.agentes.disenador.run iteracion <tarea.json> <evaluacion.json> <noticia.json> [salida.json]

Diseño:
- El modelo no produce el JSON completo de `tarea`: produce el "candidato" (contenido pedagógico) y el
  código ensambla lo determinista (id, estado, versión, cita de la noticia con sus cifras, área, rúbricas
  en null, modelo_y_prompt, agent_visibility). Así la noticia citada y las cifras no se pueden alterar.
- Las cifras de la noticia se eligen por índice (invariante 4) y todo número que el estudiante vea debe
  estar entre ellas.
- Toda salida se valida contra `contratos/tarea.schema.json` y contra las invariantes 3, 4 y 6; si falla
  se reintenta con la lista de errores (hasta `reparaciones_max`).
- Cliente único: pipeline.llm.llamar. Sin `temperature` (los modelos 5.5 no la admiten).
"""
from __future__ import annotations

import copy
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from pipeline.invariantes import (  # noqa: E402
    cumple_limite_literal, validar_contra_esquema, verificar_aislamiento, vista_estudiante,
)
from pipeline.llm import SalidaTruncada, llamar, modelo_de  # noqa: E402

DIR = Path(__file__).resolve().parent
CONFIG = yaml.safe_load((DIR / "config.yaml").read_text(encoding="utf-8"))
VERSION_PROMPT = CONFIG["version_prompt"]
VERSION_RUBRICA = CONFIG["version_rubrica"]
NIVELES = ("P", "S", "U")
NINGUNO = "ninguno"
FASES = ("P1-MRS", "P2-RM", "P3-MM", "P4-WM", "P5-INT", "P6-VAL", "P7-EXP")
AGENT_VISIBILITY = {
    "students": ["enunciado_es", "foto_descripcion", "recursos_a_solicitud"],
    "coder": ["enunciado_es", "task_space"],
    "guide": ["all"],
}


# --------------------------------------------------------------------------- prompt
def cargar_system() -> str:
    """prompt.md + MAR03 + PLT01 v0.2 + RUB01 v4.0 literales. Bloque estático: se cachea completo."""
    partes = [(DIR / "prompt.md").read_text(encoding="utf-8").strip()]
    titulos = ["MAR03 — niveles por edad", "PLT01 v0.2 — plantilla de tarea", "RUB01 v4.0 — rúbrica de calidad de tarea"]
    for titulo, ruta in zip(titulos, CONFIG["cache"]):
        partes.append(f"\n\n---\n\n# REFERENCIA: {titulo}\n\n" + (RAIZ / ruta).read_text(encoding="utf-8").strip())
    return "".join(partes)


# --------------------------------------------------------------------------- esquema que ve el modelo
def _s(**kw):
    return {"type": "string", **kw}


def _nulable(sch):
    return {"anyOf": [sch, {"type": "null"}]}


def _obj(props: dict, requeridos: list | None = None) -> dict:
    return {"type": "object", "properties": props, "required": requeridos or list(props), "additionalProperties": False}


def _esquema_candidato() -> dict:
    """Forma "de cable" del candidato. Se simplifica para no exceder el límite de gramática de la salida
    estructurada: sin anyOf (el valor "ninguno" o "" equivale a null y lo traduce `ensamblar`), una sola
    lista de recursos con su `disponibilidad` y el mapa del ciclo como lista de 7 filas."""
    nivel = {"type": "string", "enum": list(NIVELES)}
    nivel_o_nada = {"type": "string", "enum": [*NIVELES, NINGUNO]}
    ruta_nivel = {"type": "string", "enum": ["P", "S", "S1", "S2", "U"]}
    recurso = _obj({
        "id": _s(), "que_es": _s(), "contenido": _s(),
        "disponibilidad": {"type": "string", "enum": ["a_solicitud", "de_entrada"]},
        "fase": {"type": "string", "enum": list(FASES)}, "fuente": _s(),
    })
    fila = _obj({"fase": {"type": "string", "enum": list(FASES)}, "decision": _s(), "evidencia": _s(),
                 "bloqueo_probable": _s()})
    variante = _obj({"tramo": {"type": "string", "enum": ["P", "S", "S1", "S2", "U", NINGUNO]}, "cambios": _s()})
    return _obj({
        "enfoque": _s(),
        "slug": _s(),
        "titulo": _s(),
        "nivel_principal": nivel,
        "sub_tramo": {"type": "string", "enum": ["S1", "S2", NINGUNO]},
        "variantes": _obj({"abajo": nivel_o_nada, "arriba": nivel_o_nada}),
        "contenidos_matematicos": {"type": "array", "items": _s()},
        "tiempo_estimado": _s(),
        "cifras_usadas_idx": {"type": "array", "items": {"type": "integer"}},
        "enunciado_es": _s(),
        "foto_descripcion": _s(),
        "recursos": {"type": "array", "items": recurso},
        "variantes_detalle": _obj({"abajo": variante, "arriba": variante}),
        "mapa_ciclo": {"type": "array", "items": fila},
        "required_assumptions": {"type": "array", "items": _s()},
        "solucion_pasos": _s(),
        "solucion_resultado": _s(),
        "solucion_rango": _s(),
        "routes": {"type": "array", "items": _obj({
            "id": _s(), "nombre": _s(), "nivel": ruta_nivel, "modelo": _s(), "resultado": _s()})},
        "modelo_inadecuado": _s(),
        "por_que_falla": _s(),
        "validation_evidence": _s(),
    })


def esquema_salida(modo: str = "diseno") -> dict:
    """Esquema de output_config.format. Sin minItems/pattern (no admitidos): se comprueban en código."""
    if modo == "iteracion":
        return _obj({
            "atencion_mejoras": {"type": "array", "items": _obj({"criterio": _s(), "que_cambio": _s()})},
            "tarea": _esquema_candidato(),
        })
    return _obj({"candidatos": {"type": "array", "items": _esquema_candidato()}})


# --------------------------------------------------------------------------- ensamblado
def _slug(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60].strip("-") or "tarea"


def _recurso(r: dict, disponibilidad: str) -> dict:
    return {"id": r["id"], "que_es": r["que_es"], "contenido": r["contenido"],
            "disponibilidad": disponibilidad, "fase": r["fase"], "fuente": r["fuente"]}


def ensamblar(cand: dict, noticia: dict, *, fecha: str, version: int = 1, id_tarea: str | None = None,
              modelo: str | None = None) -> dict:
    """Candidato del modelo -> `tarea` completa en estado borrador."""
    n_cifras = len(noticia.get("cifras", []))
    idx = sorted({i for i in cand["cifras_usadas_idx"] if isinstance(i, int) and 0 <= i < n_cifras})
    cita = {
        "noticia_id": noticia["id"], "medio": noticia["medio"], "titulo": noticia["titulo"],
        "fecha": noticia["fecha"], "url": noticia["url"], "resumen_propio": noticia["resumen_propio"],
        "cifras_usadas": [copy.deepcopy(noticia["cifras"][i]) for i in idx],
    }
    ts = {
        "required_assumptions": list(cand["required_assumptions"]),
        "reference_solution": {"steps": cand["solucion_pasos"], "result": cand["solucion_resultado"],
                               "acceptable_range": cand["solucion_rango"]},
        "routes": [dict(r) for r in cand["routes"]],
        "modelo_inadecuado": {"id": cand["modelo_inadecuado"], "por_que_falla": cand["por_que_falla"]},
        "validation_evidence": cand["validation_evidence"],
        "agent_visibility": copy.deepcopy(AGENT_VISIBILITY),
    }
    filas = {f["fase"]: f for f in cand["mapa_ciclo"]}
    if set(filas) != set(FASES) or len(cand["mapa_ciclo"]) != len(FASES):
        raise ValueError(f"mapa_ciclo debe tener exactamente una fila por fase P1-P7; llegó {sorted(filas)}")
    mapa = {f: {"decision": filas[f]["decision"], "evidencia": filas[f]["evidencia"],
                "bloqueo_probable": filas[f]["bloqueo_probable"].strip() or None} for f in FASES}
    nv = lambda x: None if x == NINGUNO else x  # noqa: E731

    def det(v):
        return None if v["tramo"] == NINGUNO else {"tramo": v["tramo"], "cambios": v["cambios"]}

    solicitud = [r for r in cand["recursos"] if r["disponibilidad"] == "a_solicitud"]
    entrada = [r for r in cand["recursos"] if r["disponibilidad"] == "de_entrada"]
    tarea = {
        "id": id_tarea or f"{fecha[:7]}-{_slug(cand['slug'])}",
        "titulo": cand["titulo"],
        "estado": CONFIG["estado_de_salida"],
        "version": version,
        "fecha": fecha,
        "noticia": cita,
        "nivel_principal": cand["nivel_principal"],
        "variantes": {"abajo": nv(cand["variantes"]["abajo"]), "arriba": nv(cand["variantes"]["arriba"])},
        "area": noticia["area"],
        "contenidos_matematicos": cand["contenidos_matematicos"],
        "tiempo_estimado": cand["tiempo_estimado"],
        "estudiante": {
            "enunciado_es": cand["enunciado_es"],
            "foto_descripcion": cand["foto_descripcion"],
            "recursos_a_solicitud": [_recurso(r, "a_solicitud") for r in solicitud],
        },
        "variantes_detalle": {"abajo": det(cand["variantes_detalle"]["abajo"]),
                              "arriba": det(cand["variantes_detalle"]["arriba"])},
        "recursos_de_entrada": [_recurso(r, "de_entrada") for r in entrada],
        "mapa_ciclo": mapa,
        "task_space": ts,
        "rubrica_rub01": None,
        "rubrica_rub02": {"P": None, "S": None, "U": None},
        "modelo_y_prompt": {"diseñador": modelo or modelo_de("disenador"),
                            "version_prompt": VERSION_PROMPT, "version_rubrica": VERSION_RUBRICA},
    }
    if cand["nivel_principal"] == "S" and cand.get("sub_tramo") not in (None, NINGUNO):
        tarea["sub_tramo"] = cand["sub_tramo"]
    return tarea


# --------------------------------------------------------------------------- validación (invariantes 1, 3, 4, 6)
_NUM = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)*")


def _canon(tok: str) -> set[str]:
    """Formas equivalentes de un número escrito: '1.234'/'1,234'/'1234', '1,5'/'1.5'."""
    sin_miles = re.sub(r"[.,](?=\d{3}(?:\D|$))", "", tok)
    return {tok, sin_miles, tok.replace(",", "."), sin_miles.replace(",", ".")}


def numeros_en(texto: str) -> list[str]:
    return _NUM.findall(texto)


def numeros_permitidos(noticia: dict, cifras_idx: list[int] | None = None) -> set[str]:
    """Números que la noticia respalda (valor de cada cifra y año de la fecha de la noticia)."""
    permitidos: set[str] = set(numeros_en(noticia["fecha"]))
    permitidos.add(noticia["fecha"][:4])
    for c in noticia.get("cifras", []):
        for tok in numeros_en(str(c["valor"])):
            permitidos |= _canon(tok)
    return permitidos


# Regla es-CL (prompt v1.1): decimales con coma. Punto + 1-2 dígitos, o + 4 o más dígitos, es decimal;
# punto + exactamente 3 dígitos es separador de miles (3.276) y no se marca.
_DECIMAL_PUNTO = re.compile(r"(?<![\w.,])\d+\.(?:\d{1,2}|\d{4,})(?![\d]|\.\d)")
# Unidades y montos en inglés que no deben quedar en el texto en español ("$20bn", "30-day").
_INGLES = re.compile(r"\d+(?:[.,]\d+)?\s?(?:bn|mn|billions?|millions?|trillions?|k)\b|\d+-(?:day|days|year|years|month|months|week|hour)\b",
                     re.IGNORECASE)
_FUENTE_GENERICA = re.compile(
    r"^(?:descripci[oó]n (?:de|del)\b|asociaci|operadores|expertos?\b|el sector|los sectores|fuentes?\b|"
    r"ejemplo|varios|diversas?|distintos|medios\b|prensa\b|internet|conocimiento|informaci[oó]n general)|\(ejemplo\)",
    re.IGNORECASE)
PREFIJO_SUPUESTO = "supuesto del escenario"


def _textos(obj, ruta=""):
    """Hojas de texto de un objeto JSON con su ruta."""
    if isinstance(obj, str):
        yield ruta, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _textos(v, f"{ruta}.{k}" if ruta else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _textos(v, f"{ruta}[{i}]")


def errores_formato_es_cl(tarea: dict) -> list[str]:
    """Decimales con punto o unidades en inglés en el texto en español (enunciado, recursos, mapa, task_space)."""
    secciones = {"estudiante": tarea["estudiante"], "recursos_de_entrada": tarea["recursos_de_entrada"],
                 "mapa_ciclo": tarea["mapa_ciclo"], "task_space": tarea["task_space"]}
    errs = []
    for donde, txt in _textos(secciones):
        for m in _DECIMAL_PUNTO.finditer(txt):
            errs.append(f"coma decimal es-CL en {donde}: «{m.group(0)}» usa punto decimal (escribe «{m.group(0).replace('.', ',')}»)")
        for m in _INGLES.finditer(txt):
            errs.append(f"unidad en inglés en {donde}: «{m.group(0)}» (escribe montos y unidades en español: «20 mil millones de dólares», «30 días»)")
    return errs


def errores_fuente_recursos(tarea: dict) -> list[str]:
    """`fuente` de cada recurso: noticia con localizador, otra fuente concreta o supuesto del escenario marcado."""
    errs = []
    for rec in tarea["estudiante"]["recursos_a_solicitud"] + tarea["recursos_de_entrada"]:
        fuente = rec["fuente"].strip()
        bajo = fuente.lower()
        es_supuesto_contenido = rec["contenido"].strip().lower().startswith(PREFIJO_SUPUESTO)
        if bajo.startswith("noticia"):
            # misma regla que el verificador (fuente única): «noticia» exige localizador (párrafo N, titular…)
            from pipeline.agentes.verificador.run import clasificar_fuente
            if clasificar_fuente(fuente, rec["contenido"])["clase"] != "noticia":
                errs.append(f"recurso {rec['id']}: fuente «{fuente}» no tiene localizador; usa «noticia, párrafo N» "
                            "(o titular, tabla, gráfico) o marca el recurso como supuesto del escenario")
                continue
        elif bajo.startswith("otra fuente:"):
            resto = fuente.split(":", 1)[1].strip()
            ok = len(resto) >= 3 and not _FUENTE_GENERICA.search(resto)
            if not ok:
                errs.append(f"recurso {rec['id']}: fuente «{fuente}» es genérica; nombra un organismo o publicación concreta "
                            "o marca el recurso como «Supuesto del escenario: …» con fuente «supuesto del escenario»")
            continue
        elif bajo == PREFIJO_SUPUESTO:
            ok = True
            if not es_supuesto_contenido:
                errs.append(f"recurso {rec['id']}: fuente «supuesto del escenario» pero el contenido no empieza con «Supuesto del escenario»")
            continue
        else:
            errs.append(f"recurso {rec['id']}: fuente «{fuente}» debe empezar por «noticia», «otra fuente: <concreta>» o «supuesto del escenario»")
            continue
        if es_supuesto_contenido:
            errs.append(f"recurso {rec['id']}: el contenido es un supuesto del escenario pero la fuente es «{fuente}»; usa «supuesto del escenario»")
    return errs


def validar_tarea(tarea: dict, noticia: dict, texto_noticia: str | None = None) -> list[str]:
    """Lista de errores (vacía si la tarea cumple). No lanza."""
    errores: list[str] = []
    r = validar_contra_esquema(tarea, "tarea")
    errores += list(r.errores)
    if r.errores:  # sin forma válida el resto no es fiable
        return errores
    est = tarea["estudiante"]
    # invariante 6
    aisl = verificar_aislamiento(vista_estudiante(tarea), tarea)
    errores += [f"aislamiento: {e}" for e in aisl.errores]
    # invariante 4: números del estudiante respaldados por cifras de la noticia
    permitidos = numeros_permitidos(noticia)
    visibles = [("enunciado_es", est["enunciado_es"])]
    visibles += [(f"recursos_a_solicitud[{r['id']}]", r["contenido"]) for r in est["recursos_a_solicitud"]]
    visibles += [(f"recursos_de_entrada[{r['id']}]", r["contenido"]) for r in tarea["recursos_de_entrada"]]
    for donde, txt in visibles:
        for tok in numeros_en(txt):
            if not (_canon(tok) & permitidos):
                errores.append(f"cifra sin localizador en {donde}: «{tok}» no está entre las cifras de la noticia")
    # cifras_usadas deben ser las de la noticia (mismos localizadores)
    por_valor = {json.dumps(c, sort_keys=True) for c in noticia.get("cifras", [])}
    for c in tarea["noticia"]["cifras_usadas"]:
        if json.dumps(c, sort_keys=True) not in por_valor:
            errores.append(f"cifra usada ajena a la noticia: {c.get('que_es')}")
    # recursos de entrada deben estar en el enunciado (decisión architect)
    for rec in tarea["recursos_de_entrada"]:
        for tok in numeros_en(rec["contenido"]):
            if not (_canon(tok) & set().union(*[_canon(t) for t in numeros_en(est["enunciado_es"])] or [set()])):
                errores.append(f"recurso de_entrada {rec['id']} con «{tok}» que no está escrito en enunciado_es")
    ids = [r["id"] for r in est["recursos_a_solicitud"]] + [r["id"] for r in tarea["recursos_de_entrada"]]
    if len(ids) != len(set(ids)):
        errores.append("ids de recurso repetidos entre recursos_a_solicitud y recursos_de_entrada")
    # recurso con cifra debe citar la noticia como fuente
    for rec in est["recursos_a_solicitud"] + tarea["recursos_de_entrada"]:
        if numeros_en(rec["contenido"]) and "noticia" not in rec["fuente"].lower():
            errores.append(f"recurso {rec['id']} con cifras pero fuente sin localizador de la noticia")
    # prompt v1.1: coma decimal es-CL, unidades en español y fuente de cada recurso
    errores += errores_formato_es_cl(tarea)
    errores += errores_fuente_recursos(tarea)
    # forma que el esquema JSON no expresa
    if len(est["enunciado_es"].split()) < 25:
        errores.append("enunciado_es demasiado corto (< 25 palabras)")
    if not tarea["noticia"]["cifras_usadas"] and numeros_en(est["enunciado_es"]):
        errores.append("el enunciado trae cifras pero cifras_usadas está vacío")
    # invariante 3: contra el resumen y el título citados, y contra el texto completo si se entrega
    propio = {k: v for k, v in tarea.items() if k not in ("noticia",)}
    fuente = noticia["resumen_propio"] + " " + noticia["titulo"] + ("\n" + texto_noticia if texto_noticia else "")
    lit = cumple_limite_literal(propio, fuente)
    errores += [f"literal: {e}" for e in lit.errores]
    return errores


# --------------------------------------------------------------------------- mensajes
def _mensaje(modo: str, noticia: dict, nivel: str, tarea_prev: dict | None, evaluacion: dict | None) -> str:
    n = {k: noticia[k] for k in ("id", "medio", "titulo", "fecha", "url", "area", "resumen_propio")}
    n["cifras"] = [{"idx": i, **c} for i, c in enumerate(noticia.get("cifras", []))]
    cuerpo: dict = {"modo": modo, "nivel": nivel, "noticia": n}
    if modo == "iteracion":
        rub = evaluacion["rub01"] if "rub01" in evaluacion else evaluacion
        cuerpo["tarea_anterior"] = tarea_prev
        cuerpo["evaluacion"] = {"total": rub.get("total"), "mejoras": rub["mejoras"],
                                "criterios": {k: {"puntaje": v["puntaje"], "justificacion": v["justificacion"]}
                                              for k, v in rub["criterios"].items()}}
        instruccion = ("Devuelve la tarea revisada (objeto `tarea`) y `atencion_mejoras` con una entrada por "
                       "cada criterio listado en evaluacion.mejoras.")
    else:
        instruccion = "Devuelve exactamente dos candidatos distintos en `candidatos`."
    return (f"```json\n{json.dumps(cuerpo, ensure_ascii=False, indent=1)}\n```\n\n{instruccion} "
            f"Nivel objetivo: {nivel}.")


INSTRUCCION_SALIDA_CORTA = (
    "IMPORTANTE: tu respuesta anterior se cortó por exceder el máximo de tokens de salida. Responde de nuevo, "
    "completa y válida, pero breve: razona poco antes de escribir; enunciado_es de 60 a 140 palabras; cada campo "
    "de texto del mapa del ciclo, de las rutas y de la solución en 1 o 2 oraciones; como máximo 4 recursos, "
    "3 rutas y 4 supuestos por candidato. No repitas entre campos lo que ya dijiste.")


def _bucle(*, modo, noticia, nivel, tarea_prev, evaluacion, fecha, cliente, texto_noticia, version, id_tarea):
    """Llama al modelo, ensambla y valida; reintenta con errores. Devuelve (items, meta)."""
    system = cargar_system()
    user0 = _mensaje(modo, noticia, nivel, tarea_prev, evaluacion)
    esperado = 2 if modo == "diseno" else 1
    user, costo, intentos_meta, historial = user0, 0.0, [], []
    validos: list[tuple[dict, dict]] = []
    rechazados: list[dict] = []
    ultimo_meta, atencion = None, []
    acortado = False
    for ronda in range(CONFIG["reparaciones_max"] + 1):
        try:
            r = llamar(agente="disenador", system=system, user=user, schema=esquema_salida(modo),
                       esfuerzo=CONFIG["esfuerzo"], max_tokens=CONFIG["max_tokens"], cliente=cliente)
        except SalidaTruncada as e:
            # La misma petición se volvería a cortar: se repite UNA vez pidiendo una salida más corta.
            costo += getattr(e, "costo_usd", 0.0)
            if acortado or not CONFIG.get("salida_corta_si_trunca", True):
                e.costo_usd = costo
                raise
            acortado = True
            historial.append({"ronda": ronda + 1, "validos": 0, "errores": [(-1, ["stop_reason=max_tokens"])]})
            user0 = user0 + "\n\n" + INSTRUCCION_SALIDA_CORTA
            user = user + "\n\n" + INSTRUCCION_SALIDA_CORTA
            try:
                r = llamar(agente="disenador", system=system, user=user, schema=esquema_salida(modo),
                           esfuerzo=CONFIG["esfuerzo"], max_tokens=CONFIG["max_tokens"], cliente=cliente)
            except RuntimeError as e2:
                e2.costo_usd = costo + getattr(e2, "costo_usd", 0.0)
                raise
        except RuntimeError as e:
            e.costo_usd = costo + getattr(e, "costo_usd", 0.0)
            raise
        costo += r["meta"]["costo_usd"]
        ultimo_meta = r["meta"]
        crudo = r["salida"]
        atencion = crudo.get("atencion_mejoras", [])
        cands = crudo["candidatos"] if modo == "diseno" else [crudo["tarea"]]
        fallos = []
        validos = []
        for k, c in enumerate(cands):
            errs = []
            if c.get("nivel_principal") != nivel:
                errs.append(f"nivel_principal {c.get('nivel_principal')!r} ≠ nivel objetivo {nivel!r}")
            try:
                t = ensamblar(c, noticia, fecha=fecha, version=version, id_tarea=id_tarea, modelo=r["meta"]["modelo"])
                errs += validar_tarea(t, noticia, texto_noticia)
            except (KeyError, TypeError, ValueError) as e:
                t, errs = None, errs + [f"estructura inesperada: {type(e).__name__}: {e}"]
            if modo == "iteracion":
                faltan = {m["criterio"] for m in (evaluacion.get("rub01") or evaluacion)["mejoras"]} - \
                         {a["criterio"] for a in crudo.get("atencion_mejoras", [])}
                if faltan:
                    errs.append(f"atencion_mejoras no cubre los criterios: {sorted(faltan)}")
            if errs:
                fallos.append((k, errs))
            else:
                validos.append((t, c))
        if modo == "diseno" and len(cands) != esperado:
            fallos.append((-1, [f"se pidieron {esperado} candidatos y llegaron {len(cands)}"]))
        historial.append({"ronda": ronda + 1, "validos": len(validos), "errores": [(k, e) for k, e in fallos]})
        if not fallos:
            break
        if ronda < CONFIG["reparaciones_max"]:
            lista = "\n".join(f"- candidato {k}: {e}" for k, errs in fallos for e in errs)
            user = (user0 + "\n\nTu respuesta anterior no cumplió estas comprobaciones automáticas. "
                    "Devuelve la respuesta completa corregida:\n" + lista +
                    "\n\nRespuesta anterior:\n```json\n" + json.dumps(crudo, ensure_ascii=False) + "\n```")
        else:
            rechazados = [{"candidato": k, "errores": e} for k, e in fallos]
    if not validos:
        err = RuntimeError(f"disenador: ninguna salida válida tras {len(historial)} rondas: {historial[-1]['errores']}")
        err.costo_usd = costo
        raise err
    meta = {**ultimo_meta, "costo_usd": round(costo, 6), "rondas": len(historial), "historial": historial,
            "version_prompt": VERSION_PROMPT, "version_rubrica": VERSION_RUBRICA,
            "version_mar03": CONFIG["version_mar03"], "version_plantilla": CONFIG["version_plantilla"],
            "rechazados": rechazados}
    return validos, meta, atencion


# --------------------------------------------------------------------------- API pública
def disenar(noticia: dict, nivel: str, *, fecha: str | None = None, cliente=None,
            texto_noticia: str | None = None) -> dict:
    """Noticia (contrato `noticia`) + nivel -> {"candidatos": [tarea, ...], "enfoques": [...], "meta": {...}}."""
    if nivel not in NIVELES:
        raise ValueError(f"nivel debe ser uno de {NIVELES}")
    ok = validar_contra_esquema(noticia, "noticia")
    if not ok:
        raise ValueError("la noticia no valida contra su contrato: " + "; ".join(ok.errores))
    fecha = fecha or date.today().isoformat()
    validos, meta, _ = _bucle(modo="diseno", noticia=noticia, nivel=nivel, tarea_prev=None, evaluacion=None,
                           fecha=fecha, cliente=cliente, texto_noticia=texto_noticia, version=1, id_tarea=None)
    tareas = [t for t, _ in validos]
    ids = [t["id"] for t in tareas]
    for i, t in enumerate(tareas):  # ids únicos entre candidatos
        if ids.count(t["id"]) > 1:
            t["id"] = f"{t['id']}-{chr(97 + i)}"
    return {"candidatos": tareas, "enfoques": [c.get("enfoque", "") for _, c in validos], "meta": meta}


def iterar(tarea: dict, evaluacion: dict, noticia: dict, *, fecha: str | None = None, cliente=None,
           texto_noticia: str | None = None) -> dict:
    """Tarea + evaluación RUB01 con `mejoras` -> {"tarea": versión+1 en borrador, "atencion_mejoras", "meta"}."""
    rub = evaluacion["rub01"] if "rub01" in evaluacion else evaluacion
    if not rub.get("mejoras"):
        raise ValueError("la evaluación no trae mejoras: no hay nada que iterar")
    fecha = fecha or date.today().isoformat()
    previa = {k: v for k, v in tarea.items() if k not in ("rubrica_rub01", "rubrica_rub02", "modelo_y_prompt")}
    # el candidato conserva nivel y noticia; el sistema fija id (misma tarea) y versión + 1
    validos, meta, atencion = _bucle(modo="iteracion", noticia=noticia, nivel=tarea["nivel_principal"], tarea_prev=previa,
                           evaluacion=evaluacion, fecha=fecha, cliente=cliente, texto_noticia=texto_noticia,
                           version=tarea["version"] + 1, id_tarea=tarea["id"])
    nueva, _ = validos[0]
    return {"tarea": nueva, "atencion_mejoras": atencion, "meta": meta}


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("diseno", "iteracion"):
        print(__doc__)
        return 1
    leer = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))  # noqa: E731
    if argv[0] == "diseno":
        res = disenar(leer(argv[1]), argv[2])
        salida = argv[3] if len(argv) > 3 else None
    else:
        res = iterar(leer(argv[1]), leer(argv[2]), leer(argv[3]))
        salida = argv[4] if len(argv) > 4 else None
    texto = json.dumps(res, ensure_ascii=False, indent=2)
    if salida:
        Path(salida).write_text(texto, encoding="utf-8")
    else:
        print(texto)
    print(f"costo_usd={res['meta']['costo_usd']} rondas={res['meta']['rondas']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
