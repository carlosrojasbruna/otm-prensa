"""Invariantes de CLAUDE.md como funciones puras reutilizables por hooks y por el orquestador.

Cada función recibe datos ya cargados y devuelve un `Resultado` (verdadero si cumple) sin
efectos secundarios. Las únicas lecturas de disco son los contratos (`contratos/`) y los
insumos de solo lectura (RUB01, MED01), cacheadas y deterministas; ambas se pueden inyectar
por parámetro en las funciones que las usan.

Invariantes cubiertas:
  1. validar_contra_esquema(artefacto, nombre_contrato)
  2. cumple_umbral_rub01(evaluacion)            (umbral leído de insumos/rubricas/RUB01_*.json)
  3. cumple_limite_literal(texto, fuente)        (> 25 palabras consecutivas de la noticia)
  5. escenarios_respaldados(guia, trazas)
  6. vista_estudiante(tarea) / verificar_aislamiento(payload)
Auxiliares: consistencia_rub01, consistencia_trazas, medio_en_lista_blanca.

Uso desde un hook (código de salida 0 = cumple, 2 = bloquea):
  python -m pipeline.invariantes esquema <contrato> <archivo.json>
  python -m pipeline.invariantes umbral <evaluacion.json>
  python -m pipeline.invariantes literal <archivo> <texto_noticia.txt> [limite]
  python -m pipeline.invariantes aislamiento <payload.json>
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

RAIZ = Path(__file__).resolve().parents[1]
DIR_CONTRATOS = RAIZ / "contratos"
DIR_RUBRICAS = RAIZ / "insumos" / "rubricas"
DIR_MEDIOS = RAIZ / "insumos" / "medios"
BASE_ID = "https://otm-prensa.example/contratos/"

LIMITE_PALABRAS_LITERALES = 25  # CLAUDE.md invariante 3 / GOB01 §4

CONTRATOS = (
    "noticia",
    "tarea",
    "evaluacion",
    "evaluacion_rub01",
    "trazas_resumen",
    "guia",
    "catalogo",
)


# --------------------------------------------------------------------------- resultado
@dataclass(frozen=True)
class Resultado:
    """Resultado de una invariante. Es verdadero si y solo si la invariante se cumple."""

    valido: bool
    errores: tuple[str, ...] = ()
    detalle: Mapping[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.valido

    @classmethod
    def desde_errores(cls, errores: Iterable[str], **detalle: Any) -> "Resultado":
        errores = tuple(errores)
        return cls(valido=not errores, errores=errores, detalle=detalle)


# --------------------------------------------------------------------------- invariante 1
@lru_cache(maxsize=1)
def _registro() -> Registry:
    recursos = []
    for ruta in sorted(DIR_CONTRATOS.glob("*.schema.json")):
        esquema = json.loads(ruta.read_text(encoding="utf-8"))
        recursos.append((esquema["$id"], Resource.from_contents(esquema, default_specification=DRAFT202012)))
    return Registry().with_resources(recursos)


def cargar_esquema(nombre_contrato: str) -> dict:
    """Devuelve el esquema `contratos/<nombre>.schema.json` (sin fragmento)."""
    base = nombre_contrato.split("#", 1)[0]
    ruta = DIR_CONTRATOS / f"{base}.schema.json"
    if not ruta.exists():
        raise KeyError(f"Contrato desconocido: {nombre_contrato!r} (no existe {ruta.name})")
    return json.loads(ruta.read_text(encoding="utf-8"))


@lru_cache(maxsize=64)
def _validador(nombre_contrato: str) -> Draft202012Validator:
    base, _, fragmento = nombre_contrato.partition("#")
    cargar_esquema(base)  # error claro si no existe
    uri = BASE_ID + f"{base}.schema.json" + (f"#{fragmento}" if fragmento else "")
    return Draft202012Validator({"$ref": uri}, registry=_registro(), format_checker=FormatChecker())


def validar_contra_esquema(artefacto: Any, nombre_contrato: str) -> Resultado:
    """Invariante 1. Valida `artefacto` contra `contratos/<nombre_contrato>.schema.json`.

    `nombre_contrato` admite un fragmento JSON Pointer, p. ej. "catalogo#/$defs/entrada".
    """
    validador = _validador(nombre_contrato)
    errores = []
    for e in sorted(validador.iter_errors(artefacto), key=lambda e: list(e.absolute_path)):
        ruta = "/".join(str(p) for p in e.absolute_path) or "(raíz)"
        mensaje = e.message if len(e.message) <= 300 else e.message[:297] + "..."
        errores.append(f"{nombre_contrato}: {ruta}: {mensaje}")
    return Resultado.desde_errores(errores, contrato=nombre_contrato)


# --------------------------------------------------------------------------- invariante 2
def _version_de_archivo(ruta: Path) -> tuple[int, ...]:
    m = re.search(r"_v(\d+(?:\.\d+)*)_", ruta.name)
    return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)


@lru_cache(maxsize=8)
def cargar_rub01(version: str | None = None) -> dict:
    """Lee RUB01 desde insumos/rubricas/. Si `version` es None, la versión más alta."""
    rutas = sorted(DIR_RUBRICAS.glob("RUB01_*.json"), key=_version_de_archivo)
    if not rutas:
        raise FileNotFoundError(f"No hay RUB01_*.json en {DIR_RUBRICAS}")
    for ruta in reversed(rutas):
        rub = json.loads(ruta.read_text(encoding="utf-8"))
        if version is None or rub.get("version") == version:
            return rub
    raise LookupError(f"No existe RUB01 versión {version!r} en {DIR_RUBRICAS}")


def umbral_rub01(rubrica: Mapping[str, Any]) -> tuple[int, int]:
    """(total_min, puntaje_prohibido) desde RUB01.umbral_publicacion_propuesto."""
    u = rubrica["umbral_publicacion_propuesto"]
    return int(u["total_min"]), int(u["ningun_criterio_en"])


def _bloque_rub01(evaluacion: Mapping[str, Any]) -> Mapping[str, Any]:
    return evaluacion["rub01"] if "rub01" in evaluacion else evaluacion


def consistencia_rub01(rub01: Mapping[str, Any]) -> Resultado:
    """Reglas no expresables en JSON Schema: total = suma; una mejora por cada criterio < 2 y solo para ellos."""
    errores = []
    criterios = rub01.get("criterios", {})
    suma = sum(int(c["puntaje"]) for c in criterios.values())
    if rub01.get("total") != suma:
        errores.append(f"total declarado {rub01.get('total')} ≠ suma de criterios {suma}")
    bajos = {k for k, c in criterios.items() if c["puntaje"] < 2}
    con_mejora = [m["criterio"] for m in rub01.get("mejoras", [])]
    if len(con_mejora) != len(set(con_mejora)):
        errores.append("criterio repetido en mejoras")
    if faltan := sorted(bajos - set(con_mejora)):
        errores.append(f"faltan mejoras para criterios en 0 o 1: {faltan}")
    if sobran := sorted(set(con_mejora) - bajos):
        errores.append(f"mejoras para criterios con puntaje 2: {sobran}")
    return Resultado.desde_errores(errores, suma=suma)


def cumple_umbral_rub01(evaluacion: Mapping[str, Any], rubrica: Mapping[str, Any] | None = None) -> Resultado:
    """Invariante 2. Verdadero si total ≥ umbral y ningún criterio tiene el puntaje prohibido.

    Acepta evaluacion.json completo o solo el bloque `rub01`. El umbral se lee de la RUB01
    cuya versión coincide con `version_rubrica` (o de `rubrica`, si se inyecta). El total se
    recalcula desde los criterios: un total declarado inconsistente no cumple.
    """
    rub01 = _bloque_rub01(evaluacion)
    esquema = validar_contra_esquema(rub01, "evaluacion_rub01")
    if not esquema:
        return Resultado.desde_errores(("rub01 no valida contra su esquema",) + esquema.errores)
    if rubrica is None:
        try:
            rubrica = cargar_rub01(rub01["version_rubrica"])
        except LookupError as e:
            return Resultado.desde_errores([str(e)])
    ids = {c["id"] for c in rubrica["criterios"]}
    total_min, prohibido = umbral_rub01(rubrica)
    errores = []
    if set(rub01["criterios"]) != ids:
        errores.append(f"criterios no coinciden con RUB01 {rubrica['version']}")
    errores.extend(consistencia_rub01(rub01).errores)
    suma = sum(int(c["puntaje"]) for c in rub01["criterios"].values())
    en_prohibido = sorted(k for k, c in rub01["criterios"].items() if c["puntaje"] == prohibido)
    if suma < total_min:
        errores.append(f"RUB01 {suma}/{rubrica['puntaje_maximo']} < umbral {total_min}")
    if en_prohibido:
        errores.append(f"criterios en {prohibido}: {en_prohibido}")
    return Resultado.desde_errores(
        errores, total=suma, total_min=total_min, criterios_en_prohibido=en_prohibido
    )


# --------------------------------------------------------------------------- invariante 3
_PALABRA = re.compile(r"\w+", re.UNICODE)


def palabras_normalizadas(texto: str) -> list[str]:
    """Minúsculas, sin tildes ni puntuación: compara de la forma más estricta posible."""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return _PALABRA.findall(sin_tildes.casefold())


def max_palabras_consecutivas_comunes(texto: str, fuente: str) -> tuple[int, str]:
    """Longitud del tramo más largo de palabras consecutivas de `fuente` que aparece en `texto`,
    y el tramo (normalizado). Subcadena común más larga sobre palabras, O(n·m) en memoria O(m)."""
    a, b = palabras_normalizadas(texto), palabras_normalizadas(fuente)
    mejor, fin = 0, 0
    previo = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        actual = [0] * (len(b) + 1)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            if ai == b[j - 1]:
                v = previo[j - 1] + 1
                actual[j] = v
                if v > mejor:
                    mejor, fin = v, i
        previo = actual
    return mejor, " ".join(a[fin - mejor : fin])


def textos_de(artefacto: Any) -> Iterator[str]:
    """Todas las cadenas de un artefacto JSON (valores y no claves), en orden."""
    if isinstance(artefacto, str):
        yield artefacto
    elif isinstance(artefacto, Mapping):
        for v in artefacto.values():
            yield from textos_de(v)
    elif isinstance(artefacto, (list, tuple)):
        for v in artefacto:
            yield from textos_de(v)


def cumple_limite_literal(
    texto: Any, fuente: str, limite: int = LIMITE_PALABRAS_LITERALES
) -> Resultado:
    """Invariante 3. `texto` (cadena o artefacto JSON) no contiene más de `limite` palabras
    consecutivas de `fuente` (texto de la noticia). Las cadenas del artefacto se concatenan en
    orden, de modo que también se detectan copias partidas entre campos contiguos."""
    peor, tramo = max_palabras_consecutivas_comunes(" ".join(textos_de(texto)), fuente)
    errores = [f"{peor} palabras consecutivas de la noticia (> {limite}): «{tramo}»"] if peor > limite else []
    return Resultado.desde_errores(errores, max_consecutivas=peor)


# --------------------------------------------------------------------------- invariante 5
def consistencia_trazas(trazas: Mapping[str, Any]) -> Resultado:
    errores = []
    ids = [c["id"] for c in trazas.get("por_corrida", [])]
    if trazas.get("corridas") != len(ids):
        errores.append(f"corridas={trazas.get('corridas')} ≠ {len(ids)} entradas en por_corrida")
    if len(ids) != len(set(ids)):
        errores.append("ids de corrida repetidos")
    return Resultado.desde_errores(errores)


def escenarios_respaldados(guia: Mapping[str, Any], trazas: Mapping[str, Any]) -> Resultado:
    """Invariante 5. Cada escenario de la guía cita ≥ 1 id de corrida y todos existen en las trazas."""
    existentes = {c["id"] for c in trazas.get("por_corrida", [])}
    errores = []
    if guia.get("tarea_id") != trazas.get("tarea_id"):
        errores.append(f"guía de {guia.get('tarea_id')!r} con trazas de {trazas.get('tarea_id')!r}")
    for esc in guia.get("escenarios", []):
        citadas = esc.get("corridas") or []
        if not citadas:
            errores.append(f"escenario {esc.get('id')} sin id de corrida")
        if faltan := sorted(set(citadas) - existentes):
            errores.append(f"escenario {esc.get('id')} cita corridas inexistentes: {faltan}")
    return Resultado.desde_errores(errores)


# --------------------------------------------------------------------------- invariante 6
CAMPOS_ESTUDIANTE = ("enunciado_es", "foto_descripcion", "recursos_a_solicitud")
_CLAVES_PROHIBIDAS_ESTUDIANTE = frozenset(
    {"task_space", "reference_solution", "routes", "required_assumptions",
     "modelo_inadecuado", "validation_evidence", "mapa_ciclo", "recursos_de_entrada"}
)


def vista_estudiante(tarea: Mapping[str, Any]) -> dict:
    """Invariante 6. Lo único que se entrega a un estudiante simulado."""
    est = tarea["estudiante"]
    recursos = [
        {"id": r["id"], "que_es": r["que_es"], "contenido": r["contenido"]}
        for r in est["recursos_a_solicitud"]
        if r.get("disponibilidad") == "a_solicitud"
    ]
    return {
        "enunciado_es": est["enunciado_es"],
        "foto_descripcion": est["foto_descripcion"],
        "recursos_a_solicitud": recursos,
    }


def _claves(obj: Any) -> Iterator[str]:
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            yield str(k)
            yield from _claves(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _claves(v)


def verificar_aislamiento(payload: Mapping[str, Any], tarea: Mapping[str, Any] | None = None) -> Resultado:
    """Invariante 6. `payload` (lo que se enviará al estudiante simulado) contiene solo los
    campos permitidos, ninguna clave de `task_space` a ninguna profundidad y, si se entrega
    la tarea, ningún texto de su `task_space`."""
    errores = []
    if extra := sorted(set(payload) - set(CAMPOS_ESTUDIANTE)):
        errores.append(f"campos no permitidos para estudiantes: {extra}")
    if prohibidas := sorted(set(_claves(payload)) & _CLAVES_PROHIBIDAS_ESTUDIANTE):
        errores.append(f"claves reservadas al codificador/guía: {prohibidas}")
    if tarea is not None and "task_space" in tarea:
        textos_payload = "\n".join(textos_de(payload))
        for t in textos_de(tarea["task_space"]):
            if len(t) >= 20 and t in textos_payload:
                errores.append(f"texto de task_space filtrado al estudiante: «{t[:60]}»")
    return Resultado.desde_errores(errores)


# --------------------------------------------------------------------------- MED01
@lru_cache(maxsize=1)
def _ids_med01() -> frozenset[str]:
    import yaml  # dependencia solo para esta función

    rutas = sorted(DIR_MEDIOS.glob("MED01_*.yaml"), key=_version_de_archivo)
    datos = yaml.safe_load(rutas[-1].read_text(encoding="utf-8"))
    return frozenset(m["id"] for m in datos["medios"])


def medio_en_lista_blanca(medio_id: str, ids: Iterable[str] | None = None) -> Resultado:
    permitidos = frozenset(ids) if ids is not None else _ids_med01()
    ok = medio_id in permitidos
    return Resultado.desde_errores([] if ok else [f"medio {medio_id!r} fuera de MED01"])


# --------------------------------------------------------------------------- CLI para hooks
def _leer_json(ruta: str) -> Any:
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    orden, *args = argv
    if orden == "esquema":
        r = validar_contra_esquema(_leer_json(args[1]), args[0])
    elif orden == "umbral":
        r = cumple_umbral_rub01(_leer_json(args[0]))
    elif orden == "literal":
        ruta = Path(args[0])
        texto = ruta.read_text(encoding="utf-8")
        contenido = json.loads(texto) if ruta.suffix == ".json" else texto
        limite = int(args[2]) if len(args) > 2 else LIMITE_PALABRAS_LITERALES
        r = cumple_limite_literal(contenido, Path(args[1]).read_text(encoding="utf-8"), limite)
    elif orden == "aislamiento":
        r = verificar_aislamiento(_leer_json(args[0]))
    else:
        print(f"orden desconocida: {orden}", file=sys.stderr)
        return 1
    for e in r.errores:
        print(e, file=sys.stderr)
    return 0 if r else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
