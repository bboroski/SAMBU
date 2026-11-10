# SAMBU editor and language identity

SAMBU source files use the `.sambu` extension. The repository includes a TextMate grammar at `syntaxes/SAMBU.tmLanguage.json` with the scope name `source.sambu`. Editors that load TextMate grammars can use it for baseline token coloring.

## GitHub language statistics

GitHub calculates the repository language bar with GitHub Linguist. A repository cannot register a brand-new language merely by adding a `.gitattributes` override: Linguist must first know the language in its central `languages.yml` registry. Unknown language names are not included in repository language statistics, even when `linguist-language=SAMBU` is specified.

Therefore this grammar is groundwork, not a claim that the GitHub language bar already recognizes SAMBU. The remaining external step is a contribution to `github-linguist/linguist` adding SAMBU as a programming language, its `.sambu` extension, and a compatible syntax grammar plus representative licensed samples. Once that support is accepted and deployed by GitHub, this repository can add:

```gitattributes
*.sambu linguist-language=SAMBU
```

Do not add that override before Linguist recognizes SAMBU: it cannot create the language entry by itself.

## Scope and limitations

- This is editor syntax highlighting, not a parser, compiler, formatter, or semantic validator.
- The grammar covers the current canonical keywords, the implemented articulatory aliases, common literals, comments, operators, declarations, and a curated set of built-in calls.
- Runtime semantics remain defined by the SAMBU lexer, parser, resolver, type/runtime layers, and tests.
- The grammar must evolve alongside the language; unsupported or reserved future words must not be presented as implemented features.
