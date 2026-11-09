"""Evaluator and scientific standard library for SAMBU."""
from __future__ import annotations

import math
import random
from typing import Callable

from .domains import DOMAIN_BUILTINS
from .filtering import FILTERING_BUILTINS
from .textcraft import TEXTCRAFT_BUILTINS
from .workflows import WORKFLOW_BUILTINS

from .values import (
    ENERGY, MASS, SPEED, TEMP, Quantity, Record, UNITS,
    number_value, require_quantity,
)


class SambuRuntimeError(Exception):
    """Raised when a SAMBU program cannot be evaluated."""


class Environment:
    def __init__(self, parent: "Environment | None" = None) -> None:
        self.values: dict[str, object] = {}
        self.parent = parent

    def define(self, name: str, value: object) -> None:
        if name in self.values:
            raise SambuRuntimeError(f"name {name!r} is already defined")
        self.values[name] = value

    def contains(self, name: str) -> bool:
        return name in self.values or (self.parent is not None and self.parent.contains(name))

    def get(self, name: str) -> object:
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise SambuRuntimeError(f"unknown name {name!r}")


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


def _strict_int(value: object, what: str, minimum: int = 0, maximum: int = 1_000_000) -> int:
    number = number_value(value, what)
    result = int(number)
    if result != number or result < minimum or result > maximum:
        raise ValueError(f"{what} must be an integer from {minimum} to {maximum}")
    return result


def _sample_maxwell(args: list[object]) -> list[Quantity]:
    if not 3 <= len(args) <= 4:
        raise TypeError("sample_maxwell(temperature, particle_mass, count, seed=0) expects 3 or 4 arguments")
    stats = _maxwell(args[:2])
    count = _strict_int(args[2], "sample count")
    seed = _strict_int(args[3], "seed", minimum=0, maximum=2**32 - 1) if len(args) == 4 else 0
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


def _range(args: list[object]) -> list[int]:
    if len(args) == 1:
        start, stop, step = 0, _strict_int(args[0], "range stop", minimum=-(2**31), maximum=2**31 - 1), 1
    elif len(args) == 2:
        start = _strict_int(args[0], "range start", minimum=-(2**31), maximum=2**31 - 1)
        stop = _strict_int(args[1], "range stop", minimum=-(2**31), maximum=2**31 - 1)
        step = 1
    elif len(args) == 3:
        start, stop, step = (_strict_int(v, "range argument", minimum=-(2**31), maximum=2**31 - 1) for v in args)
    else:
        raise TypeError("range(stop), range(start, stop), or range(start, stop, step) expects 1 to 3 arguments")
    if step == 0:
        raise ValueError("range step cannot be zero")
    size = len(range(start, stop, step))
    if size > 100_000:
        raise ValueError("range cannot produce more than 100,000 items")
    return list(range(start, stop, step))


def _sum(args: list[object]) -> object:
    if len(args) != 1 or not isinstance(args[0], list):
        raise TypeError("sum(array) expects one array")
    values = args[0]
    if not values:
        return 0.0
    result = values[0]
    for value in values[1:]:
        result = result + value  # type: ignore[operator]
    return result


def _extreme(args: list[object], operation: str) -> object:
    if len(args) != 1 or not isinstance(args[0], list) or not args[0]:
        raise TypeError(f"{operation}(array) expects one non-empty array")
    return min(args[0]) if operation == "min" else max(args[0])


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
    "len": _count,
    "range": _range,
    "sum": _sum,
    "min": lambda args: _extreme(args, "min"),
    "max": lambda args: _extreme(args, "max"),
    **TEXTCRAFT_BUILTINS,
    **FILTERING_BUILTINS,
    **WORKFLOW_BUILTINS,
    **DOMAIN_BUILTINS,
}


class _PrintMarker:
    pass


_PRINT = _PrintMarker()


class _ReturnSignal(Exception):
    def __init__(self, value: object):
        self.value = value


class UserFunction:
    def __init__(
        self,
        name: str,
        params: list[str],
        body: list[tuple],
        closure: Environment,
        interpreter: "Interpreter",
        metadata: dict[str, object] | None = None,
    ):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure
        self.interpreter = interpreter
        metadata = metadata or {}
        self.visibility = str(metadata.get("visibility", "public"))
        self.is_static = bool(metadata.get("static", False))
        self.is_abstract = bool(metadata.get("abstract", False))
        self.is_final = bool(metadata.get("final", False))
        self.owner_class: SambuClass | None = None

    def invoke(
        self,
        args: list[object],
        *,
        bound_instance: "SambuInstance | None" = None,
        defining_class: "SambuClass | None" = None,
    ) -> object:
        if len(args) != len(self.params):
            raise TypeError(f"{self.name}() expects {len(self.params)} arguments, got {len(args)}")
        if self.interpreter.call_depth >= 200:
            raise SambuRuntimeError("maximum function call depth (200) exceeded")
        local = Environment(self.closure)
        for name, value in zip(self.params, args):
            local.define(name, value)
        if defining_class is not None:
            if bound_instance is not None:
                if "this" not in self.params:
                    local.define("this", bound_instance)
                if defining_class.base is not None and "super" not in self.params:
                    local.define("super", SuperProxy(bound_instance, defining_class.base, defining_class))
            if "__class__" not in self.params:
                local.define("__class__", defining_class)
        self.interpreter.call_depth += 1
        try:
            self.interpreter.execute_statements(self.body, local)
        except _ReturnSignal as signal:
            return signal.value
        finally:
            self.interpreter.call_depth -= 1
        return None

    def __call__(self, args: list[object]) -> object:
        return self.invoke(args)


class SambuInterface:
    """Structural interface contract: required instance method names and arities."""

    def __init__(self, name: str, methods: dict[str, UserFunction]):
        self.name = name
        self.methods = methods

    def __str__(self) -> str:
        return f"<interface {self.name}>"


class SambuTrait:
    """Reusable concrete instance methods copied into consuming classes."""

    def __init__(self, name: str, methods: dict[str, UserFunction]):
        self.name = name
        self.methods = methods

    def __str__(self) -> str:
        return f"<trait {self.name}>"


def _can_access(visibility: str, owner: "SambuClass | None", requester: "SambuClass | None") -> bool:
    if visibility == "public" or owner is None:
        return True
    if requester is None:
        return False
    if visibility == "private":
        return requester is owner
    return requester.is_subclass_of(owner)


class SambuClass:
    """Runtime class value with inheritance, interfaces, traits and static members."""

    def __init__(
        self,
        name: str,
        base: "SambuClass | None",
        methods: dict[str, UserFunction],
        *,
        is_abstract: bool = False,
        is_final: bool = False,
        interfaces: tuple[SambuInterface, ...] = (),
        static_fields: dict[str, object] | None = None,
    ):
        self.name = name
        self.base = base
        self.methods = methods
        self.is_abstract = is_abstract
        self.is_final = is_final
        self.interfaces = interfaces
        self.static_fields = static_fields or {}
        for method in self.methods.values():
            method.owner_class = self

    def find_method_with_owner(self, name: str) -> tuple[UserFunction, "SambuClass"] | None:
        method = self.methods.get(name)
        if method is not None:
            return method, self
        return self.base.find_method_with_owner(name) if self.base is not None else None

    def find_method(self, name: str) -> UserFunction | None:
        found = self.find_method_with_owner(name)
        return found[0] if found is not None else None

    def is_subclass_of(self, expected: "SambuClass") -> bool:
        current: SambuClass | None = self
        while current is not None:
            if current is expected:
                return True
            current = current.base
        return False

    def unresolved_abstract_methods(self) -> set[str]:
        unresolved: set[str] = set()
        chain: list[SambuClass] = []
        current: SambuClass | None = self
        while current is not None:
            chain.append(current)
            current = current.base
        for klass in reversed(chain):
            for name, method in klass.methods.items():
                if method.is_abstract:
                    unresolved.add(name)
                else:
                    unresolved.discard(name)
        return unresolved

    def get(self, name: str, requester: "SambuClass | None" = None) -> object:
        if name in self.static_fields:
            return self.static_fields[name]
        found = self.find_method_with_owner(name)
        if found is None:
            raise AttributeError(f"class {self.name} has no static member {name!r}")
        method, owner = found
        if not method.is_static:
            raise AttributeError(f"{name!r} is an instance method, not a static member")
        if not _can_access(method.visibility, owner, requester):
            raise SambuRuntimeError(f"cannot access {method.visibility} static method {name!r}")
        return BoundStaticMethod(method, owner)

    def set(self, name: str, value: object) -> None:
        if name not in self.static_fields:
            raise AttributeError(f"class {self.name} has no declared static field {name!r}")
        self.static_fields[name] = value

    def __call__(self, args: list[object]) -> object:
        unresolved = self.unresolved_abstract_methods()
        if self.is_abstract or unresolved:
            names = ", ".join(sorted(unresolved)) or self.name
            raise SambuRuntimeError(f"cannot instantiate abstract class {self.name}; unresolved: {names}")
        instance = SambuInstance(self)
        initializer = self.find_method_with_owner("init")
        if initializer is None:
            if args:
                raise TypeError(f"{self.name}() takes no constructor arguments")
        else:
            method, owner = initializer
            if method.is_static or method.is_abstract:
                raise SambuRuntimeError("init must be a concrete instance method")
            BoundMethod(instance, method, owner)(args)
        return instance

    def __str__(self) -> str:
        return f"<class {self.name}>"


class SambuInstance:
    """Mutable object instance with identity, dynamic fields and method dispatch."""

    def __init__(self, klass: SambuClass):
        self.klass = klass
        self.fields: dict[str, object] = {}

    def get(self, name: str, requester: SambuClass | None = None) -> object:
        if name in self.fields:
            return self.fields[name]
        found = self.klass.find_method_with_owner(name)
        if found is not None:
            method, owner = found
            if method.is_static:
                raise AttributeError(f"{name!r} is a static method; access it through its class")
            if not _can_access(method.visibility, owner, requester):
                raise SambuRuntimeError(f"cannot access {method.visibility} method {name!r}")
            return BoundMethod(self, method, owner)
        raise AttributeError(f"{self.klass.name} instance has no field or method {name!r}")

    def set(self, name: str, value: object) -> None:
        self.fields[name] = value

    def __str__(self) -> str:
        fields = ", ".join(f"{key}={_format(value)}" for key, value in self.fields.items())
        return f"{self.klass.name}({fields})"


class SuperProxy:
    """Explicit parent-method dispatch bound to the current instance."""

    def __init__(self, instance: SambuInstance, base: SambuClass, requester: SambuClass):
        self.instance = instance
        self.base = base
        self.requester = requester

    def get(self, name: str) -> object:
        found = self.base.find_method_with_owner(name)
        if found is None:
            raise AttributeError(f"base class {self.base.name} has no method {name!r}")
        method, owner = found
        if method.is_static:
            raise AttributeError("super dispatch is for instance methods")
        if not _can_access(method.visibility, owner, self.requester):
            raise SambuRuntimeError(f"cannot access {method.visibility} parent method {name!r}")
        return BoundMethod(self.instance, method, owner)


class BoundStaticMethod:
    """Static method bound to its declaring class for access-control checks."""

    def __init__(self, function: UserFunction, owner: SambuClass):
        self.function = function
        self.owner = owner

    def __call__(self, args: list[object]) -> object:
        return self.function.invoke(args, defining_class=self.owner)


class BoundMethod:
    def __init__(self, instance: SambuInstance, function: UserFunction, owner: SambuClass):
        self.instance = instance
        self.function = function
        self.owner = owner

    def __call__(self, args: list[object]) -> object:
        return self.function.invoke(
            [self.instance, *args],
            bound_instance=self.instance,
            defining_class=self.owner,
        )


class Interpreter:
    def __init__(self, output: Callable[[str], None] = print):
        self.env = Environment()
        self.output = output
        self.call_depth = 0
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
        self.env.define("G", Quantity(6.67430e-11, (-1, 3, -2, 0, 0)))
        self.env.define("version", "0.7.0")
        self.env.define("print", _PRINT)

    def run(self, statements: list[tuple]) -> object:
        try:
            return self.execute_statements(statements, self.env)
        except _ReturnSignal as exc:
            raise SambuRuntimeError("return can only be used inside a function") from exc

    def execute_statements(self, statements: list[tuple], env: Environment) -> object:
        result: object = None
        for statement in statements:
            kind = statement[0]
            if kind == "let":
                _, name, expr = statement
                env.define(name, self.evaluate(expr, env))
                result = env.get(name)
            elif kind == "expr":
                result = self.evaluate(statement[1], env)
            elif kind == "fn":
                _, name, params, body = statement
                env.define(name, UserFunction(name, params, body, env, self))
                result = env.get(name)
            elif kind == "interface":
                _, name, method_nodes = statement
                methods: dict[str, UserFunction] = {}
                for method_node in method_nodes:
                    _, method_name, params, body = method_node[:4]
                    if not params or params[0] != "self":
                        raise SambuRuntimeError(
                            f"interface method {method_name!r} must declare 'self' first"
                        )
                    if body:
                        raise SambuRuntimeError("interface methods cannot contain implementations")
                    methods[method_name] = UserFunction(
                        method_name, params, body, env, self,
                        {"visibility": "public", "abstract": True},
                    )
                env.define(name, SambuInterface(name, methods))
                result = env.get(name)
            elif kind == "trait":
                _, name, method_nodes = statement
                methods: dict[str, UserFunction] = {}
                for method_node in method_nodes:
                    _, method_name, params, body = method_node[:4]
                    metadata = method_node[4] if len(method_node) > 4 else {}
                    if not params or params[0] != "self":
                        raise SambuRuntimeError(
                            f"trait method {method_name!r} must declare 'self' first"
                        )
                    if metadata.get("static") or metadata.get("abstract"):
                        raise SambuRuntimeError("traits support concrete instance methods only")
                    methods[method_name] = UserFunction(
                        method_name, params, body, env, self, metadata,
                    )
                env.define(name, SambuTrait(name, methods))
                result = env.get(name)
            elif kind == "class":
                _, name, base_name, method_nodes = statement[:4]
                metadata = statement[4] if len(statement) > 4 else {}
                base = env.get(base_name) if base_name is not None else None
                if base is not None and not isinstance(base, SambuClass):
                    raise SambuRuntimeError(f"base {base_name!r} is not a SAMBU class")
                if base is not None and base.is_final:
                    raise SambuRuntimeError(f"cannot extend final class {base.name!r}")

                trait_methods: dict[str, UserFunction] = {}
                trait_conflicts: set[str] = set()
                for trait_name in metadata.get("traits", []):
                    trait = env.get(trait_name)
                    if not isinstance(trait, SambuTrait):
                        raise SambuRuntimeError(f"{trait_name!r} is not a SAMBU trait")
                    for method_name, source_method in trait.methods.items():
                        if method_name in trait_conflicts:
                            continue
                        if method_name in trait_methods:
                            del trait_methods[method_name]
                            trait_conflicts.add(method_name)
                            continue
                        trait_methods[method_name] = UserFunction(
                            source_method.name, source_method.params, source_method.body,
                            source_method.closure, self,
                            {
                                "visibility": source_method.visibility,
                                "static": False,
                                "abstract": False,
                                "final": source_method.is_final,
                            },
                        )

                explicit_method_names = {
                    method_node[1] for method_node in method_nodes
                }
                unresolved_trait_conflicts = trait_conflicts - explicit_method_names
                if unresolved_trait_conflicts:
                    names = ", ".join(sorted(unresolved_trait_conflicts))
                    raise SambuRuntimeError(
                        f"trait method conflict for {names}; provide an explicit class override"
                    )
                methods: dict[str, UserFunction] = dict(trait_methods)
                explicit_names: set[str] = set()
                for method_node in method_nodes:
                    _, method_name, params, body = method_node[:4]
                    method_metadata = method_node[4] if len(method_node) > 4 else {}
                    if method_metadata.get("static"):
                        if params and params[0] == "self":
                            raise SambuRuntimeError(
                                f"static method {method_name!r} must not declare 'self' as its first parameter"
                            )
                    elif not params or params[0] != "self":
                        raise SambuRuntimeError(
                            f"instance method {method_name!r} must declare 'self' as its first parameter"
                        )
                    method = UserFunction(
                        method_name, params, body, env, self, method_metadata,
                    )
                    inherited = base.find_method_with_owner(method_name) if base is not None else None
                    if inherited is not None:
                        inherited_method, _ = inherited
                        if inherited_method.is_final:
                            raise SambuRuntimeError(f"cannot override final method {method_name!r}")
                        if inherited_method.is_static != method.is_static:
                            raise SambuRuntimeError(
                                f"method {method_name!r} cannot change between static and instance dispatch"
                            )
                        if len(inherited_method.params) != len(method.params):
                            raise SambuRuntimeError(
                                f"override {method_name!r} must preserve the inherited arity"
                            )
                    methods[method_name] = method
                    explicit_names.add(method_name)

                for field_name, expression in metadata.get("static_fields", []):
                    if field_name in methods:
                        raise SambuRuntimeError(
                            f"static field {field_name!r} conflicts with a method"
                        )
                static_fields = {
                    field_name: self.evaluate(expression, env)
                    for field_name, expression in metadata.get("static_fields", [])
                }
                interface_values: list[SambuInterface] = []
                for interface_name in metadata.get("interfaces", []):
                    interface = env.get(interface_name)
                    if not isinstance(interface, SambuInterface):
                        raise SambuRuntimeError(f"{interface_name!r} is not a SAMBU interface")
                    interface_values.append(interface)

                klass = SambuClass(
                    name, base, methods,
                    is_abstract=bool(metadata.get("abstract", False)),
                    is_final=bool(metadata.get("final", False)),
                    interfaces=tuple(interface_values),
                    static_fields=static_fields,
                )
                for interface in interface_values:
                    for required_name, required in interface.methods.items():
                        found = klass.find_method_with_owner(required_name)
                        if found is None:
                            if not klass.is_abstract:
                                raise SambuRuntimeError(
                                    f"class {name!r} does not implement {interface.name}.{required_name}()"
                                )
                            continue
                        implementation, _ = found
                        if implementation.is_static or implementation.is_abstract:
                            if not klass.is_abstract:
                                raise SambuRuntimeError(
                                    f"{name}.{required_name} must be a concrete instance method"
                                )
                        if len(implementation.params) != len(required.params):
                            raise SambuRuntimeError(
                                f"{name}.{required_name} has an incompatible parameter count"
                            )
                unresolved = klass.unresolved_abstract_methods()
                if unresolved and not klass.is_abstract:
                    names = ", ".join(sorted(unresolved))
                    raise SambuRuntimeError(
                        f"class {name!r} must be abstract or implement: {names}"
                    )
                env.define(name, klass)
                result = klass
            elif kind == "set_field":
                _, target_expr, field_name, value_expr = statement
                target = self.evaluate(target_expr, env)
                value = self.evaluate(value_expr, env)
                if isinstance(target, SambuInstance):
                    target.set(field_name, value)
                elif isinstance(target, SambuClass):
                    target.set(field_name, value)
                else:
                    raise TypeError("field assignment requires a SAMBU object or class")
                result = value
            elif kind == "return":
                raise _ReturnSignal(self.evaluate(statement[1], env))
            elif kind == "if":
                _, condition, then_body, else_body = statement
                branch = then_body if self._truthy(self.evaluate(condition, env)) else else_body
                result = self.execute_statements(branch, Environment(env))
            elif kind == "for":
                _, variable, iterable_expr, body = statement
                iterable = self.evaluate(iterable_expr, env)
                if not isinstance(iterable, (list, tuple, str)):
                    raise TypeError("for-in loop expects an array, tuple, or string")
                if len(iterable) > 100_000:
                    raise SambuRuntimeError("loop iteration limit (100,000) exceeded")
                for item in iterable:
                    loop_env = Environment(env)
                    loop_env.define(variable, item)
                    result = self.execute_statements(body, loop_env)
            else:
                raise SambuRuntimeError(f"unknown statement {kind!r}")
        return result

    @staticmethod
    def _truthy(value: object) -> bool:
        if isinstance(value, Quantity):
            return bool(value.value)
        return bool(value)

    def evaluate(self, node: tuple, env: Environment | None = None) -> object:
        env = env or self.env
        kind = node[0]
        if kind == "literal": return node[1]
        if kind == "name":
            # Lexical bindings (including parameters) shadow standard functions.
            if env.contains(node[1]):
                return env.get(node[1])
            if node[1] in _BUILTINS:
                return _BUILTINS[node[1]]
            return env.get(node[1])
        if kind == "array": return [self.evaluate(item, env) for item in node[1]]
        if kind == "field":
            target = self.evaluate(node[1], env)
            requester = None
            if env.contains("__class__"):
                candidate = env.get("__class__")
                if isinstance(candidate, SambuClass):
                    requester = candidate
            if isinstance(target, Record):
                return target.get(node[2])
            if isinstance(target, SambuInstance):
                return target.get(node[2], requester)
            if isinstance(target, SambuClass):
                return target.get(node[2], requester)
            if isinstance(target, SuperProxy):
                return target.get(node[2])
            raise TypeError("field access is only available on records and SAMBU objects")
        if kind == "index":
            target, index = self.evaluate(node[1], env), self.evaluate(node[2], env)
            if not isinstance(target, (list, tuple, str)):
                raise TypeError("indexing is only available on arrays and strings")
            raw_idx = number_value(index, "array index")
            idx = int(raw_idx)
            if idx != raw_idx: raise ValueError("array index must be an integer")
            return target[idx]
        if kind == "call":
            fn = self.evaluate(node[1], env)
            args = [self.evaluate(arg, env) for arg in node[2]]
            if fn is _PRINT:
                if len(args) != 1: raise TypeError("print(value) expects 1 argument")
                self.output(_format(args[0])); return args[0]
            if callable(fn): return fn(args)
            raise TypeError("value is not callable")
        if kind == "unary":
            op, value = node[1], self.evaluate(node[2], env)
            if op == "-": return -value  # type: ignore[operator]
            if op == "+": return +value  # type: ignore[operator]
            if op == "!": return not self._truthy(value)
        if kind == "binary":
            op = node[1]
            left = self.evaluate(node[2], env)
            if op in ("&&", "and"):
                return self._truthy(left) and self._truthy(self.evaluate(node[3], env))
            if op in ("||", "or"):
                return self._truthy(left) or self._truthy(self.evaluate(node[3], env))
            right = self.evaluate(node[3], env)
            if op == "+": return left + right  # type: ignore[operator]
            if op == "-": return left - right  # type: ignore[operator]
            if op == "*": return left * right  # type: ignore[operator]
            if op == "/": return left / right  # type: ignore[operator]
            if op in ("^", "**"): return left ** right  # type: ignore[operator]
            if op == "==": return left == right
            if op == "!=": return left != right
            if op == "is":
                if not isinstance(right, (SambuClass, SambuInterface)):
                    raise TypeError("right operand of 'is' must be a class or interface")
                if isinstance(left, SambuInstance) and isinstance(right, SambuClass):
                    return left.klass.is_subclass_of(right)
                if isinstance(left, SambuInstance) and isinstance(right, SambuInterface):
                    current: SambuClass | None = left.klass
                    while current is not None:
                        if any(item is right for item in current.interfaces):
                            return True
                        current = current.base
                    return False
                return False
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
    if isinstance(value, SambuInstance): return str(value)
    if isinstance(value, SambuClass): return str(value)
    if isinstance(value, float): return f"{value:.8g}"
    return str(value)
