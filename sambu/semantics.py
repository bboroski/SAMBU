"""Conservative, source-aware semantic analysis for SAMBU programs.

The first pass reports only statically certain name, scope, call-arity and
primitive-operator errors. Dynamic values and domain built-ins remain valid.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from .ast import (
    ArrayExpr, BinaryExpr, CallExpr, ClassStatement, Expression,
    ExpressionStatement, FieldExpr, ForStatement, FunctionStatement,
    IfStatement, IndexExpr, InterfaceStatement, LetStatement, LiteralExpr,
    NameExpr, Program, ReturnStatement, SetFieldStatement, Statement,
    TraitStatement, UnaryExpr,
)
from .parser import parse_ast
from .source import SourceSpan


@dataclass(frozen=True, slots=True)
class SemanticDiagnostic:
    """One stable semantic diagnostic with an end-exclusive source range."""

    code: str
    message: str
    span: SourceSpan
    severity: str = "error"

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "start": {
                "offset": self.span.start.offset,
                "line": self.span.start.line,
                "column": self.span.start.column,
            },
            "end": {
                "offset": self.span.end.offset,
                "line": self.span.end.line,
                "column": self.span.end.column,
            },
        }


@dataclass(frozen=True, slots=True)
class SemanticReport:
    """Immutable result of checking one SAMBU source document."""

    diagnostics: tuple[SemanticDiagnostic, ...]
    declarations: int

    @property
    def valid(self) -> bool:
        return not any(item.severity == "error" for item in self.diagnostics)

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "declarations": self.declarations,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
        }


@dataclass(frozen=True, slots=True)
class _Symbol:
    kind: str
    arity: int | None = None


class _Scope:
    def __init__(self, parent: "_Scope | None" = None) -> None:
        self.parent = parent
        self.symbols: dict[str, _Symbol] = {}

    def lookup(self, name: str) -> _Symbol | None:
        current: _Scope | None = self
        while current is not None:
            found = current.symbols.get(name)
            if found is not None:
                return found
            current = current.parent
        return None

    def declare(self, name: str, symbol: _Symbol) -> bool:
        if name in self.symbols:
            return False
        self.symbols[name] = symbol
        return True


@lru_cache(maxsize=1)
def _prelude_names() -> frozenset[str]:
    # Reuse the runtime's canonical registries so new domain/articulatory
    # built-ins do not require a second manually maintained name list.
    from .runtime import _BUILTINS
    from .values import UNITS

    return frozenset(
        set(_BUILTINS)
        | set(UNITS)
        | {
            "print", "pi", "e", "k_B", "h", "hbar", "c", "N_A",
            "R", "G", "version",
        }
    )


class _Analyzer:
    def __init__(self) -> None:
        self.diagnostics: list[SemanticDiagnostic] = []
        self.declarations = 0
        self.prelude = _prelude_names()

    def report(self, code: str, message: str, span: SourceSpan) -> None:
        self.diagnostics.append(SemanticDiagnostic(code, message, span))

    def declare(
        self, scope: _Scope, name: str, symbol: _Symbol, span: SourceSpan
    ) -> None:
        if not scope.declare(name, symbol):
            self.report("SAMBU-SEM-002", f"name {name!r} is already declared in this scope", span)
        else:
            self.declarations += 1

    def predeclare(self, statements: tuple[Statement, ...], scope: _Scope) -> None:
        # Functions and nominal types are visible throughout their lexical
        # block, enabling recursion and mutually referring function bodies.
        for statement in statements:
            if isinstance(statement, FunctionStatement):
                self.declare(
                    scope, statement.name,
                    _Symbol("function", len(statement.parameters)), statement.span,
                )
            elif isinstance(statement, ClassStatement):
                self.declare(scope, statement.name, _Symbol("class"), statement.span)
            elif isinstance(statement, InterfaceStatement):
                self.declare(scope, statement.name, _Symbol("interface"), statement.span)
            elif isinstance(statement, TraitStatement):
                self.declare(scope, statement.name, _Symbol("trait"), statement.span)

    def analyze(self, program: Program) -> SemanticReport:
        root = _Scope()
        for name in self.prelude:
            root.symbols[name] = _Symbol("builtin")
        statements = program.statements
        self.predeclare(statements, root)
        self.block(statements, root, in_function=False)
        return SemanticReport(tuple(self.diagnostics), self.declarations)

    def block(
        self,
        statements: tuple[Statement, ...],
        scope: _Scope,
        *,
        in_function: bool,
    ) -> None:
        self.predeclare(statements, scope)
        for statement in statements:
            self.statement(statement, scope, in_function=in_function)

    def statement(
        self, node: Statement, scope: _Scope, *, in_function: bool
    ) -> None:
        if isinstance(node, LetStatement):
            self.expression(node.value, scope)
            self.declare(scope, node.name, _Symbol("value"), node.span)
        elif isinstance(node, ExpressionStatement):
            self.expression(node.expression, scope)
        elif isinstance(node, SetFieldStatement):
            self.expression(node.target, scope)
            self.expression(node.value, scope)
        elif isinstance(node, ReturnStatement):
            self.expression(node.value, scope)
            if not in_function:
                self.report(
                    "SAMBU-SEM-003", "return is only valid inside a function", node.span
                )
        elif isinstance(node, IfStatement):
            self.expression(node.condition, scope)
            self.block(node.then_body, _Scope(scope), in_function=in_function)
            if node.else_body:
                self.block(node.else_body, _Scope(scope), in_function=in_function)
        elif isinstance(node, ForStatement):
            self.expression(node.iterable, scope)
            loop_scope = _Scope(scope)
            self.declare(loop_scope, node.variable, _Symbol("value"), node.span)
            self.block(node.body, loop_scope, in_function=in_function)
        elif isinstance(node, FunctionStatement):
            self.function(node, scope)
        elif isinstance(node, ClassStatement):
            self.class_declaration(node, scope)
        elif isinstance(node, InterfaceStatement):
            member_scope = _Scope(scope)
            for method in node.methods:
                self.function(method, member_scope)
        elif isinstance(node, TraitStatement):
            member_scope = _Scope(scope)
            for method in node.methods:
                self.function(method, member_scope)

    def function(self, node: FunctionStatement, parent: _Scope) -> None:
        local = _Scope(parent)
        for parameter in node.parameters:
            self.declare(local, parameter, _Symbol("parameter"), node.span)
        # These names are supplied by the current object runtime for methods.
        if node.parameters and node.parameters[0] == "self":
            for implicit in ("this", "super", "__class__"):
                if implicit not in local.symbols:
                    local.symbols[implicit] = _Symbol("implicit")
        self.block(node.body, local, in_function=True)

    def class_declaration(self, node: ClassStatement, scope: _Scope) -> None:
        if node.base_name and scope.lookup(node.base_name) is None:
            self.report(
                "SAMBU-SEM-001",
                f"unknown base class {node.base_name!r}",
                node.span,
            )
        for name in node.interfaces:
            symbol = scope.lookup(name)
            if symbol is None or symbol.kind not in {"interface", "builtin"}:
                self.report("SAMBU-SEM-001", f"unknown interface {name!r}", node.span)
        for name in node.traits:
            symbol = scope.lookup(name)
            if symbol is None or symbol.kind not in {"trait", "builtin"}:
                self.report("SAMBU-SEM-001", f"unknown trait {name!r}", node.span)
        for _, value in node.static_fields:
            self.expression(value, scope)
        members = _Scope(scope)
        for method in node.methods:
            self.function(method, members)

    def expression(self, node: Expression, scope: _Scope) -> str:
        if isinstance(node, LiteralExpr):
            if node.value is None:
                return "null"
            if isinstance(node.value, bool):
                return "bool"
            if isinstance(node.value, (int, float)):
                return "number"
            if isinstance(node.value, str):
                return "text"
            return "unknown"
        if isinstance(node, NameExpr):
            if scope.lookup(node.name) is None:
                self.report("SAMBU-SEM-001", f"unknown name {node.name!r}", node.span)
            return "unknown"
        if isinstance(node, UnaryExpr):
            operand = self.expression(node.operand, scope)
            if node.operator in {"+", "-"} and operand not in {"number", "unknown"}:
                self.report(
                    "SAMBU-SEM-004",
                    f"operator {node.operator!r} requires a number, got {operand}",
                    node.span,
                )
            return "bool" if node.operator == "!" else operand
        if isinstance(node, BinaryExpr):
            left = self.expression(node.left, scope)
            right = self.expression(node.right, scope)
            operator = node.operator
            if operator in {"&&", "and", "||", "or", "==", "!=", "<", "<=", ">", ">=", "is"}:
                if operator in {"<", "<=", ">", ">="} and (
                    left != "unknown" and right != "unknown" and left != right
                ):
                    self.report(
                        "SAMBU-SEM-005",
                        f"cannot compare {left} with {right} using {operator!r}",
                        node.span,
                    )
                return "bool"
            if operator == "+" and left == right == "text":
                return "text"
            if left not in {"number", "unknown"} or right not in {"number", "unknown"}:
                self.report(
                    "SAMBU-SEM-004",
                    f"operator {operator!r} requires numeric operands, got {left} and {right}",
                    node.span,
                )
                return "unknown"
            return "number"
        if isinstance(node, ArrayExpr):
            for item in node.items:
                self.expression(item, scope)
            return "array"
        if isinstance(node, FieldExpr):
            self.expression(node.target, scope)
            return "unknown"
        if isinstance(node, IndexExpr):
            self.expression(node.target, scope)
            index_type = self.expression(node.index, scope)
            if index_type not in {"number", "unknown"}:
                self.report(
                    "SAMBU-SEM-006",
                    f"array index must be numeric, got {index_type}",
                    node.index.span,
                )
            return "unknown"
        if isinstance(node, CallExpr):
            if isinstance(node.callee, NameExpr):
                name = node.callee.name
                symbol = scope.lookup(name)
                if symbol is None:
                    self.report(
                        "SAMBU-SEM-001",
                        f"unknown function or callable {name!r}",
                        node.callee.span,
                    )
                elif symbol.kind == "function" and symbol.arity is not None:
                    if len(node.arguments) != symbol.arity:
                        self.report(
                            "SAMBU-SEM-007",
                            f"{name}() expects {symbol.arity} arguments, got {len(node.arguments)}",
                            node.span,
                        )
            else:
                self.expression(node.callee, scope)
            for argument in node.arguments:
                self.expression(argument, scope)
            return "unknown"
        return "unknown"


def analyze_ast(program: Program) -> SemanticReport:
    """Analyze an already parsed program without executing it."""
    if not isinstance(program, Program):
        raise TypeError("analyze_ast expects a sambu.ast.Program")
    return _Analyzer().analyze(program)


def analyze(source: str) -> SemanticReport:
    """Parse and statically analyze source without executing user code."""
    if not isinstance(source, str):
        raise TypeError("SAMBU source must be text")
    return analyze_ast(parse_ast(source))
