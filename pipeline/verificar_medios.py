"""Verificación semanal de los medios de MED01 (sin LLM, costo 0).

Para cada medio de la versión más alta de MED01 y para cada URL de acceso (principal, secciones y
respaldo): descarga el robots.txt del origen, comprueba si el agente y la ruta están permitidos, descarga
el RSS/listado (solo si robots lo permite) y cuenta los ítems. User-agent identificable, timeouts y
pausa entre peticiones al mismo origen.

    python -m pipeline.verificar_medios [--med01 RUTA] [--salida DIR] [--medios id ...] [--espera 1.0]

Escribe `pipeline/state/medios/verificacion_<AAAA-MM-DD>.json`. NO modifica `insumos/`: MED01 es de solo
lectura, y el explorador ya usa el respaldo en tiempo de ejecución (principal -> respaldo). El resultado
dice qué acceso conviene a cada medio hoy (`recomendacion`); un cambio en MED01 es una versión nueva que
decide una persona. Sale con 0 aunque haya medios caídos (es un informe); `--estricto` sale con 1 si algún
medio queda sin acceso.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

import yaml

RAIZ = Path(__file__).resolve().parents[1]
UA = "OTM-Prensa/1.0 (observatorio academico; PUC Chile; verificar-medios; +https://github.com/carlosrojasbruna/otm-prensa)"
AGENTE_ROBOTS = "OTM-Prensa"
TIMEOUT = 20
MAX_BYTES = 2_000_000

# fetch(url, timeout) -> (status, content_type, cuerpo_bytes). Lanza OSError ante fallo de red.
Fetch = Callable[[str, float], tuple]


def fetch_real(url: str, timeout: float = TIMEOUT) -> tuple:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — URLs de MED01
            return r.status, r.headers.get("Content-Type", ""), r.read(MAX_BYTES)
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", "") if e.headers else "", b""


def _clave_version(ruta: Path) -> tuple:
    m = re.search(r"_v(\d+)\.(\d+)_", ruta.name)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def ruta_med01(raiz: Path = RAIZ) -> Path:
    rutas = sorted((raiz / "insumos" / "medios").glob("MED01_*.yaml"), key=_clave_version)
    if not rutas:
        raise FileNotFoundError("no hay MED01_*.yaml en insumos/medios")
    return rutas[-1]


def urls_de(medio: dict) -> list[dict]:
    """[{url, rol, area}] principal, secciones y respaldo (sin repetir)."""
    out, vistas = [], set()

    def add(url, rol, area=None):
        if url and url not in vistas:
            vistas.add(url)
            out.append({"url": url, "rol": rol, "area": area})

    add(medio.get("url"), "principal")
    for s in medio.get("secciones") or []:
        add(s.get("url"), "seccion", s.get("area"))
    add((medio.get("respaldo") or {}).get("url"), "respaldo")
    return out


def contar_items(cuerpo: bytes) -> tuple[bool, int]:
    """(es_feed, items). Tolerante a XML truncado: cuenta etiquetas, no parsea todo el documento."""
    txt = cuerpo[:MAX_BYTES].decode("utf-8", "replace")
    cabeza = txt.lstrip()[:600].lower()
    es_feed = bool(re.search(r"<(rss|feed|rdf:rdf)\b", cabeza)) or (cabeza.startswith("<?xml") and bool(re.search(r"<(rss|feed|rdf:rdf)\b", txt[:2000].lower())))
    if not es_feed:
        return False, 0
    n = len(re.findall(r"<(?:item|entry)\b", txt, flags=re.I))
    return True, n


class Robots:
    """robots.txt por origen, con caché. 4xx = sin restricciones; cualquier otro fallo = no permitido."""

    def __init__(self, fetch: Fetch, timeout: float):
        self.fetch, self.timeout, self.cache = fetch, timeout, {}

    def consultar(self, url: str) -> dict:
        u = urlparse(url)
        origen = f"{u.scheme}://{u.netloc}"
        if origen not in self.cache:
            info = {"origen": origen, "estado": None, "rp": None, "error": None}
            try:
                status, _ct, cuerpo = self.fetch(origen + "/robots.txt", self.timeout)
                info["estado"] = status
                rp = urllib.robotparser.RobotFileParser()
                if 200 <= status < 300:
                    rp.parse(cuerpo.decode("utf-8", "replace").splitlines())
                    info["rp"] = rp
                elif 400 <= status < 500:
                    rp.parse([])
                    info["rp"] = rp
                else:
                    info["error"] = f"robots.txt respondió {status}"
            except Exception as e:  # noqa: BLE001 — red: se registra y se trata como no verificable
                info["error"] = f"{type(e).__name__}: {str(e)[:120]}"
            self.cache[origen] = info
        info = self.cache[origen]
        permitido = None if info["rp"] is None else bool(info["rp"].can_fetch(AGENTE_ROBOTS, url))
        return {"origen": info["origen"], "robots_http": info["estado"], "robots_permitido": permitido, "robots_error": info["error"]}


def verificar_url(item: dict, robots: Robots, fetch: Fetch, timeout: float, esperar: Callable[[str], None]) -> dict:
    r = {**item, **robots.consultar(item["url"]), "http": None, "content_type": None, "es_feed": False,
         "items": 0, "ms": None, "error": None, "descargado": False}
    if r["robots_permitido"] is None:
        r["error"] = "robots.txt no verificable: no se descarga (lectura conservadora)"
    elif r["robots_permitido"] is False:
        r["error"] = "robots.txt no permite este agente en esta ruta: no se descarga"
    else:
        esperar(r["origen"])
        t0 = time.monotonic()
        try:
            status, ct, cuerpo = fetch(item["url"], timeout)
            r.update(http=status, content_type=ct, descargado=True, ms=round((time.monotonic() - t0) * 1000))
            if 200 <= status < 300:
                r["es_feed"], r["items"] = contar_items(cuerpo)
                if not r["es_feed"]:
                    r["error"] = "la respuesta no es un feed RSS/Atom (probablemente HTML)"
                elif r["items"] == 0:
                    r["error"] = "feed sin ítems"
            else:
                r["error"] = f"HTTP {status}"
        except Exception as e:  # noqa: BLE001
            r["error"] = f"{type(e).__name__}: {str(e)[:120]}"
    r["ok"] = bool(r["es_feed"] and r["items"] > 0 and r["robots_permitido"])
    return r


def verificar_medio(medio: dict, robots: Robots, fetch: Fetch, timeout: float, esperar) -> dict:
    urls = [verificar_url(u, robots, fetch, timeout, esperar) for u in urls_de(medio)]
    principal = next((u for u in urls if u["rol"] == "principal"), None)
    respaldo = next((u for u in urls if u["rol"] == "respaldo"), None)
    if principal and principal["ok"]:
        rec = {"estado": "ok", "acceso": medio.get("acceso"), "url": principal["url"]}
    elif respaldo and respaldo["ok"]:
        rec = {"estado": "usar_respaldo", "acceso": (medio.get("respaldo") or {}).get("acceso", "gnews"), "url": respaldo["url"],
               "motivo": principal["error"] if principal else "sin URL principal"}
    else:
        rec = {"estado": "sin_acceso", "acceso": None, "url": None,
               "motivo": "; ".join(f"{u['rol']}: {u['error']}" for u in urls if u["error"]) or "sin URL"}
    return {"id": medio["id"], "nombre": medio.get("nombre"), "acceso_med01": medio.get("acceso"),
            "url_verificar": bool(medio.get("url_verificar")), "rol": medio.get("rol"),
            "recomendacion": rec, "urls": urls}


def verificar(med01: dict, *, fetch: Fetch = fetch_real, timeout: float = TIMEOUT, espera: float = 1.0,
              solo: list[str] | None = None, ahora: datetime | None = None, dormir=time.sleep) -> dict:
    robots = Robots(fetch, timeout)
    ultimo: dict[str, float] = {}

    def esperar(origen: str) -> None:   # cortesía: pausa entre peticiones al mismo origen
        t = ultimo.get(origen)
        if t is not None and espera > 0:
            falta = espera - (time.monotonic() - t)
            if falta > 0:
                dormir(falta)
        ultimo[origen] = time.monotonic()

    medios = [m for m in med01["medios"] if not solo or m["id"] in solo]
    res = [verificar_medio(m, robots, fetch, timeout, esperar) for m in medios]
    cuenta = {e: sum(1 for m in res if m["recomendacion"]["estado"] == e) for e in ("ok", "usar_respaldo", "sin_acceso")}
    ahora = ahora or datetime.now(timezone.utc)
    return {"fecha": ahora.strftime("%Y-%m-%d"), "generado": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "med01_version": med01.get("version"), "user_agent": UA, "timeout_s": timeout,
            "costo_usd": 0.0, "resumen": {"medios": len(res), **cuenta}, "medios": res}


def resumen_texto(rep: dict) -> str:
    L = [f"MED01 v{rep['med01_version']} · {rep['fecha']} · " + " · ".join(f"{k}={v}" for k, v in rep["resumen"].items())]
    for m in rep["medios"]:
        rec = m["recomendacion"]
        extra = ""
        if rec["estado"] != "ok":
            extra = f"  ({rec.get('motivo', '')[:120]})"
        n = max((u["items"] for u in m["urls"] if u["url"] == rec.get("url")), default=0) if rec.get("url") else 0
        L.append(f"  {m['id']:<12} {rec['estado']:<14} items={n:<3}{extra}")
    return "\n".join(L)


def main(argv: list[str] | None = None, *, fetch: Fetch = fetch_real) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline.verificar_medios", description=__doc__.split("\n")[0])
    ap.add_argument("--med01", type=Path, help="ruta de MED01 (por defecto, la versión más alta)")
    ap.add_argument("--salida", type=Path, default=RAIZ / "pipeline" / "state" / "medios")
    ap.add_argument("--medios", nargs="*", help="ids (por defecto, todos)")
    ap.add_argument("--espera", type=float, default=1.0, help="segundos entre peticiones al mismo origen")
    ap.add_argument("--timeout", type=float, default=TIMEOUT)
    ap.add_argument("--estricto", action="store_true", help="salir con 1 si algún medio queda sin acceso")
    a = ap.parse_args(argv)
    med01 = yaml.safe_load((a.med01 or ruta_med01()).read_text(encoding="utf-8"))
    rep = verificar(med01, fetch=fetch, timeout=a.timeout, espera=a.espera, solo=a.medios)
    a.salida.mkdir(parents=True, exist_ok=True)
    destino = a.salida / f"verificacion_{rep['fecha']}.json"
    destino.write_text(json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(resumen_texto(rep))
    print(f"escrito {destino}")
    return 1 if a.estricto and rep["resumen"]["sin_acceso"] else 0


if __name__ == "__main__":
    sys.exit(main())
