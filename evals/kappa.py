"""Kappa de Cohen ponderado (cuadrático), implementado a mano (sin scikit-learn).

kappa_w = 1 - sum_ij w_ij O_ij / sum_ij w_ij E_ij,  con w_ij = (i - j)^2 / (k - 1)^2,
O = matriz de frecuencias observadas, E = producto de marginales / n.
Coincide con sklearn.metrics.cohen_kappa_score(a, b, weights="quadratic") y con la forma
equivalente por pares: 1 - sum_i (a_i - b_i)^2 / ((1/n) sum_i sum_j (a_i - b_j)^2).
Devuelve None si el desacuerdo esperado es 0 (ambos codificadores constantes): kappa indefinido.
"""
from __future__ import annotations

from typing import Sequence


def kappa_ponderado(a: Sequence[int], b: Sequence[int], categorias: Sequence[int] = (0, 1, 2)) -> float | None:
    if len(a) != len(b) or not a:
        raise ValueError("las listas deben tener el mismo largo (> 0)")
    k = len(categorias)
    idx = {c: n for n, c in enumerate(categorias)}
    n = len(a)
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[idx[x]][idx[y]] += 1
    fa = [sum(fila) for fila in obs]
    fb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    w = [[(i - j) ** 2 / (k - 1) ** 2 for j in range(k)] for i in range(k)]
    num = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k))
    den = sum(w[i][j] * fa[i] * fb[j] / n for i in range(k) for j in range(k))
    if den == 0:
        return None
    return 1 - num / den


def acuerdo_exacto(a: Sequence[int], b: Sequence[int]) -> float:
    return sum(x == y for x, y in zip(a, b)) / len(a)
