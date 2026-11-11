# NUN Mesh — Engineering Baseline

**Status:** proposed repository policy, subject to review and project-specific CI evidence.  
**Scope:** Scientific Modeling & Automation Environment; Python-hosted language/runtime, lexer/parser, AST, reproducible scientific workflows. Keep the Python host unless benchmarks justify a native component. Validate numeric domains, units, deterministic execution, parser boundaries and model reproducibility.

## 1. Purpose and non-goals
Apply the NUN Mesh engineering principles without forcing a single language, framework or runtime onto unrelated projects. This file is a reviewable baseline, not proof that every control is already implemented. Requirements become enforced only when backed by a test, analyzer, CI job or documented manual qualification.

## 2. Eight engineering principles
1. **Fundamentality:** one clear responsibility per module; keep critical paths small and explicit.
2. **Sanity:** readable control flow, meaningful names, actionable errors and bounded function complexity. Prefer measured thresholds over arbitrary universal limits.
3. **Curtain / encapsulation:** expose typed public interfaces; keep mutable state private; validate all boundary inputs.
4. **Wave / data flow:** prefer explicit, local data flow and deterministic transformations; avoid hidden global mutable state.
5. **Slider / observability:** support configurable diagnostic depth without changing program semantics; redact secrets and bound log volume.
6. **Sepsis / defensive validation:** reject malformed, unsupported or ambiguous inputs; fail closed for safety-sensitive operations; do not silently repair unknown state.
7. **Rusty / ownership discipline:** every resource has a documented owner and lifetime; use RAII/borrow-like patterns where available; in C/C++, document ownership, check allocation results and test cleanup paths.
8. **Rust / maintenance:** deprecate APIs with migration notes; remove dead code only after reference and build checks; use supported dependency versions and reproducible update procedures. A 30-day age alone is not grounds for automatic replacement.

## 3. Anti-Teradayn delivery pipeline
1. **Dependency audit:** inventory runtime, build and web dependencies. Remove a dependency only when equivalent behavior and compatibility are verified; no blanket ban on JavaScript, Electron, Ruby, cloud APIs or frameworks.
2. **Typed boundaries:** define input/output schemas, ABI contracts, units, error domains and versioning at module boundaries.
3. **Platform isolation:** keep hardware, OS and architecture-specific operations behind narrow adapters; gate unsupported capabilities explicitly.
4. **Verification carousel:** run format/lint, static analysis, unit tests, integration tests and available host/target qualification. Never represent a host test as hardware validation.
5. **Trust and provenance:** pin or verify dependencies and artifacts where feasible; validate signatures and hashes when the product threat model requires them; do not claim zero-trust security without an implemented threat model.
6. **Performance evidence:** benchmark identified hot paths before optimization; record baseline, workload and environment; monitor CPU/memory/latency only where instrumentation exists.
7. **Integration:** use one isolated PR per repository, review the diff, wait for required checks, and merge sequentially without force-push or branch-protection bypass.

## 4. Memory and data-structure safety
All dynamic resources must have explicit ownership, allocation/deallocation pairs, size bounds and failure handling. Prefer registries, arenas or typed containers where appropriate. Detect leaks and invalid access through sanitizers, static analysis, allocator instrumentation and tests. Never scan arbitrary process/kernel memory and forcibly free unknown blocks: that can corrupt the process, kernel or unrelated owners. Unknown allocations are findings to investigate, not objects to destroy.

## 5. CI quality gates
- Build and test using the repository's documented toolchain.
- Run format/lint and language-appropriate static analysis where configured.
- Add boundary, malformed-input, failure-path and cleanup tests for changed behavior.
- Keep warnings visible; introduce stricter warning policies incrementally without hiding existing failures.
- Require all configured PR checks and review before merge. If no CI exists, document the missing gate; do not invent a passing status.
- Preserve reproducible build instructions and record target hardware/toolchain requirements.

## 6. Project-specific implementation
Scientific Modeling & Automation Environment; Python-hosted language/runtime, lexer/parser, AST, reproducible scientific workflows. Keep the Python host unless benchmarks justify a native component. Validate numeric domains, units, deterministic execution, parser boundaries and model reproducibility.

## 7. PR acceptance checklist
- [ ] Change is limited to this repository's responsibility and preserves existing public behavior unless explicitly versioned.
- [ ] No unverified language/runtime migration or speculative dependency removal.
- [ ] Ownership, bounds, errors and failure behavior are documented for changed resource paths.
- [ ] Tests and static checks are run; unavailable target checks are clearly marked.
- [ ] Documentation describes implemented behavior, not aspirational guarantees.
- [ ] CI checks pass and the PR is reviewed before merge.

## 8. Status and change control
This baseline does not automatically modify runtime code, delete data structures, rewrite drivers, introduce new language toolchains or merge itself. Each implementation change must be small, testable and independently reviewable. Update this document when project evidence or architecture changes.
