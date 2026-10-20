"""Tests del agente diseñador. Sin red: se usa ClienteFalso con las respuestas simuladas de cada caso."""
import copy
import json
from pathlib import Path

import pytest

from pipeline.agentes.disenador import run as dis
from pipeline.invariantes import validar_contra_esquema, verificar_aislamiento, vista_estudiante
from pipeline.llm import ClienteFalso

DIR_CASOS = Path(__file__).resolve().parents[1] / "evals" / "casos" / "disenador"
CASOS = sorted(DIR_CASOS.glob("*.json"))


def cargar(ruta):
    return json.loads(ruta.read_text(encoding="utf-8"))


def correr(caso, cliente):
    if caso["modo"] == "diseno":
        r = dis.disenar(caso["noticia"], caso["nivel"], fecha="2026-10-20", cliente=cliente)
        return r["candidatos"], r
    r = dis.iterar(caso["tarea_previa"], caso["evaluacion"], caso["noticia"], fecha="2026-10-20", cliente=cliente)
    return [r["tarea"]], r


def test_hay_cinco_casos_con_los_niveles_pedidos():
    assert len(CASOS) == 5
    casos = [cargar(c) for c in CASOS]
    assert {c["nivel"] for c in casos} == {"P", "S", "U"}
    assert sum(c["modo"] == "iteracion" for c in casos) == 1
    for c in casos:
        assert validar_contra_esquema(c["noticia"], "noticia"), c["id"]


@pytest.mark.parametrize("ruta", CASOS, ids=lambda r: r.stem)
def test_caso_cumple_criterio_de_aceptacion(ruta):
    caso = cargar(ruta)
    crit = caso["criterio_aceptacion"]
    cliente = ClienteFalso(copy.deepcopy(caso["respuestas_simuladas"]))
    tareas, res = correr(caso, cliente)

    assert len(tareas) == crit["n_candidatos"]
    assert res["meta"]["rondas"] == crit.get("rondas", 1)
    assert len(cliente.llamadas) == crit.get("rondas", 1)
    for t in tareas:
        r = validar_contra_esquema(t, "tarea")
        assert r.valido, r.errores
        assert t["estado"] == crit["estado"] == "borrador"
        assert t["nivel_principal"] == crit["nivel_principal"]
        assert t["rubrica_rub01"] is None
        assert verificar_aislamiento(vista_estudiante(t), t).valido
        assert "task_space" not in t["estudiante"]
        assert dis.validar_tarea(t, caso["noticia"]) == []
        # invariante 4: cada cifra usada es una cifra de la noticia con su localizador
        for c in t["noticia"]["cifras_usadas"]:
            assert c in caso["noticia"]["cifras"] and c["localizador"]["ubicacion"]
        assert t["modelo_y_prompt"]["version_prompt"] == dis.VERSION_PROMPT
        assert t["modelo_y_prompt"]["version_rubrica"] == "4.0"
    if caso["modo"] == "diseno":
        assert len({t["id"] for t in tareas}) == 2
        assert len(res["enfoques"]) == 2 and res["enfoques"][0] != res["enfoques"][1]
    else:
        assert tareas[0]["version"] == crit["version"] == caso["tarea_previa"]["version"] + 1
        assert tareas[0]["id"] == caso["tarea_previa"]["id"]
        atendidas = {a["criterio"] for a in res["atencion_mejoras"]}
        assert set(crit["atiende_mejoras"]) <= atendidas
        assert atendidas == {m["criterio"] for m in caso["evaluacion"]["mejoras"]}


def test_cifra_sin_localizador_se_detecta_y_se_repara():
    caso = cargar(DIR_CASOS / "s-maraton-cifras.json")
    cliente = ClienteFalso(copy.deepcopy(caso["respuestas_simuladas"]))
    _, res = correr(caso, cliente)
    primera = res["meta"]["historial"][0]
    assert primera["validos"] == 1
    textos = json.dumps(primera["errores"], ensure_ascii=False)
    assert "300" in textos and "cifra sin localizador" in textos
    # el reintento le muestra al modelo el error concreto
    assert "300" in cliente.llamadas[1]["messages"][0]["content"]


def test_sin_reparacion_posible_lanza_con_costo():
    caso = cargar(DIR_CASOS / "s-maraton-cifras.json")
    mala = copy.deepcopy(caso["respuestas_simuladas"][0])
    cliente = ClienteFalso([mala] * (dis.CONFIG["reparaciones_max"] + 1))
    # un candidato bueno + uno malo en todas las rondas: se devuelve el bueno y se informa el rechazado
    _, res = correr(caso, cliente)
    assert len(res["candidatos"]) == 1
    assert res["meta"]["rechazados"] and "300" in json.dumps(res["meta"]["rechazados"])
    todos_malos = copy.deepcopy(mala)
    todos_malos["candidatos"][1]["enunciado_es"] += " Participan 999 voluntarios."
    cliente = ClienteFalso([todos_malos] * (dis.CONFIG["reparaciones_max"] + 1))
    with pytest.raises(RuntimeError) as e:
        correr(caso, cliente)
    assert e.value.costo_usd > 0


def test_llamada_sin_temperature_con_schema_y_cache():
    caso = cargar(DIR_CASOS / "p-bicicletas.json")
    cliente = ClienteFalso(copy.deepcopy(caso["respuestas_simuladas"]))
    correr(caso, cliente)
    kw = cliente.llamadas[0]
    assert "temperature" not in kw
    assert kw["model"] == "claude-sonnet-5-5"
    assert kw["output_config"]["format"]["type"] == "json_schema"
    bloque = kw["system"][0]
    assert bloque["cache_control"] == {"type": "ephemeral"}
    for marca in ("MAR03", "PLT01", "RUB01", "Problema genuino"):
        assert marca in bloque["text"]
    # el esquema que ve el modelo no ofrece task_space dentro del bloque estudiante ni agent_visibility
    esq = json.dumps(kw["output_config"]["format"]["schema"])
    assert "agent_visibility" not in esq and '"estudiante"' not in esq


def test_el_esquema_del_modelo_no_usa_palabras_no_admitidas():
    esq = json.dumps(dis.esquema_salida("diseno")) + json.dumps(dis.esquema_salida("iteracion"))
    for prohibida in ("minItems", "maxItems", "pattern", "minLength", "$ref", "oneOf", "anyOf"):
        assert prohibida not in esq


def test_nivel_distinto_al_objetivo_se_rechaza():
    caso = cargar(DIR_CASOS / "p-bicicletas.json")
    malo = copy.deepcopy(caso["respuestas_simuladas"][0])
    for c in malo["candidatos"]:
        c["nivel_principal"] = "S"
    cliente = ClienteFalso([malo] * 3)
    with pytest.raises(RuntimeError):
        dis.disenar(caso["noticia"], "P", fecha="2026-10-20", cliente=cliente)


def test_fuga_de_task_space_al_enunciado_se_detecta():
    caso = cargar(DIR_CASOS / "s-cuenta-luz.json")
    r = copy.deepcopy(caso["respuestas_simuladas"][0]["candidatos"][0])
    paso = r["solucion_pasos"]
    r["enunciado_es"] += " " + paso
    t = dis.ensamblar(r, caso["noticia"], fecha="2026-10-20")
    errs = dis.validar_tarea(t, caso["noticia"])
    assert any("aislamiento" in e for e in errs)


def test_copia_literal_de_la_noticia_se_detecta():
    caso = cargar(DIR_CASOS / "s-cuenta-luz.json")
    texto = ("el consumo mensual de un hogar típico se mantiene estable durante todo el año y la familia "
             "decide con mucho cuidado si instala paneles solares o reduce el gasto en electricidad mensual")
    r = copy.deepcopy(caso["respuestas_simuladas"][0]["candidatos"][0])
    r["validation_evidence"] = texto
    t = dis.ensamblar(r, caso["noticia"], fecha="2026-10-20")
    assert dis.validar_tarea(t, caso["noticia"]) == []
    assert any("literal" in e for e in dis.validar_tarea(t, caso["noticia"], texto_noticia=texto))


def test_recurso_de_entrada_debe_estar_en_el_enunciado():
    caso = cargar(DIR_CASOS / "p-bicicletas.json")
    r = copy.deepcopy(caso["respuestas_simuladas"][0]["candidatos"][0])
    r["recursos"].append({"id": "R9", "que_es": "dato", "contenido": "Hay 8 estaciones.", "fase": "P1-MRS",
                          "fuente": "noticia (párrafo 3)", "disponibilidad": "de_entrada"})
    r["enunciado_es"] = r["enunciado_es"].replace("8 estaciones", "varias estaciones")
    t = dis.ensamblar(r, caso["noticia"], fecha="2026-10-20")
    assert any("de_entrada" in e for e in dis.validar_tarea(t, caso["noticia"]))


def test_iteracion_exige_mejoras():
    caso = cargar(DIR_CASOS / "iteracion-cuenta-luz.json")
    ev = copy.deepcopy(caso["evaluacion"])
    ev["mejoras"] = []
    with pytest.raises(ValueError):
        dis.iterar(caso["tarea_previa"], ev, caso["noticia"], cliente=ClienteFalso([]))


def test_iteracion_incompleta_se_repara():
    caso = cargar(DIR_CASOS / "iteracion-cuenta-luz.json")
    r = copy.deepcopy(caso["respuestas_simuladas"][0])
    incompleta = copy.deepcopy(r)
    incompleta["atencion_mejoras"] = incompleta["atencion_mejoras"][:1]
    cliente = ClienteFalso([incompleta, r])
    res = dis.iterar(caso["tarea_previa"], caso["evaluacion"], caso["noticia"], fecha="2026-10-20", cliente=cliente)
    assert res["meta"]["rondas"] == 2 and len(res["atencion_mejoras"]) == 2


def test_nivel_invalido_y_noticia_invalida():
    caso = cargar(DIR_CASOS / "p-bicicletas.json")
    with pytest.raises(ValueError):
        dis.disenar(caso["noticia"], "X", cliente=ClienteFalso([]))
    mala = {**caso["noticia"]}
    mala.pop("cifras")
    with pytest.raises(ValueError):
        dis.disenar(mala, "P", cliente=ClienteFalso([]))
