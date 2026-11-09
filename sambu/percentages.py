"""Explicit, dimensionless percentage arithmetic for SAMBU."""
from __future__ import annotations
import math
from typing import Callable
from .values import number_value

def _number(value: object, name: str) -> float:
    result = number_value(value, name)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result

def _arity(args: list[object], name: str, minimum: int, maximum: int | None = None) -> None:
    maximum = minimum if maximum is None else maximum
    if not minimum <= len(args) <= maximum:
        expected = str(minimum) if minimum == maximum else f"{minimum} to {maximum}"
        raise TypeError(f"{name}() expects {expected} arguments, got {len(args)}")

def _percent_of(args: list[object]) -> float:
    _arity(args, "percent_of", 2)
    return _number(args[0], "amount") * _number(args[1], "percentage") / 100.0

def _apply_percent(args: list[object]) -> float:
    _arity(args, "apply_percent", 2)
    return _number(args[0], "amount") * (1.0 + _number(args[1], "percentage change") / 100.0)

def _reduce_by_percent(args: list[object]) -> float:
    _arity(args, "reduce_by_percent", 2)
    amount, rate = _number(args[0], "amount"), _number(args[1], "reduction percentage")
    if not 0.0 <= rate <= 100.0:
        raise ValueError("reduction percentage must be between 0 and 100")
    return amount * (1.0 - rate / 100.0)

def _percentage(args: list[object]) -> float:
    _arity(args, "percentage", 2)
    part, whole = _number(args[0], "part"), _number(args[1], "whole")
    if whole == 0.0:
        raise ZeroDivisionError("whole cannot be zero when calculating a percentage")
    return part / whole * 100.0

def _percent_change(args: list[object]) -> float:
    _arity(args, "percent_change", 2)
    old, new = _number(args[0], "old value"), _number(args[1], "new value")
    if old == 0.0:
        if new == 0.0:
            return 0.0
        raise ZeroDivisionError("percent_change is undefined when the old value is zero")
    return (new - old) / abs(old) * 100.0

def _percent_to_ratio(args: list[object]) -> float:
    _arity(args, "percent_to_ratio", 1)
    return _number(args[0], "percentage") / 100.0

def _ratio_to_percent(args: list[object]) -> float:
    _arity(args, "ratio_to_percent", 1)
    return _number(args[0], "ratio") * 100.0

def _percentage_points(args: list[object]) -> float:
    _arity(args, "percentage_points", 2)
    return _number(args[0], "current percentage") - _number(args[1], "reference percentage")

def _clamp_percent(args: list[object]) -> float:
    _arity(args, "clamp_percent", 1, 3)
    value = _number(args[0], "percentage")
    minimum = _number(args[1], "minimum") if len(args) >= 2 else 0.0
    maximum = _number(args[2], "maximum") if len(args) >= 3 else 100.0
    if minimum > maximum:
        raise ValueError("minimum percentage cannot exceed maximum percentage")
    return min(max(value, minimum), maximum)

PERCENTAGE_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "percent_of": _percent_of,
    "apply_percent": _apply_percent,
    "reduce_by_percent": _reduce_by_percent,
    "percentage": _percentage,
    "percent_change": _percent_change,
    "percent_to_ratio": _percent_to_ratio,
    "ratio_to_percent": _ratio_to_percent,
    "percentage_points": _percentage_points,
    "clamp_percent": _clamp_percent,
}
__all__ = ["PERCENTAGE_BUILTINS"]
