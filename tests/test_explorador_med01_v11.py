"""Explorador con MED01 (fuentes agregadas en v1.1; vigente v1.4), sin red: feeds y HTML sintéticos escritos por el equipo (invariante 3)."""
import base64
import json
import urllib.error
from datetime import datetime, timezone

from pipeline import invariantes as inv
from pipeline.agentes.explorador import run as ex
from pipeline.llm import ClienteFalso

AHORA = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
CASO1 = json.loads((ex.RAIZ / "evals/casos/explorador/caso_1.json").read_text(encoding="utf-8"))
PAGINA = "<html><body>" + CASO1["entrada"]["cuerpo_html"] + "</body></html>"

RSS_TRUNCADO = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><title>Sintético</title>
<item><title>Uno sintético</title><link>https://www.latercera.com/s/1</link>
<pubDate>Fri, 17 Oct 2026 10:00:00 GMT</pubDate><content:encoded><![CDATA[<p>Cuerpo con 5 cifras.</p>]]></content:encoded></item>
<item><title>Dos sintético</title><link>https://www.latercera.com/s/2</link>
<pubDate>Thu, 16 Oct 2026 10:00:00 GMT</pubDate><description>Otro texto 7.</description></item>
<item><title>Tres incomple"""

RDF_NATURE = """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
<item rdf:about="https://www.nature.com/articles/d41586-026-00001-1"><title>Noticia sintética</title>
<link>https://www.nature.com/articles/d41586-026-00001-1</link><dc:date>2026-10-18T09:00:00Z</dc:date>
<dc:identifier>doi:10.1038/d41586-026-00001-1</dc:identifier></item>
<item rdf:about="https://www.nature.com/articles/s41586-026-00002-2"><title>Artículo sintético</title>
<link>https://www.nature.com/articles/s41586-026-00002-2</link><dc:date>2026-10-18T09:00:00Z</dc:date>
<dc:identifier>doi:10.1038/s41586-026-00002-2</dc:identifier></item>
<item rdf:about="https://www.nature.com/articles/d41586-026-00003-3"><title>Tercera sintética</title>
<link>https://www.nature.com/articles/d41586-026-00003-3</link><dc:date>2026-10-17T09:00:00Z</dc:date>
<dc:identifier>doi:10.1038/d41586-026-00003-3</dc:identifier></item>
<item rdf:about="https://www.nature.com/articles/d41586-026-00004-4"><title>Cortada</title><link>https://www.nat"""

FEED_NATURE_OK = """<?xml version='1.0'?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<item><title>Noticia sintética de Nature</title><link>https://www.nature.com/articles/d41586-026-00009-9</link>
<dc:date>2026-10-18T09:00:00Z</dc:date><dc:identifier>doi:10.1038/d41586-026-00009-9</dc:identifier>
<description>Solo un titular sintético.</description></item></rdf:RDF>"""


def _medio(mid):
    return next(m for m in ex.cargar_med01()["medios"] if m["id"] == mid)


def _gn(url_original):
    crudo = b"\x08\x13\x22" + url_original.encode() + b"\xd2\x01\x00"
    return "https://news.google.com/rss/articles/" + base64.urlsafe_b64encode(crudo).decode().rstrip("=") + "?oc=5"


def _rss_gnews(links):
    items = "".join(
        f"<item><title>Sintética {i} - Reuters</title><link>{u}</link>"
        f"<pubDate>Fri, 1{i} Oct 2026 10:00:00 GMT</pubDate></item>" for i, u in enumerate(links, 4))
    return f"<?xml version='1.0'?><rss version='2.0'><channel>{items}</channel></rss>".encode()


def _leer_con_robots(robots, pagina=PAGINA):
    def leer(url):
        if url.endswith("/robots.txt"):
            if isinstance(robots, int):
                raise urllib.error.HTTPError(url, robots, "x", {}, None)
            return robots.encode()
        return pagina.encode()
    return leer


def test_med01_mas_alta_y_registrada():
    assert ex.cargar_med01()["version"] == "1.4"
    ids = {m["id"] for m in ex.cargar_med01()["medios"]}
    assert {"latercera", "naturenews", "dw", "cnnchile"} <= ids
    assert _medio("cnnchile")["acceso"] == "gnews"


def test_xml_truncado_descarta_ultimo_item_incompleto():
    items = ex.parsear_feed(RSS_TRUNCADO)
    assert [i["titulo"] for i in items] == ["Uno sintético", "Dos sintético"]
    assert "5 cifras" in items[0]["cuerpo_html"]


def test_xml_truncado_sin_items_completos_falla_controlado():
    try:
        ex.parsear_feed("<rss><channel><item><title>x")
    except Exception as e:  # noqa: BLE001
        assert type(e).__name__ == "ParseError"
    else:
        raise AssertionError("debía fallar")


def test_recolectar_con_feed_truncado_no_falla():
    c = ex.recolectar(_medio("latercera"), 10, AHORA, lambda u: RSS_TRUNCADO.encode())
    assert len(c) == 2 and c[0]["medio_id"] == "latercera"


def test_filtro_doi_nature_solo_periodismo_d41586():
    c = ex.recolectar(_medio("naturenews"), 10, AHORA, lambda u: RDF_NATURE.encode())
    assert [x["titulo"] for x in c] == ["Noticia sintética", "Tercera sintética"]
    assert all("d41586" in x["url"] for x in c)


def test_gnews_resuelto_usa_url_y_medio_del_original():
    orig = "https://www.reuters.com/world/sintetico-uno"
    feed = _rss_gnews([_gn(orig)])
    c = ex.recolectar(_medio("reuters"), 5, AHORA, lambda u: feed)
    assert len(c) == 1
    assert c[0]["url"] == orig and c[0]["medio_id"] == "reuters" and "news.google" not in c[0]["url"]
    assert c[0]["titulo"] == "Sintética 4"          # sin el sufijo " - Reuters" de Google News


def test_gnews_cnnchile_resuelve_con_resolver_inyectado():
    feed = _rss_gnews(["https://news.google.com/rss/articles/CBMiOPACO?oc=5"])
    c = ex.recolectar(_medio("cnnchile"), 5, AHORA, lambda u: feed,
                      resolver=lambda u: "https://www.cnnchile.com/pais/sintetico_20261018/")
    assert c[0]["medio_id"] == "cnnchile" and c[0]["url"].startswith("https://www.cnnchile.com/")


def test_gnews_no_resuelto_se_descarta_con_motivo():
    feed = _rss_gnews(["https://news.google.com/rss/articles/CBMiXXXX?oc=5"])
    desc = []
    c = ex.recolectar(_medio("reuters"), 5, AHORA, lambda u: feed, resolver=lambda u: None, descartes=desc)
    assert c == [] and "no se pudo resolver" in desc[0]["motivo"]


def test_gnews_resuelto_a_medio_fuera_de_med01_se_descarta():
    feed = _rss_gnews([_gn("https://www.sitio-ajeno.example/nota")])
    desc = []
    c = ex.recolectar(_medio("reuters"), 5, AHORA, lambda u: feed, descartes=desc)
    assert c == [] and "no está en MED01" in desc[0]["motivo"]


def test_resolver_gnews_sin_red_con_abrir_inyectado():
    assert ex.resolver_gnews("https://www.bbc.com/x") == "https://www.bbc.com/x"
    g = "https://news.google.com/rss/articles/CBMiZZ"
    assert ex.resolver_gnews(g, abrir=lambda u: "https://www.dw.com/es/a") == "https://www.dw.com/es/a"
    assert ex.resolver_gnews(g, abrir=lambda u: u) is None

    def falla(u):
        raise OSError

    assert ex.resolver_gnews(g, abrir=falla) is None


def test_robots_prohibe_no_se_lee_ni_se_llama_al_modelo():
    base = _leer_con_robots("User-agent: *\nDisallow: /")
    assert not ex.robots_permite("https://www.nature.com/articles/x", base, {})

    def leer(url):
        return FEED_NATURE_OK.encode() if url == _medio("naturenews")["url"] else base(url)

    cli = ClienteFalso([])
    r = ex.explorar(["naturenews"], 3, cliente=cli, ahora=AHORA, leer=leer)
    assert r["noticias"] == [] and len(cli.llamadas) == 0
    assert "robots.txt" in r["descartes"][0]["motivo"]


def test_robots_404_permite_y_se_lee_el_enlace_original():
    base = _leer_con_robots(404)

    def leer(url):
        return FEED_NATURE_OK.encode() if url == _medio("naturenews")["url"] else base(url)

    cli = ClienteFalso(CASO1["respuestas_modelo"])
    r = ex.explorar(["naturenews"], 3, cliente=cli, ahora=AHORA, leer=leer)
    assert r["meta"]["n_aceptadas"] == 1 and r["meta"]["version_med01"] == "1.4"
    n = r["noticias"][0]
    assert n["medio_id"] == "naturenews" and inv.validar_contra_esquema(n, "noticia")
    # la descripción del feed se ignora: el cuerpo vino de la página
    assert "titular sintético" not in cli.llamadas[0]["messages"][0]["content"]


def test_robots_con_error_de_servidor_es_conservador():
    assert not ex.robots_permite("https://x.example/a", _leer_con_robots(503), {})
    assert ex.robots_permite("https://x.example/a", _leer_con_robots("User-agent: *\nDisallow: /privado"), {})


def test_latercera_usa_cuerpo_del_feed_sin_bajar_pagina():
    cuerpo = CASO1["entrada"]["cuerpo_html"]
    rss = ("<?xml version='1.0'?><rss version='2.0' xmlns:content='http://purl.org/rss/1.0/modules/content/'>"
           "<channel><item><title>Sintética La Tercera</title><link>https://www.latercera.com/s/9</link>"
           "<pubDate>Fri, 17 Oct 2026 10:00:00 GMT</pubDate><content:encoded><![CDATA[" + cuerpo +
           "]]></content:encoded></item></channel></rss>")
    paginas = []

    def bajar(u):
        paginas.append(u)
        return ""

    cli = ClienteFalso(CASO1["respuestas_modelo"])
    r = ex.explorar(["latercera"], 3, cliente=cli, ahora=AHORA, leer=lambda u: rss.encode(), bajar=bajar)
    assert r["meta"]["n_aceptadas"] == 1 and paginas == []


def test_error_de_api_en_una_noticia_no_detiene_el_lote(monkeypatch):
    from pipeline.agentes.explorador import run

    monkeypatch.setattr(run, "cargar_med01", lambda: {"version": "1.1", "medios": [{"id": "x"}]})
    monkeypatch.setattr(run, "recolectar", lambda *a, **k: [{"url": "https://x/1", "medio_id": "x"}])

    def falla(*a, **k):
        raise RuntimeError("explorador: la llamada falló tras 3 intentos: stop_reason=max_tokens")

    monkeypatch.setattr(run, "explorar_noticia", falla)
    res = run.explorar(cliente=object(), bajar=lambda u: "")
    assert res["noticias"] == []
    assert res["descartes"][0]["motivo"].startswith("error de API")


def test_cita_titulo_abrevia_titulares_largos():
    from pipeline.agentes.explorador.run import cita_titulo

    corto = "Un titular de diez palabras que no se debe tocar nunca"
    assert cita_titulo(corto) == corto
    largo = " ".join(f"p{i}" for i in range(34))
    c = cita_titulo(largo)
    assert c.endswith(" …") and len(c.split()) == 21
