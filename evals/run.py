"""Matriz modelo x agente del pipeline OTM-Prensa (eval-engineer, fase 3).

Para cada agente corre sus casos con claude-haiku-5-5, claude-sonnet-5-5 y claude-opus-5-5, mide la
métrica del agente, el costo y la latencia por celda, y recomienda "el modelo más barato que pasa el
umbral del agente". Escribe evals/resultados/matriz_<fecha>.md y .json (datos crudos).

Uso (desde la raíz del repo; la clave la lee pipeline/apikey.py: OTM_API_KEY, luego ANTHROPIC_API_KEY):
    python evals/run.py                                  # los 9 agentes x 3 modelos, tope 12 USD
    python evals/run.py --agentes filtro,explorador --modelos haiku,sonnet
    python evals/run.py --sin-red                        # ClienteFalso: prueba la tubería, no mide modelos
    python evals/run.py --reanudar                       # omite los agentes ya guardados en *_datos/

Reglas de gasto (estrictas):
- Toda llamada a la API pasa por ClienteMedido: antes de cada llamada se reserva su peor caso
  (entrada estimada + max_tokens a precio de salida) y, si superaría el tope total o el del agente,
  se lanza PresupuestoAgotado y la unidad queda "no corrida". Nunca se supera el tope.
- Precios: pipeline/config.yaml (precios_modelos). Los modelos 5.5 no aceptan `temperature`: no se envía.
- Evaluador/Opus no se vuelve a correr: se reutilizan las corridas de calibración v1.3 (se recosteo con
  los precios de config.yaml).
- El modelo de cada agente se cambia sin tocar los agentes: pipeline.llm.forzar_modelo (modelo_de) y,
  donde un agente recibe el modelo por parámetro (evaluador, simulador), se pasa explícito.
"""
from __future__ import annotations

import argparse
import copy
import importlib
import importlib.util
import json
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from evals.kappa import acuerdo_exacto, kappa_ponderado  # noqa: E402
from pipeline import invariantes as inv  # noqa: E402
from pipeline.llm import ClienteFalso, config, costo_usd, forzar_modelo  # noqa: E402

FECHA = "2026-10-20"
DIR_RES = RAIZ / "evals" / "resultados"
CASOS = RAIZ / "evals" / "casos"
VERSION_RUN = "1.0"

AGENTES = ["explorador", "filtro", "disenador", "evaluador", "simulador", "redactor", "ilustrador",
           "verificador", "bibliotecario"]
ALIAS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
TOPE_USD = 12.0
# Reserva por agente (el tope total manda): evita que un agente caro deje sin presupuesto a los demás.
TOPES_AGENTE = {"simulador": 4.5, "disenador": 3.5, "evaluador": 1.5, "redactor": 1.4, "filtro": 0.5,
                "ilustrador": 0.5, "verificador": 0.3, "explorador": 0.2}
EVALUADOR_REF = "claude-opus-5-5"          # evaluador de producción: puntúa las salidas del diseñador
TRAZAS_SINRED = DIR_RES / "sim_adapter" / "caso2_sugarloaf" / "trazas" / "trazas_resumen.json"
CORRIDAS_OPUS = DIR_RES / "evaluador_corridas" / "prompt_v1.3_2026-10-20.json"
ORO_CSV = RAIZ / "evals" / "oro" / "puntajes_v0.4_2026-10-20.csv"
RE_PITAGORAS = re.compile(r"pit[aá]gor|hipotenusa|cateto", re.I)

# Umbral por agente. `umbral` es el valor mínimo de `metrica` para que una celda "pase".
UMBRALES = {
    "explorador": {"metrica": "pct_casos_ok", "umbral": 0.8,
                   "texto": "Fracción de los 5 casos que cumplen el resultado esperado (aceptada: valida contra `noticia`, "
                            "medio en MED01, cifras con localizador, <= 25 palabras literales; descartada: sin noticia y con "
                            "el motivo esperado). Umbral >= 0,8 (a lo más 1 de 5 falla)."},
    "filtro": {"metrica": "kappa_decision", "umbral": 0.6,
               "texto": "Kappa de Cohen de la decisión pasa/no pasa contra la decisión esperada de los 5 casos, 3 corridas "
                        "por caso (15 pares). Umbral >= 0,6 (regla del plan para subir a Sonnet). Se informan además la "
                        "consistencia entre corridas y el total dentro del rango esperado."},
    "disenador": {"metrica": "pct_rub01_ge20", "umbral": 0.8,
                  "texto": "Fracción de los 5 casos cuyo primer candidato (o la tarea iterada) valida contra `tarea` y obtiene "
                           "RUB01 >= 20/24 sin ningún criterio en 0 según el evaluador de producción (Opus 5.5, prompt v1.3, "
                           "1 corrida). Umbral >= 0,8."},
    "evaluador": {"metrica": "kappa_ponderado", "umbral": 0.7,
                  "texto": "Kappa ponderado cuadrático contra evals/oro/puntajes_v0.4 (9 tareas x 12 criterios = 108 pares) "
                           "en cada corrida disponible (Opus: 3 corridas de calibración v1.3; Haiku y Sonnet: 1). Umbral >= 0,7 "
                           "en todas. Se informa aparte el kappa contra las 4 tareas humanas (no provisionales)."},
    "simulador": {"metrica": "pct_corridas_validas", "umbral": 1.0,
                  "texto": "Sugarloaf S1, 2 lanzadas de 6 corridas por modelo (estudiantes y codificador con el mismo modelo). "
                           "Pasa si todas las corridas se codifican y `trazas_resumen` valida contra el contrato y, además, a lo "
                           "más la mitad de las corridas de perfil N1 usan Pitágoras (el perfil N1 declara que no lo conoce: "
                           "fidelidad al perfil, punto 4 de 'Para CP2'). Umbral definido por eval-engineer; revisable en CP2."},
    "redactor": {"metrica": "pct_casos_ok", "umbral": 1.0,
                 "texto": "Fracción de los casos medibles en vivo (1 y 2: guía completa; 3: debe fallar con TrazasInsuficientes sin "
                          "llamar al modelo) cuya guía valida contra `guia`, escenarios respaldados por trazas y cifras con "
                          "localizador. Los casos 4 y 5 inducen el error con respuestas scripteadas y no son medibles en vivo. "
                          "Umbral 1,0: un error en la guía llega a docentes. Ambos modelos del redactor (secciones base e "
                          "intervenciones, y escenarios) se fuerzan al modelo de la celda."},
    "ilustrador": {"metrica": "pct_casos_ok", "umbral": 0.8,
                   "texto": "Fracción de los 5 casos para los que el agente entrega un SVG que pasa el validador (seguridad, paleta, "
                            "tamaño, viewBox) y una `foto_descripcion` coherente, en <= 1 reparación. Umbral >= 0,8."},
    "verificador": {"metrica": "pct_casos_ok", "umbral": 1.0,
                    "texto": "Fracción de los 5 casos en los que el informe coincide con lo esperado (aprobado, estado destino, "
                             "invariantes críticas). Solo el caso 1 llama al modelo; los otros 4 los resuelve el código. Umbral 1,0: "
                             "el verificador es una compuerta."},
    "bibliotecario": {"metrica": "n/a", "umbral": None,
                      "texto": "Es un script determinista (sin modelo): celda N/A. Se reportan sus tests sin red."},
}


# ------------------------------------------------------------------ utilidades
def precio_salida(modelo: str) -> float:
    return config()["precios_modelos"][modelo]["output"]


def modelos_por_precio(modelos: list[str]) -> list[str]:
    return sorted(modelos, key=precio_salida)


def corto(modelo: str) -> str:
    return modelo.replace("claude-", "").replace("-5-5", "")


def f(x, d: int = 2) -> str:
    """Número con coma decimal (convención de los informes del repo)."""
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "sí" if x else "no"
    return f"{x:.{d}f}".replace(".", ",")


def log(*a) -> None:
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ------------------------------------------------------------------ presupuesto y medidor
class PresupuestoAgotado(RuntimeError):
    """Se detiene la unidad: la llamada superaría el tope (total o del agente)."""


class Presupuesto:
    """Contabilidad con reserva del peor caso por llamada. Segura entre hilos."""

    def __init__(self, tope_total: float, topes_agente: dict | None = None):
        self.tope = tope_total
        self.topes_agente = dict(topes_agente or {})
        self.gastado = 0.0
        self.gastado_agente: dict[str, float] = {}
        self.en_vuelo = 0.0
        self.en_vuelo_agente: dict[str, float] = {}
        self.agotado: dict[str, str] = {}      # agente -> motivo
        self.llamadas: list[dict] = []
        self._lock = threading.Lock()

    def precargar(self, agente: str, usd: float, etiqueta: str = "reanudado") -> None:
        """Gasto de una corrida anterior (reanudada, completada o descartada): cuenta en el total y el tope."""
        with self._lock:
            self.gastado += usd
            if etiqueta.startswith("descartado"):
                self.gastado_agente[agente] = self.gastado_agente.get(agente, 0.0)   # no consume el tope del agente
            else:
                self.gastado_agente[agente] = self.gastado_agente.get(agente, 0.0) + usd
            self.llamadas.append({"agente": agente, "rol": etiqueta, "modelo": "(varios)", "costo_usd": usd,
                                  "segundos": 0.0})

    def reservar(self, agente: str, peor_caso: float) -> None:
        with self._lock:
            ga = self.gastado_agente.get(agente, 0.0) + self.en_vuelo_agente.get(agente, 0.0)
            tope_a = self.topes_agente.get(agente)
            if self.gastado + self.en_vuelo + peor_caso > self.tope:
                motivo = (f"tope total {self.tope:.2f} USD (gastado {self.gastado:.3f}, en vuelo {self.en_vuelo:.3f}, "
                          f"peor caso de la llamada {peor_caso:.3f})")
            elif tope_a is not None and ga + peor_caso > tope_a:
                motivo = f"tope del agente {tope_a:.2f} USD (gastado {ga:.3f}, peor caso {peor_caso:.3f})"
            else:
                self.en_vuelo += peor_caso
                self.en_vuelo_agente[agente] = self.en_vuelo_agente.get(agente, 0.0) + peor_caso
                return
            self.agotado.setdefault(agente, motivo)
        raise PresupuestoAgotado(motivo)

    def liquidar(self, agente: str, reservado: float, real: float, registro: dict | None = None) -> None:
        with self._lock:
            self.en_vuelo -= reservado
            self.en_vuelo_agente[agente] = self.en_vuelo_agente.get(agente, 0.0) - reservado
            self.gastado += real
            self.gastado_agente[agente] = self.gastado_agente.get(agente, 0.0) + real
            if registro is not None:
                self.llamadas.append(registro)


def peor_caso_usd(kw: dict) -> float:
    """Cota superior del costo de una llamada: entrada (estimada con 2,5 caracteres por token, al precio
    de escritura de caché) + max_tokens completos a precio de salida."""
    p = config()["precios_modelos"][kw["model"]]
    texto = json.dumps(kw.get("system", ""), ensure_ascii=False) + json.dumps(kw.get("messages", []), ensure_ascii=False)
    if kw.get("output_config"):
        texto += json.dumps(kw["output_config"], ensure_ascii=False)
    tin = len(texto) / 2.5
    return tin * max(p["input"], p["cache_write"]) / 1e6 + kw.get("max_tokens", 4096) * p["output"] / 1e6


class ClienteMedido:
    """Envuelve un cliente (Anthropic o ClienteFalso): reserva presupuesto, mide costo y latencia reales
    y registra el modelo realmente solicitado. Los agentes lo reciben por `cliente=`."""

    def __init__(self, base, presupuesto: Presupuesto, agente: str, rol: str | None = None):
        self.base = base
        self.presupuesto = presupuesto
        self.agente = agente
        self.rol = rol or agente
        self.llamadas: list[dict] = []
        self.messages = self

    def create(self, **kw):
        reservado = peor_caso_usd(kw)
        self.presupuesto.reservar(self.agente, reservado)
        t0 = time.time()
        try:
            r = self.base.messages.create(**kw)
        except BaseException:
            self.presupuesto.liquidar(self.agente, reservado, 0.0)
            raise
        dt = time.time() - t0
        uso = {k: getattr(r.usage, k, 0) or 0 for k in
               ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
        real = costo_usd(uso, kw["model"])
        reg = {"agente": self.agente, "rol": self.rol, "modelo": kw["model"], "costo_usd": real,
               "segundos": round(dt, 2), **uso}
        self.llamadas.append(reg)
        self.presupuesto.liquidar(self.agente, reservado, real, reg)
        return r

    def resumen(self) -> dict:
        return {"costo_usd": round(sum(c["costo_usd"] for c in self.llamadas), 6),
                "n_llamadas": len(self.llamadas),
                "segundos_api": round(sum(c["segundos"] for c in self.llamadas), 2),
                "modelos_solicitados": sorted({c["modelo"] for c in self.llamadas}),
                "tokens": {k: sum(c[k] for c in self.llamadas) for k in
                           ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}}


class Ctx:
    def __init__(self, presupuesto: Presupuesto, sin_red: bool, dir_datos: Path, args=None):
        self.p = presupuesto
        self.sin_red = sin_red
        self.dir_datos = dir_datos
        self.args = args
        self.previas: dict[tuple, dict] = {}   # (agente, modelo, id) -> unidad ya medida (modo --completar)
        self._base = None
        self._lock = threading.Lock()

    def base(self, fakes=None):
        if self.sin_red:
            return ClienteFalso(copy.deepcopy(fakes if fakes is not None else []))
        with self._lock:
            if self._base is None:
                import anthropic
                from pipeline.apikey import api_key
                self._base = anthropic.Anthropic(api_key=api_key(), max_retries=3)
        return self._base

    def cliente(self, agente: str, fakes=None, rol: str | None = None) -> ClienteMedido:
        return ClienteMedido(self.base(fakes), self.p, agente, rol)


def unidad(ctx: Ctx, agente: str, uid: str, fn, fakes=None, esperados: set | None = None) -> dict:
    """Ejecuta una unidad de medición. fn(cliente) -> (ok: bool, detalle: dict[, clientes_extra])."""
    if esperados and len(esperados) == 1:
        previa = ctx.previas.get((agente, next(iter(esperados)), uid))
        if previa is not None:
            return previa
    cli = ctx.cliente(agente, fakes)
    t0 = time.time()
    r = {"id": uid, "ok": None, "omitida": False, "error": None, "detalle": {}}
    extra: list[ClienteMedido] = []
    try:
        out = fn(cli)
        r["ok"], r["detalle"] = out[0], out[1]
        if len(out) > 2:
            extra = out[2]
    except PresupuestoAgotado as e:
        r["omitida"], r["error"] = True, f"PresupuestoAgotado: {e}"
    except Exception as e:  # noqa: BLE001 - un fallo del agente cuenta como caso no cumplido
        r["ok"], r["error"] = False, f"{type(e).__name__}: {str(e)[:300]}"
    r["segundos"] = round(time.time() - t0, 2)
    r.update(cli.resumen())
    for ex in extra:   # evaluaciones auxiliares: se reportan aparte, no entran al costo de la celda
        rs = ex.resumen()
        r["auxiliar"] = {"rol": ex.rol, "costo_usd": rs["costo_usd"], "n_llamadas": rs["n_llamadas"],
                         "segundos_api": rs["segundos_api"], "modelos_solicitados": rs["modelos_solicitados"]}
    if esperados and r["modelos_solicitados"] and not set(r["modelos_solicitados"]) <= esperados:
        r["ok"] = False
        r["error"] = f"modelo distinto del forzado: {r['modelos_solicitados']} (esperado {sorted(esperados)})"
    return r


def finalizar_celda(agente: str, modelo: str, unidades: list[dict], metrica: dict, *, pasa_extra=True,
                    extra: dict | None = None, notas: list[str] | None = None) -> dict:
    """Arma la celda: costo, latencia, estado y 'pasa' a partir de las unidades y la métrica."""
    um = UMBRALES[agente]
    omit = [u for u in unidades if u["omitida"]]
    corridas = [u for u in unidades if not u["omitida"]]
    con_llamada = [u for u in corridas if u["n_llamadas"] > 0]
    costo = round(sum(u["costo_usd"] for u in unidades), 6)
    aux = round(sum(u.get("auxiliar", {}).get("costo_usd", 0.0) for u in unidades), 6)
    if not corridas:
        estado = "no_corrida"
    elif omit:
        estado = "parcial"
    else:
        estado = "completa"
    valor = metrica.get("valor")
    pasa = None
    if estado == "completa" and valor is not None and um["umbral"] is not None:
        pasa = bool(valor >= um["umbral"] and pasa_extra)
    elif estado == "completa" and valor is None:
        pasa = False
    celda = {
        "agente": agente, "modelo": modelo, "estado": estado,
        "metrica": {"nombre": um["metrica"], "umbral": um["umbral"], **metrica},
        "pasa": pasa,
        "costo_usd": costo, "costo_auxiliar_usd": aux,
        "costo_por_unidad_usd": round(costo / len(con_llamada), 6) if con_llamada else None,
        "latencia_media_s": round(sum(u["segundos"] for u in con_llamada) / len(con_llamada), 1) if con_llamada else None,
        "latencia_max_s": round(max(u["segundos"] for u in con_llamada), 1) if con_llamada else None,
        "n_unidades": len(unidades), "n_unidades_corridas": len(corridas), "n_unidades_omitidas": len(omit),
        "n_llamadas": sum(u["n_llamadas"] for u in unidades),
        "modelos_solicitados": sorted({m for u in unidades for m in u["modelos_solicitados"]}),
        "unidades": unidades, "notas": notas or [],
    }
    if extra:
        celda.update(extra)
    return celda


def celda_na(agente: str, modelo: str, motivo: str, extra: dict | None = None) -> dict:
    c = {"agente": agente, "modelo": modelo, "estado": "n/a", "metrica": {"nombre": UMBRALES[agente]["metrica"],
         "umbral": UMBRALES[agente]["umbral"], "valor": None}, "pasa": None, "costo_usd": 0.0,
         "costo_auxiliar_usd": 0.0, "costo_por_unidad_usd": None, "latencia_media_s": None, "latencia_max_s": None,
         "n_unidades": 0, "n_unidades_corridas": 0, "n_unidades_omitidas": 0, "n_llamadas": 0,
         "modelos_solicitados": [], "unidades": [], "notas": [motivo]}
    if extra:
        c.update(extra)
    return c


def pct_ok(unidades: list[dict]) -> dict:
    corr = [u for u in unidades if not u["omitida"]]
    ok = sum(1 for u in corr if u["ok"])
    return {"valor": round(ok / len(corr), 4) if corr else None, "ok": ok, "n": len(corr),
            "detalle_por_caso": {u["id"]: u["ok"] for u in corr}}


def _j(p: Path):
    return json.loads(Path(p).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ explorador
def correr_explorador(ctx: Ctx, modelos: list[str]) -> list[dict]:
    ex = importlib.import_module("pipeline.agentes.explorador.run")
    ahora = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
    casos = [_j(p) for p in sorted((CASOS / "explorador").glob("caso_*.json"))]
    celdas = []
    for modelo in modelos:
        us = []
        with forzar_modelo("explorador", modelo):
            for caso in casos:
                def fn(cli, caso=caso):
                    cand = dict(caso["entrada"])
                    cand["fecha"] = datetime.fromisoformat(cand["fecha"]).replace(tzinfo=timezone.utc)
                    try:
                        res = ex.explorar_noticia(cand, cliente=cli, ahora=ahora, bajar=None)
                    except TypeError:
                        res = ex.explorar_noticia(cand, cliente=cli, ahora=ahora)
                    esp = caso["esperado"]
                    n = res["noticia"]
                    if esp["resultado"] == "aceptada":
                        ok = bool(n) and bool(inv.validar_contra_esquema(n, "noticia")) \
                            and bool(inv.medio_en_lista_blanca(n["medio_id"])) and bool(n["cifras"]) \
                            and all(c["localizador"]["ubicacion"] for c in n["cifras"])
                        cuerpo = "\n".join(ex.parrafos_de(caso["entrada"]["cuerpo_html"]))
                        if ok:
                            ok = bool(inv.cumple_limite_literal({k: v for k, v in n.items() if k != "titulo"}, cuerpo))
                        det = {"esperado": "aceptada", "n_cifras": len(n["cifras"]) if n else 0,
                               "descartada": res["descartada"]}
                    else:
                        ok = n is None and esp["motivo_contiene"] in (res["descartada"] or "")
                        det = {"esperado": "descartada", "motivo": res["descartada"]}
                    return ok, det
                us.append(unidad(ctx, "explorador", caso["id"], fn, fakes=caso.get("respuestas_modelo"),
                                 esperados={modelo}))
        celdas.append(finalizar_celda("explorador", modelo, us, pct_ok(us)))
    return celdas


# ------------------------------------------------------------------ filtro
def correr_filtro(ctx: Ctx, modelos: list[str]) -> list[dict]:
    fl = importlib.import_module("pipeline.agentes.filtro.run")
    n_corr = getattr(ctx.args, "corridas_filtro", 3)
    casos = [_j(p) for p in sorted((CASOS / "filtro").glob("*.json"))]
    celdas = []
    for modelo in modelos:
        us = []
        with forzar_modelo("filtro", modelo):
            for caso in casos:
                for k in range(1, n_corr + 1):
                    def fn(cli, caso=caso):
                        r = fl.filtrar(caso["noticia"], cliente=cli)
                        fi = r["noticia"]["filtro"]
                        esp = caso["esperado"]
                        return fi["pasa"] == esp["pasa"], {
                            "pasa": fi["pasa"], "total": fi["total"], "esperado_pasa": esp["pasa"],
                            "total_en_rango": esp["total_min"] <= fi["total"] <= esp["total_max"]}
                    fk = [caso["respuesta_falsa"]] if "respuesta_falsa" in caso else None
                    us.append(unidad(ctx, "filtro", f"{caso['id']}#{k}", fn, fakes=fk, esperados={modelo}))
        celdas.append(finalizar_celda("filtro", modelo, us, metrica_filtro(us, casos)))
    return celdas


def metrica_filtro(us: list[dict], casos: list[dict]) -> dict:
    """Kappa de la decisión contra la esperada (15 pares) + consistencia entre corridas."""
    corr = [u for u in us if not u["omitida"] and u["error"] is None]
    dec = [int(u["detalle"]["pasa"]) for u in corr]
    esp = [int(u["detalle"]["esperado_pasa"]) for u in corr]
    kappa = kappa_ponderado(dec, esp, categorias=(0, 1)) if dec else None
    por_caso = {}
    for c in casos:
        ds = [u["detalle"]["pasa"] for u in corr if u["id"].startswith(c["id"] + "#")]
        ts = [u["detalle"]["total"] for u in corr if u["id"].startswith(c["id"] + "#")]
        if ds:
            por_caso[c["id"]] = {"decisiones": ds, "totales": ts, "consistente": len(set(ds)) == 1,
                                 "esperado": c["esperado"]["pasa"]}
    errores = [u for u in us if not u["omitida"] and u["error"]]
    return {"valor": None if kappa is None else round(kappa, 4), "n_pares": len(dec),
            "acuerdo_exacto": round(acuerdo_exacto(dec, esp), 4) if dec else None,
            "consistencia_casos": f"{sum(v['consistente'] for v in por_caso.values())}/{len(por_caso)}",
            "total_en_rango": f"{sum(1 for u in corr if u['detalle']['total_en_rango'])}/{len(corr)}",
            "errores_agente": len(errores), "por_caso": por_caso,
            "nota": "kappa indefinido (None) si las decisiones son constantes" if kappa is None and dec else None}


# ------------------------------------------------------------------ evaluador
def _referencias() -> list[dict]:
    from evals.casos.evaluador.cargar import cargar_todos
    return cargar_todos()


def _resp_evaluador_falsa(caso: dict) -> dict:
    """Respuesta sintética (solo --sin-red): copia los puntajes de referencia."""
    ev = importlib.import_module("pipeline.agentes.evaluador.evaluador")
    cita = " ".join(caso["entrada"]["texto"].split()[:6])
    crit, mej = {}, []
    for i in ev.IDS:
        p = caso["referencia"]["puntajes"][i]
        crit[i] = {"cita": cita, "justificacion": "sintética", "puntaje": p}
        if p < 2:
            mej.append({"criterio": i, "mejora_minima": "sintética"})
    return {"version_rubrica": ev.VERSION_RUBRICA, "criterios": crit, "total": sum(c["puntaje"] for c in crit.values()),
            "mejoras": mej}


def kappas_evaluador(resultados: dict[str, dict], casos: list[dict]) -> dict:
    """resultados: tarea_id -> rub01. Kappa global y contra las tareas humanas (no provisionales)."""
    ev = importlib.import_module("pipeline.agentes.evaluador.evaluador")
    ref = {c["id"]: c["referencia"] for c in casos}
    ids = [c["id"] for c in casos if c["id"] in resultados]
    ids_h = [t for t in ids if not ref[t]["provisional"]]

    def pares(lista):
        return ([resultados[t]["criterios"][i]["puntaje"] for t in lista for i in ev.IDS],
                [ref[t]["puntajes"][i] for t in lista for i in ev.IDS])
    a, b = pares(ids)
    ah, bh = pares(ids_h)
    return {"kappa_global": kappa_ponderado(a, b) if a else None, "n_pares": len(a),
            "acuerdo_exacto": acuerdo_exacto(a, b) if a else None,
            "kappa_humanas": kappa_ponderado(ah, bh) if ah else None, "n_pares_humanas": len(ah),
            "acuerdo_exacto_humanas": acuerdo_exacto(ah, bh) if ah else None,
            "n_tareas": len(ids),
            "totales": {t: {"evaluador": resultados[t]["total"], "referencia": ref[t]["total"]} for t in ids}}


def correr_evaluador(ctx: Ctx, modelos: list[str]) -> list[dict]:
    ev = importlib.import_module("pipeline.agentes.evaluador.evaluador")
    casos = _referencias()
    celdas = []
    for modelo in modelos:
        if modelo == "claude-opus-5-5":
            celdas.append(_evaluador_opus_reutilizado(casos))
            continue
        us, res = [], {}
        prev = ev.MODELO
        try:
            ev.MODELO = modelo
            with forzar_modelo("evaluador", modelo):
                def hacer(caso, modelo=modelo):
                    def fn(cli):
                        r = ev.evaluar(caso["entrada"], modelo=modelo, cliente=cli)
                        res[caso["id"]] = r["rub01"]
                        return True, {"total": r["rub01"]["total"], "avisos": r["meta"]["avisos"]}
                    fk = [_resp_evaluador_falsa(caso)] if ctx.sin_red else None
                    return unidad(ctx, "evaluador", caso["id"], fn, fakes=fk, esperados={modelo})
                with ThreadPoolExecutor(max_workers=3) as pool:
                    us = list(pool.map(hacer, casos))
        finally:
            ev.MODELO = prev
        k = kappas_evaluador(res, casos)
        completa = k["n_tareas"] == len(casos)
        valor = None if k["kappa_global"] is None else round(k["kappa_global"], 4)
        m = {"valor": valor, "corridas": 1, "kappa_por_corrida": [valor],
             "kappa_humanas": _r(k["kappa_humanas"]), "acuerdo_exacto": _r(k["acuerdo_exacto"]),
             "acuerdo_exacto_humanas": _r(k["acuerdo_exacto_humanas"]), "n_tareas": k["n_tareas"],
             "totales": k["totales"], "reutilizada": False}
        c = finalizar_celda("evaluador", modelo, us, m, pasa_extra=completa,
                            notas=["1 corrida sobre las 9 tareas-oro; kappa total incluye 5 puntajes provisionales de Claude"])
        celdas.append(c)
    return celdas


def _r(x, d=4):
    return None if x is None else round(x, d)


def _evaluador_opus_reutilizado(casos: list[dict]) -> dict:
    """Opus no se vuelve a correr: kappas y costos de las 3 corridas de calibración v1.3 (recosteo con config.yaml)."""
    datos = _j(CORRIDAS_OPUS)
    kap, costos, lat, tot_h = [], [], [], []
    for c in datos["corridas"]:
        res = {t: r["rub01"] for t, r in c["resultados"].items()}
        k = kappas_evaluador(res, casos)
        kap.append(k)
        costos.append(sum(costo_usd(r["meta"]["uso"], "claude-opus-5-5") for r in c["resultados"].values()))
        lat += [r["meta"]["segundos"] for r in c["resultados"].values()]
    ks = [k["kappa_global"] for k in kap]
    kh = [k["kappa_humanas"] for k in kap]
    n_unid = sum(len(c["resultados"]) for c in datos["corridas"])
    valor = round(sum(ks) / len(ks), 4)
    um = UMBRALES["evaluador"]["umbral"]
    c = celda_na("evaluador", "claude-opus-5-5", "Reutilizada: corridas de calibración v1.3 (evals/resultados/evaluador_corridas/"
                 "prompt_v1.3_2026-10-20.json); no se volvió a llamar a la API. Costos recalculados con config.yaml (4/20 USD/MTok); "
                 "la calibración los registró con el supuesto 5/25.")
    c.update({
        "estado": "reutilizada", "pasa": bool(all(k is not None and k >= um for k in ks)),
        "metrica": {"nombre": "kappa_ponderado", "umbral": um, "valor": valor, "corridas": len(ks),
                    "kappa_por_corrida": [_r(k) for k in ks], "kappa_min": _r(min(ks)),
                    "kappa_humanas": _r(sum(kh) / len(kh)), "kappa_humanas_por_corrida": [_r(k) for k in kh],
                    "acuerdo_exacto": _r(sum(k["acuerdo_exacto"] for k in kap) / len(kap)),
                    "acuerdo_exacto_humanas": _r(sum(k["acuerdo_exacto_humanas"] for k in kap) / len(kap)),
                    "n_tareas": kap[0]["n_tareas"], "reutilizada": True},
        "costo_usd": 0.0, "costo_reutilizado_usd": round(sum(costos), 4),
        "costo_por_unidad_usd": round(sum(costos) / n_unid, 6),
        "latencia_media_s": round(sum(lat) / len(lat), 1), "latencia_max_s": round(max(lat), 1),
        "n_unidades": n_unid, "n_unidades_corridas": 0, "n_llamadas": 0,
        "modelos_solicitados": ["claude-opus-5-5"],
    })
    return c


# ------------------------------------------------------------------ diseñador
def tarea_a_entrada_evaluador(t: dict) -> dict:
    """Entrada del evaluador a partir de una `tarea` PLT01: lo que ve el estudiante + recursos + mapa del ciclo.
    No incluye task_space ni puntajes."""
    est = t["estudiante"]
    texto = est["enunciado_es"].strip()
    foto = (est.get("foto_descripcion") or "").strip()
    if foto and foto.lower() != "none":
        texto += f"\n\nFotografía o ilustración que acompaña: {foto}"
    rec = [f"{r['id']} · {r['que_es']} (a solicitud, fase {r.get('fase', '—')}): {r['contenido']}"
           for r in est.get("recursos_a_solicitud", [])]
    rec += [f"{r['id']} · {r['que_es']} (de entrada): {r['contenido']}" for r in t.get("recursos_de_entrada", [])]
    mapa = "\n".join(f"- {k}: {v['decision']}" + (f" (bloqueo probable {v['bloqueo_probable']})" if v.get("bloqueo_probable") else "")
                     for k, v in t["mapa_ciclo"].items())
    niv = {"nivel": t["nivel_principal"]}
    if t.get("sub_tramo") and t["sub_tramo"] != "ninguno":
        niv["sub_tramo"] = t["sub_tramo"]
    return {"titulo": t["titulo"], "nivel_declarado": niv, "forma_texto": "enunciado para estudiantes",
            "texto": texto, "recursos": rec, "mapa_ciclo": mapa}


def cumple_publicacion(rub01: dict) -> bool:
    ps = [c["puntaje"] for c in rub01["criterios"].values()]
    return sum(ps) >= 20 and min(ps) > 0


def _resp_eval_falsa_generica() -> dict:
    ev = importlib.import_module("pipeline.agentes.evaluador.evaluador")
    crit = {i: {"cita": "", "justificacion": "sintética", "puntaje": 2 if k else 1}
            for k, i in enumerate(ev.IDS)}
    return {"version_rubrica": ev.VERSION_RUBRICA, "criterios": crit, "total": sum(c["puntaje"] for c in crit.values()),
            "mejoras": [{"criterio": ev.IDS[0], "mejora_minima": "sintética"}]}


def correr_disenador(ctx: Ctx, modelos: list[str]) -> list[dict]:
    dis = importlib.import_module("pipeline.agentes.disenador.run")
    ev = importlib.import_module("pipeline.agentes.evaluador.evaluador")
    casos = [_j(p) for p in sorted((CASOS / "disenador").glob("*.json"))]
    celdas = []
    for modelo in modelos:
        us = []
        with forzar_modelo("disenador", modelo):
            for caso in casos:
                def fn(cli, caso=caso):
                    if caso["modo"] == "diseno":
                        r = dis.disenar(caso["noticia"], caso["nivel"], fecha="2026-10-20", cliente=cli)
                        tarea = r["candidatos"][0]
                    else:
                        r = dis.iterar(caso["tarea_previa"], caso["evaluacion"], caso["noticia"], fecha="2026-10-20", cliente=cli)
                        tarea = r["tarea"]
                    val = inv.validar_contra_esquema(tarea, "tarea")
                    det = {"modo": caso["modo"], "contrato_valido": bool(val), "rondas": r["meta"].get("rondas"),
                           "n_candidatos": len(r["candidatos"]) if "candidatos" in r else 1}
                    if not val:
                        return False, det
                    cev = ctx.cliente("disenador", [_resp_eval_falsa_generica()] if ctx.sin_red else None, rol="disenador/evaluacion")
                    try:
                        e = ev.evaluar(tarea_a_entrada_evaluador(tarea), modelo=EVALUADOR_REF, cliente=cev)
                    except PresupuestoAgotado:
                        det["evaluacion"] = "omitida por presupuesto"
                        raise
                    rub = e["rub01"]
                    ps = [c["puntaje"] for c in rub["criterios"].values()]
                    det.update({"rub01_total": rub["total"], "criterios_en_0": [i for i, c in rub["criterios"].items() if c["puntaje"] == 0],
                                "criterios_en_1": [i for i, c in rub["criterios"].items() if c["puntaje"] == 1],
                                "evaluador": EVALUADOR_REF, "min_criterio": min(ps)})
                    return cumple_publicacion(rub), det, [cev]
                us.append(unidad(ctx, "disenador", caso["id"], fn, fakes=caso.get("respuestas_simuladas"), esperados={modelo}))
        m = pct_ok(us)
        tot = [u["detalle"]["rub01_total"] for u in us if not u["omitida"] and "rub01_total" in u["detalle"]]
        m.update({"rub01_media": round(sum(tot) / len(tot), 2) if tot else None, "rub01_totales": tot,
                  "pct_contrato_valido": round(sum(1 for u in us if not u["omitida"] and u["detalle"].get("contrato_valido")) /
                                               max(1, sum(1 for u in us if not u["omitida"])), 4)})
        celdas.append(finalizar_celda("disenador", modelo, us, m, notas=[
            f"RUB01 por una sola corrida del evaluador {corto(EVALUADOR_REF)} (la variabilidad entre corridas llega a varios "
            "puntos, ver calibración); el costo de la evaluación se reporta aparte (costo_auxiliar_usd)."]))
    return celdas


# ------------------------------------------------------------------ simulador
def metricas_simulador(trazas: dict) -> dict:
    """Punto 4 de 'Para CP2': pct_validan y uso de Pitágoras (sobre-competencia) por perfil."""
    cor = trazas["por_corrida"]

    def usa(c):
        txt = " ".join([c.get("modelo") or "", str(c.get("respuesta_final") or ""), " ".join(c.get("supuestos") or [])])
        return bool(RE_PITAGORAS.search(txt))
    n1 = [c for c in cor if c["perfil"]["nivel"] == "N1"]
    return {"n_corridas": len(cor), "pct_validan": trazas["agregado"].get("pct_validan"),
            "pct_pitagoras": round(sum(usa(c) for c in cor) / len(cor), 4) if cor else None,
            "pct_pitagoras_N1": round(sum(usa(c) for c in n1) / len(n1), 4) if n1 else None,
            "n_pitagoras": sum(usa(c) for c in cor), "n_N1": len(n1), "n_pitagoras_N1": sum(usa(c) for c in n1),
            "modelos_observados": trazas["agregado"].get("modelos_observados"),
            "pct_bloqueo_por_transicion": trazas["agregado"].get("pct_bloqueo_por_transicion"),
            "pitagoras_por_perfil": {f"{c['perfil']['nivel']}_{c['perfil']['estilo']}": usa(c) for c in cor}}


def _unidad_sim(ctx: Ctx, modelo: str, k: int, tarea: dict, nombre_cap: float) -> dict:
    lanz = importlib.import_module("simulador.adapter.lanzador")

    def fn(cli):
        if ctx.sin_red:
            trazas = _j(TRAZAS_SINRED)
            errores = []
        else:
            dir_t = ctx.dir_datos / "simulador" / f"{corto(modelo)}_l{k}"
            res = lanz.lanzar(tarea, dir_t, cliente=cli, modelo_estudiantes=modelo, modelo_codificador=modelo,
                              workers=3, presupuesto_usd=nombre_cap)
            trazas, errores = res["trazas"], res["errores"]
            if any("PresupuestoAgotado" in e or "tope de gasto" in e for e in errores):
                raise PresupuestoAgotado("; ".join(errores)[:200])
        if trazas is None:
            return False, {"errores": errores}
        v = inv.validar_contra_esquema(trazas, "trazas_resumen")
        c = inv.consistencia_trazas(trazas)
        det = metricas_simulador(trazas)
        det.update({"errores": errores, "trazas_validas": bool(v) and bool(c),
                    "errores_contrato": list(v.errores)[:3] + list(c.errores)[:3]})
        return (not errores) and bool(v) and bool(c) and det["n_corridas"] == 6, det
    return unidad(ctx, "simulador", f"{corto(modelo)}_lanzada{k}", fn, esperados={modelo})


def correr_simulador(ctx: Ctx, modelos: list[str]) -> list[dict]:
    n_l = getattr(ctx.args, "lanzadas_simulador", 2)
    if ctx.sin_red:
        tarea = None
    else:
        tarea = importlib.import_module("simulador.adapter.casos").tarea_sugarloaf()
    por_modelo: dict[str, list[dict]] = {m: [] for m in modelos}
    for k in range(1, n_l + 1):          # primero la lanzada 1 de todos los modelos: si el tope corta, corta lo último
        for modelo in modelos:
            restante = min(ctx.p.topes_agente.get("simulador", 99) - ctx.p.gastado_agente.get("simulador", 0.0),
                           ctx.p.tope - ctx.p.gastado)
            with forzar_modelo("simulador", modelo):
                por_modelo[modelo].append(_unidad_sim(ctx, modelo, k, tarea, max(restante, 0.01)))
    celdas = []
    for modelo in modelos:
        us = por_modelo[modelo]
        corr = [u for u in us if not u["omitida"] and u["detalle"]]
        n_cor = sum(u["detalle"].get("n_corridas", 0) for u in corr)
        n_val = sum(u["detalle"].get("n_corridas", 0) for u in corr if u["detalle"].get("trazas_validas") and not u["detalle"].get("errores"))
        n1 = sum(u["detalle"]["n_N1"] for u in corr)
        n1p = sum(u["detalle"]["n_pitagoras_N1"] for u in corr)
        npit = sum(u["detalle"]["n_pitagoras"] for u in corr)
        pv = [u["detalle"]["pct_validan"] for u in corr if u["detalle"].get("pct_validan") is not None]
        esperadas = 6 * len([u for u in us if not u["omitida"]])
        m = {"valor": round(n_val / esperadas, 4) if esperadas else None, "corridas_validas": n_val, "corridas_esperadas": esperadas,
             "pct_validan": round(sum(pv) / len(pv), 4) if pv else None,
             "pct_pitagoras": round(npit / n_cor, 4) if n_cor else None,
             "pct_pitagoras_N1": round(n1p / n1, 4) if n1 else None, "n_pitagoras_N1": f"{n1p}/{n1}",
             "n_pitagoras": f"{npit}/{n_cor}", "lanzadas": len(us)}
        fidelidad = m["pct_pitagoras_N1"] is not None and m["pct_pitagoras_N1"] <= 0.5
        celdas.append(finalizar_celda("simulador", modelo, us, m, pasa_extra=fidelidad, notas=[
            "estudiantes y codificador usan el modelo de la celda (en producción el codificador es Opus 5.5)"
            + ("; --sin-red: métricas calculadas sobre trazas ya existentes (Sonnet), no miden este modelo" if ctx.sin_red else "")]))
    return celdas


# ------------------------------------------------------------------ redactor
def _cargar_redactor(nombre: str, R) -> tuple:
    d = CASOS / "redactor" / nombre
    return (_j(d / "tarea.json"), _j(d / "trazas_resumen.json"), R.cargar_transcripciones(d / "transcripciones"),
            _j(d / "contexto.json"), _j(d / "respuestas_falsas.json"), _j(d / "criterio.json"))


def correr_redactor(ctx: Ctx, modelos: list[str]) -> list[dict]:
    R = importlib.import_module("pipeline.agentes.redactor.run")
    nombres = sorted(p.name for p in (CASOS / "redactor").iterdir() if p.is_dir())
    celdas = []
    for modelo in modelos:
        us = []
        with forzar_modelo("redactor", modelo), forzar_modelo("redactor_escenarios", modelo):
            for nombre in nombres:
                tarea, trazas, trans, cx, resp, crit = _cargar_redactor(nombre, R)
                en_vivo = crit["resultado"] == "ok" or crit.get("llamadas_esperadas") == 0
                if not en_vivo and not ctx.sin_red:
                    continue   # error inducido por respuestas scripteadas: no medible con el modelo real

                def fn(cli, tarea=tarea, trazas=trazas, trans=trans, cx=cx, crit=crit):
                    if crit["resultado"] == "ok":
                        r = R.redactar(tarea, trazas, trans, cx, cliente=cli)
                        g = r["guia"]
                        v = inv.validar_contra_esquema(g, "guia")
                        e = inv.escenarios_respaldados(g, trazas)
                        ok = bool(v) and bool(e) and 3 <= len(g["escenarios"]) <= 4
                        return ok, {"esperado": "ok", "n_escenarios": len(g["escenarios"]), "guia_valida": bool(v),
                                    "escenarios_respaldados": bool(e)}
                    try:
                        R.redactar(tarea, trazas, trans, cx, cliente=cli)
                    except getattr(R, crit["error"]) as e:
                        ok = ("seccion" not in crit or getattr(e, "seccion", None) == crit["seccion"]) and \
                             crit.get("contiene", "") in str(e)
                        return ok, {"esperado": crit["error"], "obtenido": type(e).__name__}
                    return False, {"esperado": crit["error"], "obtenido": "sin error"}
                us.append(unidad(ctx, "redactor", nombre.split("-")[0], fn, fakes=resp,
                                 esperados={modelo}))
        c = finalizar_celda("redactor", modelo, us, pct_ok(us), notas=[
            "casos 4 y 5 (error inducido con respuestas scripteadas) no se miden en vivo"] if not ctx.sin_red else [])
        celdas.append(c)
    return celdas


# ------------------------------------------------------------------ ilustrador
def _tarea_ilustrador(caso: dict) -> dict:
    t = _j(RAIZ / caso["entrada"]["tarea_base"])
    for k, v in caso["entrada"]["reemplazos"].items():
        d = t
        *ruta, ultima = k.split(".")
        for p in ruta:
            d = d[p]
        d[ultima] = v
    return t


def correr_ilustrador(ctx: Ctx, modelos: list[str]) -> list[dict]:
    ilu = importlib.import_module("pipeline.agentes.ilustrador.run")
    casos = [_j(p) for p in sorted((CASOS / "ilustrador").glob("*.json"))]
    celdas = []
    for modelo in modelos:
        us = []
        with forzar_modelo("ilustrador", modelo):
            for caso in casos:
                def fn(cli, caso=caso):
                    tarea = _tarea_ilustrador(caso)
                    crit = caso["criterio_aceptacion"]
                    if ctx.sin_red and crit["resultado"] == "rechaza":
                        try:
                            ilu.ilustrar(tarea, cliente=cli)
                        except ValueError:
                            return True, {"esperado": "rechaza", "obtenido": "rechaza"}
                        return False, {"esperado": "rechaza", "obtenido": "acepta"}
                    s = ilu.ilustrar(tarea, cliente=cli)
                    errs = ilu.validar_salida(s)
                    return not errs and set(s["paleta_usada"]) <= ilu.PALETA, {
                        "esperado": "acepta", "errores": errs[:3], "reparaciones": s["meta"].get("intentos_reparacion"),
                        "bytes_svg": len(s["svg"].encode("utf-8"))}
                us.append(unidad(ctx, "ilustrador", caso["id"], fn, fakes=caso.get("respuestas_modelo"), esperados={modelo}))
        celdas.append(finalizar_celda("ilustrador", modelo, us, pct_ok(us), notas=[
            "en vivo los 5 casos se miden sobre su entrada (esperado: SVG válido); las respuestas scripteadas de los casos 3 y 4 "
            "solo existen en --sin-red"]))
    return celdas


# ------------------------------------------------------------------ verificador
def _modulo_verificador():
    try:
        return importlib.import_module("pipeline.agentes.verificador.run")
    except ImportError:
        ruta = RAIZ / "pipeline" / "agentes" / "verificador" / "run.py"
        spec = importlib.util.spec_from_file_location("verificador_run", ruta)
        m = importlib.util.module_from_spec(spec)
        sys.modules["verificador_run"] = m
        spec.loader.exec_module(m)
        return m


def correr_verificador(ctx: Ctx, modelos: list[str]) -> list[dict]:
    V = _modulo_verificador()
    dir_c = CASOS / "verificador"
    ej = {k: _j(RAIZ / "contratos" / "ejemplos" / f"{k}_ejemplo.json") for k in ("tarea", "guia", "trazas_resumen", "noticia")}
    casos = [_j(p) for p in sorted(dir_c.glob("caso*.json"))]
    celdas = []
    for modelo in modelos:
        us = []
        with forzar_modelo("verificador", modelo):
            for caso in casos:
                def fn(cli, caso=caso):
                    base = {"tarea": ej["tarea"], "guia": ej["guia"], "trazas": ej["trazas_resumen"], "noticia": ej["noticia"]}
                    base = V.aplicar_mutaciones(base, caso["mutaciones"])
                    nb = dir_c / caso["notebook"] if caso["notebook"] else None
                    inf = V.verificar(base["tarea"], base["guia"], base["trazas"], base["noticia"] if caso["con_noticia"] else None,
                                      caso["texto_noticia"], nb, cli)
                    esp = caso["esperado"]
                    crit = {h["invariante"] for h in inf["hallazgos"] if h["severidad"] == "critico"}
                    ok = (inf["aprobado"] is esp["aprobado"] and inf["estado_destino"] == esp["estado_destino"]
                          and crit == set(esp["invariantes_criticas"]))
                    return ok, {"aprobado": inf["aprobado"], "esperado_aprobado": esp["aprobado"],
                                "llamo_al_modelo": inf["meta"]["modelo_llamado"], "criticas": sorted(crit),
                                "esperadas": sorted(esp["invariantes_criticas"]),
                                "hallazgos_criticos": [f"{h['invariante']} · {h['ubicacion']}: {h['descripcion']}"[:260]
                                                       for h in inf["hallazgos"] if h["severidad"] == "critico"]}
                us.append(unidad(ctx, "verificador", caso["id"], fn, fakes=[caso["respuesta_modelo"]], esperados={modelo}))
        celdas.append(finalizar_celda("verificador", modelo, us, pct_ok(us), notas=[
            "solo el caso 1 depende del modelo; los casos 2 a 5 los decide el código (costo 0 y resultado idéntico entre modelos)"]))
    return celdas


# ------------------------------------------------------------------ bibliotecario (script)
def correr_bibliotecario(ctx: Ctx, modelos: list[str]) -> list[dict]:
    tests = {"corridos": False}
    if not getattr(ctx.args, "sin_tests_bibliotecario", False):
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                            "tests/test_agente_bibliotecario.py"], cwd=RAIZ, capture_output=True, text=True)
        resumen = (r.stdout.strip().splitlines() or [""])[-1]
        tests = {"corridos": True, "resumen": resumen, "returncode": r.returncode,
                 "passed": int(m.group(1)) if (m := re.search(r"(\d+) passed", resumen)) else 0}
    return [celda_na("bibliotecario", m, "script determinista, sin modelo", {"tests_sin_red": tests}) for m in modelos]


# ------------------------------------------------------------------ recomendación
CAVEAT_METRICA = {
    "explorador": "Métrica de contrato e invariantes sobre 5 casos sintéticos: no mide la calidad del resumen ni la cobertura de cifras en noticias reales.",
    "redactor": "Métrica de contrato e invariantes (guía válida, escenarios respaldados, cifras con localizador), no de calidad pedagógica: "
                "la revisión humana 2 sigue siendo el control de calidad de la guía.",
    "ilustrador": "Métrica de validez del SVG (seguridad, paleta, tamaño), no de calidad visual ni pertinencia de la imagen.",
}


def recomendar(agente: str, celdas: list[dict], modelo_partida: str | None) -> dict:
    """El más barato (por precio de salida de lista) cuya celda pasa el umbral."""
    um = UMBRALES[agente]
    if um["umbral"] is None:
        return {"agente": agente, "modelo": None, "cambia": False, "modelo_partida": modelo_partida,
                "justificacion": "Script determinista, sin modelo: no aplica recomendación de modelo."}
    orden = modelos_por_precio([c["modelo"] for c in celdas])
    por_modelo = {c["modelo"]: c for c in celdas}

    def res(c):
        mt = c["metrica"]
        v = mt.get("valor")
        s = f"{corto(c['modelo'])}: {um['metrica']} = {f(v, 3)} (umbral {f(um['umbral'], 2)})"
        if agente == "simulador" and mt.get("n_pitagoras_N1") is not None:
            s += (f", corridas válidas {mt.get('corridas_validas')}/{mt.get('corridas_esperadas')}, pct_validan {f(mt.get('pct_validan'), 2)}, "
                  f"Pitágoras en N1 {mt.get('n_pitagoras_N1')} y en total {mt.get('n_pitagoras')}")
        if c["estado"] == "reutilizada":
            s += f", {mt.get('corridas')} corridas {[f(k, 3) for k in mt.get('kappa_por_corrida', [])]} (reutilizadas)"
        errs = [u["error"] for u in c["unidades"] if u.get("error") and not u["omitida"]]
        if errs:
            s += f", {len(errs)} caso(s) con error del agente ({errs[0][:90]})"
        cpu_, lat_ = c.get("costo_por_unidad_usd"), c.get("latencia_media_s")
        if cpu_ is not None:
            s += f", {f(cpu_, 4)} USD/unidad, {f(lat_, 1)} s"
        if c["estado"] in ("parcial", "no_corrida"):
            s += f" [celda {c['estado']}: {c['n_unidades_omitidas']}/{c['n_unidades']} unidades sin correr por tope de gasto]"
        return s

    elegido = next((m for m in orden if por_modelo[m]["pasa"] is True), None)
    sin_verificar = [m for m in orden if por_modelo[m]["pasa"] is None and (elegido is None or precio_salida(m) < precio_salida(elegido))]
    if elegido is None:
        return {"agente": agente, "modelo": None, "cambia": False, "modelo_partida": modelo_partida,
                "justificacion": "Ningún modelo medido pasa el umbral (" + "; ".join(res(por_modelo[m]) for m in orden) +
                                 f"). Se mantiene el modelo de partida ({modelo_partida}) y se revisa el prompt/umbral."}
    c = por_modelo[elegido]
    fallan = [m for m in orden if precio_salida(m) < precio_salida(elegido) and por_modelo[m]["pasa"] is False]
    partes = [f"{res(c)} -> pasa."]
    cpu = c.get("costo_por_unidad_usd")
    lat = c.get("latencia_media_s")
    if fallan:
        partes.append("Los modelos más baratos no pasan: " + "; ".join(res(por_modelo[m]) for m in fallan) + ".")
    if sin_verificar:
        partes.append("Sin evidencia para: " + ", ".join(corto(m) for m in sin_verificar) + " (celda no corrida).")
    if modelo_partida and modelo_partida != elegido and por_modelo.get(modelo_partida):
        cp = por_modelo[modelo_partida].get("costo_por_unidad_usd")
        if cpu is not None and cp:
            partes.append(f"Frente al modelo de partida ({corto(modelo_partida)}, {f(cp, 4)} USD/unidad): {f(100 * (1 - cpu / cp), 0)} % menos costo por unidad.")
    cambia = bool(modelo_partida) and elegido != modelo_partida
    if agente in CAVEAT_METRICA:
        partes.append(CAVEAT_METRICA[agente])
    if agente == "evaluador" and c["metrica"].get("corridas") == 1:
        otros = [x["metrica"] for x in celdas if x["estado"] == "reutilizada"]
        if otros and len(otros[0].get("kappa_por_corrida", [])) > 1:
            ks = otros[0]["kappa_por_corrida"]
            partes.append(f"Atención: {corto(elegido)} se midió con 1 corrida; Opus varió entre {f(min(ks), 3)} y {f(max(ks), 3)} en sus 3 corridas "
                          f"(rango {f(max(ks) - min(ks), 3)}), de modo que la diferencia con Opus ({f(otros[0]['valor'], 3)}) está dentro del ruido. "
                          "Confirmar con 3 corridas (costo aproximado: 2 corridas más = " + f(2 * c["costo_usd"], 2) + " USD) antes de cambiar el modelo.")
    if agente == "evaluador":
        partes.append("Reserva: el kappa descansa en 5 puntajes provisionales de Claude y los ajustes del prompt se hicieron mirando las mismas "
                      "9 tareas; contra las 4 tareas humanas el kappa es " + f(c["metrica"].get("kappa_humanas"), 3) +
                      ". En producción el evaluador corre 3 veces (condición 1 de CP1): el costo se triplica.")
    return {"agente": agente, "modelo": elegido, "cambia": cambia, "modelo_partida": modelo_partida,
            "justificacion": " ".join(p for p in partes if p)}


# ------------------------------------------------------------------ informe
RUNNERS = {"explorador": correr_explorador, "filtro": correr_filtro, "disenador": correr_disenador,
           "evaluador": correr_evaluador, "simulador": correr_simulador, "redactor": correr_redactor,
           "ilustrador": correr_ilustrador, "verificador": correr_verificador, "bibliotecario": correr_bibliotecario}
ORDEN_LANZAMIENTO = ["simulador", "disenador", "redactor", "evaluador", "verificador", "ilustrador", "filtro",
                     "explorador", "bibliotecario"]


def partida(agente: str) -> str | None:
    return config()["modelos"].get(agente)


def construir_matriz(celdas_por_agente: dict[str, list[dict]], presupuesto: Presupuesto, meta: dict) -> dict:
    recs = {a: recomendar(a, cs, partida(a)) for a, cs in celdas_por_agente.items()}
    por_agente = {a: round(sum(c["costo_usd"] + c.get("costo_auxiliar_usd", 0.0) for c in cs), 6)
                  for a, cs in celdas_por_agente.items()}
    descartado = round(sum(c["costo_usd"] for c in presupuesto.llamadas if str(c.get("rol", "")).startswith("descartado")), 6)
    n_llamadas = sum(c["n_llamadas"] + sum(u.get("auxiliar", {}).get("n_llamadas", 0) for u in c["unidades"])
                     for cs in celdas_por_agente.values() for c in cs)
    sin_correr = []
    for a, cs in celdas_por_agente.items():
        for c in cs:
            if c["estado"] in ("parcial", "no_corrida"):
                ids = [u["id"] for u in c["unidades"] if u["omitida"]]
                sin_correr.append({"agente": a, "modelo": c["modelo"], "estado": c["estado"], "unidades_sin_correr": ids,
                                   "n_unidades": c["n_unidades"],
                                   "motivo": presupuesto.agotado.get(a) or "presupuesto agotado"})
    por_agente_modelo = {}
    for c in presupuesto.llamadas:
        k = f"{c['agente']}/{c['modelo']}"
        por_agente_modelo[k] = round(por_agente_modelo.get(k, 0.0) + c["costo_usd"], 6)
    reutilizado = sum(c.get("costo_reutilizado_usd", 0.0) for cs in celdas_por_agente.values() for c in cs)
    return {
        "meta": meta,
        "umbrales": {a: UMBRALES[a] for a in celdas_por_agente},
        "celdas": celdas_por_agente,
        "recomendaciones": recs,
        "costo": {"total_usd": round(presupuesto.gastado, 6), "tope_usd": presupuesto.tope,
                  "por_agente_usd": por_agente,
                  "por_agente_modelo_usd": por_agente_modelo,
                  "n_llamadas": n_llamadas, "descartado_usd": descartado,
                  "reutilizado_no_gastado_usd": round(reutilizado, 4),
                  "precios_usd_mtok": {m: config()["precios_modelos"][m] for m in ALIAS.values()}},
        "celdas_sin_correr": sin_correr,
    }


def _celda_txt(c: dict, agente: str) -> str:
    um = UMBRALES[agente]
    if c["estado"] == "n/a":
        return "N/A"
    if c["estado"] == "no_corrida":
        return "no corrida"
    v = c["metrica"].get("valor")
    s = f(v, 2)
    if agente == "simulador":
        s = f"{c['metrica'].get('corridas_validas')}/{c['metrica'].get('corridas_esperadas')} válidas"
    p = {True: "pasa", False: "no pasa", None: "parcial" if c["estado"] == "parcial" else "—"}[c["pasa"]]
    return f"{s} ({p})"


def escribir_md(m: dict) -> str:
    L: list[str] = []
    w = L.append
    meta, costo = m["meta"], m["costo"]
    modelos = meta["modelos"]
    w(f"# Matriz modelo × agente — {meta['fecha']}\n")
    if meta["sin_red"]:
        w("> **CORRIDA SIN RED (ClienteFalso).** Los números prueban la tubería, no miden los modelos: las respuestas son las "
          "scripteadas de los casos y los costos se calculan con tokens sintéticos. No usar para elegir modelos.\n")
    w(f"Generada por `evals/run.py` v{VERSION_RUN} ({meta['generada_utc']}). Modo: {'sin red' if meta['sin_red'] else 'real'}. "
      f"Agentes: {', '.join(meta['agentes'])}. Modelos: {', '.join(corto(x) for x in modelos)}.\n")
    w("## Costo de la corrida\n")
    w(f"- **Costo total registrado: {f(costo['total_usd'], 4)} USD** de un tope de {f(costo['tope_usd'], 2)} USD "
      f"({costo['n_llamadas']} llamadas a la API; precios de `pipeline/config.yaml`, tabla `precios_modelos`).")
    if costo["reutilizado_no_gastado_usd"]:
        w(f"- Evaluador/Opus no se volvió a correr: se reutilizan las 3 corridas de calibración v1.3 "
          f"(valdrían {f(costo['reutilizado_no_gastado_usd'], 2)} USD a precios de config.yaml; ya pagadas, no cuentan en el total).")
    w("- Por agente (USD, incluye evaluaciones auxiliares): " + "; ".join(f"{a} {f(v, 3)}" for a, v in costo["por_agente_usd"].items()) + ".")
    if costo["descartado_usd"]:
        w(f"- Incluye {f(costo['descartado_usd'], 3)} USD de una corrida anterior rehecha (verificador) que se descartó pero se gastó.")
    aux = sum(c["costo_auxiliar_usd"] for cs in m["celdas"].values() for c in cs)
    if aux:
        w(f"- Del gasto del diseñador, {f(aux, 3)} USD son evaluaciones RUB01 con {corto(EVALUADOR_REF)} (costo auxiliar, no "
          "se atribuye al costo de la celda del diseñador).")
    w("- Los modelos 5.5 no aceptan `temperature`: no se envió; la variabilidad entre corridas es parte de la medición.\n")

    if meta.get("historial"):
        w("## Historial de la corrida\n")
        for h in meta["historial"]:
            w(f"- {h}")
        w("")
    w("## Recomendación de modelo por agente\n")
    w("Regla: el modelo más barato (por precio de salida de lista) cuya celda pasa el umbral del agente. Esto es evidencia para CP2: "
      "`pipeline/config.yaml` no se modificó.\n")
    w("| Agente | Modelo de partida | Recomendado | Métrica (umbral) | Costo/unidad USD | Latencia media s | Cambia |")
    w("|---|---|---|---|---|---|---|")
    for a, r in m["recomendaciones"].items():
        cs = {c["modelo"]: c for c in m["celdas"][a]}
        c = cs.get(r["modelo"]) if r["modelo"] else None
        um = UMBRALES[a]
        if um["umbral"] is None:
            w(f"| {a} | script | N/A | N/A | N/A | N/A | no |")
            continue
        met = f"{um['metrica']} = {f(c['metrica'].get('valor'), 3)} (>= {f(um['umbral'], 2)})" if c else "ninguno pasa"
        w(f"| {a} | {corto(r['modelo_partida'])} | {corto(r['modelo']) if r['modelo'] else 'mantener ' + corto(r['modelo_partida'])} | {met} | "
          f"{f(c['costo_por_unidad_usd'], 4) if c else '—'} | {f(c['latencia_media_s'], 1) if c else '—'} | {'sí' if r['cambia'] else 'no'} |")
    w("")
    for a, r in m["recomendaciones"].items():
        w(f"- **{a}**: {r['justificacion']}")
    w("")

    w("## Matriz (métrica de la celda y veredicto)\n")
    w("| Agente | Métrica (umbral) | " + " | ".join(corto(x) for x in modelos) + " |")
    w("|---|---|" + "---|" * len(modelos))
    for a, cs in m["celdas"].items():
        um = UMBRALES[a]
        por = {c["modelo"]: c for c in cs}
        w(f"| {a} | {um['metrica']} (>= {f(um['umbral'], 2) if um['umbral'] is not None else '—'}) | " +
          " | ".join(_celda_txt(por[x], a) if x in por else "—" for x in modelos) + " |")
    w("\n## Costo y latencia por celda\n")
    w("Costo = gasto nuevo de la celda (USD); costo/unidad = costo / unidades con llamadas (caso, corrida o lanzada); "
      "latencia = tiempo de reloj por unidad (s), media y máximo.\n")
    w("| Agente | Modelo | Estado | Unidades (corridas/total) | Llamadas | Costo USD | Costo/unidad USD | Latencia media s | Latencia máx. s |")
    w("|---|---|---|---|---|---|---|---|---|")
    for a, cs in m["celdas"].items():
        for c in cs:
            costo_txt = f(c["costo_usd"], 4)
            if c["estado"] == "reutilizada":
                costo_txt = f"0 (reutiliza {f(c['costo_reutilizado_usd'], 2)})"
            w(f"| {a} | {corto(c['modelo'])} | {c['estado']} | {(str(c['n_unidades']) + ' reutilizadas') if c['estado'] == 'reutilizada' else str(c['n_unidades_corridas']) + '/' + str(c['n_unidades'])} | "
              f"{c['n_llamadas']} | {costo_txt} | {f(c['costo_por_unidad_usd'], 4)} | {f(c['latencia_media_s'], 1)} | {f(c['latencia_max_s'], 1)} |")

    w("\n## Umbrales por agente (definidos por eval-engineer)\n")
    w("| Agente | Métrica | Umbral | Definición |")
    w("|---|---|---|---|")
    for a in m["celdas"]:
        um = UMBRALES[a]
        w(f"| {a} | {um['metrica']} | {f(um['umbral'], 2) if um['umbral'] is not None else '—'} | {um['texto']} |")

    w("\n## Detalle por agente\n")
    for a, cs in m["celdas"].items():
        w(f"### {a}\n")
        if a == "evaluador":
            w("| Modelo | Origen | κ por corrida (global, 108 pares) | κ medio | κ solo 4 tareas humanas | Acuerdo exacto | Pasa |")
            w("|---|---|---|---|---|---|---|")
            for c in cs:
                mt = c["metrica"]
                w(f"| {corto(c['modelo'])} | {'reutilizada (v1.3, 3 corridas)' if mt.get('reutilizada') else '1 corrida nueva'} | "
                  f"{' / '.join(f(k, 3) for k in mt.get('kappa_por_corrida', []))} | {f(mt.get('valor'), 3)} | "
                  f"{f(mt.get('kappa_humanas'), 3)} | {f(mt.get('acuerdo_exacto'), 2)} | {f(c['pasa'])} |")
            w("\n> Advertencia (CLAUDE.md): 5 de los 9 puntajes de referencia son provisionales, puestos por Claude. "
              "El κ total no es evidencia de validez; la columna de las 4 tareas humanas es la referencia no contaminada "
              "(solo 48 pares: muy inestable).\n")
        elif a == "filtro":
            w("| Modelo | κ decisión (15 pares) | Acuerdo exacto | Consistencia entre corridas (casos) | Total en rango esperado | Errores del agente |")
            w("|---|---|---|---|---|---|")
            for c in cs:
                mt = c["metrica"]
                w(f"| {corto(c['modelo'])} | {f(mt.get('valor'), 3)} | {f(mt.get('acuerdo_exacto'), 2)} | {mt.get('consistencia_casos')} | "
                  f"{mt.get('total_en_rango')} | {mt.get('errores_agente')} |")
            w("\nPunto 5 de 'Para CP2' (frontera 7/6): decisiones por corrida en los casos frontera.\n")
            w("| Modelo | Caso | Decisiones (3 corridas) | Totales | Esperado pasa |")
            w("|---|---|---|---|---|")
            for c in cs:
                for cid, v in (c["metrica"].get("por_caso") or {}).items():
                    if "frontera" in cid:
                        w(f"| {corto(c['modelo'])} | {cid} | {', '.join('pasa' if d else 'no' for d in v['decisiones'])} | {v['totales']} | {f(v['esperado'])} |")
            w("")
        elif a == "disenador":
            w("| Modelo | % casos RUB01 >= 20 sin ceros | RUB01 media | Totales por caso | % contrato válido | Costo auxiliar (evaluación) USD |")
            w("|---|---|---|---|---|---|")
            for c in cs:
                mt = c["metrica"]
                w(f"| {corto(c['modelo'])} | {f(mt.get('valor'), 2)} ({mt.get('ok')}/{mt.get('n')}) | {f(mt.get('rub01_media'), 1)} | "
                  f"{mt.get('rub01_totales')} | {f(mt.get('pct_contrato_valido'), 2)} | {f(c['costo_auxiliar_usd'], 3)} |")
            w("")
        elif a == "simulador":
            w("Punto 4 de 'Para CP2' (Sugarloaf S1, `pct_validan` y Pitágoras):\n")
            w("| Modelo | Corridas válidas | pct_validan (media) | Corridas con Pitágoras | Pitágoras en perfil N1 | Pasa |")
            w("|---|---|---|---|---|---|")
            for c in cs:
                mt = c["metrica"]
                w(f"| {corto(c['modelo'])} | {mt.get('corridas_validas')}/{mt.get('corridas_esperadas')} | {f(mt.get('pct_validan'), 2)} | "
                  f"{mt.get('n_pitagoras')} | {mt.get('n_pitagoras_N1')} | {f(c['pasa'])} |")
            w("\nPitágoras = el modelo, la respuesta final o los supuestos codificados mencionan Pitágoras, hipotenusa o cateto. "
              "El perfil N1 declara que el estudiante no conoce Pitágoras (niveles.py, INS08 §2).\n")
        else:
            w("| Modelo | Casos ok | Métrica | Pasa | Casos |")
            w("|---|---|---|---|---|")
            for c in cs:
                mt = c["metrica"]
                if c["estado"] == "n/a":
                    t = c.get("tests_sin_red", {})
                    w(f"| {corto(c['modelo'])} | N/A | script sin modelo | N/A | tests sin red: {t.get('resumen', 'no corridos')} |")
                    continue
                casos_txt = ", ".join(f"{k}: {'ok' if v else 'falla'}" for k, v in (mt.get("detalle_por_caso") or {}).items())
                w(f"| {corto(c['modelo'])} | {mt.get('ok')}/{mt.get('n')} | {f(mt.get('valor'), 2)} | {f(c['pasa'])} | {casos_txt} |")
            w("")
        if a == "verificador":
            for c in cs:
                for u in c["unidades"]:
                    if u.get("ok") is False and u["detalle"].get("hallazgos_criticos"):
                        w(f"- ({corto(c['modelo'])}) `{u['id']}` esperaba aprobado={f(u['detalle']['esperado_aprobado'])} y el modelo rechazó. "
                          "Hallazgos críticos del modelo: " + " | ".join(u["detalle"]["hallazgos_criticos"]))
        vistas = set()
        for c in cs:
            for n in c["notas"]:
                if n not in vistas:
                    vistas.add(n)
                    w(f"- {n}" if len([x for x in cs if n in x["notas"]]) == len(cs) else f"- ({corto(c['modelo'])}) {n}")
            fallos = [u for u in c["unidades"] if u.get("error") and not u["omitida"]]
            for u in fallos:
                w(f"- ({corto(c['modelo'])}) caso `{u['id']}` falló: {u['error'][:200]}")
        w("")

    w("## Celdas no corridas\n")
    if m["celdas_sin_correr"]:
        for s in m["celdas_sin_correr"]:
            w(f"- **{s['agente']} / {corto(s['modelo'])}** ({s['estado']}): {len(s['unidades_sin_correr'])}/{s['n_unidades']} unidades sin correr "
              f"({', '.join(s['unidades_sin_correr'])}). Motivo: {s['motivo']}.")
    else:
        w("- Ninguna: todas las celdas pedidas se corrieron completas (o se reutilizaron).")
    w("\n## Limitaciones\n")
    w("- n pequeño: 5 casos por agente (3 para el redactor en vivo, 9 tareas-oro para el evaluador, 2 lanzadas para el simulador). "
      "Una diferencia de un caso mueve la métrica 0,2.")
    w("- Sin `temperature` en los modelos 5.5, una sola corrida mezcla capacidad y azar; solo el filtro (3 corridas) y el evaluador "
      "Opus (3 corridas) miden consistencia.")
    w("- Los casos del diseñador y del redactor son sintéticos o de los ejemplos del contrato; la evaluación RUB01 del diseñador es de una sola "
      "corrida de Opus (puede variar varios puntos). Si Opus diseña y Opus evalúa hay posible sesgo de familia.")
    w("- El simulador usa el mismo modelo para estudiantes y codificador en cada celda; en producción el codificador es Opus.")
    w("- Los precios son los de `config.yaml`; verificar el gasto real en la Console.")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ main
def parsear(argv=None):
    ap = argparse.ArgumentParser(description="Matriz modelo x agente (eval-engineer).")
    ap.add_argument("--agentes", default=",".join(AGENTES), help="lista separada por comas")
    ap.add_argument("--modelos", default="haiku,sonnet,opus", help="haiku,sonnet,opus o ids completos")
    ap.add_argument("--sin-red", action="store_true", help="ClienteFalso: prueba la tubería sin gastar")
    ap.add_argument("--tope", type=float, default=TOPE_USD, help="tope total en USD (por defecto 12)")
    ap.add_argument("--fecha", default=FECHA)
    ap.add_argument("--dir", default=str(DIR_RES), help="directorio de salida")
    ap.add_argument("--sufijo", default=None, help="sufijo del nombre (por defecto '' real y '_sinred')")
    ap.add_argument("--reanudar", action="store_true", help="omite los agentes con datos ya guardados")
    ap.add_argument("--completar", action="store_true",
                    help="como --reanudar, pero los agentes con celdas parciales/no corridas rehacen solo las unidades pendientes")
    ap.add_argument("--rehacer", default="", help="agentes a volver a correr aunque haya datos guardados (su gasto previo sigue contando)")
    ap.add_argument("--tope-agente", action="append", default=[], metavar="AGENTE=USD",
                    help="reemplaza la reserva por agente (repetible), p. ej. disenador=5")
    ap.add_argument("--paralelo", type=int, default=4, help="agentes en paralelo")
    ap.add_argument("--corridas-filtro", type=int, default=3)
    ap.add_argument("--lanzadas-simulador", type=int, default=2)
    ap.add_argument("--sin-tests-bibliotecario", action="store_true")
    return ap.parse_args(argv)


def resolver_modelos(txt: str) -> list[str]:
    out = []
    for x in [t.strip() for t in txt.split(",") if t.strip()]:
        m = ALIAS.get(x, x)
        if m not in config()["precios_modelos"]:
            raise SystemExit(f"modelo sin precio en config.yaml: {m}")
        out.append(m)
    return modelos_por_precio(out)


def main(argv=None) -> int:
    a = parsear(argv)
    agentes = [x.strip() for x in a.agentes.split(",") if x.strip()]
    for x in agentes:
        if x not in AGENTES:
            raise SystemExit(f"agente desconocido: {x}")
    modelos = resolver_modelos(a.modelos)
    sufijo = a.sufijo if a.sufijo is not None else ("_sinred" if a.sin_red else "")
    dir_out = Path(a.dir)
    dir_out.mkdir(parents=True, exist_ok=True)
    base = f"matriz_{a.fecha}{sufijo}"
    dir_datos = dir_out / f"{base}_datos"
    dir_datos.mkdir(exist_ok=True)

    topes_agente = dict(TOPES_AGENTE)
    for par in a.tope_agente:
        k, _, v = par.partition("=")
        if k not in AGENTES or not v:
            raise SystemExit(f"--tope-agente espera AGENTE=USD, recibió {par!r}")
        topes_agente[k] = float(v)
    rehacer = {x.strip() for x in a.rehacer.split(",") if x.strip()}
    pres = Presupuesto(a.tope, topes_agente)
    ctx = Ctx(pres, a.sin_red, dir_datos, a)
    celdas: dict[str, list[dict]] = {}
    pendientes, completados = [], []
    f_desc = dir_datos / "descartado.json"      # gasto de corridas rehechas: sigue contando en el total
    descartados = _j(f_desc) if f_desc.exists() else []
    for d in descartados:
        pres.precargar(d["agente"], d["costo_usd"], "descartado: corrida anterior rehecha")
    costo_celdas = lambda cs: sum(c["costo_usd"] + c.get("costo_auxiliar_usd", 0.0) for c in cs)  # noqa: E731
    for ag in agentes:
        arch = dir_datos / f"{ag}.json"
        if not (arch.exists() and (a.reanudar or a.completar or ag in rehacer)):
            pendientes.append(ag)
            continue
        previo = _j(arch)["celdas"]
        if ag in rehacer:
            pres.precargar(ag, costo_celdas(previo), "descartado: corrida anterior rehecha")
            descartados.append({"agente": ag, "costo_usd": round(costo_celdas(previo), 6),
                                "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds")})
            f_desc.write_text(json.dumps(descartados, ensure_ascii=False, indent=1), encoding="utf-8")
            pendientes.append(ag)
            log(f"{ag}: se rehace (el gasto previo {costo_celdas(previo):.3f} USD sigue contando)")
            continue
        incompleto = any(c["estado"] in ("parcial", "no_corrida", "error") for c in previo)
        pres.precargar(ag, costo_celdas(previo))
        if a.completar and incompleto:
            for c in previo:
                for u in c["unidades"]:
                    if not u["omitida"]:
                        ctx.previas[(ag, c["modelo"], u["id"])] = u
            pendientes.append(ag)
            completados.append(ag)
            log(f"{ag}: se completan las unidades pendientes")
        else:
            celdas[ag] = previo
            log(f"{ag}: reanudado desde {arch.name}")
    pendientes.sort(key=lambda x: ORDEN_LANZAMIENTO.index(x))

    def correr(ag):
        log(f"inicia {ag}")
        t0 = time.time()
        try:
            cs = RUNNERS[ag](ctx, modelos)
        except Exception as e:  # noqa: BLE001 - un fallo de un runner no pierde las demás celdas
            log(f"ERROR en {ag}: {type(e).__name__}: {e}")
            cs = [celda_na(ag, m, f"error del runner: {type(e).__name__}: {str(e)[:300]}") for m in modelos]
            for c in cs:
                c["estado"] = "error"
        (dir_datos / f"{ag}.json").write_text(json.dumps({"agente": ag, "celdas": cs}, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"termina {ag} en {time.time() - t0:.0f} s; gasto acumulado {pres.gastado:.3f} USD")
        return ag, cs

    t_ini = time.time()
    with ThreadPoolExecutor(max_workers=max(1, a.paralelo)) as pool:
        for ag, cs in pool.map(correr, pendientes):
            celdas[ag] = cs
    celdas = {ag: celdas[ag] for ag in AGENTES if ag in celdas}
    meta = {"fecha": a.fecha, "generada_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "sin_red": a.sin_red,
            "agentes": list(celdas), "modelos": modelos, "tope_usd": a.tope, "topes_agente_usd": topes_agente,
            "duracion_s": round(time.time() - t_ini), "version_run": VERSION_RUN, "reanudados": [x for x in agentes if x not in pendientes],
            "completados": completados, "rehechos": sorted(rehacer & set(agentes)),
            "evaluador_de_referencia_disenador": EVALUADOR_REF,
            "historial": _j(dir_datos / "historial.json") if (dir_datos / "historial.json").exists() else [],
            "parametros": {"corridas_filtro": a.corridas_filtro, "lanzadas_simulador": a.lanzadas_simulador},
            "temperature": "no se envía (los modelos 5.5 la rechazan)"}
    matriz = construir_matriz(celdas, pres, meta)
    (dir_out / f"{base}.json").write_text(json.dumps(matriz, ensure_ascii=False, indent=2), encoding="utf-8")
    (dir_out / f"{base}.md").write_text(escribir_md(matriz), encoding="utf-8")
    log(f"matriz escrita: {dir_out / (base + '.md')} · costo total {matriz['costo']['total_usd']:.4f} USD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
