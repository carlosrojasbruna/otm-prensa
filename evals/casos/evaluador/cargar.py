"""Carga los casos del evaluador (una tarea-oro por archivo JSON) y arma la entrada.

El texto de la tarea no se duplica en el caso: se extrae en tiempo de ejecución desde
`insumos/tareas-oro/` (entre dos marcadores de línea) y se verifica con sha256, para no copiar
otra vez texto de fuentes (CLAUDE.md, invariante 3). Excepción: Sugarloaf, cuyo enunciado está en
un repositorio externo; el caso guarda la traducción de trabajo al español (INS02 v0.2 §1.2) y la
descripción de la foto (§6.3), que son los bloques que el pipeline entrega a estudiantes.

La entrada al evaluador NUNCA incluye `referencia`, `rol` ni notas evaluativas de la fuente.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
DIR_CASOS = Path(__file__).resolve().parent


def extraer(archivo: str, desde: str, hasta: str | None) -> str:
    """Líneas estrictamente entre la línea que empieza con `desde` y la que empieza con `hasta`
    (o fin de archivo). Quita el prefijo de cita markdown '> '."""
    lineas = (RAIZ / archivo).read_text(encoding="utf-8").splitlines()
    ini = next(k for k, l in enumerate(lineas) if l.strip().startswith(desde))
    fin = len(lineas)
    if hasta:
        fin = next(k for k, l in enumerate(lineas) if k > ini and l.strip().startswith(hasta))
    cuerpo = [l[2:] if l.startswith("> ") else (l[1:] if l.startswith(">") else l) for l in lineas[ini + 1:fin]]
    return "\n".join(l.rstrip() for l in cuerpo).strip()


def sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def cargar_caso(ruta: Path) -> dict:
    caso = json.loads(Path(ruta).read_text(encoding="utf-8"))
    fuente = caso["texto_fuente"]
    if fuente["tipo"] == "extraccion":
        texto = extraer(fuente["archivo"], fuente["desde"], fuente.get("hasta"))
        if sha(texto) != fuente["sha256"]:
            raise ValueError(f"{caso['id']}: el texto extraído cambió (sha256); revisar versión del insumo")
    else:
        texto = fuente["texto"]
    entrada = {
        "titulo": caso["titulo"],
        "nivel_declarado": caso["nivel_declarado"],
        "forma_texto": caso["forma_texto"],
        "texto": texto,
        "recursos": caso.get("recursos", []),
        "mapa_ciclo": caso.get("mapa_ciclo"),
    }
    return {**caso, "entrada": entrada}


def cargar_todos() -> list[dict]:
    return [cargar_caso(p) for p in sorted(DIR_CASOS.glob("*.json"))]
