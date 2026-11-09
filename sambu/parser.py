"""Recursive-descent statement parser and Pratt expression parser."""
from __future__ import annotations

from dataclasses import replace

from .ast import (
    ArrayExpr,
    BinaryExpr,
    CallExpr,
    ClassStatement,
    Expression,
    ExpressionStatement,
    FieldExpr,
    ForStatement,
    FunctionStatement,
    IfStatement,
    IndexExpr,
    LetStatement,
    LiteralExpr,
    NameExpr,
    Program,
    ReturnStatement,
    SetFieldStatement,
    Statement,
    UnaryExpr,
)
from .lexer import Token, SambuSyntaxError, tokenize
from .source import SourcePosition, SourceSpan


_PRECEDENCE = {
    "||": 1, "or": 1,
    "&&": 2, "and": 2,
    "==": 3, "!=": 3,
    "<": 4, "<=": 4, ">": 4, ">=": 4,
    "+": 5, "-": 5,
    "*": 6, "/": 6,
    "^": 7, "**": 7,
}


def _cover(start: SourceSpan, end: SourceSpan) -> SourceSpan:
    """Return the smallest source range covering two ordered ranges."""
    return SourceSpan(start.start, end.end)


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def syntax_error(self, message: str, token: Token | None = None) -> SambuSyntaxError:
        """Build a parser diagnostic anchored to the offending token."""
        token = token or self.peek()
        return SambuSyntaxError(
            message, token.line, token.column, span=token.span, code="SAMBU-P001"
        )

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        token = self.peek()
        if token.kind != "EOF":
            self.current += 1
        return token

    def check(self, value: object) -> bool:
        return self.peek().value == value

    def match(self, *values: object) -> bool:
        if self.check_any(*values):
            self.advance()
            return True
        return False

    def check_any(self, *values: object) -> bool:
        return self.peek().value in values

    def consume(self, value: object, message: str) -> Token:
        if self.check(value):
            return self.advance()
        token = self.peek()
        raise self.syntax_error(message, token)

    def skip_separators(self) -> None:
        while self.match(";"):
            pass

    def parse_ast(self) -> Program:
        statements = self.statements("EOF")
        eof = self.consume_kind("EOF", "Unexpected trailing input")
        span = SourceSpan(SourcePosition(0, 1, 1), eof.span.end)
        return Program(tuple(statements), span)

    def parse(self) -> list[tuple]:
        """Parse source into the historical tuple AST.

        Kept as the compatibility entry point. New language tooling should use
        parse_ast to retain typed nodes and source spans.
        """
        return self.parse_ast().to_legacy()

    def consume_kind(self, kind: str, message: str) -> Token:
        if self.peek().kind == kind:
            return self.advance()
        token = self.peek()
        raise self.syntax_error(message, token)

    def statements(self, terminator: str) -> list[Statement]:
        out: list[Statement] = []
        while self.peek().kind != terminator and not (terminator == "OP" and self.check("}")):
            if self.peek().kind == "EOF":
                if terminator != "EOF":
                    token = self.peek()
                    raise self.syntax_error("Unterminated block; expected '}'", token)
                break
            if self.match(";"):
                continue
            out.append(self.statement())
            if self.match(";"):
                self.skip_separators()
            elif self.peek().kind != terminator and not (terminator == "OP" and self.check("}")) and self.peek().kind != "EOF":
                token = self.peek()
                raise self.syntax_error("Expected a newline or ';' between statements", token)
        return out

    def block(self) -> tuple[tuple[Statement, ...], Token, Token]:
        opening = self.consume("{", "Expected '{' to begin block")
        body = self.statements("OP")
        closing = self.consume("}", "Expected '}' after block")
        return tuple(body), opening, closing

    def statement(self) -> Statement:
        token = self.peek()
        if token.kind == "IDENT":
            keyword = token.value
            if keyword == "class":
                start = self.advance()
                name = self.consume_ident("Expected a class name after 'class'")
                base_name: str | None = None
                if self.peek().kind == "IDENT" and self.peek().value == "extends":
                    self.advance()
                    base_name = str(self.consume_ident("Expected a base class name after 'extends'").value)
                body, _, closing = self.block()
                methods: list[FunctionStatement] = []
                method_names: set[str] = set()
                for member in body:
                    if not isinstance(member, FunctionStatement):
                        raise self.syntax_error("Class bodies may contain method declarations only", token)
                    if member.name in method_names:
                        raise self.syntax_error(f"Duplicate method {member.name!r}", name)
                    method_names.add(member.name)
                    methods.append(member)
                return ClassStatement(
                    str(name.value), base_name, tuple(methods),
                    _cover(start.span, closing.span),
                )
            if keyword == "let":
                start = self.advance()
                name = self.consume_ident("Expected a variable name after 'let'")
                self.consume("=", "Expected '=' after variable name")
                value = self.expression()
                return LetStatement(
                    str(name.value), value, _cover(start.span, value.span)
                )
            if keyword == "fn":
                start = self.advance()
                name = self.consume_ident("Expected a function name after 'fn'")
                self.consume("(", "Expected '(' after function name")
                params: list[str] = []
                self.skip_separators()
                if not self.check(")"):
                    while True:
                        params.append(str(self.consume_ident("Expected parameter name").value))
                        self.skip_separators()
                        if not self.match(","):
                            break
                        self.skip_separators()
                self.consume(")", "Expected ')' after parameters")
                if len(params) != len(set(params)):
                    raise self.syntax_error("Function parameters must be unique", name)
                body, _, closing = self.block()
                return FunctionStatement(
                    str(name.value), tuple(params), body,
                    _cover(start.span, closing.span),
                )
            if keyword == "return":
                start = self.advance()
                if self.check(";") or self.check("}") or self.peek().kind == "EOF":
                    value = LiteralExpr(None, SourceSpan.point(start.span.end))
                else:
                    value = self.expression()
                return ReturnStatement(value, _cover(start.span, value.span))
            if keyword == "if":
                start = self.advance()
                condition = self.expression()
                then_body, _, then_close = self.block()
                after_then = self.current
                self.skip_separators()
                else_body: tuple[Statement, ...] = ()
                end_span = then_close.span
                if self.peek().kind == "IDENT" and self.peek().value == "else":
                    self.advance()
                    if self.peek().kind == "IDENT" and self.peek().value == "if":
                        else_body = (self.statement(),)
                        end_span = else_body[-1].span
                    else:
                        else_body, _, else_close = self.block()
                        end_span = else_close.span
                else:
                    self.current = after_then
                return IfStatement(
                    condition, then_body, else_body, _cover(start.span, end_span)
                )
            if keyword == "for":
                start = self.advance()
                variable = self.consume_ident("Expected loop variable after 'for'")
                if not (self.peek().kind == "IDENT" and self.peek().value == "in"):
                    bad = self.peek()
                    raise self.syntax_error("Expected 'in' after loop variable", bad)
                self.advance()
                iterable = self.expression()
                body, _, closing = self.block()
                return ForStatement(
                    str(variable.value), iterable, body,
                    _cover(start.span, closing.span),
                )
        expression = self.expression()
        if self.match("="):
            if not isinstance(expression, FieldExpr):
                raise self.syntax_error("Only object fields can be assigned; local bindings are immutable")
            value = self.expression()
            return SetFieldStatement(
                expression.target, expression.name, value,
                _cover(expression.span, value.span),
            )
        return ExpressionStatement(expression, expression.span)

    def consume_ident(self, message: str) -> Token:
        if self.peek().kind == "IDENT":
            return self.advance()
        token = self.peek()
        raise self.syntax_error(message, token)

    def expression(self, min_precedence: int = 1) -> Expression:
        left = self.postfix(self.prefix())
        while True:
            op = self.peek().value
            precedence = _PRECEDENCE.get(str(op), 0)
            if precedence < min_precedence:
                break
            self.advance()
            right = self.expression(precedence if op in ("^", "**") else precedence + 1)
            left = BinaryExpr(str(op), left, right, _cover(left.span, right.span))
        return left

    def prefix(self) -> Expression:
        token = self.advance()
        if token.kind == "NUMBER":
            return LiteralExpr(token.value, token.span)
        if token.kind == "STRING":
            return LiteralExpr(token.value, token.span)
        if token.kind == "IDENT":
            if token.value == "true":
                return LiteralExpr(True, token.span)
            if token.value == "false":
                return LiteralExpr(False, token.span)
            if token.value == "null":
                return LiteralExpr(None, token.span)
            if token.value == "not":
                operand = self.expression(8)
                return UnaryExpr("!", operand, _cover(token.span, operand.span))
            return NameExpr(str(token.value), token.span)
        if token.value in ("-", "+", "!"):
            operand = self.expression(8)
            return UnaryExpr(str(token.value), operand, _cover(token.span, operand.span))
        if token.value == "(":
            expression = self.expression()
            closing = self.consume(")", "Expected ')' after expression")
            return replace(expression, span=_cover(token.span, closing.span))
        if token.value == "[":
            items: list[Expression] = []
            self.skip_separators()
            if not self.check("]"):
                while True:
                    items.append(self.expression())
                    self.skip_separators()
                    if not self.match(","):
                        break
                    self.skip_separators()
            closing = self.consume("]", "Expected ']' after array elements")
            return ArrayExpr(tuple(items), _cover(token.span, closing.span))
        raise self.syntax_error("Expected an expression", token)

    def postfix(self, expression: Expression) -> Expression:
        while True:
            if self.match("("):
                arguments: list[Expression] = []
                self.skip_separators()
                if not self.check(")"):
                    while True:
                        arguments.append(self.expression())
                        self.skip_separators()
                        if not self.match(","):
                            break
                        self.skip_separators()
                closing = self.consume(")", "Expected ')' after function arguments")
                expression = CallExpr(
                    expression, tuple(arguments),
                    _cover(expression.span, closing.span),
                )
                continue
            if self.match("."):
                name = self.consume_ident("Expected a field name after '.'")
                expression = FieldExpr(
                    expression, str(name.value), _cover(expression.span, name.span)
                )
                continue
            if self.match("["):
                index = self.expression()
                closing = self.consume("]", "Expected ']' after index")
                expression = IndexExpr(
                    expression, index, _cover(expression.span, closing.span)
                )
                continue
            break
        return expression


def parse_ast(source: str) -> Program:
    """Parse source into immutable typed nodes carrying end-exclusive spans."""
    return Parser(tokenize(source)).parse_ast()


def parse(source: str) -> list[tuple]:
    """Parse source into the backward-compatible tuple-based AST."""
    return Parser(tokenize(source)).parse()
