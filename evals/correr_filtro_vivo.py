"""Corrida real del filtro: cada caso N veces; guarda evals/resultados/filtro_vivo_<fecha>.json.

    python evals/correr_filtro_vivo.py [--corridas 2] [--tope 1.0]
Usa pipeline.apikey (OTM_API_KEY / ANTHROPIC_API_KEY). Se detiene si el gasto supera --tope.
"""
import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from pipeline.agentes.filtro.run import CFG, VERSION_PROMPT, filtrar  # noqa: E402
from pipeline.llm import modelo_de  # noqa: E402

FECHA = "2026-10-20"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corridas", type=int, default=2)
    ap.add_argument("--tope", type=float, default=1.0)
    a = ap.parse_args()
    casos = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((RAIZ / "evals/casos/filtro").glob("*.json"))]
    gasto, filas = 0.0, []
    for c in casos:
        corr = []
        for i in range(a.corridas):
            if gasto >= a.tope:
                raise SystemExit(f"tope de gasto alcanzado ({gasto:.4f} USD)")
            r = filtrar(c["noticia"])
            f, m = r["noticia"]["filtro"], r["meta"]
            gasto += m["costo_usd"]
            corr.append({"puntajes": f["puntajes"], "total": f["total"], "pasa": f["pasa"],
                         "justificacion": f["justificacion"], "costo_usd": m["costo_usd"],
                         "request_id": m["request_id"], "uso": m["uso"]})
            print(c["id"], i + 1, f["total"], f["pasa"], m["costo_usd"], flush=True)
        esp = c["esperado"]
        decs = [x["pasa"] for x in corr]
        totales = [x["total"] for x in corr]
        filas.append({
            "caso": c["id"], "esperado": esp, "corridas": corr,
            "acuerdo_decision_entre_corridas": len(set(decs)) == 1,
            "acuerdo_total_exacto_entre_corridas": len(set(totales)) == 1,
            "diferencia_max_total": max(totales) - min(totales),
            "acuerdo_con_esperado": [d == esp["pasa"] for d in decs],
            "total_en_rango_esperado": [esp["total_min"] <= t <= esp["total_max"] for t in totales],
        })
    n = sum(len(f["corridas"]) for f in filas)
    resumen = {
        "fecha": FECHA, "agente": "filtro", "modelo": modelo_de("filtro"), "version_prompt": VERSION_PROMPT,
        "version_rubrica": CFG["version_rubrica"], "umbral": CFG["umbral"],
        "corridas_por_caso": a.corridas, "gasto_total_usd": round(gasto, 6),
        "acuerdo_decision_entre_corridas": f"{sum(f['acuerdo_decision_entre_corridas'] for f in filas)}/{len(filas)} casos",
        "acuerdo_total_exacto_entre_corridas": f"{sum(f['acuerdo_total_exacto_entre_corridas'] for f in filas)}/{len(filas)} casos",
        "acuerdo_decision_con_esperado": f"{sum(sum(f['acuerdo_con_esperado']) for f in filas)}/{n} corridas",
        "total_en_rango_esperado": f"{sum(sum(f['total_en_rango_esperado']) for f in filas)}/{n} corridas",
        "nota": "Los modelos 5.5 no aceptan temperature; la consistencia se mide como acuerdo entre corridas.",
    }
    out = RAIZ / "evals" / "resultados" / f"filtro_vivo_{FECHA}.json"
    out.write_text(json.dumps({"resumen": resumen, "casos": filas}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
