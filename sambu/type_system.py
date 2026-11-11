"""Gradual static checking and runtime enforcement for SAMBU annotations.

The checker is intentionally conservative: unknown/dynamic expressions remain
Any rather than being guessed. The runtime enforces declared contracts too.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from .ast import (
    ArrayExpr, BinaryExpr, CallExpr, ClassStatement, Expression,
    ExpressionStatement, FieldExpr, ForStatement, FunctionStatement,
    IfStatement, IndexExpr, InterfaceStatement, LetStatement, LiteralExpr,
    NameExpr, Program, ReturnStatement, SetFieldStatement, TraitStatement,
    UnaryExpr,
)
from .values import Quantity, Record


PRIMITIVES = {
    "Any", "Number", "Float", "Int", "Bool", "String", "Null", "Unit",
    "Quantity", "Record", "Function", "Object",
}
GENERIC_ARITY = {"Array": 1, "List": 1}
BUILTIN_FUNCTIONS = {
    "print": "Any", "len": "Number", "count": "Number",
    "range": "Array<Int>", "sqrt": "Any", "exp": "Number",
    "log": "Number", "abs": "Any", "sum": "Any", "min": "Any",
    "max": "Any", "mean": "Any", "variance": "Any",
    "boltzmann": "Number", "entropy": "Number", "partition": "Number",
    "thermal_energy": "Quantity", "maxwell": "Record",
    "sample_maxwell": "Array<Quantity>",
}
UNIT_NAMES = {
    "kg", "g", "mg", "m", "cm", "mm", "km", "s", "ms", "us",
    "K", "mol", "J", "kJ", "eV", "Pa", "bar", "Hz", "N", "L",
}
CONSTANT_NAMES = {"pi", "e"}


def _generic_parts(annotation: str) -> tuple[str, tuple[str, ...]]:
    """Split a type expression without splitting nested generic arguments."""
    text = annotation.strip()
    opening = text.find("<")
    if opening < 0:
        return text, ()
    if not text.endswith(">"):
        return text, ()
    base = text[:opening].strip()
    body = text[opening + 1:-1]
    parts: list[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(body):
        if char == "<":
            depth += 1
        elif char == ">":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(body[start:index].strip())
            start = index + 1
    parts.append(body[start:].strip())
    return base, tuple(parts)


def _canonical(annotation: str) -> str:
    base, arguments = _generic_parts(annotation)
    if not arguments:
        return base.strip()
    return f"{base.strip()}<{', '.join(_canonical(item) for item in arguments)}>"


class SambuTypeError(TypeError):
    """A declared SAMBU type contract was violated."""


def value_matches_type(
    value: object,
    annotation: str,
    environment: object | None = None,
) -> bool:
    """Return whether a runtime value satisfies a SAMBU type annotation."""
    annotation = _canonical(annotation)
    base, arguments = _generic_parts(annotation)
    if annotation == "Any" or base == "Any":
        return True
    if base in {"Array", "List"}:
        if len(arguments) != 1 or not isinstance(value, list):
            return False
        return all(value_matches_type(item, arguments[0], environment) for item in value)
    if base in {"Number", "Float"}:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if base == "Int":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
            and float(value).is_integer()
        )
    if base == "Bool":
        return isinstance(value, bool)
    if base == "String":
        return isinstance(value, str)
    if base in {"Null", "Unit"}:
        return value is None
    if base in {"Quantity", "UnitValue"}:
        return isinstance(value, Quantity)
    if base == "Record":
        return isinstance(value, Record)
    if base == "Function":
        return callable(value)
    if base == "Object":
        return getattr(value, "klass", None) is not None
    if environment is not None:
        contains = getattr(environment, "contains", None)
        getter = getattr(environment, "get", None)
        if callable(contains) and callable(getter) and contains(base):
            expected = getter(base)
            actual_class = getattr(value, "klass", None)
            if actual_class is expected:
                return True
            is_subclass = getattr(actual_class, "is_subclass_of", None)
            return bool(callable(is_subclass) and is_subclass(expected))
    return False


def assert_value_type(
    value: object,
    annotation: str,
    environment: object | None = None,
    *,
    context: str = "value",
) -> None:
    """Raise a stable runtime error when an annotated value is not compatible."""
    if not value_matches_type(value, annotation, environment):
        raise SambuTypeError(
            f"{context} must have type {_canonical(annotation)}, "
            f"got {infer_runtime_type(value)}"
        )


def infer_runtime_type(value: object) -> str:
    if value is None:
        return "Null"
    if isinstance(value, bool):
        return "Bool"
    if isinstance(value, (int, float)):
        return "Number"
    if isinstance(value, str):
        return "String"
    if isinstance(value, Quantity):
        return "Quantity"
    if isinstance(value, Record):
        return "Record"
    if isinstance(value, list):
        return "Array<Any>"
    if callable(value):
        return "Function"
    klass = getattr(value, "klass", None)
    if klass is not None:
        return str(getattr(klass, "name", "Object"))
    return type(value).__name__


@dataclass(frozen=True, slots=True)
class TypeDiagnostic:
    code: str
    message: str
    line: int
    column: int
    start_offset: int
    end_offset: int

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
        }


@dataclass(frozen=True, slots=True)
class FunctionSignature:
    parameter_types: tuple[str, ...]
    return_type: str


class _TypeChecker:
    def __init__(self) -> None:
        self.diagnostics: list[TypeDiagnostic] = []
        self.known_types = set(PRIMITIVES) | {"Array", "List"}
        self.class_bases: dict[str, str | None] = {}
        self.functions: dict[str, FunctionSignature] = {}
        self._return_stack: list[str | None] = []

    def error(self, node: object, message: str, code: str = "SAMBU-T001") -> None:
        span = getattr(node, "span", None)
        if span is None:
            line = column = 1
            start = end = 0
        else:
            line, column = span.start.line, span.start.column
            start, end = span.start.offset, span.end.offset
        item = TypeDiagnostic(code, message, line, column, start, end)
        if item not in self.diagnostics:
            self.diagnostics.append(item)

    def valid_type(self, annotation: str, node: object) -> bool:
        base, arguments = _generic_parts(annotation)
        base = base.strip()
        if base in GENERIC_ARITY:
            expected = GENERIC_ARITY[base]
            if len(arguments) != expected:
                self.error(node, f"{base} expects {expected} type argument(s)", "SAMBU-T002")
                return False
            valid = True
            for argument in arguments:
                valid = self.valid_type(argument, node) and valid
            return valid
        if arguments:
            self.error(node, f"unsupported generic type {annotation!r}", "SAMBU-T002")
            return False
        if base not in self.known_types:
            self.error(node, f"unknown type {base!r}", "SAMBU-T002")
            return False
        return True

    def assignable(self, actual: str, expected: str) -> bool:
        actual, expected = _canonical(actual), _canonical(expected)
        if actual == "Any" or expected == "Any" or actual == expected:
            return True
        if expected == "Number" and actual in {"Int", "Float"}:
            return True
        if expected == "Float" and actual == "Int":
            return True
        actual_base, actual_args = _generic_parts(actual)
        expected_base, expected_args = _generic_parts(expected)
        if actual_base in {"Array", "List"} and expected_base in {"Array", "List"}:
            if len(actual_args) != 1 or len(expected_args) != 1:
                return False
            return self.assignable(actual_args[0], expected_args[0])
        current = actual
        seen: set[str] = set()
        while current and current not in seen:
            seen.add(current)
            current = self.class_bases.get(current) or ""
            if current == expected:
                return True
        return False

    def check_value(self, actual: str, expected: str | None, node: object, context: str) -> None:
        if expected is None:
            return
        if not self.valid_type(expected, node):
            return
        if not self.assignable(actual, expected):
            self.error(node, f"{context} expects {expected}, inferred {actual}")

    def infer(self, expression: Expression, scope: dict[str, str]) -> str:
        if isinstance(expression, LiteralExpr):
            value = expression.value
            if value is None:
                return "Null"
            if isinstance(value, bool):
                return "Bool"
            if isinstance(value, (int, float)):
                return "Number"
            if isinstance(value, str):
                return "String"
            return "Any"
        if isinstance(expression, NameExpr):
            if expression.name in scope:
                return scope[expression.name]
            if expression.name in UNIT_NAMES:
                return "Quantity"
            if expression.name in CONSTANT_NAMES:
                return "Number"
            if expression.name in self.functions or expression.name in BUILTIN_FUNCTIONS:
                return "Function"
            if expression.name in self.class_bases:
                return expression.name
            return "Any"
        if isinstance(expression, UnaryExpr):
            operand = self.infer(expression.operand, scope)
            if expression.operator == "!":
                if operand not in {"Bool", "Any"}:
                    self.error(expression, f"logical negation expects Bool, inferred {operand}")
                return "Bool"
            if operand not in {"Number", "Int", "Float", "Quantity", "Any"}:
                self.error(expression, f"unary {expression.operator} does not accept {operand}")
            return operand
        if isinstance(expression, BinaryExpr):
            left = self.infer(expression.left, scope)
            right = self.infer(expression.right, scope)
            op = expression.operator
            if op in {"==", "!=", "<", "<=", ">", ">=", "is", "&&", "||", "and", "or"}:
                return "Bool"
            if op == "+" and left == right == "String":
                return "String"
            if left == "Any" or right == "Any":
                return "Any"
            numeric = {"Number", "Int", "Float"}
            if left in numeric and right in numeric:
                return "Number"
            if left == "Quantity" and right in {"Quantity", "Number", "Int", "Float"}:
                return "Quantity"
            if right == "Quantity" and left in {"Number", "Int", "Float"} and op == "*":
                return "Quantity"
            self.error(expression, f"operator {op!r} is not defined for {left} and {right}")
            return "Any"
        if isinstance(expression, ArrayExpr):
            if not expression.items:
                return "Array<Any>"
            members = [self.infer(item, scope) for item in expression.items]
            element = members[0] if all(self.assignable(item, members[0]) for item in members[1:]) else "Any"
            return f"Array<{element}>"
        if isinstance(expression, FieldExpr):
            self.infer(expression.target, scope)
            return "Any"
        if isinstance(expression, IndexExpr):
            target = self.infer(expression.target, scope)
            index = self.infer(expression.index, scope)
            if index not in {"Number", "Int", "Any"}:
                self.error(expression.index, f"array index must be numeric, inferred {index}")
            base, arguments = _generic_parts(target)
            if base in {"Array", "List"} and len(arguments) == 1:
                return arguments[0]
            if target == "String":
                return "String"
            return "Any"
        if isinstance(expression, CallExpr):
            if isinstance(expression.callee, NameExpr):
                name = expression.callee.name
                signature = self.functions.get(name)
                if signature is not None:
                    argument_types = [self.infer(item, scope) for item in expression.arguments]
                    if len(argument_types) != len(signature.parameter_types):
                        self.error(expression, f"{name} expects {len(signature.parameter_types)} argument(s), got {len(argument_types)}")
                    for index, (actual, expected) in enumerate(zip(argument_types, signature.parameter_types), 1):
                        self.check_value(actual, expected, expression.arguments[index - 1], f"argument {index} of {name}")
                    return signature.return_type
                for argument in expression.arguments:
                    self.infer(argument, scope)
                if name in BUILTIN_FUNCTIONS:
                    return BUILTIN_FUNCTIONS[name]
                if name in self.class_bases:
                    return name
            else:
                self.infer(expression.callee, scope)
                for argument in expression.arguments:
                    self.infer(argument, scope)
            return "Any"
        return "Any"

    def check_function(
        self,
        function: FunctionStatement,
        parent_scope: dict[str, str],
        owner_class: str | None = None,
    ) -> None:
        parameter_types = function.parameter_types or tuple(None for _ in function.parameters)
        typed = tuple(annotation or "Any" for annotation in parameter_types)
        for annotation in parameter_types:
            if annotation is not None:
                self.valid_type(annotation, function)
        signature = FunctionSignature(typed, function.return_type or "Any")
        if owner_class is None:
            self.functions[function.name] = signature
        local = dict(parent_scope)
        if owner_class is not None and function.parameters and function.parameters[0] == "self" and parameter_types[0] is None:
            local["self"] = owner_class
        for index, (name, annotation) in enumerate(zip(function.parameters, typed)):
            if owner_class is not None and index == 0 and name == "self" and parameter_types[index] is None:
                local[name] = owner_class
            else:
                local[name] = annotation
        if function.return_type is not None:
            self.valid_type(function.return_type, function)
        self._return_stack.append(function.return_type)
        self.check_statements(function.body, local)
        self._return_stack.pop()

    def check_statements(self, statements: tuple[object, ...], scope: dict[str, str]) -> None:
        for statement in statements:
            if isinstance(statement, LetStatement):
                actual = self.infer(statement.value, scope)
                if statement.type_annotation is not None:
                    self.check_value(actual, statement.type_annotation, statement, f"binding {statement.name!r}")
                scope[statement.name] = statement.type_annotation or actual
            elif isinstance(statement, FunctionStatement):
                self.check_function(statement, scope)
            elif isinstance(statement, ClassStatement):
                self.known_types.add(statement.name)
                self.class_bases[statement.name] = statement.base_name
                class_scope = dict(scope)
                for method in statement.methods:
                    self.check_function(method, class_scope, statement.name)
            elif isinstance(statement, (InterfaceStatement, TraitStatement)):
                for method in statement.methods:
                    self.check_function(method, dict(scope))
            elif isinstance(statement, ReturnStatement):
                actual = self.infer(statement.value, scope)
                expected = self._return_stack[-1] if self._return_stack else None
                if not self._return_stack:
                    self.error(statement, "return is only valid inside a function")
                else:
                    self.check_value(actual, expected, statement, "return value")
            elif isinstance(statement, IfStatement):
                self.infer(statement.condition, scope)
                self.check_statements(statement.then_body, dict(scope))
                self.check_statements(statement.else_body, dict(scope))
            elif isinstance(statement, ForStatement):
                iterable = self.infer(statement.iterable, scope)
                base, arguments = _generic_parts(iterable)
                if iterable != "Any" and iterable != "String" and not (base in {"Array", "List"} and arguments):
                    self.error(statement, f"for-in requires an array or string, inferred {iterable}")
                item_type = arguments[0] if base in {"Array", "List"} and arguments else ("String" if iterable == "String" else "Any")
                local = dict(scope)
                local[statement.variable] = item_type
                self.check_statements(statement.body, local)
            elif isinstance(statement, SetFieldStatement):
                self.infer(statement.target, scope)
                self.infer(statement.value, scope)
            elif isinstance(statement, ExpressionStatement):
                self.infer(statement.expression, scope)

    def check(self, program: Program) -> tuple[TypeDiagnostic, ...]:
        scope: dict[str, str] = {}
        # Predeclare nominal types so annotations can refer to classes declared later.
        for statement in program.statements:
            if isinstance(statement, ClassStatement):
                self.known_types.add(statement.name)
                self.class_bases[statement.name] = statement.base_name
        # Predeclare top-level signatures so calls are checked even when a
        # function appears later in the source file.
        for statement in program.statements:
            if isinstance(statement, FunctionStatement):
                parameter_types = statement.parameter_types or tuple(None for _ in statement.parameters)
                self.functions[statement.name] = FunctionSignature(
                    tuple(annotation or "Any" for annotation in parameter_types),
                    statement.return_type or "Any",
                )
        for statement in program.statements:
            self.check_statements((statement,), scope)
        return tuple(self.diagnostics)


def check_program(program: Program) -> tuple[TypeDiagnostic, ...]:
    """Check annotated declarations and statically-known function calls."""
    return _TypeChecker().check(program)


def check_source(source: str) -> tuple[TypeDiagnostic, ...]:
    """Parse and check source text without executing it."""
    from .parser import parse_ast
    return check_program(parse_ast(source))
