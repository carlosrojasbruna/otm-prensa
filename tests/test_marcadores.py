"""Marcadores deportivos «N-M» en el verificador y el diseñador (W45 «6-1», W46 «2-1»).

Dos semanas seguidas el verificador marcó «cifra 1 sin localizador» en tareas de fútbol: `parsear_numero` lee solo el
primer número de «2-1», y el 1 del enunciado quedaba sin cifra. Ahora el marcador registra los dos números y el
diseñador emite el segundo como cifra propia. Se usan los expedientes reales de W45/W46 con un texto SINTÉTICO de la
noticia (el texto real no se guarda en el repo, invariante 3). Sin red ni API."""
import copy
import json
from pathlib import Path

import pytest

from pipeline import orquestador as orq
from pipeline.agentes.disenador import run as dis
from pipeline.agentes.verificador import run as V

DIR_CASOS = Path(__file__).resolve().parents[1] / "evals" / "casos" / "disenador"


# --------------------------------------------------------------------------- lectura de números
@pytest.mark.parametrize("texto,esperado", [("ganó por 2-1", [2.0, 1.0]), ("goleada 6-1", [6.0, 1.0]),
                                            ("un 6 – 1 en casa", [6.0, 1.0])])
def test_numeros_en_registra_los_dos_numeros_del_marcador(texto, esperado):
    assert V.numeros_en(texto) == esperado


@pytest.mark.parametrize("valor,esperado", [("2-1", (2, 1)), ("6-1", (6, 1)), ("6 – 1", (6, 1)),
                                            ("2025-2026", None), ("+29", None), (21, None), ("2-1 goles", None)])
def test_marcador(valor, esperado):
    assert V.marcador(valor) == esperado


def test_numeros_de_valor():
    assert V.numeros_de_valor("2-1") == [2.0, 1.0]
    assert V.numeros_de_valor("6-1") == [6.0, 1.0]
    assert V.numeros_de_valor("+29") == [29.0]
    assert V.parsear_numero("2-1") == 2.0   # sin cambio: un solo número (lo usan los votos de alineación)


def test_expandir_marcadores_agrega_el_segundo_numero_una_vez():
    loc = {"fuente": "noticia", "ubicacion": "párrafo 13"}
    cifras = [{"valor": "2-1", "unidad": "goles (marcador)", "que_es": "U. de Chile vs Cobresal", "localizador": loc},
              {"valor": 27, "unidad": "partidos", "que_es": "partidos", "localizador": loc}]
    ex = V.expandir_marcadores(cifras)
    assert [c["valor"] for c in ex] == ["2-1", 1, 27]
    assert ex[1]["localizador"] == loc and "segundo número del marcador 2-1" in ex[1]["que_es"]
    assert V.expandir_marcadores(ex) == ex   # idempotente: no la duplica
    assert cifras[0] == ex[0] and len(cifras) == 2   # no muta la entrada


# --------------------------------------------------------------------------- verificador con expedientes reales
def _sin_cifra_manual(tid):
    """Tarea y noticia del expediente sin la cifra del segundo número agregada a mano (estado previo al arreglo)."""
    a = orq.cargar(tid).artefactos
    t, n = copy.deepcopy(a["tarea"]), copy.deepcopy(a["noticia"])
    es_manual = lambda c: c["valor"] == 1 and "segundo número" in c["que_es"]  # noqa: E731
    t["noticia"]["cifras_usadas"] = [c for c in t["noticia"]["cifras_usadas"] if not es_manual(c)]
    n["cifras"] = [c for c in n["cifras"] if not es_manual(c)]
    return t, n


def _texto(parrafos: dict[int, str], total: int = 15) -> str:
    return "".join(f"<p>{parrafos.get(i, f'Párrafo {i} sin cifras.')}</p>" for i in range(1, total + 1))


TEXTO_2_1 = _texto({8: "La fecha tuvo partidos parejos y 2 sorpresas.",
                    13: "Resultados: Universidad de Chile 2-1 Cobresal; Palestino 1-0 Everton; Huachipato 3-0 "
                        "Ñublense. Tabla: Colo Colo con 61 puntos en 27 partidos y diferencia de goles +29."})
TEXTO_6_1 = _texto({2: "Colo Colo buscaría la 35ª corona ante Ñublense.",
                    3: "Colo Colo goleó 6-1 a Universidad de Concepción.",
                    6: "El estadio tiene capacidad para 12 mil espectadores y se autorizaron 7,5 mil fanáticos.",
                    11: "El estadio de Concepción tiene una capacidad autorizada de 30 mil espectadores."})


@pytest.mark.parametrize("tid,texto", [("2026-11-que-tan-raro-fue-2-1-v2", TEXTO_2_1),
                                       ("2026-11-traslado-partido-concepcion-hinchas-v2", TEXTO_6_1)])
def test_el_segundo_numero_del_marcador_ya_no_es_falso_positivo(tid, texto):
    t, n = _sin_cifra_manual(tid)
    inf = V.verificar_tarea(t, n, texto)
    assert not any("sin localizador" in h["descripcion"] for h in inf["hallazgos"]), inf["hallazgos"]
    assert inf["aprobado"], inf["hallazgos"]


def test_sin_texto_tambien_acepta_el_marcador():
    t, n = _sin_cifra_manual("2026-11-que-tan-raro-fue-2-1-v2")
    inf = V.verificar_tarea(t, n, None)
    assert not any("sin localizador" in h["descripcion"] for h in inf["hallazgos"]), inf["hallazgos"]


def test_el_marcador_se_busca_entero_no_su_primer_numero():
    """«2 sorpresas» en el párrafo 8 no respalda un «2-1» localizado en el párrafo 8: el 2-1 está en el 13."""
    t, n = _sin_cifra_manual("2026-11-que-tan-raro-fue-2-1-v2")
    for lista in (t["noticia"]["cifras_usadas"], n["cifras"]):
        for c in lista:
            if c["valor"] == "2-1":
                c["localizador"] = {"fuente": "noticia", "ubicacion": "párrafo 8"}
    inf = V.verificar_tarea(t, n, TEXTO_2_1)
    assert not inf["aprobado"]
    assert any("'2-1'" in h["descripcion"] and "párrafo 13" in h["descripcion"] for h in inf["hallazgos"])


def test_un_numero_suelto_sigue_siendo_critico():
    t, n = _sin_cifra_manual("2026-11-que-tan-raro-fue-2-1-v2")
    t["estudiante"]["enunciado_es"] += " Consideren 7 partidos."
    inf = V.verificar_tarea(t, n, TEXTO_2_1)
    assert any("cifra 7 sin localizador" in h["descripcion"] for h in inf["hallazgos"])


# --------------------------------------------------------------------------- diseñador
def test_disenador_emite_las_dos_cifras_del_marcador():
    caso = json.loads((DIR_CASOS / "s-cuenta-luz.json").read_text(encoding="utf-8"))
    noticia = copy.deepcopy(caso["noticia"])
    loc = {"fuente": "noticia", "ubicacion": "párrafo 3"}
    noticia["cifras"].append({"valor": "2-1", "unidad": "goles (marcador)",
                              "que_es": "resultado del partido", "localizador": loc})
    r = copy.deepcopy(caso["respuestas_simuladas"][0]["candidatos"][0])
    r["cifras_usadas_idx"] = list(r["cifras_usadas_idx"]) + [len(noticia["cifras"]) - 1]
    r["enunciado_es"] += " El partido terminó 2-1."
    t = dis.ensamblar(r, noticia, fecha="2026-10-20")
    usadas = t["noticia"]["cifras_usadas"]
    i = next(k for k, c in enumerate(usadas) if c["valor"] == "2-1")
    assert usadas[i + 1]["valor"] == 1 and usadas[i + 1]["localizador"] == loc
    assert dis.validar_tarea(t, noticia) == []
    inf = V.verificar_tarea(t, noticia, None)
    assert not any("sin localizador" in h["descripcion"] for h in inf["hallazgos"]), inf["hallazgos"]
