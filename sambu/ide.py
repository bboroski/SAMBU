"""SAMBU IDE core: document snapshots, outlines and bounded completions.

This is a headless editor service layer. A graphical shell and LSP transport
can consume it; they are not included in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from . import ast as language_ast
from .articulatory import BUILTIN_ALIASES, KEYWORD_ALIASES
from .lexer import SambuSyntaxError, tokenize
from .machine import (
    CodeSamplingReport, SambuMachine, WorkspaceCheckReport,
    MAX_SOURCE_BYTES,
)
from .parser import parse_ast
from .runtime import _BUILTINS as _RUNTIME_BUILTINS
from .values import UNITS


_KEYWORDS = (
    "abstract", "and", "class", "else", "extends", "false", "final", "fn",
    "for", "if", "in", "interface", "is", "let", "null", "or", "private",
    "protected", "public", "return", "static", "trait", "true",
)
_PREDECLARED = (
    "pi", "e", "k_B", "h", "hbar", "c", "N_A", "R", "G", "version",
)
_COMPLETIONS = tuple(
    sorted(
        set(_KEYWORDS) | set(KEYWORD_ALIASES) | set(BUILTIN_ALIASES)
        | set(_RUNTIME_BUILTINS) | set(UNITS) | set(_PREDECLARED)
    )
)


class IDEError(RuntimeError):
    """An invalid document or workspace operation."""


@dataclass(frozen=True, slots=True)
class IDEDiagnostic:
    code: str
    severity: str
    message: str
    line: int
    column: int
    end_line: int
    end_column: int

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "end_column": self.end_column,
        }


@dataclass(frozen=True, slots=True)
class DocumentSymbol:
    name: str
    kind: str
    start_line: int
    end_line: int
    children: tuple["DocumentSymbol", ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "kind": self.kind,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "children": [child.to_dict() for child in self.children],
        }


@dataclass(frozen=True, slots=True)
class IDEInspection:
    uri: str
    version: int
    sha256: str
    line_count: int
    token_count: int
    syntax_valid: bool
    symbols: tuple[DocumentSymbol, ...]
    diagnostics: tuple[IDEDiagnostic, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "uri": self.uri,
            "version": self.version,
            "sha256": self.sha256,
            "line_count": self.line_count,
            "token_count": self.token_count,
            "syntax_valid": self.syntax_valid,
            "symbols": [symbol.to_dict() for symbol in self.symbols],
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


@dataclass(frozen=True, slots=True)
class _OpenDocument:
    version: int
    sha256: str


def _nested_symbols(statements: tuple[object, ...] | list[object]) -> tuple[DocumentSymbol, ...]:
    symbols: list[DocumentSymbol] = []
    for statement in statements:
        if isinstance(statement, language_ast.FunctionStatement):
            children = _nested_symbols(statement.body)
            symbols.append(DocumentSymbol(
                statement.name, "function", statement.span.start.line,
                statement.span.end.line, children,
            ))
        elif isinstance(statement, language_ast.ClassStatement):
            children = tuple(
                DocumentSymbol(
                    method.name, "method", method.span.start.line, method.span.end.line,
                    _nested_symbols(method.body),
                )
                for method in statement.methods
            )
            symbols.append(DocumentSymbol(
                statement.name, "class", statement.span.start.line,
                statement.span.end.line, children,
            ))
        elif isinstance(statement, language_ast.InterfaceStatement):
            children = tuple(
                DocumentSymbol(
                    method.name, "method", method.span.start.line, method.span.end.line
                )
                for method in statement.methods
            )
            symbols.append(DocumentSymbol(
                statement.name, "interface", statement.span.start.line,
                statement.span.end.line, children,
            ))
        elif isinstance(statement, language_ast.TraitStatement):
            children = tuple(
                DocumentSymbol(
                    method.name, "method", method.span.start.line, method.span.end.line
                )
                for method in statement.methods
            )
            symbols.append(DocumentSymbol(
                statement.name, "trait", statement.span.start.line,
                statement.span.end.line, children,
            ))
    return tuple(symbols)


def _diagnostic_from_error(error: Exception) -> IDEDiagnostic:
    span = getattr(error, "span", None)
    line = int(getattr(error, "line", getattr(getattr(span, "start", None), "line", 1)))
    column = int(getattr(error, "column", getattr(getattr(span, "start", None), "column", 1)))
    end_line = int(getattr(getattr(span, "end", None), "line", line))
    end_column = int(getattr(getattr(span, "end", None), "column", column + 1))
    return IDEDiagnostic(
        str(getattr(error, "code", "SAMBU-I001")),
        "error",
        str(error)[:512],
        line,
        column,
        end_line,
        end_column,
    )


class SambuIDE:
    """Headless editor core with versioned document snapshots and workspace tools."""

    def __init__(self, *, max_documents: int = 512):
        if isinstance(max_documents, bool) or not isinstance(max_documents, int) or not 1 <= max_documents <= 10_000:
            raise ValueError("max_documents must be an integer from 1 to 10,000")
        self.max_documents = max_documents
        self._documents: dict[str, _OpenDocument] = {}
        self.machine = SambuMachine(profile="sealed")

    def open_document(
        self, uri: str, source: str, *, version: int = 1
    ) -> IDEInspection:
        return self._inspect(uri, source, version, is_change=False)

    def change_document(
        self, uri: str, source: str, *, version: int
    ) -> IDEInspection:
        return self._inspect(uri, source, version, is_change=True)

    def _inspect(
        self, uri: str, source: str, version: int, *, is_change: bool
    ) -> IDEInspection:
        if not isinstance(uri, str) or not uri.strip():
            raise ValueError("document URI must be a non-empty string")
        if len(uri) > 2_048:
            raise ValueError("document URI exceeds 2,048 characters")
        if not isinstance(source, str):
            raise TypeError("document source must be text")
        try:
            source_size = len(source.encode("utf-8"))
        except UnicodeEncodeError as exc:
            raise ValueError("document contains text that cannot be encoded as UTF-8") from exc
        if source_size > MAX_SOURCE_BYTES:
            raise ValueError(f"document exceeds {MAX_SOURCE_BYTES} UTF-8 bytes")
        if isinstance(version, bool) or not isinstance(version, int) or version < 0:
            raise ValueError("document version must be a non-negative integer")
        previous = self._documents.get(uri)
        if is_change:
            if previous is None:
                raise IDEError(f"document is not open: {uri}")
            if version <= previous.version:
                raise IDEError(
                    f"stale document version {version}; current version is {previous.version}"
                )
        elif previous is None and len(self._documents) >= self.max_documents:
            raise IDEError(f"open document limit ({self.max_documents}) reached")
        elif previous is not None and version <= previous.version:
            raise IDEError(
                f"document version {version} must be newer than current version {previous.version}"
            )

        source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        diagnostics: tuple[IDEDiagnostic, ...] = ()
        symbols: tuple[DocumentSymbol, ...] = ()
        token_count = 0
        try:
            token_count = len(tokenize(source))
            program = parse_ast(source)
            symbols = _nested_symbols(program.statements)
        except (SambuSyntaxError, ValueError, TypeError, RecursionError) as exc:
            diagnostics = (_diagnostic_from_error(exc),)
        self._documents[uri] = _OpenDocument(version, source_hash)
        return IDEInspection(
            uri=uri,
            version=version,
            sha256=source_hash,
            line_count=max(1, source.count("\n") + 1),
            token_count=token_count,
            syntax_valid=not diagnostics,
            symbols=symbols,
            diagnostics=diagnostics,
        )

    def close_document(self, uri: str) -> bool:
        return self._documents.pop(uri, None) is not None

    def document_version(self, uri: str) -> int | None:
        value = self._documents.get(uri)
        return value.version if value is not None else None

    def complete(self, prefix: str = "", *, limit: int = 50) -> tuple[str, ...]:
        if not isinstance(prefix, str):
            raise TypeError("completion prefix must be text")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 500:
            raise ValueError("completion limit must be an integer from 1 to 500")
        folded = prefix.casefold()
        return tuple(
            item for item in _COMPLETIONS if item.casefold().startswith(folded)
        )[:limit]

    def inspect_workspace(self, path: str | Path) -> WorkspaceCheckReport:
        return self.machine.check_workspace(path)

    def sample_code(
        self, path: str | Path, *, denominator: int = 100, seed: int = 0
    ) -> CodeSamplingReport:
        return self.machine.sample_code(path, denominator=denominator, seed=seed)
