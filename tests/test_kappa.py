import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from evals.kappa import acuerdo_exacto, kappa_ponderado  # noqa: E402


def test_valor_conocido():
    # a = [0,0,1,1,2,2], b = [0,1,1,2,2,2]
    # Desacuerdo observado: sum (a_i - b_i)^2 = 2.
    # Desacuerdo esperado: (1/6) * sum_i sum_j (a_i - b_j)^2 = (1/6) * 2 * (14 + 4 + 6) = 8.
    # kappa = 1 - 2/8 = 0.75 (igual a sklearn cohen_kappa_score(..., weights="quadratic")).
    assert kappa_ponderado([0, 0, 1, 1, 2, 2], [0, 1, 1, 2, 2, 2]) == pytest.approx(0.75)


def test_forma_por_pares_equivalente():
    a = [2, 1, 0, 2, 2, 1, 0, 1, 2, 0, 1, 2]
    b = [2, 2, 0, 1, 2, 1, 1, 1, 2, 0, 0, 2]
    n = len(a)
    obs = sum((x - y) ** 2 for x, y in zip(a, b))
    esp = sum((x - y) ** 2 for x in a for y in b) / n
    assert kappa_ponderado(a, b) == pytest.approx(1 - obs / esp)


def test_acuerdo_perfecto_y_simetria():
    a = [0, 1, 2, 2, 1]
    b = [1, 1, 2, 0, 1]
    assert kappa_ponderado(a, a) == pytest.approx(1.0)
    assert kappa_ponderado(a, b) == pytest.approx(kappa_ponderado(b, a))


def test_indefinido_si_ambos_constantes():
    assert kappa_ponderado([2, 2, 2], [2, 2, 2]) is None


def test_acuerdo_exacto():
    assert acuerdo_exacto([0, 1, 2, 2], [0, 1, 1, 2]) == 0.75
