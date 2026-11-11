# Emoji programming in SAMBU

SAMBU supports an emoji notation layer that maps selected emoji to the language's existing tokens. It is deliberately interoperable: emoji source is parsed into the same AST and executed by the same interpreter as ordinary SAMBU.

## Quick example

```sambu
📦 answer 🟰 6 ✖️ 7

🧱 twice(value) {
    ↩️ value ➕ value
}

📣(twice(answer))

❓ answer 🟰🟰 42 {
    📣("Emoji syntax is active")
} 🙃 {
    📣("The calculation changed")
}

🔁 item 🧺 [1, 2, 3] {
    📣(item)
}
```

Run it with the regular interpreter:

```bash
sambu examples/emoji_programming.sambu
```

## Supported aliases

| Emoji | Existing SAMBU token | Meaning |
|---|---|---|
| 📦 | `let` | Immutable binding |
| 🧱 | `fn` | Function declaration |
| ↩️ / ↩ | `return` | Return from a function |
| ❓ | `if` | Conditional |
| 🙃 | `else` | Alternative branch |
| 🔁 | `for` | Bounded iteration |
| 🧺 | `in` | Iteration delimiter |
| 📣 / 🖨️ / 🖨 | `print` | Standard output |
| ✅ / ❌ | `true` / `false` | Boolean literals |
| 🚫 | `not` | Logical negation |
| 🤝 / 🔀 | `and` / `or` | Logical operators |
| 🟰 | `=` | Binding or field assignment |
| 🟰🟰 | `==` | Equality comparison |
| ➕ / ➖ | `+` / `-` | Addition / subtraction |
| ✖️ / ✖ | `*` | Multiplication |
| ➗ | `/` | Division |

The regular punctuation, names, arrays, calls, comparisons, comments and strings remain available. Emoji aliases may be mixed with ordinary SAMBU tokens in the same file.

## Compatibility and boundaries

- Emoji are recognized only as source tokens. Emoji inside quoted strings and comments are unchanged.
- The lexer uses longest-match recognition, including common variation-selector forms such as `✖️` and `↩️`.
- Token spans retain the original Unicode source offsets and the original emoji lexeme for editor and diagnostic tooling.
- Emoji aliases do not add runtime capabilities, imports, file access, network access or unrestricted host execution.
- An emoji not listed above is not silently guessed; it receives the normal lexical diagnostic.
- The feature does not change the legacy tuple AST, typed AST, parser precedence or the semantics of existing programs.

The public `sambu.EMOJI_SYNTAX` mapping is available to tooling that needs to inspect the alias table.
