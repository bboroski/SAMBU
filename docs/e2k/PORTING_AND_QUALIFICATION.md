# Elbrus E2K portability and qualification profile

**Repository:** `bboroski/SAMBU`  
**Status:** engineering plan; implementation and target qualification are not implied.  
**Scope:** apply the open native-optimization manifesto without weakening this project's product purpose or existing platform boundaries.

## Project-specific adaptation

Python-hosted scientific/modeling environment with lexer/parser, semantic analysis, Tkinter IDE and an experimental C11 typed-IR native slice.

Keep Python as the development/control plane. Move only profiled numeric kernels and stable runtime primitives into a separately testable C11/e2k backend; define typed IR lowering, ABI boundary, differential tests and Python fallback. Do not label the whole application a native monolith.

## Shared engineering rules

1. **Preserve platform truth.** Distinguish host build, cross-compile, emulator execution and physical E2K execution. A passing x86/ARM host test is not E2K evidence.
2. **Discover the real toolchain.** Record exact LCC/compiler version, target triple, ABI, sysroot, linker, libc, OS/kernel, CPU model/stepping and supported flags. Probe flags before enabling them. Do not assume GCC options such as `-O4`, `-march=native`, `-mtune=native`, `-fwhole-program`, `-flto` or `-Qoption,lcc,-clist` are accepted or have the claimed semantics.
3. **Optimize by measurement.** Establish a correctness-preserving baseline; profile representative workloads; inspect generated E2K assembly/VLIW bundles; measure PMU counters where documented and available; compare medians and variance. No IPC, cache-miss or latency improvement is claimed until measured on the named target.
4. **Make memory contracts explicit.** Use fixed-capacity arenas/rings only where lifetime and capacity are known. Apply `restrict` only when non-aliasing is a true API guarantee. Use alignment from the actual ABI/cache-line specification, not a universal 128-byte assumption. Keep bounds checks and overflow handling.
5. **Treat monolithic/static linking as an option, not dogma.** Produce a static artifact only when the target libc, loader, licensing, plugin model and operational requirements permit it. Preserve shared-library/process boundaries when they provide security, fault containment, independent updates or required OS integration.
6. **Avoid speculative ISA assumptions.** Predication, software pipelining, APB/prefetch facilities, vector widths, register windows, global-register use and protected-pointer modes must be confirmed against the exact processor manual and LCC documentation before code generation relies on them. Never hard-code register names or claim a fixed VLIW issue width without target evidence.
7. **Keep safe fallbacks.** Every optimized kernel must have a portable reference path, equivalence tests, boundary tests and a feature/capability gate. Fast-math, loop unrolling and branchless rewrites require numerical and semantic validation.
8. **Real-time claims require bounds.** Document worst-case execution time methodology, interrupt and scheduler assumptions, memory residency, affinity and contention. Average latency alone is not a hard-real-time guarantee.
9. **Security claims require threat models.** Protected execution, memory tags and hardware pointer bounds are platform capabilities, not universal E2K properties. Retain ordinary bounds checks, fuzzing, sanitizers where available, least privilege and explicit trust boundaries.
10. **Reproducibility is part of the feature.** Store build manifest, compiler/linker identity, source revision, flags, artifact hash, test vectors and benchmark environment with each qualification result.

## Required implementation sequence

| Gate | Deliverable | Pass condition |
|---|---|---|
| G0 — Inventory | Component map, language/runtime inventory, dependencies and platform boundaries | Every application/module has an owner, build path and applicability decision |
| G1 — Baseline | Existing tests, host build, benchmark inputs and artifact metadata | Reproducible baseline; no regression hidden by target-specific code |
| G2 — E2K toolchain | Toolchain manifest, compile/link probes and minimal ABI smoke test | Exact compiler and sysroot successfully build and link a minimal target binary |
| G3 — Native slice | Smallest portable hot-path component with reference implementation | Differential tests pass on host and E2K; no unsupported ISA assumptions |
| G4 — Optimization | Profile-guided, layout, vectorization and scheduling experiments | Assembly inspection and target measurements demonstrate a repeatable gain |
| G5 — Integration | Optional native backend, adapter contract and fallback | Existing application behavior and interfaces remain compatible |
| G6 — Qualification | Hardware/emulator evidence bundle and release decision | Evidence identifies hardware, software, tests, hashes and known limitations |

## Benchmark and evidence record

Each benchmark result must record: CPU model/stepping; board; OS/kernel; LCC version; linker/libc; build flags; source commit; artifact SHA-256; workload and input hash; warm-up/repetition policy; elapsed-time distribution; correctness result; and whether execution occurred on host, emulator or physical E2K hardware. Report baseline and candidate under the same conditions. Do not publish synthetic target numbers as measured results.

## CI checks to add when implementation exists

- Validate the E2K target manifest and reject unknown compiler/ABI combinations.
- Build the portable reference path on the normal host runner.
- Run static analysis, unit tests, fuzz/boundary tests and artifact reproducibility checks where supported.
- Run E2K cross-build only on a runner with the declared toolchain/sysroot.
- Run native execution tests only on an explicitly labelled E2K runner; otherwise mark them **not run**, never pass.
- Archive disassembly, linker map, test logs and benchmark metadata as build artifacts.

## Non-goals and prohibited claims

This profile does not assert that all repository code can or should be merged into one executable; that all dynamic libraries, interpreters, operating-system services or IPC should be removed; that all source can be translated to E2K; or that any performance/security metric has already improved. It does not claim MCST endorsement, physical hardware validation, protected-mode availability or production readiness.

## Definition of done

A change is complete only when its scope is linked to source files, builds reproducibly with the declared toolchain, passes tests, preserves the portable fallback, includes generated-code inspection where relevant, and has target evidence appropriate to its maturity. Documentation-only work remains **planned/specification**, not **implemented**.
