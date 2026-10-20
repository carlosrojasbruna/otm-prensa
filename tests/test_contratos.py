"""Contratos: cada ejemplo válido valida, cada inválido falla, y las invariantes puras se comportan."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from pipeline import invariantes as inv

RAIZ = Path(__file__).resolve().parents[1]
DIR_CONTRATOS = RAIZ / "contratos"
DIR_EJEMPLOS = DIR_CONTRATOS / "ejemplos"
CONTRATOS = list(inv.CONTRATOS)
REQUERIDOS = ["noticia", "tarea", "evaluacion", "trazas_resumen", "guia", "catalogo"]


def _leer(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _contrato_de_invalido(nombre_archivo: str) -> str:
    # el prefijo más largo gana (evaluacion_rub01 antes que evaluacion)
    for c in sorted(CONTRATOS, key=len, reverse=True):
        if nombre_archivo.startswith(c + "_"):
            return c
    raise AssertionError(f"inválido sin contrato reconocible: {nombre_archivo}")


INVALIDOS = sorted((DIR_EJEMPLOS / "invalidos").glob("*.json"))


# --------------------------------------------------------------------------- esquemas
def test_existen_los_contratos_requeridos():
    for c in REQUERIDOS + ["evaluacion_rub01"]:
        assert (DIR_CONTRATOS / f"{c}.schema.json").exists(), c


@pytest.mark.parametrize("contrato", CONTRATOS)
def test_esquema_es_draft_2020_12_valido(contrato):
    esquema = _leer(DIR_CONTRATOS / f"{contrato}.schema.json")
    assert esquema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert esquema["$id"] == inv.BASE_ID + f"{contrato}.schema.json"
    Draft202012Validator.check_schema(esquema)


@pytest.mark.parametrize("contrato", CONTRATOS)
def test_ejemplo_valido_valida(contrato):
    r = inv.validar_contra_esquema(_leer(DIR_EJEMPLOS / f"{contrato}_ejemplo.json"), contrato)
    assert r, r.errores


@pytest.mark.parametrize("contrato", REQUERIDOS + ["evaluacion_rub01"])
def test_cada_contrato_tiene_al_menos_un_invalido(contrato):
    assert any(_contrato_de_invalido(p.name) == contrato for p in INVALIDOS), contrato


@pytest.mark.parametrize("ruta", INVALIDOS, ids=[p.name for p in INVALIDOS])
def test_ejemplo_invalido_falla(ruta):
    r = inv.validar_contra_esquema(_leer(ruta), _contrato_de_invalido(ruta.name))
    assert not r
    assert r.errores


def test_fragmento_de_contrato(ejemplos):
    entrada = ejemplos["catalogo"]["tareas"][0]
    assert inv.validar_contra_esquema(entrada, "catalogo#/$defs/entrada")
    entrada.pop("licencia")
    assert not inv.validar_contra_esquema(entrada, "catalogo#/$defs/entrada")


def test_contrato_desconocido():
    with pytest.raises(KeyError):
        inv.validar_contra_esquema({}, "no_existe")


# --------------------------------------------------------------------------- RUB01 ligada al insumo
def test_ids_rub01_del_esquema_coinciden_con_el_insumo():
    rub = inv.cargar_rub01()
    esquema = _leer(DIR_CONTRATOS / "evaluacion_rub01.schema.json")
    ids_insumo = [c["id"] for c in rub["criterios"]]
    assert esquema["properties"]["criterios"]["required"] == ids_insumo
    assert esquema["$defs"]["criterio_id"]["enum"] == ids_insumo
    assert esquema["properties"]["version_rubrica"]["const"] == rub["version"]
    assert esquema["properties"]["total"]["maximum"] == rub["puntaje_maximo"]


def test_evaluacion_referencia_el_bloque_rub01(ejemplos):
    # el bloque rub01 del ejemplo completo valida solo y el ejemplo de rub01 es el mismo bloque
    assert inv.validar_contra_esquema(ejemplos["evaluacion"]["rub01"], "evaluacion_rub01")
    assert ejemplos["evaluacion"]["rub01"] == ejemplos["evaluacion_rub01"]


# --------------------------------------------------------------------------- invariante 2 (pura)
def _con_puntajes(evaluacion, puntajes: dict):
    rub = evaluacion["rub01"]
    for k, v in puntajes.items():
        rub["criterios"][k]["puntaje"] = v
    rub["total"] = sum(c["puntaje"] for c in rub["criterios"].values())
    rub["mejoras"] = [
        {"criterio": k, "mejora_minima": "mejora"} for k, c in rub["criterios"].items() if c["puntaje"] < 2
    ]
    return evaluacion


def test_umbral_leido_del_insumo():
    rub = inv.cargar_rub01("4.0")
    assert inv.umbral_rub01(rub) == (
        rub["umbral_publicacion_propuesto"]["total_min"],
        rub["umbral_publicacion_propuesto"]["ningun_criterio_en"],
    )


def test_umbral_cumple_con_23(ejemplos):
    r = inv.cumple_umbral_rub01(ejemplos["evaluacion"])
    assert r and r.detalle["total"] == 23
    assert inv.cumple_umbral_rub01(ejemplos["evaluacion_rub01"])  # también con el bloque solo


def test_umbral_falla_con_19(ejemplos):
    ev = _con_puntajes(ejemplos["evaluacion"], {"genuino": 1, "abierta": 1, "decisiones": 1, "realismo": 1, "validacion": 1})
    assert ev["rub01"]["total"] == 19
    r = inv.cumple_umbral_rub01(ev)
    assert not r
    assert any("< umbral" in e for e in r.errores)


def test_umbral_falla_con_criterio_en_0_aunque_total_alto(ejemplos):
    ev = _con_puntajes(ejemplos["evaluacion"], {"validacion": 2, "recursos": 0})
    assert ev["rub01"]["total"] == 22
    r = inv.cumple_umbral_rub01(ev)
    assert not r
    assert r.detalle["criterios_en_prohibido"] == ["recursos"]


def test_umbral_falla_si_total_declarado_no_cuadra(ejemplos):
    ev = ejemplos["evaluacion"]
    ev["rub01"]["total"] = 24
    assert not inv.cumple_umbral_rub01(ev)


def test_umbral_falla_si_rub01_no_valida(ejemplos):
    ev = ejemplos["evaluacion"]
    del ev["rub01"]["criterios"]["recursos"]
    assert not inv.cumple_umbral_rub01(ev)


def test_umbral_con_rubrica_inyectada(ejemplos):
    rub = json.loads(json.dumps(inv.cargar_rub01()))
    rub["umbral_publicacion_propuesto"]["total_min"] = 24
    assert not inv.cumple_umbral_rub01(ejemplos["evaluacion"], rubrica=rub)


def test_consistencia_rub01_exige_mejoras(ejemplos):
    rub = ejemplos["evaluacion_rub01"]
    rub["mejoras"] = []
    assert not inv.consistencia_rub01(rub)


# --------------------------------------------------------------------------- invariante 3 (pura)
FUENTE = " ".join(f"p{i}" for i in range(60))


def test_literal_25_palabras_permitido():
    texto = "inicio " + " ".join(f"p{i}" for i in range(10, 35)) + " fin"
    r = inv.cumple_limite_literal(texto, FUENTE)
    assert r and r.detalle["max_consecutivas"] == 25


def test_literal_26_palabras_bloqueado():
    texto = "inicio " + " ".join(f"p{i}" for i in range(10, 36)) + " fin"
    r = inv.cumple_limite_literal(texto, FUENTE)
    assert not r and r.detalle["max_consecutivas"] == 26


def test_literal_ignora_mayusculas_tildes_y_puntuacion():
    fuente = "El embalse está al 38 % de su capacidad, según la Dirección General de Aguas."
    texto = "el EMBALSE esta al 38% de su capacidad segun la direccion general de aguas"
    assert inv.max_palabras_consecutivas_comunes(texto, fuente)[0] == 14


def test_literal_detecta_copia_partida_entre_campos():
    a = " ".join(f"p{i}" for i in range(0, 15))
    b = " ".join(f"p{i}" for i in range(15, 30))
    assert not inv.cumple_limite_literal({"x": a, "y": [b]}, FUENTE)


def test_literal_ejemplos_no_copian_su_resumen_mas_alla_del_limite(ejemplos):
    # el resumen propio es el texto que más se parece a la noticia; sirve de humo
    assert inv.cumple_limite_literal(ejemplos["tarea"]["estudiante"], ejemplos["noticia"]["resumen_propio"])


# --------------------------------------------------------------------------- invariantes 5 y 6 (puras)
def test_escenarios_respaldados(ejemplos):
    assert inv.escenarios_respaldados(ejemplos["guia"], ejemplos["trazas_resumen"])
    ejemplos["guia"]["escenarios"][0]["corridas"] = ["N9_ZZ_r1"]
    assert not inv.escenarios_respaldados(ejemplos["guia"], ejemplos["trazas_resumen"])


def test_consistencia_trazas(ejemplos):
    assert inv.consistencia_trazas(ejemplos["trazas_resumen"])
    ejemplos["trazas_resumen"]["corridas"] = 12
    assert not inv.consistencia_trazas(ejemplos["trazas_resumen"])


def test_vista_estudiante_no_contiene_task_space(ejemplos):
    tarea = ejemplos["tarea"]
    vista = inv.vista_estudiante(tarea)
    assert set(vista) == set(inv.CAMPOS_ESTUDIANTE)
    assert inv.verificar_aislamiento(vista, tarea)
    assert "disponibilidad" not in vista["recursos_a_solicitud"][0]


def test_aislamiento_rechaza_task_space(ejemplos):
    tarea = ejemplos["tarea"]
    vista = inv.vista_estudiante(tarea)
    assert not inv.verificar_aislamiento({**vista, "task_space": tarea["task_space"]})
    anidado = dict(vista, recursos_a_solicitud=[{"id": "R9", "routes": []}])
    assert not inv.verificar_aislamiento(anidado)
    filtrado = dict(vista, enunciado_es=vista["enunciado_es"] + " " + tarea["task_space"]["validation_evidence"])
    assert not inv.verificar_aislamiento(filtrado, tarea)


def test_medio_en_lista_blanca(ejemplos):
    assert inv.medio_en_lista_blanca(ejemplos["noticia"]["medio_id"])
    assert not inv.medio_en_lista_blanca("diario_inventado")


# --------------------------------------------------------------------------- CLI para hooks
def test_cli_codigos_de_salida(tmp_path, ejemplos):
    ok = tmp_path / "ev.json"
    ok.write_text(json.dumps(ejemplos["evaluacion"]), encoding="utf-8")
    assert inv.main(["esquema", "evaluacion", str(ok)]) == 0
    assert inv.main(["umbral", str(ok)]) == 0
    malo = tmp_path / "malo.json"
    malo.write_text(json.dumps(_con_puntajes(ejemplos["evaluacion"], {"recursos": 0})), encoding="utf-8")
    assert inv.main(["umbral", str(malo)]) == 2
