# SAMBU Glyph Syntax (SGS-1)

SGS-1 is a punctuation-first source surface for SAMBU. It is not a second
interpreter: the lexer normalizes glyph terminals into the canonical SAMBU token
stream, and the existing parser, typed AST, interpreter, diagnostics, and runtime
remain authoritative. Canonical and articulatory spellings remain valid and can
be mixed with SGS-1.

## Structural terminals

| Glyph | Canonical form | Meaning |
|---|---|---|
| `[[` | `[` + `[` | Two opening delimiters; begin a nested array literal |
| `]]` | `]` + `]` | Two closing delimiters; finish a nested array literal |
| `}-` | `fn` | Begin a function declaration |
| `--{` | `{` | Open a statement block |
| `}{` | `} else {` | Close the current conditional arm and open its alternative |
| `::` | `.` | Access a record field |
| `;;`, `:;`, `;:` | `;` | Separate statements or array items |

The `[[` and `]]` pairs intentionally remain two ordinary bracket tokens. This
preserves SAMBU's existing nested-array syntax rather than collapsing the pair
into a single token. The `}{` branch marker expands to the parser's three
structural tokens and is valid between an `if` body and its `else` body.

## Operator terminals

SGS-1 keeps canonical SAMBU precedence and evaluation order. Glyph aliases are
normalized before parsing:

| Glyphs | Canonical operator |
|---|---|
| `+_`, `++_`, `/+-*` | `+` |
| `-=` | `-` |
| `*/`, `/*`, `-*/`, `-/*`, `/*-`, `*/-`, `*/=`, `=/*`, `/*=`, `*-/`, `=*`, `-*/+_`, `=*/--`, `/]--*/=*` | `*` |
| `/-`, `/-=`, `/=-`, `/--`, `=/`, `/-]*/`, `/=-*/` | `/` |
| `=-*-`, `--**`, `==*` | `**` |
| `:-`, `-:` | `<`, `>` |
| `;;-`, `;-` | `<=`, `>=` |
| `=-`, `=]`, `=-]` | `==` |
| `]=`, `=\]`, `]=\`, `\]=` | `!=` |
| `]-=`, `--=` | `=` |

The lexer uses longest-match recognition. Every recognized token retains its
original spelling in `Token.lexeme`; source spans point to the characters typed
by the author. Glyph aliases do not change numeric semantics, precedence,
evaluation order, or runtime capabilities.

## Multiline glyph strings

The pair `"{` and `}"` delimits a multiline string. A close marker preceded by
an unescaped backslash is treated as string content. Standard single- and
double-quoted strings are unchanged.

```sambu
let message = "{First line
Second line}"
```

## Complete example

```sambu
}- square(value) --{
    return value */ value
}

let coordinates = [[1, 2], [3, 4]];;
let answer = square(6) +_ 2;;

if (answer :- 37) --{
    print(coordinates[0][0])
}{ 
    print(0)
}
```

The program is equivalent to the canonical SAMBU form:

```sambu
fn square(value) {
    return value * value
}

let coordinates = [[1, 2], [3, 4]]
let answer = square(6) + 2

if (answer < 37) {
    print(coordinates[0][0])
} else {
    print(0)
}
```

## Compatibility and status

SGS-1 is an implemented experimental syntax profile. It adds no new runtime
built-ins, types, ownership rules, asynchronous behavior, or native code
generation. Run `python -m pytest` for the regression suite. The exported
`GLYPH_ALIASES` and `GLYPH_SYNTAX_VERSION` constants expose the active
terminal registry to language tooling.
