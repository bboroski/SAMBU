# Changelog

## 0.7.0 — 2026-11-09

- Added native Unicode-aware text metrics, approximate syllable counting, rhyme-tail grouping, line-level prosody and alliteration diagnostics.
- Added a non-destructive text-craft workflow that preserves colloquial language, marked stress, dialect forms and intentional phonetic distortion.
- Fixed parser precedence for the runtime-supported `is` type operator and added class/interface regression coverage.
- Exported interface and trait AST node types through the public package API.
- Synchronized package, runtime and README version metadata at 0.7.0.
- Added text-craft documentation, an executable example and regression tests.


## 0.6.0 — 2026-11-09

- Added the separate sambu_studio package and sambu-studio inspect CLI.
- Added read-only Magento XML inspection for DI preferences/plugins and message-queue topics, consumers, exchanges, bindings and publishers.
- Added static cross-file queue reference checks and versioned JSON output.
- Added XML size, UTF-8, DTD/entity and symlink-read guardrails with stable diagnostics.
- Added an illustrative Magento module fixture and CI execution for text and JSON inspection.
- Corrected MQ documentation: topics use exactly one request or schema contract; Magento topology uses topic exchanges; publishers and consumers have separate declarations.
- Added the Neo-Modern Developer language strategy: typed AST, effect-aware async, generated-PHP interoperability, semantic refactoring and Magento dependency graph roadmap.
- Updated package/runtime versions and added the sambu-studio console entry point.
- Kept official XSD validation, merged runtime DI resolution, RabbitMQ access, SSH and mutating operations explicitly out of scope.
## 0.5.1 — 2026-11-09

- Added an immutable typed AST with end-exclusive source spans for every expression and statement.
- Added `parse_ast()` while preserving the exact legacy tuple structure returned by `parse()`.
- Added `Program.to_legacy()` for incremental migration by tooling and interpreter clients.
- Corrected the public `__version__` value to match package release metadata.
- Fixed parser EOF token handling so incomplete expressions report the actual EOF position.
- Added AST span, nested-block, Unicode-offset, tuple-compatibility, and EOF-diagnostic regression coverage.


## 0.5.0 — 2026-11-09

- Added audio_profile, order_pipeline, studio_offer and capture_node planning models.
- Added a cross-domain runnable blueprint example, regression tests and architecture documentation.

## 0.4.0 — 2026-11-09

- Added SourcePosition, SourceSpan, token ranges and stable ranged syntax diagnostics.
- Preserved the tuple-based parser AST and existing line/column API.

## 0.3.0 — 2026-11-09

- Added queue capacity, retry and idempotency planning models and Magento architecture guidance.

## 0.2.0 — 2026-11-09

- Added user-defined functions, lexical scope, return, conditionals, bounded loops and systems models.

## 0.1.0 — 2026-11-09

- Initial lexer, parser, evaluator, CLI, SI-aware quantities, statistical-mechanics helpers, examples, tests and CI.
