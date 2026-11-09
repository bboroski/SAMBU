"""Recursive-descent statement parser and Pratt expression parser."""
from __future__ import annotations

from .lexer import Token, SambuSyntaxError, tokenize


_PRECEDENCE = {
    "||": 1, "or": 1,
    "&&": 2, "and": 2,
    "==": 3, "!=": 3,
    "<": 4, "<=": 4, ">": 4, ">=": 4,
    "+": 5, "-": 5,
    "*": 6, "/": 6,
    "^": 7, "**": 7,
}


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if self.peek().kind != "EOF":
            self.current += 1
        return self.previous()

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
        raise SambuSyntaxError(message, token.line, token.column)

    def parse(self) -> list[tuple]:
        statements: list[tuple] = []
        while self.peek().kind != "EOF":
            if self.match(";"):
                continue
            statements.append(self.statement())
            while self.match(";"):
                pass
            if self.peek().kind != "EOF" and self.previous().value != ";":
                token = self.peek()
                raise SambuSyntaxError("Expected a newline or ';' between statements", token.line, token.column)
        return statements

    def statement(self) -> tuple:
        if self.peek().kind == "IDENT" and self.peek().value == "let":
            self.advance()
            name = self.peek()
            if name.kind != "IDENT":
                raise SambuSyntaxError("Expected a variable name after 'let'", name.line, name.column)
            self.advance()
            self.consume("=", "Expected '=' after variable name")
            return ("let", str(name.value), self.expression())
        return ("expr", self.expression())

    def expression(self, min_precedence: int = 1) -> tuple:
        left = self.prefix()
        left = self.postfix(left)
        while True:
            op = self.peek().value
            precedence = _PRECEDENCE.get(str(op), 0)
            if precedence < min_precedence:
                break
            self.advance()
            right = self.expression(precedence if op in ("^", "**") else precedence + 1)
            left = ("binary", str(op), left, right)
        return left

    def prefix(self) -> tuple:
        token = self.advance()
        if token.kind == "NUMBER":
            return ("literal", token.value)
        if token.kind == "STRING":
            return ("literal", token.value)
        if token.kind == "IDENT":
            if token.value == "true": return ("literal", True)
            if token.value == "false": return ("literal", False)
            if token.value == "null": return ("literal", None)
            if token.value in ("not",):
                return ("unary", "!", self.expression(8))
            return ("name", str(token.value))
        if token.value in ("-", "+", "!"):
            return ("unary", str(token.value), self.expression(8))
        if token.value == "(":
            expr = self.expression()
            self.consume(")", "Expected ')' after expression")
            return expr
        if token.value == "[":
            items: list[tuple] = []
            if not self.check("]"):
                while True:
                    items.append(self.expression())
                    if not self.match(","):
                        break
            self.consume("]", "Expected ']' after array elements")
            return ("array", items)
        raise SambuSyntaxError("Expected an expression", token.line, token.column)

    def postfix(self, expr: tuple) -> tuple:
        while True:
            if self.match("("):
                args: list[tuple] = []
                if not self.check(")"):
                    while True:
                        args.append(self.expression())
                        if not self.match(","):
                            break
                self.consume(")", "Expected ')' after function arguments")
                expr = ("call", expr, args)
                continue
            if self.match("."):
                name = self.peek()
                if name.kind != "IDENT":
                    raise SambuSyntaxError("Expected a field name after '.'", name.line, name.column)
                self.advance()
                expr = ("field", expr, str(name.value))
                continue
            if self.match("["):
                index = self.expression()
                self.consume("]", "Expected ']' after index")
                expr = ("index", expr, index)
                continue
            break
        return expr


def parse(source: str) -> list[tuple]:
    return Parser(tokenize(source)).parse()
