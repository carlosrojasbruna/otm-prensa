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
OK_MODELO = {"cifras": [], "afirmaciones_no_respaldadas": [], "recursos": []}


def _ej():
    ej = {k: json.loads((DIR_EJ / f"{k}_ejemplo.json").read_text(encoding="utf-8"))
          for k in ("tarea", "guia", "trazas_resumen", "noticia")}
    # v1.1: el ejemplo del contrato cita "otra fuente: informe de la empresa sanitaria (ejemplo)", que no es una
    # fuente concreta (el verificador la rechaza como genérica). Los contratos no se editan: se concretiza aquí.
    for r in ej["tarea"]["estudiante"]["recursos_a_solicitud"]:
        if r["fuente"].startswith("otra fuente"):
            r["fuente"] = "otra fuente: Superintendencia de Servicios Sanitarios, informe de consumo 2025"
    return ej


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
                 "recursos": [],
                 "afirmaciones_no_respaldadas": [{"ubicacion": "guia.escenarios.E1", "afirmacion": "x",
                                                  "motivo": "sin respaldo", "severidad": "advertencia"}]}
    informe = V.verificar(ej["tarea"], ej["guia"], ej["trazas_resumen"], ej["noticia"], cliente=ClienteFalso([respuesta]))
    assert not informe["aprobado"] and informe["estado_destino"] == "evaluada"   # el hallazgo es sobre la tarea
    assert {h["origen"] for h in informe["hallazgos"]
            if h["invariante"] == "semantica" and h["severidad"] == "critico"} == {"modelo"}
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


def test_contraste_semantico_recibe_titulo_de_la_noticia(monkeypatch):
    """Una afirmación que solo está en el titular no debe quedar sin fuente (caso anticipo-renta-vitalicia)."""
    import json as _json
    from pipeline.agentes.verificador import run as ver

    capturado = {}

    def falso_llamar(**kw):
        capturado["user"] = _json.loads(kw["user"])
        return {"salida": {"cifras": [], "afirmaciones_no_respaldadas": []}, "meta": {"costo_usd": 0.0}}

    monkeypatch.setattr(ver, "llamar", falso_llamar)
    tarea = {"noticia": {"medio": "CIPER Chile", "titulo": "Suprema da la razón a aseguradoras", "fecha": "2026-10-19",
                         "resumen_propio": "Resumen sin el sentido del fallo.", "cifras_usadas": []}}

    class Inf:
        def add(self, *a, **k):
            pass

    try:
        ver._contraste_semantico(Inf(), tarea, {}, {}, None, {"estado": "no_encontrado", "stdout": ""}, [], None)
    except (KeyError, TypeError):
        pass  # el resto del procesamiento no importa aquí; solo lo enviado al modelo
    noticia = capturado["user"]["fuentes"]["noticia"]
    assert noticia["titulo"] == "Suprema da la razón a aseguradoras"
    assert noticia["medio"] == "CIPER Chile" and noticia["fecha"] == "2026-10-19"


# --------------------------------------------------------------------------- recursos (prompt v1.1)
TEXTO = "\n".join(
    ["<p>Primer párrafo de relleno sobre la sequía en la región, sin cifras relevantes aquí.</p>",
     "<p>El embalse tiene una capacidad de 220 millones de metros cúbicos y hoy está al 38 %.</p>",
     "<p>Párrafo secreto que no debe viajar al modelo: contiene otra frase de la noticia sobre alcaldes.</p>"])


def _recurso(rid, fuente, contenido="Dato de apoyo para el estudiante."):
    return {"id": rid, "que_es": "dato", "contenido": contenido, "disponibilidad": "a_solicitud",
            "fase": "P2-RM", "fuente": fuente}


def _con_recursos(*recursos):
    ej = _ej()
    ej["tarea"]["estudiante"]["recursos_a_solicitud"] = list(recursos)
    return ej


def _verificar(ej, respuesta=OK_MODELO, texto=None):
    cliente = ClienteFalso([respuesta])
    informe = V.verificar(ej["tarea"], ej["guia"], ej["trazas_resumen"], ej["noticia"], texto, None, cliente)
    assert not list(Draft202012Validator(ESQUEMA).iter_errors(informe))
    return informe, cliente


def _enviado(cliente):
    return cliente.llamadas[0]["messages"][0]["content"]


def _sem(informe, sev):
    return [h for h in informe["hallazgos"] if h["invariante"] == "semantica" and h["severidad"] == sev]


@pytest.mark.parametrize("fuente,clase", [
    ("noticia, párrafo 2", "noticia"), ("noticia (párrafo 2, gráfico 1)", "noticia"),
    ("La noticia, titular", "noticia"), ("noticia", "generica"), ("noticia, en general", "generica"),
    ("otra fuente: Banco Central de Chile, Indicadores 2025", "otra_fuente"), ("otra fuente: INE", "otra_fuente"),
    ("otra fuente: datos oficiales", "generica"), ("otra fuente: conocimiento general", "generica"),
    ("otra fuente", "generica"), ("otra fuente: informe de la empresa sanitaria (ejemplo)", "generica"),
    ("conocimiento general", "generica"), ("estimación propia", "generica"), ("", "generica"),
    ("supuesto del escenario", "supuesto"), ("Supuesto del Escenario", "supuesto"),
])
def test_clasificar_fuente(fuente, clase):
    assert V.clasificar_fuente(fuente)["clase"] == clase


def test_clasificar_fuente_parrafos_y_marca_en_contenido():
    assert V.clasificar_fuente("noticia, párrafos 2-4")["parrafos"] == [2, 3, 4]
    assert V.clasificar_fuente("noticia, párrafos 2 y 5")["parrafos"] == [2, 5]
    c = V.clasificar_fuente("estimación propia", "Supuesto del escenario: consumo de 150 l/día.")
    assert c["clase"] == "supuesto" and c["marca_completa"] is False


def test_fuente_generica_es_critico_y_no_llama_al_modelo():
    ej = _con_recursos(_recurso("R1", "conocimiento general"))
    cliente = ClienteFalso([])
    informe = V.verificar(ej["tarea"], ej["guia"], ej["trazas_resumen"], ej["noticia"], cliente=cliente)
    assert not informe["aprobado"] and informe["estado_destino"] == "evaluada"   # recurso de la tarea
    crit = _sem(informe, "critico")
    assert len(crit) == 1 and "R1" in crit[0]["ubicacion"] and crit[0]["origen"] == "codigo"
    assert cliente.llamadas == []


def test_recurso_de_entrada_con_fuente_generica_tambien_es_critico():
    ej = _con_recursos(_recurso("R1", "noticia, párrafo 2"))
    ej["tarea"]["recursos_de_entrada"] = [dict(_recurso("R9", "otra fuente: datos oficiales"),
                                               disponibilidad="de_entrada")]
    informe = V.verificar(ej["tarea"], ej["guia"], ej["trazas_resumen"], ej["noticia"], cliente=ClienteFalso([]))
    assert [h["ubicacion"] for h in _sem(informe, "critico")] == ["tarea.recursos_de_entrada[R9]"]


def test_supuesto_marcado_no_genera_hallazgo():
    ej = _con_recursos(_recurso("R1", "supuesto del escenario", "Supuesto del escenario: el consumo por persona es constante."))
    informe, cliente = _verificar(ej)
    assert not [h for h in informe["hallazgos"] if "R1" in h["ubicacion"]]
    assert informe["aprobado"] is True
    # y el recurso supuesto no se envía al modelo para juzgarlo
    assert json.loads(_enviado(cliente))["recursos_a_contrastar"] == []


def test_supuesto_marcado_en_un_solo_lugar_es_advertencia():
    ej = _con_recursos(_recurso("R1", "supuesto del escenario", "El consumo por persona es constante."))
    informe, _ = _verificar(ej)
    assert informe["aprobado"] is True and len(_sem(informe, "advertencia")) == 1


def test_noticia_con_parrafo_envia_solo_ese_parrafo_al_modelo():
    ej = _con_recursos(_recurso("R1", "noticia, párrafo 2", "El embalse está casi lleno."))
    informe, cliente = _verificar(ej, texto=TEXTO)
    bruto = _enviado(cliente)
    payload = json.loads(bruto)
    citados = payload["fuentes"]["noticia"]["parrafos_citados"]
    assert list(citados) == ["2"] and "capacidad de 220 millones" in citados["2"]
    assert "Párrafo secreto" not in bruto and "Primer párrafo de relleno" not in bruto
    assert TEXTO not in bruto
    rec = payload["recursos_a_contrastar"][0]
    assert rec["id"] == "R1" and rec["clase"] == "noticia" and rec["parrafos"] == [2]
    assert informe["meta"]["texto_noticia_recibido"] is True
    assert not [h for h in _sem(informe, "advertencia") if "no se pudo contrastar" in h["descripcion"]]


def test_noticia_sin_texto_advierte_que_no_se_pudo_contrastar():
    ej = _con_recursos(_recurso("R1", "noticia, párrafo 2"))
    informe, cliente = _verificar(ej, texto=None)
    adv = [h for h in _sem(informe, "advertencia") if "no se pudo contrastar con el texto" in h["descripcion"]]
    assert len(adv) == 1 and "R1" in adv[0]["ubicacion"]
    assert "parrafos_citados" not in json.loads(_enviado(cliente))["fuentes"]["noticia"]
    assert informe["aprobado"] is True


def test_recurso_contradicho_es_critico_y_no_respaldado_es_advertencia():
    ej = _con_recursos(_recurso("R1", "noticia, párrafo 2"), _recurso("R3", "noticia, párrafo 1"))
    resp = dict(OK_MODELO, recursos=[{"id": "R1", "juicio": "contradicho", "nota": "el párrafo dice 38 %, no 83 %"},
                                     {"id": "R3", "juicio": "no_respaldado", "nota": "el párrafo no menciona el dato"}])
    informe, _ = _verificar(ej, resp, TEXTO)
    assert not informe["aprobado"]
    assert [h["ubicacion"] for h in _sem(informe, "critico")] == ["tarea.estudiante.recursos_a_solicitud[R1]"]
    adv = _sem(informe, "advertencia")
    assert any("R3" in h["ubicacion"] and "no respaldada por los párrafos citados" in h["descripcion"] for h in adv)


def test_otra_fuente_concreta_solo_advierte_si_el_modelo_la_ve_inverosimil():
    ej = _con_recursos(_recurso("R1", "otra fuente: Superintendencia de Servicios Sanitarios, informe 2025"))
    informe, _ = _verificar(ej, dict(OK_MODELO, recursos=[{"id": "R1", "juicio": "plausible", "nota": "existe"}]))
    assert informe["aprobado"] and not [h for h in _sem(informe, "advertencia") if "R1" in h["ubicacion"]]
    informe, _ = _verificar(ej, dict(OK_MODELO, recursos=[{"id": "R1", "juicio": "no_plausible", "nota": "inventada"}]))
    assert informe["aprobado"] and len([h for h in _sem(informe, "advertencia") if "R1" in h["ubicacion"]]) == 1


def test_hallazgos_del_modelo_no_reproducen_mas_de_25_palabras_de_la_noticia():
    parrafo = ("El embalse tiene una capacidad de 220 millones de metros cúbicos y hoy está al 38 % según el "
               "informe técnico entregado por la dirección regional de aguas durante la mañana de ayer en la capital")
    texto = f"<p>{parrafo}</p>"
    ej = _con_recursos(_recurso("R1", "noticia, párrafo 1"))
    resp = dict(OK_MODELO, recursos=[{"id": "R1", "juicio": "contradicho", "nota": parrafo}])
    informe, _ = _verificar(ej, resp, texto)
    from pipeline import invariantes as inv
    assert inv.cumple_limite_literal(informe, texto)
