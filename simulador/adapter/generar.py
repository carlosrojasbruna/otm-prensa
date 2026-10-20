"""Genera TAREA.md, PERFILES.md y PROMPTS.md (formato de bloques que lee sim.py) desde una tarea PLT01.

Origen de cada bloque (SIM01 §1):
  TAREA.md     enunciado_es, foto_descripcion      <- tarea["estudiante"] vía vista_estudiante (invariante 6)
  PERFILES.md  niveles (MAR03 §3), estilos (INS08 sin cambios), contexto_base, diseno_otm
  PROMPTS.md   student_system, student_turn, coder_user (INS09 v0.2 sin cambios, salvo la edad),
               coder_system (INS09 reescrito: recibe task_space, sin F1-F6), coder_schema
INS08/INS09 se leen del repo del simulador (rutas de sim.py), no se copian al repo.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from pipeline.invariantes import textos_de, validar_contra_esquema, vista_estudiante

from . import _comun, niveles
from .aislamiento import _TOKENS, AislamientoError, verificar_payload_estudiante

COMPOSICIONES = {"VV": ["V", "V"], "AA": ["A", "A"]}
# 6 corridas: N1, N2/N3, N4 x VV, AA (SIM01 §1). El nivel intermedio alterna N2 (VV) y N3 (AA).
CORRIDAS_DISENO_6 = [
    {"nivel": "N1", "composicion": "VV"}, {"nivel": "N1", "composicion": "AA"},
    {"nivel": "N2", "composicion": "VV"}, {"nivel": "N3", "composicion": "AA"},
    {"nivel": "N4", "composicion": "VV"}, {"nivel": "N4", "composicion": "AA"},
]


def modelo_codificador_defecto() -> str:
    """pipeline/config.yaml::modelos.simulador_codificador (claude-opus-5-5 de partida, el de INS08)."""
    from pipeline.llm import modelo_de
    return modelo_de("simulador_codificador")


MODELO_CODIFICADOR_DEFECTO = modelo_codificador_defecto()   # informativo; generar_todo relee config.yaml

CODER_SYSTEM = """Eres un investigador en didáctica de la matemática y codificas transcripciones de pares de estudiantes que resuelven una tarea de modelación. Codificas de forma deductiva, con el libro de códigos que se entrega abajo. Te basas solo en lo que está escrito en la transcripción: no supones intenciones que no se expresan. No conoces el perfil de los estudiantes, y no debes intentar deducirlo.

TAREA QUE RESOLVIERON:
{enunciado}
{foto}

ESPACIO DE LA TAREA (solo para ti; los estudiantes no lo conocen):
__TASK_SPACE__

CÓDIGOS DE FASE (uno dominante por turno; opcionalmente uno secundario):
P1-MRS comprender, construir la representación de la situación, identificar la incógnita | P2-RM simplificar o estructurar, hacer supuestos, descartar datos, dibujo esquemático de la situación | P3-MM matematizar, traducir a un objeto matemático | P4-WM calcular o manipular | P5-INT interpretar el resultado en el contexto | P6-VAL validar: plausibilidad, revisar supuestos, precisión | P7-EXP exponer la respuesta final | EMK usar conocimiento extra-matemático del mundo real | OFF fuera de la tarea u organizacional.

EVENTOS (cero o más por turno): DIST (menciona o usa un dato que el modelo de referencia no necesita) | PREC (precisión excesiva, por ejemplo decimales sin sentido) | STRAT (uso consciente de una estrategia: planificar, dibujar para entender, monitorear, "revisemos") | ASSUME (declara un supuesto) | LEX (duda sobre el significado de una palabra).

BLOQUEO: hay bloqueo cuando hay 2 o más turnos consecutivos en una transición sin avance, más una de estas señales: duda explícita, objeción, "no sé cómo seguir", repetición o abandono. Códigos: B12 (comprender→simplificar), B23 (modelo real→matemático), B34 (matemático→cálculo), B45 (cálculo→interpretación), B56 (interpretación→validación), B67 (validación→exposición). Para cada bloqueo indica cómo se resolvió: peer (lo destraba el compañero), self (el mismo estudiante) o unresolved.

SUPUESTOS: lista, con palabras breves, los supuestos que el par declara o usa de forma explícita (por ejemplo "velocidad constante"). No agregues supuestos que solo aparecen en el espacio de la tarea.

MODELO: nombra con una o dos palabras el modelo matemático con que el par obtiene su respuesta (por ejemplo "proporcional", "lineal", "exponencial", "geométrico").

VALIDACIÓN: true solo si hay al menos un turno de validación sustantiva (se discute la plausibilidad, un supuesto o se revisa con un argumento); una mención vacía ("está bien, ¿no?") es false.

RUTA: clasifica la corrida con el id de una ruta del espacio de la tarea (R1, R2, ...) o "otra" si ninguna corresponde. Puede haber más de una; indica la principal.

Responde solo con el JSON que pide el esquema."""

CODER_SCHEMA = {
    "type": "object",
    "properties": {
        "turnos": {"type": "array", "items": {"type": "object", "properties": {
            "n": {"type": "integer"}, "fase": {"type": "string"}, "fase_secundaria": {"type": ["string", "null"]},
            "eventos": {"type": "array", "items": {"type": "string"}}}, "required": ["n", "fase", "eventos"]}},
        "bloqueos": {"type": "array", "items": {"type": "object", "properties": {
            "codigo": {"type": "string"}, "turnos": {"type": "array", "items": {"type": "integer"}},
            "resolucion": {"type": "string", "enum": ["peer", "self", "unresolved"]},
            "descripcion": {"type": "string"}},
            "required": ["codigo", "turnos", "resolucion", "descripcion"]}},
        "supuestos": {"type": "array", "items": {"type": "string"}},
        "modelo": {"type": "string"},
        "validacion": {"type": "boolean"},
        "respuesta_final": {"type": "object", "properties": {"texto": {"type": "string"}},
                            "required": ["texto"]},
        "ruta_principal": {"type": "string"},
        "rutas": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["turnos", "bloqueos", "supuestos", "modelo", "validacion", "respuesta_final",
                 "ruta_principal", "rutas"],
}


# --------------------------------------------------------------------------- utilidades
def _bloque(lang: str, bid: str, contenido: str | Mapping | list) -> str:
    cuerpo = contenido if isinstance(contenido, str) else json.dumps(contenido, ensure_ascii=False, indent=2)
    if "```" in cuerpo:
        raise ValueError(f"el bloque {bid} contiene ``` y rompería el formato de sim.py")
    return f"```{lang} {bid}\n{cuerpo}\n```"


def bloques_de(ruta: Path) -> dict:
    """{id: contenido} de los bloques de un .md, con el mismo regex que sim.bloques."""
    txt = Path(ruta).read_text(encoding="utf-8")
    out = {}
    for lang, bid, body in re.findall(r"```(json|text) (\w+)\n(.*?)\n```", txt, flags=re.S):
        out[bid] = json.loads(body) if lang == "json" else body
    return out


def render_task_space(ts: Mapping[str, Any]) -> str:
    rs = ts["reference_solution"]
    rutas = "\n".join(f"- {r['id']} ({r['nombre']}; nivel {r['nivel']}): {r['modelo']} -> {r['resultado']}"
                      for r in ts["routes"])
    supuestos = "\n".join(f"- {s}" for s in ts["required_assumptions"])
    mi = ts["modelo_inadecuado"]
    return (f"Supuestos necesarios:\n{supuestos}\n\n"
            f"Solución de referencia: {rs['steps']}\nResultado: {rs['result']}. Rango aceptable: {rs['acceptable_range']}\n\n"
            f"Rutas posibles:\n{rutas}\n\n"
            f"Modelo inadecuado ({mi['id']}): {mi['por_que_falla']}\n\n"
            f"Evidencia de validación: {ts['validation_evidence']}")


# --------------------------------------------------------------------------- generadores
def generar_tarea_md(tarea: Mapping) -> str:
    vista = vista_estudiante(tarea)
    verificar_payload_estudiante(vista, tarea)
    partes = [
        f"# TAREA {tarea['id']} (v{tarea['version']}) - insumo del simulador",
        "",
        "Generado por simulador/adapter. Solo contiene la vista de estudiante (invariante 6). No editar a mano.",
        "",
        _bloque("text", "enunciado_es", vista["enunciado_es"]),
        "",
        _bloque("text", "foto_descripcion", vista["foto_descripcion"]),
    ]
    if vista["recursos_a_solicitud"]:
        # Informativo: sim.py no sirve recursos a solicitud (ver DECISIONES.md); no se entregan.
        partes += ["", "## Recursos a solicitud (no entregados por sim.py v0.1)", ""]
        partes += [f"- {r['id']} ({r['que_es']})" for r in vista["recursos_a_solicitud"]]
    return "\n".join(partes) + "\n"


def diseno_otm(tarea: Mapping, *, modelo_estudiantes: str, modelo_codificador: str, max_turnos: int = 30) -> dict:
    foto = vista_estudiante(tarea)["foto_descripcion"].strip().lower()
    return {
        "nombres": ["Cami", "Fran"],
        "niveles": ["N1", "N2", "N3", "N4"],
        "composiciones": COMPOSICIONES,
        "corridas": CORRIDAS_DISENO_6,
        "repeticiones": 1,
        "max_turnos": max_turnos,
        "modelo_estudiantes": modelo_estudiantes,
        "modelo_codificador": modelo_codificador,
        "idioma": "es",
        "foto": "none" if foto in ("none", "") else "text_description",
        "carpeta": "corridas",
        "tramo": niveles.tramo_de(dict(tarea)),
    }


def generar_perfiles_md(tarea: Mapping, sim, *, diseno: Mapping) -> str:
    tramo = niveles.tramo_de(dict(tarea))
    f_perfiles = Path(sim.F_PERFILES)
    estilos = bloques_de(f_perfiles)["estilos"]   # INS08 sin cambios
    return "\n".join([
        f"# PERFILES {tarea['id']} - insumo del simulador",
        "",
        f"Generado por simulador/adapter. Tramo {tramo} (MAR03 §3); estilos de {f_perfiles.name} sin cambios.",
        "",
        _bloque("json", "niveles", niveles.niveles_de(tramo)), "",
        _bloque("json", "estilos", estilos), "",
        _bloque("json", "contexto_base", niveles.contexto_base_de(tramo)), "",
        _bloque("json", "diseno_otm", dict(diseno)),
    ]) + "\n"


def generar_prompts_md(tarea: Mapping, sim) -> str:
    tramo = niveles.tramo_de(dict(tarea))
    edad = niveles.edad_de(tramo)
    f_prompts = Path(sim.F_PROMPTS)
    ins09 = bloques_de(f_prompts)
    student_system = ins09["student_system"]
    if "15 años" not in student_system:
        raise ValueError("INS09 student_system ya no menciona '15 años'; revisar la sustitución de edad")
    student_system = student_system.replace("15 años", f"{edad} años")
    coder_system = CODER_SYSTEM.replace("__TASK_SPACE__", render_task_space(tarea["task_space"]))
    return "\n".join([
        f"# PROMPTS {tarea['id']} - insumo del simulador",
        "",
        f"Generado por simulador/adapter desde {f_prompts.name} (estudiante y coder_user sin cambios salvo la edad: "
        f"{edad} años). El coder_system recibe el task_space de la tarea; el estudiante nunca.",
        "",
        _bloque("text", "student_system", student_system), "",
        _bloque("text", "student_turn", ins09["student_turn"]), "",
        _bloque("text", "coder_system", coder_system), "",
        _bloque("text", "coder_user", ins09["coder_user"]), "",
        _bloque("json", "coder_schema", CODER_SCHEMA),
    ]) + "\n"


def verificar_archivos_estudiante(dir_sim: Path, tarea: Mapping) -> None:
    """Defensa en profundidad: lo que sim.py entregará a estudiantes (TAREA.md, PERFILES.md, student_*)
    no trae task_space."""
    dir_sim = Path(dir_sim)
    ids = set(bloques_de(dir_sim / "TAREA.md"))
    if ids != {"enunciado_es", "foto_descripcion"}:
        raise AislamientoError(f"TAREA.md debe tener solo enunciado_es y foto_descripcion, tiene {sorted(ids)}")
    pr = bloques_de(dir_sim / "PROMPTS.md")
    entregado = ((dir_sim / "TAREA.md").read_text(encoding="utf-8") + pr["student_system"] + pr["student_turn"]
                 + (dir_sim / "PERFILES.md").read_text(encoding="utf-8"))
    vista = vista_estudiante(tarea)
    resto = entregado.replace(vista["enunciado_es"], " ").replace(vista["foto_descripcion"], " ")
    if _TOKENS.search(resto):
        raise AislamientoError("clave de task_space en los archivos que reciben los estudiantes")
    for t in textos_de(tarea["task_space"]):
        if len(t) >= 20 and t in resto:
            raise AislamientoError(f"texto de task_space en los archivos de estudiante: «{t[:60]}»")


def generar_todo(tarea: Mapping, dir_sim: Path, sim=None, *, modelo_estudiantes: str | None = None,
                 modelo_codificador: str | None = None) -> dict:
    """Valida la tarea (invariante 1) y escribe TAREA.md, PERFILES.md y PROMPTS.md en `dir_sim`.
    Devuelve el bloque diseno_otm."""
    r = validar_contra_esquema(dict(tarea), "tarea")
    if not r:
        raise ValueError("la tarea no valida contra contratos/tarea.schema.json: " + "; ".join(r.errores[:5]))
    sim = sim or _comun.cargar_sim()
    from pipeline.llm import modelo_de
    diseno = diseno_otm(tarea, modelo_estudiantes=modelo_estudiantes or modelo_de("simulador"),
                        modelo_codificador=modelo_codificador or modelo_codificador_defecto())
    dir_sim = Path(dir_sim)
    dir_sim.mkdir(parents=True, exist_ok=True)
    (dir_sim / "TAREA.md").write_text(generar_tarea_md(tarea), encoding="utf-8")
    (dir_sim / "PERFILES.md").write_text(generar_perfiles_md(tarea, sim, diseno=diseno), encoding="utf-8")
    (dir_sim / "PROMPTS.md").write_text(generar_prompts_md(tarea, sim), encoding="utf-8")
    verificar_archivos_estudiante(dir_sim, tarea)
    return diseno
