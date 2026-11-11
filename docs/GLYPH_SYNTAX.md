# SAMBU Glyph Syntax v1

Glyph Syntax is an additional spelling layer for the existing SAMBU language.
It does not introduce a second evaluator, alter operator precedence, or change
the typed or legacy AST. Every glyph token is translated by the lexer to an
established SAMBU token before parsing.

- **Version:** 1.0
- **Implementation:** `sambu/glyph_syntax.py` and `sambu/lexer.py`
- **Public API:** `GLYPH_SYNTAX_VERSION`, `GLYPH_TOKEN_ALIASES`, `tokenize`
- **Compatibility:** canonical SAMBU keywords and punctuation remain valid

## Lexical rules

The lexer applies deterministic **longest match** to the registered glyph
spellings. A complete multi-character glyph is emitted as one token; it is
never split into individual punctuation. Each token retains the original
spelling in `Token.lexeme` and preserves end-exclusive source offsets and
line/column coordinates.

The symbolic forms can be mixed with canonical SAMBU syntax in one file.

## Active glyph registry

| Glyph spelling | Canonical token | Role |
|---|---|---|
| `[[`, `--{` | `{` | Begin a block |
| `]]`, `}-` | `}` | End a block |
| `;;-`, `;;`, `:;`, `;:`, `;-`, `:-`, `-:` | `;` | Separate statements |
| `::` | `=` | Bind or initialize a value |
| `+_`, `++_` | `+` | Addition |
| `/+-*`, `*/+-*` | `*` | Multiplication |
| `-*/`, `/=-*/` | `/` | Division |
| `=]` | `==` | Equality |
| `='[` | `!=` | Inequality |
| `]-=`, `-]=` | `<` | Less-than |
| `=-]` | `>` | Greater-than |
| `\]=`, `=\]` | `<=` | Less-than or equal |
| `]=\`, `=-\` | `>=` | Greater-than or equal |

Canonical tokens are deliberately reused, so all expressions keep the existing
SAMBU precedence, right-associative exponentiation rules, runtime type checks
and diagnostics.

## String and comment forms

Single- and double-quoted strings continue to work as before. The paired
`$$...$$` form adds a verbatim multiline string: its content is returned as
one `STRING` token, with no escape processing. The lexer also accepts
C-style `/* ... */` block comments in addition to `#` line comments.

An unterminated raw string reports `SAMBU-L004`; an unterminated block comment
reports `SAMBU-L003`. Both diagnostics span from the opening delimiter to EOF.

## Example

```sambu
let scale :: 3;;-
let title :: $$Glyph mode
preserves source spelling.$$;;

fn square(value) [[
  return value /+-* value
]]

if square(scale) =] 9 --{
  print(title)
  print("symbolic syntax is active")
}- 
```

The equivalent classic spelling remains available:

```sambu
let scale = 3
let title = "Glyph mode preserves source spelling."

fn square(value) {
  return value * value
}

if square(scale) == 9 {
  print(title)
  print("symbolic syntax is active")
}
```

## Scope and reserved fragments

The registry intentionally activates complete, documented spellings rather
than rewriting arbitrary punctuation runs. Quote-bearing fragments such as
`"}{`, `}"{` and `++_}{'"}']]` are not independent operators: quote marks
retain their ordinary string-delimiter meaning. Long decorative or repeated
backslash/bracket chains that are not listed in the active registry remain
ordinary source text candidates, not executable grammar productions. They can
be placed safely inside `$$...$$` raw strings or comments.

This boundary prevents ambiguous tokenization and avoids assigning accidental
runtime meaning to arbitrary character sequences. New glyphs must be added to
the registry with a canonical token mapping, source-span tests and editor
grammar coverage before they are considered part of the language.
