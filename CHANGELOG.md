# Changelog

## 0.6.0 — 2026-11-09

- Added classes, object construction, init constructors, mutable instance fields, instance methods, single inheritance and method overriding while preserving the legacy parser AST API.
- Added deterministic rock-paper-scissors and legal-state tic-tac-toe built-ins, including turn, occupancy, win/draw and unreachable-board validation.
- Added typed AST spans and legacy conversion for class declarations and object-field assignments.
- Added OOP/game regression tests, an executable example and an OOP/game language guide.
- Clarified that interfaces, traits, access modifiers, generics, static members, explicit super dispatch and static class typing remain future work.

## 0.5.1 — 2026-11-09

- Added an immutable typed AST with end-exclusive source spans for every expression and statement.
- Added `parse_ast()` while preserving the exact legacy tuple structure returned by `parse()`.
- Added `Program.to_legacy()` for incremental migration by tooling and interpreter clients.
- Corrected the public `__version__` value to match package release metadata.
- Fixed parser EOF token handling so incomplete expressions report the actual EOF position.
- Added AST span, nested-block, Unicode-offset, tuple-compatibility, and EOF-diagnostic regression coverage.


## 0.5.0 — 2026-11-09

- Added `audio_profile` to validate tempo, swing, snare timing, master ceiling and production-feature flags without rendering or mastering audio.
- Added `order_pipeline` to check durable-outbox, persisted-idempotency, inventory-reservation, payment-authorization, post-commit acknowledgement, supervised-worker and DLQ invariants with at-least-once semantics.
- Added `studio_offer` for configurable introductory-class conversion targets and multi-session package economics.
- Added `capture_node` to model resistance depletion and ownership transfer only when a target reaches zero resistance.
- Added a cross-domain runnable blueprint example, regression tests and operational boundary documentation.
- Preserved the existing queue, schedule, funnel, network and `capture_tower` behavior.


## 0.4.0 — 2026-11-09

- Added public immutable `SourcePosition` and end-exclusive `SourceSpan` primitives.
- Extended lexer tokens with source offsets, end positions, and a stable `span` property while preserving the original fields.
- Added stable lexical and parser diagnostic codes with token-aligned ranges; retained legacy `line` / `column` attributes and message formatting.
- Exported the source-location, token, lexer, parser, and syntax-diagnostic interfaces from the `sambu` package.
- Kept the tuple-based parser AST and interpreter behavior backward-compatible; node-level AST spans remain a follow-up milestone.
- Added regression tests for Unicode offsets, multiline positions, EOF spans, and diagnostic ranges.


## 0.3.0 — 2026-11-09

- Expanded SAMBU's systems-modeling scope with commerce queue-planning primitives.
- Added `queue_profile` for bounded worker concurrency, prefetch, retry limits, and optional dead-letter routing.
- Added `retry_schedule` for capped exponential backoff plans.
- Added `idempotency_key` for stable namespaced request identifiers.
- Added a runnable commerce queue example and regression tests for validation and edge cases.
- Added Magento / Adobe Commerce architecture guidance covering checkout boundaries, durable messaging, idempotency, inventory reservations, payment orchestration, retries, dead letters, observability, and deployment.
- Added an IDE architecture specification for semantic tokens, dimensional diagnostics, completion, REPL, tracing, and the Diplomat Night theme.
- Clarified that these are language-level models and design specifications, not live Magento, RabbitMQ, or IDE integrations.
- Preserved the scientific mechanics core and existing language behavior.

## 0.2.0 — 2026-11-09

- Added user-defined functions, lexical scope, `return`, conditionals, and bounded loops.
- Added networks, negotiation, resource allocation, funnels, A/B screening, schedules, and operational models.
- Added Neo-Modern Diplomat examples and domain documentation.

## 0.1.0 — 2026-11-09

- Initial lexer, parser, evaluator, CLI, SI-aware quantities, statistical-mechanics helpers, examples, tests, and CI.
