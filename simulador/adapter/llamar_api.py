"""Port de `sim.llamar()` a la API de Anthropic (GOB01 §3).

Mismo contrato que `sim.llamar(system, user, model, schema=None, intentos=3)` y mismo tipo de retorno
que el JSON de `claude -p --output-format json` en las claves que usa sim.py:
    result            texto de la respuesta (con schema: el JSON como texto)
    structured_output dict si hubo schema, si no None
    total_cost_usd    costo calculado con pipeline/llm.py (tabla precios_modelos de config.yaml)
    is_error          False (los fallos lanzan RuntimeError, como sim.llamar)
Extras (sim.py los ignora): usage, model, request_id.

La clave se obtiene en pipeline.llm vía pipeline.apikey (OTM_API_KEY, luego ANTHROPIC_API_KEY).
Se conserva la versión `claude -p` (sim.llamar original) como backend `claude_p`; ver lanzador.
"""
from __future__ import annotations

import json
import threading

from pipeline.llm import llamar as _llamar_llm

MAX_TOKENS_ESTUDIANTE = 2000   # turnos de máximo 2 oraciones
MAX_TOKENS_CODIFICADOR = 16000


def esquema_estricto(schema):
    """Copia del esquema con `additionalProperties: false` en cada objeto.

    La API de salida estructurada lo exige; los esquemas de INS09 (coder_schema) no lo traen. Es solo
    una adaptación de transporte: no cambia lo que el codificador puede devolver."""
    if isinstance(schema, dict):
        out = {k: esquema_estricto(v) for k, v in schema.items()}
        tipo = out.get("type")
        if (tipo == "object" or (isinstance(tipo, list) and "object" in tipo)) and "additionalProperties" not in out:
            out["additionalProperties"] = False
        return out
    if isinstance(schema, list):
        return [esquema_estricto(v) for v in schema]
    return schema


def llamar(system: str, user: str, model: str, schema: dict | None = None, intentos: int = 3,
           *, cliente=None, agente: str = "simulador") -> dict:
    r = _llamar_llm(
        agente=agente, system=system, user=user, schema=esquema_estricto(schema) if schema else None, modelo=model,
        max_tokens=MAX_TOKENS_CODIFICADOR if schema else MAX_TOKENS_ESTUDIANTE,
        cachear_system=schema is None,   # el system del estudiante se repite en cada turno
        cliente=cliente, reintentos=max(intentos - 1, 0),
    )
    salida, meta = r["salida"], r["meta"]
    return {
        "result": json.dumps(salida, ensure_ascii=False) if schema else salida,
        "structured_output": salida if schema else None,
        "total_cost_usd": meta["costo_usd"],
        "is_error": False,
        "usage": meta["uso"],
        "model": meta["modelo_respuesta"],
        "request_id": meta["request_id"],
    }


class Gasto:
    """Acumula el costo de las llamadas y corta al superar el tope (USD)."""

    def __init__(self, tope_usd: float | None = None, ledger=None):
        self.tope = tope_usd
        self.ledger = ledger   # archivo .jsonl donde se anota cada llamada (auditoría del gasto real)
        self.total = 0.0
        self.llamadas = 0
        self._lock = threading.Lock()

    def verificar(self) -> None:
        with self._lock:
            if self.tope is not None and self.total >= self.tope:
                raise RuntimeError(f"tope de gasto alcanzado: {self.total:.3f} >= {self.tope} USD")

    def sumar(self, usd: float | None) -> None:
        with self._lock:
            self.total += usd or 0.0
            self.llamadas += 1
            if self.ledger is not None:
                with open(self.ledger, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"n": self.llamadas, "usd": usd or 0.0, "acumulado": round(self.total, 6)}) + chr(10))
