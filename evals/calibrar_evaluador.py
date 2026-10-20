"""Calibración del agente evaluador (RUB01 v4.0) contra las 9 tareas-oro.

Uso (desde la raíz del repo; la clave se lee con pipeline.apikey: OTM_API_KEY local):
    python evals/calibrar_evaluador.py --prompt 1.0            # 3 corridas × 9 tareas + informe
    python evals/calibrar_evaluador.py --solo-informe          # regenera el informe desde las corridas guardadas

Cada corrida es independiente: una llamada nueva por tarea, sin historial compartido (la caché de
prompt solo reutiliza el prefijo del system prompt; no transmite respuestas entre llamadas).

Salidas:
    evals/resultados/evaluador_corridas/prompt_v<X.Y>_<fecha>.json   (crudo, por versión de prompt)
    evals/resultados/calibracion_evaluador_v1.0_2026-10-20.{json,md} (informe consolidado)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from evals.casos.evaluador.cargar import cargar_todos  # noqa: E402
from evals.kappa import acuerdo_exacto, kappa_ponderado  # noqa: E402,F401  (re-export para tests)
from pipeline.agentes.evaluador import evaluador as ev  # noqa: E402

FECHA = "2026-10-20"
DIR_RES = RAIZ / "evals" / "resultados"
DIR_CORR = DIR_RES / "evaluador_corridas"
INFORME = DIR_RES / f"calibracion_evaluador_v1.0_{FECHA}"
UMBRAL = 0.7
PROVISIONALES_ESPERADAS = {"sugarloaf", "port-of-hamburg", "lighthouse", "st-michaels-church", "clear-day-at-the-ocean"}

# Historial de versiones del prompt (se documenta cada cambio; también en pipeline/state/decisiones.md).
CAMBIOS_PROMPT = {
    "1.0": "Versión inicial: RUB01 v4.0 completa (JSON literal, incluidas instrucciones_evaluador) y MAR03 §1 "
           "literales; procedimiento por criterio; cita literal ≤ 25 palabras antes de justificación y puntaje; "
           "regla de independencia entre criterios.",
    "1.1": "Ajuste 1 (κ v1.0 = 0,58–0,61; evaluador sistemáticamente más severo, sobre todo en ciclo, nivel, "
           "validación y autenticidad). Se reemplaza la frase «el 2 exige cumplimiento pleno con evidencia» por una "
           "lectura de descriptores que no exige más de lo que dicen; se acota «ante duda, el menor» a dudas genuinas "
           "entre descriptores adyacentes; se agregan lecturas fijas de los criterios 5 (procedencia declarada se toma "
           "como cierta), 7 («exige» = la resolución obliga a recorrer las fases), 8 («posible» = evidencia accesible, "
           "no necesariamente entregada) y 9 (no descontar de nuevo apertura/supuestos/validación), y una regla para "
           "textos que relatan una tarea implementada. RUB01 y MAR03 sin cambios.",
    "1.2": "Ajuste 2 (κ v1.1 = 0,72/0,69/0,73: corrida 2 bajo el umbral; v1.1 corrigió la severidad pero pasó a "
           "sobrepuntuar autodiferenciación y recursos, y a poner 0 donde hay presencia parcial). Se agrega una frontera "
           "0/1 simétrica a la del 2 (el 0 describe ausencia total) y lecturas fijas de los criterios 10 (piso = entrada "
           "sin una única idea clave; techo = la tarea misma admite soluciones más sofisticadas) y 12 (obtenibilidad real "
           "de la información para el nivel declarado). RUB01 y MAR03 sin cambios.",
    "1.3": "Ajuste 3, último permitido (κ v1.2 = 0,71/0,68/0,74: corrida 2 bajo el umbral). Se agrega la lectura del "
           "criterio 4 (realismo = la situación existe o es plausible; una pregunta de curiosidad o desafío sobre hechos "
           "reales no es un encuadre forzado; la necesidad se juzga en el criterio 1) y se precisa la regla para relatos "
           "de tareas implementadas: las fases que el relato recorre sin decir quién decidió se leen como proceso de los "
           "estudiantes; solo cuenta como entregado lo que el texto dice que se les dio. RUB01 y MAR03 sin cambios.",
}


def _git_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return None


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def gasto_previo() -> float:
    tot = 0.0
    for f in DIR_CORR.glob("prompt_v*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        tot += sum(r["meta"]["costo_usd"] for c in d["corridas"] for r in c["resultados"].values())
        tot += d.get("costo_fallidas", 0.0)
    return tot


def correr(version: str, n_corridas: int, presupuesto: float, paralelo: int) -> Path:
    import anthropic
    from pipeline.apikey import api_key

    casos = cargar_todos()
    ev.cargar_prompt(version)  # verifica que exista y contenga RUB01 literal
    cliente = anthropic.Anthropic(api_key=api_key(), max_retries=3)
    gastado = gasto_previo()
    por_llamada = 0.25  # estimación por llamada (USD, precio supuesto) para el control previo; observado ≈ 0,16
    necesario = n_corridas * len(casos) * por_llamada
    if gastado + necesario > presupuesto:
        raise SystemExit(f"Detenido: gasto previo {gastado:.2f} + estimado {necesario:.2f} > tope {presupuesto:.2f} USD")

    corridas = []
    fallidas = 0.0
    for k in range(1, n_corridas + 1):
        res, errores = {}, {}
        with ThreadPoolExecutor(max_workers=paralelo) as pool:
            fut = {pool.submit(ev.evaluar, c["entrada"], version, cliente=cliente): c["id"] for c in casos}
            for f in as_completed(fut):
                cid = fut[f]
                try:
                    res[cid] = f.result()
                    print(f"corrida {k} · {cid}: total {res[cid]['rub01']['total']} · "
                          f"{res[cid]['meta']['costo_usd']:.3f} USD", flush=True)
                except Exception as e:  # se registra; la corrida queda incompleta
                    errores[cid] = repr(e)
                    fallidas += getattr(e, "costo_usd", 0.0)
                    print(f"corrida {k} · {cid}: ERROR {e!r}", flush=True)
        corridas.append({"corrida": k, "resultados": {c["id"]: res[c["id"]] for c in casos if c["id"] in res},
                         "errores": errores})
        gastado += sum(r["meta"]["costo_usd"] for r in res.values())
        if gastado > presupuesto:
            print(f"Tope de gasto alcanzado ({gastado:.2f} USD); se detiene.")
            break

    import anthropic as _a
    salida = {
        "version_prompt": version,
        "cambio": CAMBIOS_PROMPT.get(version),
        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reproducibilidad": {
            "modelo": ev.MODELO, "effort": ev.ESFUERZO, "max_tokens": ev.MAX_TOKENS,
            "temperature": "no se envía (el modelo la rechaza: 'deprecated for this model')",
            "salida_estructurada": "output_config.format json_schema",
            "cache": "system prompt con cache_control ephemeral",
            "prompt_archivo": f"pipeline/agentes/evaluador/prompt_sistema_v{version}.md",
            "prompt_sha256": _sha(ev.DIR / f"prompt_sistema_v{version}.md"),
            "version_rubrica": ev.VERSION_RUBRICA, "rubrica_sha256": _sha(ev.RUB01_PATH),
            "version_mar03": ev.VERSION_MAR03,
            "referencia": "evals/oro/puntajes_v0.4_2026-10-20.csv",
            "referencia_sha256": _sha(RAIZ / "evals" / "oro" / "puntajes_v0.4_2026-10-20.csv"),
            "sdk_anthropic": _a.__version__, "python": platform.python_version(), "git_commit": _git_commit(),
            "precios_usd_mtok": ev.PRECIOS, "precios_pesimistas_usd_mtok": ev.PRECIOS_PESIMISTAS,
        },
        "corridas": corridas,
        "costo_fallidas": fallidas,
    }
    DIR_CORR.mkdir(parents=True, exist_ok=True)
    ruta = DIR_CORR / f"prompt_v{version}_{FECHA}.json"
    ruta.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta


# ---------------------------------------------------------------- análisis

def analizar(datos: dict, casos: list[dict]) -> dict:
    ref = {c["id"]: c["referencia"] for c in casos}
    ids_h = [c["id"] for c in casos if not c["referencia"]["provisional"]]
    ids_p = [c["id"] for c in casos if c["referencia"]["provisional"]]
    assert set(ids_p) == PROVISIONALES_ESPERADAS, ids_p
    out = {"version_prompt": datos["version_prompt"], "corridas": [], "por_criterio": {}, "diferencias_ge3": []}
    todas_a, todas_b = [], []
    for c in datos["corridas"]:
        res = c["resultados"]
        if len(res) != len(casos):
            out["corridas"].append({"corrida": c["corrida"], "incompleta": True, "errores": c["errores"]})
            continue

        def pares(ids, crits=ev.IDS):
            a = [res[t]["rub01"]["criterios"][i]["puntaje"] for t in ids for i in crits]
            b = [ref[t]["puntajes"][i] for t in ids for i in crits]
            return a, b

        todos = [x["id"] for x in casos]
        a, b = pares(todos)
        todas_a += a
        todas_b += b
        ah, bh = pares(ids_h)
        ap, bp = pares(ids_p)
        totales = {t: {"evaluador": res[t]["rub01"]["total"], "referencia": ref[t]["total"],
                       "dif": res[t]["rub01"]["total"] - ref[t]["total"]} for t in todos}
        for t, v in totales.items():
            if abs(v["dif"]) >= 3:
                out["diferencias_ge3"].append({"corrida": c["corrida"], "tarea": t, **v})
        avisos = [f"{t}:{a_}" for t in todos for a_ in res[t]["meta"]["avisos"]]
        out["corridas"].append({
            "corrida": c["corrida"],
            "kappa_global": kappa_ponderado(a, b), "n_pares": len(a), "acuerdo_exacto": acuerdo_exacto(a, b),
            "kappa_humanas": kappa_ponderado(ah, bh), "n_pares_humanas": len(ah),
            "acuerdo_exacto_humanas": acuerdo_exacto(ah, bh),
            "kappa_provisionales": kappa_ponderado(ap, bp), "n_pares_provisionales": len(ap),
            "totales": totales,
            "publicables_evaluador": sorted(t for t in todos if res[t]["rub01"]["total"] >= 20
                                            and min(x["puntaje"] for x in res[t]["rub01"]["criterios"].values()) > 0),
            "costo_usd": sum(res[t]["meta"]["costo_usd"] for t in todos),
            "costo_usd_pesimista": sum(res[t]["meta"]["costo_usd_pesimista"] for t in todos),
            "tokens": {k: sum(res[t]["meta"]["uso"].get(k) or 0 for t in todos)
                       for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens",
                                 "cache_read_input_tokens", "thinking_tokens")},
            "avisos": avisos,
        })
    completas = [c for c in datos["corridas"] if len(c["resultados"]) == len(casos)]
    for i in ev.IDS:
        a = [c["resultados"][t]["rub01"]["criterios"][i]["puntaje"] for c in completas for t in ref]
        b = [ref[t]["puntajes"][i] for c in completas for t in ref]
        por_corrida = []
        for c in completas:
            aa = [c["resultados"][t]["rub01"]["criterios"][i]["puntaje"] for t in ref]
            bb = [ref[t]["puntajes"][i] for t in ref]
            por_corrida.append(kappa_ponderado(aa, bb))
        out["por_criterio"][i] = {"kappa_agrupado": kappa_ponderado(a, b) if a else None, "n_pares": len(a),
                                  "acuerdo_exacto": acuerdo_exacto(a, b) if a else None,
                                  "kappa_por_corrida": por_corrida,
                                  "media_evaluador": mean(a) if a else None, "media_referencia": mean(b) if b else None}
    # consistencia entre corridas (evaluador vs. evaluador)
    cons = []
    for x in range(len(completas)):
        for y in range(x + 1, len(completas)):
            a = [completas[x]["resultados"][t]["rub01"]["criterios"][i]["puntaje"] for t in ref for i in ev.IDS]
            b = [completas[y]["resultados"][t]["rub01"]["criterios"][i]["puntaje"] for t in ref for i in ev.IDS]
            cons.append({"corridas": [completas[x]["corrida"], completas[y]["corrida"]],
                         "kappa": kappa_ponderado(a, b), "acuerdo_exacto": acuerdo_exacto(a, b)})
    out["consistencia_entre_corridas"] = cons
    out["kappa_global_agrupado"] = kappa_ponderado(todas_a, todas_b) if todas_a else None
    ks = [c.get("kappa_global") for c in out["corridas"]]
    out["n_corridas_completas"] = len(completas)
    out["acepta"] = len(completas) >= 3 and all(k is not None and k >= UMBRAL for k in ks)
    out["costo_usd"] = sum(c.get("costo_usd", 0) for c in out["corridas"])
    out["costo_usd_pesimista"] = sum(c.get("costo_usd_pesimista", 0) for c in out["corridas"])
    return out


def _f(x, d=3):
    return "indef." if x is None else f"{x:.{d}f}".replace(".", ",")


def informe(analisis: list[dict], crudos: list[dict], casos: list[dict]) -> None:
    final = analisis[-1]
    crudo_final = crudos[-1]
    j = {
        "informe": "calibracion_evaluador", "version_informe": "1.0", "fecha": FECHA,
        "advertencia": ("5 de los 9 puntajes de referencia (sugarloaf, port-of-hamburg, lighthouse, "
                        "st-michaels-church, clear-day-at-the-ocean) son provisionales, puestos por Claude "
                        "(2026-10-20). El kappa no se reporta como validez hasta la doble codificación humana."),
        "umbral_kappa": UMBRAL, "version_prompt_final": final["version_prompt"], "acepta": final["acepta"],
        "historial_prompt": [{"version": a["version_prompt"], "cambio": c.get("cambio"), "acepta": a["acepta"],
                              "kappa_por_corrida": [x.get("kappa_global") for x in a["corridas"]],
                              "costo_usd": a["costo_usd"]} for a, c in zip(analisis, crudos)],
        "costo_total_usd": sum(a["costo_usd"] for a in analisis),
        "costo_total_usd_pesimista": sum(a["costo_usd_pesimista"] for a in analisis),
        "reproducibilidad": crudo_final["reproducibilidad"],
        "analisis": analisis,
    }
    Path(str(INFORME) + ".json").write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")

    L = []
    w = L.append
    w(f"# Calibración del agente evaluador (RUB01 v4.0) — informe v1.0, {FECHA}\n")
    w("> **ADVERTENCIA.** 5 de los 9 puntajes de referencia (Sugarloaf, Port of Hamburg, Lighthouse, "
      "St. Michael's Church, A Clear Day at the Ocean) son **provisionales, puestos por Claude** (2026-10-20), "
      "un modelo de la misma familia que el evaluador. El acuerdo medido contra ellos está probablemente inflado. "
      "**Este kappa no se reporta como validez** hasta la doble codificación humana (Hugo/Mahsa). "
      "Se reporta por separado el kappa contra las 4 tareas codificadas por un humano (Abiam Muñoz).\n")
    r = crudo_final["reproducibilidad"]
    w("## Resultado\n")
    w(f"- Prompt final: `{r['prompt_archivo']}` (sha256 `{r['prompt_sha256'][:12]}…`).")
    w(f"- Modelo: `{r['modelo']}`, effort `{r['effort']}`, temperatura: {r['temperature']}; salida: {r['salida_estructurada']}.")
    w(f"- Criterio de aceptación: kappa ponderado cuadrático ≥ {_f(UMBRAL, 1)} en cada una de 3 corridas independientes "
      f"(108 pares criterio × tarea por corrida).")
    w(f"- **{'ACEPTA' if final['acepta'] else 'NO ACEPTA'}** con prompt v{final['version_prompt']}.")
    w(f"- Costo total de la calibración (todas las versiones): {_f(j['costo_total_usd'], 2)} USD "
      f"(precio supuesto 5/25 USD por MTok; con precio pesimista 15/75: {_f(j['costo_total_usd_pesimista'], 2)} USD).\n")

    w("## Kappa por corrida (prompt final)\n")
    w("| Corrida | κ global (108) | Acuerdo exacto | κ solo humanas (48) | Acuerdo exacto humanas | κ solo provisionales (60) | Costo USD |")
    w("|---|---|---|---|---|---|---|")
    for c in final["corridas"]:
        if c.get("incompleta"):
            w(f"| {c['corrida']} | incompleta | | | | | |")
            continue
        w(f"| {c['corrida']} | {_f(c['kappa_global'])} | {_f(c['acuerdo_exacto'], 2)} | {_f(c['kappa_humanas'])} | "
          f"{_f(c['acuerdo_exacto_humanas'], 2)} | {_f(c['kappa_provisionales'])} | {_f(c['costo_usd'], 2)} |")
    w(f"\nκ global agrupado (3 corridas, {3 * 108} pares): {_f(final['kappa_global_agrupado'])}.\n")

    w("## Kappa por criterio (prompt final, 27 pares = 9 tareas × 3 corridas)\n")
    w("| Criterio | κ agrupado | κ por corrida | Acuerdo exacto | Media evaluador | Media referencia |")
    w("|---|---|---|---|---|---|")
    for i, v in final["por_criterio"].items():
        w(f"| {i} | {_f(v['kappa_agrupado'])} | {' / '.join(_f(x) for x in v['kappa_por_corrida'])} | "
          f"{_f(v['acuerdo_exacto'], 2)} | {_f(v['media_evaluador'], 2)} | {_f(v['media_referencia'], 2)} |")
    w("\nκ indefinido = la referencia y el evaluador son constantes en ese criterio (desacuerdo esperado 0). "
      "Con 9 tareas, el κ por criterio es muy inestable: un solo desacuerdo en un criterio casi constante lo hunde; "
      "léase junto al acuerdo exacto.\n")

    w("## Totales por tarea (prompt final)\n")
    ids = [c["id"] for c in casos]
    comp = [c for c in final["corridas"] if not c.get("incompleta")]
    w("| Tarea | Referencia | Codificador | " + " | ".join(f"Corrida {c['corrida']}" for c in comp) + " |")
    w("|---|---|---|" + "---|" * len(comp))
    for c in casos:
        t = c["id"]
        w(f"| {t} | {c['referencia']['total']} | {'Claude (prov.)' if c['referencia']['provisional'] else 'humano'} | "
          + " | ".join(f"{x['totales'][t]['evaluador']} ({x['totales'][t]['dif']:+d})" for x in comp) + " |")
    w("\n### Tareas con |total − referencia| ≥ 3\n")
    if final["diferencias_ge3"]:
        for d in final["diferencias_ge3"]:
            w(f"- Corrida {d['corrida']}: **{d['tarea']}** — evaluador {d['evaluador']}, referencia {d['referencia']} ({d['dif']:+d}).")
    else:
        w("- Ninguna.")
    w("\n### Decisión de publicación (≥ 20 y ningún 0)\n")
    for x in comp:
        w(f"- Corrida {x['corrida']}: publica {', '.join(x['publicables_evaluador']) or '—'}.")
    w("- Referencia: publican las 8 positivas; quedan fuera poblacion-belga y clear-day-at-the-ocean.\n")

    w("## Consistencia entre corridas (evaluador vs. evaluador, 108 pares)\n")
    for c in final["consistencia_entre_corridas"]:
        w(f"- Corridas {c['corridas'][0]}–{c['corridas'][1]}: κ {_f(c['kappa'])}, acuerdo exacto {_f(c['acuerdo_exacto'], 2)}.")
    avisos = [a for x in comp for a in x["avisos"]]
    w(f"\nAvisos de post-proceso (citas no literales, mejoras sobrantes descartadas, total del modelo distinto): {len(avisos)}"
      + (f" — {', '.join(avisos[:15])}{' …' if len(avisos) > 15 else ''}" if avisos else "") + "\n")

    kh = [c["kappa_humanas"] for c in comp]
    w("## Limitaciones (leer antes de usar el resultado)\n")
    w(f"- **El umbral se cumple por poco** (mínimo por corrida {_f(min(c['kappa_global'] for c in comp))}). "
      f"Contra las 4 tareas humanas solamente, κ por corrida = {' / '.join(_f(k) for k in kh)}"
      f"{' (bajo 0,7)' if any(k is None or k < UMBRAL for k in kh) else ''}: "
      "el cumplimiento global descansa en parte sobre los puntajes provisionales de Claude.")
    w("- **Riesgo de sobreajuste:** los tres ajustes del prompt se decidieron mirando los desacuerdos en estas mismas "
      "9 tareas (no hay conjunto de prueba separado). El prompt no contiene las tareas-oro ni sus puntajes, y cada "
      "ajuste es una lectura general de un descriptor de RUB01, pero el κ de la versión final es optimista. "
      "Recalibrar con tareas nuevas y con la doble codificación humana.")
    w("- **Variabilidad entre corridas:** el modelo no acepta temperatura 0; con el mismo prompt los totales de una "
      "tarea varían hasta en varios puntos (ver Sugarloaf: 24 / 22 / 17), y eso puede cambiar la decisión de publicar.")
    w("- **κ por criterio** con 9 tareas es inestable e indefinido donde la referencia es constante (nivel; realismo casi "
      "constante): no sirve para juzgar criterios individuales.")
    w("- **Costo:** el precio de Opus 5.5 no está documentado en el repo; se supuso 5/25 USD por MTok. Verificar en la "
      "Console. No incluye ~0,17 USD de sondeos de API y una prueba de humo previas a las corridas.\n")

    w("## Historial de versiones del prompt\n")
    w("| Versión | Cambio | κ por corrida | Acepta | Costo USD |")
    w("|---|---|---|---|---|")
    for h in j["historial_prompt"]:
        w(f"| {h['version']} | {h['cambio']} | {' / '.join(_f(k) for k in h['kappa_por_corrida'])} | "
          f"{'sí' if h['acepta'] else 'no'} | {_f(h['costo_usd'], 2)} |")
    w("\n## Reproducibilidad\n")
    for k, v in r.items():
        w(f"- `{k}`: {v}")
    w("\n## Notas de método\n")
    w("- Kappa ponderado cuadrático implementado a mano (`evals/kappa.py`, test en `tests/test_kappa.py`).")
    w("- Entrada al evaluador: nivel declarado, título, texto de la tarea (extraído de `insumos/tareas-oro/` con "
      "verificación sha256; Sugarloaf: traducción de trabajo de INS02 v0.2 §1.2 y descripción de foto §6.3) y recursos "
      "declarados. No recibe puntajes, rol de calibración ni las notas evaluativas de las autoras.")
    w("- Las tareas de Abiam (residuos-plasticos, vapes-litio, poblacion-belga) son descripciones o extractos de la "
      "fuente, no enunciados para estudiantes; el evaluador lo sabe por el campo «Tipo de texto».")
    w("- El total se recalcula en código; las mejoras se filtran a criterios en 0 o 1.")
    Path(str(INFORME) + ".md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", default=ev.VERSION_PROMPT)
    p.add_argument("--corridas", type=int, default=3)
    p.add_argument("--presupuesto", type=float, default=15.0, help="tope USD (precio supuesto de lista, ver evaluador.PRECIOS)")
    p.add_argument("--paralelo", type=int, default=3)
    p.add_argument("--solo-informe", action="store_true")
    a = p.parse_args()
    if not a.solo_informe:
        correr(a.prompt, a.corridas, a.presupuesto, a.paralelo)
    casos = cargar_todos()

    def clave(f):
        return tuple(int(x) for x in f.name.split("_")[1][1:].split("."))

    archivos = sorted(DIR_CORR.glob("prompt_v*.json"), key=clave)
    crudos = [json.loads(f.read_text(encoding="utf-8")) for f in archivos]
    analisis = [analizar(d, casos) for d in crudos]
    informe(analisis, crudos, casos)
    for an in analisis:
        print(f"prompt v{an['version_prompt']}: kappa por corrida "
              f"{[round(c['kappa_global'], 3) if c.get('kappa_global') is not None else None for c in an['corridas']]} "
              f"acepta={an['acepta']} costo={an['costo_usd']:.2f} USD")


if __name__ == "__main__":
    main()
