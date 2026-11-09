"""Parameterized Anatidae-inspired models for avian thermoregulation and flight.

The functions are deliberately generic. They require model inputs from the
caller and do not embed species-wide biological constants.
"""
from __future__ import annotations

import math
from typing import Callable

from .values import ENERGY, PRESSURE, SPEED, TEMP, TIME, Quantity, Record, number_value, require_quantity

POWER = (1, 2, -3, 0, 0)


def _ratio(value: object, name: str, *, maximum: float = 1.0) -> float:
    result = number_value(value, name)
    if not math.isfinite(result) or not 0.0 <= result <= maximum:
        raise ValueError(f"{name} must be finite and between 0 and {maximum}")
    return result


def _positive(value: object, dims: tuple[int, int, int, int, int], name: str, *, allow_zero: bool = False) -> Quantity:
    quantity = require_quantity(value, dims, name)
    if quantity.value < 0 or (quantity.value == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{name} must be {qualifier}")
    return quantity


def _countercurrent_exchange(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("countercurrent_exchange(arterial_temperature, venous_temperature, efficiency) expects 3 arguments")
    arterial = _positive(args[0], TEMP, "arterial temperature")
    venous = _positive(args[1], TEMP, "venous temperature")
    efficiency = _ratio(args[2], "exchange efficiency")
    gradient = arterial.value - venous.value
    return Record({
        "temperature_gradient": Quantity(gradient, TEMP),
        "arterial_outlet": Quantity(arterial.value - efficiency * gradient, TEMP),
        "venous_return": Quantity(venous.value + efficiency * gradient, TEMP),
        "efficiency": efficiency,
    })


def _plumage_insulation(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("plumage_insulation(baseline_index, compression_ratio, wetness_ratio) expects 3 arguments")
    baseline = number_value(args[0], "baseline insulation index")
    if not math.isfinite(baseline) or baseline < 0:
        raise ValueError("baseline insulation index must be finite and non-negative")
    compression = _ratio(args[1], "compression ratio")
    wetness = _ratio(args[2], "wetness ratio")
    effective = baseline * (1.0 - compression) * (1.0 - wetness)
    return Record({
        "baseline_index": baseline,
        "effective_index": effective,
        "retained_fraction": effective / baseline if baseline else 0.0,
        "loss_fraction": 1.0 - (effective / baseline) if baseline else 0.0,
    })


def _flight_energy_budget(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("flight_energy_budget(power, duration, available_energy) expects 3 arguments")
    power = _positive(args[0], POWER, "flight power")
    duration = _positive(args[1], TIME, "flight duration", allow_zero=True)
    reserve = _positive(args[2], ENERGY, "available energy", allow_zero=True)
    required = power * duration
    remaining = reserve - required
    used = required.value / reserve.value if reserve.value else (0.0 if required.value == 0 else None)
    return Record({
        "energy_required": required,
        "energy_remaining": remaining,
        "is_sufficient": remaining.value >= 0,
        "fraction_used": used,
    })


def _migration_speed(args: list[object]) -> Quantity:
    if len(args) != 2:
        raise TypeError("migration_speed(distance, duration) expects 2 arguments")
    distance = _positive(args[0], (0, 1, 0, 0, 0), "migration distance", allow_zero=True)
    duration = _positive(args[1], TIME, "migration duration")
    return Quantity(distance.value / duration.value, SPEED)


def _oxygen_pressure_ratio(args: list[object]) -> float:
    if len(args) != 2:
        raise TypeError("oxygen_pressure_ratio(partial_pressure, reference_pressure) expects 2 arguments")
    altitude = _positive(args[0], PRESSURE, "oxygen partial pressure")
    reference = _positive(args[1], PRESSURE, "reference oxygen pressure")
    return altitude.value / reference.value


ANATIDAE_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "countercurrent_exchange": _countercurrent_exchange,
    "plumage_insulation": _plumage_insulation,
    "flight_energy_budget": _flight_energy_budget,
    "migration_speed": _migration_speed,
    "oxygen_pressure_ratio": _oxygen_pressure_ratio,
}

__all__ = ["ANATIDAE_BUILTINS"]
