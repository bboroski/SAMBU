# GRAND-SLAM Protocol — SAMBU

**Status:** adoption baseline proposed for review  
**Scope:** SAMBU — Python-hosted scientific modeling, language tooling, reproducible workflows and the experimental C11 compiler slice.

## Purpose

GRAND-SLAM turns four metaphors into measurable engineering controls. The protocol is a repository-local acceptance contract, not a claim that every optimization is already implemented. Record evidence, distinguish **implemented / partial / planned / not applicable**, and never infer a capability from a design mock-up or a document.

## 1. Physical vector — resource and execution efficiency

- Establish a reproducible baseline before optimizing: build configuration, target, workload, warm-up, sample count and toolchain.
- Track the resources relevant to this project: CPU time/utilization, peak and steady-state RAM, allocation count, I/O volume and latency, startup time, and energy/current only where suitable measurement hardware exists.
- Profile first; optimize measured hot paths. Preserve correctness and compare before/after results. Record p50/p95 (and p99 where sample volume supports it), variance and regression thresholds.
- Improve locality and reduce copies/allocations only where profiling confirms benefit. Bound queues, buffers, retries and work per cycle where deterministic behavior matters.
- Use asynchronous I/O only for genuinely wait-bound/concurrent workloads. Do not introduce threads, schedulers, containers or complexity into deterministic/bare-metal components without a demonstrated requirement.
- Hardware, thermal and energy claims require target-specific measurements; host CI is not hardware qualification.

## 2. Biological vector — human factors and safe interaction

- Where a human-facing interface exists, verify keyboard operation, visible focus, readable labels, contrast, scalable text, responsive layouts, error recovery and screen-reader semantics. Target WCAG 2.2 AA where applicable.
- Make frequent actions easy to reach; use sufficiently large touch targets and spacing, and test with keyboard, mouse and touch where supported.
- Respect operating-system preferences such as reduced motion and color scheme. Keep user-controlled settings available and reversible.
- Keep interaction patterns consistent. Provide clear progress, success, warning and failure states; avoid animation that hides status or blocks work.
- Personalization and prediction must be opt-in, explainable and reversible. Do not infer stress, health, attention or circadian state from click speed, pauses or other behavioral telemetry. Collect the minimum data, locally where feasible, with explicit consent and deletion controls.
- If this repository has no GUI, mark visual ergonomics **not applicable** and apply the principle to CLI messages, diagnostics, documentation and operator workflows instead.

## 3. Technical vector — architecture, verification and maintenance

- Keep modules cohesive with explicit ownership, stable interfaces and versioned contracts. Prefer a modular monolith or library boundary when that is simpler than microservices.
- Define invariants, input validation, error semantics, resource ownership and compatibility rules at each public boundary.
- Test behavior at the appropriate levels: unit tests for local logic, integration tests for contracts, end-to-end tests for real user workflows, and hardware/emulator tests only where the target exists.
- Set coverage goals from risk and critical-path evidence. Do not impose a universal 90% threshold; coverage is not proof of correctness. Add mutation/property/fuzz tests to parsers, validators and safety-critical boundaries where useful.
- Keep CI reproducible. Pin or constrain dependencies, scan secrets and dependencies, produce an SBOM where release practices support it, and preserve test artifacts/logs without leaking sensitive data.
- Refactor in small reviewable changes. Remove dead code only after reference and compatibility checks; track technical debt with an owner and rationale.
- Scale only where the deployment model needs it. Containers, orchestration and horizontal scaling are not default requirements for libraries, desktop tools, firmware or kernels.

## 4. SAMBO vector — resilience and controlled change

- Treat invalid, missing, stale and adversarial input as normal operating conditions. Validate at boundaries, provide actionable correction guidance and never silently change meaning.
- Define failure states and graceful degradation. Use bounded timeouts, retry budgets, backoff and idempotency for external calls; avoid retry storms and unbounded queues.
- Preserve safe defaults and least privilege. Read-only tools must remain read-only; validators must not execute the artifacts they inspect.
- Define recovery behavior: cleanup, restart/rollback boundary, state integrity, operator guidance and evidence to diagnose failure.
- Use staged/canary rollout and automated rollback only when the repository has a real deployment channel and reliable health signals. Otherwise document the release/rollback procedure appropriate to its distribution model.
- Exercise fault paths: malformed input, truncation, timeout, resource exhaustion, partial initialization, corrupted metadata and interrupted operations.

## Repository-specific application

SAMBU — Python-hosted scientific modeling, language tooling, reproducible workflows and the experimental C11 compiler slice.

**Required evidence for this repository**
- Re-run `python -m pytest`; compare representative interpreter, parser, scientific-model and workflow workloads. Track allocations and wall time; preserve deterministic seeds and SI dimensional correctness. Treat the native compiler slice as experimental until end-to-end code-generation evidence exists.

## Release gate and scorecard

A change is acceptable only when its applicable checks pass and evidence is attached to the PR:

| Gate | Evidence |
|---|---|
| Correctness | Tests for changed behavior and regression cases |
| Resource use | Reproducible before/after benchmark, or explicit **not measured** |
| Human factors | Accessibility/CLI/operator review, or **not applicable** with reason |
| Architecture | Interface, ownership and compatibility impact documented |
| Resilience | At least one relevant failure-path test and recovery behavior |
| Security | Input-boundary review; secret/dependency checks where configured |
| Release safety | Distribution-appropriate rollback/recovery instructions |

Do not merge solely because a percentage target is met. Block release on failing required tests, data loss, privilege expansion, unbounded resource behavior or undocumented incompatible API changes.

## Measurement record template

For each material optimization, record: commit, target, toolchain, workload, environment, baseline, result, sample count, variance, correctness checks, limitations and reviewer. Use **not measured** rather than invented values.

## Adoption sequence

1. Inventory existing tests, workflows, public contracts and constraints.
2. Establish baseline measurements and identify the highest-impact bottleneck.
3. Select one low-risk improvement per applicable vector.
4. Add regression/failure tests and update this evidence record.
5. Review compatibility, privacy, security and rollback.
6. Merge only after repository-required checks pass; repeat from measured evidence.

**Non-goals:** mandatory microservices, blanket 90% coverage, speculative quantum/neuromorphic claims, silent behavioral surveillance, fake performance numbers, or automatic deployment to physical devices.
