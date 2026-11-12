# OCTAGON PYRAMID — SAMBU

**Status:** architecture proposal implemented on an isolated feature branch; not yet merged into `main`.

## Mission

This repository is an independent node in a 13-repository system. It participates in every shared method while retaining ownership of its source code, release cycle, secrets, data and domain decisions. Integration is contract-based, not a monolithic code merge.

## Geometry

- **Octagonal foundation:** eight reusable methods applied by every node.
- **Pyramid layers:** repository intelligence → cross-repository matrix → coordination → execution → verification.
- **NEXUS apex:** a logical coordinator that indexes capabilities, contracts, events and health. It is not a single point of runtime failure; nodes continue safely when it is unavailable.

## Eight foundation methods

| # | Method | Required behavior |
|---:|---|---|
| 1 | **ANALYSIS** | Inspect repository structure, interfaces, dependencies, tests and runtime behavior. |
| 2 | **DECOMPOSITION** | Split cross-project goals into bounded, independently reviewable tasks. |
| 3 | **SYNTHESIS** | Combine compatible designs through versioned contracts; never copy code blindly. |
| 4 | **SYNCHRONIZATION** | Exchange versioned events and dependency state without sharing mutable internals. |
| 5 | **ADAPTATION** | Translate shared contracts into each repository's native language and conventions. |
| 6 | **VALIDATION** | Verify schemas, security, tests, provenance and compatibility before promotion. |
| 7 | **OPTIMIZATION** | Measure bottlenecks and improve only with reproducible evidence. |
| 8 | **EVOLUTION** | Propose incremental improvements, guarded by review, tests and rollback. |

Every method is applied locally in this repository and to each of the other 12 repositories through published contracts. No method is exclusive to one node.

## Complete cross-repository matrix

Participants:
- `bboroski/SAMBU`
- `bboroski/ToolNG`
- `bboroski/ReaperCripple`
- `bboroski/Kloz`
- `bboroski/CO`
- `bboroski/SaintSI`
- `bboroski/Klipot`
- `bboroski/NUN`
- `bboroski/NUNLauncher`
- `bboroski/Fragile-Baby`
- `bboroski/Luci`
- `bboroski/Hellduck`
- `bboroski/9circ`

For each ordered pair of distinct repositories, expose eight method pathways: analysis, decomposition, synthesis, synchronization, adaptation, validation, optimization and evolution. With 13 nodes this defines **156 directed repository relationships × 8 methods = 1,248 cross-repository method pathways**. Self-processing is local and is not counted in that total.

A pathway is a capability/contract, not permission to read private data or write to another repository. Each node publishes only approved metadata and versioned interfaces. Direct repository-to-repository mutation is prohibited.

## Pyramid execution flow

1. **Foundation:** publish method definitions, schema versions and trust rules.
2. **Repository intelligence:** discover this repository's capabilities, interfaces, tests and ownership.
3. **Cross-repository matrix:** match capabilities and dependencies across all participants.
4. **Coordination:** produce a dependency graph and conflict-free work plan.
5. **Execution:** create isolated branches and small proposed changes.
6. **Verification:** run relevant tests, security checks, compatibility checks and provenance validation.
7. **NEXUS:** aggregate status and recommend promotion; it cannot bypass repository protections.

## Inter-node contract

Exchange an envelope with these logical fields: `schema_version`, `message_id`, `source_repo`, `target_repo`, `method`, `capability`, `created_at`, `correlation_id`, `payload_digest`, `signature`. Payloads must be minimal, validated and free of secrets. Unknown schema versions are rejected or quarantined, never guessed.

Suggested event names: `capability.published`, `analysis.completed`, `dependency.proposed`, `change.proposed`, `validation.completed`, `release.promoted`, `rollback.requested`.

## Safety and governance

- Least privilege; no cross-repository write tokens in runtime workers.
- No automatic merge, deployment, destructive migration or secret transfer.
- All generated changes go through pull requests, required checks and human review.
- Pin and verify dependencies; record SBOM/provenance where supported.
- Use timeouts, idempotency keys, bounded retries, dead-letter handling and audit logs.
- NEXUS outage must not stop local builds or releases.
- Roll back by reverting the specific change or disabling the integration adapter.
- Treat external repository content and events as untrusted input.

## Rollout gates

**P0 — Contract only:** document capabilities and schemas.  
**P1 — Read-only discovery:** inventory repositories and dependency edges.  
**P2 — Event exchange:** signed, schema-validated messages; no remote writes.  
**P3 — Coordinated proposals:** create isolated branches/PRs with checks.  
**P4 — Controlled adoption:** enable per-repository adapters after owner approval.

A phase advances only when tests, security review, observability and rollback are demonstrated. This document alone does not claim that network transport, agents or automation are already running.

## Node-specific implementation

This copy is owned by **SAMBU**. The repository must implement the eight methods using its own native architecture. Domain-specific adapters and capabilities are to be registered after code and tests are inspected; no unsupported assumptions about this repository's internals are made.
