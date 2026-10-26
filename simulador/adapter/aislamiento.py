"""Hook de aislamiento (invariante 6).

Antes de cada llamada de un estudiante simulado se comprueba que lo que se envía contiene solo la
vista de estudiante (enunciado_es, foto_descripcion, recursos_a_solicitud) y nada del `task_space`.
Se apoya en pipeline.invariantes.vista_estudiante / verificar_aislamiento. Lanza AislamientoError.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from pipeline.invariantes import palabras_normalizadas, textos_de, verificar_aislamiento, vista_estudiante

MARCA_CONVERSACION = "CONVERSACIÓN HASTA AHORA:"   # student_turn de INS09
UMBRAL_PALABRAS_COMUNES = 12  # tramo de palabras (no numéricas) de task_space que, copiado, cuenta como filtración
_TOKENS = re.compile(r"task_space|reference_solution|required_assumptions|validation_evidence|"
                     r"modelo_inadecuado|mapa_ciclo|recursos_de_entrada|agent_visibility", re.I)


class AislamientoError(RuntimeError):
    """Se intentó entregar a un estudiante algo fuera de su vista."""


def verificar_payload_estudiante(payload: Mapping[str, Any], tarea: Mapping[str, Any] | None = None) -> None:
    """El payload estructurado destinado a estudiantes debe cumplir verificar_aislamiento."""
    r = verificar_aislamiento(payload, tarea)
    if not r:
        raise AislamientoError("aislamiento (invariante 6): " + "; ".join(r.errores))


def _palabras(texto: str) -> list[str]:
    """Palabras normalizadas sin los tokens puramente numéricos: «64.256.232» o «124.082.273» son datos del
    enunciado o cálculos de los estudiantes, no texto de task_space (falso positivo del 2026-10-26)."""
    return [w for w in palabras_normalizadas(texto) if not w.isdigit()]


def _ngramas(palabras: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(palabras[i:i + n]) for i in range(len(palabras) - n + 1)}


def verificar_llamada_estudiante(system: str, user: str, tarea: Mapping[str, Any]) -> None:
    """Comprueba el texto real de una llamada de estudiante (system + user).

    1. La vista de estudiante de la tarea cumple verificar_aislamiento contra su task_space.
    2. En toda la llamada (incluida la conversación) no aparece ninguna clave reservada de task_space.
    3. Solo en las ENTRADAS que pone el pipeline (system y la parte de `user` anterior a la conversación):
       ninguna cadena (>= 20 caracteres) ni tramo (>= 12 palabras no numéricas) del task_space que no esté ya
       en enunciado_es, foto_descripcion o recursos a solicitud.

    La conversación no se compara con task_space: la escriben los propios estudiantes desde su vista, y es
    natural que lleguen a la misma suma que la solución de referencia (que-tan-renida-fue, 2026-10-26). Si las
    entradas no filtran nada, la conversación tampoco puede filtrarlo."""
    verificar_payload_estudiante(vista_estudiante(tarea), tarea)
    estatico, _, conversacion = user.partition(MARCA_CONVERSACION)
    vista = vista_estudiante(tarea)
    permitidos = [vista["enunciado_es"], vista["foto_descripcion"]] + [r["contenido"] for r in vista["recursos_a_solicitud"]]
    estatico = f"{system}\n{estatico}"
    for p in sorted(permitidos, key=len, reverse=True):
        if p:
            estatico = estatico.replace(p, " ")
    errores = []
    if m := _TOKENS.search(f"{estatico}\n{conversacion}"):
        errores.append(f"clave reservada «{m.group(0)}» en la llamada del estudiante")
    ts = tarea.get("task_space")
    if ts is not None:
        texto_permitido = "\n".join(permitidos)
        for t in textos_de(ts):
            if len(t) >= 20 and t in estatico and t not in texto_permitido:
                errores.append(f"texto de task_space en la llamada del estudiante: «{t[:60]}»")
        n = UMBRAL_PALABRAS_COMUNES
        ya_vistos = _ngramas(_palabras(texto_permitido), n)
        de_ts = set().union(*(_ngramas(_palabras(t), n) for t in textos_de(ts))) - ya_vistos
        if fuga := sorted(_ngramas(_palabras(estatico), n) & de_ts):
            errores.append(f"{n} o más palabras consecutivas de task_space en las entradas del estudiante: "
                           f"«{' '.join(fuga[0])[:80]}»")
    if errores:
        raise AislamientoError("aislamiento (invariante 6): " + "; ".join(errores))
