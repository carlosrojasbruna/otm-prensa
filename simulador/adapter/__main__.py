"""CLI: python -m simulador.adapter {caso1|caso2|lanzar} ..."""
import argparse
import json
import sys

from . import casos


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m simulador.adapter")
    ap.add_argument("orden", choices=["caso1", "caso2"])
    ap.add_argument("--run", default="N1_AA_r1")
    ap.add_argument("--solo", nargs="*")
    ap.add_argument("--tope", type=float, default=None, help="presupuesto USD para esta orden")
    ap.add_argument("--backend", choices=["api", "claude_p"], default=None)
    ap.add_argument("--sufijo", default="")
    a = ap.parse_args(argv)
    if a.orden == "caso1":
        r = casos.caso1_reproducir(a.run, backend=a.backend, presupuesto_usd=a.tope, sufijo=a.sufijo)
    else:
        r = casos.caso2_sugarloaf(backend=a.backend, presupuesto_usd=a.tope, solo=a.solo)
        r = {k: v for k, v in r.items() if k != "trazas"} | {"corridas_traducidas": r["trazas"] and r["trazas"]["corridas"]}
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    sys.exit(main())
