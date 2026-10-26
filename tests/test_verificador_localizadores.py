"""Verificador y localizadores de cifras: caso real 2026-10-cuanto-pagar-cada-mes (ciclo 2026-10-26).

La tarea se archivó tras dos rechazos «valor 48 en la tarea, '5 millones' en la noticia (párrafo 5)». Causas:
(1) tres cifras de la noticia comparten «párrafo 5» y el verificador guardaba solo la última; (2) el explorador
numera los párrafos del feed de La Tercera y el ciclo relee la página completa (≈146 párrafos de menú antes del
cuerpo). Se usan los artefactos reales del expediente y un texto SINTÉTICO con la misma estructura de cifras (el
texto de la noticia no se guarda en el repo, invariante 3). Sin red ni API."""
import copy

import pytest

from pipeline import orquestador as orq
from pipeline.agentes.verificador import run as V
from pipeline.llm import ClienteFalso

TID = "2026-10-cuanto-pagar-cada-mes"
MENU = 146   # párrafos de navegación antes del cuerpo en la página real


def _cuerpo(p48=5):
    """Cuerpo sintético con las cifras de la noticia en los párrafos que dice el explorador."""
    ps = {1: "Texto de apertura sobre la ley.", 2: "Contexto general sin cifras relevantes.",
          3: "La plataforma registró 4.000 consultas y 2.000 convenios en sus primeros días.",
          4: "Declaraciones de la autoridad sobre el proceso.",
          5: "Hay cerca de 578.000 deudores; la barrera de 5 millones de pesos se eliminó.",
          6: "El trámite se hace en línea.", 7: "Antes el máximo era de 24 cuotas.",
          8: "Más declaraciones.", 9: "Detalle del procedimiento.", 10: "Por ejemplo, con un pie de 10% de la deuda.",
          11: "Se estiman 200 mil millones de pesos en un año."}
    ps[p48] += " El nuevo convenio permite pagar en 48 cuotas."
    return ps


def _pagina(cuerpo):
    menu = "".join(f"<li><a href='/seccion-{i}/'>Sección {i} del menú</a></li>" for i in range(1, MENU + 1))
    return menu + "".join(f"<p>{cuerpo[i]}</p>" for i in sorted(cuerpo))


@pytest.fixture
def exp():
    return orq.cargar(TID)


def test_alinea_la_numeracion_del_explorador(exp):
    ps, k = V.parrafos_alineados(_pagina(_cuerpo()), exp.artefactos["noticia"]["cifras"])
    assert k == MENU and "48 cuotas" in ps[5 - 1]


def test_el_48_del_parrafo_5_coincide(exp):
    a = exp.artefactos
    inf = V.verificar_tarea(a["tarea"], a["noticia"], _pagina(_cuerpo()))
    assert inf["aprobado"], inf["hallazgos"]
    assert inf["cifras_contrastadas"][0]["resultado"] == "coincide" and inf["localizadores_corregidos"] == {}


def test_sin_texto_tampoco_confunde_cifras_del_mismo_parrafo(exp):
    """El fallo exacto del ciclo: sin desambiguar, 48 se comparaba con «5 millones» (la última del párrafo 5)."""
    a = exp.artefactos
    inf = V.verificar_tarea(a["tarea"], a["noticia"], None)
    assert inf["aprobado"], inf["hallazgos"]


def test_corrido_un_parrafo_es_advertencia_con_localizador_corregido(exp):
    a = exp.artefactos
    inf = V.verificar_tarea(a["tarea"], a["noticia"], _pagina(_cuerpo(p48=6)))
    assert inf["aprobado"]
    assert inf["localizadores_corregidos"] == {"0": {"fuente": "noticia", "ubicacion": "párrafo 6"}}
    adv = [h for h in inf["hallazgos"] if h["severidad"] == "advertencia" and h["invariante"] == "4"]
    assert len(adv) == 1 and "párrafo 6" in adv[0]["descripcion"]
    t, n = V.aplicar_localizadores(a["tarea"], V.localizadores_corregidos(inf), a["noticia"])
    assert t["noticia"]["cifras_usadas"][0]["localizador"]["ubicacion"] == "párrafo 6"
    assert [c["localizador"]["ubicacion"] for c in n["cifras"] if c["valor"] == 48] == ["párrafo 6"]
    assert a["tarea"]["noticia"]["cifras_usadas"][0]["localizador"]["ubicacion"] == "párrafo 5"   # no muta


def test_lejos_del_localizador_es_critico_sobre_la_tarea(exp):
    a = exp.artefactos
    inf = V.verificar_tarea(a["tarea"], a["noticia"], _pagina(_cuerpo(p48=9)))
    assert not inf["aprobado"]
    assert V.hallazgos_sobre_tarea(inf["hallazgos"])[0]["ubicacion"] == "tarea.noticia.cifras_usadas[0]"


def test_verificacion_completa_con_la_guia_real_aprueba(exp):
    """La guía v1 que se rechazó dos veces: con el texto alineado y el modelo sin objeciones, aprueba."""
    a = exp.artefactos
    modelo = ClienteFalso([{"cifras": [], "recursos": [], "afirmaciones_no_respaldadas": []}])
    inf = V.verificar(a["tarea"], a["guia"], a["trazas_resumen"], a["noticia"], texto_noticia=_pagina(_cuerpo()),
                      cliente=modelo)
    assert inf["aprobado"], [h for h in inf["hallazgos"] if h["severidad"] == "critico"]
    assert inf["estado_destino"] == "verificada"


def test_hallazgo_sobre_la_tarea_devuelve_a_evaluada(exp):
    a = copy.deepcopy(exp.artefactos)
    a["tarea"]["noticia"]["cifras_usadas"][0]["valor"] = 36
    inf = V.verificar(a["tarea"], a["guia"], a["trazas_resumen"], a["noticia"], texto_noticia=_pagina(_cuerpo()),
                      cliente=ClienteFalso([]))
    assert not inf["aprobado"] and inf["estado_destino"] == "evaluada"


def test_numeros_raros_no_rompen_la_lectura():
    assert V.numeros_en("versión 0.5.8 y 48 cuotas") == [48.0]
