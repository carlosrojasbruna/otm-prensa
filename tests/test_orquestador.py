"""Máquina de estados: camino feliz, transiciones ilegales e invariantes 1, 2, 3 y 5 en las transiciones."""
import copy
import itertools

import pytest

from pipeline import orquestador as orq
from pipeline.orquestador import (
    ArtefactoInvalido,
    InvarianteViolada,
    LimiteIteraciones,
    TransicionIlegal,
    UmbralRUB01NoCumplido,
    transicionar,
)

CAMINO = ["borrador", "evaluada", "revisada", "simulada", "con_guia", "verificada", "publicada"]
REVISOR = "Carlos Rojas Bruna"


def _evaluacion_con(ev, puntajes):
    ev = copy.deepcopy(ev)
    rub = ev["rub01"]
    for k, v in puntajes.items():
        rub["criterios"][k]["puntaje"] = v
    rub["total"] = sum(c["puntaje"] for c in rub["criterios"].values())
    rub["mejoras"] = [{"criterio": k, "mejora_minima": "m"} for k, c in rub["criterios"].items() if c["puntaje"] < 2]
    return ev


@pytest.fixture
def exp(ejemplos):
    return orq.nuevo_expediente(ejemplos["tarea"], ejemplos["noticia"])


def _hasta(exp, ejemplos, destino):
    """Avanza por el camino feliz hasta `destino`."""
    guia_pub = copy.deepcopy(ejemplos["guia"])
    guia_pub["trazabilidad"]["revision_humana_2"] = {"revisor": REVISOR, "fecha": "2026-10-26"}
    pasos = {
        "evaluada": dict(artefactos={"evaluacion": ejemplos["evaluacion"]}),
        "revisada": dict(revisor=REVISOR),
        "simulada": dict(artefactos={"trazas_resumen": ejemplos["trazas_resumen"]}),
        "con_guia": dict(artefactos={"guia": ejemplos["guia"]}),
        "verificada": dict(),
        "publicada": dict(artefactos={"guia": guia_pub}, revisor=REVISOR),
    }
    for estado in CAMINO[CAMINO.index(exp.estado) + 1 : CAMINO.index(destino) + 1]:
        exp = transicionar(exp, estado, **pasos[estado])
    return exp


# --------------------------------------------------------------------------- camino feliz
def test_camino_feliz_completo(exp, ejemplos):
    final = _hasta(exp, ejemplos, "publicada")
    assert final.estado == "publicada"
    assert final.artefactos["tarea"]["estado"] == "publicada"
    assert [h["a"] for h in final.historial] == CAMINO
    assert final.artefactos["tarea"]["rubrica_rub01"]["total"] == 23


def test_transicionar_no_modifica_la_entrada(exp, ejemplos):
    antes = copy.deepcopy(exp.a_dict())
    transicionar(exp, "evaluada", artefactos={"evaluacion": ejemplos["evaluacion"]})
    assert exp.a_dict() == antes


def test_persistencia_ida_y_vuelta(exp, ejemplos, tmp_path):
    e = _hasta(exp, ejemplos, "revisada")
    ruta = orq.guardar(e, tmp_path)
    assert orq.cargar(e.tarea_id, tmp_path).a_dict() == e.a_dict()


# --------------------------------------------------------------------------- transiciones ilegales
def test_borrador_a_publicada_es_ilegal(exp):
    with pytest.raises(TransicionIlegal):
        transicionar(exp, "publicada", revisor=REVISOR)


def test_estado_desconocido(exp):
    with pytest.raises(TransicionIlegal):
        transicionar(exp, "aprobada")


ILEGALES = [
    (o, d) for o, d in itertools.product(orq.ESTADOS, orq.ESTADOS) if d not in orq.TRANSICIONES[o]
]


@pytest.mark.parametrize("origen,destino", ILEGALES, ids=[f"{o}->{d}" for o, d in ILEGALES])
def test_toda_transicion_fuera_de_la_tabla_es_ilegal(exp, origen, destino):
    exp.estado = origen  # se fuerza el estado: la tabla se comprueba antes que los artefactos
    with pytest.raises(TransicionIlegal):
        transicionar(exp, destino, revisor=REVISOR, motivo="x")


def test_tabla_de_transiciones_esperada():
    assert orq.TRANSICIONES["borrador"] == {"evaluada", "archivada"}
    assert orq.TRANSICIONES["evaluada"] == {"revisada", "borrador", "archivada"}
    assert orq.TRANSICIONES["publicada"] == frozenset()
    assert orq.TRANSICIONES["archivada"] == frozenset()
    for a, b in zip(CAMINO, CAMINO[1:]):
        assert b in orq.TRANSICIONES[a]


def test_error_es_excepcion_propia(exp):
    with pytest.raises(orq.ErrorOrquestador):
        transicionar(exp, "publicada")


# --------------------------------------------------------------------------- invariante 1
def test_evaluada_con_evaluacion_invalida(exp, ejemplos):
    ev = copy.deepcopy(ejemplos["evaluacion"])
    del ev["reproducibilidad"]
    with pytest.raises(ArtefactoInvalido):
        transicionar(exp, "evaluada", artefactos={"evaluacion": ev})


def test_tarea_invalida_no_abre_expediente(ejemplos):
    t = ejemplos["tarea"]
    t["estudiante"]["task_space"] = t["task_space"]
    with pytest.raises(ArtefactoInvalido):
        orq.nuevo_expediente(t)


def test_toda_transicion_revalida_artefactos(exp, ejemplos):
    e = _hasta(exp, ejemplos, "revisada")
    e.artefactos["tarea"]["task_space"]["routes"] = e.artefactos["tarea"]["task_space"]["routes"][:1]
    with pytest.raises(ArtefactoInvalido):
        transicionar(e, "simulada", artefactos={"trazas_resumen": ejemplos["trazas_resumen"]})


def test_falta_artefacto(exp):
    with pytest.raises(InvarianteViolada):
        transicionar(exp, "evaluada")


def test_artefactos_de_otra_tarea(exp, ejemplos):
    ev = copy.deepcopy(ejemplos["evaluacion"])
    ev["tarea_id"] = "2026-10-otra-tarea"
    with pytest.raises(InvarianteViolada):
        transicionar(exp, "evaluada", artefactos={"evaluacion": ev})


# --------------------------------------------------------------------------- invariante 2
def test_revisada_con_19_falla(exp, ejemplos):
    ev = _evaluacion_con(ejemplos["evaluacion"], {"genuino": 1, "abierta": 1, "decisiones": 1, "realismo": 1})
    assert ev["rub01"]["total"] == 19
    e = transicionar(exp, "evaluada", artefactos={"evaluacion": ev})  # evaluar sí se puede
    with pytest.raises(UmbralRUB01NoCumplido):
        transicionar(e, "revisada", revisor=REVISOR)


def test_revisada_con_criterio_en_0_falla(exp, ejemplos):
    ev = _evaluacion_con(ejemplos["evaluacion"], {"validacion": 2, "fecundidad": 0})
    assert ev["rub01"]["total"] == 22
    e = transicionar(exp, "evaluada", artefactos={"evaluacion": ev})
    with pytest.raises(UmbralRUB01NoCumplido):
        transicionar(e, "revisada", revisor=REVISOR)


def test_revisada_con_20_y_sin_ceros_pasa(exp, ejemplos):
    ev = _evaluacion_con(ejemplos["evaluacion"], {"genuino": 1, "abierta": 1, "decisiones": 1})
    assert ev["rub01"]["total"] == 20
    e = transicionar(exp, "evaluada", artefactos={"evaluacion": ev})
    assert transicionar(e, "revisada", revisor=REVISOR).estado == "revisada"


def test_umbral_se_reaplica_despues_de_revisada(exp, ejemplos):
    e = _hasta(exp, ejemplos, "revisada")
    e.artefactos["evaluacion"] = _evaluacion_con(ejemplos["evaluacion"], {"recursos": 0})
    with pytest.raises(UmbralRUB01NoCumplido):
        transicionar(e, "simulada", artefactos={"trazas_resumen": ejemplos["trazas_resumen"]})


def test_revisada_requiere_revisor(exp, ejemplos):
    e = _hasta(exp, ejemplos, "evaluada")
    with pytest.raises(InvarianteViolada):
        transicionar(e, "revisada")


# --------------------------------------------------------------------------- iteraciones
def test_iteracion_disenador_evaluador_max_3(exp, ejemplos):
    ev_baja = _evaluacion_con(ejemplos["evaluacion"], {"recursos": 0})
    e = exp
    for i in range(1, 4):
        e = transicionar(e, "evaluada", artefactos={"evaluacion": ev_baja})
        assert e.iteraciones == i
        if i < 3:
            e = transicionar(e, "borrador")
            assert "evaluacion" not in e.artefactos  # la evaluación vieja no se reutiliza
    with pytest.raises(LimiteIteraciones):
        transicionar(e, "borrador")
    archivada = transicionar(e, "archivada", motivo="RUB01 bajo umbral tras 3 iteraciones")
    assert archivada.estado == "archivada"
    with pytest.raises(TransicionIlegal):
        transicionar(archivada, "borrador")


def test_archivar_requiere_motivo(exp):
    with pytest.raises(InvarianteViolada):
        transicionar(exp, "archivada")


# --------------------------------------------------------------------------- invariante 5 y retrocesos de guía
def test_con_guia_con_escenario_sin_traza_falla(exp, ejemplos):
    e = _hasta(exp, ejemplos, "simulada")
    guia = copy.deepcopy(ejemplos["guia"])
    guia["escenarios"][1]["corridas"] = ["N9_ZZ_r1"]
    with pytest.raises(InvarianteViolada):
        transicionar(e, "con_guia", artefactos={"guia": guia})


def test_rechazo_de_guia_vuelve_a_simulada(exp, ejemplos):
    e = _hasta(exp, ejemplos, "con_guia")
    v = transicionar(e, "simulada", motivo="verificador: cifra sin localizador")
    assert v.estado == "simulada" and "guia" not in v.artefactos


def test_publicada_requiere_revision_humana_2(exp, ejemplos):
    e = _hasta(exp, ejemplos, "verificada")
    with pytest.raises(InvarianteViolada):
        transicionar(e, "publicada", revisor=REVISOR)  # guía sin revision_humana_2


# --------------------------------------------------------------------------- invariante 3
def test_texto_literal_de_la_noticia_bloquea(exp, ejemplos):
    texto_noticia = " ".join(f"palabra{i}" for i in range(40))
    ev = ejemplos["evaluacion"]
    e = transicionar(exp, "evaluada", artefactos={"evaluacion": ev}, texto_noticia=texto_noticia)
    e.artefactos["tarea"]["estudiante"]["enunciado_es"] += " " + " ".join(f"palabra{i}" for i in range(5, 31))
    with pytest.raises(InvarianteViolada):
        transicionar(e, "revisada", revisor=REVISOR, texto_noticia=texto_noticia)
