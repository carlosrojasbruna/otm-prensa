"""Tests del explorador: sin red, con ClienteFalso y fixtures sintéticos (evals/casos/explorador)."""
import json
from datetime import datetime, timezone

import pytest

from pipeline import invariantes as inv
from pipeline.agentes.explorador import run as ex
from pipeline.llm import ClienteFalso

DIR = ex.RAIZ / "evals" / "casos" / "explorador"
AHORA = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
CASOS = sorted(DIR.glob("caso_*.json"))


def _caso(i):
    return json.loads(CASOS[i].read_text(encoding="utf-8"))


def _candidato(entrada):
    c = dict(entrada)
    c["fecha"] = datetime.fromisoformat(c["fecha"]).replace(tzinfo=timezone.utc)
    return c


def test_hay_cinco_casos():
    assert len(CASOS) == 5


@pytest.mark.parametrize("ruta", CASOS, ids=lambda p: p.stem)
def test_caso(ruta):
    caso = json.loads(ruta.read_text(encoding="utf-8"))
    esp = caso["esperado"]
    cli = ClienteFalso(caso["respuestas_modelo"])
    res = ex.explorar_noticia(_candidato(caso["entrada"]), cliente=cli, ahora=AHORA, bajar=None)
    assert len(cli.llamadas) == esp["llamadas"]
    if esp["resultado"] == "aceptada":
        n = res["noticia"]
        assert n is not None, res["descartada"]
        v = inv.validar_contra_esquema(n, "noticia")
        assert v, v.errores
        assert inv.medio_en_lista_blanca(n["medio_id"])
        assert n["cifras"] and all(c["localizador"]["ubicacion"] for c in n["cifras"])
        assert len(n["cifras"]) == esp["n_cifras"]
        if "area" in esp:
            assert n["area"] == esp["area"]
        if "id" in esp:
            assert n["id"] == esp["id"]
        if "cifra_ausente" in esp:
            assert esp["cifra_ausente"] not in [c["valor"] for c in n["cifras"]]
        cuerpo = "\n".join(ex.parrafos_de(caso["entrada"]["cuerpo_html"]))
        assert inv.cumple_limite_literal({k: v_ for k, v_ in n.items() if k != "titulo"}, cuerpo)
        if "aviso_en_segunda_llamada" in esp:
            assert "AVISO DE CORRECCIÓN" in cli.llamadas[1]["messages"][0]["content"]
    else:
        assert res["noticia"] is None
        assert esp["motivo_contiene"] in res["descartada"]


def test_modelo_es_el_de_config_y_sin_temperatura():
    caso = _caso(0)
    cli = ClienteFalso(caso["respuestas_modelo"])
    ex.explorar_noticia(_candidato(caso["entrada"]), cliente=cli, ahora=AHORA, bajar=None)
    assert cli.llamadas[0]["model"] == "claude-haiku-5-5"
    assert "temperature" not in cli.llamadas[0]


def test_resumen_siempre_copia_se_descarta():
    caso = _caso(1)
    cli = ClienteFalso([caso["respuestas_modelo"][0]] * 3)
    res = ex.explorar_noticia(_candidato(caso["entrada"]), cliente=cli, ahora=AHORA, bajar=None)
    assert res["noticia"] is None and "rechazado" in res["descartada"]
    assert len(cli.llamadas) == 3


def test_resumen_de_mas_de_80_palabras_se_rechaza():
    caso = _caso(0)
    largo = dict(caso["respuestas_modelo"][0], resumen_propio=" ".join(["palabra"] * 81))
    cli = ClienteFalso([largo, caso["respuestas_modelo"][0]])
    res = ex.explorar_noticia(_candidato(caso["entrada"]), cliente=cli, ahora=AHORA, bajar=None)
    assert res["noticia"] is not None and len(cli.llamadas) == 2


RSS_VIEJA = """<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>Reciente sintética</title><link>https://www.cnnchile.com/s/1</link><pubDate>Fri, 17 Oct 2026 10:00:00 GMT</pubDate>
<description>Texto sintético con 12 cifras.</description></item>
<item><title>Vieja sintética</title><link>https://www.cnnchile.com/s/2</link><pubDate>Mon, 01 Sep 2026 10:00:00 GMT</pubDate>
<description>x</description></item></channel></rss>"""


def test_recolectar_filtra_por_fecha_y_no_usa_respaldo_si_hay_principal():
    med = next(m for m in ex.cargar_med01()["medios"] if m["id"] == "cnnchile")
    visitadas = []

    def leer(url):
        visitadas.append(url)
        return RSS_VIEJA.encode()

    c = ex.recolectar(med, 10, AHORA, leer)
    assert [x["titulo"] for x in c] == ["Reciente sintética"]
    assert visitadas == [med["url"]]


def test_explorar_de_punta_a_punta_con_feed_local():
    caso = _caso(0)
    rss = ("<?xml version='1.0'?><rss version='2.0'><channel><item><title>Sintética con embalse</title>"
           "<link>https://www.cnnchile.com/s/9</link><pubDate>Fri, 17 Oct 2026 10:00:00 GMT</pubDate>"
           "<description><![CDATA[" + caso["entrada"]["cuerpo_html"] + "]]></description></item></channel></rss>")
    cli = ClienteFalso(caso["respuestas_modelo"])
    r = ex.explorar(["cnnchile"], 5, cliente=cli, ahora=AHORA, leer=lambda u: rss.encode(), bajar=None)
    assert r["meta"]["n_aceptadas"] == 1 and r["meta"]["costo_usd"] > 0
    assert r["meta"]["version_prompt"] == "1.0" and r["meta"]["modelo"] == "claude-haiku-5-5"
    for n in r["noticias"]:
        assert inv.validar_contra_esquema(n, "noticia")


def test_cifra_verificada():
    ps = ["El nivel es 1.234,5 litros", "Sube 38 %"]
    assert ex.cifra_verificada("1.234,5", ps, 1)
    assert ex.cifra_verificada("38 %", ps, 2)
    assert not ex.cifra_verificada("38 %", ps, 1)
    assert not ex.cifra_verificada("38", ps, 3)
