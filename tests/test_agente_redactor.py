"""Tests del agente redactor, sin red: ClienteFalso reproduce las respuestas de cada caso."""
import copy
import json

import pytest

from pipeline.agentes.redactor import run as R
from pipeline.invariantes import cumple_limite_literal, escenarios_respaldados, validar_contra_esquema
from pipeline.llm import ClienteFalso, modelo_de

from conftest import RAIZ

CASOS = RAIZ / "evals" / "casos" / "redactor"
NOMBRES = sorted(p.name for p in CASOS.iterdir() if p.is_dir())


def _j(p):
    return json.loads(p.read_text(encoding="utf-8"))


def cargar(nombre):
    d = CASOS / nombre
    return (_j(d / "tarea.json"), _j(d / "trazas_resumen.json"), R.cargar_transcripciones(d / "transcripciones"),
            _j(d / "contexto.json"), _j(d / "respuestas_falsas.json"), _j(d / "criterio.json"))


def test_hay_cinco_casos():
    assert len(NOMBRES) == 5


@pytest.mark.parametrize("nombre", NOMBRES)
def test_caso(nombre):
    tarea, trazas, trans, ctx, resp, crit = cargar(nombre)
    cliente = ClienteFalso(resp)
    if crit["resultado"] == "ok":
        r = R.redactar(tarea, trazas, trans, ctx, cliente=cliente)
        g = r["guia"]
        assert validar_contra_esquema(g, "guia"), validar_contra_esquema(g, "guia").errores
        assert escenarios_respaldados(g, trazas)
        assert 3 <= len(g["escenarios"]) <= 4
        assert g["tabla_bloqueos"] == trazas["agregado"]["pct_bloqueo_por_transicion"]
        # modelos usados por sección (Sonnet para base e intervenciones, Opus para escenarios)
        modelos = {c["seccion"]: c["modelo"] for c in r["meta"]["llamadas"]}
        assert modelos == {"base": modelo_de("redactor"), "escenarios": modelo_de("redactor_escenarios"),
                           "intervenciones": modelo_de("redactor")}
        assert r["meta"]["costo_usd"] > 0 and r["meta"]["version_prompt"] == R.VERSION_PROMPT
        assert all("temperature" not in c for c in cliente.llamadas)
    else:
        with pytest.raises(getattr(R, crit["error"])) as e:
            R.redactar(tarea, trazas, trans, ctx, cliente=cliente)
        if "seccion" in crit:
            assert e.value.seccion == crit["seccion"]
        if "contiene" in crit:
            assert crit["contiene"] in str(e.value)
        assert len(cliente.llamadas) == crit.get("llamadas_esperadas", len(cliente.llamadas))


def test_caso3_no_llama_al_modelo():
    tarea, trazas, trans, ctx, resp, _ = cargar("caso3-error-trazas-insuficientes")
    c = ClienteFalso([])
    with pytest.raises(R.TrazasInsuficientes):
        R.redactar(tarea, trazas, trans, ctx, cliente=c)
    assert c.llamadas == []


def test_modelo_declara_insuficiente():
    tarea, trazas, trans, ctx, resp, _ = cargar("caso1-ok-embalse-3-escenarios")
    resp[1] = {"estado": "insuficiente", "motivo": "las corridas son casi idénticas", "escenarios": []}
    with pytest.raises(R.TrazasInsuficientes):
        R.redactar(tarea, trazas, trans, ctx, cliente=ClienteFalso(resp[:2]))


def test_dialogo_inventado_se_rechaza():
    tarea, trazas, trans, ctx, resp, _ = cargar("caso1-ok-embalse-3-escenarios")
    resp[1]["escenarios"][0]["extracto_dialogo"][0]["texto"] = "Esto nunca lo dijo nadie en la corrida."
    with pytest.raises(R.RedaccionRechazada) as e:
        R.redactar(tarea, trazas, trans, ctx, cliente=ClienteFalso([resp[0], resp[1], resp[1]]))
    assert "no está en las transcripciones" in str(e.value)


def test_bloqueo_inventado_se_rechaza():
    tarea, trazas, trans, ctx, resp, _ = cargar("caso1-ok-embalse-3-escenarios")
    resp[1]["escenarios"][0]["bloqueos"] = [{"transicion": "B34", "como_se_destrabo": "inventado"}]
    with pytest.raises(R.RedaccionRechazada) as e:
        R.redactar(tarea, trazas, trans, ctx, cliente=ClienteFalso([resp[0], resp[1], resp[1]]))
    assert "bloqueos" in str(e.value)


def test_reparacion_una_vez_y_acepta():
    tarea, trazas, trans, ctx, resp, _ = cargar("caso1-ok-embalse-3-escenarios")
    mala = copy.deepcopy(resp[1])
    mala["escenarios"][2]["corridas"] = ["N9_ZZ_r1"]
    c = ClienteFalso([resp[0], mala, resp[1], resp[2]])
    r = R.redactar(tarea, trazas, trans, ctx, cliente=c)
    assert len(c.llamadas) == 4
    assert "Corrección requerida" in c.llamadas[2]["messages"][0]["content"]
    assert escenarios_respaldados(r["guia"], trazas)


def test_sin_revision_humana_1_falla():
    tarea, trazas, trans, ctx, resp, _ = cargar("caso1-ok-embalse-3-escenarios")
    ctx.pop("revision_humana_1")
    with pytest.raises(R.EntradaInvalida):
        R.redactar(tarea, trazas, trans, ctx, cliente=ClienteFalso(resp))


def test_literal_noticia():
    tarea, trazas, trans, ctx, resp, _ = cargar("caso1-ok-embalse-3-escenarios")
    noticia = "El embalse baja de su nivel habitual y las autoridades aseguran que este verano no habrá riesgo para nadie"
    resp[0]["meta"]["que_observar"] = ("El embalse baja de su nivel habitual y las autoridades aseguran que este verano "
                                       "no habrá riesgo para nadie " + "y además " * 0)
    # ya son 18 palabras: pasa; se alarga la noticia para superar 25 palabras
    larga = noticia + " según informó el medio durante la semana pasada en una conferencia con detalles sobre el consumo"
    resp[0]["meta"]["que_observar"] = larga
    with pytest.raises(R.RedaccionRechazada) as e:
        R.redactar(tarea, trazas, trans, ctx, cliente=ClienteFalso(resp), texto_noticia=larga)
    assert "palabras consecutivas" in str(e.value)


def test_cifras_utilidades():
    tarea, trazas, trans, *_ = cargar("caso1-ok-embalse-3-escenarios")
    p = R.numeros_permitidos(tarea, trazas, trans)
    assert R.cifras_sin_localizador("Con 220 y 38 % en B12 y P4, 33 % de los grupos, 50 min", p) == []
    assert R.cifras_sin_localizador("Dura 41 meses", p)


def test_esquemas_de_salida_basicos():
    for esq in (R.esquema_base(), R.esquema_escenarios(), R.esquema_intervenciones()):
        assert esq["additionalProperties"] is False
        assert "$ref" not in json.dumps(esq) and "minItems" not in json.dumps(esq)


def test_prompt_tiene_las_secciones():
    p = R.cargar_prompt()
    assert set(p) == {"comun", "base", "escenarios", "intervenciones"}
    assert "solo" in p["escenarios"] and "id de corrida" in p["escenarios"].lower() or "corridas" in p["escenarios"]


def test_normalizar_bloqueos_deja_solo_el_codigo():
    """Caso queso-v2: sin bloqueos observados, el modelo anotó el código con una nota y la guía no validaba."""
    from pipeline.agentes.redactor.run import normalizar_bloqueos

    s = {"intervenciones": [{"bloqueo": "B12 (probable según el mapa del ciclo; la tabla viene vacía)"},
                            {"bloqueo": "B67"}]}
    assert normalizar_bloqueos(s) == []
    assert [i["bloqueo"] for i in s["intervenciones"]] == ["B12", "B67"]

    malo = {"intervenciones": [{"bloqueo": "B12 o B23"}, {"bloqueo": "simplificar"}]}
    assert len(normalizar_bloqueos(malo)) == 2


def test_observaciones_de_revision_llegan_a_cada_seccion(monkeypatch):
    """Guía v2 por revisión humana 2: las observaciones van en el mensaje de cada sección."""
    import pytest as _pt
    from pipeline.agentes.redactor import run as red

    vistos = []

    def generar(seccion, user, schema, verificar, cuenta, cliente=None):
        vistos.append((seccion, user))
        raise RuntimeError("alto")  # basta con el primer mensaje

    monkeypatch.setattr(red, "_generar", generar)
    monkeypatch.setattr(red, "validar_entradas", lambda *a, **k: None)
    monkeypatch.setattr(red, "numeros_permitidos", lambda *a, **k: set())
    with _pt.raises(RuntimeError):
        red.redactar({"task_space": {}, "rubrica_rub01": {"total": 23}}, {}, {},
                     {"observaciones_revision": ["Corregir E1"], "revision_humana_1": {"r": 1}, "puntaje_rub01": 23})
    assert "Corregir E1" in vistos[0][1] and "revisión humana" in vistos[0][1]
