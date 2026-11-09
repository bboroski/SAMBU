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

    def skip_separators(self) -> None:
        while self.match(";"):
            pass

    def parse(self) -> list[tuple]:
        statements = self.statements("EOF")
        self.consume_kind("EOF", "Unexpected trailing input")
        return statements

    def consume_kind(self, kind: str, message: str) -> Token:
        if self.peek().kind == kind:
            return self.advance()
        token = self.peek()
        raise SambuSyntaxError(message, token.line, token.column)

    def statements(self, terminator: str) -> list[tuple]:
        out: list[tuple] = []
        while self.peek().kind != terminator and not (terminator == "OP" and self.check("}")):
            if self.peek().kind == "EOF":
                if terminator != "EOF":
                    token = self.peek()
                    raise SambuSyntaxError("Unterminated block; expected '}'", token.line, token.column)
                break
            if self.match(";"):
                continue
            out.append(self.statement())
            if self.match(";"):
                self.skip_separators()
            elif self.peek().kind != terminator and not (terminator == "OP" and self.check("}")) and self.peek().kind != "EOF":
                token = self.peek()
                raise SambuSyntaxError("Expected a newline or ';' between statements", token.line, token.column)
        return out

    def block(self) -> list[tuple]:
        self.consume("{", "Expected '{' to begin block")
        body = self.statements("OP")
        self.consume("}", "Expected '}' after block")
        return body

    def statement(self) -> tuple:
        token = self.peek()
        if token.kind == "IDENT":
            keyword = token.value
            if keyword == "let":
                self.advance()
                name = self.consume_ident("Expected a variable name after 'let'")
                self.consume("=", "Expected '=' after variable name")
                return ("let", str(name.value), self.expression())
            if keyword == "fn":
                self.advance()
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
                    raise SambuSyntaxError("Function parameters must be unique", name.line, name.column)
                return ("fn", str(name.value), params, self.block())
            if keyword == "return":
                self.advance()
                if self.check(";") or self.check("}") or self.peek().kind == "EOF":
                    return ("return", ("literal", None))
                return ("return", self.expression())
            if keyword == "if":
                self.advance()
                condition = self.expression()
                then_body = self.block()
                # A newline before else is optional. Only consume it when an
                # else branch follows; otherwise it still separates outer statements.
                after_then = self.current
                self.skip_separators()
                else_body: list[tuple] = []
                if self.peek().kind == "IDENT" and self.peek().value == "else":
                    self.advance()
                    if self.peek().kind == "IDENT" and self.peek().value == "if":
                        else_body = [self.statement()]
                    else:
                        else_body = self.block()
                else:
                    self.current = after_then
                return ("if", condition, then_body, else_body)
            if keyword == "for":
                self.advance()
                variable = self.consume_ident("Expected loop variable after 'for'")
                if not (self.peek().kind == "IDENT" and self.peek().value == "in"):
                    bad = self.peek()
                    raise SambuSyntaxError("Expected 'in' after loop variable", bad.line, bad.column)
                self.advance()
                iterable = self.expression()
                return ("for", str(variable.value), iterable, self.block())
        return ("expr", self.expression())

    def consume_ident(self, message: str) -> Token:
        if self.peek().kind == "IDENT":
            return self.advance()
        token = self.peek()
        raise SambuSyntaxError(message, token.line, token.column)

    def expression(self, min_precedence: int = 1) -> tuple:
        left = self.postfix(self.prefix())
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
            if token.value == "not":
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
            self.skip_separators()
            if not self.check("]"):
                while True:
                    items.append(self.expression())
                    self.skip_separators()
                    if not self.match(","):
                        break
                    self.skip_separators()
            self.consume("]", "Expected ']' after array elements")
            return ("array", items)
        raise SambuSyntaxError("Expected an expression", token.line, token.column)

    def postfix(self, expr: tuple) -> tuple:
        while True:
            if self.match("("):
                args: list[tuple] = []
                self.skip_separators()
                if not self.check(")"):
                    while True:
                        args.append(self.expression())
                        self.skip_separators()
                        if not self.match(","):
                            break
                        self.skip_separators()
                self.consume(")", "Expected ')' after function arguments")
                expr = ("call", expr, args)
                continue
            if self.match("."):
                name = self.consume_ident("Expected a field name after '.'")
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
