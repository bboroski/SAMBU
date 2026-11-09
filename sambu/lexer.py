"""Lexer for the SAMBU language."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int


class SambuSyntaxError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"{message} (line {line}, column {column})")
        self.line = line
        self.column = column


_OPERATORS = ("==", "!=", "<=", ">=", "&&", "||", "**")
_SINGLE = set("+-*/^<>=!(),.[];{}")


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

    while i < n:
        ch = source[i]
        if ch in " \t\r":
            advance(ch); i += 1; continue
        if ch == "\n":
            tokens.append(Token("SEMI", ";", line, col))
            advance(ch); i += 1; continue
        if ch == "#":
            j = source.find("\n", i)
            if j == -1:
                break
            advance(source[i:j]); i = j; continue
        if ch in "\"'":
            start_line, start_col, quote = line, col, ch
            j = i + 1
            escaped = False
            while j < n:
                c = source[j]
                if c == quote and not escaped:
                    break
                if c == "\n" and not escaped:
                    raise SambuSyntaxError("Unterminated string literal", start_line, start_col)
                if c == "\\" and not escaped:
                    escaped = True
                else:
                    escaped = False
                j += 1
            if j >= n:
                raise SambuSyntaxError("Unterminated string literal", start_line, start_col)
            raw = source[i:j + 1]
            body = raw[1:-1]
            value = body.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r")
            value = value.replace("\\\\", "\\").replace('\\"', '"').replace("\\'", "'")
            tokens.append(Token("STRING", value, start_line, start_col))
            advance(raw); i = j + 1; continue
        if ch.isdigit() or (ch == "." and i + 1 < n and source[i + 1].isdigit()):
            start = i
            start_line, start_col = line, col
            if ch == ".":
                i += 1
                while i < n and source[i].isdigit(): i += 1
            else:
                while i < n and source[i].isdigit(): i += 1
                if i < n and source[i] == ".":
                    i += 1
                    while i < n and source[i].isdigit(): i += 1
            if i < n and source[i] in "eE":
                exp_start = i
                i += 1
                if i < n and source[i] in "+-": i += 1
                digits = i
                while i < n and source[i].isdigit(): i += 1
                if digits == i:
                    i = exp_start
            raw = source[start:i]
            tokens.append(Token("NUMBER", float(raw), start_line, start_col))
            advance(raw)
            continue
        if ch.isalpha() or ch == "_":
            start = i
            start_line, start_col = line, col
            i += 1
            while i < n and (source[i].isalnum() or source[i] == "_"):
                i += 1
            raw = source[start:i]
            tokens.append(Token("IDENT", raw, start_line, start_col))
            advance(raw)
            continue
        op = next((op for op in _OPERATORS if source.startswith(op, i)), None)
        if op:
            tokens.append(Token("OP", op, line, col))
            advance(op); i += len(op); continue
        if ch in _SINGLE:
            kind = "SEMI" if ch == ";" else "OP"
            tokens.append(Token(kind, ch, line, col))
            advance(ch); i += 1; continue
        raise SambuSyntaxError(f"Unexpected character {ch!r}", line, col)

    tokens.append(Token("EOF", None, line, col))
    return tokens
