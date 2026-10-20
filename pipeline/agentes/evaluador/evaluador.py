"""Agente evaluador de OTM-Prensa: puntúa una tarea con RUB01 v4.0.

Uso como módulo:
    from pipeline.agentes.evaluador.evaluador import evaluar
    res = evaluar(tarea)            # tarea: dict (ver construir_mensaje)
    res["rub01"]                    # bloque con la forma fijada por build-lead
    res["meta"]                     # modelo, versión de prompt, uso de tokens, costo, etc.

Uso por línea de comandos (desde la raíz del repo):
    python -m pipeline.agentes.evaluador.evaluador evals/casos/evaluador/giants-shoes.json

Decisiones (ver pipeline/state/decisiones.md):
- El modelo de partida (claude-opus-5-5) rechaza `temperature` ("deprecated for this model"):
  se usa el default del modelo. También rechaza `tool_choice` forzado y `thinking.disabled`;
  la salida estructurada se fuerza con `output_config.format` (json_schema), y el esfuerzo de
  razonamiento se fija con `output_config.effort`.
- El total se recalcula en código; no se confía en el que devuelve el modelo.
- La clave se obtiene solo con pipeline.apikey.api_key (OTM_API_KEY local / ANTHROPIC_API_KEY en Actions).
"""
from __future__ import annotations

import copy
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

DIR = Path(__file__).resolve().parent
RUB01_PATH = RAIZ / "insumos" / "rubricas" / "RUB01_calidad-tarea_v4.0_2026-10-20.json"

MODELO = "claude-opus-5-5"
VERSION_PROMPT = "1.3"          # versión vigente del prompt de sistema
ESFUERZO = "high"               # output_config.effort
MAX_TOKENS = 16000
VERSION_RUBRICA = "4.0"
VERSION_MAR03 = "1.0"

# Precios USD por millón de tokens. SUPUESTO (no hay tabla oficial en el repo): precio de lista
# de Opus 4.5/4.6 (5 entrada / 25 salida; escritura de caché 5 min = 1,25x; lectura = 0,1x).
# PRECIOS_PESIMISTAS (precio de Opus 4.1: 15/75) se informan como cota superior; el tope usa PRECIOS.
PRECIOS = {"input": 5.0, "output": 25.0, "cache_write": 6.25, "cache_read": 0.50}
PRECIOS_PESIMISTAS = {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.50}


def cargar_rub01() -> dict:
    return json.loads(RUB01_PATH.read_text(encoding="utf-8"))


RUB01 = cargar_rub01()
IDS = [c["id"] for c in RUB01["criterios"]]
assert RUB01["version"] == VERSION_RUBRICA and len(IDS) == 12


def cargar_prompt(version: str = VERSION_PROMPT) -> str:
    """Carga el prompt de sistema versionado y verifica que contiene RUB01 literal y completa."""
    texto = (DIR / f"prompt_sistema_v{version}.md").read_text(encoding="utf-8")
    rub = RUB01_PATH.read_text(encoding="utf-8").strip()
    if rub not in texto:
        raise ValueError(f"prompt_sistema_v{version}.md no contiene RUB01 v{VERSION_RUBRICA} literal")
    return texto


def esquema_salida() -> dict:
    """JSON Schema para output_config.format. El orden cita → justificación → puntaje obliga a
    fijar la evidencia antes del número. El bloque coincide con la forma fijada por build-lead."""
    crit = {
        "type": "object",
        "properties": {
            "cita": {"type": "string"},
            "justificacion": {"type": "string"},
            "puntaje": {"type": "integer", "enum": [0, 1, 2]},
        },
        "required": ["cita", "justificacion", "puntaje"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "version_rubrica": {"type": "string", "enum": [VERSION_RUBRICA]},
            "criterios": {
                "type": "object",
                "properties": {i: copy.deepcopy(crit) for i in IDS},
                "required": list(IDS),
                "additionalProperties": False,
            },
            "total": {"type": "integer"},
            "mejoras": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "criterio": {"type": "string", "enum": list(IDS)},
                        "mejora_minima": {"type": "string"},
                    },
                    "required": ["criterio", "mejora_minima"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["version_rubrica", "criterios", "total", "mejoras"],
        "additionalProperties": False,
    }


def construir_mensaje(tarea: dict) -> str:
    """tarea: {titulo, nivel_declarado: {nivel, sub_tramo?}, forma_texto, texto, recursos: [str],
    mapa_ciclo?: str}. Nunca incluye puntajes de referencia, rol de calibración ni notas evaluativas."""
    niv = tarea["nivel_declarado"]
    nivel = niv["nivel"] + (f" (sub-tramo {niv['sub_tramo']})" if niv.get("sub_tramo") else "")
    recursos = tarea.get("recursos") or []
    rec = "\n".join(f"- {r}" for r in recursos) if recursos else "No se declaran recursos ni materiales adicionales."
    mapa = tarea.get("mapa_ciclo") or "No incluido."
    return (
        "# Tarea a evaluar con RUB01 v4.0\n\n"
        f"## Nivel declarado (MAR03)\n{nivel}\n\n"
        f"## Título\n{tarea['titulo']}\n\n"
        f"## Texto de la tarea\nTipo de texto: {tarea['forma_texto']}.\n\n{tarea['texto'].strip()}\n\n"
        f"## Recursos y materiales\n{rec}\n\n"
        f"## Mapa a priori del ciclo\n{mapa}\n\n"
        "Puntúa los 12 criterios según el prompt de sistema y devuelve el objeto JSON."
    )


def _norm(s: str) -> str:
    s = s.lower().replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[^\w']+", " ", s)
    return " ".join(s.split())


def costo_usd(uso: dict, precios: dict = PRECIOS) -> float:
    return round(
        uso.get("input_tokens", 0) * precios["input"] / 1e6
        + uso.get("output_tokens", 0) * precios["output"] / 1e6
        + uso.get("cache_creation_input_tokens", 0) * precios["cache_write"] / 1e6
        + uso.get("cache_read_input_tokens", 0) * precios["cache_read"] / 1e6,
        6,
    )


def postprocesar(bruto: dict, mensaje: str) -> tuple[dict, list[str]]:
    """Valida la forma, recalcula el total y revisa mejoras y citas. Devuelve (rub01, avisos)."""
    avisos: list[str] = []
    crits = bruto["criterios"]
    if set(crits) != set(IDS):
        raise ValueError(f"ids de criterios distintos de RUB01: {sorted(crits)}")
    criterios = {}
    for i in IDS:
        c = crits[i]
        if c["puntaje"] not in (0, 1, 2):
            raise ValueError(f"puntaje inválido en {i}: {c['puntaje']}")
        cita = c["cita"].strip()
        if len(cita.split()) > 25:  # invariante 3: nunca más de 25 palabras literales seguidas
            cita = " ".join(cita.split()[:25]) + " …"
            avisos.append(f"cita_recortada_25:{i}")
        criterios[i] = {"puntaje": int(c["puntaje"]), "justificacion": c["justificacion"].strip(), "cita": cita}
        if _norm(c["cita"]) and _norm(c["cita"]) not in _norm(mensaje):
            avisos.append(f"cita_no_literal:{i}")
    total = sum(c["puntaje"] for c in criterios.values())
    if bruto.get("total") != total:
        avisos.append(f"total_modelo={bruto.get('total')}_recalculado={total}")
    bajos = [i for i in IDS if criterios[i]["puntaje"] < 2]
    mejoras, vistos = [], set()
    for m in bruto.get("mejoras", []):
        if m["criterio"] in bajos and m["criterio"] not in vistos and m["mejora_minima"].strip():
            mejoras.append({"criterio": m["criterio"], "mejora_minima": m["mejora_minima"].strip()})
            vistos.add(m["criterio"])
    faltan = [i for i in bajos if i not in vistos]
    if faltan:  # error, no aviso: cumple_umbral_rub01 exige una mejora por criterio en 0 o 1 (se reintenta)
        raise ValueError("mejora_faltante:" + ",".join(faltan))
    if len(mejoras) != len(bruto.get("mejoras", [])):
        avisos.append("mejora_sobrante_o_repetida_descartada")
    mejoras.sort(key=lambda m: IDS.index(m["criterio"]))
    rub01 = {"version_rubrica": VERSION_RUBRICA, "criterios": criterios, "total": total, "mejoras": mejoras}
    validar_contrato(rub01)
    return rub01, avisos


def validar_contrato(rub01: dict) -> None:
    """Invariante 1: valida contra contratos/evaluacion_rub01.schema.json y la consistencia
    (total = suma; una mejora por criterio < 2). Lanza ValueError si no cumple."""
    from pipeline.invariantes import consistencia_rub01, validar_contra_esquema

    errores = list(validar_contra_esquema(rub01, "evaluacion_rub01").errores) + list(consistencia_rub01(rub01).errores)
    if errores:
        raise ValueError("rub01 no valida: " + "; ".join(errores))


def evaluar(tarea: dict, version_prompt: str = VERSION_PROMPT, modelo: str = MODELO,
            esfuerzo: str = ESFUERZO, cliente=None, reintentos: int = 2) -> dict:
    """Una llamada independiente al evaluador. Devuelve {"rub01": ..., "meta": ...}."""
    import anthropic
    from pipeline.apikey import api_key

    cliente = cliente or anthropic.Anthropic(api_key=api_key())
    sistema = cargar_prompt(version_prompt)
    mensaje = construir_mensaje(tarea)
    kwargs = dict(
        model=modelo,
        max_tokens=MAX_TOKENS,
        system=[{"type": "text", "text": sistema, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": mensaje}],
        output_config={"format": {"type": "json_schema", "schema": esquema_salida()}, "effort": esfuerzo},
    )
    ultimo_error = None
    uso_acum = {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    for intento in range(reintentos + 1):
        t0 = time.time()
        try:
            r = cliente.messages.create(**kwargs)
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError) as e:
            ultimo_error = e
            time.sleep(10 * (intento + 1))
            continue
        u = r.usage
        for k in uso_acum:
            uso_acum[k] += getattr(u, k, 0) or 0
        texto = "".join(b.text for b in r.content if b.type == "text")
        try:
            if r.stop_reason != "end_turn":
                raise ValueError(f"stop_reason={r.stop_reason}")
            rub01, avisos = postprocesar(json.loads(texto), mensaje)
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            ultimo_error = e
            continue
        thinking = getattr(getattr(u, "output_tokens_details", None), "thinking_tokens", None)
        meta = {
            "agente": "evaluador",
            "modelo_solicitado": modelo,
            "modelo_respuesta": r.model,
            "version_prompt": version_prompt,
            "version_rubrica": VERSION_RUBRICA,
            "version_mar03": VERSION_MAR03,
            "parametros": {"temperature": "default (el modelo rechaza temperature)",
                           "effort": esfuerzo, "max_tokens": MAX_TOKENS,
                           "salida": "output_config.format json_schema"},
            "request_id": getattr(r, "_request_id", None),
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "segundos": round(time.time() - t0, 1),
            "intentos": intento + 1,
            "uso": {**uso_acum, "thinking_tokens": thinking},
            "costo_usd": costo_usd(uso_acum),
            "costo_usd_pesimista": costo_usd(uso_acum, PRECIOS_PESIMISTAS),
            "avisos": avisos,
        }
        return {"rub01": rub01, "meta": meta}
    err = RuntimeError(f"evaluador falló tras {reintentos + 1} intentos: {ultimo_error}")
    err.costo_usd = costo_usd(uso_acum)  # el gasto de intentos fallidos también cuenta
    raise err from ultimo_error


if __name__ == "__main__":
    from evals.casos.evaluador.cargar import cargar_caso  # noqa: E402

    caso = cargar_caso(Path(sys.argv[1]))
    print(json.dumps(evaluar(caso["entrada"]), ensure_ascii=False, indent=2))
