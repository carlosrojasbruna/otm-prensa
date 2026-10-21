"""Tras el merge de un PR `publicar/*` (lo usa .github/workflows/publicada.yml): `verificada` -> `publicada`.

Busca en main los expedientes en `verificada` cuya marca `publicacion_propuesta.rama` es la rama del PR, comprueba
que el catálogo de main ya tenga esa versión y hace la transición con el orquestador: valida contra contratos/
(invariante 1), exige la revisión humana 2 en la guía y usa como revisor el de la marca `revision_humana_2`.

Solo cambia el estado: `estado` del expediente, su espejo `tarea.estado` y la entrada de `historial` que el
orquestador escribe en toda transición. No toca otros artefactos ni marcas, ni `tareas/`. El PR y el merge van en
el motivo de la transición y en el mensaje del commit.

Uso: python -m pipeline.marcar_publicadas --rama publicar/AAAA-MM-DD-N --pr 12 --merge abc1234 [--raiz R]
Código de salida: 0 ok (imprime los ids); 2 error (no se escribió nada); 3 ningún expediente de esa rama.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from pipeline import orquestador as orq  # noqa: E402
from pipeline.agentes.bibliotecario.run import RUTA_CATALOGO, id_base  # noqa: E402


class Error(Exception):
    pass


def de_la_rama(rama: str, raiz: Path) -> list[orq.Expediente]:
    exps = []
    for ruta in sorted((raiz / "pipeline" / "state" / "expedientes").glob("*.json")):
        exp = orq.Expediente.desde_dict(json.loads(ruta.read_text(encoding="utf-8")))
        if exp.estado == "verificada" and exp.marcas.get("publicacion_propuesta", {}).get("rama") == rama:
            exps.append(exp)
    return exps


def marcar(rama: str, pr: str, merge: str, *, raiz: Path) -> list[str]:
    exps = de_la_rama(rama, raiz)
    if not exps:
        return []
    catalogo = json.loads((raiz / RUTA_CATALOGO).read_text(encoding="utf-8"))
    versiones = {t["id"]: t["version"] for t in catalogo["tareas"]}
    nuevos, errores = [], []
    for exp in exps:
        tarea = exp.artefactos["tarea"]
        if versiones.get(id_base(exp.tarea_id)) != tarea["version"]:
            errores.append(f"{exp.tarea_id}: el catálogo de main no tiene la v{tarea['version']}")
            continue
        revisor = (exp.marcas.get("revision_humana_2") or {}).get("revisor")
        try:
            nuevos.append(orq.transicionar(exp, "publicada", revisor=revisor,
                                           motivo=f"PR #{pr} mergeado ({merge}); publicada.yml"))
        except orq.ErrorOrquestador as e:
            errores.append(f"{exp.tarea_id}: {e} {list(getattr(e, 'errores', ()))}")
    if errores:
        raise Error("; ".join(errores))
    for nuevo in nuevos:                                  # todo o nada: se escribe solo si todos pasan
        orq.guardar(nuevo, raiz / "pipeline" / "state" / "expedientes")
        espejo = raiz / "pipeline" / "state" / "trabajo" / nuevo.tarea_id / "tarea.json"
        if espejo.exists():
            t = json.loads(espejo.read_text(encoding="utf-8"))
            t["estado"] = "publicada"
            espejo.write_text(json.dumps(t, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return [n.tarea_id for n in nuevos]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rama", required=True)
    p.add_argument("--pr", required=True)
    p.add_argument("--merge", required=True)
    p.add_argument("--raiz", default=str(RAIZ))
    a = p.parse_args(argv)
    try:
        ids = marcar(a.rama, a.pr, a.merge, raiz=Path(a.raiz))
    except Error as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if not ids:
        print(f"ningún expediente en `verificada` con publicacion_propuesta.rama = {a.rama}", file=sys.stderr)
        return 3
    print(" ".join(ids))
    return 0


if __name__ == "__main__":
    sys.exit(main())
