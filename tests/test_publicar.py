"""Tests de pipeline/publicar.py (publicar.yml). Repo git de prueba en tmp_path, sin red."""
import json
import subprocess
from pathlib import Path

import pytest

from pipeline import orquestador as orq
from pipeline import publicar as P

RAIZ = Path(__file__).resolve().parents[1]
REVISOR = "Revisora de Prueba"
FECHA = "2026-10-27"


def _leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def _git(raiz, *a):
    return subprocess.run(["git", *a], cwd=raiz, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def _expediente(repo, estado="verificada", tid=None):
    t, g, e = (_leer(RAIZ / "contratos" / "ejemplos" / f"{n}_ejemplo.json") for n in ("tarea", "guia", "evaluacion"))
    t["estado"] = estado
    g["trazabilidad"]["revision_humana_2"] = None
    exp = orq.Expediente(tarea_id=tid or t["id"], estado=estado, artefactos={"tarea": t, "guia": g, "evaluacion": e})
    orq.guardar(exp, repo / "pipeline" / "state" / "expedientes")
    return exp


@pytest.fixture
def repo_tid(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    for k, v in (("user.name", "Test"), ("user.email", "t@example.org"), ("commit.gpgsign", "false")):
        _git(r, "config", k, v)
    exp = _expediente(r)
    _git(r, "add", ".")
    _git(r, "commit", "-q", "-m", "inicial")
    return r, exp.tarea_id


def _sin_texto(url):
    raise RuntimeError("sin red")


def test_publica_en_rama_con_revision_2_y_expediente_sigue_verificada(repo_tid):
    repo, tid = repo_tid
    lote = P.preparar_todas([tid], REVISOR, raiz=repo, fecha=FECHA, leer_noticia=lambda u: "texto breve")
    hechos = P.ejecutar(lote, REVISOR, raiz=repo, rama="publicar/prueba", fecha=FECHA)
    assert _git(repo, "branch", "--show-current").strip() == "publicar/prueba"
    cat = _leer(repo / "tareas" / "catalogo.json")
    assert [t["id"] for t in cat["tareas"]] == [hechos[0]["entrada"]["id"]]
    exp = orq.cargar(tid, repo / "pipeline" / "state" / "expedientes")
    assert exp.estado == "verificada"
    assert exp.marcas["revision_humana_2"]["revisor"] == REVISOR
    assert exp.artefactos["guia"]["trazabilidad"]["revision_humana_2"] == {"revisor": REVISOR, "fecha": FECHA}
    guia_pub = next((repo / hechos[0]["ruta"]).glob("guia_v*.json"))
    assert _leer(guia_pub)["trazabilidad"]["revision_humana_2"]["revisor"] == REVISOR
    assert _git(repo, "status", "--porcelain") == ""
    assert REVISOR in P.cuerpo_pr(hechos, REVISOR)


def test_rechaza_publicada_sin_tocar_nada(repo_tid):
    repo, tid = repo_tid
    _expediente(repo, estado="publicada", tid="2026-10-ya-publicada")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "publicada")
    antes = _git(repo, "rev-parse", "HEAD")
    assert P.main(["2026-10-ya-publicada", "--revisor", REVISOR, "--ejecutar", "--rama", "publicar/x",
                   "--raiz", str(repo)]) == 2
    assert _git(repo, "rev-parse", "HEAD") == antes and _git(repo, "status", "--porcelain") == ""
    assert "publicar/x" not in _git(repo, "branch")


def test_sin_texto_de_noticia_rechaza(repo_tid):
    repo, tid = repo_tid
    with pytest.raises(P.Rechazo, match="invariante 3"):
        P.preparar_todas([tid], REVISOR, raiz=repo, fecha=FECHA, leer_noticia=_sin_texto)


def test_revisor_e_ids_obligatorios(repo_tid):
    repo, tid = repo_tid
    with pytest.raises(P.Rechazo, match="revisor"):
        P.preparar_todas([tid], " ", raiz=repo, fecha=FECHA, leer_noticia=lambda u: "x")
    with pytest.raises(P.Rechazo, match="repetidos"):
        P.preparar_todas([tid, tid], REVISOR, raiz=repo, fecha=FECHA, leer_noticia=lambda u: "x")
    with pytest.raises(P.Rechazo, match="no existe"):
        P.preparar_todas(["2026-10-no-existe"], REVISOR, raiz=repo, fecha=FECHA, leer_noticia=lambda u: "x")


def test_estado_distinto_de_verificada_rechaza(repo_tid):
    repo, tid = repo_tid
    _expediente(repo, estado="evaluada", tid="2026-10-en-evaluada")
    with pytest.raises(P.Rechazo, match="evaluada"):
        P.preparar_todas(["2026-10-en-evaluada"], REVISOR, raiz=repo, fecha=FECHA, leer_noticia=lambda u: "x")
