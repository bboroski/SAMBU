"""Deterministic language-design craft pipeline for SAMBU.

The pipeline records lexical provenance, extracts selected fragments, maps
those fragments to terminal definitions, assembles grammar productions and
audits the resulting language blueprint. It does not mutate SAMBU's parser or
compile a user-defined grammar.
"""
from __future__ import annotations

import re
import unicodedata
from collections import deque
from typing import Callable

from .values import Record


_MAX_SOURCES = 64
_MAX_FRAGMENTS = 256
_MAX_TOKENS = 512
_MAX_RULES = 1024
_MAX_FRAGMENT_LENGTH = 1024
_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SYMBOL_RE = re.compile(r"^\$[A-Z][A-Z0-9_]*$")
_TOKEN_ROLES = frozenset({"keyword", "identifier", "operator", "delimiter", "literal"})


def _arity(args: list[object], count: int, signature: str) -> None:
    if len(args) != count:
        raise TypeError(f"{signature} expects {count} arguments")


def _string(value: object, label: str, limit: int = 256) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized.strip():
        raise ValueError(f"{label} must not be empty")
    if len(normalized) > limit:
        raise ValueError(f"{label} must be at most {limit} characters")
    return normalized


def _items(value: object, label: str, minimum: int, maximum: int) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{label} must be an array")
    if not minimum <= len(value) <= maximum:
        raise ValueError(f"{label} must contain between {minimum} and {maximum} items")
    return value


def _typed_record(value: object, expected: str, label: str) -> Record:
    if not isinstance(value, Record):
        raise TypeError(f"{label} must be a language-craft record")
    if value.get("kind") != expected:
        raise TypeError(f"{label} must be a {expected} record")
    return value


def craft_source(args: list[object]) -> Record:
    """Register source material and its declared provenance/reuse note."""
    _arity(args, 5, "craft_source(name, domain, provenance, reuse_note, fragments)")
    name = _string(args[0], "source name", 64).strip()
    domain = _string(args[1], "source domain", 64).strip()
    provenance = _string(args[2], "source provenance", 256).strip()
    reuse_note = _string(args[3], "source reuse note", 512).strip()
    fragments = _items(args[4], "source fragments", 1, _MAX_FRAGMENTS)
    clean: list[str] = []
    seen: set[str] = set()
    total = 0
    for index, value in enumerate(fragments, start=1):
        fragment = _string(value, f"fragment {index}", _MAX_FRAGMENT_LENGTH)
        key = fragment.casefold()
        if key in seen:
            raise ValueError(f"source fragments must be unique; duplicate at position {index}")
        seen.add(key)
        clean.append(fragment)
        total += len(fragment)
    if total > 65_536:
        raise ValueError("combined source fragments must not exceed 65,536 characters")
    return Record({
        "kind": "source",
        "name": name,
        "domain": domain,
        "provenance": provenance,
        "reuse_note": reuse_note,
        "fragments": clean,
        "fragment_count": len(clean),
    })


def craft_cut(args: list[object]) -> Record:
    """Select ordered source fragments while retaining exact provenance."""
    _arity(args, 2, "craft_cut(source, selected_fragments)")
    source = _typed_record(args[0], "source", "source")
    requested = _items(args[1], "selected fragments", 1, _MAX_FRAGMENTS)
    source_fragments = source.get("fragments")
    source_index = {text: index for index, text in enumerate(source_fragments)}
    selected: list[Record] = []
    seen: set[str] = set()
    for cut_index, value in enumerate(requested):
        fragment = _string(value, f"selected fragment {cut_index + 1}", _MAX_FRAGMENT_LENGTH)
        if fragment not in source_index:
            raise ValueError(f"selected fragment is not present in source {source.get('name')!r}")
        if fragment in seen:
            raise ValueError("a source fragment may be selected only once per cut")
        seen.add(fragment)
        selected.append(Record({
            "text": fragment,
            "source_index": source_index[fragment],
            "cut_index": cut_index,
        }))
    return Record({
        "kind": "cut",
        "source_name": source.get("name"),
        "domain": source.get("domain"),
        "provenance": source.get("provenance"),
        "reuse_note": source.get("reuse_note"),
        "fragments": selected,
        "fragment_count": len(selected),
    })


def craft_token(args: list[object]) -> Record:
    """Turn one selected fragment into a documented grammar terminal."""
    _arity(args, 6, "craft_token(cut, fragment, symbol, lexeme, meaning, role)")
    cut = _typed_record(args[0], "cut", "cut")
    fragment = _string(args[1], "source fragment", _MAX_FRAGMENT_LENGTH)
    symbol = _string(args[2], "terminal symbol", 64).strip()
    lexeme = _string(args[3], "lexeme", 64).strip()
    meaning = _string(args[4], "token meaning", 256).strip()
    role = _string(args[5], "token role", 32).strip().casefold()
    if not _NAME_RE.fullmatch(symbol):
        raise ValueError("terminal symbol must use ASCII identifier form, e.g. LET or NUMBER")
    if not lexeme or any(character.isspace() for character in lexeme):
        raise ValueError("lexeme must be a non-empty token spelling without whitespace")
    if role not in _TOKEN_ROLES:
        raise ValueError("token role must be keyword, identifier, operator, delimiter or literal")
    if role in {"keyword", "identifier"} and not lexeme.isidentifier():
        raise ValueError(f"{role} lexeme must be a valid identifier")
    if role in {"operator", "delimiter"} and lexeme.isidentifier():
        raise ValueError(f"{role} lexeme must be symbolic, not an identifier")
    selected = {item.get("text") for item in cut.get("fragments")}
    if fragment not in selected:
        raise ValueError("token fragment must first be selected by craft_cut")
    return Record({
        "kind": "token",
        "symbol": symbol,
        "lexeme": lexeme,
        "meaning": meaning,
        "role": role,
        "source_name": cut.get("source_name"),
        "source_domain": cut.get("domain"),
        "provenance": cut.get("provenance"),
        "reuse_note": cut.get("reuse_note"),
        "source_fragment": fragment,
    })


def craft_rule(args: list[object]) -> Record:
    """Declare one context-free production; an empty RHS represents epsilon."""
    _arity(args, 2, "craft_rule(nonterminal, symbols)")
    lhs = _string(args[0], "rule nonterminal", 64).strip()
    if not _NAME_RE.fullmatch(lhs):
        raise ValueError("rule nonterminal must be an ASCII identifier")
    rhs = args[1]
    if not isinstance(rhs, list):
        raise TypeError("rule symbols must be an array")
    if len(rhs) > 64:
        raise ValueError("a rule may contain at most 64 symbols")
    symbols: list[str] = []
    for index, value in enumerate(rhs):
        symbol = _string(value, f"rule symbol {index + 1}", 64).strip()
        if symbol.startswith("$"):
            if not _SYMBOL_RE.fullmatch(symbol):
                raise ValueError("terminal references must use $UPPERCASE_SYMBOL form")
        elif not _NAME_RE.fullmatch(symbol):
            raise ValueError("nonterminal references must be ASCII identifiers")
        symbols.append(symbol)
    return Record({"kind": "rule", "lhs": lhs, "rhs": symbols})


def craft_assemble(args: list[object]) -> Record:
    """Assemble sources, terminals and productions into a design snapshot."""
    _arity(args, 5, "craft_assemble(name, sources, tokens, rules, start)")
    name = _string(args[0], "language name", 96).strip()
    sources = _items(args[1], "sources", 1, _MAX_SOURCES)
    tokens = _items(args[2], "tokens", 1, _MAX_TOKENS)
    rules = _items(args[3], "rules", 1, _MAX_RULES)
    start = _string(args[4], "start nonterminal", 64).strip()
    if not _NAME_RE.fullmatch(start):
        raise ValueError("start nonterminal must be an ASCII identifier")
    source_records = [_typed_record(item, "source", "source item") for item in sources]
    token_records = [_typed_record(item, "token", "token item") for item in tokens]
    rule_records = [_typed_record(item, "rule", "rule item") for item in rules]
    return Record({
        "kind": "language_blueprint",
        "name": name,
        "start": start,
        "sources": source_records,
        "tokens": token_records,
        "rules": rule_records,
    })


def craft_master(args: list[object]) -> Record:
    """Audit references, collisions, reachability and source-fragment coverage."""
    _arity(args, 1, "craft_master(blueprint)")
    blueprint = _typed_record(args[0], "language_blueprint", "blueprint")
    sources: list[Record] = blueprint.get("sources")
    tokens: list[Record] = blueprint.get("tokens")
    rules: list[Record] = blueprint.get("rules")
    start: str = blueprint.get("start")
    errors: list[str] = []
    warnings: list[str] = []

    source_by_name: dict[str, Record] = {}
    for source in sources:
        key = str(source.get("name")).casefold()
        if key in source_by_name:
            errors.append(f"LC001 duplicate source name: {source.get('name')}")
        else:
            source_by_name[key] = source

    token_by_symbol: dict[str, Record] = {}
    lexeme_owner: dict[str, str] = {}
    for token in tokens:
        symbol = str(token.get("symbol"))
        lexeme = str(token.get("lexeme"))
        if symbol in token_by_symbol:
            errors.append("LC004 duplicate terminal symbol: $" + symbol)
        else:
            token_by_symbol[symbol] = token
        lexical_key = lexeme.casefold()
        if lexical_key in lexeme_owner:
            errors.append(
                f"LC005 duplicate lexeme {lexeme!r}: {lexeme_owner[lexical_key]} and {symbol}"
            )
        else:
            lexeme_owner[lexical_key] = symbol
        source_key = str(token.get("source_name")).casefold()
        source = source_by_name.get(source_key)
        if source is None:
            errors.append(f"LC002 token {symbol} references unknown source {token.get('source_name')!r}")
        elif token.get("source_fragment") not in source.get("fragments"):
            errors.append(f"LC003 token {symbol} references a fragment absent from its source")

    lhs_symbols = {str(rule.get("lhs")) for rule in rules}
    rule_signatures: set[tuple[str, tuple[str, ...]]] = set()
    adjacency: dict[str, set[str]] = {}
    used_terminals: set[str] = set()
    used_fragments = {
        (str(token.get("source_name")).casefold(), str(token.get("source_fragment")))
        for token in tokens
    }

    for rule in rules:
        lhs = str(rule.get("lhs"))
        rhs = tuple(str(item) for item in rule.get("rhs"))
        signature = (lhs, rhs)
        if signature in rule_signatures:
            errors.append(f"LC006 duplicate production: {lhs} -> {' '.join(rhs) or 'epsilon'}")
        rule_signatures.add(signature)
        for symbol in rhs:
            if symbol.startswith("$"):
                terminal = symbol[1:]
                if terminal not in token_by_symbol:
                    errors.append(f"LC007 undefined terminal reference: {symbol}")
                else:
                    used_terminals.add(terminal)
            elif symbol not in lhs_symbols:
                errors.append(f"LC008 undefined nonterminal reference: {symbol}")
            else:
                adjacency.setdefault(lhs, set()).add(symbol)

    if start not in lhs_symbols:
        errors.append(f"LC010 start nonterminal is not defined: {start}")

    reachable: set[str] = set()
    if start in lhs_symbols:
        pending = deque([start])
        while pending:
            current = pending.popleft()
            if current in reachable:
                continue
            reachable.add(current)
            for child in sorted(adjacency.get(current, set())):
                if child not in reachable:
                    pending.append(child)

    unreachable = sorted(lhs_symbols - reachable)
    if unreachable:
        warnings.append("LW001 unreachable nonterminals: " + ", ".join(unreachable))

    unused_tokens = sorted(set(token_by_symbol) - used_terminals)
    if unused_tokens:
        warnings.append("LW002 unused terminals: " + ", ".join("$" + item for item in unused_tokens))

    all_fragments = {
        (str(source.get("name")).casefold(), str(fragment))
        for source in sources
        for fragment in source.get("fragments")
    }
    unused_fragments = all_fragments - used_fragments
    if unused_fragments:
        warnings.append(f"LW003 {len(unused_fragments)} source fragments were not mapped to terminals")

    token_coverage = len(used_terminals) / len(token_by_symbol) if token_by_symbol else 0.0
    grammar_reachability = len(reachable) / len(lhs_symbols) if lhs_symbols else 0.0
    source_coverage = len(used_fragments & all_fragments) / len(all_fragments) if all_fragments else 0.0
    ready = not errors
    status = "ready" if ready and not warnings else "ready_with_warnings" if ready else "blocked"

    return Record({
        "language": blueprint.get("name"),
        "status": status,
        "ready": ready,
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "source_count": len(sources),
        "source_fragment_count": len(all_fragments),
        "mapped_fragment_count": len(used_fragments & all_fragments),
        "source_coverage": source_coverage,
        "token_count": len(tokens),
        "referenced_terminal_count": len(used_terminals),
        "token_coverage": token_coverage,
        "production_count": len(rules),
        "nonterminal_count": len(lhs_symbols),
        "reachable_nonterminal_count": len(reachable),
        "grammar_reachability": grammar_reachability,
        "start": start,
        "scope": "design_audit_only",
    })


LANGUAGE_CRAFT_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "craft_source": craft_source,
    "craft_cut": craft_cut,
    "craft_token": craft_token,
    "craft_rule": craft_rule,
    "craft_assemble": craft_assemble,
    "craft_master": craft_master,
}


__all__ = ["LANGUAGE_CRAFT_BUILTINS"]
