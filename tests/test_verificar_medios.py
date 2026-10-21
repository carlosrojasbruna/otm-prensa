"""pipeline/verificar_medios.py sin red: respuestas simuladas."""
import json

import pytest
import yaml

from pipeline import verificar_medios as V

RSS = b'<?xml version="1.0"?><rss version="2.0"><channel><title>x</title>' + b"<item><title>a</title></item>" * 3 + b"</channel></rss>"
RSS_TRUNCADO = b'<?xml version="1.0"?><rss><channel><item><title>a</title></item><item><title>b</ti'
HTML = b"<!doctype html><html><body>no soy feed</body></html>"

MED01 = {
    "version": "9.9",
    "medios": [
        {"id": "bueno", "nombre": "Bueno", "acceso": "rss", "url": "https://bueno.cl/rss",
         "secciones": [{"area": "salud", "url": "https://bueno.cl/salud.xml"}]},
        {"id": "caido", "nombre": "Caído", "acceso": "rss", "url": "https://caido.cl/rss",
         "url_verificar": True, "respaldo": {"acceso": "gnews", "url": "https://news.google.com/rss/search?q=site:caido.cl"}},
        {"id": "html", "nombre": "Html", "acceso": "rss", "url": "https://html.cl/feed"},
        {"id": "robots", "nombre": "Robots", "acceso": "rss", "url": "https://robots.cl/privado/rss"},
        {"id": "solognews", "nombre": "G", "acceso": "gnews", "url": "https://news.google.com/rss/search?q=site:g.cl"},
    ],
}

RESP = {
    "https://bueno.cl/robots.txt": (200, "text/plain", b"User-agent: *\nAllow: /\n"),
    "https://bueno.cl/rss": (200, "application/rss+xml", RSS),
    "https://bueno.cl/salud.xml": (200, "text/xml", RSS_TRUNCADO),
    "https://caido.cl/robots.txt": (404, "text/html", b""),
    "https://caido.cl/rss": (503, "text/html", b""),
    "https://news.google.com/robots.txt": (200, "text/plain", b"User-agent: *\nAllow: /\n"),
    "https://news.google.com/rss/search?q=site:caido.cl": (200, "text/xml", RSS),
    "https://news.google.com/rss/search?q=site:g.cl": (200, "text/xml", RSS),
    "https://html.cl/robots.txt": (404, "", b""),
    "https://html.cl/feed": (200, "text/html", HTML),
    "https://robots.cl/robots.txt": (200, "text/plain", b"User-agent: OTM-Prensa\nDisallow: /privado/\n"),
    "https://robots.cl/privado/rss": (200, "text/xml", RSS),
}


class Falso:
    def __init__(self, resp=None):
        self.resp, self.pedidas = dict(resp or RESP), []

    def __call__(self, url, timeout):
        self.pedidas.append(url)
        if url not in self.resp:
            raise OSError("sin ruta simulada")
        return self.resp[url]


def correr(fetch=None, **kw):
    f = fetch or Falso()
    rep = V.verificar(MED01, fetch=f, espera=0, **kw)
    return rep, f, {m["id"]: m for m in rep["medios"]}


def test_contar_items_tolera_truncado_y_rechaza_html():
    assert V.contar_items(RSS) == (True, 3)
    assert V.contar_items(RSS_TRUNCADO) == (True, 2)
    assert V.contar_items(HTML) == (False, 0)
    assert V.contar_items(b'<feed xmlns="http://www.w3.org/2005/Atom"><entry/><entry/></feed>') == (True, 2)


def test_medio_sano_es_ok_y_cuenta_items_de_cada_url():
    rep, _, m = correr()
    assert m["bueno"]["recomendacion"] == {"estado": "ok", "acceso": "rss", "url": "https://bueno.cl/rss"}
    n = {u["url"]: u["items"] for u in m["bueno"]["urls"]}
    assert n == {"https://bueno.cl/rss": 3, "https://bueno.cl/salud.xml": 2}


def test_principal_caido_usa_respaldo_gnews():
    _, _, m = correr()
    rec = m["caido"]["recomendacion"]
    assert rec["estado"] == "usar_respaldo" and rec["acceso"] == "gnews" and "site:caido.cl" in rec["url"]
    assert "503" in rec["motivo"]


def test_html_en_vez_de_feed_y_sin_respaldo_es_sin_acceso():
    _, _, m = correr()
    assert m["html"]["recomendacion"]["estado"] == "sin_acceso"
    assert "no es un feed" in m["html"]["recomendacion"]["motivo"]


def test_robots_que_prohibe_la_ruta_no_se_descarga():
    _, f, m = correr()
    assert "https://robots.cl/privado/rss" not in f.pedidas
    assert m["robots"]["recomendacion"]["estado"] == "sin_acceso"
    assert m["robots"]["urls"][0]["robots_permitido"] is False


def test_robots_inaccesible_es_no_verificable_y_no_descarga():
    resp = dict(RESP)
    resp["https://bueno.cl/robots.txt"] = (500, "", b"")
    _, f, m = correr(Falso(resp))
    assert "https://bueno.cl/rss" not in f.pedidas
    assert m["bueno"]["urls"][0]["robots_permitido"] is None


def test_error_de_red_se_registra_sin_romper():
    resp = dict(RESP)
    del resp["https://bueno.cl/rss"]
    _, _, m = correr(Falso(resp))
    assert "OSError" in m["bueno"]["urls"][0]["error"]


def test_robots_se_descarga_una_vez_por_origen():
    _, f, _ = correr()
    assert f.pedidas.count("https://bueno.cl/robots.txt") == 1


def test_filtro_por_ids_y_resumen():
    rep, _, m = correr(solo=["bueno"])
    assert list(m) == ["bueno"] and rep["resumen"] == {"medios": 1, "ok": 1, "usar_respaldo": 0, "sin_acceso": 0}
    assert rep["costo_usd"] == 0.0 and "OTM-Prensa" in rep["user_agent"]


def test_main_escribe_json_y_no_toca_insumos(tmp_path):
    med = tmp_path / "MED01_x_v9.9_2026-01-01.yaml"
    med.write_text(yaml.safe_dump(MED01), encoding="utf-8")
    antes = {p: p.read_bytes() for p in (V.RAIZ / "insumos" / "medios").glob("*.yaml")}
    rc = V.main(["--med01", str(med), "--salida", str(tmp_path / "out"), "--espera", "0"], fetch=Falso())
    assert rc == 0
    [salida] = list((tmp_path / "out").glob("verificacion_*.json"))
    assert json.loads(salida.read_text(encoding="utf-8"))["med01_version"] == "9.9"
    assert antes == {p: p.read_bytes() for p in antes}


def test_estricto_sale_con_1_si_hay_medios_sin_acceso(tmp_path):
    med = tmp_path / "MED01_x_v9.9_2026-01-01.yaml"
    med.write_text(yaml.safe_dump(MED01), encoding="utf-8")
    assert V.main(["--med01", str(med), "--salida", str(tmp_path), "--espera", "0", "--estricto"], fetch=Falso()) == 1


def test_espera_entre_peticiones_al_mismo_origen():
    dormidas = []
    V.verificar(MED01, fetch=Falso(), espera=5.0, dormir=dormidas.append, solo=["bueno"])
    assert dormidas and all(0 < d <= 5.0 for d in dormidas)


def test_ruta_med01_elige_la_version_mas_alta():
    assert "v1.4" in V.ruta_med01().name or V.ruta_med01().name >= "MED01_medios_v1.4"
