"""Publicación de expedientes en `verificada` (lo usa .github/workflows/publicar.yml; también sirve en local).

Envuelve al bibliotecario. Por cada id:
  1. carga el expediente y exige `verificada` (una tarea `publicada` se rechaza: no se edita, se versiona);
  2. registra la revisión humana 2 (`--revisor`, obligatorio, GOB01 §2) en `guia.trazabilidad` y en la marca
     `revision_humana_2` del expediente; la guía resultante se valida contra su esquema (invariante 1);
  3. relee la noticia en memoria para la invariante 3; si no se puede leer, se rechaza (lectura conservadora:
     es la última puerta antes de lo público);
  4. el bibliotecario valida y calcula el plan (umbral RUB01, escenarios respaldados, catálogo, duplicados).

Todo o nada: si una tarea no pasa, no se escribe ninguna. Con `--ejecutar` escribe `tareas/<mes>/<slug>/`,
`tareas/catalogo.json` y la marca del expediente, y commitea en `--rama` sin push (el push y el PR los hace el
workflow). El expediente sigue en `verificada`: pasa a `publicada` solo tras el merge del PR.

Uso:
  python -m pipeline.publicar ID [ID ...] --revisor "Nombre Apellido"                 # dry-run
  python -m pipeline.publicar ID [ID ...] --revisor "…" --ejecutar --rama publicar/X --cuerpo pr.md
Código de salida: 0 ok; 2 rechazado (no se escribió nada).
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from pipeline import invariantes as inv  # noqa: E402
from pipeline import orquestador as orq  # noqa: E402
from pipeline.agentes.bibliotecario import run as bib  # noqa: E402


class Rechazo(Exception):
    def __init__(self, errores):
        self.errores = [errores] if isinstance(errores, str) else list(errores)
        super().__init__("; ".join(self.errores))


def _leer_noticia(url: str) -> str:
    from pipeline.agentes.explorador.run import bajar_cuerpo
    return bajar_cuerpo(url)


def _cargar(tid: str, raiz: Path) -> orq.Expediente:
    ruta = raiz / "pipeline" / "state" / "expedientes" / f"{tid}.json"
    if not ruta.exists():
        raise Rechazo(f"{tid}: no existe el expediente {ruta.relative_to(raiz).as_posix()}")
    return orq.Expediente.desde_dict(json.loads(ruta.read_text(encoding="utf-8")))


def _icono(tid: str, raiz: Path) -> str | None:
    ruta = raiz / "pipeline" / "state" / "trabajo" / tid / "icono.svg"   # la marca guarda una ruta local absoluta
    return ruta.read_text(encoding="utf-8") if ruta.exists() else None


def preparar_todas(ids: list[str], revisor: str, *, raiz: Path, fecha: str,
                   leer_noticia: Callable[[str], str] = _leer_noticia) -> list[dict]:
    """Valida todas las tareas sin escribir nada. Devuelve, por id, lo necesario para publicar."""
    errores: list[str] = []
    if len(revisor.strip()) < 3:
        errores.append("--revisor es obligatorio (quien hizo la revisión humana 2)")
    if len(set(ids)) != len(ids):
        errores.append("hay ids repetidos")
    bases = [bib.id_base(t) for t in ids]
    if len(set(bases)) != len(bases):
        errores.append("dos ids son versiones de la misma tarea; se publica una por vez")
    if errores:
        raise Rechazo(errores)

    lote = []
    for tid in ids:
        try:
            exp = _cargar(tid, raiz)
            if exp.estado == "publicada":
                pub = exp.marcas.get("publicacion", {})
                raise Rechazo(f"{tid}: ya está publicada ({pub.get('ruta', '?')}, merge {pub.get('merge', '?')}); "
                              "una tarea publicada no se edita, se crea una versión nueva")
            if exp.estado != "verificada":
                raise Rechazo(f"{tid}: está en `{exp.estado}`; solo se publica desde `verificada`")
            art = exp.artefactos
            guia = copy.deepcopy(art["guia"])
            guia["trazabilidad"]["revision_humana_2"] = {"revisor": revisor.strip(), "fecha": fecha}
            r = inv.validar_contra_esquema(guia, "guia")                                    # invariante 1
            if not r:
                raise Rechazo([f"{tid}: la guía con la revisión 2 no valida:", *r.errores])
            url = (art.get("noticia") or art["tarea"].get("noticia") or {}).get("url")
            try:
                texto = leer_noticia(url)
            except Exception as err:  # noqa: BLE001
                raise Rechazo(f"{tid}: no se pudo releer la noticia para la invariante 3 ({str(err)[:160]}); "
                              "no se publica sin comprobarla") from err
            if not texto:
                raise Rechazo(f"{tid}: la noticia releída está vacía; no se publica sin comprobar la invariante 3")
            plan = bib.preparar(art["tarea"], guia, art["evaluacion"], raiz=raiz, trazas=art.get("trazas_resumen"),
                                texto_noticia=texto, fecha_publicacion=fecha, icono_svg=_icono(tid, raiz))
        except bib.ErrorBibliotecario as e:
            errores += [f"{tid}: {x}" for x in e.errores]
            continue
        except Rechazo as e:
            errores += e.errores
            continue
        lote.append({"tid": tid, "exp": exp, "guia": guia, "texto": texto, "plan": plan})
    if errores:
        raise Rechazo(errores)
    return lote


def _git(args: list[str], raiz: Path) -> str:
    r = subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise Rechazo(f"falló `git {' '.join(args)}`: {r.stderr.strip()[:300]}")
    return r.stdout.strip()


def ejecutar(lote: list[dict], revisor: str, *, raiz: Path, rama: str, fecha: str) -> list[dict]:
    """Escribe y commitea en `rama` (sin push). Cada tarea se re-prepara contra el catálogo ya actualizado."""
    hechos = []
    for i, item in enumerate(lote):
        tid, exp = item["tid"], item["exp"]
        art = exp.artefactos
        plan = item["plan"] if i == 0 else bib.preparar(
            art["tarea"], item["guia"], art["evaluacion"], raiz=raiz, trazas=art.get("trazas_resumen"),
            texto_noticia=item["texto"], fecha_publicacion=fecha, icono_svg=_icono(tid, raiz))
        plan.rama = rama
        r = bib.ejecutar(plan, raiz=raiz, remoto=False)
        # expediente: sigue en `verificada`; guía con la revisión 2 y marca para la transición tras el merge
        nuevo = orq.Expediente.desde_dict(exp.a_dict())
        nuevo.artefactos["guia"] = item["guia"]
        nuevo.marcas["revision_humana_2"] = {"revisor": revisor.strip(), "fecha": fecha, "resultado": "aprobada",
                                             "nota": "publicar.yml"}
        nuevo.marcas["publicacion_propuesta"] = {"rama": rama, "ruta": plan.ruta, "commit": r["commit_tarea"]}
        orq.guardar(nuevo, raiz / "pipeline" / "state" / "expedientes")
        trabajo = raiz / "pipeline" / "state" / "trabajo" / tid / "guia.json"
        if trabajo.parent.exists():
            trabajo.write_text(json.dumps(item["guia"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _git(["add", "--", f"pipeline/state/expedientes/{tid}.json"]
             + ([f"pipeline/state/trabajo/{tid}/guia.json"] if trabajo.exists() else []), raiz)
        _git(["commit", "-q", "-m", f"pipeline: revisión humana 2 de {tid} ({revisor.strip()}); sigue en verificada"], raiz)
        hechos.append({"tid": tid, "ruta": plan.ruta, "commit": r["commit_tarea"], "entrada": plan.entrada})
    return hechos


def cuerpo_pr(hechos: list[dict], revisor: str, url_run: str = "") -> str:
    texto = bib.cuerpo_pr([h["entrada"] for h in hechos])
    pie = [f"Revisión humana 2 por **{revisor.strip()}** (input `revisor` de publicar.yml)."
           + (f" Ejecución: {url_run}" if url_run else ""), "",
           "Los expedientes siguen en `verificada`; pasan a `publicada` solo después del merge de este PR."]
    return texto + "\n\n" + "\n".join(pie) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ids", nargs="+")
    p.add_argument("--revisor", required=True)
    p.add_argument("--ejecutar", action="store_true", help="escribe y commitea (por defecto, dry-run)")
    p.add_argument("--rama", help="rama donde commitear (obligatoria con --ejecutar)")
    p.add_argument("--cuerpo", help="con --ejecutar: archivo donde escribir el cuerpo del PR")
    p.add_argument("--url-run", default="")
    p.add_argument("--raiz", default=str(RAIZ))
    p.add_argument("--fecha", help="fecha de publicación y de la revisión 2 (por defecto, hoy UTC)")
    a = p.parse_args(argv)
    raiz = Path(a.raiz)
    fecha = a.fecha or datetime.now(timezone.utc).date().isoformat()
    try:
        if a.ejecutar and not a.rama:
            raise Rechazo("--rama es obligatoria con --ejecutar")
        lote = preparar_todas(a.ids, a.revisor, raiz=raiz, fecha=fecha)
        if not a.ejecutar:
            print("# DRY-RUN: no se escribe ningún archivo ni se ejecuta ningún comando")
            for item in lote:
                pl = item["plan"]
                print(f"# {item['tid']} v{pl.version} -> {pl.ruta} (revisión 2: {a.revisor.strip()}, {fecha})")
                for n, _ in pl.archivos.values():
                    print(f"#   escribiría {pl.ruta}{n}")
            print(f"#   actualizaría {bib.RUTA_CATALOGO} y la marca revision_humana_2 de cada expediente")
            return 0
        hechos = ejecutar(lote, a.revisor, raiz=raiz, rama=a.rama, fecha=fecha)
        if a.cuerpo:
            Path(a.cuerpo).write_text(cuerpo_pr(hechos, a.revisor, a.url_run), encoding="utf-8")
        for h in hechos:
            print(f"publicable: {h['tid']} -> {h['ruta']} (commit {h['commit']})")
    except Rechazo as e:
        print("RECHAZADO:", *e.errores, sep="\n  - ", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
