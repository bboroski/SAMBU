"""Physical quantities and units used by SAMBU."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

Dims = tuple[int, int, int, int, int]
ZERO: Dims = (0, 0, 0, 0, 0)


def _combine(a: Dims, b: Dims, sign: int = 1) -> Dims:
    return tuple(x + sign * y for x, y in zip(a, b))  # type: ignore[return-value]


def _fmt_number(value: float) -> str:
    if value == 0.0:
        return "0"
    return f"{value:.8g}"


@dataclass(frozen=True)
class Quantity:
    """An SI-normalized value with integer physical dimensions."""
    value: float
    dims: Dims = ZERO

    def __post_init__(self) -> None:
        if not math.isfinite(self.value):
            raise ValueError("quantity must be finite")

    def _coerce(self, other: object) -> "Quantity":
        if isinstance(other, Quantity):
            return other
        if isinstance(other, (int, float)) and self.dims == ZERO:
            return Quantity(float(other))
        raise TypeError("cannot combine a dimensional quantity with a plain number")

    def __add__(self, other: object) -> "Quantity":
        rhs = self._coerce(other)
        if self.dims != rhs.dims:
            raise ValueError("addition requires matching physical dimensions")
        return Quantity(self.value + rhs.value, self.dims)

    __radd__ = __add__

    def __sub__(self, other: object) -> "Quantity":
        rhs = self._coerce(other)
        if self.dims != rhs.dims:
            raise ValueError("subtraction requires matching physical dimensions")
        return Quantity(self.value - rhs.value, self.dims)

    def __rsub__(self, other: object) -> "Quantity":
        return self._coerce(other).__sub__(self)

    def __mul__(self, other: object) -> "Quantity":
        rhs = other if isinstance(other, Quantity) else Quantity(float(other)) if isinstance(other, (int, float)) else None
        if rhs is None:
            return NotImplemented
        return Quantity(self.value * rhs.value, _combine(self.dims, rhs.dims))

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> "Quantity":
        rhs = other if isinstance(other, Quantity) else Quantity(float(other)) if isinstance(other, (int, float)) else None
        if rhs is None:
            return NotImplemented
        if rhs.value == 0:
            raise ZeroDivisionError("division by zero")
        return Quantity(self.value / rhs.value, _combine(self.dims, rhs.dims, -1))

    def __rtruediv__(self, other: object) -> "Quantity":
        lhs = other if isinstance(other, Quantity) else Quantity(float(other)) if isinstance(other, (int, float)) else None
        if lhs is None:
            return NotImplemented
        return lhs.__truediv__(self)

    def __pow__(self, power: object) -> "Quantity":
        if isinstance(power, Quantity):
            if power.dims != ZERO:
                raise ValueError("power must be dimensionless")
            exponent = power.value
        else:
            exponent = float(power)  # type: ignore[arg-type]
        rounded = round(exponent)
        if not math.isclose(exponent, rounded, abs_tol=1e-12):
            if self.dims != ZERO:
                raise ValueError("fractional powers of dimensional quantities are not supported")
            return Quantity(self.value ** exponent)
        return Quantity(self.value ** exponent, tuple(int(x * rounded) for x in self.dims))  # type: ignore[arg-type]

    def __neg__(self) -> "Quantity":
        return Quantity(-self.value, self.dims)

    def __pos__(self) -> "Quantity":
        return self

    def __abs__(self) -> "Quantity":
        return Quantity(abs(self.value), self.dims)

    def _compare(self, other: object, op: str) -> bool:
        rhs = self._coerce(other)
        if self.dims != rhs.dims:
            raise ValueError("comparison requires matching physical dimensions")
        return {"<": self.value < rhs.value, "<=": self.value <= rhs.value,
                ">": self.value > rhs.value, ">=": self.value >= rhs.value,
                "==": self.value == rhs.value, "!=": self.value != rhs.value}[op]

    def __lt__(self, other: object) -> bool: return self._compare(other, "<")
    def __le__(self, other: object) -> bool: return self._compare(other, "<=")
    def __gt__(self, other: object) -> bool: return self._compare(other, ">")
    def __ge__(self, other: object) -> bool: return self._compare(other, ">=")

    def __bool__(self) -> bool:
        return bool(self.value)

    def __str__(self) -> str:
        symbol = _DIMENSION_NAMES.get(self.dims)
        if symbol:
            return f"{_fmt_number(self.value)} {symbol}"
        if self.dims == ZERO:
            return _fmt_number(self.value)
        pieces = []
        names = ("kg", "m", "s", "K", "mol")
        for name, power in zip(names, self.dims):
            if power:
                pieces.append(name if power == 1 else f"{name}^{power}")
        return f"{_fmt_number(self.value)} {' '.join(pieces)}"

    def __repr__(self) -> str:
        return f"Quantity({self.value!r}, {self.dims!r})"


@dataclass(frozen=True)
class Record:
    fields: Mapping[str, object]

    def get(self, name: str) -> object:
        if name not in self.fields:
            raise AttributeError(f"record has no field {name!r}")
        return self.fields[name]

    def __str__(self) -> str:
        body = ", ".join(f"{k}={v}" for k, v in self.fields.items())
        return "{" + body + "}"


MASS: Dims = (1, 0, 0, 0, 0)
LENGTH: Dims = (0, 1, 0, 0, 0)
TIME: Dims = (0, 0, 1, 0, 0)
TEMP: Dims = (0, 0, 0, 1, 0)
AMOUNT: Dims = (0, 0, 0, 0, 1)
ENERGY: Dims = (1, 2, -2, 0, 0)
SPEED: Dims = (0, 1, -1, 0, 0)
PRESSURE: Dims = (1, -1, -2, 0, 0)

_DIMENSION_NAMES: dict[Dims, str] = {
    MASS: "kg", LENGTH: "m", TIME: "s", TEMP: "K", AMOUNT: "mol",
    ENERGY: "J", SPEED: "m/s", PRESSURE: "Pa",
    _combine(ENERGY, TEMP, -1): "J/K",
    _combine(ENERGY, AMOUNT, -1): "J/mol",
}

UNITS: dict[str, Quantity] = {
    "kg": Quantity(1.0, MASS),
    "g": Quantity(1e-3, MASS),
    "m": Quantity(1.0, LENGTH),
    "cm": Quantity(1e-2, LENGTH),
    "km": Quantity(1e3, LENGTH),
    "s": Quantity(1.0, TIME),
    "ms": Quantity(1e-3, TIME),
    "K": Quantity(1.0, TEMP),
    "mol": Quantity(1.0, AMOUNT),
    "J": Quantity(1.0, ENERGY),
    "kJ": Quantity(1e3, ENERGY),
    "eV": Quantity(1.602176634e-19, ENERGY),
    "Pa": Quantity(1.0, PRESSURE),
    "bar": Quantity(1e5, PRESSURE),
    "Hz": Quantity(1.0, (0, 0, -1, 0, 0)),
    "N": Quantity(1.0, (1, 1, -2, 0, 0)),
    "L": Quantity(1e-3, (0, 3, 0, 0, 0)),
}


def require_quantity(value: object, dims: Dims, what: str) -> Quantity:
    if not isinstance(value, Quantity):
        raise TypeError(f"{what} must be a physical quantity")
    if value.dims != dims:
        raise ValueError(f"{what} has the wrong physical dimension")
    return value


def number_value(value: object, what: str = "value") -> float:
    if isinstance(value, Quantity):
        if value.dims != ZERO:
            raise ValueError(f"{what} must be dimensionless")
        return value.value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    raise TypeError(f"{what} must be a number")
