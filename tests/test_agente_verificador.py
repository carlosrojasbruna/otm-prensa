"""Tests del verificador sin red: ClienteFalso, ejemplos de contratos y los 5 casos de evals."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from pipeline.llm import ClienteFalso

RAIZ = Path(__file__).resolve().parents[1]
DIR_AGENTE = RAIZ / "pipeline" / "agentes" / "verificador"
DIR_CASOS = RAIZ / "evals" / "casos" / "verificador"
DIR_EJ = RAIZ / "contratos" / "ejemplos"

_spec = importlib.util.spec_from_file_location("verificador_run", DIR_AGENTE / "run.py")
V = importlib.util.module_from_spec(_spec)
sys.modules["verificador_run"] = V
_spec.loader.exec_module(V)

ESQUEMA = json.loads((DIR_AGENTE / "salida.schema.json").read_text(encoding="utf-8"))
OK_MODELO = {"cifras": [], "afirmaciones_no_respaldadas": []}


def _ej():
    return {k: json.loads((DIR_EJ / f"{k}_ejemplo.json").read_text(encoding="utf-8"))
            for k in ("tarea", "guia", "trazas_resumen", "noticia")}


def _correr(caso):
    ej = _ej()
    base = {"tarea": ej["tarea"], "guia": ej["guia"], "trazas": ej["trazas_resumen"], "noticia": ej["noticia"]}
    base = V.aplicar_mutaciones(base, caso["mutaciones"])
    nb = DIR_CASOS / caso["notebook"] if caso["notebook"] else None
    cliente = ClienteFalso([caso["respuesta_modelo"]])
    informe = V.verificar(base["tarea"], base["guia"], base["trazas"],
                          base["noticia"] if caso["con_noticia"] else None,
                          caso["texto_noticia"], nb, cliente)
    return informe, cliente


def test_esquema_de_salida_es_valido():
    Draft202012Validator.check_schema(ESQUEMA)


@pytest.mark.parametrize("ruta", sorted(DIR_CASOS.glob("caso*.json")), ids=lambda p: p.stem)
def test_casos(ruta):
    caso = json.loads(ruta.read_text(encoding="utf-8"))
    informe, cliente = _correr(caso)
    assert not list(Draft202012Validator(ESQUEMA).iter_errors(informe))
    esp = caso["esperado"]
    assert informe["aprobado"] is esp["aprobado"]
    assert informe["estado_destino"] == esp["estado_destino"]
    assert informe["meta"]["modelo_llamado"] is esp["modelo_llamado"]
    assert len(cliente.llamadas) == (1 if esp["modelo_llamado"] else 0)
    criticas = {h["invariante"] for h in informe["hallazgos"] if h["severidad"] == "critico"}
    assert criticas == set(esp["invariantes_criticas"])


def test_caso1_ejecuta_notebook_y_contrasta_cifra():
    caso = json.loads((DIR_CASOS / "caso1_aprobado_limpio.json").read_text(encoding="utf-8"))
    informe, cliente = _correr(caso)
    assert informe["notebook"]["estado"] == "ejecutado"
    assert "83.6" in informe["notebook"]["salida_resumen"]
    assert [c["resultado"] for c in informe["cifras_contrastadas"]] == ["coincide"] * 3
    # el modelo no recibe texto_noticia ni task_space de estudiantes aparte de la tarea completa
    assert "temperature" not in cliente.llamadas[0]


def test_caso5_no_guarda_ni_cita_texto_noticia():
    caso = json.loads((DIR_CASOS / "caso5_mas_de_25_palabras_literales.json").read_text(encoding="utf-8"))
    informe, _ = _correr(caso)
    assert informe["meta"]["texto_noticia_recibido"] is True
    h = [h for h in informe["hallazgos"] if h["invariante"] == "3"]
    assert h and "33 palabras" in h[0]["descripcion"] or "palabras consecutivas" in h[0]["descripcion"]


def test_ejemplos_del_contrato_sin_notebook_aprueba_con_advertencia():
    ej = _ej()
    cliente = ClienteFalso([OK_MODELO])
    informe = V.verificar(ej["tarea"], ej["guia"], ej["trazas_resumen"], ej["noticia"], cliente=cliente)
    assert informe["aprobado"] is True
    assert informe["notebook"]["estado"] == "no_encontrado"
    assert any(h["invariante"] == "notebook" and h["severidad"] == "advertencia" for h in informe["hallazgos"])


def test_cifra_con_fuente_notebook_sin_notebook_rechaza():
    ej = _ej()
    ej["tarea"]["noticia"]["cifras_usadas"][0]["localizador"] = {"fuente": "notebook", "ubicacion": "celda 1"}
    informe = V.verificar(ej["tarea"], ej["guia"], ej["trazas_resumen"], ej["noticia"], cliente=ClienteFalso([]))
    assert not informe["aprobado"]
    assert any(h["invariante"] == "4" for h in informe["hallazgos"])


def test_modelo_puede_rechazar_pero_no_aprobar_contra_el_codigo():
    ej = _ej()
    respuesta = {"cifras": [{"indice": 0, "coincide": False, "valor_en_fuente": "20", "nota": "no es la capacidad"}],
                 "afirmaciones_no_respaldadas": [{"ubicacion": "guia.escenarios.E1", "afirmacion": "x",
                                                  "motivo": "sin respaldo", "severidad": "advertencia"}]}
    informe = V.verificar(ej["tarea"], ej["guia"], ej["trazas_resumen"], ej["noticia"], cliente=ClienteFalso([respuesta]))
    assert not informe["aprobado"] and informe["estado_destino"] == "simulada"
    assert {h["origen"] for h in informe["hallazgos"] if h["invariante"] == "semantica"} == {"modelo"}
    assert not list(Draft202012Validator(ESQUEMA).iter_errors(informe))


def test_notebook_con_red_o_error_no_cuelga(tmp_path):
    nb = {"cells": [{"cell_type": "code", "source": ["import socket\n", "socket.create_connection(('example.com', 80))\n"]}]}
    ruta = tmp_path / "nb.ipynb"
    ruta.write_text(json.dumps(nb), encoding="utf-8")
    r = V.ejecutar_notebook(ruta, 20)
    assert r["estado"] == "error" and "red bloqueada" in r["salida_resumen"]


def test_notebook_tiempo_limite(tmp_path):
    nb = {"cells": [{"cell_type": "code", "source": ["while True:\n", "    pass\n"]}]}
    ruta = tmp_path / "nb.ipynb"
    ruta.write_text(json.dumps(nb), encoding="utf-8")
    assert V.ejecutar_notebook(ruta, 2)["estado"] == "tiempo_agotado"


def test_parsear_numero():
    assert V.parsear_numero("38 %") == 38 and V.parsear_numero("1.234,5") == 1234.5
    assert V.parsear_numero(220) == 220 and V.parsear_numero("sin cifra") is None
