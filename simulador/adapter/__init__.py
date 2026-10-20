"""Adapter entre el pipeline OTM-Prensa y el simulador externo (SIM01 v0.1).

generar      TAREA.md / PERFILES.md / PROMPTS.md desde una tarea PLT01
lanzador     corre las 6 corridas con sim.py parcheado en tiempo de ejecución (sin editarlo)
llamar_api   port de sim.llamar() a la API (backend `api`); `claude_p` conserva la original
aislamiento  hook de la invariante 6
traductor    *_cod.json -> trazas_resumen
"""
from .aislamiento import AislamientoError, verificar_llamada_estudiante, verificar_payload_estudiante  # noqa: F401
