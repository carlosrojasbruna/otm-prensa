"""Textos de perfil por nivel P/S/U (MAR03 §3) y contexto base por tramo.

Plantilla de MAR03 §3: "Tienes {edad} años. {frase de confianza según N1–N4}. Manejas {herramientas del
nivel, versión N}. {Experiencia con problemas abiertos según contexto_base}."
- N1 y N4 de las herramientas son los textos de MAR03 §3; N2 y N3 son interpolaciones [EP] (MAR03 no los da).
- La frase de confianza reutiliza la gradación de INS08 §2 sin la mención a Pitágoras (los perfiles son
  independientes de la tarea, INS08 §1.1).
- La experiencia con problemas abiertos va en `contexto_base` (como en INS08 §4), no se repite aquí.
"""
from __future__ import annotations

TRAMOS = ("P", "S", "S1", "S2", "U")

EDAD = {"P": 11, "S": 15, "S1": 14, "S2": 17, "U": 19}   # edad central del tramo (MAR03 §1)
_ALIAS = {"S": "S1"}  # S sin sub-tramo: se usan las herramientas de S1 (lectura conservadora)

CONFIANZA = {
    "N1": "Te cuesta bastante la matemática, sueles tener notas bajas y te sientes con poca confianza.",
    "N2": "Tus notas en matemática están algo bajo el promedio del curso y a veces dudas de tus resultados.",
    "N3": "Tus notas en matemática están sobre el promedio del curso y te sientes con bastante confianza.",
    "N4": "Tienes de las mejores notas de matemática del curso y te sientes con mucha confianza.",
}

HERRAMIENTAS = {
    "P": {
        "N1": "Haces operaciones básicas, pero te equivocas con los decimales; los porcentajes solo los haces con calculadora y te cuesta leer tablas.",
        "N2": "Haces operaciones y proporcionalidad directa simple, aunque a veces te equivocas con decimales; los porcentajes los haces con calculadora y lees tablas con esfuerzo.",
        "N3": "Manejas operaciones, proporcionalidad directa y porcentajes simples; lees tablas y gráficos de barras y a veces estimas antes de calcular.",
        "N4": "Haces operaciones y porcentajes con soltura, lees gráficos y tablas y estimas antes de calcular.",
    },
    "S1": {
        "N1": "Haces proporciones con ayuda, confundes tasa con cantidad y no recuerdas fórmulas de memoria.",
        "N2": "Manejas proporciones y tasas simples, aunque a veces confundes tasa con cantidad, y recuerdas pocas fórmulas.",
        "N3": "Manejas razones, tasas, función lineal y ecuaciones de primer grado en los ejercicios del libro.",
        "N4": "Manejas con soltura proporciones, función lineal y ecuaciones, e interpretas la pendiente como una tasa.",
    },
    "S2": {
        "N1": "Conoces las funciones solo como fórmulas y no distingues lineal de exponencial en una tabla de datos.",
        "N2": "Manejas funciones lineales y cuadráticas como fórmulas, y a veces distingues lineal de exponencial en una tabla.",
        "N3": "Manejas funciones lineales, cuadráticas y exponenciales y estadística descriptiva en los ejercicios del libro.",
        "N4": "Eliges el modelo según los datos, usas estadística descriptiva y haces análisis de qué pasa si.",
    },
    "U": {
        "N1": "Haces cálculo y álgebra lineal de forma mecánica y no tienes experiencia en modelar.",
        "N2": "Haces cálculo y álgebra lineal apoyándote en ejemplos resueltos y tienes poca experiencia en modelar.",
        "N3": "Manejas cálculo, álgebra lineal y probabilidad en los ejercicios del curso y modelas si tienes una guía.",
        "N4": "Modelas con las herramientas del curso, discutes supuestos y conoces los límites de un modelo.",
    },
}

_BASE_CONTEXTO = ("En el curso casi no han trabajado problemas abiertos: la mayoría de los problemas que "
                  "resuelven traen todos los datos necesarios. La clase es en español, que es la lengua "
                  "materna de ambos.")
CONTEXTO = {
    "P": "Están en la educación primaria (10 a 12 años). " + _BASE_CONTEXTO,
    "S": "Están en la educación secundaria (13 a 18 años). " + _BASE_CONTEXTO,
    "S1": "Están en los primeros años de la educación secundaria (13 a 15 años). " + _BASE_CONTEXTO,
    "S2": "Están en los últimos años de la educación secundaria (16 a 18 años). " + _BASE_CONTEXTO,
    "U": "Están en el primer o segundo año de la universidad (18 a 20 años). " + _BASE_CONTEXTO,
}


def tramo_de(tarea: dict) -> str:
    """P | S | S1 | S2 | U desde nivel_principal y sub_tramo de la tarea."""
    n = tarea["nivel_principal"]
    return tarea.get("sub_tramo", n) if n == "S" else n


def edad_de(tramo: str) -> int:
    return EDAD[tramo]


def niveles_de(tramo: str) -> dict[str, str]:
    """Bloque `niveles` de INS08 (N1–N4) para el tramo."""
    if tramo not in TRAMOS:
        raise ValueError(f"tramo desconocido: {tramo!r}")
    herr = HERRAMIENTAS[_ALIAS.get(tramo, tramo)]
    return {n: f"Tienes {EDAD[tramo]} años. {CONFIANZA[n]} {herr[n]}" for n in ("N1", "N2", "N3", "N4")}


def contexto_base_de(tramo: str) -> dict:
    return {"id": f"otm_{tramo}", "texto": CONTEXTO[tramo]}
