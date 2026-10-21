"""Fusiona el gasto semanal de varias copias de `gasto_semanal.json` (main + rama semanal abierta).

El tope (GOB01 §3) se calcula con `gasto_semanal.json`. En Actions el ciclo corre sobre una rama
`semanal/<AAAA-WW>` que se mergea después de la revisión humana, así que el archivo de `main` puede no
incluir ciclos ya gastados (rama o PR abiertos). Lectura conservadora: antes de correr, el workflow suma
al archivo base los ciclos (por `ciclo_id`) que solo existen en las otras copias. Nunca resta gasto.

    python -m pipeline.gasto_ramas BASE.json OTRA.json [OTRA2.json ...]   # reescribe BASE.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def fusionar(base: dict, *otros: dict) -> tuple[dict, list[str]]:
    """Devuelve (base fusionada, ciclos agregados 'semana/ciclo_id'). No modifica los argumentos."""
    res = json.loads(json.dumps(base))
    res.setdefault("semanas", {})
    agregados: list[str] = []
    for otro in otros:
        for semana, datos in (otro.get("semanas") or {}).items():
            dest = res["semanas"].setdefault(semana, {"usd": 0.0, "ciclos": []})
            conocidos = {c["ciclo_id"] for c in dest["ciclos"]}
            for c in datos.get("ciclos", []):
                if c["ciclo_id"] in conocidos:
                    continue
                dest["ciclos"].append(c)
                dest["usd"] = round(dest["usd"] + float(c["usd"]), 6)
                conocidos.add(c["ciclo_id"])
                agregados.append(f"{semana}/{c['ciclo_id']}")
    return res, agregados


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    base_ruta = Path(argv[0])
    cargar = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))  # noqa: E731
    res, agregados = fusionar(cargar(base_ruta), *[cargar(p) for p in argv[1:]])
    base_ruta.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"gasto_semanal: {len(agregados)} ciclo(s) agregado(s) desde otras copias")
    for a in agregados:
        print("  +", a)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
