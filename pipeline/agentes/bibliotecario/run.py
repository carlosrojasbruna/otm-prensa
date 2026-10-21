"""Agente bibliotecario: archiva una tarea publicable en `tareas/AAAA-MM/slug/`, actualiza el
catálogo (`tareas/catalogo.json`, contrato `catalogo`) y prepara rama, commit y PR semanal.

La carpeta y el id del catálogo usan el slug base, sin el sufijo `-vN` que el pipeline agrega a las
versiones nuevas (`2026-10-queso-v3` -> `tareas/2026-10/queso/`): todas las versiones de una tarea viven
en la misma carpeta y se distinguen por el nombre de archivo (`tarea_v3.0_AAAA-MM-DD.json`). Junto al
JSON se escriben `tarea_vX.Y_….md` y `guia_vX.Y_….md` (render de PLT01/PLT02) y, si hay, `icono_vX.Y_….svg`.

Script determinista (sin modelo). Por defecto es un ensayo (`--dry-run`): valida, calcula todo
y muestra los comandos git/gh, pero NO escribe archivos ni ejecuta nada. Solo `--ejecutar`
escribe y ejecuta. `GH_TOKEN` se lee del entorno (lo usa `gh`); nunca se imprime ni se escribe.

Uso:
  python -m pipeline.agentes.bibliotecario.run --tarea t.json --guia g.json --evaluacion e.json
  python -m pipeline.agentes.bibliotecario.run --ejemplos            # demo con contratos/ejemplos
  ... --ejecutar [--sin-remoto] [--raiz RUTA]
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

RAIZ_REPO = Path(__file__).resolve().parents[3]
if str(RAIZ_REPO) not in sys.path:
    sys.path.insert(0, str(RAIZ_REPO))

import yaml  # noqa: E402

from pipeline import invariantes as inv  # noqa: E402
from pipeline.agentes.bibliotecario.render import render_guia, render_tarea  # noqa: E402

CONFIG = yaml.safe_load((Path(__file__).with_name("config.yaml")).read_text(encoding="utf-8"))
LICENCIA = CONFIG["git"]["licencia"]
RUTA_CATALOGO = CONFIG["salida"]["archivo"]
ESTADOS_ARCHIVABLES = frozenset(CONFIG["estados_archivables"])
RE_ID = re.compile(r"^([0-9]{4})-([0-9]{2})-([a-z0-9]+(?:-[a-z0-9]+)*)$")
RE_NOMBRE = re.compile(r"^[a-z0-9_]+_v[0-9]+\.[0-9]+_[0-9]{4}-[0-9]{2}-[0-9]{2}\.(json|md|svg)$")
RE_SUFIJO_VERSION = re.compile(r"-v[0-9]+$")
# claves de `archivos` del contrato `catalogo` v1.1 (los .md y el ícono de cada versión se listan)
CLAVES_CATALOGO = ("tarea", "tarea_md", "guia", "guia_md", "evaluacion", "trazas", "icono")
VERSION_CONTRATO_CATALOGO = "1.1"


class ErrorBibliotecario(Exception):
    """La tarea o el catálogo no se pueden archivar; no se escribió ni ejecutó nada."""

    def __init__(self, errores):
        self.errores = [errores] if isinstance(errores, str) else list(errores)
        super().__init__("; ".join(self.errores))


@dataclass
class Plan:
    tarea_id: str
    version: int
    ruta: str                              # tareas/AAAA-MM/slug/
    archivos: dict[str, tuple[str, Any]]   # clave -> (nombre, contenido)
    entrada: dict                          # entrada de catálogo (con commit provisional)
    catalogo: dict                         # catálogo resultante (con commit provisional)
    rama: str
    mensaje_commit: str
    mensaje_commit_catalogo: str
    titulo_pr: str
    cuerpo_pr: str = ""
    comandos: list[list[str]] = field(default_factory=list)
    acciones: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- utilidades
def nombre_archivo(base: str, version: int, fecha: str, ext: str = "json") -> str:
    """`nombre_vX.Y_AAAA-MM-DD.ext` (convención del proyecto; las versiones enteras son X.0)."""
    return f"{base}_v{version}.0_{fecha}.{ext}"


def id_base(tarea_id: str) -> str:
    """Id sin el sufijo de versión del pipeline: `2026-10-queso-v3` -> `2026-10-queso`."""
    return RE_SUFIJO_VERSION.sub("", tarea_id)


def _ahora(ahora: datetime | None) -> str:
    return (ahora or datetime.now(timezone.utc)).isoformat(timespec="seconds")


def _semana(fecha: str) -> str:
    y, w, _ = date.fromisoformat(fecha).isocalendar()
    return f"{y}-W{w:02d}"


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def _contenido(nombre: str, obj: Any) -> str:
    return obj if nombre.endswith((".md", ".svg")) else _json(obj)


def cargar_catalogo(raiz: Path, ahora: datetime | None = None) -> dict:
    """Catálogo existente (validado; si no valida se rechaza sin tocarlo) o uno vacío."""
    ruta = raiz / RUTA_CATALOGO
    if not ruta.exists():
        return {"version_contrato": VERSION_CONTRATO_CATALOGO, "actualizado": _ahora(ahora), "tareas": []}
    cat = json.loads(ruta.read_text(encoding="utf-8"))
    r = inv.validar_contra_esquema(cat, "catalogo")
    if not r:
        raise ErrorBibliotecario(["el catálogo existente no valida (no se toca):", *r.errores])
    return cat


# --------------------------------------------------------------------------- validación
def _validar_entradas(tarea, guia, evaluacion, trazas, texto_noticia, icono_svg=None) -> None:
    errores: list[str] = []
    for nombre, art in (("tarea", tarea), ("guia", guia), ("evaluacion", evaluacion)):
        errores += list(inv.validar_contra_esquema(art, nombre).errores)          # invariante 1
    if trazas is not None:
        errores += list(inv.validar_contra_esquema(trazas, "trazas_resumen").errores)
    if errores:
        raise ErrorBibliotecario(errores)

    if tarea["estado"] not in ESTADOS_ARCHIVABLES:
        errores.append(f"estado `{tarea['estado']}` no publicable (se exige uno de {sorted(ESTADOS_ARCHIVABLES)})")
    if not RE_ID.match(tarea["id"]):
        errores.append(f"id mal formado: {tarea['id']!r} (se espera AAAA-MM-slug)")
    if icono_svg is not None and not icono_svg.lstrip().startswith(("<svg", "<?xml")):
        errores.append("el ícono no es un SVG")
    if not (tarea["id"] == guia["tarea_id"] == evaluacion["tarea_id"]):
        errores.append("tarea, guía y evaluación no son de la misma tarea")
    if guia["version"] != tarea["version"]:
        errores.append(f"versión de guía ({guia['version']}) distinta de la de la tarea ({tarea['version']})")
    umbral = inv.cumple_umbral_rub01(evaluacion)                                   # invariante 2
    if not umbral:
        errores += list(umbral.errores) or ["RUB01 bajo el umbral"]
    if guia["ficha"]["puntaje_rub01"] != evaluacion["rub01"]["total"]:
        errores.append("guia.ficha.puntaje_rub01 no coincide con evaluacion.rub01.total")
    if trazas is not None:                                                         # invariante 5
        r = inv.escenarios_respaldados(guia, trazas)
        if not r:
            errores += list(r.errores)
    if texto_noticia:                                                              # invariante 3
        for nombre, art in (("tarea", tarea), ("guia", guia)):
            r = inv.cumple_limite_literal(art, texto_noticia)
            if not r:
                errores += [f"{nombre}: {e}" for e in r.errores]
    if errores:
        raise ErrorBibliotecario(errores)


def cuerpo_pr(entradas: list[dict]) -> str:
    """Cuerpo del PR (plantilla determinista; solo cita la noticia, nunca la reproduce)."""
    L = ["## Tareas incluidas", ""]
    for e in entradas:
        n = e["noticia"]
        L += [f"- `{e['id']}` v{e['version']} · nivel {e['nivel_principal']} · RUB01 {e['rub01_total']}/24",
              f"  - Noticia: {n['medio']}, «{n['titulo']}», {n['fecha']}, {n['url']}"]
    L += ["", "## Revisión (GOB01 §2)",
          "- [ ] Quien revisó la guía aprueba el merge.",
          "- [ ] Cifras con localizador; ningún texto literal de noticia > 25 palabras.",
          "- [ ] Productos bajo CC BY-NC-SA 4.0.", "",
          "Generado por el agente bibliotecario (script determinista)."]
    return "\n".join(L)


# --------------------------------------------------------------------------- plan
def preparar(tarea, guia, evaluacion, *, raiz: Path, trazas=None, texto_noticia: str | None = None,
             fecha_publicacion: str | None = None, ahora: datetime | None = None,
             commit_provisional: str = "0000000", icono_svg: str | None = None) -> Plan:
    """Valida y calcula todo sin escribir en disco. Lanza ErrorBibliotecario si algo no cumple."""
    _validar_entradas(tarea, guia, evaluacion, trazas, texto_noticia, icono_svg)
    fecha = fecha_publicacion or (ahora or datetime.now(timezone.utc)).date().isoformat()
    rf = inv.validar_contra_esquema(fecha, "noticia#/$defs/fecha")
    if not rf:
        raise ErrorBibliotecario(rf.errores)

    tid, ver = tarea["id"], tarea["version"]
    base = id_base(tid)
    aaaa, mm, slug = RE_ID.match(base).groups()
    ruta = f"tareas/{aaaa}-{mm}/{slug}/"
    catalogo = copy.deepcopy(cargar_catalogo(raiz, ahora))   # valida el existente (licencia, etc.)

    previas = [t for t in catalogo["tareas"] if t["id"] == base]
    anterior = previas[0] if previas else None
    if anterior and ver <= anterior["version"]:
        raise ErrorBibliotecario(
            f"{tid} v{ver}: ya está publicada la v{anterior['version']}; una tarea publicada no se edita, "
            f"hay que crear la v{anterior['version'] + 1} o superior")

    tarea_md, guia_md = render_tarea(tarea, evaluacion), render_guia(guia, trazas)
    if texto_noticia:                                                              # invariante 3 (render)
        errores = [f"{n}: {e}" for n, md in (("tarea.md", tarea_md), ("guia.md", guia_md))
                   for e in inv.cumple_limite_literal(md, texto_noticia,
                                                     titulares=[tarea["noticia"]["titulo"]]).errores]
        if errores:
            raise ErrorBibliotecario(errores)
    archivos = {
        "tarea": (nombre_archivo("tarea", ver, fecha), tarea),
        "tarea_md": (nombre_archivo("tarea", ver, fecha, "md"), tarea_md),
        "guia": (nombre_archivo("guia", ver, fecha), guia),
        "guia_md": (nombre_archivo("guia", ver, fecha, "md"), guia_md),
        "evaluacion": (nombre_archivo("evaluacion", ver, fecha), evaluacion),
    }
    if trazas is not None:
        archivos["trazas"] = (nombre_archivo("trazas", ver, fecha), trazas)
    if icono_svg is not None:
        archivos["icono"] = (nombre_archivo("icono", ver, fecha, "svg"), icono_svg)
    errores = []
    for nombre, _ in archivos.values():
        if not RE_NOMBRE.match(nombre):
            errores.append(f"nombre de archivo mal formado: {nombre}")
        if (raiz / ruta / nombre).exists():
            errores.append(f"{ruta}{nombre} ya existe; no se sobrescribe")
    if errores:
        raise ErrorBibliotecario(errores)

    var = tarea["variantes"]
    entrada = {
        "id": base, "titulo": tarea["titulo"], "version": ver, "fecha_publicacion": fecha,
        "nivel_principal": tarea["nivel_principal"],
        **({"sub_tramo": tarea["sub_tramo"]} if tarea.get("sub_tramo") else {}),
        "variantes": [v for v in (var.get("abajo"), var.get("arriba")) if v],
        "area": tarea["area"], "contenidos_matematicos": tarea["contenidos_matematicos"],
        "tiempo_estimado": tarea["tiempo_estimado"], "rub01_total": evaluacion["rub01"]["total"],
        "noticia": {k: tarea["noticia"][k] for k in ("medio", "titulo", "fecha", "url")},
        "ruta": ruta,
        "archivos": {k: v[0] for k, v in archivos.items() if k in CLAVES_CATALOGO},
        "licencia": LICENCIA, "commit": commit_provisional,
        "versiones_anteriores": [],
    }
    if anterior:
        entrada["versiones_anteriores"] = [
            *anterior["versiones_anteriores"],
            {"version": anterior["version"], "fecha_publicacion": anterior["fecha_publicacion"],
             "commit": anterior["commit"], "archivos": anterior["archivos"]},
        ]
    catalogo["tareas"] = sorted([t for t in catalogo["tareas"] if t["id"] != base] + [entrada],
                                key=lambda t: t["id"])
    catalogo["version_contrato"] = VERSION_CONTRATO_CATALOGO   # un catálogo v1.0 se reescribe como v1.1
    catalogo["actualizado"] = _ahora(ahora)
    r = inv.validar_contra_esquema(catalogo, "catalogo")                           # invariante 1
    if not r:
        raise ErrorBibliotecario(["el catálogo resultante no valida:", *r.errores])

    pref = CONFIG["git"]["prefijo_commit"]
    semana = _semana(fecha)
    return Plan(
        tarea_id=tid, version=ver, ruta=ruta, archivos=archivos, entrada=entrada, catalogo=catalogo,
        rama=f"{CONFIG['git']['prefijo_rama']}{semana}",
        mensaje_commit=f"{pref} publica {tid} v{ver}",
        mensaje_commit_catalogo=f"{pref} catálogo: {tid} v{ver}",
        titulo_pr=f"Tareas de la semana {semana}",
        cuerpo_pr=cuerpo_pr([entrada]),
    )


# --------------------------------------------------------------------------- git / gh
def _cmd(c: list[str]) -> str:
    return " ".join(shlex.quote(x) for x in c)


def _correr(c: list[str], raiz: Path, comprobar: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(c, cwd=raiz, capture_output=True, text=True, encoding="utf-8")
    if comprobar and r.returncode != 0:
        raise ErrorBibliotecario(f"falló `{_cmd(c)}`: {r.stderr.strip()[:300]}")
    return r


def comandos(plan: Plan, *, remoto: bool = True) -> list[list[str]]:
    """Secuencia de comandos que se ejecutaría."""
    c = [
        ["git", "switch", "-c", plan.rama],
        ["git", "add", "--", plan.ruta],
        ["git", "commit", "-m", plan.mensaje_commit],
        ["git", "add", "--", RUTA_CATALOGO],
        ["git", "commit", "-m", plan.mensaje_commit_catalogo],
    ]
    if remoto:
        c += [["git", "push", "-u", "origin", plan.rama],
              ["gh", "pr", "create", "--base", CONFIG["git"]["rama_base"], "--head", plan.rama,
               "--title", plan.titulo_pr, "--body", plan.cuerpo_pr]]
    return c


def ejecutar(plan: Plan, *, raiz: Path, remoto: bool = True) -> dict:
    """Escribe y ejecuta. Requiere repo git en `raiz` sin cambios en el índice."""
    if _correr(["git", "diff", "--cached", "--quiet"], raiz, comprobar=False).returncode != 0:
        raise ErrorBibliotecario("el índice de git tiene cambios en preparación; no se mezcla con ellos")
    if remoto and not (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")):
        raise ErrorBibliotecario("falta GH_TOKEN en el entorno (necesario para push y PR)")
    existe = _correr(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{plan.rama}"], raiz,
                     comprobar=False).returncode == 0
    _correr(["git", "switch", plan.rama] if existe else ["git", "switch", "-c", plan.rama], raiz)

    carpeta = raiz / plan.ruta
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre, contenido in plan.archivos.values():
        (carpeta / nombre).write_text(_contenido(nombre, contenido), encoding="utf-8")
    _correr(["git", "add", "--", plan.ruta], raiz)
    _correr(["git", "commit", "-m", plan.mensaje_commit], raiz)
    sha = _correr(["git", "rev-parse", "--short=12", "HEAD"], raiz).stdout.strip()

    # el catálogo registra el commit real de los archivos de la tarea
    plan.entrada["commit"] = sha
    r = inv.validar_contra_esquema(plan.catalogo, "catalogo")
    if not r:
        raise ErrorBibliotecario(["catálogo inválido tras fijar commit:", *r.errores])
    (raiz / RUTA_CATALOGO).write_text(_json(plan.catalogo), encoding="utf-8")
    _correr(["git", "add", "--", RUTA_CATALOGO], raiz)
    _correr(["git", "commit", "-m", plan.mensaje_commit_catalogo], raiz)

    pr = None
    if remoto:
        _correr(["git", "push", "-u", "origin", plan.rama], raiz)
        ya = _correr(["gh", "pr", "list", "--head", plan.rama, "--json", "url", "--jq", ".[0].url"], raiz)
        if ya.stdout.strip():
            pr = ya.stdout.strip()   # el push ya actualizó el PR semanal existente
        else:
            pr = _correr(["gh", "pr", "create", "--base", CONFIG["git"]["rama_base"], "--head", plan.rama,
                          "--title", plan.titulo_pr, "--body", plan.cuerpo_pr], raiz).stdout.strip()
    return {"rama": plan.rama, "commit_tarea": sha, "pr": pr}


# --------------------------------------------------------------------------- API de alto nivel
def publicar(tarea, guia, evaluacion, *, raiz: Path | str | None = None, trazas=None,
             texto_noticia: str | None = None, fecha_publicacion: str | None = None,
             ahora: datetime | None = None, ejecutar_real: bool = False, remoto: bool = True,
             icono_svg: str | None = None, salida=print) -> Plan:
    """Dry-run por defecto. Con `ejecutar_real=True` escribe y ejecuta."""
    raiz = Path(raiz) if raiz else RAIZ_REPO
    plan = preparar(tarea, guia, evaluacion, raiz=raiz, trazas=trazas, texto_noticia=texto_noticia,
                    fecha_publicacion=fecha_publicacion, ahora=ahora, icono_svg=icono_svg)
    plan.comandos = comandos(plan, remoto=remoto)
    if ejecutar_real:
        plan.acciones = [f"escribir {plan.ruta}{n}" for n, _ in plan.archivos.values()]
        ejecutar(plan, raiz=raiz, remoto=remoto)
        return plan
    salida("# DRY-RUN: no se escribe ningún archivo ni se ejecuta ningún comando")
    salida(f"# tarea {plan.tarea_id} v{plan.version} -> {plan.ruta}")
    for n, _ in plan.archivos.values():
        salida(f"#   escribiría {plan.ruta}{n}")
    salida(f"#   actualizaría {RUTA_CATALOGO} ({len(plan.catalogo['tareas'])} tarea(s); valida contra `catalogo`)")
    if plan.entrada["versiones_anteriores"]:
        vs = [v["version"] for v in plan.entrada["versiones_anteriores"]]
        salida(f"#   versiones anteriores conservadas intactas: {vs}")
    salida("#   el commit del catálogo es el real tras el primer commit (aquí 0000000)")
    for c in plan.comandos:
        if c[:3] == ["gh", "pr", "create"]:
            c = [x if x != plan.cuerpo_pr else "<cuerpo del PR, ver abajo>" for x in c]
        salida("$ " + _cmd(c))
    salida("# cuerpo del PR:")
    for linea in plan.cuerpo_pr.splitlines():
        salida("#   " + linea)
    return plan


# --------------------------------------------------------------------------- CLI
def _leer(ruta) -> Any:
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tarea"); p.add_argument("--guia"); p.add_argument("--evaluacion")
    p.add_argument("--trazas"); p.add_argument("--texto-noticia"); p.add_argument("--icono", help="SVG del ícono")
    p.add_argument("--ejemplos", action="store_true",
                   help="usa contratos/ejemplos (la tarea se marca `verificada` en memoria) para una demo")
    p.add_argument("--raiz", default=str(RAIZ_REPO))
    p.add_argument("--fecha", help="fecha de publicación AAAA-MM-DD (por defecto, hoy UTC)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="(por defecto) solo muestra los comandos")
    g.add_argument("--ejecutar", action="store_true", help="escribe archivos y ejecuta git/gh")
    p.add_argument("--sin-remoto", action="store_true", help="con --ejecutar: no hace push ni PR")
    a = p.parse_args(argv)
    try:
        if a.ejemplos:
            d = RAIZ_REPO / "contratos" / "ejemplos"
            tarea, guia, ev = (_leer(d / f"{n}_ejemplo.json") for n in ("tarea", "guia", "evaluacion"))
            tarea["estado"] = "verificada"
            trazas = None
        else:
            if not (a.tarea and a.guia and a.evaluacion):
                p.error("faltan --tarea, --guia, --evaluacion (o use --ejemplos)")
            tarea, guia, ev = _leer(a.tarea), _leer(a.guia), _leer(a.evaluacion)
            trazas = _leer(a.trazas) if a.trazas else None
        texto = Path(a.texto_noticia).read_text(encoding="utf-8") if a.texto_noticia else None
        icono = Path(a.icono).read_text(encoding="utf-8") if a.icono else None
        publicar(tarea, guia, ev, raiz=a.raiz, trazas=trazas, texto_noticia=texto, icono_svg=icono,
                 fecha_publicacion=a.fecha, ejecutar_real=a.ejecutar, remoto=not a.sin_remoto)
    except ErrorBibliotecario as e:
        print("RECHAZADO:", *e.errores, sep="\n  - ", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
