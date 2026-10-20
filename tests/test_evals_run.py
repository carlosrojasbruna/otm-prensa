"""Tests sin red de evals/run.py: forma de la matriz, regla de recomendación y registro de costo."""
import json

import pytest

from evals import run as R
from pipeline.llm import ClienteFalso, costo_usd

H, S, O = "claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"


def _celda(agente, modelo, valor, pasa, estado="completa", costo_u=0.01, **extra):
    c = R.celda_na(agente, modelo, "x")
    c.update({"estado": estado, "pasa": pasa, "costo_por_unidad_usd": costo_u, "latencia_media_s": 1.0,
              "metrica": {"nombre": R.UMBRALES[agente]["metrica"], "umbral": R.UMBRALES[agente]["umbral"], "valor": valor},
              "n_unidades": 5, "n_unidades_omitidas": 0})
    c.update(extra)
    return c


# ------------------------------------------------------------------ regla de recomendación
def test_recomienda_el_mas_barato_que_pasa():
    cs = [_celda("filtro", O, 0.9, True, costo_u=0.08), _celda("filtro", H, 0.4, False, costo_u=0.001),
          _celda("filtro", S, 0.7, True, costo_u=0.02)]
    r = R.recomendar("filtro", cs, H)
    assert r["modelo"] == S and r["cambia"] is True
    assert "0,700" in r["justificacion"] and "0,400" in r["justificacion"]   # justificada con números


def test_no_cambia_si_el_de_partida_es_el_mas_barato_que_pasa():
    cs = [_celda("filtro", H, 0.8, True), _celda("filtro", S, 0.9, True), _celda("filtro", O, 1.0, True)]
    r = R.recomendar("filtro", cs, H)
    assert r["modelo"] == H and r["cambia"] is False


def test_celda_no_corrida_no_puede_ser_recomendada_y_se_avisa():
    cs = [_celda("redactor", H, None, None, estado="no_corrida"), _celda("redactor", S, 1.0, True),
          _celda("redactor", O, 1.0, True)]
    r = R.recomendar("redactor", cs, S)
    assert r["modelo"] == S and "Sin evidencia" in r["justificacion"]


def test_ningun_modelo_pasa_mantiene_el_de_partida():
    cs = [_celda("explorador", m, 0.2, False) for m in (H, S, O)]
    r = R.recomendar("explorador", cs, H)
    assert r["modelo"] is None and r["cambia"] is False and "Ningún modelo" in r["justificacion"]


def test_bibliotecario_no_tiene_recomendacion():
    r = R.recomendar("bibliotecario", [R.celda_na("bibliotecario", m, "script") for m in (H, S, O)], H)
    assert r["modelo"] is None and "sin modelo" in r["justificacion"]


def test_orden_por_precio_de_config():
    assert R.modelos_por_precio([O, H, S]) == [H, S, O]


def test_umbrales_definidos_para_los_9_agentes():
    assert set(R.UMBRALES) == set(R.AGENTES) and len(R.AGENTES) == 9
    assert R.UMBRALES["filtro"]["umbral"] == 0.6 and R.UMBRALES["evaluador"]["umbral"] == 0.7
    assert R.UMBRALES["bibliotecario"]["umbral"] is None


def test_celda_pasa_solo_si_completa_y_sobre_umbral():
    u_ok = {"id": "a", "ok": True, "omitida": False, "error": None, "segundos": 1.0, "costo_usd": 0.01, "n_llamadas": 1,
            "modelos_solicitados": [H], "detalle": {}}
    u_om = dict(u_ok, id="b", omitida=True, ok=None, n_llamadas=0, costo_usd=0.0, modelos_solicitados=[])
    c = R.finalizar_celda("explorador", H, [u_ok, u_ok], {"valor": 1.0})
    assert c["estado"] == "completa" and c["pasa"] is True
    c = R.finalizar_celda("explorador", H, [u_ok, u_om], {"valor": 1.0})
    assert c["estado"] == "parcial" and c["pasa"] is None and c["n_unidades_omitidas"] == 1
    c = R.finalizar_celda("explorador", H, [u_om], {"valor": None})
    assert c["estado"] == "no_corrida" and c["pasa"] is None


# ------------------------------------------------------------------ presupuesto y registro de costo
def test_cliente_medido_registra_costo_con_la_tabla_de_config():
    p = R.Presupuesto(1.0)
    cli = R.ClienteMedido(ClienteFalso([{"ok": 1}]), p, "filtro")
    cli.create(model=O, max_tokens=100, system=[{"type": "text", "text": "s"}], messages=[{"role": "user", "content": "u"}])
    esperado = costo_usd({"input_tokens": 1000, "output_tokens": 200}, O)
    assert cli.resumen()["costo_usd"] == pytest.approx(esperado)
    assert p.gastado == pytest.approx(esperado) and p.en_vuelo == pytest.approx(0)
    assert p.llamadas[0]["modelo"] == O and p.gastado_agente["filtro"] == pytest.approx(esperado)


def test_presupuesto_se_detiene_antes_de_superar_el_tope():
    p = R.Presupuesto(0.05)
    kw = dict(model=O, max_tokens=16000, system=[{"type": "text", "text": "s"}], messages=[{"role": "user", "content": "u"}])
    cli = R.ClienteMedido(ClienteFalso([{"ok": 1}]), p, "filtro")
    with pytest.raises(R.PresupuestoAgotado):
        cli.create(**kw)           # peor caso 0,32 USD > tope 0,05: no se llama
    assert cli.base.llamadas == [] and p.gastado == 0 and "filtro" in p.agotado


def test_tope_por_agente():
    p = R.Presupuesto(10.0, {"filtro": 0.001})
    cli = R.ClienteMedido(ClienteFalso([{"ok": 1}]), p, "filtro")
    with pytest.raises(R.PresupuestoAgotado):
        cli.create(model=H, max_tokens=4000, system="s", messages=[{"role": "user", "content": "u" * 100}])
    otro = R.ClienteMedido(ClienteFalso([{"ok": 1}]), p, "explorador")
    otro.create(model=H, max_tokens=4000, system="s", messages=[{"role": "user", "content": "u"}])


def test_unidad_omitida_por_presupuesto():
    p = R.Presupuesto(0.0001)
    ctx = R.Ctx(p, True, None)
    u = R.unidad(ctx, "filtro", "x", lambda cli: cli.create(model=O, max_tokens=5000, system="s", messages=[]) and (True, {}),
                 fakes=[{"a": 1}])
    assert u["omitida"] is True and u["ok"] is None and u["costo_usd"] == 0


def test_unidad_detecta_modelo_distinto_del_forzado():
    p = R.Presupuesto(10.0)
    ctx = R.Ctx(p, True, None)

    def fn(cli):
        cli.create(model=O, max_tokens=100, system="s", messages=[])
        return True, {}
    u = R.unidad(ctx, "filtro", "x", fn, fakes=[{"a": 1}], esperados={H})
    assert u["ok"] is False and "modelo distinto" in u["error"]


# ------------------------------------------------------------------ métricas puras
def test_metrica_filtro_kappa_y_consistencia():
    casos = [{"id": "a", "esperado": {"pasa": True}}, {"id": "b", "esperado": {"pasa": False}}]

    def u(cid, k, pasa, esp, total=8):
        return {"id": f"{cid}#{k}", "omitida": False, "error": None,
                "detalle": {"pasa": pasa, "esperado_pasa": esp, "total": total, "total_en_rango": True}}
    us = [u("a", 1, True, True), u("a", 2, True, True), u("b", 1, False, False), u("b", 2, True, False)]
    m = R.metrica_filtro(us, casos)
    assert m["n_pares"] == 4 and m["valor"] == pytest.approx(0.5) and m["consistencia_casos"] == "1/2"


def test_metricas_simulador_sobre_trazas_existentes():
    trazas = json.loads(R.TRAZAS_SINRED.read_text(encoding="utf-8"))
    m = R.metricas_simulador(trazas)
    assert m["n_corridas"] == 6 and m["pct_validan"] == 1.0
    assert m["n_N1"] == 2 and 0 <= m["pct_pitagoras"] <= 1


def test_evaluador_opus_reutilizado_no_gasta_y_reporta_kappa_humanas():
    c = R._evaluador_opus_reutilizado(R._referencias())
    assert c["estado"] == "reutilizada" and c["costo_usd"] == 0.0 and c["costo_reutilizado_usd"] > 0
    m = c["metrica"]
    assert len(m["kappa_por_corrida"]) == 3 and all(k >= 0.7 for k in m["kappa_por_corrida"])
    assert m["kappa_humanas"] < 0.7 and c["pasa"] is True      # la advertencia de CP1: humanas < 0,7


def test_tarea_a_entrada_evaluador_no_incluye_task_space():
    from conftest import cargar_ejemplo
    t = cargar_ejemplo("tarea")
    e = R.tarea_a_entrada_evaluador(t)
    assert set(e) == {"titulo", "nivel_declarado", "forma_texto", "texto", "recursos", "mapa_ciclo"}
    assert "reference_solution" not in json.dumps(e) and t["estudiante"]["enunciado_es"] in e["texto"]


# ------------------------------------------------------------------ forma de la matriz (corrida completa sin red)
@pytest.fixture(scope="module")
def corrida_sinred(tmp_path_factory):
    d = tmp_path_factory.mktemp("matriz")
    rc = R.main(["--sin-red", "--dir", str(d), "--sin-tests-bibliotecario"])
    assert rc == 0
    base = d / "matriz_2026-10-20_sinred"
    return json.loads(base.with_suffix(".json").read_text(encoding="utf-8")), base.with_suffix(".md").read_text(encoding="utf-8"), d


def test_matriz_cubre_9_agentes_x_3_modelos(corrida_sinred):
    m, md, _ = corrida_sinred
    assert list(m["celdas"]) == R.AGENTES
    for a, cs in m["celdas"].items():
        assert [c["modelo"] for c in cs] == [H, S, O]
        for c in cs:
            assert {"estado", "metrica", "pasa", "costo_usd", "latencia_media_s", "costo_por_unidad_usd"} <= set(c)
    assert set(m["recomendaciones"]) == set(R.AGENTES)
    for a in R.AGENTES:
        assert a in md
    assert "CORRIDA SIN RED" in md and "Recomendación de modelo por agente" in md


def test_matriz_registra_costo_total_igual_a_la_suma_de_llamadas(corrida_sinred):
    m, md, _ = corrida_sinred
    c = m["costo"]
    assert c["total_usd"] > 0 and c["total_usd"] <= c["tope_usd"] == 12.0
    assert c["total_usd"] == pytest.approx(sum(c["por_agente_modelo_usd"].values()), abs=1e-4)
    celdas = sum(x["costo_usd"] + x["costo_auxiliar_usd"] for cs in m["celdas"].values() for x in cs)
    assert c["total_usd"] == pytest.approx(celdas, abs=1e-4)
    assert f"{c['total_usd']:.4f}".replace(".", ",") in md
    assert c["precios_usd_mtok"][O]["output"] == 20.0


def test_evaluador_opus_se_reutiliza_y_los_demas_no_llaman_a_opus_sin_motivo(corrida_sinred):
    m, _, _ = corrida_sinred
    ev = {c["modelo"]: c for c in m["celdas"]["evaluador"]}
    assert ev[O]["estado"] == "reutilizada" and ev[O]["n_llamadas"] == 0
    assert ev[H]["n_unidades"] == ev[S]["n_unidades"] == 9
    for c in m["celdas"]["filtro"]:
        assert c["n_unidades"] == 15            # 5 casos x 3 corridas


def test_cada_celda_usa_solo_el_modelo_forzado(corrida_sinred):
    m, _, _ = corrida_sinred
    for a in ("explorador", "filtro", "evaluador", "redactor", "ilustrador", "verificador"):
        for c in m["celdas"][a]:
            if c["estado"] != "reutilizada":
                assert set(c["modelos_solicitados"]) <= {c["modelo"]}, (a, c["modelo"])


def test_reanudar_reutiliza_datos_guardados(corrida_sinred):
    m, _, d = corrida_sinred
    rc = R.main(["--sin-red", "--dir", str(d), "--sin-tests-bibliotecario", "--reanudar"])
    assert rc == 0
    m2 = json.loads((d / "matriz_2026-10-20_sinred.json").read_text(encoding="utf-8"))
    assert m2["costo"]["total_usd"] == pytest.approx(m["costo"]["total_usd"], abs=1e-4)
    assert set(m2["meta"]["reanudados"]) == set(R.AGENTES)


def test_tope_bajo_deja_celdas_sin_correr_y_nunca_lo_supera(tmp_path):
    rc = R.main(["--sin-red", "--dir", str(tmp_path), "--agentes", "filtro,redactor", "--tope", "0.05",
                 "--sin-tests-bibliotecario"])
    assert rc == 0
    m = json.loads((tmp_path / "matriz_2026-10-20_sinred.json").read_text(encoding="utf-8"))
    assert m["costo"]["total_usd"] <= 0.05
    assert m["celdas_sin_correr"], "con un tope tan bajo deben quedar celdas sin correr"
    s = m["celdas_sin_correr"][0]
    assert {"agente", "modelo", "unidades_sin_correr", "motivo"} <= set(s)
    assert "Celdas no corridas" in (tmp_path / "matriz_2026-10-20_sinred.md").read_text(encoding="utf-8")


def test_alias_de_modelos_y_error_de_modelo_desconocido():
    assert R.resolver_modelos("opus,haiku") == [H, O]
    with pytest.raises(SystemExit):
        R.resolver_modelos("gpt-4")


def test_completar_rehace_solo_lo_pendiente_y_no_duplica_el_gasto(tmp_path):
    R.main(["--sin-red", "--dir", str(tmp_path), "--agentes", "filtro", "--tope", "0.12", "--sin-tests-bibliotecario"])
    p = tmp_path / "matriz_2026-10-20_sinred.json"
    m1 = json.loads(p.read_text(encoding="utf-8"))
    assert m1["celdas_sin_correr"]
    gasto1 = m1["costo"]["total_usd"]
    R.main(["--sin-red", "--dir", str(tmp_path), "--agentes", "filtro", "--tope", "12", "--completar",
            "--sin-tests-bibliotecario"])
    m2 = json.loads(p.read_text(encoding="utf-8"))
    assert not m2["celdas_sin_correr"] and m2["meta"]["completados"] == ["filtro"]
    llamadas = sum(c["n_llamadas"] for c in m2["celdas"]["filtro"])
    assert llamadas == 45                                   # 3 modelos x 5 casos x 3 corridas, ninguna repetida
    unico = sum(c["costo_usd"] for c in m2["celdas"]["filtro"])
    assert m2["costo"]["total_usd"] == pytest.approx(unico, abs=1e-4) and m2["costo"]["total_usd"] >= gasto1


def test_rehacer_cuenta_el_gasto_descartado(tmp_path):
    R.main(["--sin-red", "--dir", str(tmp_path), "--agentes", "explorador", "--sin-tests-bibliotecario"])
    p = tmp_path / "matriz_2026-10-20_sinred.json"
    g1 = json.loads(p.read_text(encoding="utf-8"))["costo"]["total_usd"]
    R.main(["--sin-red", "--dir", str(tmp_path), "--agentes", "explorador", "--rehacer", "explorador",
            "--sin-tests-bibliotecario"])
    m = json.loads(p.read_text(encoding="utf-8"))
    assert m["costo"]["descartado_usd"] == pytest.approx(g1, abs=1e-4)
    assert m["costo"]["total_usd"] == pytest.approx(2 * g1, abs=1e-4)
