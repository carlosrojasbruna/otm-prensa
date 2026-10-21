"""Tests de pipeline/marcar_publicadas.py (publicada.yml): publicar -> merge -> `publicada`. Repo git en tmp_path."""
import json
import subprocess
from pathlib import Path

import pytest
import yaml

from pipeline import marcar_publicadas as M
from pipeline import orquestador as orq
from pipeline import publicar as P

RAIZ = Path(__file__).resolve().parents[1]
REVISOR = "Revisora de Prueba"
FECHA = "2026-10-27"
RAMA = "publicar/2026-10-27-1"


def _leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def _git(raiz, *a):
    return subprocess.run(["git", *a], cwd=raiz, capture_output=True, text=True, encoding="utf-8", check=True).stdout


@pytest.fixture
def publicado(tmp_path):
    """Repo con un expediente `verificada` publicado por publicar.py en RAMA y mergeado a main."""
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    for k, v in (("user.name", "Test"), ("user.email", "t@example.org"), ("commit.gpgsign", "false")):
        _git(r, "config", k, v)
    t, g, e, tr = (_leer(RAIZ / "contratos" / "ejemplos" / f"{n}_ejemplo.json")
                   for n in ("tarea", "guia", "evaluacion", "trazas_resumen"))
    t["estado"] = "verificada"
    g["trazabilidad"]["revision_humana_2"] = None
    exp = orq.Expediente(tarea_id=t["id"], estado="verificada",
                         artefactos={"tarea": t, "guia": g, "evaluacion": e, "trazas_resumen": tr})
    orq.guardar(exp, r / "pipeline" / "state" / "expedientes")
    _git(r, "add", ".")
    _git(r, "commit", "-q", "-m", "inicial")
    lote = P.preparar_todas([t["id"]], REVISOR, raiz=r, fecha=FECHA, leer_noticia=lambda u: "texto breve")
    P.ejecutar(lote, REVISOR, raiz=r, rama=RAMA, fecha=FECHA)
    _git(r, "switch", "-q", "main")
    _git(r, "merge", "-q", "--no-ff", "-m", "merge", RAMA)
    return r, t["id"]


def test_merge_de_publicar_pasa_a_publicada_solo_el_estado(publicado):
    repo, tid = publicado
    antes = orq.cargar(tid, repo / "pipeline" / "state" / "expedientes")
    assert M.marcar(RAMA, "7", "abc1234", raiz=repo) == [tid]
    despues = orq.cargar(tid, repo / "pipeline" / "state" / "expedientes")
    assert despues.estado == "publicada" and despues.artefactos["tarea"]["estado"] == "publicada"
    assert despues.historial[-1]["revisor"] == REVISOR and "PR #7" in despues.historial[-1]["motivo"]
    assert despues.marcas == antes.marcas                       # no toca marcas
    for n in ("guia", "evaluacion", "trazas_resumen"):          # ni otros artefactos
        assert despues.artefactos[n] == antes.artefactos[n]
    cambiados = _git(repo, "status", "--porcelain").split("\n")
    assert all("pipeline/state/" in c for c in cambiados if c)  # nada en tareas/


def test_otra_rama_o_repetido_no_hace_nada(publicado):
    repo, tid = publicado
    assert M.marcar("publicar/otra", "7", "abc1234", raiz=repo) == []
    assert M.main(["--rama", "publicar/otra", "--pr", "7", "--merge", "abc", "--raiz", str(repo)]) == 3
    assert M.marcar(RAMA, "7", "abc1234", raiz=repo) == [tid]
    assert M.marcar(RAMA, "7", "abc1234", raiz=repo) == []     # ya publicada: idempotente


def test_sin_la_version_en_el_catalogo_no_escribe(publicado):
    repo, tid = publicado
    ruta_cat = repo / "tareas" / "catalogo.json"
    cat = _leer(ruta_cat)
    cat["tareas"] = []
    ruta_cat.write_text(json.dumps(cat), encoding="utf-8")
    with pytest.raises(M.Error, match="catálogo"):
        M.marcar(RAMA, "7", "abc1234", raiz=repo)
    assert orq.cargar(tid, repo / "pipeline" / "state" / "expedientes").estado == "verificada"


def test_sin_revision_humana_2_falla(publicado):
    repo, tid = publicado
    ruta = repo / "pipeline" / "state" / "expedientes" / f"{tid}.json"
    d = _leer(ruta)
    d["artefactos"]["guia"]["trazabilidad"]["revision_humana_2"] = None
    ruta.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(M.Error, match="revision_humana_2"):
        M.marcar(RAMA, "7", "abc1234", raiz=repo)


def test_workflow_publicada_solo_tras_merge_de_publicar():
    d = yaml.safe_load((RAIZ / ".github" / "workflows" / "publicada.yml").read_text(encoding="utf-8"))
    on = d.pop(True, d.get("on"))
    assert on == {"pull_request": {"types": ["closed"], "branches": ["main"]}}
    cond = d["jobs"]["publicada"]["if"]
    assert "merged == true" in cond and "'publicar/'" in cond
    texto = json.dumps(d["jobs"])
    assert "pipeline.marcar_publicadas" in texto and "otm_hook.py staged" in texto and "ANTHROPIC_API_KEY" not in texto
