"""Tests del agente filtro: sin red, con ClienteFalso. Cada caso trae la respuesta simulada del modelo."""
import copy
import json
from pathlib import Path

import pytest

from pipeline import invariantes as inv
from pipeline.agentes.filtro import run as filtro
from pipeline.llm import ClienteFalso

CASOS_DIR = Path(__file__).resolve().parents[1] / "evals" / "casos" / "filtro"
CASOS = sorted(CASOS_DIR.glob("*.json"))


def cargar(p):
    return json.loads(p.read_text(encoding="utf-8"))


def test_hay_cinco_casos():
    assert len(CASOS) == 5


@pytest.mark.parametrize("ruta", CASOS, ids=[p.stem for p in CASOS])
def test_caso(ruta):
    c = cargar(ruta)
    # Entrada sintética válida y sin texto copiado (resumen <= 80 palabras lo exige el esquema).
    assert inv.validar_contra_esquema(c["noticia"], "noticia")
    cliente = ClienteFalso([c["respuesta_falsa"]])
    r = filtro.filtrar(c["noticia"], cliente=cliente)
    out = r["noticia"]
    assert inv.validar_contra_esquema(out, "noticia"), "salida inválida contra noticia"
    f = out["filtro"]
    esp = c["esperado"]
    assert f["pasa"] is esp["pasa"]
    assert esp["total_min"] <= f["total"] <= esp["total_max"]
    assert f["total"] == sum(f["puntajes"].values())
    assert f["version_rubrica"] == "4.0"
    # La noticia no se altera salvo el bloque filtro.
    assert {k: v for k, v in out.items() if k != "filtro"} == c["noticia"]
    # Una sola llamada, con el system cacheado.
    assert len(cliente.llamadas) == 1
    assert cliente.llamadas[0]["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "temperature" not in cliente.llamadas[0]
    assert r["meta"]["version_prompt"] == "1.0"


def test_total_y_decision_se_recalculan_en_codigo():
    c = cargar(CASOS_DIR / "04-frontera-6.json")
    resp = copy.deepcopy(c["respuesta_falsa"])
    # El modelo intenta imponer total y decisión: se ignoran.
    resp["total"] = 10
    resp["pasa"] = True
    r = filtro.filtrar(c["noticia"], cliente=ClienteFalso([resp]))
    assert r["noticia"]["filtro"]["total"] == 6
    assert r["noticia"]["filtro"]["pasa"] is False


@pytest.mark.parametrize("total,pasa", [(0, False), (6, False), (7, True), (10, True)])
def test_umbral(total, pasa):
    vals = [2, 2, 2, 2, 2]
    puntajes = dict(zip(filtro.CRITERIOS, [0] * 5))
    restante = total
    for i, k in enumerate(filtro.CRITERIOS):
        puntajes[k] = min(2, restante)
        restante -= puntajes[k]
    assert filtro.calcular(puntajes) == (total, pasa)


def test_config_coincide_con_rub01_y_gob01():
    filtro.verificar_config()
    assert filtro.UMBRAL == 7


def test_system_incluye_rub01_corta_y_criterios():
    s = filtro.construir_system()
    assert "{{" not in s
    for k in filtro.CRITERIOS:
        assert k in s
    assert "umbral_propuesto" in s


def test_esquema_de_salida_cierra_puntajes():
    e = filtro.esquema_salida()
    assert set(e["properties"]["criterios"]["required"]) == set(filtro.CRITERIOS)


def test_rechaza_entrada_invalida():
    c = cargar(CASOS[0])
    n = copy.deepcopy(c["noticia"])
    n["medio_id"] = "diario_inventado"
    with pytest.raises(ValueError):
        filtro.filtrar(n, cliente=ClienteFalso([]))


def test_ignora_filtro_previo_en_la_entrada():
    c = cargar(CASOS[0])
    n = copy.deepcopy(c["noticia"])
    n["filtro"] = {"version_rubrica": "4.0", "puntajes": dict.fromkeys(filtro.CRITERIOS, 2), "total": 10, "pasa": True}
    cliente = ClienteFalso([c["respuesta_falsa"]])
    filtro.filtrar(n, cliente=cliente)
    assert "filtro" not in json.loads(cliente.llamadas[0]["messages"][0]["content"])


def test_justificacion_se_recorta_a_80_palabras():
    c = cargar(CASOS[0])
    resp = copy.deepcopy(c["respuesta_falsa"])
    resp["justificacion_global"] = " ".join(f"palabra{i}" for i in range(200))
    r = filtro.filtrar(c["noticia"], cliente=ClienteFalso([resp]))
    assert len(r["noticia"]["filtro"]["justificacion"].split()) == 80


def test_justificacion_copiada_de_la_noticia_falla():
    c = cargar(CASOS[0])
    resp = copy.deepcopy(c["respuesta_falsa"])
    resp["justificacion_global"] = c["noticia"]["resumen_propio"]
    with pytest.raises(ValueError):
        filtro.filtrar(c["noticia"], cliente=ClienteFalso([resp]))
