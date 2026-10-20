"""Cliente común de la API para los agentes del pipeline.

Uso:
    from pipeline.llm import llamar, costo_usd, modelo_de
    r = llamar(agente="filtro", system=PROMPT, user=texto, schema=ESQUEMA)
    r["salida"]   # dict (si hubo schema) o str
    r["meta"]     # modelo, request_id, uso, costo_usd, fecha, intentos

Reglas (ver pipeline/state/decisiones.md):
- La clave se obtiene solo con pipeline.apikey.api_key.
- Los modelos 5.5 rechazan `temperature` distinto del default: no se envía.
- La salida estructurada se fuerza con output_config.format (json_schema); no hay tool_choice forzado.
- El costo se calcula con la tabla `precios_modelos` de pipeline/config.yaml.
- En tests se inyecta `cliente` (un objeto con .messages.create) para no gastar.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

CONFIG_PATH = RAIZ / "pipeline" / "config.yaml"
CLAVES_USO = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


@lru_cache(maxsize=1)
def config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def modelo_de(agente: str) -> str:
    return config()["modelos"][agente]


def costo_usd(uso: dict, modelo: str) -> float:
    p = config()["precios_modelos"][modelo]
    return round(
        uso.get("input_tokens", 0) * p["input"] / 1e6
        + uso.get("output_tokens", 0) * p["output"] / 1e6
        + uso.get("cache_creation_input_tokens", 0) * p["cache_write"] / 1e6
        + uso.get("cache_read_input_tokens", 0) * p["cache_read"] / 1e6,
        6,
    )


def llamar(*, agente: str, system: str, user: str, schema: dict | None = None,
           modelo: str | None = None, esfuerzo: str | None = None, max_tokens: int = 16000,
           cachear_system: bool = True, cliente=None, reintentos: int = 2) -> dict:
    """Una llamada a la API con el contrato (system, user, model, schema) de sim.py/llamar().

    Reintenta ante errores transitorios y ante JSON inválido o stop_reason distinto de end_turn.
    Devuelve {"salida": dict|str, "meta": {...}}. Si falla, lanza RuntimeError con .costo_usd."""
    modelo = modelo or modelo_de(agente)
    if cliente is None:
        import anthropic
        from pipeline.apikey import api_key
        cliente = anthropic.Anthropic(api_key=api_key())
    bloque = {"type": "text", "text": system}
    if cachear_system:
        bloque["cache_control"] = {"type": "ephemeral"}
    kwargs = dict(model=modelo, max_tokens=max_tokens, system=[bloque],
                  messages=[{"role": "user", "content": user}])
    output_config = {}
    if schema is not None:
        output_config["format"] = {"type": "json_schema", "schema": schema}
    if esfuerzo:
        output_config["effort"] = esfuerzo
    if output_config:
        kwargs["output_config"] = output_config

    uso = dict.fromkeys(CLAVES_USO, 0)
    ultimo_error: Exception | None = None
    for intento in range(reintentos + 1):
        t0 = time.time()
        try:
            r = cliente.messages.create(**kwargs)
        except Exception as e:  # noqa: BLE001 — se distingue abajo
            if type(e).__name__ in ("RateLimitError", "APIConnectionError", "InternalServerError",
                                    "APITimeoutError", "OverloadedError"):
                ultimo_error = e
                time.sleep(10 * (intento + 1))
                continue
            raise
        for k in CLAVES_USO:
            uso[k] += getattr(r.usage, k, 0) or 0
        texto = "".join(b.text for b in r.content if getattr(b, "type", None) == "text")
        try:
            if r.stop_reason != "end_turn":
                raise ValueError(f"stop_reason={r.stop_reason}")
            salida = json.loads(texto) if schema is not None else texto
        except (ValueError, json.JSONDecodeError) as e:
            ultimo_error = e
            continue
        meta = {
            "agente": agente,
            "modelo": modelo,
            "modelo_respuesta": getattr(r, "model", modelo),
            "request_id": getattr(r, "_request_id", None),
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "segundos": round(time.time() - t0, 1),
            "intentos": intento + 1,
            "parametros": {"temperature": "default (los modelos 5.5 no la admiten)",
                           "effort": esfuerzo or "default", "max_tokens": max_tokens},
            "uso": uso,
            "costo_usd": costo_usd(uso, modelo),
        }
        return {"salida": salida, "meta": meta}
    err = RuntimeError(f"{agente}: la llamada falló tras {reintentos + 1} intentos: {ultimo_error}")
    err.costo_usd = costo_usd(uso, modelo)
    raise err


class ClienteFalso:
    """Cliente de prueba: devuelve respuestas fijas en orden. Para tests sin red ni gasto."""

    def __init__(self, respuestas: list):
        self._respuestas = list(respuestas)
        self.llamadas: list[dict] = []
        self.messages = self

    def create(self, **kwargs):
        from types import SimpleNamespace as NS
        self.llamadas.append(kwargs)
        resp = self._respuestas.pop(0)
        texto = resp if isinstance(resp, str) else json.dumps(resp, ensure_ascii=False)
        return NS(content=[NS(type="text", text=texto)], stop_reason="end_turn", model=kwargs["model"],
                  usage=NS(input_tokens=1000, output_tokens=200, cache_creation_input_tokens=0,
                           cache_read_input_tokens=0))
