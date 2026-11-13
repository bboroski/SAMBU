# JM-NATIVE-66 — Native Execution & Controlled Memory Doctrine

**Revision:** 2026-11-13  
**Scope:** this repository only; applied as an engineering policy and implementation backlog, not a claim that all requirements are already implemented.  
**Status:** proposal pending code-level implementation, CI evidence and review.

## Mission

Prefer native machine-code execution, explicit resource ownership, predictable hot paths, compact data layouts, measurable performance and reproducible release artifacts. Optimize from measurements, preserve correctness and security, and keep every platform claim evidence-backed.

## Resolution of conflicting requirements

The 66 rules are engineering goals, not permission to break portability or correctness. Apply them conditionally:

- A statically linked application is still dependent on its operating system and CPU ABI. “OS-independent executable” is not a realistic property of a normal native desktop binary.
- Direct system calls are platform-specific and brittle. Use narrow, documented OS adapters; bypass wrappers only when profiling proves a benefit and compatibility is maintained.
- Static linking does not mean one source file or one inseparable binary. Keep source modules and tests separable; combine compatible release objects at link time.
- A universal monolith cannot cover multiple CPU architectures, firmware targets or OSes. Produce one optimized artifact per target triple/profile.
- Do not remove interpreters, VMs, garbage collectors, exceptions, dynamic libraries or dependencies until the product's actual language/runtime needs and compatibility tests permit it.
- “No third-party dependencies” is not an absolute: retain audited platform SDKs, compiler runtimes, cryptography and legally required components when necessary.
- SIMD, CPU-specific tuning, core pinning and lock-free algorithms are opt-in, architecture-gated optimizations. Keep a portable baseline and test concurrency correctness.
- Determinism means bounded and specified behavior where required; general-purpose desktop scheduling and OS I/O cannot promise hard real-time latency.
- No unsafe kernel/driver shortcuts, undocumented kernel structure manipulation, or claims of hardware qualification without real target evidence.

## 66-point implementation checklist

1. Compile eligible production components to native machine code; document interpreted/tooling exceptions.
2. Prefer static linkage for deployable artifacts when compatible with platform licensing and ABI.
3. Statically compose release modules where practical while preserving source-level modularity.
4. Exclude development interpreters/VMs from production only after feature and compatibility parity.
5. Define memory budgets and ownership for every long-lived/static region.
6. Avoid tracing GC in deterministic/native core paths where explicit ownership is viable.
7. Prefer cache-conscious layouts for measured hot data.
8. Add SIMD kernels behind feature detection and scalar fallbacks.
9. Reduce indirect calls in profiled hot paths without sacrificing clear interfaces.
10. Specify bounded execution for real-time or latency-sensitive operations.
11. Prefer small native components over heavyweight frameworks on critical paths.
12. Keep OS calls behind narrow, documented platform adapters; use direct calls only with evidence.
13. Embed essential assets in release artifacts when this improves deployment and maintainability.
14. Use strict compile-time types and warnings-as-errors for supported toolchains.
15. Keep abstraction overhead out of measured critical paths.
16. Use release optimization profiles per supported target CPU; retain a portable baseline.
17. Use task-specific allocators only with explicit bounds, ownership and tests.
18. Prefer lock-free synchronization only when its memory-ordering proof and stress tests exist.
19. Organize hot loops/data for locality and predictable prefetching.
20. Prefer flat arrays/SoA/AoS layouts based on measured access patterns.
21. Disable unused exception/runtime machinery only where the language and ABI allow it safely.
22. Prefer explicit error codes/results in low-level APIs; preserve actionable diagnostics at boundaries.
23. Pin threads only for justified real-time workloads and supported operating systems.
24. Use atomics with documented memory ordering; retain locks where they are safer or faster.
25. Use asynchronous I/O/event loops where the platform and workload benefit.
26. Use bounded pools for frequent, predictable object lifetimes.
27. Use ring buffers for streaming paths with defined overflow/backpressure behavior.
28. Avoid reflection/dynamic type discovery in hot or security-critical paths.
29. Minimize dependencies; record and audit unavoidable platform/toolchain dependencies.
30. Profile on target hardware and record reproducible baselines.
31. Use compact serialization only with versioning, bounds checks and compatibility tests.
32. Keep frequently accessed state in contiguous bounded storage where practical.
33. Use bitsets/bitwise operations for compact flags when they improve clarity and performance.
34. Measure branch behavior; simplify unpredictable branches in hot paths.
35. Precompute constants/tables only when memory and correctness trade-offs are favorable.
36. Assert and test alignment, size, overflow and ABI layout at boundaries.
37. Produce self-contained deployment artifacts where platform rules permit.
38. Keep low-level/driver code in supported system languages and documented APIs.
39. Run compile-time checks, static analysis and unit tests in the build pipeline.
40. Track binary size, sections and dependency inventory in release CI.
41. Statically link eligible third-party modules; preserve license notices and required shared components.
42. Enable dead-code elimination/LTO where supported and validated.
43. Prefer bounded byte slices/views over unnecessary string allocations in hot paths.
44. Tune data structures against measured cache behavior; do not assume cache sizes.
45. Use bounded asynchronous logging with loss/overflow policy and nonblocking hot paths.
46. Keep dynamic values out of critical core interfaces where static types suffice.
47. Use zero-copy views/ownership transfer where lifetime and aliasing rules are explicit.
48. Analyze worst-case complexity and adversarial input bounds for critical algorithms.
49. Compile immutable configuration into constants when runtime configurability is not required.
50. Eliminate undefined behavior; use supported language subsets and sanitizers/static analysis.
51. Document OS, ABI, CPU and firmware dependencies; do not claim OS independence for hosted binaries.
52. Inline only measured hot functions; verify code-size and instruction-cache effects.
53. Strip private debug symbols from release artifacts while retaining separate symbol files for diagnostics.
54. Use monotonic/high-resolution platform timers and document their precision/overhead.
55. Make object/resource lifetime transitions explicit and test failure paths.
56. Define fault containment, recovery and single-point-of-failure analysis appropriate to the product.
57. Enable available memory protections, sanitizers, MPU/MMU and hardware integrity features where supported.
58. Use native worker pools only when parallelism improves measured throughput/latency.
59. Reduce context switches through batching and event-driven work where appropriate.
60. Order fields and add explicit padding only after ABI/cache measurements.
61. Define one clear entry point per executable/image, not one global entry point for unrelated products.
62. Pair allocation/release APIs and test leaks, double frees and ownership violations.
63. Make builds reproducible with pinned toolchains, dependencies, flags and deterministic inputs.
64. Minimize protocol overhead with versioned, bounded and observable interfaces.
65. Stress-test resource, concurrency and throughput limits on representative target hardware.
66. Ship a verified release artifact per supported target, with test reports, checksums and dependency manifest.

## Repository-specific native target

**Project class:** Python-hosted language/workflow environment with an experimental C11 compiler slice  
**Recommended implementation profile:** Compile the language core and hot execution kernels incrementally to native code; retain the Python host/CLI/IDE as development tooling until a complete native frontend, runtime, diagnostics and parity suite exist. Do not remove the interpreter from production until native parity is demonstrated.

## Required evidence before calling the doctrine implemented

- Inventory current languages, build systems, dependencies, runtime boundaries and target architectures.
- Establish baseline build/test status and benchmark methodology before changing implementation.
- Implement in small reviewable increments; keep a portable fallback when target-specific code is introduced.
- CI must build every declared target, run unit/integration tests, static analysis and binary/dependency checks.
- Hardware-only claims require target-device logs or reproducible qualification records.
- Release notes must distinguish implemented, partial, planned and not-applicable items.

## Release acceptance

A release is acceptable only when the relevant target builds reproducibly, required tests pass, binary/dependency reports are attached, security checks are clean, and the artifact matches the declared platform. A documentation-only adoption PR does not constitute a native rewrite or production release.
