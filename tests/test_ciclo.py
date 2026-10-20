"""Tests del ciclo (pipeline/ciclo.py), sin red: ClienteFalso de pipeline/llm.py y un simulador falso.

Cubre: ciclo feliz hasta `verificada` con artefactos que validan (redactor, ilustrador, verificador y
bibliotecario reales con respuestas falsas); iteración bajo umbral que se archiva a la 3.ª evaluación;
mediana de 3 corridas y marca de inestabilidad; rechazo del verificador → retroceso; detención por tope;
aislamiento del simulador (invariante 6); y los pendientes técnicos de config.yaml.
"""
import copy
import json
from pathlib import Path

import pytest

from conftest import RAIZ, cargar_ejemplo
from pipeline import ciclo as C
from pipeline import invariantes as inv
from pipeline import orquestador as orq
from pipeline.llm import ClienteFalso, config, costo_usd, modelo_de

IDS = [c["id"] for c in inv.cargar_rub01()["criterios"]]
CASO_RED = RAIZ / "evals" / "casos" / "redactor" / "caso1-ok-embalse-3-escenarios"
REVISOR = "Carlos Rojas Bruna"
TID = "2026-10-embalse-el-yeso"


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- fábricas
def rub(bajos: dict | None = None, nota: str = "") -> dict:
    """Salida cruda del evaluador (forma de evaluador.esquema_salida) con puntaje 2 salvo `bajos`."""
    bajos = bajos or {}
    crit = {i: {"cita": "¿Tienen razón?", "justificacion": f"justificación {nota} {i}".strip(),
                "puntaje": bajos.get(i, 2)} for i in IDS}
    return {"version_rubrica": "4.0", "criterios": crit, "total": sum(c["puntaje"] for c in crit.values()),
            "mejoras": [{"criterio": i, "mejora_minima": f"mejora {nota} {i}"} for i in IDS if bajos.get(i, 2) < 2]}


OK_23 = {"validacion": 1}                                       # 23/24
BAJO_18 = {"genuino": 1, "abierta": 1, "ciclo": 1, "validacion": 1, "fecundidad": 1, "recursos": 1}  # 18/24


def tarea_base() -> dict:
    t = cargar_ejemplo("tarea")
    # verificador v1.1: la fuente del ejemplo del contrato ("informe de la empresa sanitaria") no es concreta
    for r in t["estudiante"]["recursos_a_solicitud"]:
        if r["fuente"].startswith("otra fuente"):
            r["fuente"] = "otra fuente: Superintendencia de Servicios Sanitarios, informe de consumo 2025"
    return t


def candidato_b(t: dict) -> dict:
    b = copy.deepcopy(t)
    b["id"] = TID + "-b"
    b["titulo"] = "¿Alcanza el agua del embalse hasta marzo?"
    return b


def disenar_falso(n_candidatos: int = 2):
    def disenar(noticia, nivel, *, cliente, texto_noticia):
        t = tarea_base()
        cands = [t, candidato_b(t)][:n_candidatos]
        return {"candidatos": cands, "enfoques": [], "meta": {"costo_usd": 0.0}}
    return disenar


def iterar_falso(tarea, evaluacion, noticia, *, cliente, texto_noticia):
    nueva = copy.deepcopy(tarea)
    nueva["version"] = tarea["version"] + 1
    nueva["estado"] = "borrador"
    nueva["rubrica_rub01"] = None
    return {"tarea": nueva, "atencion_mejoras": [{"criterio": m["criterio"], "cambio": "x"}
                                                 for m in evaluacion["rub01"]["mejoras"]], "meta": {}}


def simulador_falso(trazas: dict, dir_transcripciones: Path | None = None, *, filtrar_task_space=False):
    """Imita sim.py: por corrida, una llamada de estudiante (sin schema) y una del codificador (con
    schema), ambas por el hook real del adapter (simulador/adapter/hooked.py)."""
    from simulador.adapter.generar import render_task_space
    from simulador.adapter.hooked import crear_llamar

    llamado = {"n": 0}

    def simular(tarea, dir_tarea, *, cliente, presupuesto_usd):
        llamado["n"] += 1
        llamar = crear_llamar(tarea, backend="api", cliente=cliente)
        vista = inv.vista_estudiante(tarea)
        sistema_est = f"Eres estudiante.\nTAREA:\n{vista['enunciado_es']}\n{vista['foto_descripcion']}"
        if filtrar_task_space:
            sistema_est += "\n" + render_task_space(tarea["task_space"])
        for c in trazas["por_corrida"]:
            llamar(sistema_est, "CONVERSACIÓN HASTA AHORA:\n(inicio)", modelo_de("simulador"))
            llamar("Codificador.\n" + render_task_space(tarea["task_space"]), "transcripción",
                   modelo_de("simulador_codificador"), schema={"type": "object", "properties": {"ok": {"type": "boolean"}}})
        d = Path(dir_tarea) / "sim" / "corridas"
        d.mkdir(parents=True, exist_ok=True)
        if dir_transcripciones is not None:
            for p in Path(dir_transcripciones).glob("*.md"):
                (d / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        t = copy.deepcopy(trazas)
        t["tarea_id"] = tarea["id"]
        return {"trazas": t, "errores": [], "avisos": [], "dir_transcripciones": str(d),
                "manifiesto": {"diseno": "diseno_otm", "insumos_simulador": {"INS09": "INS09_prueba.md"}}}
    simular.llamado = llamado
    return simular


def respuestas_simulador(n_corridas: int) -> list:
    return [r for _ in range(n_corridas) for r in ("Hola, empecemos.", {"ok": True})]


@pytest.fixture
def rutas(tmp_path):
    return C.Rutas(expedientes=tmp_path / "expedientes", trabajo=tmp_path / "trabajo",
                   ciclos=tmp_path / "ciclos", gasto_semanal=tmp_path / "gasto_semanal.json")


def nuevo_ciclo(rutas, respuestas, **kw):
    agentes = kw.pop("agentes", None) or C.Agentes()
    return C.Ciclo(agentes=agentes, rutas=rutas, cliente=ClienteFalso(respuestas), salida=lambda s: None, **kw)


def tramo_a(rutas, evals: list, n_candidatos: int = 1, **kw):
    """Corre el tramo A con un diseñador falso y el evaluador real (ClienteFalso)."""
    ag = C.Agentes(disenar=disenar_falso(n_candidatos), iterar=iterar_falso)
    c = nuevo_ciclo(rutas, evals, agentes=ag, **kw)
    reg = c.correr(noticias=[cargar_ejemplo("noticia")], max_tareas=1, nivel="S")
    return c, reg


def validar_artefactos(exp: orq.Expediente):
    for nombre, art in exp.artefactos.items():
        r = inv.validar_contra_esquema(art, orq.CONTRATO_DE[nombre])
        assert r, (nombre, r.errores)


# =========================================================================== ciclo feliz
def test_ciclo_feliz_hasta_verificada(rutas):
    # Tramo A: 2 candidatos × 3 corridas del evaluador (A: 23/24; B: 21/24)
    evals = [rub(OK_23)] * 3 + [rub({"validacion": 1, "ciclo": 1, "nivel": 1})] * 3
    _, reg = tramo_a(rutas, evals, n_candidatos=2)
    assert reg["expedientes"] == {TID: "evaluada", TID + "-b": "archivada"}
    assert reg["pendientes_humanos"] == [{"tarea_id": TID, "pendiente": "revision_humana_1", "estado": "evaluada"}]
    exp = orq.cargar(TID, rutas.expedientes)
    assert "revisada" not in [h["a"] for h in exp.historial]          # el ciclo no inventa revisores
    b = orq.cargar(TID + "-b", rutas.expedientes)
    assert "candidato no elegido" in b.historial[-1]["motivo"]

    # Tramo B: revisión humana 1 explícita; simulador falso por el hook real; redactor, ilustrador,
    # verificador y bibliotecario reales con respuestas falsas.
    trazas = _j(CASO_RED / "trazas_resumen.json")
    ilu = _j(RAIZ / "evals" / "casos" / "ilustrador" / "01-embalse-valido.json")["respuestas_modelo"][0]
    resp = (respuestas_simulador(trazas["corridas"]) + _j(CASO_RED / "respuestas_falsas.json")
            + [ilu, {"cifras": [], "afirmaciones_no_respaldadas": [], "recursos": []}])
    sim = simulador_falso(trazas, CASO_RED / "transcripciones")
    c = nuevo_ciclo(rutas, resp, agentes=C.Agentes(simular=sim))
    reg = c.continuar([TID], revisor=REVISOR)
    assert reg["errores"] == [], reg["errores"]
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "verificada"
    assert [h["a"] for h in exp.historial] == ["borrador", "evaluada", "revisada", "simulada", "con_guia", "verificada"]
    assert exp.historial[2]["revisor"] == REVISOR
    validar_artefactos(exp)
    assert inv.cumple_umbral_rub01(exp.artefactos["evaluacion"])
    assert inv.escenarios_respaldados(exp.artefactos["guia"], exp.artefactos["trazas_resumen"])
    assert exp.artefactos["guia"]["trazabilidad"]["revision_humana_1"]["revisor"] == REVISOR

    # Invariante 8: reproducibilidad completa
    rep = exp.artefactos["evaluacion"]["reproducibilidad"]
    assert {"evaluador", "simulador", "simulador_codificador", "redactor", "redactor_escenarios",
            "ilustrador", "verificador"} <= set(rep["agentes"])
    assert rep["agentes"]["evaluador"]["modelo"] == modelo_de("evaluador")
    assert rep["agentes"]["simulador_codificador"]["modelo"] == modelo_de("simulador_codificador")
    assert rep["agentes"]["simulador"]["version_prompt"] == "INS09_prueba.md"
    assert rep["version_rubrica"] == "4.0" and rep["version_MAR03"] == "1.0"
    assert rep["version_MED01"] == C.version_med01()
    assert rep["diseno_simulador"] == trazas["diseno"]
    assert rep["costo_usd"] == pytest.approx(sum(a["costo_usd"] for a in rep["agentes"].values()))
    assert rep["costo_usd"] > 0
    # Pendiente humano 2 y bibliotecario en dry-run (no escribe en tareas/)
    assert exp.marcas["pendiente"] == "revision_humana_2"
    assert exp.marcas["bibliotecario_dry_run"]["ok"], exp.marcas["bibliotecario_dry_run"]
    dry = (rutas.de(TID) / "bibliotecario_dry_run.txt").read_text(encoding="utf-8")
    assert "DRY-RUN" in dry
    assert not (RAIZ / "tareas" / "2026-10" / "embalse-el-yeso").exists()
    assert (rutas.de(TID) / "icono.svg").exists()
    # registro del ciclo y gasto semanal
    assert Path(reg["archivo"]).exists()
    assert C.gasto_semana(rutas.gasto_semanal, C.semana_iso()) == pytest.approx(
        reg["gasto"]["semana_usd"], abs=1e-6)


def test_tramo_b_exige_revisor(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    sim = simulador_falso(cargar_ejemplo("trazas_resumen"))
    c = nuevo_ciclo(rutas, [], agentes=C.Agentes(simular=sim))
    reg = c.continuar([TID])
    assert orq.cargar(TID, rutas.expedientes).estado == "evaluada"
    assert "falta --revisor" in reg["errores"][0]["error"]
    assert sim.llamado["n"] == 0


def test_cli_rechaza_revisor_sin_continuar():
    with pytest.raises(SystemExit):
        C.main(["--noticia", str(RAIZ / "contratos" / "ejemplos" / "noticia_ejemplo.json"), "--revisor", "X"])


# =========================================================================== iteración y archivo
def test_bajo_umbral_itera_y_archiva_a_la_tercera_evaluacion(rutas):
    evals = [rub(BAJO_18, f"e{i}") for i in range(12)]   # 2 candidatos × 3 + 2 iteraciones × 3
    _, reg = tramo_a(rutas, evals, n_candidatos=2)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "archivada"
    assert exp.iteraciones == 3
    assert [h["a"] for h in exp.historial] == ["borrador", "evaluada", "borrador", "evaluada", "borrador",
                                               "evaluada", "archivada"]
    motivo = exp.historial[-1]["motivo"]
    assert "18/24" in motivo and "tras 3 evaluaciones" in motivo and "genuino=1" in motivo
    assert exp.artefactos["tarea"]["version"] == 3
    doc = _j(rutas.de(TID) / "evaluacion_corridas.json")
    assert [e["iteracion"] for e in doc["evaluaciones"]] == [1, 2, 3]
    assert [e["version_tarea"] for e in doc["evaluaciones"]] == [1, 2, 3]
    assert C.validar_corridas(doc) == []
    assert reg["pendientes_humanos"] == []
    with pytest.raises(orq.TransicionIlegal):   # terminal
        orq.transicionar(exp, "borrador")


def test_iteracion_que_alcanza_el_umbral_queda_pendiente(rutas):
    evals = [rub(BAJO_18)] * 3 + [rub(OK_23)] * 3
    _, reg = tramo_a(rutas, evals)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "evaluada" and exp.iteraciones == 2
    assert exp.marcas["pendiente"] == "revision_humana_1"
    assert exp.artefactos["tarea"]["rubrica_rub01"]["total"] == 23


# =========================================================================== mediana e inestabilidad
def test_mediana_por_criterio_unitaria():
    r1 = rub({"genuino": 0, "abierta": 1}, "r1")
    r2 = rub({"genuino": 1}, "r2")
    r3 = rub({"genuino": 2, "abierta": 1, "ciclo": 0}, "r3")
    for r in (r1, r2, r3):
        r["total"] = sum(c["puntaje"] for c in r["criterios"].values())
    med, det = C.mediana_rub01([r1, r2, r3])
    assert det["por_criterio"]["genuino"] == 1 and det["corrida_fuente"]["genuino"] == 2
    assert det["por_criterio"]["abierta"] == 1 and det["corrida_fuente"]["abierta"] == 1
    assert det["por_criterio"]["ciclo"] == 2
    assert med["criterios"]["genuino"]["justificacion"].startswith("justificación r2")
    assert med["total"] == 22 == sum(det["por_criterio"].values())
    assert [m["criterio"] for m in med["mejoras"]] == ["genuino", "abierta"]
    assert inv.consistencia_rub01(med) and inv.validar_contra_esquema(med, "evaluacion_rub01")
    # n par: mediana inferior (conservadora)
    med2, _ = C.mediana_rub01([rub({"genuino": 1}), rub()])
    assert med2["criterios"]["genuino"]["puntaje"] == 1


def test_tres_corridas_mediana_y_marca_inestable(rutas):
    evals = [rub(), rub({"validacion": 1, "ciclo": 1}), rub({"validacion": 1, "ciclo": 1, "genuino": 1,
                                                              "fecundidad": 1, "autenticidad": 1})]
    c, reg = tramo_a(rutas, evals)   # totales 24, 22, 19 → rango 5 ≥ 4
    assert len(c.contador.registro) == config()["evaluador"]["corridas"] == 3
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "evaluada"
    assert exp.marcas["evaluacion_inestable"] is True and exp.marcas["evaluacion_rango_total"] == 5
    assert reg["pendientes_humanos"][0]["evaluacion_inestable"] is True
    rub01 = exp.artefactos["evaluacion"]["rub01"]
    assert rub01["total"] == 22    # mediana por criterio: validacion=1, ciclo=1, resto 2
    doc = _j(rutas.de(TID) / "evaluacion_corridas.json")
    ev = doc["evaluaciones"][0]
    assert len(ev["corridas"]) == 3 and ev["totales"] == [24, 22, 19]
    assert ev["rango_total"] == 5 and ev["evaluacion_inestable"] is True
    assert C.validar_corridas(doc) == []


def test_tres_corridas_estables_sin_marca(rutas):
    _, _ = tramo_a(rutas, [rub(OK_23), rub(), rub({"validacion": 1, "ciclo": 1})])   # 23, 24, 22 → rango 2
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.marcas["evaluacion_inestable"] is False
    assert exp.artefactos["evaluacion"]["rub01"]["total"] == 23


# =========================================================================== verificador → retroceso
def _agentes_tramo_b(verificaciones: list[bool], redacciones: list):
    def redactar(tarea, trazas, transcripciones, contexto, *, cliente, texto_noticia):
        redacciones.append(contexto)
        g = cargar_ejemplo("guia")
        g["tarea_id"] = tarea["id"]  # como el redactor real
        g["version"] = tarea["version"]
        g["ficha"]["version"] = tarea["version"]
        g["ficha"]["puntaje_rub01"] = contexto["puntaje_rub01"]
        g["trazabilidad"]["rub01_total"] = contexto["puntaje_rub01"]
        g["trazabilidad"]["revision_humana_1"] = contexto["revision_humana_1"]
        return {"guia": g, "meta": {}}

    def verificar(tarea, guia, trazas, noticia, *, cliente, texto_noticia):
        ok = verificaciones.pop(0)
        return {"tarea_id": tarea["id"], "aprobado": ok, "estado_destino": "verificada" if ok else "simulada",
                "hallazgos": [] if ok else [{"invariante": "4", "severidad": "critico", "ubicacion": "guia.escenarios[0]",
                                             "descripcion": "cifra sin localizador", "origen": "codigo"}],
                "cifras_contrastadas": [], "notebook": {}, "meta": {}}

    return C.Agentes(simular=simulador_falso(cargar_ejemplo("trazas_resumen")), redactar=redactar,
                     ilustrar=lambda tarea, *, cliente: {"svg": "<svg/>", "tarea_id": tarea["id"]},
                     verificar=verificar, publicar=lambda *a, **k: {"ruta": "x", "rama": "y", "lineas": []})


def test_rechazo_del_verificador_retrocede_y_rehace_la_guia(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    redacciones: list = []
    ag = _agentes_tramo_b([False, True], redacciones)
    c = nuevo_ciclo(rutas, respuestas_simulador(6), agentes=ag)
    c.continuar([TID], revisor=REVISOR)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "verificada"
    assert [h["a"] for h in exp.historial][-5:] == ["simulada", "con_guia", "simulada", "con_guia", "verificada"]
    assert "verificador rechaza la guía (rechazo 1)" in exp.historial[-3]["motivo"]
    assert len(redacciones) == 2 and exp.marcas["rechazos_verificador"] == 1
    assert (rutas.de(TID) / "verificacion_1.json").exists() and (rutas.de(TID) / "verificacion_2.json").exists()
    validar_artefactos(exp)


def test_segundo_rechazo_del_verificador_archiva(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    redacciones: list = []
    c = nuevo_ciclo(rutas, respuestas_simulador(6), agentes=_agentes_tramo_b([False, False], redacciones))
    c.continuar([TID], revisor=REVISOR)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "archivada"
    assert "rechazó la guía 2 veces" in exp.historial[-1]["motivo"]
    assert len(redacciones) == 2


# =========================================================================== tope
def test_detencion_por_tope_deja_expedientes_en_su_estado(rutas):
    usd_llamada = costo_usd({"input_tokens": 1000, "output_tokens": 200}, modelo_de("evaluador"))
    presupuesto = 3 * usd_llamada - 1e-9          # alcanza para las 3 corridas del candidato A, no más
    evals = [rub(OK_23)] * 6
    c, reg = tramo_a(rutas, evals, n_candidatos=2, presupuesto_ciclo_usd=presupuesto)
    assert reg["detenido_por_tope"] is True
    assert reg["expedientes"] == {TID: "evaluada", TID + "-b": "borrador"}
    assert len(c.contador.registro) == 3
    assert orq.cargar(TID + "-b", rutas.expedientes).estado == "borrador"
    assert Path(reg["archivo"]).exists()
    assert any(e["tipo"] == "detencion_por_tope" for e in reg["eventos"])
    semana = C.semana_iso()
    assert C.gasto_semana(rutas.gasto_semanal, semana) == pytest.approx(3 * usd_llamada)

    # Un ciclo posterior de la misma semana con el tope ya consumido no hace ninguna llamada.
    fr = config()["fraccion_detencion"]
    cli = ClienteFalso([rub(OK_23)] * 3)
    c2 = C.Ciclo(agentes=C.Agentes(disenar=disenar_falso(1)), rutas=rutas, cliente=cli,
                 tope_semanal_usd=(3 * usd_llamada) / fr)
    reg2 = c2.correr(noticias=[cargar_ejemplo("noticia")], max_tareas=1, nivel="S")
    assert reg2["detenido_por_tope"] is True and cli.llamadas == []


def test_reanudar_tras_tope(rutas):
    usd_llamada = costo_usd({"input_tokens": 1000, "output_tokens": 200}, modelo_de("evaluador"))
    tramo_a(rutas, [rub(OK_23)] * 6, n_candidatos=2, presupuesto_ciclo_usd=3 * usd_llamada - 1e-9)
    c = nuevo_ciclo(rutas, [rub(OK_23)] * 3)
    c.continuar([TID + "-b"])
    exp = orq.cargar(TID + "-b", rutas.expedientes)
    assert exp.estado == "evaluada" and exp.marcas["pendiente"] == "revision_humana_1"


# =========================================================================== aislamiento (invariante 6)
def _hasta_revisada(rutas, tarea: dict) -> None:
    exp = orq.nuevo_expediente(tarea, cargar_ejemplo("noticia"))
    exp = orq.transicionar(exp, "evaluada", artefactos={"evaluacion": cargar_ejemplo("evaluacion")})
    exp = orq.transicionar(exp, "revisada", revisor=REVISOR)
    orq.guardar(exp, rutas.expedientes)


def test_simulador_no_recibe_task_space(rutas):
    _hasta_revisada(rutas, tarea_base())
    cli = ClienteFalso(respuestas_simulador(6))
    sim = simulador_falso(cargar_ejemplo("trazas_resumen"))
    c = C.Ciclo(agentes=C.Agentes(simular=sim, redactar=lambda *a, **k: (_ for _ in ()).throw(RuntimeError("alto"))),
                rutas=rutas, cliente=cli)
    c.continuar([TID])
    assert orq.cargar(TID, rutas.expedientes).estado == "simulada"
    ts = tarea_base()["task_space"]
    textos_ts = [t for t in inv.textos_de(ts) if len(t) >= 20]
    estudiantes = [ll for ll in cli.llamadas if "output_config" not in ll]
    codificador = [ll for ll in cli.llamadas if "output_config" in ll]
    assert len(estudiantes) == len(codificador) == 6
    for ll in estudiantes:
        enviado = ll["system"][0]["text"] + json.dumps(ll["messages"], ensure_ascii=False)
        assert "task_space" not in enviado and "reference_solution" not in enviado
        assert not any(t in enviado for t in textos_ts)
    assert any(ts["reference_solution"]["steps"] in ll["system"][0]["text"] for ll in codificador)


def test_hook_bloquea_task_space_en_llamada_de_estudiante(rutas):
    _hasta_revisada(rutas, tarea_base())
    cli = ClienteFalso(respuestas_simulador(6))
    sim = simulador_falso(cargar_ejemplo("trazas_resumen"), filtrar_task_space=True)
    reg = C.Ciclo(agentes=C.Agentes(simular=sim), rutas=rutas, cliente=cli).continuar([TID])
    assert orq.cargar(TID, rutas.expedientes).estado == "revisada"
    assert cli.llamadas == []                     # el hook corta antes de la red
    assert "AislamientoError" in reg["errores"][0]["error"]


def test_tarea_con_task_space_en_el_enunciado_no_se_simula(rutas):
    t = tarea_base()
    t["estudiante"]["enunciado_es"] += " " + t["task_space"]["reference_solution"]["steps"]
    _hasta_revisada(rutas, t)
    sim = simulador_falso(cargar_ejemplo("trazas_resumen"))
    reg = C.Ciclo(agentes=C.Agentes(simular=sim), rutas=rutas, cliente=ClienteFalso([])).continuar([TID])
    assert sim.llamado["n"] == 0
    assert orq.cargar(TID, rutas.expedientes).estado == "revisada"
    assert reg["errores"][0].get("invariante") is True and "Invariante 6" in reg["errores"][0]["error"]


# =========================================================================== entrada del evaluador
def test_entrada_evaluador_sin_task_space():
    t = tarea_base()
    e = C.entrada_evaluador(t)
    assert e["nivel_declarado"] == {"nivel": "S", "sub_tramo": "S1"}
    assert e["mapa_ciclo"] is None and t["estudiante"]["enunciado_es"] in e["texto"]
    plano = json.dumps(e, ensure_ascii=False)
    assert t["task_space"]["reference_solution"]["steps"] not in plano
    assert len(e["recursos"]) == 2


# =========================================================================== pendientes técnicos (config.yaml)
def test_evaluador_lee_modelo_y_precios_de_config():
    from pipeline.agentes.evaluador import evaluador as ev
    assert ev.MODELO == modelo_de("evaluador")
    assert ev.PRECIOS == config()["precios_modelos"][modelo_de("evaluador")]
    cli = ClienteFalso([rub(OK_23)])
    r = ev.evaluar(C.entrada_evaluador(tarea_base()), cliente=cli)
    assert cli.llamadas[0]["model"] == modelo_de("evaluador")
    assert r["meta"]["costo_usd"] == costo_usd(
        {"input_tokens": 1000, "output_tokens": 200}, modelo_de("evaluador"))
    assert r["meta"]["version_prompt"] == ev.VERSION_PROMPT == "1.3"


def test_codificador_del_simulador_desde_config():
    from simulador.adapter import generar
    assert config()["modelos"]["simulador_codificador"] == generar.modelo_codificador_defecto()
    assert generar.MODELO_CODIFICADOR_DEFECTO == modelo_de("simulador_codificador")


def test_requirements_incluye_defusedxml():
    req = (RAIZ / "requirements.txt").read_text(encoding="utf-8").lower()
    for dep in ("anthropic", "pyyaml", "jsonschema", "referencing", "defusedxml"):
        assert dep in req


# =========================================================================== agentes reales del tramo A
def test_tramo_a_con_disenador_real(rutas):
    caso = _j(RAIZ / "evals" / "casos" / "disenador" / "s-cuenta-luz.json")
    resp = list(caso["respuestas_simuladas"]) + [rub(OK_23)] * 3 + [rub({"validacion": 1, "ciclo": 1})] * 3
    c = nuevo_ciclo(rutas, resp)
    reg = c.correr(noticias=[caso["noticia"]], max_tareas=1, nivel=caso["nivel"])
    assert reg["errores"] == [], reg["errores"]
    estados = sorted(reg["expedientes"].values())
    assert estados == ["archivada", "evaluada"]
    elegido = next(t for t, e in reg["expedientes"].items() if e == "evaluada")
    exp = orq.cargar(elegido, rutas.expedientes)
    validar_artefactos(exp)
    rep = exp.artefactos["evaluacion"]["reproducibilidad"]
    assert rep["agentes"]["disenador"]["modelo"] == modelo_de("disenador")
    assert "disenador" in exp.marcas["costos_compartidos"]
    assert rep["diseno_simulador"] is None          # aún no simulada


def test_explorador_aplica_filtro_y_descarta(rutas):
    noticias = [dict(cargar_ejemplo("noticia"), id=f"2026-10-14-cnnchile-embalse-{i}") for i in range(2)]
    for n in noticias:
        n.pop("filtro", None)

    def filtrar(noticia, *, cliente):
        n = copy.deepcopy(noticia)
        pasa = noticia["id"].endswith("-1")
        n["filtro"] = {"version_rubrica": "4.0", "puntajes": {k: 2 if pasa else 1 for k in
                       ("genuino", "decisiones", "realismo", "autenticidad", "validacion")},
                       "total": 10 if pasa else 5, "pasa": pasa, "justificacion": "prueba"}
        return {"noticia": n, "meta": {}}

    ag = C.Agentes(explorar=lambda *, cliente, tope_usd: {"noticias": noticias, "descartes": []},
                   filtrar=filtrar, disenar=disenar_falso(1))
    reg = nuevo_ciclo(rutas, [rub(OK_23)] * 3, agentes=ag).correr(max_tareas=1)
    assert reg["noticias"][0]["resultado"].startswith("no pasa el filtro")
    assert reg["noticias"][1]["resultado"] == "evaluada"
    assert reg["explorador"] == {"aceptadas": 2, "descartadas": 0}
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.artefactos["noticia"]["filtro"]["pasa"] is True
    assert exp.marcas["nivel_objetivo"] == "P"      # rotación S, P, U por noticia


# =========================================================================== invariante 3 con texto releído
def test_releer_noticia_pasa_el_texto_al_hook_de_invariante_3(rutas):
    """Sin --texto-noticia, el ciclo relee la noticia en memoria y el hook la usa en cada transición."""
    leidas = []

    def leer(url):
        leidas.append(url)
        return "texto de la noticia sin relación con la tarea"

    _, reg = tramo_a(rutas, [rub(OK_23)] * 3, releer_noticia=True, leer_noticia=leer)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "evaluada"
    assert leidas and len(set(leidas)) == 1  # se lee una vez por noticia y se reutiliza


def test_releer_noticia_bloquea_copia_literal(rutas):
    tarea = tarea_base()
    copia = " ".join(f"palabra{i}" for i in range(30))
    tarea["estudiante"]["enunciado_es"] = copia + " " + tarea["estudiante"]["enunciado_es"]
    ag = C.Agentes(disenar=lambda *a, **k: {"candidatos": [tarea], "meta": {}}, iterar=iterar_falso)
    c = nuevo_ciclo(rutas, [rub(OK_23)] * 3, agentes=ag, releer_noticia=True, leer_noticia=lambda u: copia)
    c.correr(noticias=[cargar_ejemplo("noticia")], max_tareas=1, nivel="S")
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "borrador"  # el hook impidió pasar a evaluada
    assert "Invariante 3" in json.dumps(exp.marcas.get("ultimo_error"), ensure_ascii=False)


def test_releer_noticia_que_falla_queda_registrada(rutas):
    def leer(url):
        raise OSError("robots.txt prohíbe")

    c, reg = tramo_a(rutas, [rub(OK_23)] * 3, releer_noticia=True, leer_noticia=leer)
    assert any(e["tipo"] == "invariante3_sin_texto" for e in reg["eventos"])


# =========================================================================== revisión humana 2
def test_rehacer_guia_por_revision_humana_2(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    redacciones: list = []
    c = nuevo_ciclo(rutas, respuestas_simulador(6), agentes=_agentes_tramo_b([True], redacciones))
    c.continuar([TID], revisor=REVISOR)
    assert orq.cargar(TID, rutas.expedientes).estado == "verificada"

    obs = ["E4 sobreinterpreta la corrida", "usar coma decimal"]
    c2 = nuevo_ciclo(rutas, [], agentes=_agentes_tramo_b([True], redacciones))
    reg = c2.rehacer_guia({TID: obs}, revisor=REVISOR)
    assert reg["errores"] == [], reg["errores"]
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "verificada" and exp.marcas["pendiente"] == "revision_humana_2"
    assert [h["a"] for h in exp.historial][-4:] == ["verificada", "simulada", "con_guia", "verificada"]
    assert exp.historial[-3]["motivo"].startswith("revisión humana 2 rechaza la guía v1")
    ctx = redacciones[-1]
    assert ctx["observaciones_revision"] == obs and ctx["version"] == 2 and "v2" in ctx["cambios"]


def test_rehacer_guia_exige_verificada_y_revisor(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    c = nuevo_ciclo(rutas, [], agentes=_agentes_tramo_b([], []))
    with pytest.raises(ValueError):
        c.rehacer_guia({TID: ["x"]}, revisor="")
    reg = c.rehacer_guia({TID: ["x"]}, revisor=REVISOR)
    assert "exige `verificada`" in reg["errores"][0]["error"]
    assert orq.cargar(TID, rutas.expedientes).estado == "evaluada"


# =========================================================================== nueva versión de una tarea
def _hasta_verificada(rutas, redacciones):
    tramo_a(rutas, [rub(OK_23)] * 3)
    c = nuevo_ciclo(rutas, respuestas_simulador(6), agentes=_agentes_tramo_b([True], redacciones))
    c.continuar([TID], revisor=REVISOR)
    assert orq.cargar(TID, rutas.expedientes).estado == "verificada"


MEJORAS = [{"criterio": "recursos", "mejora_minima": "marcar el supuesto de R4"}]


def test_nueva_version_reutiliza_simulacion_y_guia_base(rutas):
    redacciones: list = []
    _hasta_verificada(rutas, redacciones)
    ag = _agentes_tramo_b([True], redacciones)
    ag.iterar = iterar_falso
    sim_llamado = ag.simular.llamado
    n_sim = sim_llamado["n"]
    c = nuevo_ciclo(rutas, [rub(OK_23)] * 3, agentes=ag)
    reg = c.nueva_version({TID: MEJORAS})
    tid2 = TID + "-v2"
    assert reg["errores"] == [], reg["errores"]
    exp2 = orq.cargar(tid2, rutas.expedientes)
    assert exp2.estado == "evaluada" and exp2.marcas["pendiente"] == "revision_humana_1"
    assert exp2.artefactos["tarea"]["version"] == 2
    assert orq.cargar(TID, rutas.expedientes).estado == "verificada"   # la v1 no se toca
    # tramo B con revisión humana 1: no se re-simula (enunciado y foto iguales) y la guía v1 es la base
    c2 = nuevo_ciclo(rutas, [], agentes=ag)
    c2.continuar([tid2], revisor=REVISOR)
    exp2 = orq.cargar(tid2, rutas.expedientes)
    assert exp2.estado == "verificada"
    assert ag.simular.llamado["n"] == n_sim
    assert exp2.marcas["simulacion_reutilizada_de"] == TID
    assert exp2.artefactos["trazas_resumen"]["tarea_id"] == tid2
    assert redacciones[-1]["guia_base"]["tarea_id"] == TID
    assert exp2.artefactos["evaluacion"]["reproducibilidad"]["agentes"]["simulador"]["costo_usd"] == 0.0
    validar_artefactos(exp2)


def test_nueva_version_con_enunciado_cambiado_vuelve_a_simular(rutas):
    redacciones: list = []
    _hasta_verificada(rutas, redacciones)
    ag = _agentes_tramo_b([True], redacciones)

    def iterar_cambia(tarea, evaluacion, noticia, *, cliente, texto_noticia):
        r = iterar_falso(tarea, evaluacion, noticia, cliente=cliente, texto_noticia=texto_noticia)
        r["tarea"]["estudiante"]["enunciado_es"] += " Usen coma decimal."
        return r

    ag.iterar = iterar_cambia
    c = nuevo_ciclo(rutas, [rub(OK_23)] * 3 + respuestas_simulador(6), agentes=ag)
    c.nueva_version({TID: MEJORAS})
    n_sim = ag.simular.llamado["n"]
    c2 = nuevo_ciclo(rutas, respuestas_simulador(6), agentes=ag)
    reg = c2.continuar([TID + "-v2"], revisor=REVISOR)
    assert ag.simular.llamado["n"] == n_sim + 1
    assert "simulacion_reutilizada_de" not in orq.cargar(TID + "-v2", rutas.expedientes).marcas
    assert any(e["tipo"] == "simulacion_no_reutilizable" for e in reg["eventos"])
