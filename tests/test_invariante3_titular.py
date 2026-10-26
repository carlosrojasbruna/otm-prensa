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


# --------------------------------------------------------------------------- caso real del ciclo 2026-10-26
def _pagina_ciper(noticia: dict) -> str:
    """HTML como el que devuelve `bajar_cuerpo` para una nota de CIPER: los <p> arrastran el índice lateral y los
    botones de compartir, con enlaces cuyo slug repite fecha y titular (y `utm_campaign` otra vez el slug). El
    cuerpo es sintético: el texto real de la noticia no se guarda en el repo (invariante 3)."""
    ruta = noticia["url"].split("ciperchile.cl", 1)[1]
    return (f'<p class="fecha">23.10.2026</p>\n<p><ul><li><a class="aside-indice-link" href="{ruta}">- INICIO</a>'
            f'</li></ul><!-- <a href="{noticia["url"]}">compartir</a> --></p>\n'
            f'<p><a href="https://twitter.com/intent/tweet?url={noticia["url"]}">X</a></p>\n'
            "<p>" + CUERPO_26 + " según el informe técnico entregado al concejo municipal la semana pasada.</p>\n")


def _expediente_real(tid="2026-10-que-programas-restituir"):
    from pipeline import orquestador as orq
    return orq.cargar(tid)


def test_ciclo_20261026_url_citada_no_cuenta_como_cuerpo():
    """4 borradores (que-programas-restituir, cual-recorte-duele-mas, dio-resultado-oponerse-tribunales,
    dos-cifras-misma-noticia) se rechazaron con «2026 10 23 fundacion horizonte ciudadano … utm_source rss …»:
    la URL de la cita contra los enlaces del HTML. Con los artefactos reales del expediente, pasa."""
    exp = _expediente_real()
    fuente = _pagina_ciper(exp.artefactos["noticia"])
    viejo = inv.max_palabras_consecutivas_comunes(" ".join(inv.textos_de(exp.artefactos)), fuente)[0]
    assert viejo > 25                       # así fallaba antes: sin quitar la cita ni el marcado
    r = inv.cumple_limite_literal(exp.artefactos, fuente)
    assert r, r.errores
    assert r.detalle["max_consecutivas"] < 10


def test_ciclo_20261026_el_orquestador_aplica_la_exclusion():
    from pipeline import orquestador as orq
    exp = _expediente_real()
    fuente = _pagina_ciper(exp.artefactos["noticia"])
    nuevo = orq.transicionar(exp, "archivada", motivo="test", texto_noticia=fuente)   # comprueba la invariante 3
    assert nuevo.estado == "archivada"


def test_ciclo_20261026_el_cuerpo_copiado_sigue_fallando():
    from pipeline import orquestador as orq
    import pytest
    exp = _expediente_real()
    fuente = _pagina_ciper(exp.artefactos["noticia"])
    exp.artefactos["tarea"]["estudiante"]["enunciado_es"] += " " + CUERPO_26
    with pytest.raises(orq.InvarianteViolada, match="26 palabras"):
        orq.transicionar(exp, "archivada", motivo="test", texto_noticia=fuente)


def test_texto_plano_quita_marcado_y_urls():
    t = inv.texto_plano('<p>Hola <a href="https://x.cl/2026/10/23/a-b-c/?utm_source=rss">mundo</a> &amp; '
                        'más /2026/10/23/slug-del-titular/ www.medio.cl/a</p><script>var a=1;</script>')
    assert inv.palabras_normalizadas(t) == ["hola", "mundo", "mas"]
