"""Lexer for the SAMBU language."""
from __future__ import annotations

from dataclasses import dataclass

from .source import SourcePosition, SourceSpan
from .articulatory import KEYWORD_ALIASES
from .glyph_syntax import GLYPH_TOKEN_ALIASES, GLYPH_TOKEN_ALIASES_BY_LENGTH


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

    def span_to_eof(start: int, start_line: int, start_col: int) -> SourceSpan:
        tail = source[start:]
        end_line = start_line + tail.count("\n")
        end_col = len(tail.rsplit("\n", 1)[-1]) + 1
        if "\n" not in tail:
            end_col = start_col + len(tail)
        return SourceSpan(
            SourcePosition(start, start_line, start_col),
            SourcePosition(n, end_line, end_col),
        )

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

        # C-style block comments are part of the glyph family.  They are
        # recognized before operators so the closing */ is never a token.
        if source.startswith("/*", i):
            start, start_line, start_col = i, line, col
            closing = source.find("*/", i + 2)
            if closing == -1:
                raise SambuSyntaxError(
                    "Unterminated block comment",
                    start_line,
                    start_col,
                    span=span_to_eof(start, start_line, start_col),
                    code="SAMBU-L003",
                )
            comment_end = closing + 2
            cursor = i
            while cursor < comment_end:
                newline = source.find("\n", cursor, comment_end)
                if newline == -1:
                    advance(source[cursor:comment_end])
                    cursor = comment_end
                    continue
                advance(source[cursor:newline])
                separator_line, separator_col = line, col
                advance("\n")
                tokens.append(
                    Token(
                        "SEMI", ";", separator_line, separator_col,
                        line, col, newline, newline + 1, "\\n",
                    )
                )
                cursor = newline + 1
            i = comment_end
            continue

        # $$...$$ is a verbatim multiline string.  Its contents do not
        # interpret escapes or any of the symbolic operators.
        if source.startswith("$$", i):
            start, start_line, start_col = i, line, col
            closing = source.find("$$", i + 2)
            if closing == -1:
                raise SambuSyntaxError(
                    "Unterminated raw string literal; expected closing '$$'",
                    start_line,
                    start_col,
                    span=span_to_eof(start, start_line, start_col),
                    code="SAMBU-L004",
                )
            value = source[i + 2:closing]
            raw = source[i:closing + 2]
            advance(raw)
            i = closing + 2
            emit("STRING", value, start, start_line, start_col, raw)
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
                raise SambuSyntaxError(
                    "Unterminated string literal",
                    start_line,
                    start_col,
                    span=span_to_eof(start, start_line, start_col),
                    code="SAMBU-L002",
                )
            raw = source[i:j + 1]
            body = raw[1:-1]
            value = body.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
            value = value.replace("\\\\", "\\").replace('\\"', '"').replace("\\'", "'")
            advance(raw)
            i = j + 1
            emit("STRING", value, start, start_line, start_col, raw)
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
            emit("NUMBER", float(raw), start, start_line, start_col, raw)
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

        # Match complete glyph spellings before ordinary operators or
        # punctuation.  This is deterministic longest-match lexing.
        glyph = next(
            (
                spelling
                for spelling in GLYPH_TOKEN_ALIASES_BY_LENGTH
                if source.startswith(spelling, i)
            ),
            None,
        )
        if glyph is not None:
            kind, value = GLYPH_TOKEN_ALIASES[glyph]
            start, start_line, start_col = i, line, col
            advance(glyph)
            i += len(glyph)
            emit(kind, value, start, start_line, start_col, glyph)
            continue

        op = next((op for op in _OPERATORS if source.startswith(op, i)), None)
        if op:
            start, start_line, start_col = i, line, col
            advance(op)
            i += len(op)
            emit("OP", op, start, start_line, start_col, op)
            continue
        if ch in _SINGLE:
            start, start_line, start_col = i, line, col
            kind = "SEMI" if ch == ";" else "OP"
            advance(ch)
            i += 1
            emit(kind, ch, start, start_line, start_col, ch)
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
