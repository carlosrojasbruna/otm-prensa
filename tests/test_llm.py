from pipeline.llm import ClienteFalso, config, costo_usd, llamar, modelo_de


def test_precios_para_todos_los_modelos_configurados():
    precios = config()["precios_modelos"]
    for agente, modelo in config()["modelos"].items():
        assert modelo in precios, f"{agente}: {modelo} sin precio en config.yaml"


def test_costo_usa_tabla():
    assert costo_usd({"input_tokens": 1_000_000, "output_tokens": 1_000_000}, "claude-haiku-5-5") == 0.6


def test_llamar_con_esquema_y_cliente_falso():
    c = ClienteFalso([{"ok": True}])
    r = llamar(agente="filtro", system="s", user="u", schema={"type": "object"}, cliente=c)
    assert r["salida"] == {"ok": True}
    assert r["meta"]["modelo"] == modelo_de("filtro")
    assert "temperature" not in c.llamadas[0]
    assert c.llamadas[0]["output_config"]["format"]["type"] == "json_schema"


def test_llamar_reintenta_json_invalido():
    c = ClienteFalso(["no es json", {"ok": 1}])
    r = llamar(agente="filtro", system="s", user="u", schema={"type": "object"}, cliente=c)
    assert r["meta"]["intentos"] == 2
