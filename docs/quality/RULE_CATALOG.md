# SAMBU engineering rule catalog

Catalog version: 0.1  
Snapshot date: 2026-11-10

Each rule has a stable ID, version, scope, trigger/evidence, validation and disable condition. Rules are guardrails, not a claim that the repository has an autonomous rule-evolution engine.

## Source completeness

The project requirements refer to an earlier two-series catalogue of 100 rules (50 + 50). That source list was not present in the current repository tree and could not be recovered from the available prior-conversation context during this audit. The entries below therefore normalize only requirements explicitly available in the current engineering brief and verified repository findings. They are not represented as the missing original 100 rules; no ungrounded entries are fabricated. Import and reconcile the original 100 when its source becomes available.

## Confirmed rules

| ID | Version | Scope | Rule / trigger | Evidence and validation | Disable / exception | History |
|---|---:|---|---|---|---|---|
| SAM-Q-001 | 1 | All changes | Keep each iteration small and atomic. | PR diff and one stated objective. | Split only when a dependency requires a coordinated change; explain it. | 2026-11-10 baseline |
| SAM-Q-002 | 1 | All changes | Require a reproducible defect, measurable risk or stable requirement before editing. | Issue, failing test, CI log or explicit requirement. | None; speculative work stays in backlog. | 2026-11-10 baseline |
| SAM-Q-003 | 1 | Code | Add a focused test with the implementation. | Unit/regression test on candidate SHA. | Documentation-only changes use applicable link/config checks instead. | 2026-11-10 baseline |
| SAM-Q-004 | 1 | Code | Test boundaries, malformed input and regressions. | Negative and boundary assertions. | Document a justified untestable external boundary. | 2026-11-10 baseline |
| SAM-Q-005 | 1 | Public API | Preserve public API and parser compatibility. | Export/API regression tests and documented migration. | Breaking change only with explicit versioned migration. | 2026-11-10 baseline |
| SAM-Q-006 | 1 | Releases | Update documentation and CHANGELOG for user-visible changes. | Changed docs and release-note diff. | Internal-only change may record why no public note is needed. | 2026-11-10 baseline |
| SAM-Q-007 | 1 | Dependencies/config | Check dependency necessity, optionality and supported-version compatibility. | pyproject/workflow diff and install matrix. | Add a core dependency only with measured necessity. | 2026-11-10 baseline |
| SAM-Q-008 | 1 | Reporting | Do not claim behavior without code/test/CI evidence. | Claims trace to paths, tests or exact run. | None. | 2026-11-10 baseline |
| SAM-Q-009 | 1 | CI | A pass must match the exact candidate SHA and completed success conclusion. | Workflow run head SHA, job status and logs. | None; stale or in-progress runs are not passes. | 2026-11-10 baseline |
| SAM-Q-010 | 1 | Publishing | Use topic branches; never force-push or bypass checks; do not merge drafts. | PR state, checks and merge result. | Repository policy may require human approval. | 2026-11-10 baseline |
| SAM-Q-011 | 1 | Architecture | Keep Python-hosted core separate from optional IDE, web, Magento and engine adapters. | Import graph, dependencies and package metadata. | A dependency enters core only with measured justification. | 2026-11-10 baseline |
| SAM-Q-012 | 1 | Compatibility | Preserve Python 3.10+ support until a tested decision changes it. | requires-python and CI matrix. | Change only with migration note and complete matrix. | 2026-11-10 baseline |
| SAM-Q-013 | 1 | Types | Distinguish runtime dimensional checks from static semantic analysis. | Tests and explicit analyzer implementation. | Never mark static analysis complete from runtime behavior alone. | 2026-11-10 baseline |
| SAM-Q-014 | 1 | Native compiler | Label native HIR/MIR/LIR as experimental until CFG, lowering and code-generation claims have direct proof. | Native source, verifier tests and C11 CI. | Status advances only by implemented/tested milestone. | 2026-11-10 baseline |
| SAM-Q-015 | 1 | OOP | Implement one executable OOP mechanism at a time across AST, runtime and tests. | Language example and regression test. | No completeness claim while listed mechanisms remain absent. | 2026-11-10 baseline |
| SAM-Q-016 | 1 | Games | Keep RPS and Tic-Tac-Toe deterministic and validate legal state transitions and terminal states. | Exhaustive outcome/turn matrix. | No random or network-dependent behavior in core rules. | 2026-11-10 baseline |
| SAM-Q-017 | 1 | Magento | Treat XML/metadata inspection as static unless a versioned live adapter is tested. | Versioned fixture, official contract reference and adapter tests. | No invented API or platform compatibility claim. | 2026-11-10 baseline |
| SAM-Q-018 | 1 | Commerce | Require durable outbox, at-least-once semantics, persisted idempotency and explicit order/payment/inventory states. | Failure-injection and idempotency tests. | No production writes in unattended automation. | 2026-11-10 baseline |
| SAM-Q-019 | 1 | Production operations | Start with read-only telemetry; require operator approval, audit, least privilege, dry-run and rollback for future action. | Operation plan and audit record. | Production mutation remains disabled by default. | 2026-11-10 baseline |
| SAM-Q-020 | 1 | Metrics | Never invent health, entropy, cache, synergy or performance metrics. | Raw measurement, formula, threshold and environment. | Unmeasured values must be marked unavailable. | 2026-11-10 baseline |
| SAM-Q-021 | 1 | Performance | Make no language/runtime speed claim without comparable benchmarks. | Reproducible harness, baselines and methodology. | None. | 2026-11-10 baseline |
| SAM-Q-022 | 1 | Studio | Do not describe CLI inspection as a graphical IDE or live integration. | Executable surface and user-facing documentation. | Status changes only after GUI/adapter tests exist. | 2026-11-10 baseline |
| SAM-Q-023 | 1 | GitHub Actions | Declare least-privilege workflow token permissions explicitly. Trigger: audit found no workflow-level permissions in tests.yml or native.yml. | permissions: contents: read in both workflows plus tests/test_workflow_permissions.py; candidate CI must pass. | Broaden only for a documented job that requires a specific permission; scope it to that job. | Added 2026-11-10 from verified configuration gap |

## Lifecycle

- Active: applies by default.
- Proposed: awaiting required evidence or regression test.
- Superseded: replaced by another ID; retain the old entry and point to the successor.
- Disabled: requires a reason, approver and date; never delete history.

No automatic activation of new rules occurs from a single noisy warning. The workflow-permission rule is grounded in a stable least-privilege requirement and a directly observed configuration gap; the added test prevents silent regression.
