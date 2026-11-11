# Anti-Teradayn Protocol — SAMBU

**Status:** repository-level engineering standard. Implementation claims require source, test, and target evidence.  
**Scope:** this repository only; no destructive rewrite, unrelated language migration, or implicit cross-repository code execution is authorized.

## Purpose

Turn Anti-Teradayn into concrete controls: bounded responsibilities, explicit interfaces, predictable resource use, minimal necessary dependencies, and reproducible verification. “Typed streaming” means typed, bounded, reviewable changes—not a new runtime or a claim of zero entropy.

## Seven-phase protocol

1. **Dependency discipline.** Inventory direct and transitive dependencies. Remove one only when a supported replacement exists and tests prove it. Keep web, GUI, scripting, and network features that are part of the product contract; isolate them from the core instead of deleting them.
2. **Corpuscular transparency.** Prefer explicit data flow, narrow functions, fixed-width types where ABI matters, clear ownership, and measured hot paths. Use C/assembly only for demonstrated low-level needs. Swift is optional, never a universal bridge/compiler layer without a supported target and maintenance case.
3. **Driver and hardware boundaries.** Keep privileged operations and hardware access in platform-specific native adapters with explicit contracts, error paths, and capability checks. Ruby may support developer tooling where justified; it is not a kernel-driver ABI or substitute for native driver code.
4. **Applicable validation matrix.** Run unit, integration, static, build, and stress tests matching the actual product. GUI, Lua, rendering, interrupt, and hardware tests are conditional, not test theater. Label host, emulator, and physical-target evidence separately.
5. **Hardened integration boundary.** Use least privilege, authenticated transport where transport exists, bounded timeouts, input validation, and explicit cache/retention rules. Google services and external APIs are optional integrations, never mandatory architecture.
6. **SAMBU relationship.** Use SAMBU for scientific/statistical modeling only when a real modeling requirement exists. Integrate through versioned data contracts and reproducible fixtures; do not embed or claim Boltzmann functionality where irrelevant.
7. **Resource allocation.** Keep compute in the repository's native core and orchestration/UI in its existing supported layer. C/C++ and C# are choices, not mandatory tracks; “six-molecule allocation” is not a technical rule. Express memory, CPU, concurrency, and latency budgets in measurable units.

## Six coding styles, translated into enforceable practice

These names are review metaphors, not new languages, execution modes, or guarantees. Apply only the parts that fit a repository's real workload.

1. **Штора — Curtain / encapsulation.** Hide implementation state behind narrow module and API boundaries. Expose validated inputs and explicit results; keep state transitions local and observable. A boundary must improve isolation without hiding errors or creating needless layers.
2. **Волна — Wave / stable iterative computation.** Make iteration order, units, seed, tolerances, and convergence criteria explicit. Prefer stable recurrences and compensated or accurate summation where appropriate. A simulated phase or waveform must never control host scheduling or be presented as proof of zero jitter.
3. **Бегунок — Slider / sequential traversal.** Use a bounded cursor over immutable or read-only buffers for workloads that are naturally sequential. Check start/end offsets, chunk boundaries, and progress invariants. Claim cache-locality gains only after a repeatable benchmark against the existing implementation.
4. **Сепсис — fail-closed quarantine.** Reject malformed or out-of-contract inputs before committing state. Isolate failed work items, preserve bounded diagnostic evidence, and use explicit retry/restart budgets. Never self-modify, delete code, or silently remove a subsystem in response to a runtime error.
5. **Ржавый — disciplined native memory.** In C11/C++, define allocation, ownership, lifetime, initialization, alignment, bounds, and cleanup at each ABI boundary. Prefer RAII in C++ and explicit cleanup paths in C. Raw pointer arithmetic or manual optimization requires a measured need plus sanitizer and boundary tests; it is not a performance shortcut by definition.
6. **Ржавчина — ownership and borrowing discipline.** Default to immutable data, one clear mutable owner, short-lived borrows, and explicit synchronization. Use Rust's compiler-enforced ownership when Rust is actually part of a target. Python can document and check runtime boundaries, but it cannot claim compile-time borrow checking.

## Typed-streaming rules

- **Never boil:** no broad refactor without a scoped behavior change and regression coverage.
- **Never over-boil:** keep modules bounded; prefer composition and explicit ownership over deep inheritance.
- **Never cook:** avoid hidden global state, unbounded queues, implicit network calls, and unnecessary runtime work.
- Preserve public APIs and data formats unless a versioned migration is supplied.
- Make no performance claim without a reproducible benchmark and baseline.
- Do not infer production, driver, OS, or hardware readiness from a mockup, specification, or host test alone.

## Repository-specific application

**Verified profile:** Python-hosted language and scientific modeling environment with dimensional analysis, spatial data, CLI/Tkinter tooling, tests, and a bounded C11 typed-IR compiler slice. Keep Python as the current host; do not claim a complete native compiler.

- **Волна:** statistical helpers use explicit physical units, deterministic inputs, bounded arrays, reference-energy shifting, and `math.fsum` for probability and moment reductions. Extend tests around normalization, representable energy-offset invariance, extreme-but-finite inputs, and deterministic seeded sampling.
- **Штора:** keep parser, semantic analysis, runtime, domain models, and native IR behind explicit contracts; do not leak mutable runtime internals into public APIs.
- **Бегунок:** use sequential bounded traversal in voxel/chunk or data-processing paths only where the data shape supports it; retain bounds checks and benchmark before optimizing.
- **Сепсис:** reject invalid dimensions, non-finite values, invalid distributions, malformed AST/IR, and oversized payloads before state is committed. Preserve bounded failure records; do not add self-modifying quarantine logic.
- **Ржавый:** constrain low-level work to the existing C11 IR slice and explicit ABI boundaries. Require allocation/cleanup, bounds, sanitizer, and target-build evidence before introducing pointer-heavy code.
- **Ржавчина:** use immutable snapshots, explicit actor state transitions, bounded mailboxes, and locks where Python threads cross shared mutable state. These are runtime protections, not compiler-enforced ownership or hard-real-time guarantees.

The current scientific module is not an audio sampler or hardware DSP backend. It does not establish 54% swing timing, zero-latency buffers, interrupt safety, or hardware register polling. Those claims require a real target implementation, loopback/latency measurements, stress tests, and device-specific evidence. Checks for the current Python host: `python -m pytest`; `python one.py check`. Native C11 checks must run through their own build and CTest workflow.

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
