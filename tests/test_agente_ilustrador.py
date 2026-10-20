"""Tests del agente ilustrador: sin red, con ClienteFalso."""
import copy
import json
from pathlib import Path

import pytest

from pipeline.agentes.ilustrador import run as ilu
from pipeline.invariantes import validar_contra_esquema, verificar_aislamiento
from pipeline.llm import ClienteFalso

RAIZ = Path(__file__).resolve().parents[1]
CASOS = sorted((RAIZ / "evals" / "casos" / "ilustrador").glob("*.json"))


def _tarea(caso):
    t = json.loads((RAIZ / caso["entrada"]["tarea_base"]).read_text(encoding="utf-8"))
    for k, v in caso["entrada"]["reemplazos"].items():
        d = t
        *ruta, ultima = k.split(".")
        for p in ruta:
            d = d[p]
        d[ultima] = v
    return t


def test_hay_cinco_casos():
    assert len(CASOS) == 5


@pytest.mark.parametrize("ruta", CASOS, ids=lambda p: p.stem)
def test_caso(ruta):
    caso = json.loads(ruta.read_text(encoding="utf-8"))
    crit = caso["criterio_aceptacion"]
    tarea = _tarea(caso)
    assert validar_contra_esquema(tarea, "tarea")  # la entrada cumple el contrato
    cliente = ClienteFalso(caso["respuestas_modelo"])
    if crit["resultado"] == "acepta":
        s = ilu.ilustrar(tarea, cliente=cliente)
        assert ilu.validar_salida(s) == []
        assert s["meta"]["intentos_reparacion"] == crit["intentos_reparacion"]
        assert set(s["paleta_usada"]) <= ilu.PALETA
    else:
        with pytest.raises(ValueError) as e:
            ilu.ilustrar(tarea, cliente=cliente)
        # los errores que reporta el validador sobre la respuesta mala
        errs = ilu.validar_svg(caso["respuestas_modelo"][0]["svg"])
        assert errs
        for frag in crit["errores_contienen"]:
            assert any(frag in x for x in errs), (frag, errs)


def test_el_modelo_no_ve_task_space_ni_noticia():
    caso = json.loads(CASOS[0].read_text(encoding="utf-8"))
    tarea = _tarea(caso)
    cliente = ClienteFalso(caso["respuestas_modelo"])
    ilu.ilustrar(tarea, cliente=cliente)
    user = cliente.llamadas[0]["messages"][0]["content"]
    payload = json.loads(user)
    assert set(payload) == {"titulo", "area", "enunciado_es", "foto_descripcion"}
    assert "reference_solution" not in user and "task_space" not in user
    assert tarea["noticia"]["url"] not in user
    assert "temperature" not in cliente.llamadas[0]


@pytest.mark.parametrize("svg,frag", [
    ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><a href="https://x.y"><rect x="0" y="0" width="1" height="1"/></a></svg>', "<a>"),
    ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect x="0" y="0" width="1" height="1" style="fill:red"/></svg>', "style"),
    ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect x="0" y="0" width="1" height="1" fill="#abcdef"/></svg>', "paleta"),
    ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect x="0" y="0" width="1" height="1"/></svg>', "viewBox"),
    ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect x="0" y="0" width="1"', "XML inválido"),
    ('<!DOCTYPE svg [<!ENTITY a "b">]><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"/>', "DOCTYPE"),
    ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><text x="1" y="1">hola</text></svg>', "<text>"),
    ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect x="0" y="0" width="1" height="1" fill="#ffffff" onload="x()"/></svg>', "onload"),
    ('<svg viewBox="0 0 400 300"><rect x="0" y="0" width="1" height="1"/></svg>', "raíz"),
])
def test_validador_rechaza(svg, frag):
    assert any(frag in e for e in ilu.validar_svg(svg))


def test_validador_rechaza_tamano():
    grande = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300">' + '<rect x="0" y="0" width="1" height="1"/>' * 400 + "</svg>"
    errs = ilu.validar_svg(grande)
    assert any("bytes" in e for e in errs) and any("elementos" in e for e in errs)


def test_salida_con_digitos_en_foto_se_rechaza():
    caso = json.loads(CASOS[0].read_text(encoding="utf-8"))
    r = copy.deepcopy(caso["respuestas_modelo"][0])
    r["foto_descripcion"] = "Embalse al 38 por ciento de su capacidad."
    with pytest.raises(ValueError):
        ilu.ilustrar(_tarea(caso), cliente=ClienteFalso([r, r]))
