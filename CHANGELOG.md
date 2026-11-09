# Changelog

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
