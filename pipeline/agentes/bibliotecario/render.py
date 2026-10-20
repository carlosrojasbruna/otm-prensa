"""Render de tarea y guía a Markdown para lectura humana en el repositorio publicado.

Determinista, sin modelo. Sigue las secciones de PLT01 v0.2 (tarea) y PLT02 v0.1 (guía docente).
El JSON es la fuente de verdad: el Markdown solo lo presenta y no agrega contenido.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping

import yaml

FASES = ("P1-MRS", "P2-RM", "P3-MM", "P4-WM", "P5-INT", "P6-VAL", "P7-EXP")
NOMBRE_FASE = {"P1-MRS": "Comprender", "P2-RM": "Simplificar", "P3-MM": "Matematizar", "P4-WM": "Trabajar",
               "P5-INT": "Interpretar", "P6-VAL": "Validar", "P7-EXP": "Exponer"}


def _c(v: Any) -> str:
    """Celda de tabla: sin saltos de línea ni barras que rompan la tabla."""
    if v is None:
        return "—"
    if isinstance(v, (list, tuple)):
        v = "; ".join(_c(x) for x in v)
    return str(v).replace("\r", " ").replace("\n", " ").replace("|", "\\|").strip() or "—"


def _tabla(cabecera: Iterable[str], filas: Iterable[Iterable[Any]]) -> list[str]:
    cab = list(cabecera)
    L = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    L += ["| " + " | ".join(_c(x) for x in f) + " |" for f in filas]
    return L


def _bloque(etiqueta: str, texto: str) -> list[str]:
    return [f"```text {etiqueta}", texto.strip(), "```"]


def _lista(items: Iterable[Any]) -> list[str]:
    return [f"- {x}" for x in items]


# --------------------------------------------------------------------------- tarea (PLT01)
def _frontmatter(t: Mapping[str, Any]) -> dict:
    claves = ("id", "titulo", "estado", "version", "fecha", "noticia", "nivel_principal", "sub_tramo", "variantes",
              "area", "contenidos_matematicos", "tiempo_estimado", "rubrica_rub01", "rubrica_rub02", "modelo_y_prompt")
    return {k: t[k] for k in claves if k in t}


def render_tarea(t: Mapping[str, Any], evaluacion: Mapping[str, Any] | None = None) -> str:
    est, ts = t["estudiante"], t["task_space"]
    L = [f"# {t['titulo']}", "",
         f"Tarea `{t['id']}` · versión {t['version']} · {t['fecha']} · nivel {t['nivel_principal']} · "
         f"{t['tiempo_estimado']}. Licencia CC BY-NC-SA 4.0. Generado desde `tarea` (JSON, fuente de verdad).", "",
         "```yaml frontmatter",
         yaml.safe_dump(_frontmatter(t), allow_unicode=True, sort_keys=False, width=1000).rstrip(),
         "```", "", "## 1. Enunciado para estudiantes (nivel principal)", ""]
    L += _bloque("enunciado_es", est["enunciado_es"]) + [""] + _bloque("foto_descripcion", est["foto_descripcion"])
    for lado, titulo in (("abajo", "1.1 Variante hacia abajo"), ("arriba", "1.2 Variante hacia arriba")):
        v = (t.get("variantes_detalle") or {}).get(lado)
        L += ["", f"### {titulo}" + (f" (tramo {v['tramo']})" if v else ""), "",
              v["cambios"] if v else "No hay."]
    L += ["", "## 2. Datos y recursos no reveladores", ""]
    recursos = list(t.get("recursos_de_entrada", [])) + list(est.get("recursos_a_solicitud", []))
    L += _tabla(("Recurso", "Qué es", "Contenido", "Disponibilidad", "Fase que alimenta", "Fuente"),
                ((r["id"], r["que_es"], r["contenido"], r["disponibilidad"], r["fase"], r["fuente"])
                 for r in sorted(recursos, key=lambda r: r["id"])))
    L += ["", "Los recursos `de_entrada` están incorporados en el enunciado. Ningún recurso contiene el modelo, "
              "la regla ni la estructura de la solución.", "", "## 3. Mapa a priori del ciclo", ""]
    mapa = t["mapa_ciclo"]
    L += _tabla(("Fase", "Decisión o actividad esperable", "Evidencia observable", "Bloqueo probable"),
                ((f"{f} {NOMBRE_FASE[f]}", mapa[f]["decision"], mapa[f]["evidencia"], mapa[f].get("bloqueo_probable"))
                 for f in FASES if f in mapa))
    rs = ts["reference_solution"]
    L += ["", "## 4. Espacio de soluciones", "",
          "> Para docentes, evaluador y simulador-codificador; **no** se entrega a estudiantes.", "",
          "### Supuestos necesarios", "", *_lista(ts["required_assumptions"]), "",
          "### Solución de referencia", "", rs["steps"], "", f"**Resultado.** {rs['result']}", "",
          f"**Rango aceptable.** {rs['acceptable_range']}", "", "### Rutas", ""]
    L += _tabla(("Ruta", "Nombre", "Nivel", "Modelo", "Resultado"),
                ((r["id"], r["nombre"], r["nivel"], r["modelo"], r["resultado"]) for r in ts["routes"]))
    mi = ts["modelo_inadecuado"]
    L += ["", f"### Modelo inadecuado ({mi['id']})", "", mi["por_que_falla"], "",
          "### Evidencia de validación (independiente del modelo)", "", ts["validation_evidence"], ""]
    L += ["## 5. Rúbrica aplicada (RUB01)", ""]
    crit = ((evaluacion or {}).get("rub01") or {}).get("criterios")
    if isinstance(crit, Mapping) and crit:
        filas = [(i, k, c.get("puntaje"), c.get("justificacion"), c.get("mejora_minima"))
                 for i, (k, c) in enumerate(crit.items(), 1)]
        total = evaluacion["rub01"]["total"]
        L += _tabla(("#", "Criterio", "Puntaje", "Justificación", "Mejora mínima si < 2"), filas)
        L += [f"| | **Total** | **{total}/24** | | |"]
    else:
        pc = t["rubrica_rub01"]["por_criterio"]
        L += _tabla(("#", "Criterio", "Puntaje"), ((i, k, v) for i, (k, v) in enumerate(pc.items(), 1)))
        L += [f"| | **Total** | **{t['rubrica_rub01']['total']}/24** |"]
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- guía (PLT02)
def _tabla_bloqueos(trazas: Mapping[str, Any] | None) -> list[str]:
    if not trazas or not trazas.get("por_corrida"):
        return []
    corr = trazas["por_corrida"]
    n = len(corr)
    cuenta = Counter(b["transicion"] for c in corr for b in {x["transicion"]: x for x in c.get("bloqueos", [])}.values())
    if not cuenta:
        return ["", f"Tabla agregada: ninguno de los {n} grupos simulados registró bloqueos."]
    return ["", f"Tabla agregada de bloqueos ({n} grupos simulados):", "",
            *_tabla(("Transición", "Grupos que se trabaron", "%"),
                    ((t, f"{k}/{n}", f"{round(100 * k / n)} %") for t, k in sorted(cuenta.items())))]


def render_guia(g: Mapping[str, Any], trazas: Mapping[str, Any] | None = None) -> str:
    f, n = g["ficha"], g["ficha"]["noticia"]
    L = [f"# Guía docente · {f['titulo']}", "",
         f"Tarea `{g['tarea_id']}` · guía versión {g['version']} · {g['fecha']}. Licencia CC BY-NC-SA 4.0. "
         "Generado desde `guia` (JSON, fuente de verdad).", "", "## 0. Ficha", ""]
    L += _tabla(("Campo", "Valor"), (
        ("Título", f["titulo"]),
        ("Noticia", ", ".join([n["medio"], *([f"«{n['titulo']}»"] if n.get("titulo") else []), n["fecha"], n["url"]])),
        ("Nivel principal", f["nivel_principal"] + (f" ({f['sub_tramo']})" if f.get("sub_tramo") else "")),
        ("Variantes", f.get("variantes")),
        ("Contenidos", f["contenidos"]), ("Tiempo", f["tiempo"]), ("Puntaje RUB01", f"{f['puntaje_rub01']}/24"),
        ("Versión y fecha", f"v{f['version']} · {f['fecha']}"), ("Cambios", f.get("cambios"))))
    m = g["meta"]
    L += ["", "## 1. Meta de la clase (C1)", "", m["que_observar"], ""]
    if m.get("contenido"):
        L += [f"**Contenido.** {m['contenido']}", ""]
    L += ["**Subcompetencias de modelación.**", "", *_lista(m["subcompetencias"]), ""]
    if m.get("meta_social"):
        L += [f"**Meta social.** {m['meta_social']}", ""]
    L += ["**Evidencia que se recoge.**", "", *_lista(m["evidencia"])]
    a = g["analisis_a_priori"]
    L += ["", "## 2. Análisis a priori del espacio de soluciones (C2)", "", "### Rutas", ""]
    L += _tabla(("Ruta", "Nombre", "Nivel", "Modelo"), ((r["id"], r["nombre"], r["nivel"], r["modelo"])
                                                       for r in a["rutas"]))
    mi = a["modelo_inadecuado"]
    L += ["", f"### Modelo inadecuado ({mi['id']})", "", mi["por_que_falla"], "", "### Solución de referencia", "",
          a["solucion_referencia"], "", f"**Rango aceptable.** {a['rango_aceptable']}", "",
          "### Barreras anticipadas por fase", ""]
    L += _tabla(("Fase", "Barrera"), ((b["fase"], b["barrera"]) for b in a["barreras_por_fase"]))
    o = g["organizacion"]
    L += ["", "## 3. Organización (C3, C4, C7)", ""]
    L += _tabla(("Momento", "Tiempo", "Qué hacen los estudiantes", "Qué hace el docente"),
                ((x["momento"], x["tiempo"], x["estudiantes"], x["docente"]) for x in o["momentos"]))
    L += ["", f"**Agrupamiento.** {o['agrupamiento']}", "", f"**Roles.** {o['roles']}", "",
          "**Producciones que se registran.**", "", *_lista(o["producciones"]), "",
          f"**Tecnología.** {o['tecnologia']}", "", "## 4. Escenarios simulados (C2, C6)", "",
          "Derivados de las trazas del simulador; cada escenario cita las corridas que lo respaldan.", ""]
    for e in g["escenarios"]:
        bloq = "; ".join(f"{b['transicion']}: {b['como_se_destrabo']}" for b in e.get("bloqueos", [])) or "sin bloqueos"
        L += [f"### {e['id']} · {e['nombre']}", ""]
        L += _tabla(("Campo", "Valor"), (
            ("Corridas", ", ".join(e["corridas"])), ("Perfil del grupo", e["perfil"]),
            ("Ruta observada", " → ".join(e["ruta"])), ("Supuestos que emergieron", e["supuestos"]),
            ("Modelo al que llegaron", e["modelo"]), ("Dónde se trabaron y cómo se destrabaron", bloq)))
        L += ["", f"**Qué aprende el curso.** {e['que_aprende']}", "", "**Extracto de diálogo simulado.**", ""]
        L += [f"> **{x['hablante']}:** {_c(x['texto'])}  " for x in e.get("extracto_dialogo", [])]
        L += [""]
    L += _tabla_bloqueos(trazas)
    L += ["", "## 5. Intervenciones graduadas por bloqueo anticipado (C5, C6)", "",
          "La ayuda mínima primero; diagnosticar antes de intervenir. Ninguna ayuda entrega la regla.", ""]
    L += _tabla(("Bloqueo", "Z1–Z2 motivación / retroalimentación", "Z3 estratégica general",
                 "Z4 estratégica de contenido", "Z5 contenido (último recurso)"),
                ((i["bloqueo"], i["z1_z2"], i["z3"], i["z4"], i["z5"]) for i in g["intervenciones"]))
    p = g["puesta_en_comun"]
    L += ["", "## 6. Puesta en común: orquestar soluciones múltiples (C8)", "", "### Selección y orden", "",
          *[f"{k}. {x}" for k, x in enumerate(p["seleccion_y_orden"], 1)], "", "### Preguntas", "",
          *_lista(p["preguntas"]), "", "### Contraste con la evidencia independiente", "", p["contraste_validacion"],
          "", "## 7. Evaluación del trabajo del estudiante", ""]
    ev = (g.get("evaluacion_estudiante") or {}).get("por_fase")
    if ev:
        L += _tabla(("Fase", "Nivel 1", "Nivel 2", "Nivel 3"), ((x["fase"], *x["niveles"]) for x in ev))
    else:
        L += ["Pendiente en PLT02 v0.1 (rúbrica por fase del ciclo); esta versión de la guía no la incluye."]
    v = g["variantes_y_continuidad"]
    L += ["", "## 8. Variantes y continuidad (P3, C9)", "", f"**Uso de variantes.** {v['uso_variantes']}", "",
          f"**Acostumbramiento.** {v['acostumbramiento']}", "",
          f"**Tarea siguiente.** {v['tarea_siguiente'] or 'No definida.'}", "", "## 9. Materiales", ""]
    L += _tabla(("Material", "Archivo"), g["materiales"].items())
    tz = g["trazabilidad"]

    def _rev(r):
        return f"{r['revisor']} ({r['fecha']})" if r else "pendiente"
    L += ["", "## 10. Trazabilidad", ""]
    L += _tabla(("Paso", "Registro"), (
        ("Noticia", tz["noticia_url"]),
        ("Diseño", f"{tz['diseno']['modelo']}, prompt {tz['diseno']['version_prompt']}"),
        ("RUB01", f"{tz['rub01_total']}/24"), ("Revisión humana 1", _rev(tz["revision_humana_1"])),
        ("Simulación", f"{tz['simulacion']['n_grupos']} grupos, diseño {tz['simulacion']['diseno']}"),
        ("Guía", ", ".join(f"{k}: {v}" for k, v in (g.get("modelo_y_prompt") or {}).items())),
        ("Revisión humana 2", _rev(tz["revision_humana_2"])), ("Commit", tz.get("commit") or "—")))
    return "\n".join(L) + "\n"
