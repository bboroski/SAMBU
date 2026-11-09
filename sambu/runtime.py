"""Evaluator and scientific standard library for SAMBU."""
from __future__ import annotations

import math
import random
from typing import Callable

from .values import (
    AMOUNT, ENERGY, MASS, SPEED, TEMP, ZERO, Quantity, Record, UNITS,
    number_value, require_quantity,
)


class SambuRuntimeError(Exception):
    """Raised when a SAMBU program cannot be evaluated."""


class Environment:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    def define(self, name: str, value: object) -> None:
        if name in self.values:
            raise SambuRuntimeError(f"name {name!r} is already defined")
        self.values[name] = value

    def get(self, name: str) -> object:
        try:
            return self.values[name]
        except KeyError as exc:
            raise SambuRuntimeError(f"unknown name {name!r}") from exc


def _positive_temperature(value: object) -> Quantity:
    q = require_quantity(value, TEMP, "temperature")
    if q.value <= 0:
        raise ValueError("temperature must be greater than zero kelvin")
    return q


def _maxwell(args: list[object]) -> Record:
    if len(args) != 2:
        raise TypeError("maxwell(temperature, particle_mass) expects 2 arguments")
    temp = _positive_temperature(args[0])
    mass = require_quantity(args[1], MASS, "particle mass")
    if mass.value <= 0:
        raise ValueError("particle mass must be positive")
    kbt_over_m = 1.380649e-23 * temp.value / mass.value
    return Record({
        "most_probable": Quantity(math.sqrt(2.0 * kbt_over_m), SPEED),
        "mean": Quantity(math.sqrt(8.0 * kbt_over_m / math.pi), SPEED),
        "rms": Quantity(math.sqrt(3.0 * kbt_over_m), SPEED),
        "component_sigma": Quantity(math.sqrt(kbt_over_m), SPEED),
    })


def _boltzmann(args: list[object]) -> float:
    if len(args) != 2:
        raise TypeError("boltzmann(energy, temperature) expects 2 arguments")
    energy = require_quantity(args[0], ENERGY, "energy")
    temp = _positive_temperature(args[1])
    exponent = -energy.value / (1.380649e-23 * temp.value)
    if exponent < -745:
        return 0.0
    return math.exp(exponent)


def _thermal_energy(args: list[object]) -> Quantity:
    if not 1 <= len(args) <= 2:
        raise TypeError("thermal_energy(temperature, degrees_of_freedom=3) expects 1 or 2 arguments")
    temp = _positive_temperature(args[0])
    dof = number_value(args[1], "degrees of freedom") if len(args) == 2 else 3.0
    if dof <= 0:
        raise ValueError("degrees of freedom must be positive")
    return Quantity(0.5 * dof * 1.380649e-23 * temp.value, ENERGY)


def _partition(args: list[object]) -> float:
    if len(args) != 2 or not isinstance(args[0], list):
        raise TypeError("partition(energy_levels, temperature) expects an array and a temperature")
    temp = _positive_temperature(args[1])
    terms = []
    for level in args[0]:
        energy = require_quantity(level, ENERGY, "energy level")
        exponent = -energy.value / (1.380649e-23 * temp.value)
        terms.append(0.0 if exponent < -745 else math.exp(exponent))
    return sum(terms)


def _entropy(args: list[object]) -> float:
    if len(args) != 1 or not isinstance(args[0], list):
        raise TypeError("entropy(probabilities) expects one array")
    probs = [number_value(p, "probability") for p in args[0]]
    if any(p < 0 for p in probs):
        raise ValueError("probabilities cannot be negative")
    total = sum(probs)
    if not math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("probabilities must sum to 1")
    return -sum(p * math.log(p) for p in probs if p > 0)


def _sample_maxwell(args: list[object]) -> list[Quantity]:
    if not 3 <= len(args) <= 4:
        raise TypeError("sample_maxwell(temperature, particle_mass, count, seed=0) expects 3 or 4 arguments")
    stats = _maxwell(args[:2])
    count = int(number_value(args[2], "sample count"))
    if count < 0 or count > 1_000_000:
        raise ValueError("sample count must be between 0 and 1,000,000")
    seed = int(number_value(args[3], "seed")) if len(args) == 4 else 0
    rng = random.Random(seed)
    sigma = stats.get("component_sigma").value  # type: ignore[union-attr]
    return [Quantity(math.sqrt(sum(rng.gauss(0.0, sigma) ** 2 for _ in range(3))), SPEED) for _ in range(count)]


def _mean(args: list[object]) -> object:
    if len(args) != 1 or not isinstance(args[0], list) or not args[0]:
        raise TypeError("mean(values) expects a non-empty array")
    values = args[0]
    first = values[0]
    if isinstance(first, Quantity):
        total = Quantity(0.0, first.dims)
        for item in values:
            if not isinstance(item, Quantity) or item.dims != first.dims:
                raise ValueError("all values must have matching dimensions")
            total = total + item
        return total / len(values)
    nums = [number_value(item) for item in values]
    return sum(nums) / len(nums)


def _variance(args: list[object]) -> object:
    if len(args) != 1 or not isinstance(args[0], list) or len(args[0]) < 2:
        raise TypeError("variance(values) expects an array with at least two items")
    values = args[0]
    average = _mean([values])
    if isinstance(average, Quantity):
        total = Quantity(0.0, (average.dims[0] * 2, average.dims[1] * 2, average.dims[2] * 2, average.dims[3] * 2, average.dims[4] * 2))
        for item in values:
            delta = item - average  # type: ignore[operator]
            total = total + delta * delta  # type: ignore[operator]
        return total / (len(values) - 1)
    nums = [number_value(item) for item in values]
    avg = float(average)
    return sum((x - avg) ** 2 for x in nums) / (len(nums) - 1)


def _sqrt(args: list[object]) -> object:
    if len(args) != 1:
        raise TypeError("sqrt(value) expects 1 argument")
    value = args[0]
    if isinstance(value, Quantity):
        if value.value < 0:
            raise ValueError("sqrt input cannot be negative")
        if any(power % 2 for power in value.dims):
            raise ValueError("sqrt requires even powers in all physical dimensions")
        return Quantity(math.sqrt(value.value), tuple(power // 2 for power in value.dims))
    x = number_value(value)
    if x < 0: raise ValueError("sqrt input cannot be negative")
    return math.sqrt(x)


def _exp(args: list[object]) -> float:
    if len(args) != 1: raise TypeError("exp(value) expects 1 argument")
    return math.exp(number_value(args[0]))


def _log(args: list[object]) -> float:
    if len(args) != 1: raise TypeError("log(value) expects 1 argument")
    x = number_value(args[0])
    if x <= 0: raise ValueError("log input must be positive")
    return math.log(x)


def _abs(args: list[object]) -> object:
    if len(args) != 1: raise TypeError("abs(value) expects 1 argument")
    return abs(args[0])  # type: ignore[arg-type]


def _count(args: list[object]) -> int:
    if len(args) != 1 or not isinstance(args[0], list): raise TypeError("count(array) expects an array")
    return len(args[0])


_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "maxwell": _maxwell,
    "boltzmann": _boltzmann,
    "thermal_energy": _thermal_energy,
    "partition": _partition,
    "entropy": _entropy,
    "sample_maxwell": _sample_maxwell,
    "mean": _mean,
    "variance": _variance,
    "sqrt": _sqrt,
    "exp": _exp,
    "log": _log,
    "abs": _abs,
    "count": _count,
}


class _PrintMarker:
    pass


_PRINT = _PrintMarker()


class Interpreter:
    def __init__(self, output: Callable[[str], None] = print):
        self.env = Environment()
        self.output = output
        self._install_prelude()

    def _install_prelude(self) -> None:
        for name, unit in UNITS.items():
            self.env.define(name, unit)
        self.env.define("pi", math.pi)
        self.env.define("e", math.e)
        self.env.define("k_B", Quantity(1.380649e-23, (1, 2, -2, -1, 0)))
        self.env.define("h", Quantity(6.62607015e-34, (1, 2, -1, 0, 0)))
        self.env.define("hbar", Quantity(1.054571817e-34, (1, 2, -1, 0, 0)))
        self.env.define("c", Quantity(299792458.0, SPEED))
        self.env.define("N_A", Quantity(6.02214076e23, (0, 0, 0, 0, -1)))
        self.env.define("R", Quantity(8.31446261815324, (1, 2, -2, -1, -1)))
        self.env.define("G", Quantity(6.67430e-11, ( -1, 3, -2, 0, 0)))
        self.env.define("version", "0.1.0")
        self.env.define("print", _PRINT)

    def run(self, statements: list[tuple]) -> object:
        result: object = None
        for statement in statements:
            if statement[0] == "let":
                _, name, expr = statement
                self.env.define(name, self.evaluate(expr))
                result = self.env.get(name)
            elif statement[0] == "expr":
                result = self.evaluate(statement[1])
            else:
                raise SambuRuntimeError(f"unknown statement {statement[0]!r}")
        return result

    def evaluate(self, node: tuple) -> object:
        kind = node[0]
        if kind == "literal": return node[1]
        if kind == "name":
            if node[1] in _BUILTINS:
                return _BUILTINS[node[1]]
            return self.env.get(node[1])
        if kind == "array": return [self.evaluate(item) for item in node[1]]
        if kind == "field":
            target = self.evaluate(node[1])
            if not isinstance(target, Record):
                raise TypeError("field access is only available on records")
            return target.get(node[2])
        if kind == "index":
            target, index = self.evaluate(node[1]), self.evaluate(node[2])
            if not isinstance(target, list): raise TypeError("indexing is only available on arrays")
            idx = int(number_value(index, "array index"))
            return target[idx]
        if kind == "call":
            fn = self.evaluate(node[1])
            args = [self.evaluate(arg) for arg in node[2]]
            if fn is _PRINT:
                if len(args) != 1: raise TypeError("print(value) expects 1 argument")
                self.output(_format(args[0])); return args[0]
            if callable(fn): return fn(args)
            raise TypeError("value is not callable")
        if kind == "unary":
            op, value = node[1], self.evaluate(node[2])
            if op == "-": return -value  # type: ignore[operator]
            if op == "+": return +value  # type: ignore[operator]
            if op == "!": return not bool(value)
        if kind == "binary":
            op = node[1]
            left = self.evaluate(node[2])
            if op in ("&&", "and"):
                return bool(left) and bool(self.evaluate(node[3]))
            if op in ("||", "or"):
                return bool(left) or bool(self.evaluate(node[3]))
            right = self.evaluate(node[3])
            if op == "+": return left + right  # type: ignore[operator]
            if op == "-": return left - right  # type: ignore[operator]
            if op == "*": return left * right  # type: ignore[operator]
            if op == "/": return left / right  # type: ignore[operator]
            if op in ("^", "**"): return left ** right  # type: ignore[operator]
            if op == "==": return left == right
            if op == "!=": return left != right
            if op == "<": return left < right  # type: ignore[operator]
            if op == "<=": return left <= right  # type: ignore[operator]
            if op == ">": return left > right  # type: ignore[operator]
            if op == ">=": return left >= right  # type: ignore[operator]
        raise SambuRuntimeError(f"unsupported expression node {kind!r}")


def _format(value: object) -> str:
    if isinstance(value, bool): return "true" if value else "false"
    if value is None: return "null"
    if isinstance(value, list): return "[" + ", ".join(_format(v) for v in value) + "]"
    if isinstance(value, Quantity): return str(value)
    if isinstance(value, Record): return str(value)
    if isinstance(value, float): return f"{value:.8g}"
    return str(value)
