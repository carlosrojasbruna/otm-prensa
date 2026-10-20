"""Tests del bibliotecario. Todo en tmp_path (repo git de prueba), sin red; nunca toca el repo real."""
import copy
import json
import subprocess
from pathlib import Path

import pytest

from pipeline import invariantes as inv
from pipeline.agentes.bibliotecario import run as bib

RAIZ = Path(__file__).resolve().parents[1]
CASOS = sorted((RAIZ / "evals" / "casos" / "bibliotecario").glob("*.json"))
NOMBRES = ("tarea", "guia", "evaluacion")


def _leer(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def _ejemplos():
    return [_leer(RAIZ / "contratos" / "ejemplos" / f"{n}_ejemplo.json") for n in NOMBRES]


def _parchar(art, parches):
    art = copy.deepcopy(art)
    for ruta, valor in parches.items():
        *ks, ultimo = ruta.split(".")
        d = art
        for k in ks:
            d = d[k]
        d[ultimo] = valor
    return art


def _git(raiz, *a):
    return subprocess.run(["git", *a], cwd=raiz, capture_output=True, text=True, encoding="utf-8", check=True).stdout


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    _git(r, "init", "-q")
    for k, v in (("user.name", "Test"), ("user.email", "t@example.org"), ("commit.gpgsign", "false")):
        _git(r, "config", k, v)
    (r / "README.md").write_text("repo de prueba\n", encoding="utf-8")
    _git(r, "add", ".")
    _git(r, "commit", "-q", "-m", "inicial")
    return r


def _arbol(raiz):
    return sorted(str(p.relative_to(raiz)) for p in raiz.rglob("*") if ".git" not in p.parts)


def _v1(repo):
    t, g, e = _ejemplos()
    t["estado"] = "verificada"
    return bib.publicar(t, g, e, raiz=repo, fecha_publicacion="2026-10-27", ejecutar_real=True, remoto=False)


@pytest.mark.parametrize("ruta", CASOS, ids=[c.stem for c in CASOS])
def test_casos(ruta, repo):
    caso = _leer(ruta)
    crit, ent = caso["criterio_aceptacion"], caso["entrada"]
    base = [_parchar(a, ent["parches"].get(n, {})) for a, n in zip(_ejemplos(), NOMBRES)]
    tarea, guia, ev = base
    if ent["catalogo_previo"]:
        (repo / "tareas").mkdir()
        (repo / "tareas" / "catalogo.json").write_text(
            (RAIZ / ent["catalogo_previo"]).read_text(encoding="utf-8"), encoding="utf-8")
    v1_bytes = {}
    if ent["publicar_antes"]:
        _v1(repo)
        v1_bytes = {p.name: p.read_bytes() for p in (repo / crit["ruta"]).iterdir()}
    antes = _arbol(repo)

    if crit["resultado"] == "rechazo":
        with pytest.raises(bib.ErrorBibliotecario) as ex:
            bib.publicar(tarea, guia, ev, raiz=repo, fecha_publicacion=ent["fecha_publicacion"],
                         ejecutar_real=True, remoto=False)
        assert crit["mensaje_contiene"] in " ".join(ex.value.errores)
        assert _arbol(repo) == antes          # no escribió nada
        return

    plan = bib.publicar(tarea, guia, ev, raiz=repo, fecha_publicacion=ent["fecha_publicacion"],
                        ejecutar_real=True, remoto=False)
    carpeta = repo / crit["ruta"]
    for n in crit["archivos_escritos"]:
        assert (carpeta / n).is_file()
    cat = _leer(repo / "tareas" / "catalogo.json")
    r = inv.validar_contra_esquema(cat, "catalogo")
    assert r, r.errores
    c = crit["catalogo"]
    assert len(cat["tareas"]) == c["n_tareas"]
    e = cat["tareas"][0]
    assert e["version"] == c["version"] and e["licencia"] == c["licencia"]
    assert [v["version"] for v in e["versiones_anteriores"]] == c["versiones_anteriores"]
    assert e["ruta"] == crit["ruta"]
    assert set(e["archivos"].values()) == set(crit["archivos_escritos"])
    if "rama" in crit:
        assert plan.rama == crit["rama"]
        assert _git(repo, "branch", "--show-current").strip() == crit["rama"]
    # el commit del catálogo es el real de los archivos de la tarea
    assert _git(repo, "rev-parse", "--short=12", "HEAD~1").strip() == e["commit"]
    if crit.get("v1_intacta"):
        for nombre, b in v1_bytes.items():
            assert (carpeta / nombre).read_bytes() == b
        assert e["versiones_anteriores"][0]["commit"] != e["commit"]
    if crit.get("repetir_v1_rechazado"):
        t1, g1, e1 = _ejemplos()
        t1["estado"] = "verificada"
        with pytest.raises(bib.ErrorBibliotecario, match="no se edita"):
            bib.publicar(t1, g1, e1, raiz=repo, fecha_publicacion="2026-12-01", ejecutar_real=True, remoto=False)


def test_dry_run_no_escribe_ni_ejecuta_y_no_filtra_secretos(repo, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "ghp_SECRETO_DE_PRUEBA_123")
    t, g, e = _ejemplos()
    t["estado"] = "publicada"
    antes, ramas = _arbol(repo), _git(repo, "branch", "--list")
    salida = []
    plan = bib.publicar(t, g, e, raiz=repo, fecha_publicacion="2026-10-27", salida=salida.append)
    texto = "\n".join(salida)
    assert _arbol(repo) == antes and _git(repo, "branch", "--list") == ramas
    assert "git switch -c tareas/semana-2026-W44" in texto and "gh pr create" in texto
    assert "SECRETO" not in texto and "GH_TOKEN" not in texto
    assert inv.validar_contra_esquema(plan.catalogo, "catalogo")


def test_ejecutar_remoto_exige_token(repo, monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    t, g, e = _ejemplos()
    t["estado"] = "verificada"
    antes = _arbol(repo)
    with pytest.raises(bib.ErrorBibliotecario, match="GH_TOKEN"):
        bib.publicar(t, g, e, raiz=repo, fecha_publicacion="2026-10-27", ejecutar_real=True, remoto=True)
    assert _arbol(repo) == antes


def test_dos_tareas_misma_semana_comparten_rama_y_catalogo_ordenado(repo):
    _v1(repo)
    t, g, e = _ejemplos()
    nuevo = "2026-10-abeja-en-la-ciudad"
    t["id"], g["tarea_id"], e["tarea_id"] = nuevo, nuevo, nuevo
    t["estado"] = "verificada"
    plan = bib.publicar(t, g, e, raiz=repo, fecha_publicacion="2026-10-28", ejecutar_real=True, remoto=False)
    cat = _leer(repo / "tareas" / "catalogo.json")
    assert [x["id"] for x in cat["tareas"]] == [nuevo, "2026-10-embalse-el-yeso"]
    assert plan.rama == "tareas/semana-2026-W44"
    assert inv.validar_contra_esquema(cat, "catalogo")


def test_rechaza_rub01_bajo_umbral_y_texto_literal(repo):
    t, g, e = _ejemplos()
    t["estado"] = "verificada"
    e2 = copy.deepcopy(e)
    e2["rub01"]["criterios"]["genuino"]["puntaje"] = 0
    with pytest.raises(bib.ErrorBibliotecario):
        bib.preparar(t, g, e2, raiz=repo)
    fuente = " ".join(f"palabra{i}" for i in range(40))
    t2 = copy.deepcopy(t)
    t2["estudiante"]["enunciado_es"] = " ".join(f"palabra{i}" for i in range(30))
    with pytest.raises(bib.ErrorBibliotecario, match="consecutivas"):
        bib.preparar(t2, g, e, raiz=repo, texto_noticia=fuente)


def test_no_sobrescribe_archivo_existente(repo):
    t, g, e = _ejemplos()
    t["estado"] = "verificada"
    carpeta = repo / "tareas" / "2026-10" / "embalse-el-yeso"
    carpeta.mkdir(parents=True)
    (carpeta / "tarea_v1.0_2026-10-27.json").write_text("{}", encoding="utf-8")
    with pytest.raises(bib.ErrorBibliotecario, match="ya existe"):
        bib.preparar(t, g, e, raiz=repo, fecha_publicacion="2026-10-27")


def test_version_del_pipeline_va_a_la_carpeta_del_slug_base_con_md_e_icono(repo):
    """`…-v3` se archiva en la carpeta del slug base, con render .md (PLT01/PLT02) e ícono versionados."""
    t, g, e = _ejemplos()
    base = t["id"]
    tid = f"{base}-v3"
    t["id"], g["tarea_id"], e["tarea_id"] = tid, tid, tid
    t["version"] = g["version"] = g["ficha"]["version"] = 3
    t["estado"] = "verificada"
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle cx="5" cy="5" r="4"/></svg>'
    bib.publicar(t, g, e, raiz=repo, fecha_publicacion="2026-10-27", ejecutar_real=True, remoto=False, icono_svg=svg)
    aaaa_mm, slug = base[:7], base[8:]
    carpeta = repo / "tareas" / aaaa_mm / slug
    nombres = sorted(p.name for p in carpeta.iterdir())
    assert nombres == sorted(f"{n}_v3.0_2026-10-27.{x}" for n, x in (
        ("tarea", "json"), ("tarea", "md"), ("guia", "json"), ("guia", "md"), ("evaluacion", "json"), ("icono", "svg")))
    assert (carpeta / "icono_v3.0_2026-10-27.svg").read_text(encoding="utf-8") == svg
    md_t = (carpeta / "tarea_v3.0_2026-10-27.md").read_text(encoding="utf-8")
    md_g = (carpeta / "guia_v3.0_2026-10-27.md").read_text(encoding="utf-8")
    for s in ("## 1. Enunciado", "## 2. Datos y recursos", "## 3. Mapa a priori", "## 4. Espacio de soluciones",
              "## 5. Rúbrica aplicada", t["estudiante"]["enunciado_es"].strip()[:40]):
        assert s in md_t
    for k in range(11):
        assert f"## {k}. " in md_g
    cat = _leer(repo / "tareas" / "catalogo.json")
    assert inv.validar_contra_esquema(cat, "catalogo")
    ent = cat["tareas"][0]
    assert ent["id"] == base and ent["ruta"] == f"tareas/{aaaa_mm}/{slug}/"
    assert ent["archivos"]["icono"] == "icono_v3.0_2026-10-27.svg" and not any(
        v.endswith(".md") for v in ent["archivos"].values())
    # la v4 del pipeline (`…-v4`) se reconoce como versión nueva de la misma tarea, en la misma carpeta
    t4, g4, e4 = copy.deepcopy(t), copy.deepcopy(g), copy.deepcopy(e)
    tid4 = f"{base}-v4"
    t4["id"], g4["tarea_id"], e4["tarea_id"] = tid4, tid4, tid4
    t4["version"] = g4["version"] = g4["ficha"]["version"] = 4
    bib.publicar(t4, g4, e4, raiz=repo, fecha_publicacion="2026-11-03", ejecutar_real=True, remoto=False)
    ent = _leer(repo / "tareas" / "catalogo.json")["tareas"][0]
    assert ent["version"] == 4 and [v["version"] for v in ent["versiones_anteriores"]] == [3]
    assert (carpeta / "tarea_v3.0_2026-10-27.md").read_text(encoding="utf-8") == md_t


def test_rechaza_icono_que_no_es_svg(repo):
    t, g, e = _ejemplos()
    t["estado"] = "verificada"
    with pytest.raises(bib.ErrorBibliotecario, match="SVG"):
        bib.preparar(t, g, e, raiz=repo, icono_svg="no soy un svg")
