# SAMBU automatic improvement policy

Version: 1.0  
Established: 2026-11-10

This policy governs small, evidence-led repository changes. It does not claim that SAMBU currently contains a self-modifying or autonomous engineering agent. Automation may inspect, propose and validate changes only within the permissions actually granted to it.

## Required change sequence

1. Refresh evidence: read the current default branch, HEAD, recent commits, open/closed issues and PRs, workflow runs, source tree, tests, package metadata and relevant documentation. Do not use stale snapshots as current facts.
2. Audit CI before edits. Match the newest relevant completed workflow runs to the exact branch HEAD. Separate queued/in-progress from completed results. Inspect failed job steps and logs; label hypotheses separately from confirmed defects.
3. State the defect or benefit. Every change must cite a reproducible failure, measurable risk or stable requirement. Avoid speculative refactors and feature accumulation.
4. Choose one atomic scope. Make one small, reviewable change. Keep core runtime independent of optional IDE, web, Magento and other adapters. Preserve Python 3.10+ until a tested compatibility decision justifies otherwise.
5. Test with the change. Add a focused unit/regression test, including relevant boundaries and negative cases. Do not add a heavy mandatory core dependency to test configuration.
6. Preserve contracts. Keep public exports, parser behavior, serialized formats and runtime semantics compatible unless a documented, tested migration is approved.
7. Update evidence. Update relevant documentation and CHANGELOG. Keep the state matrix tied to a concrete revision and distinguish executable behavior from specification.
8. Validate configuration. Check package metadata, workflow permissions, Python matrix, install/test commands, optional extras, examples, documentation paths, dependencies and supported versions.
9. Verify the actual candidate. Run the available test and example suite. Wait for required GitHub checks on the candidate SHA. A running or stale check is not a pass.
10. Publish safely. Use a topic branch and a small PR. Never force-push, bypass checks or merge a draft. Merge only when the candidate's required checks are successful and repository policy permits it.
11. Report precisely. List changed files, commit/PR, exact test and CI outcomes, blocked work and next priority. Never claim deployment, production health, performance improvement or live integration without direct evidence.

## Risk boundaries

- Magento, RabbitMQ, checkout, inventory, payment, SQL, Redis, Varnish, PHP-FPM, OpenSearch, Nginx, CDN, backup and deployment guidance starts with read-only inspection and proposals.
- No production payment, queue/cache/data purge, production deployment or destructive operation is permitted in an unattended iteration.
- Any future production action requires explicit operator approval, audit trail, least privilege, dry-run and rollback plan.
- Do not confirm an order because a message was merely published. Commerce workflows require durable outbox, at-least-once delivery, persisted idempotency, explicit order states, safe inventory reservation and separately authorized/captured payment.
- Do not invent Magento APIs, supported platform versions, runtime integrations, system metrics or performance results.
- Do not treat a CLI simulation, sample XML, metadata model or documentation as a graphical IDE, live broker, live Magento connection or complete language feature.

## Rule evolution

- Add or strengthen a rule only when supported by a repeated defect, CI incident, stable security/compatibility requirement or user-approved architectural constraint.
- Record trigger, evidence, affected scope, regression test, owner/disable condition and history in RULE_CATALOG.md.
- Normalize duplicate rules instead of creating near-identical entries. Retain source ID and explain supersession.
- Record false positives and exceptions; do not silently weaken an existing rule.
- Documentation-only scores or metrics must never alter executable code.

## Change history

- 2026-11-10 / v1.0: established the evidence-first workflow and safety boundaries from the current project requirements. Added the explicit least-privilege workflow-permission check after the audit found that both existing CI workflows omitted a workflow-level permissions block. The candidate sets only contents: read and adds a standard-library regression test; effective permissions must still be verified through repository settings and the PR's own CI.
- 2026-11-10 review: a draft change removed the historical 0.8.0–0.1.0 changelog sections. The sections were restored and a release-heading regression test was added. No new policy rule was introduced because this is one observed incident; the existing repeated-evidence threshold remains in force.
