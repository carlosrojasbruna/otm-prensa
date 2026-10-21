"""Invariante 3 con el contrato `noticia` v1.2: el titular se cita completo y queda fuera del conteo de 25 palabras;
el límite sigue rigiendo para el cuerpo (resumen_propio, enunciado, recursos y guía). Sin red."""
import copy
import importlib.util
import json

from conftest import RAIZ, cargar_ejemplo
from pipeline import invariantes as inv

# Titular sintético de 30 palabras y cuerpo sintético; el cuerpo repite el titular como entradilla.
TITULAR = ("Municipio de una ciudad costera evalúa ampliar la ciclovía principal del centro hacia los barrios del "
           "norte tras registrar un aumento sostenido de viajes diarios durante los últimos tres años")
CUERPO_26 = ("los conteos automáticos instalados en los cruces mostraron que la mayoría de los ciclistas recorre "
             "tramos cortos y que el uso cae con fuerza en invierno")
FUENTE = TITULAR + ".\n" + CUERPO_26 + " según el informe técnico entregado al concejo municipal la semana pasada."


def test_el_caso_tiene_las_longitudes_pedidas():
    assert len(TITULAR.split()) == 30 and len(CUERPO_26.split()) == 26


def _tarea_con(titular, enunciado_extra=""):
    t = copy.deepcopy(cargar_ejemplo("tarea"))
    t["noticia"]["titulo"] = titular
    if enunciado_extra:
        t["estudiante"]["enunciado_es"] += " " + enunciado_extra
    return t


def test_titular_de_30_palabras_en_la_cita_pasa():
    r = inv.cumple_limite_literal(_tarea_con(TITULAR), FUENTE)
    assert r, r.errores


def test_26_palabras_del_cuerpo_fallan():
    r = inv.cumple_limite_literal(_tarea_con(TITULAR, CUERPO_26), FUENTE)
    assert not r and "26 palabras" in r.errores[0]


def test_el_titular_copiado_fuera_de_la_cita_cuenta():
    # el titular solo queda fuera del conteo como cita; copiado en el enunciado sí cuenta
    r = inv.cumple_limite_literal(_tarea_con("Otro titular", TITULAR), FUENTE)
    assert not r


def test_artefacto_noticia_y_catalogo():
    n = copy.deepcopy(cargar_ejemplo("noticia"))
    n["titulo"] = TITULAR
    assert inv.validar_contra_esquema(n, "noticia")
    assert inv.cumple_limite_literal(n, FUENTE)
    cat = {"tareas": [{"titulo": "propio", "noticia": {"medio": "M", "titulo": TITULAR, "fecha": "2026-10-20",
                                                         "url": "https://example.org/x"}}]}
    assert inv.cumple_limite_literal(cat, FUENTE)


def test_en_una_cadena_se_quitan_los_titulares_entregados():
    md = f"Noticia: Medio, «{TITULAR}», 2026-10-20\n\nEnunciado propio sin copia."
    assert not inv.cumple_limite_literal(md, FUENTE)                        # sin decir cuál es el titular
    assert inv.cumple_limite_literal(md, FUENTE, titulares=[TITULAR])
    assert not inv.cumple_limite_literal(md + " " + CUERPO_26, FUENTE, titulares=[TITULAR])


def test_contrato_noticia_v1_2():
    esq = json.loads((RAIZ / "contratos" / "noticia.schema.json").read_text(encoding="utf-8"))
    assert "Contrato v1.2" in esq["description"]
    assert "fuera del conteo" in esq["properties"]["titulo"]["description"]


def test_hook_excluye_el_titular_en_json():
    spec = importlib.util.spec_from_file_location("otm_hook", RAIZ / ".claude" / "hooks" / "otm_hook.py")
    h = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h)
    texto = json.dumps(_tarea_con(TITULAR), ensure_ascii=False)
    assert h.chequear_texto("tareas/2026-10/x/tarea_v1.0_2026-10-21.json", texto, [("n", FUENTE)]) == []
    malo = json.dumps(_tarea_con(TITULAR, CUERPO_26), ensure_ascii=False)
    assert h.chequear_texto("tareas/2026-10/x/tarea_v1.0_2026-10-21.json", malo, [("n", FUENTE)])
