"""Canonical registry for SAMBU's symbolic Glyph Syntax v1.

Glyph spellings are lexical aliases, not a second runtime.  Each spelling maps
to an existing token consumed by the established parser and interpreter.
Longest-match tokenization is applied by :mod:`sambu.lexer`.
"""

GLYPH_SYNTAX_VERSION = "1.0"

# (token kind, canonical token value).  Keep this table declarative so editor
# tooling, tests and documentation can audit the exact spelling contract.
GLYPH_TOKEN_ALIASES: dict[str, tuple[str, str]] = {
    # Block delimiters.
    "[[": ("OP", "{"),
    "--{": ("OP", "{"),
    "]]": ("OP", "}"),
    "}-": ("OP", "}"),

    # Statement separators.
    ";;-": ("SEMI", ";"),
    ";;": ("SEMI", ";"),
    ":;": ("SEMI", ";"),
    ";:": ("SEMI", ";"),
    ";-": ("SEMI", ";"),
    ":-": ("SEMI", ";"),
    "-:": ("SEMI", ";"),

    # Binding and arithmetic.
    "::": ("OP", "="),
    "+_": ("OP", "+"),
    "++_": ("OP", "+"),
    "/+-*": ("OP", "*"),
    "*/+-*": ("OP", "*"),
    "-*/": ("OP", "/"),
    "/=-*/": ("OP", "/"),

    # Comparison family.  The bracket/backslash forms are intentionally
    # atomic; they must never be split into unrelated punctuation tokens.
    "=]": ("OP", "=="),
    "='[": ("OP", "!="),
    "]-=": ("OP", "<"),
    "-]=": ("OP", "<"),
    "=-]": ("OP", ">"),
    r"\]=": ("OP", "<="),
    r"=\]": ("OP", "<="),
    "]=\\": ("OP", ">="),
    "=-\\": ("OP", ">="),
}

GLYPH_TOKEN_ALIASES_BY_LENGTH = tuple(
    sorted(GLYPH_TOKEN_ALIASES, key=lambda spelling: (-len(spelling), spelling))
)
