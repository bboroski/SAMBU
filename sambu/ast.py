"""Public, source-aware abstract syntax tree for SAMBU.

The legacy tuple AST remains available through parse(). New tooling should
prefer parse_ast() and these immutable nodes, whose spans are end-exclusive.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from .source import SourceSpan


@dataclass(frozen=True, slots=True)
class LiteralExpr:
    value: object
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class NameExpr:
    name: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class UnaryExpr:
    operator: str
    operand: Expression
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class BinaryExpr:
    operator: str
    left: Expression
    right: Expression
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class ArrayExpr:
    items: tuple[Expression, ...]
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class CallExpr:
    callee: Expression
    arguments: tuple[Expression, ...]
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class FieldExpr:
    target: Expression
    name: str
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class IndexExpr:
    target: Expression
    index: Expression
    span: SourceSpan


Expression: TypeAlias = (
    LiteralExpr
    | NameExpr
    | UnaryExpr
    | BinaryExpr
    | ArrayExpr
    | CallExpr
    | FieldExpr
    | IndexExpr
)


@dataclass(frozen=True, slots=True)
class LetStatement:
    name: str
    value: Expression
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class SetFieldStatement:
    target: Expression
    name: str
    value: Expression
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class FunctionStatement:
    name: str
    parameters: tuple[str, ...]
    body: tuple[Statement, ...]
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class ClassStatement:
    name: str
    base_name: str | None
    methods: tuple[FunctionStatement, ...]
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class ReturnStatement:
    value: Expression
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class IfStatement:
    condition: Expression
    then_body: tuple[Statement, ...]
    else_body: tuple[Statement, ...]
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class ForStatement:
    variable: str
    iterable: Expression
    body: tuple[Statement, ...]
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class ExpressionStatement:
    expression: Expression
    span: SourceSpan


Statement: TypeAlias = (
    LetStatement
    | SetFieldStatement
    | FunctionStatement
    | ClassStatement
    | ReturnStatement
    | IfStatement
    | ForStatement
    | ExpressionStatement
)


@dataclass(frozen=True, slots=True)
class Program:
    statements: tuple[Statement, ...]
    span: SourceSpan

    def to_legacy(self) -> list[tuple]:
        """Return the historical tuple AST without changing its shape."""
        return [statement_to_legacy(statement) for statement in self.statements]


def expression_to_legacy(expression: Expression) -> tuple:
    """Convert one typed expression to the pre-0.5.1 tuple representation."""
    if isinstance(expression, LiteralExpr):
        return ("literal", expression.value)
    if isinstance(expression, NameExpr):
        return ("name", expression.name)
    if isinstance(expression, UnaryExpr):
        return ("unary", expression.operator, expression_to_legacy(expression.operand))
    if isinstance(expression, BinaryExpr):
        return (
            "binary",
            expression.operator,
            expression_to_legacy(expression.left),
            expression_to_legacy(expression.right),
        )
    if isinstance(expression, ArrayExpr):
        return ("array", [expression_to_legacy(item) for item in expression.items])
    if isinstance(expression, CallExpr):
        return (
            "call",
            expression_to_legacy(expression.callee),
            [expression_to_legacy(argument) for argument in expression.arguments],
        )
    if isinstance(expression, FieldExpr):
        return ("field", expression_to_legacy(expression.target), expression.name)
    if isinstance(expression, IndexExpr):
        return (
            "index",
            expression_to_legacy(expression.target),
            expression_to_legacy(expression.index),
        )
    raise TypeError(f"unsupported SAMBU expression node: {type(expression).__name__}")


def statement_to_legacy(statement: Statement) -> tuple:
    """Convert one typed statement to the historical tuple representation."""
    if isinstance(statement, LetStatement):
        return ("let", statement.name, expression_to_legacy(statement.value))
    if isinstance(statement, FunctionStatement):
        return (
            "fn",
            statement.name,
            list(statement.parameters),
            [statement_to_legacy(item) for item in statement.body],
        )
    if isinstance(statement, SetFieldStatement):
        return (
            "set_field", expression_to_legacy(statement.target), statement.name,
            expression_to_legacy(statement.value),
        )
    if isinstance(statement, ClassStatement):
        return (
            "class", statement.name, statement.base_name,
            [statement_to_legacy(method) for method in statement.methods],
        )
    if isinstance(statement, ReturnStatement):
        return ("return", expression_to_legacy(statement.value))
    if isinstance(statement, IfStatement):
        return (
            "if",
            expression_to_legacy(statement.condition),
            [statement_to_legacy(item) for item in statement.then_body],
            [statement_to_legacy(item) for item in statement.else_body],
        )
    if isinstance(statement, ForStatement):
        return (
            "for",
            statement.variable,
            expression_to_legacy(statement.iterable),
            [statement_to_legacy(item) for item in statement.body],
        )
    if isinstance(statement, ExpressionStatement):
        return ("expr", expression_to_legacy(statement.expression))
    raise TypeError(f"unsupported SAMBU statement node: {type(statement).__name__}")
