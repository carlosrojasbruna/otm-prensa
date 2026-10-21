#!/usr/bin/env python3
"""Hooks de las 8 invariantes de CLAUDE.md (devops, fase 5).

No reimplementa las invariantes: llama a `pipeline/invariantes.py` y `pipeline/orquestador.py`
(las mismas funciones que usa el orquestador). Este archivo solo decide QUÉ archivos se revisan y
con qué funciones.

Un único punto de entrada con cuatro modos:

  pretool   Hook PreToolUse de Claude Code (Write | Edit | MultiEdit). Lee el JSON del evento por stdin
            y revisa el contenido que quedaría escrito. Exit 2 = bloquea (el motivo va por stderr).
  staged    Hook pre-commit de git (.githooks/pre-commit): revisa el contenido INDEXADO de los
            archivos del commit. Exit 1 = bloquea.
  archivos  Revisa los archivos que se indiquen (rutas relativas a la raíz o absolutas).
  repo      Revisa todos los archivos versionados (CI).

Invariante -> dónde se aplica
  1  esquema      tareas/**/{tarea,evaluacion,trazas,guia}_v*.json, tareas/catalogo.json, expedientes y
                  pipeline/state/trabajo/*: validar_contra_esquema (y, en expedientes, el
                  orquestador). La invariante 4 (toda cifra con localizador) la impone el esquema:
                  noticia.cifras[].localizador y tarea.recursos[].fuente son obligatorios.
  2  RUB01        evaluacion.json de una tarea en estado >= revisada: cumple_umbral_rub01 (>= 20/24 y
                  ningún criterio en 0, leído de RUB01).
  3  literal      (a) rutas de "texto de noticia" prohibidas en el repo; (b) si OTM_TEXTOS_NOTICIAS
                  apunta a una carpeta con los textos (.txt, fuera del repo), ningún archivo
                  revisado comparte > 25 palabras consecutivas con ellos (cumple_limite_literal).
                  El repo nunca guarda el cuerpo de las noticias: el ciclo lo relee en memoria.
  5  escenarios   guia + trazas hermanas (misma versión): escenarios_respaldados + consistencia_trazas.
  6  aislamiento  tarea: verificar_aislamiento(vista_estudiante(tarea), tarea).
  7  secretos     todo archivo de texto: claves de Anthropic/GitHub/Supabase y URLs de base con clave.
  8  reproducibilidad  evaluacion.json: el esquema exige agentes, versiones de prompt/RUB01/MAR03/MED01,
                  diseño del simulador, fecha y costo.
  (CLAUDE.md) insumos/ es de solo lectura: se bloquea modificar o borrar archivos existentes.

Un error INTERNO del hook (no una violación) no bloquea la sesión de Claude Code (avisa y sale con 0);
en `staged`, `archivos` y `repo` falla cerrado (exit 1).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from pipeline import invariantes as inv  # noqa: E402
from pipeline import orquestador as orq  # noqa: E402

# --------------------------------------------------------------------------- invariante 7
PATRONES_SECRETOS = (
    ("clave de Anthropic", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("token de GitHub", re.compile(r"github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{30,}")),
    ("clave secreta de Supabase", re.compile(r"sb_secret_[A-Za-z0-9_-]{20,}")),
    ("JWT (p. ej. service_role de Supabase)",
     re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}")),
    ("URL de base de datos con contraseña",
     re.compile(r"postgres(?:ql)?://[^:/\s'\"@]+:(?!\*+@|<|\$|\{|%|PASSWORD|CLAVE|\[|xxx)[^@\s'\"]{6,}@")),
)
EXT_TEXTO = {".py", ".md", ".json", ".yaml", ".yml", ".mjs", ".js", ".ts", ".astro", ".sql", ".txt", ".toml",
             ".cfg", ".ini", ".sh", ".html", ".css", ".csv", ".env", ""}
RUTAS_SIN_ESCANEO = ("sitio/package-lock.json",)

# --------------------------------------------------------------------------- invariante 3
RE_TEXTO_NOTICIA = re.compile(r"(^|/)(texto_noticia|cuerpo_noticia|noticia_texto|cuerpo)[^/]*\.(txt|md)$", re.I)


def textos_de_noticias() -> list[tuple[str, str]]:
    d = os.environ.get("OTM_TEXTOS_NOTICIAS")
    if not d or not Path(d).is_dir():
        return []
    return [(p.name, p.read_text(encoding="utf-8", errors="replace")) for p in sorted(Path(d).glob("*.txt"))]


# --------------------------------------------------------------------------- clasificación
CONTRATO_POR_PREFIJO = {"tarea": "tarea", "evaluacion": "evaluacion", "trazas": "trazas_resumen", "guia": "guia"}
CONTRATO_POR_NOMBRE_TRABAJO = {"tarea.json": "tarea", "evaluacion.json": "evaluacion",
                               "trazas_resumen.json": "trazas_resumen", "guia.json": "guia"}
RE_PUBLICADO = re.compile(r"^(tarea|evaluacion|trazas|guia)_(v[0-9][^/]*)\.json$")


def _rel(ruta: str | Path) -> str:
    p = Path(ruta)
    if p.is_absolute():
        try:
            p = p.resolve().relative_to(RAIZ)
        except ValueError:
            return str(p).replace("\\", "/")
    return str(p).replace("\\", "/")


def _hermano(rel: str, nombre: str) -> dict | None:
    p = RAIZ / Path(rel).parent / nombre
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _err(prefijo: str, r) -> list[str]:
    return [f"{prefijo}: {e}" for e in r.errores]


def chequear_json(rel: str, doc, *, estricto: bool) -> list[str]:
    """Invariantes 1, 2, 5, 6 y 8 sobre un artefacto JSON. `estricto`: exige los hermanos (guia sin
    trazas es error); en el hook de Claude Code (False) un hermano ausente aún no se puede comprobar."""
    errores: list[str] = []
    nombre = Path(rel).name
    en_tareas = rel.startswith("tareas/")
    en_trabajo = rel.startswith("pipeline/state/trabajo/")
    en_exp = rel.startswith("pipeline/state/expedientes/")

    if rel == "tareas/catalogo.json":
        return _err("Invariante 1", inv.validar_contra_esquema(doc, "catalogo"))

    if en_exp:
        art = doc.get("artefactos", {})
        try:
            orq._validar_artefactos(art)
            orq._comprobar_coherencia(art, doc["tarea_id"])
        except orq.ErrorOrquestador as e:
            return [f"Invariante 1: {e}"] + [f"  {x}" for x in getattr(e, "errores", ())]
        estado = doc.get("estado")
        if estado in orq._POST_REVISION:
            errores += _err("Invariante 2", inv.cumple_umbral_rub01(art["evaluacion"]))
            if "trazas_resumen" in art:
                errores += _err("trazas", inv.consistencia_trazas(art["trazas_resumen"]))
        if estado in orq._CON_GUIA:
            errores += _err("Invariante 5", inv.escenarios_respaldados(art["guia"], art["trazas_resumen"]))
        errores += _err("Invariante 6", inv.verificar_aislamiento(inv.vista_estudiante(art["tarea"]), art["tarea"]))
        return errores

    if en_tareas:
        m = RE_PUBLICADO.match(nombre)
        if not m:
            return []
        prefijo, version = m.groups()
        contrato, sufijo = CONTRATO_POR_PREFIJO[prefijo], version
        tarea = doc if prefijo == "tarea" else _hermano(rel, f"tarea_{sufijo}.json")
        hermano = lambda p: doc if prefijo == p else _hermano(rel, f"{p}_{sufijo}.json")  # noqa: E731
    elif en_trabajo and nombre in CONTRATO_POR_NOMBRE_TRABAJO:
        contrato = CONTRATO_POR_NOMBRE_TRABAJO[nombre]
        prefijo = {"tarea": "tarea", "evaluacion": "evaluacion", "trazas_resumen": "trazas", "guia": "guia"}[contrato]
        tarea = doc if prefijo == "tarea" else _hermano(rel, "tarea.json")
        hermano = lambda p: doc if prefijo == p else _hermano(  # noqa: E731
            rel, {"tarea": "tarea.json", "evaluacion": "evaluacion.json", "trazas": "trazas_resumen.json",
                  "guia": "guia.json"}[p])
    else:
        return []

    errores += _err("Invariante 1", inv.validar_contra_esquema(doc, contrato))      # incluye 4 y 8
    if errores:
        return errores
    estado = (tarea or {}).get("estado")
    if prefijo == "tarea":
        errores += _err("Invariante 6", inv.verificar_aislamiento(inv.vista_estudiante(doc), doc))
    if prefijo == "evaluacion":
        if tarea is None and estricto:
            errores.append("Invariante 2: no hay tarea hermana para saber el estado")
        elif estado in orq._POST_REVISION:
            errores += _err("Invariante 2", inv.cumple_umbral_rub01(doc))
    if prefijo == "trazas":
        errores += _err("trazas", inv.consistencia_trazas(doc))
    if prefijo == "guia":
        trazas = hermano("trazas")
        if trazas is None:
            if estricto:
                errores.append("Invariante 5: la guía no tiene trazas hermanas que respalden sus escenarios")
        else:
            errores += _err("Invariante 5", inv.escenarios_respaldados(doc, trazas))
    return errores


def chequear_texto(rel: str, texto: str, noticias: list[tuple[str, str]]) -> list[str]:
    """Invariantes 7 y 3 sobre el texto de un archivo."""
    errores: list[str] = []
    if RE_TEXTO_NOTICIA.search(rel):
        errores.append("Invariante 3: no se versiona el cuerpo de una noticia (se cita y se resume)")
    if rel not in RUTAS_SIN_ESCANEO:
        for que, patron in PATRONES_SECRETOS:
            if patron.search(texto):
                errores.append(f"Invariante 7: posible {que} en el archivo (no se muestra el valor)")
    if noticias and not rel.startswith(("insumos/", "evals/casos/")):
        objeto: object = texto
        if rel.endswith(".json"):           # en un JSON el titular de las citas queda fuera del conteo (noticia v1.2)
            try:
                objeto = json.loads(texto)
            except ValueError:
                pass
        for nombre, cuerpo in noticias:
            r = inv.cumple_limite_literal(objeto, cuerpo)
            if not r:
                errores.append(f"Invariante 3: {r.errores[0][:200]} (noticia {nombre})")
    return errores


def chequear(rel: str, contenido: str | bytes, *, estricto: bool = True, noticias=None) -> list[str]:
    """Todas las revisiones aplicables a un archivo con el contenido dado."""
    if isinstance(contenido, bytes):
        try:
            contenido = contenido.decode("utf-8")
        except UnicodeDecodeError:
            return []   # binario
    errores: list[str] = []
    suf = Path(rel).suffix.lower()
    if suf in EXT_TEXTO:
        errores += chequear_texto(rel, contenido, textos_de_noticias() if noticias is None else noticias)
    if suf == ".json":
        try:
            doc = json.loads(contenido)
        except json.JSONDecodeError as e:
            return errores + [f"Invariante 1: JSON inválido ({e.msg}, línea {e.lineno})"]
        errores += chequear_json(rel, doc, estricto=estricto)
    return [f"{rel}: {e}" for e in errores]


# --------------------------------------------------------------------------- git
def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", check=True).stdout


def _git_bytes(*args: str) -> bytes:
    return subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, check=True).stdout


def modo_staged() -> int:
    salida = _git("diff", "--cached", "--name-status", "--no-renames").splitlines()
    errores: list[str] = []
    for linea in salida:
        estado, _, ruta = linea.partition("\t")
        ruta = ruta.strip().strip('"')
        if ruta.startswith("insumos/") and estado[0] in "MD":
            errores.append(f"{ruta}: insumos/ es de solo lectura; el cambio es una nueva versión (nombre_vX.Y_AAAA-MM-DD)")
        if estado[0] in "AM":
            errores += chequear(ruta, _git_bytes("show", f":{ruta}"), estricto=False)
    return _informar(errores, "commit")


def modo_archivos(rutas: list[str]) -> int:
    errores: list[str] = []
    for r in rutas:
        rel = _rel(r)
        p = RAIZ / rel
        if p.is_file():
            errores += chequear(rel, p.read_bytes())
    return _informar(errores, "archivos")


def modo_repo() -> int:
    errores: list[str] = []
    for rel in _git("ls-files").splitlines():
        p = RAIZ / rel
        if p.is_file() and p.stat().st_size < 5_000_000:
            errores += chequear(rel, p.read_bytes())
    return _informar(errores, "repositorio")


def _informar(errores: list[str], que: str) -> int:
    if errores:
        print(f"[otm-hook] {len(errores)} violación(es) de invariantes en {que}:", file=sys.stderr)
        for e in errores:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"[otm-hook] invariantes ok ({que})")
    return 0


# --------------------------------------------------------------------------- Claude Code (PreToolUse)
def _aplicar_edicion(rel: str, ed: dict, texto: str) -> str:
    viejo, nuevo = ed.get("old_string", ""), ed.get("new_string", "")
    if ed.get("replace_all"):
        return texto.replace(viejo, nuevo)
    return texto.replace(viejo, nuevo, 1)


def modo_pretool(evento: dict) -> int:
    herramienta = evento.get("tool_name", "")
    datos = evento.get("tool_input", {}) or {}
    ruta = datos.get("file_path")
    if not ruta or herramienta not in {"Write", "Edit", "MultiEdit"}:
        return 0
    rel = _rel(ruta)
    p = RAIZ / rel
    if rel.startswith("../") or Path(rel).is_absolute():
        return 0   # fuera del repo
    if rel.startswith("insumos/") and p.exists():
        print(f"[otm-hook] BLOQUEADO: {rel} es un insumo (solo lectura). Un cambio es una nueva versión "
              "(nombre_vX.Y_AAAA-MM-DD), nunca una edición in situ.", file=sys.stderr)
        return 2
    actual = p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""
    if herramienta == "Write":
        nuevo = datos.get("content", "")
    elif herramienta == "Edit":
        nuevo = _aplicar_edicion(rel, datos, actual)
    else:
        nuevo = actual
        for ed in datos.get("edits", []):
            nuevo = _aplicar_edicion(rel, ed, nuevo)
    errores = chequear(rel, nuevo, estricto=False)
    if errores:
        print("[otm-hook] BLOQUEADO por invariantes de CLAUDE.md:", file=sys.stderr)
        for e in errores:
            print(f"  - {e}", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    modo, *resto = argv
    try:
        if modo == "pretool":
            return modo_pretool(json.loads(sys.stdin.read() or "{}"))
        if modo == "staged":
            return modo_staged()
        if modo == "archivos":
            return modo_archivos(resto)
        if modo == "repo":
            return modo_repo()
    except Exception as e:  # noqa: BLE001 — un fallo del hook no es una violación
        print(f"[otm-hook] error interno del hook ({type(e).__name__}: {e})", file=sys.stderr)
        return 0 if modo == "pretool" else 1   # en la sesión no se bloquea; en commit/CI se falla cerrado
    print(f"modo desconocido: {modo}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
