"""Construye el `llamar` que se inyecta en sim.py: hook de aislamiento + backend + control de gasto."""
from __future__ import annotations

from typing import Callable, Mapping

from . import llamar_api
from .aislamiento import verificar_llamada_estudiante


def crear_llamar(tarea: Mapping, *, backend: str = "api", cliente=None, gasto: llamar_api.Gasto | None = None,
                 llamar_claude_p: Callable | None = None, registro: list | None = None) -> Callable:
    """Devuelve una función con la firma de sim.llamar.

    Las llamadas sin `schema` son las de los estudiantes (sim.py solo usa schema en el codificador):
    antes de enviarlas se verifica el aislamiento y, si falla, se lanza AislamientoError sin llamar."""
    if backend not in ("api", "claude_p"):
        raise ValueError(f"backend desconocido: {backend!r} (api | claude_p)")
    if backend == "claude_p" and llamar_claude_p is None:
        raise ValueError("backend claude_p requiere el sim.llamar original")
    gasto = gasto or llamar_api.Gasto()

    def llamar(system, user, model, schema=None, intentos=3):
        rol = "estudiante" if schema is None else "codificador"
        if rol == "estudiante":
            verificar_llamada_estudiante(system, user, tarea)
        gasto.verificar()
        if backend == "api":
            r = llamar_api.llamar(system, user, model, schema=schema, intentos=intentos, cliente=cliente)
        else:
            r = llamar_claude_p(system, user, model, schema=schema, intentos=intentos)
        gasto.sumar(r.get("total_cost_usd"))
        if registro is not None:
            registro.append({"rol": rol, "modelo": model, "costo_usd": r.get("total_cost_usd") or 0.0})
        return r

    return llamar
