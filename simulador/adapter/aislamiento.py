"""Hook de aislamiento (invariante 6).

Antes de cada llamada de un estudiante simulado se comprueba que lo que se envía contiene solo la
vista de estudiante (enunciado_es, foto_descripcion, recursos_a_solicitud) y nada del `task_space`.
Se apoya en pipeline.invariantes.vista_estudiante / verificar_aislamiento. Lanza AislamientoError.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from pipeline.invariantes import (max_palabras_consecutivas_comunes, textos_de, verificar_aislamiento,
                                  vista_estudiante)

MARCA_CONVERSACION = "CONVERSACIÓN HASTA AHORA:"   # student_turn de INS09
UMBRAL_PALABRAS_COMUNES = 12  # tramo de palabras de task_space que, copiado, cuenta como filtración
_TOKENS = re.compile(r"task_space|reference_solution|required_assumptions|validation_evidence|"
                     r"modelo_inadecuado|mapa_ciclo|recursos_de_entrada|agent_visibility", re.I)


class AislamientoError(RuntimeError):
    """Se intentó entregar a un estudiante algo fuera de su vista."""


def verificar_payload_estudiante(payload: Mapping[str, Any], tarea: Mapping[str, Any] | None = None) -> None:
    """El payload estructurado destinado a estudiantes debe cumplir verificar_aislamiento."""
    r = verificar_aislamiento(payload, tarea)
    if not r:
        raise AislamientoError("aislamiento (invariante 6): " + "; ".join(r.errores))


def verificar_llamada_estudiante(system: str, user: str, tarea: Mapping[str, Any]) -> None:
    """Comprueba el texto real de una llamada de estudiante (system + user).

    1. La vista de estudiante de la tarea cumple verificar_aislamiento contra su task_space.
    2. Descontados los textos de la vista, el resto no menciona claves de task_space ni copia
       cadenas (>= 20 caracteres) ni tramos (>= 12 palabras) del task_space."""
    verificar_payload_estudiante(vista_estudiante(tarea), tarea)
    # Lo que escriben los estudiantes (conversación) no se compara por cadenas cortas: es natural que
    # digan "velocidad por tiempo". Sí se comparan claves reservadas y tramos largos (>= 12 palabras).
    estatico, _, conversacion = user.partition(MARCA_CONVERSACION)
    vista = vista_estudiante(tarea)
    permitidos = [vista["enunciado_es"], vista["foto_descripcion"]] + [r["contenido"] for r in vista["recursos_a_solicitud"]]
    estatico = f"{system}\n{estatico}"
    for p in sorted(permitidos, key=len, reverse=True):
        if p:
            estatico = estatico.replace(p, " ")
    resto = f"{estatico}\n{conversacion}"
    errores = []
    if m := _TOKENS.search(resto):
        errores.append(f"clave reservada «{m.group(0)}» en la llamada del estudiante")
    ts = tarea.get("task_space")
    if ts is not None:
        for t in textos_de(ts):
            if len(t) >= 20 and t in estatico:
                errores.append(f"texto de task_space en la llamada del estudiante: «{t[:60]}»")
        n, tramo = max_palabras_consecutivas_comunes(resto, " ".join(textos_de(ts)))
        if n >= UMBRAL_PALABRAS_COMUNES:
            errores.append(f"{n} palabras consecutivas de task_space en la llamada: «{tramo[:80]}»")
    if errores:
        raise AislamientoError("aislamiento (invariante 6): " + "; ".join(errores))
