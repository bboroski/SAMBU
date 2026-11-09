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
    "==": 3, "!=": 3, "is": 3,
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
            if keyword == "class" or (
                keyword in {"abstract", "final"}
                and self.current + 1 < len(self.tokens)
                and self.tokens[self.current + 1].value == "class"
            ):
                return self.class_declaration()
            if keyword == "interface":
                return self.interface_declaration()
            if keyword == "trait":
                return self.trait_declaration()
            if keyword == "let":
                start = self.advance()
                name = self.consume_ident("Expected a variable name after 'let'")
                self.consume("=", "Expected '=' after variable name")
                value = self.expression()
                return LetStatement(
                    str(name.value), value, _cover(start.span, value.span)
                )
            if keyword == "fn":
                return self.function_declaration({})
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

    def function_declaration(
        self,
        modifiers: set[str],
        *,
        allow_abstract: bool = False,
    ) -> FunctionStatement:
        start = self.consume("fn", "Expected 'fn' before method name")
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
        closing_params = self.consume(")", "Expected ')' after parameters")
        if len(params) != len(set(params)):
            raise self.syntax_error("Function parameters must be unique", name)
        is_abstract = "abstract" in modifiers
        if self.check("{"):
            if is_abstract:
                raise self.syntax_error("Abstract methods cannot have a body", self.peek())
            body, _, closing = self.block()
            end_span = closing.span
        else:
            if not (allow_abstract or is_abstract):
                raise self.syntax_error("Expected a method body", self.peek())
            if not is_abstract:
                raise self.syntax_error("A body-less method must be abstract", self.peek())
            self.match(";")
            body = ()
            end_span = closing_params.span
        visibility = next(
            (item for item in ("private", "protected", "public") if item in modifiers),
            "public",
        )
        return FunctionStatement(
            str(name.value), tuple(params), body, _cover(start.span, end_span),
            visibility=visibility,
            is_static="static" in modifiers,
            is_abstract=is_abstract,
            is_final="final" in modifiers,
        )

    def _member_modifiers(self) -> set[str]:
        allowed = {"public", "protected", "private", "static", "abstract", "final"}
        modifiers: set[str] = set()
        while self.peek().kind == "IDENT" and self.peek().value in allowed:
            value = str(self.advance().value)
            if value in modifiers:
                raise self.syntax_error(f"Duplicate member modifier {value!r}", self.previous())
            modifiers.add(value)
        visibility = modifiers & {"public", "protected", "private"}
        if len(visibility) > 1:
            raise self.syntax_error("A member can have only one visibility modifier", self.previous())
        if "abstract" in modifiers and "final" in modifiers:
            raise self.syntax_error("A method cannot be both abstract and final", self.previous())
        return modifiers

    def class_declaration(self) -> ClassStatement:
        modifiers: set[str] = set()
        while self.peek().kind == "IDENT" and self.peek().value in {"abstract", "final"}:
            value = str(self.advance().value)
            if value in modifiers:
                raise self.syntax_error(f"Duplicate class modifier {value!r}", self.previous())
            modifiers.add(value)
        start = self.consume("class", "Expected 'class' after class modifiers")
        name = self.consume_ident("Expected a class name after 'class'")
        base_name: str | None = None
        interfaces: list[str] = []
        traits: list[str] = []
        while self.peek().kind == "IDENT" and self.peek().value in {"extends", "implements", "uses"}:
            clause = str(self.advance().value)
            if clause == "extends":
                if base_name is not None:
                    raise self.syntax_error("A class can extend only one base class", self.previous())
                base_name = str(self.consume_ident("Expected a base class name after 'extends'").value)
                continue
            target = interfaces if clause == "implements" else traits
            while True:
                target.append(str(self.consume_ident(f"Expected a name after '{clause}'").value))
                if not self.match(","):
                    break
        if len(interfaces) != len(set(interfaces)) or len(traits) != len(set(traits)):
            raise self.syntax_error("Interface and trait names must be unique", name)
        if "abstract" in modifiers and "final" in modifiers:
            raise self.syntax_error("A class cannot be both abstract and final", name)
        self.consume("{", "Expected '{' to begin class body")
        methods: list[FunctionStatement] = []
        method_names: set[str] = set()
        static_fields: list[tuple[str, Expression]] = []
        field_names: set[str] = set()
        while not self.check("}"):
            if self.peek().kind == "EOF":
                raise self.syntax_error("Unterminated class body; expected '}'")
            self.skip_separators()
            if self.check("}"):
                break
            member_modifiers = self._member_modifiers()
            if self.peek().kind == "IDENT" and self.peek().value == "fn":
                method = self.function_declaration(member_modifiers, allow_abstract=True)
                if method.name in method_names:
                    raise self.syntax_error(f"Duplicate method {method.name!r}", name)
                if method.is_static and method.parameters and method.parameters[0] == "self":
                    raise self.syntax_error("Static methods do not receive an implicit 'self'", name)
                if not method.is_static and not method.is_abstract and (
                    not method.parameters or method.parameters[0] != "self"
                ):
                    raise self.syntax_error("Instance methods must declare 'self' as their first parameter", name)
                method_names.add(method.name)
                methods.append(method)
                self.skip_separators()
                continue
            if (
                "static" in member_modifiers
                and self.peek().kind == "IDENT"
                and self.peek().value == "let"
            ):
                self.advance()
                field_name = self.consume_ident("Expected a static field name")
                self.consume("=", "Expected '=' after static field name")
                value = self.expression()
                field_key = str(field_name.value)
                if field_key in field_names:
                    raise self.syntax_error(f"Duplicate static field {field_key!r}", field_name)
                if field_key in method_names:
                    raise self.syntax_error(f"Static field {field_key!r} conflicts with a method", field_name)
                field_names.add(field_key)
                static_fields.append((field_key, value))
                self.skip_separators()
                continue
            raise self.syntax_error("Class bodies contain methods and 'static let' fields only")
        closing = self.consume("}", "Expected '}' after class body")
        return ClassStatement(
            str(name.value), base_name, tuple(methods), _cover(start.span, closing.span),
            is_abstract="abstract" in modifiers,
            is_final="final" in modifiers,
            interfaces=tuple(interfaces),
            traits=tuple(traits),
            static_fields=tuple(static_fields),
        )

    def interface_declaration(self) -> InterfaceStatement:
        start = self.consume("interface", "Expected 'interface'")
        name = self.consume_ident("Expected an interface name")
        self.consume("{", "Expected '{' to begin interface body")
        methods: list[FunctionStatement] = []
        names: set[str] = set()
        while not self.check("}"):
            if self.peek().kind == "EOF":
                raise self.syntax_error("Unterminated interface body; expected '}'")
            self.skip_separators()
            if self.check("}"):
                break
            modifiers = self._member_modifiers()
            if modifiers - {"public", "abstract"}:
                raise self.syntax_error("Interface methods support only public and abstract modifiers")
            modifiers.update({"public", "abstract"})
            method = self.function_declaration(modifiers, allow_abstract=True)
            if method.is_static or method.name in names:
                raise self.syntax_error("Interface method names must be unique and instance-based")
            if method.parameters and method.parameters[0] != "self":
                raise self.syntax_error("Interface methods must declare 'self' first")
            names.add(method.name)
            methods.append(method)
            self.skip_separators()
        closing = self.consume("}", "Expected '}' after interface body")
        return InterfaceStatement(str(name.value), tuple(methods), _cover(start.span, closing.span))

    def trait_declaration(self) -> TraitStatement:
        start = self.consume("trait", "Expected 'trait'")
        name = self.consume_ident("Expected a trait name")
        self.consume("{", "Expected '{' to begin trait body")
        methods: list[FunctionStatement] = []
        names: set[str] = set()
        while not self.check("}"):
            if self.peek().kind == "EOF":
                raise self.syntax_error("Unterminated trait body; expected '}'")
            self.skip_separators()
            if self.check("}"):
                break
            modifiers = self._member_modifiers()
            if "static" in modifiers or "abstract" in modifiers:
                raise self.syntax_error("Traits currently support concrete instance methods only")
            method = self.function_declaration(modifiers)
            if not method.parameters or method.parameters[0] != "self":
                raise self.syntax_error("Trait methods must declare 'self' first")
            if method.name in names:
                raise self.syntax_error(f"Duplicate trait method {method.name!r}")
            names.add(method.name)
            methods.append(method)
            self.skip_separators()
        closing = self.consume("}", "Expected '}' after trait body")
        return TraitStatement(str(name.value), tuple(methods), _cover(start.span, closing.span))

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
