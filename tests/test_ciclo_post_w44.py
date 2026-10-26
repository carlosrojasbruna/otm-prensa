"""Ciclo tras el lote de corrección post-W44 (2026-10-26): verificación previa antes de simular, hallazgo del
verificador sobre la tarea → `evaluada` (no se archiva), --aceptar-hallazgos y --archivar. Sin red ni API."""
import pytest

from conftest import cargar_ejemplo
from pipeline import ciclo as C
from pipeline import orquestador as orq
from test_ciclo import (OK_23, REVISOR, TID, _agentes_tramo_b, nuevo_ciclo, respuestas_simulador, rub, rutas,  # noqa: F401
                        tramo_a, validar_artefactos)

HALLAZGO_TAREA = {"invariante": "4", "severidad": "critico", "ubicacion": "tarea.noticia.cifras_usadas[0]",
                  "descripcion": "localizador erróneo: 48 no está en «párrafo 5» sino en el párrafo 9", "origen": "codigo"}


def _contar(fn, cuenta: list):
    def envuelta(*a, **k):
        cuenta.append(1)
        return fn(*a, **k)
    return envuelta


def _informe_tarea(tarea, hallazgos=(), corregidos=None):
    return {"tarea_id": tarea["id"], "aprobado": not any(h["severidad"] == "critico" for h in hallazgos),
            "alcance": "tarea", "hallazgos": list(hallazgos), "cifras_contrastadas": [],
            "localizadores_corregidos": corregidos or {}, "meta": {}}


def _agentes(verificaciones, redacciones, simulaciones, verificar_tarea=None):
    ag = _agentes_tramo_b(verificaciones, redacciones)
    ag.simular = _contar(ag.simular, simulaciones)
    ag.verificar_tarea = verificar_tarea or (lambda tarea, noticia, *, texto_noticia: _informe_tarea(tarea))
    return ag


def _verificar_con(hallazgos_por_llamada: list):
    def verificar(tarea, guia, trazas, noticia, *, cliente, texto_noticia):
        hs = hallazgos_por_llamada.pop(0)
        ok = not hs
        return {"tarea_id": tarea["id"], "aprobado": ok, "estado_destino": "verificada" if ok else "evaluada",
                "hallazgos": hs, "cifras_contrastadas": [], "notebook": {}, "meta": {}}
    return verificar


# --------------------------------------------------------------------------- (b) hallazgo sobre la tarea
def test_hallazgo_sobre_la_tarea_vuelve_a_evaluada_sin_archivar(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    redacciones, simulaciones = [], []
    ag = _agentes([], redacciones, simulaciones)
    ag.verificar = _verificar_con([[HALLAZGO_TAREA]])
    c = nuevo_ciclo(rutas, respuestas_simulador(6), agentes=ag)
    reg = c.continuar([TID], revisor=REVISOR)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "evaluada" and exp.iteraciones == 1          # no cuenta como evaluación nueva
    assert [h["a"] for h in exp.historial][-4:] == ["revisada", "simulada", "con_guia", "evaluada"]
    assert "hallazgos sobre la tarea" in exp.historial[-1]["motivo"]
    assert "guia" not in exp.artefactos and "trazas_resumen" in exp.artefactos
    assert exp.marcas["hallazgos_tarea"] and exp.marcas["pendiente"] == "revision_humana_1"
    assert "rechazos_verificador" not in exp.marcas and len(redacciones) == 1   # no se rehízo la guía
    assert {"tarea_id": TID, "pendiente": "revision_humana_1", "estado": "evaluada"} in reg["pendientes_humanos"]
    validar_artefactos(exp)

    # el revisor del tramo B no resuelve el hallazgo por sí solo
    c2 = nuevo_ciclo(rutas, [], agentes=ag)
    reg2 = c2.continuar([TID], revisor=REVISOR)
    assert "hallazgos del verificador" in reg2["errores"][0]["error"]
    assert orq.cargar(TID, rutas.expedientes).estado == "evaluada"

    # --aceptar-hallazgos: sigue, reutiliza la simulación (no simula de nuevo) y rehace la guía
    ag.verificar = _verificar_con([[HALLAZGO_TAREA]])   # el verificador vuelve a verlo: ya está aceptado
    c3 = nuevo_ciclo(rutas, [], agentes=ag)
    c3.continuar([TID], revisor=REVISOR, aceptar_hallazgos=True)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "verificada" and len(simulaciones) == 1 and len(redacciones) == 2
    assert exp.marcas["hallazgos_aceptados"][0]["revisor"] == REVISOR
    assert exp.marcas["verificada_con_hallazgos_aceptados"] is True
    validar_artefactos(exp)


def test_hallazgo_solo_en_la_guia_sigue_rehaciendo_la_guia(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    redacciones, simulaciones = [], []
    c = nuevo_ciclo(rutas, respuestas_simulador(6), agentes=_agentes([False, True], redacciones, simulaciones))
    c.continuar([TID], revisor=REVISOR)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "verificada" and exp.marcas["rechazos_verificador"] == 1 and len(redacciones) == 2


# --------------------------------------------------------------------------- (c) verificación previa
def test_verificacion_previa_bloquea_antes_de_simular(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    redacciones, simulaciones = [], []
    ag = _agentes([], redacciones, simulaciones,
                  verificar_tarea=lambda tarea, noticia, *, texto_noticia: _informe_tarea(tarea, [HALLAZGO_TAREA]))
    c = nuevo_ciclo(rutas, [], agentes=ag)
    c.continuar([TID], revisor=REVISOR)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "evaluada" and simulaciones == [] and c.contador.total == 0
    assert exp.marcas["preverificacion"]["criticos"] and exp.marcas["pendiente"] == "revision_humana_1"
    assert (rutas.de(TID) / "preverificacion.json").exists()


def test_verificacion_previa_en_revisada_no_simula(rutas):
    """Expedientes que ya estaban en `revisada` (que-tan-renida-fue) pasan por la verificación previa al reanudar."""
    tramo_a(rutas, [rub(OK_23)] * 3)
    exp = orq.cargar(TID, rutas.expedientes)
    orq.guardar(orq.transicionar(exp, "revisada", revisor=REVISOR), rutas.expedientes)
    simulaciones = []
    ag = _agentes([], [], simulaciones,
                  verificar_tarea=lambda tarea, noticia, *, texto_noticia: _informe_tarea(tarea, [HALLAZGO_TAREA]))
    reg = nuevo_ciclo(rutas, [], agentes=ag).continuar([TID])
    assert simulaciones == [] and orq.cargar(TID, rutas.expedientes).estado == "revisada"
    assert "verificación previa" in reg["errores"][0]["error"]


def test_verificacion_previa_corrige_localizador_y_sigue(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    corr = {"0": {"fuente": "noticia", "ubicacion": "párrafo 4"}}
    adv = {**HALLAZGO_TAREA, "severidad": "advertencia", "descripcion": "localizador corrido"}
    simulaciones = []
    ag = _agentes([True], [], simulaciones,
                  verificar_tarea=lambda tarea, noticia, *, texto_noticia: _informe_tarea(tarea, [adv], corr))
    nuevo_ciclo(rutas, respuestas_simulador(6), agentes=ag).continuar([TID], revisor=REVISOR)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "verificada" and len(simulaciones) == 1
    assert exp.artefactos["tarea"]["noticia"]["cifras_usadas"][0]["localizador"]["ubicacion"] == "párrafo 4"
    assert exp.marcas["localizadores_corregidos"][0]["etapa"] == "preverificacion"
    validar_artefactos(exp)


# --------------------------------------------------------------------------- --archivar (revisión humana 1 negativa)
def test_archivar_evaluada_con_motivo_y_revisor(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    reg = C.Ciclo(rutas=rutas, salida=lambda s: None).archivar([TID], motivo="revisión humana 1", revisor=REVISOR)
    exp = orq.cargar(TID, rutas.expedientes)
    assert exp.estado == "archivada" and exp.historial[-1]["motivo"] == f"revisión humana 1 ({REVISOR})"
    assert exp.marcas["revision_humana_1"]["resultado"] == "negativa" and "pendiente" not in exp.marcas
    assert reg["gasto"]["ciclo_usd"] == 0 and reg["orden"] == "archivar"
    reg2 = C.Ciclo(rutas=rutas, salida=lambda s: None).archivar([TID], motivo="otra vez", revisor=REVISOR)
    assert "exige `evaluada`" in reg2["errores"][0]["error"]


def test_archivar_exige_motivo_y_revisor(rutas):
    with pytest.raises(ValueError):
        C.Ciclo(rutas=rutas, salida=lambda s: None).archivar([TID], motivo="", revisor=REVISOR)
    with pytest.raises(SystemExit):
        C.main(["--archivar", TID, "--revisor", REVISOR])


def test_orquestador_con_guia_a_evaluada():
    assert "evaluada" in orq.TRANSICIONES["con_guia"]
    assert orq._DESCARTA_AL_VOLVER["evaluada"] == ("guia",)
    cargar_ejemplo("tarea")   # el contrato de tarea ya admite `evaluada` como estado


# --------------------------------------------------------------------------- rescate: --version-sin-cambios
def test_version_sin_cambios_rescata_una_archivada(rutas):
    tramo_a(rutas, [rub(OK_23)] * 3)
    redacciones, simulaciones = [], []
    ag = _agentes([], redacciones, simulaciones)
    ag.verificar = _verificar_con([[HALLAZGO_TAREA]])
    nuevo_ciclo(rutas, respuestas_simulador(6), agentes=ag).continuar([TID], revisor=REVISOR)
    exp = orq.cargar(TID, rutas.expedientes)
    orq.guardar(orq.transicionar(exp, "archivada", motivo="falso rechazo (test)"), rutas.expedientes)

    c = C.Ciclo(agentes=ag, rutas=rutas, salida=lambda s: None)
    reg = c.version_sin_cambios([TID], motivo="rescate de un falso rechazo")
    v2 = orq.cargar(f"{TID}-v2", rutas.expedientes)
    assert v2.estado == "evaluada" and v2.marcas["pendiente"] == "revision_humana_1" and c.contador.total == 0
    assert v2.artefactos["tarea"]["version"] == 2
    t1, t2 = exp.artefactos["tarea"], v2.artefactos["tarea"]
    assert {k: v for k, v in t2.items() if k not in ("id", "version", "estado", "rubrica_rub01")} == \
           {k: v for k, v in t1.items() if k not in ("id", "version", "estado", "rubrica_rub01")}
    assert v2.marcas["reusar_simulacion_de"] == TID and v2.marcas["evaluacion_heredada_de"] == TID
    assert v2.artefactos["evaluacion"]["rub01"] == exp.artefactos["evaluacion"]["rub01"]
    assert orq.cargar(TID, rutas.expedientes).estado == "archivada"   # la v1 no se toca
    assert reg["errores"] == []
    validar_artefactos(v2)

    # tramo B de la v2: reutiliza la simulación de la v1 (no simula) y verifica
    ag.verificar = _verificar_con([[]])
    nuevo_ciclo(rutas, [], agentes=ag).continuar([f"{TID}-v2"], revisor=REVISOR)
    v2 = orq.cargar(f"{TID}-v2", rutas.expedientes)
    assert v2.estado == "verificada" and len(simulaciones) == 1 and v2.marcas["simulacion_reutilizada_de"] == TID
