# Anti-Teradayn Protocol — SAMBU

**Status:** repository-level engineering standard. Implementation claims require source, test, and target evidence.  
**Scope:** this repository only; no destructive rewrite, unrelated language migration, or implicit cross-repository code execution is authorized.

## Purpose

Turn Anti-Teradayn into concrete controls: bounded responsibilities, explicit interfaces, predictable resource use, minimal necessary dependencies, and reproducible verification. “Typified steaming” means typed, bounded, reviewable changes—not a new runtime or a claim of zero entropy.

## Seven-phase protocol

1. **Dependency discipline.** Inventory direct and transitive dependencies. Remove one only when a supported replacement exists and tests prove it. Keep web, GUI, scripting, and network features that are part of the product contract; isolate them from the core instead of deleting them.
2. **Corpuscular transparency.** Prefer explicit data flow, narrow functions, fixed-width types where ABI matters, clear ownership, and measured hot paths. Use C/assembly only for demonstrated low-level needs. Swift is optional, never a universal bridge/compiler layer without a supported target and maintenance case.
3. **Driver and hardware boundaries.** Keep privileged operations and hardware access in platform-specific native adapters with explicit contracts, error paths, and capability checks. Ruby may support developer tooling where justified; it is not a kernel-driver ABI or substitute for native driver code.
4. **Applicable validation matrix.** Run unit, integration, static, build, and stress tests matching the actual product. GUI, Lua, rendering, interrupt, and hardware tests are conditional, not test theater. Label host, emulator, and physical-target evidence separately.
5. **Hardened integration boundary.** Use least privilege, authenticated transport where transport exists, bounded timeouts, input validation, and explicit cache/retention rules. Google services and external APIs are optional integrations, never mandatory architecture.
6. **SAMBU relationship.** Use SAMBU for scientific/statistical modeling only when a real modeling requirement exists. Integrate through versioned data contracts and reproducible fixtures; do not embed or claim Boltzmann functionality where irrelevant.
7. **Resource allocation.** Keep compute in the repository's native core and orchestration/UI in its existing supported layer. C/C++ and C# are choices, not mandatory tracks; “six-molecule allocation” is not a technical rule. Express memory, CPU, concurrency, and latency budgets in measurable units.

## Typed-steaming rules

- **Never boil:** no broad refactor without a scoped behavior change and regression coverage.
- **Never over-boil:** keep modules bounded; prefer composition and explicit ownership over deep inheritance.
- **Never cook:** avoid hidden global state, unbounded queues, implicit network calls, and unnecessary runtime work.
- Preserve public APIs and data formats unless a versioned migration is supplied.
- Make no performance claim without a reproducible benchmark and baseline.
- Do not infer production, driver, OS, or hardware readiness from a mockup, specification, or host test alone.

## Repository-specific application

**Verified profile:** Python-hosted language and scientific modeling environment with dimensional analysis, spatial data, CLI/Tkinter tooling, tests, and a bounded C11 typed-IR compiler slice. Keep Python as the current host; do not claim a complete native compiler. Priorities: deterministic sampling, dimensional invariants, parser/AST property tests, reproducible model fixtures, and measured profiling of voxel/graph workloads. Native C11 stays behind typed IR. Checks: `python -m pytest`; `python one.py check`.

## Change acceptance checklist

- [ ] Change has a clear purpose and stays within this repository's responsibility.
- [ ] Dependency and security impact are recorded; no blanket technology purge.
- [ ] Interfaces, ownership, failure modes, and resource limits are explicit.
- [ ] Relevant tests/checks pass; unsupported target checks are marked pending.
- [ ] Documentation and examples match implemented behavior.
- [ ] Cross-repository integration uses a versioned contract and never executes foreign code implicitly.

## Ecosystem boundary

Repositories remain independently buildable and retain their own APIs, release cycles, and evidence. Federation means documented, versioned contracts—not a forced monolith or shared runtime. See the [Hellduck Integration Playbook](https://github.com/bboroski/Hellduck/blob/main/docs/INTEGRATION_PLAYBOOK.md) where applicable.

---

*Engineering maxim: make every claim testable, every boundary explicit, and every optimization measurable.*
