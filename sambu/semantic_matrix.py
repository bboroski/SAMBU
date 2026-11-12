"""Bounded matrix operations for cross-domain scientific exploration.

The expansion models weighted paths over a finite relation matrix. It is not a
physical quantum simulator and makes no claims about causal or physical coupling.
"""
from __future__ import annotations

import math
from collections.abc import Sequence

MAX_NODES = 64
MAX_DEPTH = 6


class SemanticMatrixError(ValueError):
    """Raised when a matrix or expansion request violates resource bounds."""


def _square(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    if not isinstance(matrix, Sequence) or isinstance(matrix, (str, bytes)):
        raise SemanticMatrixError("matrix must be a sequence of rows")
    size = len(matrix)
    if size == 0 or size > MAX_NODES:
        raise SemanticMatrixError(f"matrix size must be between 1 and {MAX_NODES}")
    result: list[list[float]] = []
    for row in matrix:
        if not isinstance(row, Sequence) or isinstance(row, (str, bytes)) or len(row) != size:
            raise SemanticMatrixError("matrix must be square")
        values = [float(value) for value in row]
        if any(not math.isfinite(value) or value < 0.0 for value in values):
            raise SemanticMatrixError("weights must be finite and non-negative")
        result.append(values)
    return result


def multiply(left: Sequence[Sequence[float]],
             right: Sequence[Sequence[float]]) -> tuple[tuple[float, ...], ...]:
    """Multiply two bounded square matrices without mutating either input."""
    a = _square(left)
    b = _square(right)
    if len(a) != len(b):
        raise SemanticMatrixError("matrix dimensions must match")
    n = len(a)
    product = [[0.0] * n for _ in range(n)]
    for row in range(n):
        for pivot, a_value in enumerate(a[row]):
            if a_value == 0.0:
                continue
            for column, b_value in enumerate(b[pivot]):
                product[row][column] += a_value * b_value
    return tuple(tuple(row) for row in product)


def expand_relations(matrix: Sequence[Sequence[float]], *,
                     depth: int = 3, damping: float = 0.65) -> tuple[tuple[float, ...], ...]:
    """Return normalized, bounded multi-hop relation scores.

    Rows are normalized before multiplication. Each hop is damped, the diagonal
    is cleared to avoid self-reinforcing identity paths, and output rows are
    normalized to keep scores finite and comparable.
    """
    source = _square(matrix)
    if not isinstance(depth, int) or isinstance(depth, bool) or not 1 <= depth <= MAX_DEPTH:
        raise SemanticMatrixError(f"depth must be an integer from 1 to {MAX_DEPTH}")
    damping = float(damping)
    if not math.isfinite(damping) or not 0.0 <= damping <= 1.0:
        raise SemanticMatrixError("damping must be finite and between 0 and 1")

    n = len(source)
    transition = []
    for row in source:
        total = sum(row)
        transition.append([value / total for value in row] if total else [0.0] * n)

    frontier = transition
    accumulated = [[0.0] * n for _ in range(n)]
    factor = 1.0
    for _ in range(depth):
        for i in range(n):
            for j in range(n):
                accumulated[i][j] += factor * frontier[i][j]
        frontier = [list(row) for row in multiply(frontier, transition)]
        factor *= damping

    for i in range(n):
        accumulated[i][i] = 0.0
        total = sum(accumulated[i])
        if total:
            accumulated[i] = [value / total for value in accumulated[i]]
    return tuple(tuple(row) for row in accumulated)
