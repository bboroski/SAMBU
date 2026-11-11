"""Lexer for the SAMBU language."""
from __future__ import annotations

from dataclasses import dataclass

from .source import SourcePosition, SourceSpan
from .articulatory import KEYWORD_ALIASES


@dataclass(frozen=True)
class Token:
    """A lexical token with an end-exclusive source span.

    The original line and column attributes remain one-based and unchanged.
    """

    kind: str
    value: object
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None
    start_offset: int = 0
    end_offset: int = 0
    lexeme: str | None = None

    @property
    def span(self) -> SourceSpan:
        end_line = self.line if self.end_line is None else self.end_line
        end_column = self.column if self.end_column is None else self.end_column
        return SourceSpan(
            SourcePosition(self.start_offset, self.line, self.column),
            SourcePosition(self.end_offset, end_line, end_column),
        )


class SambuSyntaxError(Exception):
    """Lexical or parse error with a stable code and source range."""

    def __init__(
        self,
        message: str,
        line: int,
        column: int,
        *,
        span: SourceSpan | None = None,
        code: str = "SAMBU-SYN-001",
    ) -> None:
        self.message = message
        self.line = line
        self.column = column
        self.span = span or SourceSpan.point(SourcePosition(0, line, column))
        self.code = code
        super().__init__(f"{message} (line {line}, column {column})")


_OPERATORS = ("==", "!=", "<=", ">=", "&&", "||", "**")
_SINGLE = set("+-*/%^<>=!(),.[];{}")

# SGS-1 glyph aliases normalize into the established SAMBU token vocabulary.
GLYPH_SYNTAX_VERSION = "SGS-1"
GLYPH_ALIASES: dict[str, tuple[str, object]] = {
      "}-": ("IDENT", "fn"), "--{": ("OP", "{"), "::": ("OP", "."),
    ";;": ("SEMI", ";"), ":;": ("SEMI", ";"), ";:": ("SEMI", ";"),
    "++_": ("OP", "+"), "/+-*": ("OP", "+"), "+_": ("OP", "+"),
    "-=": ("OP", "-"),
    "-*/+_": ("OP", "*"), "/]--*/=*": ("OP", "*"), "=*/--": ("OP", "*"),
    "-*/": ("OP", "*"), "-/*": ("OP", "*"), "/*-": ("OP", "*"),
    "*/-": ("OP", "*"), "*/=": ("OP", "*"), "=/*": ("OP", "*"),
    "/*=": ("OP", "*"), "/*": ("OP", "*"), "*/": ("OP", "*"),
    "*-/": ("OP", "*"), "=*": ("OP", "*"),
    "/=-*/": ("OP", "/"), "/-]*/": ("OP", "/"), "/-=": ("OP", "/"),
    "/=-": ("OP", "/"), "/--": ("OP", "/"), "/-": ("OP", "/"), "=/": ("OP", "/"),
    "=-*-": ("OP", "**"), "--**": ("OP", "**"), "==*": ("OP", "**"),
    ";;-": ("OP", "<="), ";-": ("OP", ">="), ":-": ("OP", "<"), "-:": ("OP", ">"),
    "=-]": ("OP", "=="), "=]": ("OP", "=="), "=-": ("OP", "=="),
    "]=\\": ("OP", "!="), "=\\]": ("OP", "!="), "\\]=": ("OP", "!="),
    "]-=": ("OP", "="), "--=": ("OP", "="),
}
_GLYPH_TOKENS = tuple(sorted(GLYPH_ALIASES, key=len, reverse=True))


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    i, line, col = 0, 1, 1
    n = len(source)

    def advance(text: str) -> None:
        nonlocal line, col
        lines = text.split("\n")
        if len(lines) > 1:
            line += len(lines) - 1
            col = len(lines[-1]) + 1
        else:
            col += len(text)

    def emit(
        kind: str,
        value: object,
        start: int,
        start_line: int,
        start_col: int,
        lexeme: str | None = None,
    ) -> None:
        tokens.append(Token(kind, value, start_line, start_col, line, col, start, i, lexeme))

    while i < n:
        ch = source[i]
        if ch in " \t\r":
            advance(ch)
            i += 1
            continue
        if ch == "\n":
            start, start_line, start_col = i, line, col
            advance(ch)
            i += 1
            emit("SEMI", ";", start, start_line, start_col)
            continue
        if ch == "#":
            j = source.find("\n", i)
            if j == -1:
                advance(source[i:])
                i = n
                break
            advance(source[i:j])
            i = j
            continue
        # Raw multiline glyph string: $ ... $. Escape the closing marker with \$.
        if source.startswith("$", i):
            start, start_line, start_col = i, line, col
            j = i + 2
            while j < n:
                if source.startswith("\\$", j):
                    j += 3
                    continue
                if source.startswith("$", j):
                    break
                j += 1
            if j >= n:
                raise SambuSyntaxError(
                    "Unterminated raw glyph string literal", start_line, start_col,
                    span=SourceSpan.point(SourcePosition(start, start_line, start_col)),
                    code="SAMBU-L004",
                )
            raw = source[i:j + 2]
            body = source[i + 2:j].replace("\\$", "$")
            advance(raw)
            i = j + 2
            emit("STRING", body, start, start_line, start_col, raw)
            continue

        # Multiline glyph string: "{ ... }".
        if source.startswith('"{', i):
            start, start_line, start_col = i, line, col
            j = i + 2
            escaped = False
            while j < n:
                if source.startswith('}"', j) and not escaped:
                    break
                current = source[j]
                if current == "\\" and not escaped:
                    escaped = True
                else:
                    escaped = False
                j += 1
            if j >= n:
                raise SambuSyntaxError(
                    "Unterminated glyph string literal", start_line, start_col,
                    span=SourceSpan.point(SourcePosition(start, start_line, start_col)),
                    code="SAMBU-L003",
                )
            raw = source[i:j + 2]
            body = source[i + 2:j]
            value = body.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
            value = value.replace("\\\\", "\\").replace('\\"', '"').replace("\\'", "'")
            advance(raw)
            i = j + 2
            emit("STRING", value, start, start_line, start_col, raw)
            continue

        # Compact else-arm marker: close the current block, then open its else block.
        if source.startswith("}{", i):
            start, start_line, start_col = i, line, col
            advance("}{")
            i += 2
            tokens.append(Token("OP", "}", start_line, start_col,
                                start_line, start_col + 1, start, start + 1, "}"))
            tokens.append(Token("IDENT", "else", start_line, start_col + 1,
                                start_line, start_col + 1, start + 1, start + 1, "else"))
            tokens.append(Token("OP", "{", start_line, start_col + 1,
                                line, col, start + 1, i, "{"))
            continue

        glyph = next((item for item in _GLYPH_TOKENS if source.startswith(item, i)), None)
        if glyph is not None:
            start, start_line, start_col = i, line, col
            kind, value = GLYPH_ALIASES[glyph]
            advance(glyph)
            i += len(glyph)
            emit(kind, value, start, start_line, start_col, glyph)
            continue

        if ch in "\"'":
            start, start_line, start_col, quote = i, line, col, ch
            j = i + 1
            escaped = False
            while j < n:
                c = source[j]
                if c == quote and not escaped:
                    break
                if c == "\n" and not escaped:
                    tail = source[i:j]
                    end_line = start_line + tail.count("\n")
                    end_col = len(tail.rsplit("\n", 1)[-1]) + 1
                    if "\n" not in tail:
                        end_col = start_col + len(tail)
                    raise SambuSyntaxError(
                        "Unterminated string literal", start_line, start_col,
                        span=SourceSpan(
                            SourcePosition(start, start_line, start_col),
                            SourcePosition(j, end_line, end_col),
                        ),
                        code="SAMBU-L002",
                    )
                if c == "\\" and not escaped:
                    escaped = True
                else:
                    escaped = False
                j += 1
            if j >= n:
                tail = source[i:]
                end_line = start_line + tail.count("\n")
                end_col = len(tail.rsplit("\n", 1)[-1]) + 1
                if "\n" not in tail:
                    end_col = start_col + len(tail)
                raise SambuSyntaxError(
                    "Unterminated string literal", start_line, start_col,
                    span=SourceSpan(
                        SourcePosition(start, start_line, start_col),
                        SourcePosition(n, end_line, end_col),
                    ),
                    code="SAMBU-L002",
                )
            raw = source[i:j + 1]
            body = raw[1:-1]
            value = body.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
            value = value.replace("\\\\", "\\").replace('\\"', '"').replace("\\'", "'")
            advance(raw)
            i = j + 1
            emit("STRING", value, start, start_line, start_col)
            continue
        if ch.isdigit() or (ch == "." and i + 1 < n and source[i + 1].isdigit()):
            start = i
            start_line, start_col = line, col
            if ch == ".":
                i += 1
                while i < n and source[i].isdigit():
                    i += 1
            else:
                while i < n and source[i].isdigit():
                    i += 1
                if i < n and source[i] == ".":
                    i += 1
                    while i < n and source[i].isdigit():
                        i += 1
            if i < n and source[i] in "eE":
                exp_start = i
                i += 1
                if i < n and source[i] in "+-":
                    i += 1
                digits = i
                while i < n and source[i].isdigit():
                    i += 1
                if digits == i:
                    i = exp_start
            raw = source[start:i]
            advance(raw)
            emit("NUMBER", float(raw), start, start_line, start_col)
            continue
        if ch.isalpha() or ch == "_":
            start = i
            start_line, start_col = line, col
            i += 1
            while i < n and (source[i].isalnum() or source[i] == "_"):
                i += 1
            raw = source[start:i]
            advance(raw)
            # Canonicalize only reserved articulatory words. Keep the original
            # spelling separately so source-aware tools can display what was typed.
            canonical = KEYWORD_ALIASES.get(raw, raw)
            emit("IDENT", canonical, start, start_line, start_col, raw)
            continue
        op = next((op for op in _OPERATORS if source.startswith(op, i)), None)
        if op:
            start, start_line, start_col = i, line, col
            advance(op)
            i += len(op)
            emit("OP", op, start, start_line, start_col)
            continue
        if ch in _SINGLE:
            start, start_line, start_col = i, line, col
            kind = "SEMI" if ch == ";" else "OP"
            advance(ch)
            i += 1
            emit(kind, ch, start, start_line, start_col)
            continue
        raise SambuSyntaxError(
            f"Unexpected character {ch!r}", line, col,
            span=SourceSpan(
                SourcePosition(i, line, col),
                SourcePosition(i + 1, line, col + 1),
            ),
            code="SAMBU-L001",
        )

    tokens.append(Token("EOF", None, line, col, line, col, n, n))
    return tokens
