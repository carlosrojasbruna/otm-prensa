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
import base64
import functools
import urllib.error
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

try:  # MED01 v1.1: parser seguro si está instalado; si no, xml.etree estándar (ver DECISIONES.md)
    from defusedxml import ElementTree as _ET_SEGURO
except ImportError:  # pragma: no cover
    _ET_SEGURO = None

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

# Dominios de los medios de MED01 (para validar que un enlace resuelto pertenece a un medio de la lista).
# Los más específicos (con ruta) van antes que su dominio general.
DOMINIOS = {
    "bbcmundo": ["bbc.com/mundo", "bbc.co.uk/mundo"], "bbc": ["bbc.com", "bbc.co.uk"],
    "latercera": ["latercera.com"], "emol": ["emol.com"], "cnnchile": ["cnnchile.com"],
    "ciper": ["ciperchile.cl"], "canal13": ["t13.cl"], "reuters": ["reuters.com"],
    "dw": ["dw.com"], "naturenews": ["nature.com"],
}
# MED01 v1.1: solo La Tercera trae el cuerpo completo en el feed; en el resto se lee el enlace original.
CUERPO_EN_FEED = {"latercera"}


class ErrorLectura(Exception):
    """No se pudo (o no se puede) leer el enlace original; el mensaje es el motivo de descarte."""


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
def _clave_version(ruta: Path) -> tuple:
    m = re.search(r"_v(\d+)\.(\d+)_", ruta.name)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def cargar_med01() -> dict:
    """Versión más alta de MED01 (orden numérico: v1.10 > v1.9)."""
    rutas = sorted((RAIZ / "insumos" / "medios").glob("MED01_*.yaml"), key=_clave_version)
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


_RE_ITEM = re.compile(r"(?is)<(item|entry)\b.*?</\1\s*>")


def _fromstring(datos):
    return (_ET_SEGURO or ET).fromstring(datos)


def _raiz_tolerante(texto: str):
    """Feed truncado: se conservan solo los ítems completos (se descarta el último, incompleto)."""
    bloques = [m.group(0) for m in _RE_ITEM.finditer(texto)]
    if not bloques:
        raise ET.ParseError("feed ilegible y sin ítems completos")
    decl = ""
    tag = re.search(r"(?is)<(rss|rdf:RDF|feed)\b[^>]*>", texto)
    if tag:
        decl = " ".join(re.findall(r'xmlns(?::[\w.-]+)?\s*=\s*"[^"]*"', tag.group(0)))
    return _fromstring(f"<raiz {decl}>" + "".join(bloques) + "</raiz>")


def parsear_feed(xml_bytes: bytes | str) -> list[dict]:
    """RSS 2.0, RSS 1.0 (RDF) o Atom -> [{titulo, url, fecha(datetime), cuerpo_html, ids}].

    Tolerante a XML truncado (MED01 v1.1): si no parsea entero, usa los ítems completos."""
    if isinstance(xml_bytes, str):
        xml_bytes = xml_bytes.encode("utf-8")
    try:
        raiz = _fromstring(xml_bytes)
    except ET.ParseError:
        raiz = _raiz_tolerante(xml_bytes.decode("utf-8", "ignore"))
    out = []
    for it in raiz.iter():
        if _local(it.tag) not in ("item", "entry"):
            continue
        d: dict = {"titulo": "", "url": "", "fecha": None, "cuerpo_html": "", "ids": []}
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
            elif t in ("guid", "identifier", "doi", "id"):
                d["ids"].append((ch.text or "").strip())
        if d["titulo"] and d["url"]:
            out.append(d)
    return out


_CACHE_ROBOTS: dict = {}


def robots_permite(url: str, leer=_get, cache: dict | None = None) -> bool:
    """robots.txt del origen de `url` (urllib.robotparser). 4xx = sin restricciones; cualquier otro
    fallo al leerlo = no se lee (lectura conservadora)."""
    cache = _CACHE_ROBOTS if cache is None else cache
    u = urlparse(url)
    origen = f"{u.scheme}://{u.netloc}"
    if origen not in cache:
        rp = urllib.robotparser.RobotFileParser()
        try:
            rp.parse(leer(origen + "/robots.txt").decode("utf-8", "replace").splitlines())
            cache[origen] = rp
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                rp.parse([])
                cache[origen] = rp
            else:
                cache[origen] = False
        except Exception:  # noqa: BLE001
            cache[origen] = False
    rp = cache[origen]
    return bool(rp) and rp.can_fetch("OTM-Prensa", url)


def bajar_cuerpo(url: str, leer=_get, cache: dict | None = None) -> str:
    """Párrafos <p> de la página original, solo en memoria. Respeta robots.txt.
    Lanza ErrorLectura (con el motivo) si robots.txt lo prohíbe o la página no se puede leer."""
    if not robots_permite(url, leer, cache):
        raise ErrorLectura("robots.txt prohíbe (o no permite verificar) la lectura del enlace original")
    try:
        pag = leer(url).decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        raise ErrorLectura(f"no se pudo leer el enlace original ({type(e).__name__})") from e
    ps = re.findall(r"(?is)<p[^>]*>(.*?)</p>", pag)
    return "\n".join(f"<p>{p}</p>" for p in ps)


# ------------------------------------------------------------------ gnews
def es_google_news(url: str) -> bool:
    return urlparse(url).netloc.lower().endswith("news.google.com")


def _final_http(url: str) -> str | None:
    """Sigue redirecciones HTTP; devuelve la URL final o el enlace canónico incrustado en la página."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:  # noqa: S310
        final = r.geturl()
        if not es_google_news(final):
            return final
        m = re.search(r'data-n-au="([^"]+)"', r.read(200000).decode("utf-8", "replace"))
        return html.unescape(m.group(1)) if m else None


def resolver_gnews(url: str, abrir=_final_http) -> str | None:
    """Enlace de news.google.com -> URL del medio original, o None si no se puede resolver."""
    if not es_google_news(url):
        return url
    ident = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
    try:  # ids antiguos: base64 con la URL en claro
        crudo = base64.urlsafe_b64decode(ident + "=" * (-len(ident) % 4))
        m = re.search(rb"https?://[\x21-\x7e]+", crudo)
        if m:
            cand = m.group(0).decode("ascii")
            if not es_google_news(cand):
                return cand
    except Exception:  # noqa: BLE001, S110
        pass
    try:
        r = abrir(url)
    except Exception:  # noqa: BLE001
        return None
    return r if r and not es_google_news(r) else None


def medio_de_url(url: str, med: dict) -> dict | None:
    """Medio de MED01 al que pertenece la URL (por dominio), o None."""
    u = urlparse(url)
    host, ruta = u.netloc.lower().split(":")[0], u.path.lower()
    ids = {m["id"]: m for m in med["medios"]}
    for mid, doms in DOMINIOS.items():
        if mid not in ids:
            continue
        for d in doms:
            dh, _, dr = d.partition("/")
            if (host == dh or host.endswith("." + dh)) and (not dr or ruta.startswith("/" + dr)):
                return ids[mid]
    return None


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


def _prefijo_doi(medio: dict) -> str | None:
    m = re.search(r"solo DOI con prefijo (\w+)", medio.get("filtro", ""))
    return m.group(1) if m else None


def recolectar(medio: dict, max_n: int, ahora: datetime, leer=_get, resolver=resolver_gnews,
               descartes: list | None = None, med: dict | None = None) -> list[dict]:
    """Candidatos recientes (<= dias_maximos) de un medio. `leer(url)->bytes` y `resolver` inyectables.

    - Filtro DOI (p. ej. Nature: solo d41586) según `filtro` de MED01.
    - Ítems de news.google.com: se resuelve el enlace al medio original; `url` y `medio_id` son los
      del original (debe estar en MED01); si no se resuelve, se descarta con motivo en `descartes`."""
    med = med or cargar_med01()
    descartes = descartes if descartes is not None else []
    doi = _prefijo_doi(medio)
    brutos: list[dict] = []
    vistos: set[str] = set()
    principal_ok = False
    for url, _area in urls_de_medio(medio):
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
            if doi and not any(doi in x for x in [it["url"], *it["ids"]]):
                continue
            vistos.add(it["url"])
            brutos.append(it)
    brutos.sort(key=lambda c: c["fecha"], reverse=True)
    cands: list[dict] = []
    for it in brutos:
        if len(cands) >= max_n:
            break
        dest, titulo = medio, it["titulo"]
        if es_google_news(it["url"]):
            titulo = re.sub(r"\s+-\s+[^-]{2,40}$", "", titulo)
            real = resolver(it["url"])
            if not real:
                descartes.append({"url": it["url"], "medio_id": medio["id"],
                                  "motivo": "gnews: no se pudo resolver la redirección al medio original"})
                continue
            dest = medio_de_url(real, med)
            if dest is None:
                descartes.append({"url": real, "medio_id": medio["id"],
                                  "motivo": "gnews: el medio original no está en MED01"})
                continue
            it = {**it, "url": real}
        cands.append({**it, "titulo": titulo, "medio_id": dest["id"], "medio": dest["nombre"],
                      "idioma": dest["idioma"]})
    return cands


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
    # MED01 v1.1: el cuerpo se lee del enlace original; solo La Tercera lo trae completo en el feed.
    # (`bajar=None` = modo fixture/test: se usa el cuerpo entregado en el candidato.)
    usar_feed = bajar is None or c["medio_id"] in CUERPO_EN_FEED
    parrafos = parrafos_de(c.get("cuerpo_html", "")) if usar_feed else []
    if sum(len(p) for p in parrafos) < 400 and bajar:
        try:
            extra = parrafos_de(bajar(c["url"]))
        except ErrorLectura as e:
            if not parrafos:
                return fin(motivo=str(e))
            extra = []
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


_AUTO = object()


def explorar(medios_ids: list[str] | None = None, max_por_medio: int = 8, *, cliente=None,
             ahora: datetime | None = None, leer=_get, bajar=_AUTO, tope_usd: float = 1.0,
             resolver=resolver_gnews) -> dict:
    ahora = ahora or datetime.now(timezone.utc)
    med = cargar_med01()
    if bajar is _AUTO:  # lectura del enlace original con el mismo `leer`, respetando robots.txt
        bajar = functools.partial(bajar_cuerpo, leer=leer, cache=None if leer is _get else {})
    medios = [m for m in med["medios"] if not medios_ids or m["id"] in medios_ids]
    noticias, descartes, gasto = [], [], 0.0
    for m in medios:
        desc_rec: list = []
        cands = recolectar(m, max_por_medio, ahora, leer, resolver, desc_rec, med)
        descartes += desc_rec
        for c in cands:
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
