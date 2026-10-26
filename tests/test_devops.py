"""Fase 5 (devops): tope al 90 % en el ciclo, noticia de prueba para Actions, fusión del gasto entre
ramas, hooks de invariantes (.claude/hooks/otm_hook.py) y forma de los workflows. Sin red."""
import copy
import importlib.util
import json
import re

import pytest
import yaml

from conftest import RAIZ, cargar_ejemplo
from pipeline import ciclo as C
from pipeline import gasto_ramas
from pipeline import invariantes as inv
from pipeline.llm import ClienteFalso, config, costo_usd, modelo_de
from test_ciclo import OK_23, disenar_falso, rub, rutas  # noqa: F401  (fixture `rutas`)

NOTICIA_PRUEBA = RAIZ / "evals" / "casos" / "ciclo" / "noticia_prueba_actions.json"


def _hook():
    spec = importlib.util.spec_from_file_location("otm_hook", RAIZ / ".claude" / "hooks" / "otm_hook.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


H = _hook()


# =========================================================================== tope al 90 %
def _ciclo_con_previo(rutas, previo_usd, tope=100.0, n_evals=6):
    C.registrar_gasto_semana(rutas.gasto_semanal, C.semana_iso(), "previo", previo_usd)
    cli = ClienteFalso([rub(OK_23)] * n_evals)
    c = C.Ciclo(agentes=C.Agentes(disenar=disenar_falso(2)), rutas=rutas, cliente=cli, tope_semanal_usd=tope,
                salida=lambda s: None)
    return c, cli


def test_el_ciclo_se_detiene_al_90_por_ciento_del_tope(rutas):
    usd = costo_usd({"input_tokens": 1000, "output_tokens": 200}, modelo_de("evaluador"))
    assert config()["fraccion_detencion"] == 0.9
    c, cli = _ciclo_con_previo(rutas, 90.0 - 1.5 * usd)     # caben 2 llamadas bajo el 90 %, la 3.ª no
    reg = c.correr(noticias=[cargar_ejemplo("noticia")], max_tareas=1, nivel="S")
    assert reg["parametros"]["limite_usd"] == pytest.approx(90.0)
    assert reg["detenido_por_tope"] is True
    assert len(cli.llamadas) == 2
    assert reg["gasto"]["semana_usd"] >= 90.0
    # el gasto de este ciclo quedó persistido para que el siguiente lo vea
    assert C.gasto_semana(rutas.gasto_semanal, C.semana_iso()) == pytest.approx(90.0 - 1.5 * usd + 2 * usd)


def test_por_debajo_del_90_por_ciento_el_ciclo_no_se_detiene(rutas):
    c, cli = _ciclo_con_previo(rutas, 10.0, tope=100.0, n_evals=3)
    reg = c.correr(noticias=[cargar_ejemplo("noticia")], max_tareas=1, nivel="S")
    assert reg["detenido_por_tope"] is False
    assert reg["parametros"]["limite_usd"] == pytest.approx(90.0)


def test_con_el_tope_ya_consumido_no_hay_ninguna_llamada(rutas):
    c, cli = _ciclo_con_previo(rutas, 90.0)
    reg = c.correr(noticias=[cargar_ejemplo("noticia")], max_tareas=1, nivel="S")
    assert reg["detenido_por_tope"] is True and cli.llamadas == []


def test_presupuesto_de_ciclo_manda_si_es_menor_que_el_90(rutas):
    C.registrar_gasto_semana(rutas.gasto_semanal, C.semana_iso(), "previo", 27.0)
    c = C.Ciclo(rutas=rutas, cliente=ClienteFalso([]), presupuesto_ciclo_usd=2.0, tope_semanal_usd=35.0)
    assert c.contador.limite_usd == pytest.approx(29.0)   # 27 + 2, por debajo de 0,9 × 35 = 31,5


# =========================================================================== noticia de prueba
def test_noticia_de_prueba_valida_contra_el_contrato():
    n = json.loads(NOTICIA_PRUEBA.read_text(encoding="utf-8"))
    r = inv.validar_contra_esquema(n, "noticia")
    assert r, r.errores
    assert C._leer_noticias([str(NOTICIA_PRUEBA)]) == [n]
    assert len(n["resumen_propio"].split()) <= 80
    assert all(c["localizador"] for c in n["cifras"])                      # invariante 4
    assert H.chequear(NOTICIA_PRUEBA.relative_to(RAIZ).as_posix(), NOTICIA_PRUEBA.read_bytes()) == []


# =========================================================================== gasto entre ramas
def test_fusion_de_gasto_suma_solo_ciclos_desconocidos():
    base = {"semanas": {"2026-W43": {"usd": 10.0, "ciclos": [{"ciclo_id": "a", "usd": 10.0}]}}}
    rama = {"semanas": {"2026-W43": {"usd": 12.5, "ciclos": [{"ciclo_id": "a", "usd": 10.0},
                                                             {"ciclo_id": "b", "usd": 2.5}]},
                        "2026-W44": {"usd": 1.0, "ciclos": [{"ciclo_id": "c", "usd": 1.0}]}}}
    antes = copy.deepcopy(base)
    res, agregados = gasto_ramas.fusionar(base, rama, rama)
    assert base == antes
    assert res["semanas"]["2026-W43"]["usd"] == pytest.approx(12.5)
    assert res["semanas"]["2026-W44"]["usd"] == pytest.approx(1.0)
    assert agregados == ["2026-W43/b", "2026-W44/c"]


# =========================================================================== hooks
def test_hook_repo_sin_violaciones():
    assert H.modo_repo() == 0


# Los valores de prueba se arman por partes para que este archivo no dispare el escaneo de secretos.
@pytest.mark.parametrize("texto", [
    "ANTHROPIC_API_KEY=sk-ant-" + "api03-" + "A" * 30,
    "token github_" + "pat_" + "B" * 30,
    "postgresql://" + "postgres:" + "ContrasenaReal123" + "@db.xyz.supabase.co:5432/postgres",
    "sb_" + "secret_" + "C" * 25,
    "eyJ" + "a" * 25 + ".eyJ" + "b" * 25 + "." + "c" * 25,
])
def test_hook_invariante_7_detecta_secretos(texto):
    errores = H.chequear("docs/x.md", texto)
    assert errores and "Invariante 7" in errores[0] and texto not in errores[0]


def test_hook_invariante_7_no_marca_marcadores():
    assert H.chequear("docs/x.md", "postgresql://postgres:***@host/db y postgresql://u:$PASS@h/db") == []


def test_hook_invariante_3_literal_y_rutas_de_texto():
    cuerpo = " ".join(f"palabra{i}" for i in range(40))
    texto = "Resumen propio. " + " ".join(f"palabra{i}" for i in range(5, 5 + 26)) + " fin."
    assert any("Invariante 3" in e for e in H.chequear("tareas/x.md", texto, noticias=[("n.txt", cuerpo)]))
    corto = " ".join(f"palabra{i}" for i in range(5, 5 + 25))
    assert H.chequear("tareas/x.md", corto, noticias=[("n.txt", cuerpo)]) == []
    assert any("Invariante 3" in e for e in H.chequear("tareas/texto_noticia_x.txt", "hola"))


def _eval_con_total(total_bajo: bool, ceros=()):
    ev = cargar_ejemplo("evaluacion")
    crit = ev["rub01"]["criterios"]
    for k in crit:
        crit[k]["puntaje"] = 2
    if total_bajo:
        for k in list(crit)[:5]:
            crit[k]["puntaje"] = 1
    for k in ceros:
        crit[k]["puntaje"] = 0
    ev["rub01"]["total"] = sum(c["puntaje"] for c in crit.values())
    ev["rub01"]["mejoras"] = [{"criterio": k, "mejora_minima": "x"} for k, c in crit.items() if c["puntaje"] < 2]
    return ev


def test_hook_invariante_2_en_evaluacion_publicada(monkeypatch):
    tarea = cargar_ejemplo("tarea")
    tarea["estado"] = "revisada"
    monkeypatch.setattr(H, "_hermano", lambda rel, nombre: tarea)
    rel = "tareas/2026-10/x/evaluacion_v1.0_2026-10-20.json"
    assert any("Invariante 2" in e for e in H.chequear_json(rel, _eval_con_total(True), estricto=True))
    primero = next(iter(cargar_ejemplo("evaluacion")["rub01"]["criterios"]))
    assert any("Invariante 2" in e for e in H.chequear_json(rel, _eval_con_total(False, ceros=[primero]), estricto=True))
    assert H.chequear_json(rel, _eval_con_total(False), estricto=True) == []
    tarea["estado"] = "evaluada"     # en evaluada el umbral no se exige (la iteración sigue)
    assert H.chequear_json(rel, _eval_con_total(True), estricto=True) == []


def test_hook_invariantes_1_y_8_en_evaluacion():
    ev = cargar_ejemplo("evaluacion")
    del ev["reproducibilidad"]["version_MED01"]
    errores = H.chequear_json("pipeline/state/trabajo/x/evaluacion.json", ev, estricto=False)
    assert any("Invariante 1" in e for e in errores)


def test_hook_invariante_5_escenario_sin_corrida(monkeypatch):
    guia, trazas = cargar_ejemplo("guia"), cargar_ejemplo("trazas_resumen")
    guia["tarea_id"] = trazas["tarea_id"]
    monkeypatch.setattr(H, "_hermano", lambda rel, nombre: trazas)
    rel = "tareas/2026-10/x/guia_v1.0_2026-10-20.json"
    guia["escenarios"][0]["corridas"] = ["inexistente"]
    errores = H.chequear_json(rel, guia, estricto=True)
    assert any("Invariante 5" in e or "Invariante 1" in e for e in errores)


def test_hook_invariante_6_aislamiento(monkeypatch):
    tarea = cargar_ejemplo("tarea")
    assert H.chequear_json("pipeline/state/trabajo/x/tarea.json", tarea, estricto=False) == []
    monkeypatch.setattr(inv, "vista_estudiante", lambda t: {"enunciado_es": "x", "task_space": {}})
    errores = H.chequear_json("pipeline/state/trabajo/x/tarea.json", tarea, estricto=False)
    assert any("Invariante 6" in e for e in errores)


def test_hook_pretool_bloquea_insumos_y_secretos(tmp_path):
    insumo = next((RAIZ / "insumos").glob("GOB01_*.md"))
    ev = {"tool_name": "Edit", "tool_input": {"file_path": str(insumo), "old_string": "a", "new_string": "b"}}
    assert H.modo_pretool(ev) == 2
    nuevo = {"tool_name": "Write", "tool_input": {"file_path": str(RAIZ / "insumos" / "nuevo_v1.0_2026-10-21.md"),
                                                   "content": "ok"}}
    assert H.modo_pretool(nuevo) == 0                                     # una versión nueva sí
    clave = "sk-ant-" + "Z" * 30
    sec = {"tool_name": "Write", "tool_input": {"file_path": str(RAIZ / "docs" / "x.md"), "content": "k=" + clave}}
    assert H.modo_pretool(sec) == 2
    ajeno = {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / "sk.md"), "content": clave}}
    assert H.modo_pretool(ajeno) == 0
    assert H.modo_pretool({"tool_name": "Bash", "tool_input": {"command": "ls"}}) == 0


def test_settings_registra_el_hook_pretool():
    cfg = json.loads((RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8"))
    cmd = cfg["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    assert "otm_hook.py" in cmd and "pretool" in cmd
    assert (RAIZ / ".githooks" / "pre-commit").exists()


# =========================================================================== workflows
def _wf(nombre):
    d = yaml.safe_load((RAIZ / ".github" / "workflows" / nombre).read_text(encoding="utf-8"))
    d["on"] = d.pop(True, d.get("on"))      # PyYAML lee `on` como True
    return d


@pytest.mark.parametrize("nombre", ["ci.yml", "deploy.yml", "semanal.yml", "tramo_b.yml", "publicar.yml", "publicada.yml"])
def test_workflows_son_yaml_validos(nombre):
    assert _wf(nombre)["jobs"]


def test_semanal_cron_lunes_y_dispatch():
    d = _wf("semanal.yml")
    assert d["on"]["schedule"][0]["cron"] == "17 9 * * 1"
    entradas = d["on"]["workflow_dispatch"]["inputs"]
    assert {"max_tareas", "presupuesto_ciclo", "noticia_prueba"} <= set(entradas)
    assert d["concurrency"]["cancel-in-progress"] is False


def test_tramo_b_solo_manual_con_revisor_y_guarda_de_secrets():
    d = _wf("tramo_b.yml")
    assert set(d["on"]) == {"workflow_dispatch"}
    assert d["on"]["workflow_dispatch"]["inputs"]["revisor"]["required"] is True
    texto = (RAIZ / ".github" / "workflows" / "tramo_b.yml").read_text(encoding="utf-8")
    assert "SIM_REPO" in texto and "SIM_REPO_TOKEN" in texto


def test_tramo_b_solo_comprobar_no_usa_api_ni_escribe():
    d = _wf("tramo_b.yml")
    e = d["on"]["workflow_dispatch"]["inputs"]["solo_comprobar"]
    assert e["type"] == "boolean" and e["default"] is False
    assert "solo_comprobar" in d["jobs"]["tramo_b"]["if"] and "!inputs.solo_comprobar" in d["jobs"]["tramo_b"]["if"]
    texto = json.dumps(d["jobs"]["comprobar"])
    assert "ANTHROPIC_API_KEY" not in texto and "GH_TOKEN" not in texto and "pipeline.ciclo" not in texto
    assert "simulacion/sim.py" in texto and "insumos" in texto and "cargar_sim" in texto


def test_publicar_solo_manual_con_revisor_dry_run_y_pr():
    d = _wf("publicar.yml")
    assert set(d["on"]) == {"workflow_dispatch"}
    e = d["on"]["workflow_dispatch"]["inputs"]
    assert e["revisor"]["required"] is True and e["ids"]["required"] is True
    assert e["dry_run"]["type"] == "boolean" and e["dry_run"]["default"] is False
    texto = (RAIZ / ".github" / "workflows" / "publicar.yml").read_text(encoding="utf-8")
    assert "pipeline.publicar" in texto and "gh pr create" in texto
    assert "ANTHROPIC_API_KEY" not in json.dumps(d["jobs"])      # no llama a ningún modelo
    pasos = {s.get("name"): s for s in d["jobs"]["publicar"]["steps"]}
    assert pasos["Push y PR"]["if"] == "${{ !inputs.dry_run }}"


def test_workflows_no_incrustan_secretos_ni_los_imprimen():
    for p in (RAIZ / ".github" / "workflows").glob("*.yml"):
        t = p.read_text(encoding="utf-8")
        assert H.chequear_texto(f".github/workflows/{p.name}", t, []) == []
        assert not re.search(r"echo[^\n]*\$\{\{\s*secrets\.", t), p.name
        assert not re.search(r"echo[^\n]*\$\{?(SUPABASE_DB_URL|ANTHROPIC_API_KEY|GH_TOKEN|SUPABASE_SERVICE_KEY)\b", re.sub(r".*::add-mask::.*", "", t)), p.name  # add-mask registra el valor, no lo imprime


def test_deploy_usa_pages_y_no_pone_la_clave_de_servicio_en_el_build():
    d = _wf("deploy.yml")
    assert d["permissions"]["pages"] == "write" and d["permissions"]["id-token"] == "write"
    for s in d["jobs"]["sitio"]["steps"]:
        if "build" in json.dumps(s):
            assert "SUPABASE_SERVICE_KEY" not in s.get("env", {})
    t = (RAIZ / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
    assert "PUBLIC_SUPABASE_ANON_KEY" in t and "actions/deploy-pages" in t


def test_marcas_de_ruta_son_relativas_al_repo_y_se_resuelven():
    dentro = RAIZ / "pipeline" / "state" / "trabajo" / "x" / "evaluacion_corridas.json"
    assert C._ruta_marca(dentro) == "pipeline/state/trabajo/x/evaluacion_corridas.json"
    assert C._ruta_de_marca(C._ruta_marca(dentro)) == dentro
    assert C._ruta_marca(None) == ""
    d = json.loads(NOTICIA_PRUEBA.read_text(encoding="utf-8"))
    assert d["medio_id"] == "diario_ficticio" and "ficticio" in d["medio"].lower()
