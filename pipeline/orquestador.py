"""Máquina de estados del pipeline OTM-Prensa.

    borrador → evaluada → revisada → simulada → con_guia → verificada → publicada

Retrocesos permitidos (ver pipeline/state/decisiones.md):
  evaluada → borrador     iteración diseñador ↔ evaluador; máx. 3 evaluaciones (GOB01 §1)
  con_guia → simulada     el verificador rechaza la guía; se reescribe desde las mismas trazas
  con_guia → evaluada     el verificador encuentra un hallazgo crítico sobre la TAREA (no se arregla rehaciendo
                          la guía): vuelve a la revisión humana 1 con el hallazgo; conserva las trazas, descarta
                          la guía y no cuenta como evaluación (ciclo 2026-10-26)
  verificada → simulada   la revisión humana 2 rechaza la guía
Terminal adicional:
  * → archivada           desde cualquier estado no terminal, con `motivo` (GOB01 §1: la noticia
                          se archiva con su diagnóstico si no alcanza el umbral en 3 iteraciones)

Toda transición valida contra `contratos/` todos los artefactos del expediente (invariante 1).
Llegar a `revisada` o a cualquier estado posterior exige RUB01 ≥ umbral y ningún criterio en 0
(invariante 2). `con_guia` y posteriores exigen que cada escenario cite corridas existentes
(invariante 5). Si se entrega `texto_noticia`, se aplica además la invariante 3.

`transicionar` no modifica su entrada: devuelve un expediente nuevo.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from pipeline import invariantes as inv

# --------------------------------------------------------------------------- estados
ESTADOS = ("borrador", "evaluada", "revisada", "simulada", "con_guia", "verificada", "publicada", "archivada")
TERMINALES = frozenset({"publicada", "archivada"})
MAX_ITERACIONES = 3  # evaluaciones por tarea (GOB01 §1)

_AVANCE = {
    "borrador": {"evaluada"},
    "evaluada": {"revisada", "borrador"},
    "revisada": {"simulada"},
    "simulada": {"con_guia"},
    "con_guia": {"verificada", "simulada", "evaluada"},
    "verificada": {"publicada", "simulada"},
    "publicada": set(),
    "archivada": set(),
}
TRANSICIONES: dict[str, frozenset[str]] = {
    e: frozenset(d | ({"archivada"} if e not in TERMINALES else set())) for e, d in _AVANCE.items()
}

# Artefactos que deben existir al llegar a cada estado.
REQUERIDOS: dict[str, tuple[str, ...]] = {
    "borrador": ("tarea",),
    "evaluada": ("tarea", "evaluacion"),
    "revisada": ("tarea", "evaluacion"),
    "simulada": ("tarea", "evaluacion", "trazas_resumen"),
    "con_guia": ("tarea", "evaluacion", "trazas_resumen", "guia"),
    "verificada": ("tarea", "evaluacion", "trazas_resumen", "guia"),
    "publicada": ("tarea", "evaluacion", "trazas_resumen", "guia"),
    "archivada": ("tarea",),
}
# Contrato de cada artefacto del expediente.
CONTRATO_DE = {
    "noticia": "noticia",
    "tarea": "tarea",
    "evaluacion": "evaluacion",
    "trazas_resumen": "trazas_resumen",
    "guia": "guia",
}
_POST_REVISION = frozenset({"revisada", "simulada", "con_guia", "verificada", "publicada"})
_CON_GUIA = frozenset({"con_guia", "verificada", "publicada"})
_REQUIEREN_REVISOR = frozenset({"revisada", "publicada"})  # revisiones humanas 1 y 2 (GOB01 §2)
# Al retroceder se descarta el artefacto que hay que rehacer.
_DESCARTA_AL_VOLVER = {"borrador": ("evaluacion",), "simulada": ("guia",), "evaluada": ("guia",)}


# --------------------------------------------------------------------------- errores
class ErrorOrquestador(Exception):
    """Base de los errores del orquestador."""


class TransicionIlegal(ErrorOrquestador):
    """La transición no existe en la máquina de estados."""


class LimiteIteraciones(TransicionIlegal):
    """Se agotaron las iteraciones diseñador ↔ evaluador; solo cabe archivar."""


class InvarianteViolada(ErrorOrquestador):
    """Alguna invariante de CLAUDE.md no se cumple; la transición no ocurre."""

    def __init__(self, mensaje: str, errores: tuple[str, ...] = ()):
        self.errores = tuple(errores)
        super().__init__(mensaje + ("".join(f"\n  - {e}" for e in self.errores)))


class ArtefactoInvalido(InvarianteViolada):
    """Invariante 1: un artefacto no valida contra su contrato."""


class UmbralRUB01NoCumplido(InvarianteViolada):
    """Invariante 2: RUB01 bajo el umbral o con un criterio en 0."""


# --------------------------------------------------------------------------- expediente
@dataclass
class Expediente:
    tarea_id: str
    estado: str = "borrador"
    iteraciones: int = 0  # evaluaciones realizadas
    artefactos: dict[str, Any] = field(default_factory=dict)
    historial: list[dict[str, Any]] = field(default_factory=list)
    # Anotaciones del ciclo que no son artefactos con contrato (p. ej. `evaluacion_inestable`,
    # rechazos del verificador, costos por agente). No pasan por la validación de contratos ni
    # cambian el estado; las escribe pipeline/ciclo.py y las lee la revisión humana.
    marcas: dict[str, Any] = field(default_factory=dict)

    def a_dict(self) -> dict:
        return {
            "tarea_id": self.tarea_id,
            "estado": self.estado,
            "iteraciones": self.iteraciones,
            "artefactos": self.artefactos,
            "historial": self.historial,
            "marcas": self.marcas,
        }

    @classmethod
    def desde_dict(cls, d: Mapping[str, Any]) -> "Expediente":
        return cls(**copy.deepcopy(dict(d)))


def _ahora(ahora: datetime | None) -> str:
    return (ahora or datetime.now(timezone.utc)).isoformat(timespec="seconds")


def nuevo_expediente(tarea: Mapping[str, Any], noticia: Mapping[str, Any] | None = None,
                     *, ahora: datetime | None = None) -> Expediente:
    """Abre un expediente en `borrador`. La tarea (y la noticia, si se da) deben validar."""
    tarea = copy.deepcopy(dict(tarea))
    tarea["estado"] = "borrador"
    artefactos: dict[str, Any] = {"tarea": tarea}
    if noticia is not None:
        artefactos["noticia"] = copy.deepcopy(dict(noticia))
    _validar_artefactos(artefactos)
    return Expediente(
        tarea_id=tarea["id"],
        artefactos=artefactos,
        historial=[{"fecha": _ahora(ahora), "de": None, "a": "borrador"}],
    )


# --------------------------------------------------------------------------- comprobaciones
def _validar_artefactos(artefactos: Mapping[str, Any]) -> None:
    errores: list[str] = []
    for nombre, art in artefactos.items():
        contrato = CONTRATO_DE.get(nombre)
        if contrato is None:
            errores.append(f"artefacto sin contrato: {nombre!r}")
            continue
        errores.extend(inv.validar_contra_esquema(art, contrato).errores)
    if errores:
        raise ArtefactoInvalido("Invariante 1: artefactos inválidos", tuple(errores))


def _comprobar_coherencia(art: Mapping[str, Any], tarea_id: str) -> None:
    errores = [
        f"{n}.tarea_id={art[n]['tarea_id']!r} ≠ {tarea_id!r}"
        for n in ("evaluacion", "trazas_resumen", "guia")
        if n in art and art[n].get("tarea_id") != tarea_id
    ]
    if art["tarea"]["id"] != tarea_id:
        errores.append(f"tarea.id={art['tarea']['id']!r} ≠ {tarea_id!r}")
    if errores:
        raise InvarianteViolada("Artefactos de tareas distintas en el mismo expediente", tuple(errores))


def puede_transicionar(origen: str, destino: str) -> bool:
    return destino in TRANSICIONES.get(origen, frozenset())


# --------------------------------------------------------------------------- transición
def transicionar(
    exp: Expediente,
    destino: str,
    *,
    artefactos: Mapping[str, Any] | None = None,
    revisor: str | None = None,
    motivo: str | None = None,
    texto_noticia: str | None = None,
    ahora: datetime | None = None,
) -> Expediente:
    """Devuelve un expediente nuevo en `destino` o lanza una subclase de ErrorOrquestador.

    `artefactos`: artefactos nuevos o actualizados que acompañan la transición
    (p. ej. {"evaluacion": ...} al pasar a `evaluada`).
    `revisor`: obligatorio para `revisada` y `publicada` (revisiones humanas, GOB01 §2).
    `motivo`: obligatorio para `archivada`.
    `texto_noticia`: si se entrega, se exige la invariante 3 sobre todos los artefactos.
    """
    origen = exp.estado
    if destino not in ESTADOS:
        raise TransicionIlegal(f"Estado desconocido: {destino!r}")
    if not puede_transicionar(origen, destino):
        permitidos = sorted(TRANSICIONES.get(origen, ()))
        raise TransicionIlegal(f"{origen} → {destino} no está permitida (desde {origen}: {permitidos})")

    nuevo = Expediente.desde_dict(exp.a_dict())
    art = nuevo.artefactos
    for nombre in _DESCARTA_AL_VOLVER.get(destino, ()):
        if ESTADOS.index(destino) < ESTADOS.index(origen):
            art.pop(nombre, None)
    if artefactos:
        art.update(copy.deepcopy(dict(artefactos)))

    # Iteraciones diseñador ↔ evaluador (volver de con_guia a evaluada no es una evaluación nueva)
    if destino == "evaluada" and origen == "borrador":
        if nuevo.iteraciones >= MAX_ITERACIONES:
            raise LimiteIteraciones(f"{MAX_ITERACIONES} evaluaciones agotadas; solo cabe archivar")
        nuevo.iteraciones += 1
    if destino == "borrador" and nuevo.iteraciones >= MAX_ITERACIONES:
        raise LimiteIteraciones(
            f"{MAX_ITERACIONES} evaluaciones agotadas; evaluada → borrador ya no se permite, solo archivar"
        )

    # Requisitos de la transición
    if faltan := [n for n in REQUERIDOS[destino] if n not in art]:
        raise InvarianteViolada(f"Faltan artefactos para {destino}: {faltan}")
    if destino in _REQUIEREN_REVISOR and not (revisor and revisor.strip()):
        raise InvarianteViolada(f"{destino} requiere `revisor` (revisión humana, GOB01 §2)")
    if destino == "archivada" and not (motivo and motivo.strip()):
        raise InvarianteViolada("archivada requiere `motivo` (diagnóstico)")

    # El orquestador mantiene el estado y el resumen RUB01 dentro de la tarea
    art["tarea"]["estado"] = destino
    if destino == "evaluada" and "evaluacion" in art:
        rub = art["evaluacion"].get("rub01", {})
        crit = rub.get("criterios", {})
        if isinstance(crit, dict) and all(isinstance(c, dict) and "puntaje" in c for c in crit.values()):
            art["tarea"]["rubrica_rub01"] = {
                "total": rub.get("total"),
                "por_criterio": {k: c["puntaje"] for k, c in crit.items()},
            }

    # Invariante 1: todo artefacto presente valida contra su contrato
    _validar_artefactos(art)
    _comprobar_coherencia(art, nuevo.tarea_id)

    # Invariante 2
    if destino in _POST_REVISION:
        r = inv.cumple_umbral_rub01(art["evaluacion"])
        if not r:
            raise UmbralRUB01NoCumplido(f"Invariante 2: {origen} → {destino} bloqueada", r.errores)

    # Consistencia de trazas e invariante 5
    if "trazas_resumen" in art and destino in _POST_REVISION:
        r = inv.consistencia_trazas(art["trazas_resumen"])
        if not r:
            raise InvarianteViolada("trazas_resumen inconsistente", r.errores)
    if destino in _CON_GUIA:
        r = inv.escenarios_respaldados(art["guia"], art["trazas_resumen"])
        if not r:
            raise InvarianteViolada("Invariante 5: escenarios sin corrida que los respalde", r.errores)
    if destino == "publicada" and not art["guia"]["trazabilidad"].get("revision_humana_2"):
        raise InvarianteViolada("publicada requiere guia.trazabilidad.revision_humana_2")

    # Invariante 3 (solo si se dispone del texto de la noticia; no se guarda en el repo)
    if texto_noticia:
        r = inv.cumple_limite_literal({k: v for k, v in art.items()}, texto_noticia)
        if not r:
            raise InvarianteViolada("Invariante 3: texto literal de la noticia", r.errores)

    entrada = {"fecha": _ahora(ahora), "de": origen, "a": destino}
    if revisor:
        entrada["revisor"] = revisor
    if motivo:
        entrada["motivo"] = motivo
    if destino == "evaluada" and origen == "borrador":
        entrada["iteracion"] = nuevo.iteraciones
        entrada["rub01_total"] = art["evaluacion"]["rub01"]["total"]
    nuevo.estado = destino
    nuevo.historial.append(entrada)
    return nuevo


# --------------------------------------------------------------------------- persistencia
DIR_EXPEDIENTES = inv.RAIZ / "pipeline" / "state" / "expedientes"


def guardar(exp: Expediente, directorio: Path = DIR_EXPEDIENTES) -> Path:
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / f"{exp.tarea_id}.json"
    ruta.write_text(json.dumps(exp.a_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ruta


def cargar(tarea_id: str, directorio: Path = DIR_EXPEDIENTES) -> Expediente:
    ruta = directorio / f"{tarea_id}.json"
    return Expediente.desde_dict(json.loads(ruta.read_text(encoding="utf-8")))
