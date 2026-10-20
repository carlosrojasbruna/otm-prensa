import copy
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

DIR_EJEMPLOS = RAIZ / "contratos" / "ejemplos"


def cargar_ejemplo(contrato: str) -> dict:
    return json.loads((DIR_EJEMPLOS / f"{contrato}_ejemplo.json").read_text(encoding="utf-8"))


@pytest.fixture
def ejemplos():
    """Copias frescas de los ejemplos válidos, por contrato."""
    nombres = ["noticia", "tarea", "evaluacion", "evaluacion_rub01", "trazas_resumen", "guia", "catalogo"]
    return {n: copy.deepcopy(cargar_ejemplo(n)) for n in nombres}
