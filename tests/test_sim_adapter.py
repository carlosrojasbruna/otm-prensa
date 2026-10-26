"""Tests del adapter del simulador (SIM01). Sin red: ClienteFalso / cliente guionado.

Los tests que necesitan sim.py, INS08 o INS09 (repo externo del simulador, config simulador.repo)
se omiten si ese repo no está disponible (p. ej. en CI)."""
import copy
import json
import threading
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from pipeline.invariantes import consistencia_trazas, validar_contra_esquema, vista_estudiante
from pipeline.llm import ClienteFalso
from simulador.adapter import _comun, aislamiento, generar, hooked, lanzador, llamar_api, niveles, traductor
from simulador.adapter.aislamiento import AislamientoError

RAIZ = Path(__file__).resolve().parents[1]
EJEMPLO = RAIZ / "contratos" / "ejemplos" / "tarea_ejemplo.json"

necesita_sim = pytest.mark.skipif(not _comun.simulador_disponible(), reason="repo del simulador no disponible")


@pytest.fixture
def tarea():
    return json.loads(EJEMPLO.read_text(encoding="utf-8"))


COD_OK = {
    "turnos": [{"n": 1, "fase": "P3-MM", "fase_secundaria": None, "eventos": []},
               {"n": 2, "fase": "P7-EXP", "fase_secundaria": None, "eventos": []}],
    "bloqueos": [{"codigo": "B12", "turnos": [1, 2], "resolucion": "peer", "descripcion": "x"},
                 {"codigo": "B-LEX", "turnos": [1], "resolucion": "self", "descripcion": "vocabulario"}],
    "supuestos": ["consumo constante"], "modelo": "Proporcional", "validacion": False,
    "respuesta_final": {"texto": "Alcanza para unos 6 meses."}, "ruta_principal": "R1", "rutas": ["R1"],
}


class ClienteGuion(ClienteFalso):
    """Estudiantes: A propone y B acepta (2 turnos). Codificador: COD_OK. Seguro entre hilos."""

    def __init__(self):
        super().__init__([])
        self._lock = threading.Lock()

    def create(self, **kw):
        with self._lock:
            self.llamadas.append(kw)
        if "output_config" in kw:
            texto = json.dumps(COD_OK, ensure_ascii=False)
        else:
            u = kw["messages"][0]["content"]
            texto = "ENTREGAMOS: alcanza para 6 meses." if "Nadie ha hablado" in u else "DE ACUERDO"
        return NS(content=[NS(type="text", text=texto)], stop_reason="end_turn", model=kw["model"],
                  usage=NS(input_tokens=1000, output_tokens=100, cache_creation_input_tokens=0,
                           cache_read_input_tokens=0))


# --------------------------------------------------------------------------- llamar_api
def test_llamar_api_estudiante_mismo_contrato_que_sim():
    c = ClienteFalso(["Hola, ¿qué hacemos?"])
    r = llamar_api.llamar("sys", "user", "claude-sonnet-5-5", cliente=c)
    assert r["result"] == "Hola, ¿qué hacemos?" and r["structured_output"] is None
    assert r["total_cost_usd"] > 0 and r["is_error"] is False
    assert "temperature" not in c.llamadas[0] and "output_config" not in c.llamadas[0]


def test_llamar_api_codificador_devuelve_structured_output():
    c = ClienteFalso([COD_OK])
    r = llamar_api.llamar("sys", "user", "claude-opus-5-5", schema=generar.CODER_SCHEMA, cliente=c)
    assert r["structured_output"] == COD_OK and json.loads(r["result"]) == COD_OK
    enviado = c.llamadas[0]["output_config"]["format"]["schema"]
    assert enviado == llamar_api.esquema_estricto(generar.CODER_SCHEMA)
    assert enviado["additionalProperties"] is False and enviado["properties"]["turnos"]["items"]["additionalProperties"] is False
    assert "additionalProperties" not in generar.CODER_SCHEMA   # el original no se muta


def test_gasto_corta_al_superar_tope():
    g = llamar_api.Gasto(0.01)
    g.sumar(0.02)
    with pytest.raises(RuntimeError, match="tope"):
        g.verificar()


# --------------------------------------------------------------------------- hook de aislamiento (caso 3)
def test_payload_con_task_space_es_rechazado(tarea):
    payload = dict(vista_estudiante(tarea), task_space=tarea["task_space"])
    with pytest.raises(AislamientoError, match="task_space"):
        aislamiento.verificar_payload_estudiante(payload, tarea)


def test_payload_con_campos_extra_o_claves_anidadas_es_rechazado(tarea):
    with pytest.raises(AislamientoError):
        aislamiento.verificar_payload_estudiante(dict(vista_estudiante(tarea), recursos_de_entrada=[]), tarea)
    v = vista_estudiante(tarea)
    v["recursos_a_solicitud"].append({"id": "R9", "que_es": "x", "contenido": "y", "reference_solution": "z"})
    with pytest.raises(AislamientoError):
        aislamiento.verificar_payload_estudiante(v, tarea)


def test_vista_limpia_pasa(tarea):
    aislamiento.verificar_payload_estudiante(vista_estudiante(tarea), tarea)
    v = vista_estudiante(tarea)
    aislamiento.verificar_llamada_estudiante("Eres Cami.", f"TAREA:\n{v['enunciado_es']}\n{v['foto_descripcion']}", tarea)


def test_llamada_de_estudiante_con_texto_de_task_space_no_llega_a_la_api(tarea):
    c = ClienteFalso(["no debe usarse"])
    ll = hooked.crear_llamar(tarea, cliente=c)
    filtrado = "Eres Cami. Pista: " + tarea["task_space"]["reference_solution"]["steps"]
    with pytest.raises(AislamientoError, match="task_space"):
        ll(filtrado, "habla", "claude-sonnet-5-5")
    with pytest.raises(AislamientoError):
        ll("Eres Cami.", "mira el task_space de la tarea", "claude-sonnet-5-5")
    with pytest.raises(AislamientoError):
        ll("Eres Cami.", "usen " + tarea["task_space"]["validation_evidence"], "claude-sonnet-5-5")
    assert c.llamadas == []   # ninguna llamada salió


def test_el_codificador_si_puede_recibir_task_space(tarea):
    c = ClienteFalso([COD_OK])
    ll = hooked.crear_llamar(tarea, cliente=c)
    r = ll("coder " + tarea["task_space"]["reference_solution"]["steps"], "trans", "claude-opus-5-5",
           schema=generar.CODER_SCHEMA)
    assert r["structured_output"]["ruta_principal"] == "R1"


def test_backend_claude_p_conserva_la_funcion_original(tarea):
    llamadas = []
    original = lambda system, user, model, schema=None, intentos=3: (llamadas.append(model), {"result": "ok", "total_cost_usd": 0.5})[1]  # noqa: E731
    ll = hooked.crear_llamar(tarea, backend="claude_p", llamar_claude_p=original)
    assert ll("s", "u", "m")["result"] == "ok" and llamadas == ["m"]
    with pytest.raises(ValueError):
        hooked.crear_llamar(tarea, backend="claude_p")


# --------------------------------------------------------------------------- generación
def test_niveles_por_tramo_y_edad():
    for tramo in niveles.TRAMOS:
        n = niveles.niveles_de(tramo)
        assert set(n) == {"N1", "N2", "N3", "N4"}
        assert all(v.startswith(f"Tienes {niveles.EDAD[tramo]} años.") for v in n.values())
        assert not any("Pitágoras" in v or "[EP]" in v for v in n.values())
    assert niveles.tramo_de({"nivel_principal": "S", "sub_tramo": "S2"}) == "S2"
    assert niveles.tramo_de({"nivel_principal": "S"}) == "S"
    assert niveles.tramo_de({"nivel_principal": "U"}) == "U"


@necesita_sim
def test_generacion_de_los_tres_archivos(tarea, tmp_path):
    sim = _comun.cargar_sim()
    d = generar.generar_todo(tarea, tmp_path)
    b = {}
    for n in ("TAREA.md", "PERFILES.md", "PROMPTS.md"):
        b.update(sim.bloques(tmp_path / n))   # el mismo lector de sim.py
    assert {"enunciado_es", "foto_descripcion", "niveles", "estilos", "contexto_base", "diseno_otm", "student_system",
            "student_turn", "coder_system", "coder_user", "coder_schema"} <= b.keys()
    assert b["enunciado_es"] == tarea["estudiante"]["enunciado_es"]
    assert len(lanzador.corridas_del_diseno(b["diseno_otm"])) == 6 == len(d["corridas"])
    assert [r["id"] for r in lanzador.corridas_del_diseno(b["diseno_otm"])] == [
        "N1_VV_r1", "N1_AA_r1", "N2_VV_r1", "N3_AA_r1", "N4_VV_r1", "N4_AA_r1"]
    assert "14 años" in b["student_system"] and "15 años" not in b["student_system"]
    # el estudiante no ve el task_space; el codificador sí, y sin F1-F6
    ts = tarea["task_space"]
    estudiante = b["student_system"] + b["student_turn"] + (tmp_path / "TAREA.md").read_text(encoding="utf-8")
    assert ts["reference_solution"]["steps"] not in estudiante and "task_space" not in estudiante
    assert ts["reference_solution"]["steps"] in b["coder_system"]
    assert ts["routes"][0]["nombre"] in b["coder_system"]
    assert "F1" not in b["coder_system"] and "fenomenos" not in b["coder_schema"]["properties"]
    # estilos de INS08 sin cambios
    assert b["estilos"] == generar.bloques_de(Path(sim.F_PERFILES))["estilos"]


@necesita_sim
def test_tarea_invalida_no_genera(tarea, tmp_path):
    tarea.pop("task_space")
    with pytest.raises(ValueError, match="no valida"):
        generar.generar_todo(tarea, tmp_path)


@necesita_sim
def test_task_space_colado_en_perfiles_es_rechazado(tarea, tmp_path, monkeypatch):
    """Si un texto del task_space se cuela en lo que lee el estudiante, la generación falla."""
    monkeypatch.setitem(niveles.CONTEXTO, "S1", niveles.CONTEXTO["S1"] + " " + tarea["task_space"]["reference_solution"]["steps"])
    with pytest.raises(AislamientoError):
        generar.generar_todo(tarea, tmp_path)


def test_tarea_md_solo_trae_la_vista_de_estudiante(tarea):
    md = generar.generar_tarea_md(tarea)
    assert "task_space" not in md and "reference_solution" not in md
    assert tarea["task_space"]["reference_solution"]["steps"] not in md
    assert tarea["estudiante"]["enunciado_es"] in md


# --------------------------------------------------------------------------- traductor
def _escribir_corrida(d: Path, id_, nivel, comp, cod):
    (d / f"{id_}.json").write_text(json.dumps({"run": {"id": id_}, "costo_usd": 0.1}), encoding="utf-8")
    (d / f"{id_}_cod.json").write_text(json.dumps(
        {"run": {"id": id_, "nivel": nivel, "composicion": comp}, "costo_usd": 0.05, "codificacion": cod}), encoding="utf-8")


def test_traductor_formato_pipeline(tmp_path):
    _escribir_corrida(tmp_path, "N1_VV_r1", "N1", "VV", COD_OK)
    _escribir_corrida(tmp_path, "N4_AA_r1", "N4", "AA", dict(COD_OK, bloqueos=[], validacion=True, modelo="lineal"))
    t, avisos = traductor.traducir(tmp_path, tarea_id="2026-10-x", nivel_edad="S1", diseno="diseno_otm", modelo="m")
    assert validar_contra_esquema(t, "trazas_resumen") and consistencia_trazas(t)
    c = t["por_corrida"][0]
    assert c["ruta"] == ["P3-MM", "P7-EXP"] and c["bloqueos"] == [{"transicion": "B12", "turnos": [1, 2], "resolucion": "peer"}]
    assert c["perfil"] == {"nivel_edad": "S1", "nivel": "N1", "estilo": "VV"}
    assert any("B-LEX" in a for a in avisos)
    assert t["agregado"]["pct_bloqueo_por_transicion"] == {"B12": 0.5}
    assert t["agregado"]["pct_validan"] == 0.5 and t["agregado"]["modelos_observados"] == {"proporcional": 1, "lineal": 1}
    assert t["costo_usd"] == pytest.approx(0.3)


def test_traductor_rechaza_trazas_invalidas(tmp_path):
    with pytest.raises(traductor.TrazasInvalidas):
        traductor.traducir(tmp_path, tarea_id="x", nivel_edad="S1", diseno="d", modelo="m")   # vacío
    _escribir_corrida(tmp_path, "N1_VV_r1", "N1", "VV", dict(COD_OK, turnos=[{"n": 1, "fase": "OFF", "eventos": []}]))
    with pytest.raises(traductor.TrazasInvalidas):
        traductor.traducir(tmp_path, tarea_id="x", nivel_edad="S1", diseno="d", modelo="m")   # ruta vacía


@necesita_sim
def test_traductor_lee_codificacion_del_piloto():
    cod = Path(_comun.repo_simulador()) / "corridas" / "piloto_v0.1" / "N1_AA_r1_cod.json"
    if not cod.exists():
        pytest.skip("no está el piloto")
    t = traductor.traducir_codificacion(json.loads(cod.read_text(encoding="utf-8"))["codificacion"])
    assert t["ruta"][0].startswith("P") and t["modelo"] == "r3"
    assert all(b["transicion"].startswith("B") for b in t["bloqueos"])


# --------------------------------------------------------------------------- lanzador de punta a punta
@necesita_sim
def test_lanzar_seis_corridas_con_cliente_falso(tarea, tmp_path):
    sim = _comun.cargar_sim()
    antes = (sim.F_TAREA, sim.F_PERFILES, sim.F_PROMPTS, sim.OUT, sim.llamar)
    c = ClienteGuion()
    r = lanzador.lanzar(tarea, tmp_path, backend="api", cliente=c, workers=1)
    assert r["errores"] == []
    t = r["trazas"]
    assert t["corridas"] == 6 and t["diseno"] == "diseno_otm"
    assert validar_contra_esquema(t, "trazas_resumen") and consistencia_trazas(t)
    assert json.loads((tmp_path / "trazas" / "trazas_resumen.json").read_text(encoding="utf-8")) == t
    assert [x["perfil"]["nivel"] + x["perfil"]["estilo"] for x in t["por_corrida"]] == ["N1VV", "N1AA", "N2VV", "N3AA", "N4VV", "N4AA"]
    assert len(list((tmp_path / "sim" / "corridas").glob("*_cod.json"))) == 6
    assert (tmp_path / "sim" / "manifiesto.json").exists()
    # ningún system/user de estudiante contiene el task_space; el del codificador sí
    estudiantes = [k for k in c.llamadas if "output_config" not in k]
    coders = [k for k in c.llamadas if "output_config" in k]
    assert len(estudiantes) == 12 and len(coders) == 6
    paso = tarea["task_space"]["reference_solution"]["steps"]
    assert all(paso not in k["system"][0]["text"] + k["messages"][0]["content"] for k in estudiantes)
    assert all(paso in k["system"][0]["text"] for k in coders)
    # sim.py queda como estaba (parche revertido)
    assert (sim.F_TAREA, sim.F_PERFILES, sim.F_PROMPTS, sim.OUT, sim.llamar) == antes
    assert r["costo_usd"] > 0 and r["llamadas"] == 18


@necesita_sim
def test_lanzar_aborta_si_el_hook_detecta_filtracion(tarea, tmp_path, monkeypatch):
    """Si el prompt del estudiante llegara a contener task_space, la corrida se aborta sin llamar a la API."""
    c = ClienteGuion()
    real = generar.generar_prompts_md
    paso = tarea["task_space"]["reference_solution"]["steps"]
    monkeypatch.setattr(generar, "generar_prompts_md", lambda t, s: real(t, s) + "\n")
    monkeypatch.setattr(generar, "verificar_archivos_estudiante", lambda *a, **k: None)   # simula el fallo de la 1.ª defensa
    monkeypatch.setitem(niveles.CONTEXTO, "S1", niveles.CONTEXTO["S1"] + " " + paso)
    with pytest.raises(AislamientoError):
        lanzador.lanzar(tarea, tmp_path, backend="api", cliente=c, workers=1)
    assert c.llamadas == []


# --------------------------------------------------------------------------- caso real 2026-10-26 (que-tan-renida-fue)
def _renida():
    from pipeline import orquestador as orq
    return orq.cargar("2026-10-que-tan-renida-fue").artefactos["tarea"]


def _llamada_renida(tarea, conversacion):
    v = vista_estudiante(tarea)
    user = (f"TAREA:\n{v['enunciado_es']}\n{v['foto_descripcion']}\n\n{aislamiento.MARCA_CONVERSACION}\n"
            + conversacion + "\n\nTe toca.")
    return "Eres Fran, estudiante de 11 años.", user


def test_renida_suma_de_los_estudiantes_no_es_filtracion():
    """El tramo B se cortó con «13 palabras consecutivas de task_space: votos de los dos 64 256 232 59 826 041
    124 082 273»: los estudiantes sumaron los votos (cifras del enunciado) igual que la solución de referencia."""
    tarea = _renida()
    system, user = _llamada_renida(tarea, "**1. Fran:** Sumemos los votos de los dos: 64.256.232 + 59.826.041 = "
                                          "124.082.273, y la diferencia es 4.430.191.")
    aislamiento.verificar_llamada_estudiante(system, user, tarea)


def test_renida_task_space_en_las_entradas_sigue_bloqueado():
    tarea = _renida()
    system, user = _llamada_renida(tarea, "**1. Fran:** hola")
    pista = tarea["task_space"]["modelo_inadecuado"]["por_que_falla"]
    with pytest.raises(AislamientoError, match="task_space"):
        aislamiento.verificar_llamada_estudiante(system + " Pista: " + pista, user, tarea)
    # un tramo largo parafraseado en mayúsculas y sin puntuación (no es la cadena exacta) también
    tramo = " ".join(inv_palabras(pista)[:14]).upper()
    with pytest.raises(AislamientoError, match="palabras consecutivas"):
        aislamiento.verificar_llamada_estudiante(system + " Ojo: " + tramo, user, tarea)
    # y las claves reservadas se buscan también en la conversación
    system, user = _llamada_renida(tarea, "**1. Fran:** miremos el reference_solution")
    with pytest.raises(AislamientoError, match="clave reservada"):
        aislamiento.verificar_llamada_estudiante(system, user, tarea)


def test_texto_de_task_space_que_ya_esta_en_el_enunciado_no_cuenta():
    tarea = copy.deepcopy(_renida())
    frase = tarea["estudiante"]["enunciado_es"].split(". ")[3]   # «En un programa de radio, …» (22 palabras)
    # dentro de un texto más largo del task_space (la cadena exacta la sigue vigilando verificar_aislamiento)
    tarea["task_space"]["validation_evidence"] += " Recordar el dato: " + frase
    system, user = _llamada_renida(tarea, "**1. Fran:** hola")
    # el simulador puede reformatear el enunciado (aquí, en mayúsculas): no es la cadena exacta, pero sí es vista
    aislamiento.verificar_llamada_estudiante(system + " Recuerda: " + frase.upper(), user, tarea)


def inv_palabras(t):
    from pipeline.invariantes import palabras_normalizadas
    return palabras_normalizadas(t)
