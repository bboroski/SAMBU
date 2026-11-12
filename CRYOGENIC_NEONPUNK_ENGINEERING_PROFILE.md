# Cryogenic Neonpunk Engineering Profile

> Repository: `SAMBU`  
> System role: Contract authority

## Purpose

This profile translates the Cryogenic Neonpunk / Egyptian Cyber Duck concept into practical engineering constraints. The visual language is cold, precise, modular, resilient, and deliberately playful; production behavior remains conventional, observable, secure, and testable.

Own stable interfaces, shared types, capability declarations, and versioned contracts. Keep consumers independent of implementation details.

## Engineering principles

1. **Cold-start clarity** — every subsystem documents its inputs, outputs, lifecycle, failure modes, and ownership.
2. **Small, bounded units** — prefer cohesive modules, explicit contracts, bounded queues and allocations, and predictable resource limits.
3. **Deterministic core** — isolate nondeterminism, make state transitions explicit, and test repeatability where applicable.
4. **Safe automation** — automation is opt-in or policy-controlled, idempotent where possible, auditable, and reversible. Never silently delete, overwrite, or mutate user data.
5. **Layered resilience** — validate at boundaries; use timeouts, cancellation, back-pressure, and graceful degradation where relevant.
6. **Measured optimization** — establish a baseline, profile real workloads, and retain changes only when tests and measurements support them.
7. **Compatibility first** — preserve public APIs, data formats, migration paths, and supported platforms unless a separately reviewed breaking change is approved.
8. **Readable implementation** — consistent naming, narrow functions, meaningful errors, minimal dependencies, and comments that explain decisions rather than restate code.

## Cryogenic implementation profile

- **Neonpunk** is the presentation vocabulary for developer-facing surfaces: high-contrast accents, clear state indicators, and restrained visual effects. It does not dictate application behavior.
- **Cryogenic** means explicit resource budgets, bounded work, predictable shutdown, leak detection, and reproducible builds.
- **Cybernetic** means observable interfaces, health signals, structured logs, traceable operations, and well-defined component boundaries.
- **Egyptian Duck** is a lightweight, optional identity motif for examples, demo fixtures, and non-critical UI details. It must never enter protocol names, security decisions, core domain semantics, or required runtime paths.
- **Multiplicative / divine scale** means horizontal composability and repeatable reuse—not claims of infinite capacity, unbounded recursion, or unchecked replication.

## Required change workflow

- Make changes in focused, reviewable commits and isolated pull requests targeting `main`.
- Add or update tests for behavior changed; test edge cases, failure paths, and compatibility.
- Run the repository's real formatter, linter, type checks, tests, and build. Do not invent passing results or placeholder checks.
- Document configuration, migration, operational limits, and known limitations.
- Do not add dependencies, generated binaries, secrets, fake screenshots, or destructive cleanup without a concrete need and review.
- Merge only after required status checks pass and the diff has been reviewed. Preserve branch protection.

## Acceptance checklist

- [ ] Scope is limited to this repository's responsibility.
- [ ] Public contracts and compatibility are preserved or explicitly versioned.
- [ ] Resource limits and failure behavior are documented where relevant.
- [ ] Tests exercise real behavior; no mock-only success claims.
- [ ] Security, privacy, and data-retention implications are reviewed.
- [ ] Documentation matches the shipped implementation.
- [ ] CI is green and the PR is mergeable under repository policy.

## Non-goals

This profile does not authorize mass refactors, speculative algorithms, hidden background processes, recursive self-modification, uncontrolled code generation, automatic data deletion, or bypassing repository protections. Implementation decisions require evidence from the actual codebase.

---
*Engineering motto: precise as ice, adaptable as water, and harmlessly duck-shaped.*
