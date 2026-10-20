"""Agente explorador de OTM-Prensa: feeds de MED01 -> candidatos -> objetos `noticia` validados.

Uso (desde la raíz del repo):
    python -m pipeline.agentes.explorador.run --medios cnnchile bbc --max-por-medio 8 \
        --salida evals/resultados/explorador_vivo_2026-10-20.json

Invariantes:
- 3: el cuerpo de la noticia vive solo en memoria; el resumen se rechaza si copia > 25 palabras
  seguidas (título o cuerpo) o supera 80 palabras; hasta `intentos_resumen` intentos.
- 4: toda cifra se verifica en código contra el párrafo citado; sin localizador verificado se descarta.
- 7: la clave sale de pipeline.apikey (vía pipeline.llm).
- 8: cada noticia aceptada se acompaña de metadatos de la corrida (modelo, versión de prompt, costo).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import yaml  # noqa: E402

from pipeline import invariantes as inv  # noqa: E402
from pipeline.llm import llamar, modelo_de  # noqa: E402

DIR = Path(__file__).resolve().parent
CFG = yaml.safe_load((DIR / "config.yaml").read_text(encoding="utf-8"))
P = CFG["parametros"]
VERSION_PROMPT = CFG["version_prompt"]
PROMPT = (DIR / CFG["prompt"]).read_text(encoding="utf-8")
AREAS = ["medio_ambiente", "economia", "salud", "ciencia_tecnologia", "deporte", "transporte_ciudad", "sociedad_datos"]
UA = "OTM-Prensa/1.0 (observatorio academico; PUC Chile)"

ESQUEMA_MODELO = {
    "type": "object",
    "additionalProperties": False,
    "required": ["es_candidata", "motivo", "area", "resumen_propio", "cifras"],
    "properties": {
        "es_candidata": {"type": "boolean"},
        "motivo": {"type": "string"},
        "area": {"type": "string", "enum": AREAS},
        "resumen_propio": {"type": "string"},
        "cifras": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["valor", "unidad", "que_es", "parrafo"],
                "properties": {
                    "valor": {"type": "string"},
                    "unidad": {"type": "string"},
                    "que_es": {"type": "string"},
                    "parrafo": {"type": "integer"},
                },
            },
        },
    },
}


# ------------------------------------------------------------------ MED01
def cargar_med01() -> dict:
    rutas = sorted((RAIZ / "insumos" / "medios").glob("MED01_*.yaml"))
    return yaml.safe_load(rutas[-1].read_text(encoding="utf-8"))


def version_med01() -> str:
    return cargar_med01().get("version", "?")


# ------------------------------------------------------------------ texto
def _html_a_texto(s: str) -> str:
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?i)</p>|<br\s*/?>|</li>|</h[1-6]>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)


def parrafos_de(s: str) -> list[str]:
    """Párrafos no vacíos de un fragmento HTML/texto. El índice visible al modelo parte en 1."""
    partes = [re.sub(r"\s+", " ", p).strip() for p in _html_a_texto(s).split("\n")]
    return [p for p in partes if len(p) > 3]


def numerar(parrafos: list[str]) -> str:
    return "\n".join(f"[{i}] {p}" for i, p in enumerate(parrafos, 1))


def _nums(texto: str) -> set[str]:
    """Números de un texto normalizados sin separadores de miles ni decimales: '1.234,5' -> '12345'."""
    return {re.sub(r"[.,\s]", "", m) for m in re.findall(r"\d[\d.,]*\d|\d", texto)}


def cifra_verificada(valor: str, parrafos: list[str], n: int) -> bool:
    """Invariante 4: el número de `valor` aparece en el párrafo n del cuerpo."""
    if not (1 <= n <= len(parrafos)):
        return False
    vn = _nums(str(valor))
    return bool(vn) and vn <= _nums(parrafos[n - 1])


def _valor(v: str):
    s = v.strip()
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    return s


def n_palabras(s: str) -> int:
    return len(s.split())


def slug(s: str, n: int = 6) -> str:
    base = "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))
    pal = re.findall(r"[a-z0-9]+", base)
    return "-".join(pal[:n]) or "sin-titulo"


# ------------------------------------------------------------------ feeds
def _get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — URLs de MED01
        return r.read()


def _fecha(txt: str | None) -> datetime | None:
    if not txt:
        return None
    try:
        d = parsedate_to_datetime(txt)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(txt.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parsear_feed(xml_bytes: bytes | str) -> list[dict]:
    """RSS 2.0 o Atom -> [{titulo, url, fecha(datetime), cuerpo_html}]. Sin dependencias externas."""
    if isinstance(xml_bytes, str):
        xml_bytes = xml_bytes.encode("utf-8")
    raiz = ET.fromstring(xml_bytes)
    out = []
    for it in raiz.iter():
        if _local(it.tag) not in ("item", "entry"):
            continue
        d: dict = {"titulo": "", "url": "", "fecha": None, "cuerpo_html": ""}
        for ch in it:
            t = _local(ch.tag)
            if t == "title":
                d["titulo"] = (ch.text or "").strip()
            elif t == "link":
                d["url"] = (ch.get("href") or ch.text or "").strip() or d["url"]
            elif t in ("pubDate", "published", "updated", "date"):
                d["fecha"] = d["fecha"] or _fecha((ch.text or "").strip())
            elif t == "encoded":
                d["cuerpo_html"] = ch.text or d["cuerpo_html"]
            elif t in ("description", "summary", "content") and not d["cuerpo_html"]:
                d["cuerpo_html"] = ch.text or ""
        if d["titulo"] and d["url"]:
            out.append(d)
    return out


def bajar_cuerpo(url: str) -> str:
    """Mejor esfuerzo: párrafos <p> de la página. Solo en memoria."""
    try:
        pag = _get(url).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        return ""
    ps = re.findall(r"(?is)<p[^>]*>(.*?)</p>", pag)
    return "\n".join(f"<p>{p}</p>" for p in ps)


def urls_de_medio(medio: dict) -> list[tuple[str, str | None]]:
    """[(url, area_sugerida)] principal y luego respaldo."""
    res = []
    if medio.get("secciones"):
        res += [(s["url"], s.get("area")) for s in medio["secciones"]]
    else:
        res.append((medio["url"], None))
    if medio.get("respaldo"):
        res.append((medio["respaldo"]["url"], None))
    return res


def recolectar(medio: dict, max_n: int, ahora: datetime, leer=_get) -> list[dict]:
    """Candidatos recientes (<= dias_maximos) de un medio. `leer(url)->bytes` inyectable para tests."""
    cands: list[dict] = []
    vistos: set[str] = set()
    principal_ok = False
    for i, (url, _area) in enumerate(urls_de_medio(medio)):
        es_respaldo = bool(medio.get("respaldo")) and url == medio["respaldo"]["url"]
        if es_respaldo and principal_ok:
            continue
        try:
            items = parsear_feed(leer(url))
        except Exception as e:  # noqa: BLE001
            print(f"[{medio['id']}] feed falló {url}: {type(e).__name__}", file=sys.stderr)
            continue
        if not es_respaldo:
            principal_ok = principal_ok or bool(items)
        for it in items:
            if it["url"] in vistos:
                continue
            f = it["fecha"]
            if f is None or ahora - f > timedelta(days=P["dias_maximos"]) or f > ahora + timedelta(days=1):
                continue
            vistos.add(it["url"])
            cands.append({**it, "medio_id": medio["id"], "medio": medio["nombre"], "idioma": medio["idioma"]})
    cands.sort(key=lambda c: c["fecha"], reverse=True)
    return cands[:max_n]


# ------------------------------------------------------------------ modelo
def _mensaje(c: dict, parrafos: list[str], aviso: str | None) -> str:
    m = (f"Medio: {c['medio']}\nTítulo: {c['titulo']}\nFecha: {c['fecha'].date().isoformat()}\n"
         f"URL: {c['url']}\nIdioma: {c['idioma']}\n\nCuerpo disponible (párrafos numerados):\n"
         f"<noticia>\n{numerar(parrafos)[: P['max_chars_cuerpo']]}\n</noticia>")
    if aviso:
        m += f"\n\nAVISO DE CORRECCIÓN: {aviso}"
    return m


def explorar_noticia(c: dict, *, cliente=None, ahora: datetime | None = None, bajar=bajar_cuerpo) -> dict:
    """Procesa un candidato. Devuelve {"noticia": dict|None, "descartada": motivo|None, "costo_usd": float, "meta": [...]}."""
    ahora = ahora or datetime.now(timezone.utc)
    costo, metas = 0.0, []

    def fin(noticia=None, motivo=None):
        return {"noticia": noticia, "descartada": motivo, "costo_usd": round(costo, 6), "meta": metas}

    ok = inv.medio_en_lista_blanca(c["medio_id"])
    if not ok:
        return fin(motivo="; ".join(ok.errores))
    parrafos = parrafos_de(c.get("cuerpo_html", ""))
    if sum(len(p) for p in parrafos) < 400 and bajar:
        extra = parrafos_de(bajar(c["url"]))
        if sum(len(p) for p in extra) > sum(len(p) for p in parrafos):
            parrafos = extra
    if not any(re.search(r"\d", p) for p in parrafos):
        return fin(motivo="sin cifras en el cuerpo disponible (filtro previo MED01)")
    fuente = c["titulo"] + "\n" + "\n".join(parrafos)

    aviso = None
    for intento in range(P["intentos_resumen"]):
        r = llamar(agente="explorador", system=PROMPT, user=_mensaje(c, parrafos, aviso),
                   schema=ESQUEMA_MODELO, max_tokens=P["max_tokens"], cliente=cliente)
        costo += r["meta"]["costo_usd"]
        metas.append(r["meta"])
        s = r["salida"]
        if not s.get("es_candidata"):
            return fin(motivo=f"no candidata: {s.get('motivo', '')[:120]}")
        resumen = " ".join(s["resumen_propio"].split())
        problemas = []
        if not 1 <= n_palabras(resumen) <= 80:
            problemas.append(f"el resumen tiene {n_palabras(resumen)} palabras; debe tener entre 1 y 80")
        lit = inv.cumple_limite_literal(resumen, fuente)
        if not lit:
            problemas.append(f"el resumen copia {lit.detalle.get('max_consecutivas', '>25')} palabras seguidas del texto; "
                             "reescríbelo con otras palabras")
        if problemas:
            aviso = "; ".join(problemas)
            continue
        cifras = []
        for ci in s["cifras"]:
            if cifra_verificada(ci["valor"], parrafos, ci["parrafo"]) and ci["que_es"].strip():
                cifras.append({"valor": _valor(ci["valor"]), "unidad": ci["unidad"].strip(),
                               "que_es": ci["que_es"].strip()[:200],
                               "localizador": {"fuente": "noticia", "ubicacion": f"párrafo {ci['parrafo']}"}})
        if not cifras:
            return fin(motivo="ninguna cifra verificada contra el texto (invariante 4)")
        fecha = c["fecha"].date().isoformat()
        noticia = {
            "id": f"{fecha}-{c['medio_id']}-{slug(c['titulo'])}",
            "medio_id": c["medio_id"], "medio": c["medio"], "idioma": c["idioma"],
            "titulo": c["titulo"][:300], "fecha": fecha, "url": c["url"],
            "area": s["area"], "resumen_propio": resumen, "cifras": cifras,
            "recuperada_en": ahora.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        v = inv.validar_contra_esquema(noticia, "noticia")
        if not v:
            return fin(motivo="no valida contra noticia: " + "; ".join(v.errores)[:300])
        # el título es cita legítima: se excluye de la comparación final
        sin_titulo = {k: v_ for k, v_ in noticia.items() if k != "titulo"}
        if not inv.cumple_limite_literal(sin_titulo, "\n".join(parrafos)):
            return fin(motivo="el artefacto copia > 25 palabras del cuerpo")
        return fin(noticia=noticia)
    return fin(motivo=f"resumen rechazado tras {P['intentos_resumen']} intentos: {aviso}")


def explorar(medios_ids: list[str] | None = None, max_por_medio: int = 8, *, cliente=None,
             ahora: datetime | None = None, leer=_get, bajar=bajar_cuerpo, tope_usd: float = 1.0) -> dict:
    ahora = ahora or datetime.now(timezone.utc)
    med = cargar_med01()
    medios = [m for m in med["medios"] if not medios_ids or m["id"] in medios_ids]
    noticias, descartes, gasto = [], [], 0.0
    for m in medios:
        for c in recolectar(m, max_por_medio, ahora, leer):
            if gasto >= tope_usd:
                descartes.append({"url": c["url"], "motivo": "tope de gasto alcanzado"})
                continue
            res = explorar_noticia(c, cliente=cliente, ahora=ahora, bajar=bajar)
            gasto += res["costo_usd"]
            if res["noticia"]:
                noticias.append(res["noticia"])
            else:
                descartes.append({"url": c["url"], "medio_id": c["medio_id"], "motivo": res["descartada"]})
    return {
        "meta": {"agente": "explorador", "modelo": modelo_de("explorador"), "version_prompt": VERSION_PROMPT,
                 "version_med01": med.get("version"), "fecha": ahora.isoformat(timespec="seconds"),
                 "costo_usd": round(gasto, 6), "n_aceptadas": len(noticias), "n_descartadas": len(descartes)},
        "noticias": noticias,
        "descartes": descartes,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--medios", nargs="*", help="ids de MED01 (por defecto, todos)")
    ap.add_argument("--max-por-medio", type=int, default=8)
    ap.add_argument("--tope-usd", type=float, default=1.0)
    ap.add_argument("--salida", type=Path)
    a = ap.parse_args(argv)
    res = explorar(a.medios, a.max_por_medio, tope_usd=a.tope_usd)
    for n in res["noticias"]:
        v = inv.validar_contra_esquema(n, "noticia")
        assert v, v.errores
    texto = json.dumps(res, ensure_ascii=False, indent=2)
    if a.salida:
        a.salida.parent.mkdir(parents=True, exist_ok=True)
        a.salida.write_text(texto + "\n", encoding="utf-8")
    print(json.dumps(res["meta"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
