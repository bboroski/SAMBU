# Engineering upgrade baseline — SAMBU

## Scope
Python-hosted language runtime, lexer/parser/AST, semantic analysis, scientific arrays and C11 typed-IR slice.

## Required engineering changes
1. **Contracts and typing:** validate public inputs at module/API boundaries; version externally consumed schemas and ABI; reject malformed or unsupported versions explicitly.
2. **Runtime and memory:** profile before optimizing; document ownership, lifetime, bounds and failure behavior; use bounded reuse/pooling only where allocation measurements justify it.
3. **Interfaces and events:** isolate adapters behind stable interfaces; keep asynchronous work bounded, observable and non-blocking where the platform supports it; define overload and shutdown behavior.
4. **Performance:** establish repeatable baselines for latency, throughput and peak memory; optimize measured hot paths; add SIMD only with scalar fallback and equivalence tests.
5. **Reliability:** add boundary, malformed-input, fault-injection and stress tests; preserve deterministic behavior and explicit degraded/unknown states.
6. **Configuration and migration:** version persisted configuration; validate before applying; make migrations idempotent, transactional where possible, and rollback-capable.
7. **CI/CD:** require build, tests, static checks and migration validation before merge; auto-merge may be enabled only after repository protections and required checks are verified.

## Repository-specific constraints
Define typed contracts at AST/IR and adapter boundaries; benchmark-driven cache/buffer reuse; keep native compiler claims limited to the implemented C11 slice. SIMD only behind portable scalar fallbacks and equivalence tests.

## Verification gates
python -m pytest; python one.py check; benchmark interpreter hot paths before/after; verify dimensional and array edge cases.

## Delivery policy
Implement changes in small independently reviewable PRs. Keep `main` unchanged until checks pass and review is complete. Record benchmark environment and results; do not claim hardware/production readiness from host-only tests.

## Status
This PR establishes the repository-specific acceptance baseline. It does not claim that the runtime optimizations above have already been implemented; each implementation must land with code, tests and measured evidence.
