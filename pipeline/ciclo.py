"""Ciclo del pipeline OTM-Prensa: encadena los agentes sobre la máquina de estados de pipeline/orquestador.py.

El ciclo tiene dos tramos separados por la revisión humana 1 (GOB01 §2). En la máquina de estados
`simulada` solo se alcanza desde `revisada`, y `revisada` exige un `revisor` humano: el ciclo nunca
lo inventa. Por eso:

  Tramo A (automático, sin revisor):
    python -m pipeline.ciclo [--noticia N.json ...] [--con-filtro] [--max-tareas N] [--nivel P|S|U]
    explorador → filtro → diseñador (2 candidatos) → evaluador ×3 por candidato (mediana por criterio)
    → se elige el mejor candidato (el otro queda `archivada`) → iteración diseñador ↔ evaluador
    (máx. 3 evaluaciones; si no llega al umbral: `archivada` con diagnóstico).
    Cada tarea que alcanza el umbral queda en `evaluada`, pendiente de la revisión humana 1.

  Tramo B (lo lanza quien hizo la revisión humana 1 de ESOS expedientes):
    python -m pipeline.ciclo --continuar ID [ID ...] --revisor "Nombre Apellido"
    evaluada → revisada → simulador (6 corridas) → redactor → ilustrador → verificador
    (si rechaza: con_guia → simulada, se rehace la guía una vez; al segundo rechazo: `archivada`)
    → verificada → bibliotecario en dry-run. Se detiene en `verificada`: `publicada` exige la
    revisión humana 2 y no se simula.
    `--continuar` también reanuda expedientes que quedaron a medio camino (error o tope): retoma
    desde su estado actual; `--revisor` solo se exige si el expediente está en `evaluada`.

Otras órdenes: `--estado` lista los expedientes y su estado.

Invariantes que aplica este módulo además de las del orquestador:
  - Condición 1 de CP1: `evaluador.corridas` corridas por evaluación; puntaje oficial = mediana por
    criterio; todas las corridas en `evaluacion_corridas.json` (esquema local
    pipeline/esquemas/evaluacion_corridas.schema.json); rango del total >= `rango_inestable` →
    marca `evaluacion_inestable` en el expediente.
  - Invariante 6: antes de simular se comprueba `verificar_aislamiento(vista_estudiante(tarea), tarea)`;
    el hook del adapter (simulador/adapter/hooked.py) vuelve a comprobar cada llamada de estudiante.
  - Invariante 8: `evaluacion.reproducibilidad` se reconstruye en cada transición con modelo, versión
    de modelo (la que devuelve la API), versión de prompt y costo de cada agente que corrió para la
    tarea, más RUB01, MAR03, MED01, diseño del simulador, fecha y costo total.
  - Tope (GOB01 §3): todas las llamadas pasan por un `Contador` que envuelve al cliente de la API y
    suma el costo con pipeline.llm.costo_usd; antes de cada llamada comprueba
    gasto_semana_previo + gasto_ciclo < fraccion_detencion × tope_semanal_usd. Si se alcanza, el ciclo
    se detiene, cada expediente queda en su último estado válido y se escribe el registro del ciclo en
    pipeline/state/ciclos/ y el gasto en pipeline/state/gasto_semanal.json.

La clave de la API sale solo de pipeline/apikey.py (vía el cliente que crea el Contador).
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import threading
import traceback
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from jsonschema import Draft202012Validator  # noqa: E402

from pipeline import invariantes as inv  # noqa: E402
from pipeline import orquestador as orq  # noqa: E402
from pipeline.llm import CLAVES_USO, config, costo_usd, modelo_de  # noqa: E402

DIR_STATE = RAIZ / "pipeline" / "state"
ESQUEMA_CORRIDAS = json.loads(
    (RAIZ / "pipeline" / "esquemas" / "evaluacion_corridas.schema.json").read_text(encoding="utf-8"))
NIVELES_ROTACION = ("S", "P", "U")
MAX_RECHAZOS_VERIFICADOR = 2  # 1.er rechazo: se rehace la guía; 2.º: se archiva


# =========================================================================== utilidades
def ahora_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str) + "\n"


def _escribir(ruta: Path, contenido: Any) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido if isinstance(contenido, str) else _json(contenido), encoding="utf-8")
    return ruta


def semana_iso(d: date | None = None) -> str:
    a, s, _ = (d or datetime.now(timezone.utc).date()).isocalendar()
    return f"{a}-W{s:02d}"


def version_med01() -> str:
    import yaml

    rutas = sorted((RAIZ / "insumos" / "medios").glob("MED01_*.yaml"), key=inv._version_de_archivo)
    return str(yaml.safe_load(rutas[-1].read_text(encoding="utf-8"))["version"])


class TopeAlcanzado(Exception):
    """Gasto de la semana >= fraccion_detencion × tope_semanal_usd. No hereda de RuntimeError a
    propósito: los agentes reintentan ante RuntimeError y esto no debe reintentarse."""


class ErrorEtapa(Exception):
    """Una etapa no produjo un resultado utilizable; el expediente queda en su estado."""


# =========================================================================== contador de gasto
class Contador:
    """Cliente de la API que envuelve al real (o a un ClienteFalso) y lleva la cuenta del gasto.

    Tiene la misma interfaz que usan pipeline.llm.llamar y el evaluador (`.messages.create`).
    Antes de cada llamada comprueba el límite; después suma el costo con pipeline.llm.costo_usd."""

    def __init__(self, real=None, *, limite_usd: float, previo_usd: float = 0.0):
        self._real = real
        self.limite_usd = float(limite_usd)
        self.previo_usd = float(previo_usd)
        self.total = 0.0
        self.registro: list[dict] = []  # una entrada por llamada: modelo pedido, modelo respuesta, usd
        self.alcanzado = False
        self._lock = threading.Lock()
        self.messages = self

    # --- cliente
    def _cliente(self):
        if self._real is None:
            import anthropic

            from pipeline.apikey import api_key
            self._real = anthropic.Anthropic(api_key=api_key())
        return self._real

    def verificar(self) -> None:
        with self._lock:
            if self.previo_usd + self.total >= self.limite_usd:
                self.alcanzado = True
                raise TopeAlcanzado(
                    f"gasto semanal {self.previo_usd + self.total:.4f} USD >= límite {self.limite_usd:.4f} USD "
                    f"(fraccion_detencion × tope_semanal_usd)")

    def create(self, **kwargs):
        self.verificar()
        r = self._cliente().messages.create(**kwargs)
        uso = {k: getattr(getattr(r, "usage", None), k, 0) or 0 for k in CLAVES_USO}
        usd = costo_usd(uso, kwargs["model"])
        with self._lock:
            self.total = round(self.total + usd, 6)
            self.registro.append({"modelo": kwargs["model"], "modelo_respuesta": getattr(r, "model", kwargs["model"]),
                                  "usd": usd})
        return r

    def sumar_externo(self, usd: float, modelo: str = "externo") -> None:
        """Gasto que no pasó por este cliente (p. ej. backend `claude_p` del simulador)."""
        with self._lock:
            self.total = round(self.total + (usd or 0.0), 6)
            self.registro.append({"modelo": modelo, "modelo_respuesta": modelo, "usd": usd or 0.0})

    # --- medición por tramo
    def marca(self) -> int:
        with self._lock:
            return len(self.registro)

    def desde(self, marca: int) -> list[dict]:
        with self._lock:
            return list(self.registro[marca:])

    @property
    def gastado_semana(self) -> float:
        return round(self.previo_usd + self.total, 6)

    def restante(self) -> float:
        return max(0.0, round(self.limite_usd - self.gastado_semana, 6))


# =========================================================================== agentes (inyectables)
def _explorar_real(*, cliente, tope_usd: float) -> dict:
    from pipeline.agentes.explorador.run import explorar
    return explorar(cliente=cliente, tope_usd=tope_usd)


def _filtrar_real(noticia: dict, *, cliente) -> dict:
    from pipeline.agentes.filtro.run import filtrar
    return filtrar(noticia, cliente=cliente)


def _disenar_real(noticia: dict, nivel: str, *, cliente, texto_noticia: str | None) -> dict:
    from pipeline.agentes.disenador.run import disenar
    return disenar(noticia, nivel, cliente=cliente, texto_noticia=texto_noticia)


def _iterar_real(tarea: dict, evaluacion: dict, noticia: dict, *, cliente, texto_noticia: str | None) -> dict:
    from pipeline.agentes.disenador.run import iterar
    return iterar(tarea, evaluacion, noticia, cliente=cliente, texto_noticia=texto_noticia)


def _evaluar_real(entrada: dict, *, cliente) -> dict:
    from pipeline.agentes.evaluador.evaluador import evaluar
    return evaluar(entrada, cliente=cliente)


def _simular_real(tarea: dict, dir_tarea: Path, *, cliente, presupuesto_usd: float) -> dict:
    """Adapter SIM01 (simulador/adapter/lanzador.py). Devuelve trazas, errores, manifiesto y la
    carpeta de transcripciones (sim/corridas/*.md)."""
    from simulador.adapter import _comun, lanzador

    backend = _comun.config_sim()["backend"]
    res = lanzador.lanzar(tarea, dir_tarea, backend=backend, cliente=cliente, presupuesto_usd=presupuesto_usd)
    ruta_m = Path(dir_tarea) / "sim" / "manifiesto.json"
    res["manifiesto"] = json.loads(ruta_m.read_text(encoding="utf-8")) if ruta_m.exists() else {}
    res["dir_transcripciones"] = str(res["dir_corridas"])
    res["costo_externo_usd"] = res["costo_usd"] if backend != "api" else 0.0
    return res


def _redactar_real(tarea, trazas, transcripciones, contexto, *, cliente, texto_noticia) -> dict:
    from pipeline.agentes.redactor.run import redactar
    return redactar(tarea, trazas, transcripciones, contexto, cliente=cliente, texto_noticia=texto_noticia)


def _ilustrar_real(tarea: dict, *, cliente) -> dict:
    from pipeline.agentes.ilustrador.run import ilustrar
    return ilustrar(tarea, cliente=cliente)


def _verificar_real(tarea, guia, trazas, noticia, *, cliente, texto_noticia) -> dict:
    from pipeline.agentes.verificador.run import verificar
    return verificar(tarea, guia, trazas, noticia=noticia, texto_noticia=texto_noticia, cliente=cliente)


def _publicar_dry_run(tarea, guia, evaluacion, trazas, *, texto_noticia) -> dict:
    """Bibliotecario en ensayo: valida y calcula, no escribe ni ejecuta nada."""
    from pipeline.agentes.bibliotecario.run import publicar
    lineas: list[str] = []
    plan = publicar(tarea, guia, evaluacion, trazas=trazas, texto_noticia=texto_noticia,
                    ejecutar_real=False, salida=lineas.append)
    return {"ruta": plan.ruta, "rama": plan.rama, "lineas": lineas}


def cargar_transcripciones(directorio: str | Path) -> dict[str, str]:
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted(Path(directorio).glob("*.md"))}


def _versiones_prompt() -> dict[str, str]:
    """Versión de prompt de cada agente, leída de su módulo o config (sin red)."""
    from pipeline.agentes.disenador import run as dis
    from pipeline.agentes.evaluador import evaluador as ev
    from pipeline.agentes.filtro import run as fil
    from pipeline.agentes.ilustrador import run as ilu
    from pipeline.agentes.redactor import run as red
    from pipeline.agentes.verificador import run as ver
    v = {"filtro": fil.VERSION_PROMPT, "disenador": dis.VERSION_PROMPT, "evaluador": ev.VERSION_PROMPT,
         "redactor": red.VERSION_PROMPT, "redactor_escenarios": red.VERSION_PROMPT,
         "ilustrador": str(ilu.CFG["version_prompt"]), "verificador": str(ver.CONFIG["version_prompt"])}
    try:  # el explorador lo actualiza otro agente en paralelo: no se exige su forma
        from pipeline.agentes.explorador import run as exp_mod
        v["explorador"] = str(exp_mod.VERSION_PROMPT)
    except Exception:  # noqa: BLE001
        v["explorador"] = "desconocida"
    return v


@dataclass
class Agentes:
    """Funciones de cada agente. Los tests sustituyen las que quieran (sin red)."""
    explorar: Callable = _explorar_real
    filtrar: Callable = _filtrar_real
    disenar: Callable = _disenar_real
    iterar: Callable = _iterar_real
    evaluar: Callable = _evaluar_real
    simular: Callable = _simular_real
    redactar: Callable = _redactar_real
    ilustrar: Callable = _ilustrar_real
    verificar: Callable = _verificar_real
    publicar: Callable = _publicar_dry_run
    versiones_prompt: Callable = _versiones_prompt


# =========================================================================== evaluación (condición 1 de CP1)
def entrada_evaluador(tarea: Mapping[str, Any]) -> dict:
    """Tarea del contrato → entrada del evaluador (forma de evaluador.construir_mensaje).

    Mismas condiciones que en la calibración (CP1): nivel declarado, título, tipo de texto, texto que
    recibe el estudiante y recursos declarados. No se entrega `task_space` ni el mapa a priori del
    ciclo (las tareas-oro se calibraron sin él; el evaluador juzga la tarea, no lo que el diseñador
    dice de ella)."""
    est = tarea["estudiante"]
    nivel = {"nivel": tarea["nivel_principal"]}
    if tarea.get("sub_tramo"):
        nivel["sub_tramo"] = tarea["sub_tramo"]
    texto = est["enunciado_es"].strip()
    if est.get("foto_descripcion", "").strip():
        texto += "\n\n[Imagen que acompaña la tarea] " + est["foto_descripcion"].strip()
    recursos = [f"{r['id']} ({r['que_es']}), disponible a solicitud del grupo: {r['contenido']}"
                for r in est.get("recursos_a_solicitud", [])]
    recursos += [f"{r['id']} ({r['que_es']}), entregado de entrada (ya escrito en el enunciado): {r['contenido']}"
                 for r in tarea.get("recursos_de_entrada", [])]
    return {"titulo": tarea["titulo"], "nivel_declarado": nivel, "forma_texto": "enunciado para estudiantes",
            "texto": texto, "recursos": recursos, "mapa_ciclo": None}


def mediana_rub01(rubs: list[Mapping[str, Any]]) -> tuple[dict, dict]:
    """Puntaje oficial = mediana por criterio (con n par, la mediana inferior: lectura conservadora).
    Justificación, cita y mejora se toman de la primera corrida cuyo puntaje es la mediana.
    Devuelve (rub01, detalle {por_criterio, corrida_fuente, total, regla})."""
    if not rubs:
        raise ValueError("no hay corridas del evaluador")
    ids = list(rubs[0]["criterios"])
    criterios, fuente, por_criterio, mejoras = {}, {}, {}, []
    for cid in ids:
        pts = sorted(int(r["criterios"][cid]["puntaje"]) for r in rubs)
        med = pts[(len(pts) - 1) // 2]
        k = next(i for i, r in enumerate(rubs) if int(r["criterios"][cid]["puntaje"]) == med)
        criterios[cid] = copy.deepcopy(dict(rubs[k]["criterios"][cid]))
        fuente[cid], por_criterio[cid] = k + 1, med
        if med < 2:
            m = next((m for m in rubs[k].get("mejoras", []) if m["criterio"] == cid), None)
            if m is None:
                raise ValueError(f"la corrida {k + 1} puntúa {cid}={med} sin mejora")
            mejoras.append(copy.deepcopy(dict(m)))
    total = sum(por_criterio.values())
    rub = {"version_rubrica": rubs[0]["version_rubrica"], "criterios": criterios, "total": total, "mejoras": mejoras}
    detalle = {"regla": "mediana por criterio (n par: mediana inferior)", "total": total,
               "por_criterio": por_criterio, "corrida_fuente": fuente}
    return rub, detalle


def validar_corridas(doc: Mapping[str, Any]) -> list[str]:
    errores = [f"evaluacion_corridas: {'/'.join(map(str, e.absolute_path)) or '(raíz)'}: {e.message}"
               for e in Draft202012Validator(ESQUEMA_CORRIDAS).iter_errors(doc)]
    for ev in doc.get("evaluaciones", []):
        for c in ev.get("corridas", []):
            errores += list(inv.validar_contra_esquema(c.get("rub01"), "evaluacion_rub01").errores)
    return errores


# =========================================================================== rutas
@dataclass
class Rutas:
    expedientes: Path = DIR_STATE / "expedientes"
    trabajo: Path = DIR_STATE / "trabajo"
    ciclos: Path = DIR_STATE / "ciclos"
    gasto_semanal: Path = DIR_STATE / "gasto_semanal.json"

    def de(self, tarea_id: str) -> Path:
        return self.trabajo / tarea_id


def gasto_semana(ruta: Path, semana: str) -> float:
    if not ruta.exists():
        return 0.0
    return float(json.loads(ruta.read_text(encoding="utf-8")).get("semanas", {}).get(semana, {}).get("usd", 0.0))


def registrar_gasto_semana(ruta: Path, semana: str, ciclo_id: str, usd: float) -> None:
    datos = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {
        "descripcion": "Gasto en la API por semana ISO (lo escribe pipeline/ciclo.py; GOB01 §3).", "semanas": {}}
    s = datos["semanas"].setdefault(semana, {"usd": 0.0, "ciclos": []})
    s["usd"] = round(s["usd"] + usd, 6)
    s["ciclos"].append({"ciclo_id": ciclo_id, "usd": round(usd, 6)})
    _escribir(ruta, datos)


# =========================================================================== ciclo
@dataclass
class Ciclo:
    agentes: Agentes = field(default_factory=Agentes)
    rutas: Rutas = field(default_factory=Rutas)
    cliente: Any = None                 # cliente real o falso; None = anthropic con pipeline/apikey.py
    tope_semanal_usd: float | None = None
    fraccion_detencion: float | None = None
    presupuesto_ciclo_usd: float | None = None  # tope adicional solo para este ciclo (p. ej. el prototipo)
    corridas_evaluador: int | None = None
    rango_inestable: int | None = None
    corridas_simulador: int | None = None
    salida: Callable[[str], None] = print
    # Invariante 3: si el texto de la noticia no vino por --texto-noticia, se relee del enlace original
    # (solo en memoria, respetando robots.txt). La CLI lo activa; los tests no tocan la red.
    releer_noticia: bool = False
    leer_noticia: Callable[[str], str] | None = None

    def __post_init__(self):
        cfg = config()
        self.tope_semanal_usd = float(self.tope_semanal_usd if self.tope_semanal_usd is not None
                                      else cfg["tope_semanal_usd"])
        self.fraccion_detencion = float(self.fraccion_detencion if self.fraccion_detencion is not None
                                        else cfg["fraccion_detencion"])
        self.corridas_evaluador = int(self.corridas_evaluador or cfg["evaluador"]["corridas"])
        self.rango_inestable = int(self.rango_inestable or cfg["evaluador"]["rango_inestable"])
        self.corridas_simulador = int(self.corridas_simulador or cfg["simulador"]["corridas_por_tarea"])
        self.semana = semana_iso()
        self.ciclo_id = "ciclo_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        previo = gasto_semana(self.rutas.gasto_semanal, self.semana)
        limite = self.fraccion_detencion * self.tope_semanal_usd
        if self.presupuesto_ciclo_usd is not None:
            limite = min(limite, previo + float(self.presupuesto_ciclo_usd))
        self.contador = Contador(self.cliente, limite_usd=limite, previo_usd=previo)
        self.registro: dict[str, Any] = {
            "ciclo_id": self.ciclo_id, "inicio": ahora_utc(), "fin": None, "semana": self.semana,
            "parametros": {"tope_semanal_usd": self.tope_semanal_usd, "fraccion_detencion": self.fraccion_detencion,
                           "presupuesto_ciclo_usd": self.presupuesto_ciclo_usd, "limite_usd": round(limite, 6),
                           "gasto_semana_previo_usd": previo, "corridas_evaluador": self.corridas_evaluador,
                           "rango_inestable": self.rango_inestable, "corridas_simulador": self.corridas_simulador},
            "detenido_por_tope": False, "eventos": [], "expedientes": {}, "noticias": [],
            "pendientes_humanos": [], "errores": [],
        }
        self._versiones: dict[str, str] | None = None
        self._textos: dict[str, str] = {}

    # ------------------------------------------------------------------ registro
    def evento(self, tipo: str, **datos) -> None:
        self.registro["eventos"].append({"fecha": ahora_utc(), "tipo": tipo, **datos})

    def versiones(self) -> dict[str, str]:
        if self._versiones is None:
            self._versiones = self.agentes.versiones_prompt()
        return self._versiones

    def _guardar(self, exp: orq.Expediente) -> orq.Expediente:
        orq.guardar(exp, self.rutas.expedientes)
        self.registro["expedientes"][exp.tarea_id] = exp.estado
        d = self.rutas.de(exp.tarea_id)
        art = exp.artefactos
        _escribir(d / "tarea.json", art["tarea"])
        for nombre in ("evaluacion", "guia"):
            if nombre in art:
                _escribir(d / f"{nombre}.json", art[nombre])
            elif (d / f"{nombre}.json").exists():
                (d / f"{nombre}.json").unlink()  # descartado por un retroceso
        if "trazas_resumen" in art:
            _escribir(d / "trazas_resumen.json", art["trazas_resumen"])
        return exp

    def _texto(self, clave: str, url: str | None) -> str | None:
        """Texto de la noticia en memoria (invariante 3). Nunca se escribe a disco."""
        if clave in self._textos or not (self.releer_noticia and url):
            return self._textos.get(clave)
        leer = self.leer_noticia
        if leer is None:
            from pipeline.agentes.explorador.run import bajar_cuerpo as leer
        try:
            self._textos[clave] = leer(url)
        except Exception as err:  # noqa: BLE001 — sin texto la invariante 3 no se puede comprobar: se registra
            self._textos[clave] = None
            self.evento("invariante3_sin_texto", clave=clave, error=str(err)[:200])
        return self._textos[clave]

    def _texto_de(self, exp: orq.Expediente) -> str | None:
        n = exp.artefactos.get("noticia") or exp.artefactos["tarea"].get("noticia") or {}
        return self._texto(exp.tarea_id, n.get("url"))

    def _transicionar(self, exp: orq.Expediente, destino: str, **kw) -> orq.Expediente:
        texto = self._texto_de(exp)
        nuevo = orq.transicionar(exp, destino, texto_noticia=texto, **kw)
        nuevo.marcas.pop("ultimo_error", None)
        self.evento("transicion", tarea_id=exp.tarea_id, de=exp.estado, a=destino,
                    **({"motivo": kw["motivo"]} if kw.get("motivo") else {}))
        return self._guardar(nuevo)

    def _archivar(self, exp: orq.Expediente, motivo: str) -> orq.Expediente:
        return self._transicionar(exp, "archivada", motivo=motivo)

    # ------------------------------------------------------------------ gasto por agente
    def _medir(self, agente: str, fn: Callable, *a, exps: Iterable[orq.Expediente] = (), **kw):
        """Corre `fn` y atribuye su gasto (llamadas del Contador en ese tramo) a `agente` en cada
        expediente de `exps`. Devuelve (resultado, llamadas)."""
        self.contador.verificar()
        m = self.contador.marca()
        exps = list(exps)
        try:
            res = fn(*a, **kw)
        finally:
            llamadas = self.contador.desde(m)
            usd = round(sum(x["usd"] for x in llamadas), 6)
            self.evento("agente", agente=agente, tareas=[e.tarea_id for e in exps], llamadas=len(llamadas), usd=usd)
            for e in exps:
                self._anotar_agente(e, agente, llamadas)
        if self.contador.alcanzado:  # un agente pudo atrapar TopeAlcanzado (p. ej. el lanzador por corrida)
            raise TopeAlcanzado("tope alcanzado durante " + agente)
        return res, llamadas

    def _clave_agente(self, agente: str, modelo: str) -> str:
        """Agentes con dos modelos se registran por separado (invariante 8: modelo de cada agente)."""
        try:
            if agente == "simulador" and modelo == modelo_de("simulador_codificador") != modelo_de("simulador"):
                return "simulador_codificador"
            if agente == "redactor" and modelo == modelo_de("redactor_escenarios") != modelo_de("redactor"):
                return "redactor_escenarios"
        except KeyError:
            pass
        return agente

    def _anotar_agente(self, exp: orq.Expediente, agente: str, llamadas: list[dict]) -> None:
        reg = exp.marcas.setdefault("agentes", {})
        for ll in llamadas:
            clave = self._clave_agente(agente, ll["modelo"])
            e = reg.setdefault(clave, {"modelo": ll["modelo"], "versiones_modelo": [], "costo_usd": 0.0, "llamadas": 0})
            if ll["modelo_respuesta"] not in e["versiones_modelo"]:
                e["versiones_modelo"].append(ll["modelo_respuesta"])
            e["costo_usd"] = round(e["costo_usd"] + ll["usd"], 6)
            e["llamadas"] += 1

    def _anotar_compartido(self, exps: Iterable[orq.Expediente], agente: str, llamadas: list[dict]) -> None:
        for e in exps:
            self._anotar_agente(e, agente, llamadas)
            e.marcas.setdefault("costos_compartidos", [])
            if agente not in e.marcas["costos_compartidos"]:
                e.marcas["costos_compartidos"].append(agente)

    # ------------------------------------------------------------------ invariante 8
    def reproducibilidad(self, exp: orq.Expediente) -> dict:
        vers = self.versiones()
        agentes = {}
        for nombre, e in sorted(exp.marcas.get("agentes", {}).items()):
            ent = {"modelo": e["modelo"], "version_modelo": ",".join(e["versiones_modelo"]) or e["modelo"],
                   "costo_usd": round(e["costo_usd"], 6)}
            if nombre in vers:
                ent["version_prompt"] = vers[nombre]
            elif nombre == "simulador_codificador" or nombre == "simulador":
                ins = (exp.marcas.get("simulador_manifiesto") or {}).get("insumos_simulador", {})
                ent["version_prompt"] = ins.get("INS09") or "INS09"
            agentes[nombre] = ent
        trazas = exp.artefactos.get("trazas_resumen")
        return {
            "agentes": agentes,
            "version_prompt": {k: v["version_prompt"] for k, v in agentes.items() if "version_prompt" in v},
            "version_rubrica": exp.artefactos.get("evaluacion", {}).get("rub01", {}).get("version_rubrica")
            or inv.cargar_rub01()["version"],
            "version_MAR03": exp.marcas.get("version_MAR03", "1.0"),
            "version_MED01": version_med01(),
            "diseno_simulador": trazas["diseno"] if trazas else None,
            "fecha": ahora_utc(),
            "costo_usd": round(sum(v["costo_usd"] for v in agentes.values()), 6),
        }

    def _evaluacion_actualizada(self, exp: orq.Expediente, trazas: dict | None = None) -> dict:
        ev = copy.deepcopy(exp.artefactos["evaluacion"])
        tmp = orq.Expediente.desde_dict(exp.a_dict())
        if trazas is not None:
            tmp.artefactos["trazas_resumen"] = trazas
        ev["reproducibilidad"] = self.reproducibilidad(tmp)
        return ev

    # ------------------------------------------------------------------ etapa: evaluación (borrador → evaluada)
    def evaluar(self, exp: orq.Expediente) -> orq.Expediente:
        tarea = exp.artefactos["tarea"]
        entrada = entrada_evaluador(tarea)
        corridas = []
        for n in range(1, self.corridas_evaluador + 1):
            res, _ = self._medir("evaluador", self.agentes.evaluar, entrada, cliente=self.contador, exps=[exp])
            meta = res.get("meta", {})
            corridas.append({"n": n, "rub01": res["rub01"], "meta": {
                "modelo_respuesta": str(meta.get("modelo_respuesta") or meta.get("modelo") or modelo_de("evaluador")),
                "request_id": meta.get("request_id"), "fecha": str(meta.get("fecha") or ahora_utc()),
                "intentos": int(meta.get("intentos") or 1), "costo_usd": float(meta.get("costo_usd") or 0.0),
                "avisos": [str(a) for a in meta.get("avisos", [])]}})
            if meta.get("version_mar03"):
                exp.marcas["version_MAR03"] = str(meta["version_mar03"])
        rub, detalle = mediana_rub01([c["rub01"] for c in corridas])
        totales = [int(c["rub01"]["total"]) for c in corridas]
        rango = max(totales) - min(totales)
        inestable = rango >= self.rango_inestable
        entrada_corr = {
            "iteracion": exp.iteraciones + 1, "version_tarea": int(tarea["version"]), "fecha": ahora_utc(),
            "modelo": modelo_de("evaluador"), "version_prompt": self.versiones().get("evaluador", "?"),
            "version_rubrica": rub["version_rubrica"], "corridas": corridas, "totales": totales,
            "rango_total": rango, "rango_inestable": self.rango_inestable, "evaluacion_inestable": inestable,
            "mediana": detalle,
        }
        ruta = self.rutas.de(exp.tarea_id) / "evaluacion_corridas.json"
        doc = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {"tarea_id": exp.tarea_id, "evaluaciones": []}
        doc["evaluaciones"].append(entrada_corr)
        if errores := validar_corridas(doc):
            raise orq.ArtefactoInvalido("evaluacion_corridas.json no valida (esquema local)", tuple(errores))
        _escribir(ruta, doc)

        exp.marcas["evaluacion_inestable"] = inestable
        exp.marcas["evaluacion_rango_total"] = rango
        exp.marcas["evaluacion_corridas"] = str(ruta)
        evaluacion = {"tarea_id": exp.tarea_id, "fecha": ahora_utc(), "rub01": rub,
                      "reproducibilidad": self.reproducibilidad(exp)}
        if inestable:
            self.evento("evaluacion_inestable", tarea_id=exp.tarea_id, totales=totales, rango=rango)
        return self._transicionar(exp, "evaluada", artefactos={"evaluacion": evaluacion})

    # ------------------------------------------------------------------ diagnóstico
    @staticmethod
    def diagnostico(exp: orq.Expediente) -> str:
        rub = exp.artefactos["evaluacion"]["rub01"]
        r = inv.cumple_umbral_rub01(exp.artefactos["evaluacion"])
        bajos = ", ".join(f"{k}={c['puntaje']}" for k, c in rub["criterios"].items() if c["puntaje"] < 2)
        return (f"RUB01 {rub['total']}/24 (mediana de corridas) tras {exp.iteraciones} evaluaciones; "
                f"no cumple: {'; '.join(r.errores) or 'umbral'}; criterios bajo 2: {bajos or 'ninguno'}")

    # ------------------------------------------------------------------ tramo A
    def procesar_noticia(self, noticia: dict, nivel: str, *, filtrar: bool) -> orq.Expediente | None:
        """Noticia → (filtro) → 2 candidatos evaluados → mejor candidato iterado hasta el umbral o archivado.
        Devuelve el expediente elegido (en `evaluada` si cumple, `archivada` si no) o None."""
        nid = noticia.get("id", "?")
        texto = self._texto(nid, noticia.get("url"))
        info = {"noticia_id": nid, "nivel": nivel, "resultado": None}
        self.registro["noticias"].append(info)
        llam_filtro: list[dict] = []
        if filtrar:
            r, llam_filtro = self._medir("filtro", self.agentes.filtrar, noticia, cliente=self.contador)
            noticia = r["noticia"]
            if not noticia["filtro"]["pasa"]:
                info["resultado"] = f"no pasa el filtro ({noticia['filtro']['total']}/10)"
                return None
        elif noticia.get("filtro") and not noticia["filtro"].get("pasa"):
            info["resultado"] = "la noticia trae un filtro que no pasa; no se diseña"
            return None
        r, llam_dis = self._medir("disenador", self.agentes.disenar, noticia, nivel,
                                  cliente=self.contador, texto_noticia=texto)
        exps: list[orq.Expediente] = []
        for tarea in r["candidatos"]:
            tarea = copy.deepcopy(tarea)
            tarea["id"] = self._id_libre(tarea["id"], {e.tarea_id for e in exps})
            exp = orq.nuevo_expediente(tarea, noticia)
            exp.marcas.update({"ciclo_id": self.ciclo_id, "noticia_id": nid, "nivel_objetivo": nivel})
            if texto:
                self._textos[exp.tarea_id] = texto
            exps.append(self._guardar(exp))
        self._anotar_compartido(exps, "disenador", llam_dis)
        if filtrar:
            self._anotar_compartido(exps, "filtro", llam_filtro)
        info["candidatos"] = [e.tarea_id for e in exps]
        if not exps:
            info["resultado"] = "el diseñador no entregó candidatos"
            return None

        evaluados = []
        for e in exps:
            try:
                evaluados.append(self.evaluar(e))
            except TopeAlcanzado:
                raise
            except Exception as err:  # noqa: BLE001 — queda en borrador, se reanuda con --continuar
                self._error(e, "evaluador", err)
        if not evaluados:
            info["resultado"] = "ningún candidato pudo evaluarse"
            return None

        def clave(e):
            ev = e.artefactos["evaluacion"]
            ceros = sum(c["puntaje"] == 0 for c in ev["rub01"]["criterios"].values())
            return (bool(inv.cumple_umbral_rub01(ev)), ev["rub01"]["total"], -ceros)
        elegido = max(evaluados, key=clave)  # en empate, el primero (max conserva el primero)
        for e in evaluados:
            if e is not elegido:
                motivo = (f"candidato no elegido: RUB01 {e.artefactos['evaluacion']['rub01']['total']}/24 frente a "
                          f"{elegido.artefactos['evaluacion']['rub01']['total']}/24 de {elegido.tarea_id} "
                          "(2 candidatos por noticia; se sigue con el mejor)")
                self._archivar(e, motivo)
        info["elegido"] = elegido.tarea_id
        final = self.avanzar(elegido)
        info["resultado"] = final.estado
        return final

    def _id_libre(self, tid: str, usados: set[str]) -> str:
        base, n, cand = tid, 2, tid
        while cand in usados or (self.rutas.expedientes / f"{cand}.json").exists():
            cand, n = f"{base}-{n}", n + 1
        return cand

    def _error(self, exp: orq.Expediente, etapa: str, err: Exception) -> None:
        detalle = {"tarea_id": exp.tarea_id, "estado": exp.estado, "etapa": etapa,
                   "error": f"{type(err).__name__}: {err}"[:2000]}
        if isinstance(err, orq.InvarianteViolada):
            detalle["invariante"] = True
        self.registro["errores"].append(detalle)
        self.evento("error", **detalle, traza=traceback.format_exception_only(type(err), err)[-1][:500])
        exp.marcas["ultimo_error"] = detalle
        self._guardar(exp)

    # ------------------------------------------------------------------ motor de estados
    def avanzar(self, exp: orq.Expediente, revisor: str | None = None) -> orq.Expediente:
        """Lleva el expediente tan lejos como se pueda sin humanos. Errores de agentes: el expediente
        queda en su estado y se registra. TopeAlcanzado se propaga (detiene todo el ciclo)."""
        while exp.estado not in orq.TERMINALES:
            etapa = exp.estado
            try:
                siguiente = self._paso(exp, revisor)
            except TopeAlcanzado:
                self._guardar(exp)
                raise
            except Exception as err:  # noqa: BLE001
                self._error(exp, etapa, err)
                return exp
            if siguiente is None:  # espera a un humano
                return exp
            exp = siguiente
        return exp

    def _paso(self, exp: orq.Expediente, revisor: str | None) -> orq.Expediente | None:
        estado = exp.estado
        if estado == "borrador":
            return self.evaluar(exp)
        if estado == "evaluada":
            return self._tras_evaluar(exp, revisor)
        if estado == "revisada":
            return self._simular(exp)
        if estado == "simulada":
            return self._redactar(exp)
        if estado == "con_guia":
            return self._verificar(exp)
        if estado == "verificada":
            self._bibliotecario(exp)
            self._pendiente(exp, "revision_humana_2")
            return None
        raise orq.TransicionIlegal(f"estado sin etapa: {estado}")

    def _pendiente(self, exp: orq.Expediente, que: str) -> None:
        exp.marcas["pendiente"] = que
        self._guardar(exp)
        ent = {"tarea_id": exp.tarea_id, "pendiente": que, "estado": exp.estado}
        if exp.marcas.get("evaluacion_inestable"):
            ent["evaluacion_inestable"] = True
        self.registro["pendientes_humanos"].append(ent)

    def _tras_evaluar(self, exp: orq.Expediente, revisor: str | None) -> orq.Expediente | None:
        ev = exp.artefactos["evaluacion"]
        if inv.cumple_umbral_rub01(ev):
            if not (revisor and revisor.strip()):
                self._pendiente(exp, "revision_humana_1")
                return None
            exp.marcas.pop("pendiente", None)
            return self._transicionar(exp, "revisada", revisor=revisor.strip())
        if exp.iteraciones >= orq.MAX_ITERACIONES:
            return self._archivar(exp, self.diagnostico(exp))
        noticia = exp.artefactos.get("noticia")
        if noticia is None:
            raise ErrorEtapa("el expediente no trae la noticia: no se puede iterar el diseño")
        r, _ = self._medir("disenador", self.agentes.iterar, exp.artefactos["tarea"], ev, noticia,
                           cliente=self.contador, texto_noticia=self._texto_de(exp), exps=[exp])
        nueva = copy.deepcopy(r["tarea"])
        if nueva["id"] != exp.tarea_id:
            raise ErrorEtapa(f"la iteración cambió el id de la tarea ({nueva['id']!r})")
        exp.marcas.setdefault("atencion_mejoras", []).append(r.get("atencion_mejoras", []))
        return self._transicionar(exp, "borrador", artefactos={"tarea": nueva},
                                  motivo=f"iteración: RUB01 {ev['rub01']['total']}/24 bajo el umbral")

    # ------------------------------------------------------------------ tramo B
    def _simular(self, exp: orq.Expediente) -> orq.Expediente:
        tarea = exp.artefactos["tarea"]
        r = inv.verificar_aislamiento(inv.vista_estudiante(tarea), tarea)   # invariante 6
        if not r:
            raise orq.InvarianteViolada("Invariante 6: la vista de estudiante filtra task_space", r.errores)
        d = self.rutas.de(exp.tarea_id)
        res, _ = self._medir("simulador", self.agentes.simular, tarea, d, cliente=self.contador,
                             presupuesto_usd=self.contador.restante(), exps=[exp])
        if res.get("costo_externo_usd"):
            self.contador.sumar_externo(res["costo_externo_usd"], "simulador_externo")
        trazas = res.get("trazas")
        if res.get("errores"):
            raise ErrorEtapa(f"corridas con error: {res['errores'][:3]}")
        if not trazas or trazas.get("corridas") != self.corridas_simulador:
            raise ErrorEtapa(f"se esperaban {self.corridas_simulador} corridas y hay "
                             f"{trazas.get('corridas') if trazas else 0}")
        exp.marcas["simulador_manifiesto"] = res.get("manifiesto") or {}
        exp.marcas["dir_transcripciones"] = str(res.get("dir_transcripciones") or "")
        if res.get("avisos"):
            exp.marcas["avisos_simulador"] = list(res["avisos"])
        return self._transicionar(exp, "simulada", artefactos={
            "trazas_resumen": trazas, "evaluacion": self._evaluacion_actualizada(exp, trazas)})

    def _revision_1(self, exp: orq.Expediente) -> dict:
        h = next(h for h in reversed(exp.historial) if h["a"] == "revisada")
        return {"revisor": h["revisor"], "fecha": h["fecha"][:10]}

    def _redactar(self, exp: orq.Expediente) -> orq.Expediente:
        art = exp.artefactos
        tarea, trazas = art["tarea"], art["trazas_resumen"]
        trans = cargar_transcripciones(exp.marcas.get("dir_transcripciones") or "")
        contexto = {"puntaje_rub01": art["evaluacion"]["rub01"]["total"], "revision_humana_1": self._revision_1(exp),
                    "fecha": date.today().isoformat(), "version": tarea["version"]}
        r, _ = self._medir("redactor", self.agentes.redactar, tarea, trazas, trans, contexto, cliente=self.contador,
                           texto_noticia=self._texto_de(exp), exps=[exp])
        return self._transicionar(exp, "con_guia", artefactos={
            "guia": r["guia"], "evaluacion": self._evaluacion_actualizada(exp)})

    def _ilustrar(self, exp: orq.Expediente) -> None:
        """El ícono no bloquea: si falla, queda anotado para la revisión humana 2."""
        d = self.rutas.de(exp.tarea_id)
        try:
            s, _ = self._medir("ilustrador", self.agentes.ilustrar, exp.artefactos["tarea"], cliente=self.contador,
                               exps=[exp])
        except TopeAlcanzado:
            raise
        except Exception as err:  # noqa: BLE001
            exp.marcas["icono"] = None
            exp.marcas["aviso_ilustrador"] = f"{type(err).__name__}: {err}"[:500]
            self.evento("aviso", tarea_id=exp.tarea_id, etapa="ilustrador", detalle=exp.marcas["aviso_ilustrador"])
            return
        _escribir(d / "icono.svg", s["svg"])
        _escribir(d / "ilustrador.json", s)
        exp.marcas["icono"] = str(d / "icono.svg")

    def _verificar(self, exp: orq.Expediente) -> orq.Expediente:
        if "icono" not in exp.marcas:   # ilustrador (orden: redactor → ilustrador → verificador); una vez por tarea
            self._ilustrar(exp)
            self._guardar(exp)
        art = exp.artefactos
        inf, _ = self._medir("verificador", self.agentes.verificar, art["tarea"], art["guia"], art["trazas_resumen"],
                             art.get("noticia"), cliente=self.contador,
                             texto_noticia=self._texto_de(exp), exps=[exp])
        n = exp.marcas.get("rechazos_verificador", 0)
        _escribir(self.rutas.de(exp.tarea_id) / f"verificacion_{n + 1}.json", inf)
        if inf["aprobado"]:
            return self._transicionar(exp, "verificada", artefactos={"evaluacion": self._evaluacion_actualizada(exp)})
        n += 1
        exp.marcas["rechazos_verificador"] = n
        criticos = [f"[{h['invariante']}] {h['ubicacion']}: {h['descripcion']}"
                    for h in inf["hallazgos"] if h["severidad"] == "critico"]
        resumen = "; ".join(criticos)[:900] or "rechazo sin hallazgos críticos listados"
        if n >= MAX_RECHAZOS_VERIFICADOR:
            return self._archivar(exp, f"el verificador rechazó la guía {n} veces: {resumen}")
        return self._transicionar(exp, "simulada", motivo=f"verificador rechaza la guía (rechazo {n}): {resumen}",
                                  artefactos={"evaluacion": self._evaluacion_actualizada(exp)})

    def _bibliotecario(self, exp: orq.Expediente) -> None:
        if exp.marcas.get("bibliotecario_dry_run", {}).get("ok"):
            return
        art = exp.artefactos
        try:
            r = self.agentes.publicar(art["tarea"], art["guia"], art["evaluacion"], art["trazas_resumen"],
                                      texto_noticia=self._texto_de(exp))
            exp.marcas["bibliotecario_dry_run"] = {"ok": True, "ruta": r.get("ruta"), "rama": r.get("rama")}
            _escribir(self.rutas.de(exp.tarea_id) / "bibliotecario_dry_run.txt", "\n".join(r.get("lineas", [])) + "\n")
        except Exception as err:  # noqa: BLE001 — no cambia el estado; lo ve la revisión humana 2
            exp.marcas["bibliotecario_dry_run"] = {"ok": False, "error": f"{type(err).__name__}: {err}"[:1000]}
        self.evento("bibliotecario_dry_run", tarea_id=exp.tarea_id, **exp.marcas["bibliotecario_dry_run"])
        self._guardar(exp)

    # ------------------------------------------------------------------ órdenes
    def correr(self, *, noticias: list[dict] | None = None, max_tareas: int = 3, nivel: str | None = None,
               filtrar: bool | None = None, textos: Mapping[str, str] | None = None) -> dict:
        """Tramo A. `noticias` None = explorador (y filtro). Con noticias, el filtro es opcional."""
        self._textos.update(textos or {})
        self.registro["orden"] = "tramo_a"
        self.registro["parametros"].update({"max_tareas": max_tareas, "nivel": nivel,
                                            "origen": "explorador" if noticias is None else "archivo"})
        try:
            self.contador.verificar()
            if noticias is None:
                res, _ = self._medir("explorador", self.agentes.explorar, cliente=self.contador,
                                     tope_usd=self.contador.restante())
                noticias = list(res.get("noticias", []))
                self.registro["explorador"] = {"aceptadas": len(noticias), "descartadas": len(res.get("descartes", []))}
                filtrar = True if filtrar is None else filtrar
            filtrar = bool(filtrar)
            listas = 0
            for i, noticia in enumerate(noticias):
                if listas >= max_tareas:
                    break
                niv = nivel or NIVELES_ROTACION[i % len(NIVELES_ROTACION)]
                try:
                    exp = self.procesar_noticia(noticia, niv, filtrar=filtrar)
                except TopeAlcanzado:
                    raise
                except Exception as err:  # noqa: BLE001 — la noticia falla; el ciclo sigue
                    self.registro["errores"].append({"noticia_id": noticia.get("id"), "etapa": "noticia",
                                                     "error": f"{type(err).__name__}: {err}"[:2000]})
                    continue
                if exp is not None and exp.estado == "evaluada":
                    listas += 1
        except TopeAlcanzado as e:
            self._detener(e)
        return self._cerrar()

    def continuar(self, ids: list[str], *, revisor: str | None = None,
                  textos: Mapping[str, str] | None = None) -> dict:
        """Tramo B (o reanudación). `revisor` aprueba la revisión humana 1 de estos expedientes."""
        self._textos.update(textos or {})
        self.registro["orden"] = "tramo_b"
        self.registro["parametros"].update({"ids": list(ids), "revisor": revisor})
        try:
            self.contador.verificar()
            for tid in ids:
                exp = orq.cargar(tid, self.rutas.expedientes)
                if exp.estado in orq.TERMINALES:
                    self.registro["errores"].append({"tarea_id": tid, "error": f"expediente en {exp.estado}"})
                    continue
                if exp.estado == "evaluada" and inv.cumple_umbral_rub01(exp.artefactos["evaluacion"]) and not revisor:
                    self.registro["errores"].append({"tarea_id": tid, "error": "evaluada: falta --revisor "
                                                     "(revisión humana 1)"})
                    continue
                self.avanzar(exp, revisor)
        except TopeAlcanzado as e:
            self._detener(e)
        return self._cerrar()

    def _detener(self, e: TopeAlcanzado) -> None:
        self.registro["detenido_por_tope"] = True
        self.registro["motivo_detencion"] = str(e)
        self.evento("detencion_por_tope", detalle=str(e))

    def _cerrar(self) -> dict:
        self.registro["fin"] = ahora_utc()
        self.registro["gasto"] = {"ciclo_usd": round(self.contador.total, 6),
                                  "semana_usd": self.contador.gastado_semana,
                                  "limite_usd": round(self.contador.limite_usd, 6),
                                  "llamadas": len(self.contador.registro)}
        registrar_gasto_semana(self.rutas.gasto_semanal, self.semana, self.ciclo_id, self.contador.total)
        ruta = _escribir(self.rutas.ciclos / f"{self.ciclo_id}.json", self.registro)
        self.registro["archivo"] = str(ruta)
        return self.registro


# =========================================================================== CLI
def _leer_noticias(rutas: list[str]) -> list[dict]:
    out: list[dict] = []
    for r in rutas:
        d = json.loads(Path(r).read_text(encoding="utf-8"))
        if isinstance(d, list):
            out += d
        elif isinstance(d, dict) and "noticias" in d:   # salida del explorador
            out += d["noticias"]
        elif isinstance(d, dict) and "noticia" in d and "id" not in d:   # caso de evals
            out.append(d["noticia"])
        else:
            out.append(d)
    for n in out:
        r = inv.validar_contra_esquema(n, "noticia")
        if not r:
            raise SystemExit(f"noticia {n.get('id')!r} no valida contra contratos/noticia.schema.json: {r.errores[:3]}")
    return out


def _resumen(reg: dict) -> str:
    L = [f"ciclo {reg['ciclo_id']} ({reg.get('orden')}) · gasto ciclo {reg['gasto']['ciclo_usd']:.4f} USD · "
         f"semana {reg['gasto']['semana_usd']:.4f}/{reg['gasto']['limite_usd']:.2f} USD"]
    if reg["detenido_por_tope"]:
        L.append(f"DETENIDO POR TOPE: {reg.get('motivo_detencion')}")
    for tid, est in reg["expedientes"].items():
        L.append(f"  {tid}: {est}")
    for p in reg["pendientes_humanos"]:
        extra = " · EVALUACIÓN INESTABLE (ver evaluacion_corridas.json)" if p.get("evaluacion_inestable") else ""
        L.append(f"  pendiente {p['pendiente']}: {p['tarea_id']}{extra}")
    for e in reg["errores"]:
        L.append(f"  error: {json.dumps(e, ensure_ascii=False)[:300]}")
    L.append(f"registro: {reg.get('archivo')}")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline.ciclo", description=__doc__.split("\n")[0],
                                 epilog="Ver el docstring del módulo para los dos tramos.")
    ap.add_argument("--noticia", nargs="+", metavar="ARCHIVO.json",
                    help="noticia(s) del contrato `noticia` (salta el explorador; el filtro solo con --con-filtro)")
    ap.add_argument("--con-filtro", action="store_true", help="con --noticia: pasa igual por el filtro")
    ap.add_argument("--texto-noticia", metavar="ARCHIVO.txt",
                    help="texto de la noticia (solo en memoria, invariante 3); con una sola noticia o un solo id")
    ap.add_argument("--max-tareas", type=int, default=3, help="tareas que llegan a `evaluada` (por defecto 3)")
    ap.add_argument("--nivel", choices=["P", "S", "U"], help="nivel objetivo (por defecto rota S, P, U)")
    ap.add_argument("--continuar", nargs="+", metavar="TAREA_ID", help="tramo B / reanudar expedientes")
    ap.add_argument("--revisor", help="quien hizo la revisión humana 1 de los expedientes de --continuar")
    ap.add_argument("--presupuesto-ciclo", type=float, metavar="USD",
                    help="tope adicional para este ciclo (además del 90 %% del tope semanal)")
    ap.add_argument("--estado", action="store_true", help="lista los expedientes y su estado")
    a = ap.parse_args(argv)

    rutas = Rutas()
    if a.estado:
        for p in sorted(rutas.expedientes.glob("*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            m = d.get("marcas", {})
            extra = [x for x in (m.get("pendiente"), "inestable" if m.get("evaluacion_inestable") else None,
                                 "error" if m.get("ultimo_error") else None) if x]
            print(f"{d['tarea_id']}: {d['estado']} (evaluaciones {d['iteraciones']}) {' · '.join(extra)}")
        return 0
    if a.revisor and not a.continuar:
        ap.error("--revisor solo se usa con --continuar (la revisión humana 1 es de un expediente ya evaluado)")
    if a.noticia and a.continuar:
        ap.error("--noticia y --continuar son órdenes distintas")
    texto = Path(a.texto_noticia).read_text(encoding="utf-8") if a.texto_noticia else None

    ciclo = Ciclo(rutas=rutas, presupuesto_ciclo_usd=a.presupuesto_ciclo, releer_noticia=True)
    if a.continuar:
        if texto and len(a.continuar) != 1:
            ap.error("--texto-noticia exige un solo id")
        reg = ciclo.continuar(a.continuar, revisor=a.revisor, textos={a.continuar[0]: texto} if texto else None)
    else:
        noticias = _leer_noticias(a.noticia) if a.noticia else None
        textos = None
        if texto:
            if not noticias or len(noticias) != 1:
                ap.error("--texto-noticia exige exactamente una noticia")
            textos = {noticias[0]["id"]: texto}
        reg = ciclo.correr(noticias=noticias, max_tareas=a.max_tareas, nivel=a.nivel,
                           filtrar=a.con_filtro if noticias is not None else None, textos=textos)
    print(_resumen(reg))
    return 3 if reg["detenido_por_tope"] else 0


if __name__ == "__main__":
    sys.exit(main())
