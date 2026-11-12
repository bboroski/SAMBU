# Swift 6+ Modular-Monolith Adoption Contract

**Status:** architecture baseline; implementation is incremental and must be proven by repository CI. **Language mode:** Swift 6; pin the exact toolchain.

## Objective and safety rules

Use a high-performance in-process Swift core only where this repository's target and deployment model support it. Organize code as SwiftPM targets with acyclic dependencies and typed APIs. Preserve independently deployed, hardware, privilege, network, and fault-containment boundaries.

- Enable Swift 6 language mode and complete strict-concurrency checking per target. Fix diagnostics; do not blanket-suppress them.
- Use actors or narrowly scoped synchronization for shared mutable state. Audit every `@unchecked Sendable`, unsafe pointer, C/C++ bridge, and mutable global.
- `Sendable` is a checked concurrency contract, not a module-access restriction. Keep non-Sendable values inside their owning isolation domain.
- Prefer value semantics. Use `~Copyable`, `borrowing`, and `consuming` only when supported by the pinned compiler and justified by measured lifetime/copy costs.
- Use SwiftPM targets (Domain, Application, Infrastructure, Adapters, Tests); keep dependency direction inward and avoid singleton service locators.
- Replace only unnecessary in-process HTTP/JSON calls with typed calls. Retain network/process/device boundaries where they provide security, independent lifecycle, or fault isolation.
- Preserve public APIs, ABI, schemas, file formats, and cross-language contracts. Version every incompatible change and test compatibility.
- Choose embedded versus external persistence from durability, multi-writer, and recovery requirements. Test transactions, WAL/checkpointing, crash recovery, backup, and restore.
- Shutdown: stop ingress, cancel owned task groups, drain owned transports, flush durable state, and report incomplete cleanup.
- Benchmark real workloads (toolchain, hardware, p50/p95/p99, throughput, allocations, memory) before optimization. No theoretical latency claims.
- Enable CMO/LTO only in supported release configurations after correctness and reproducibility checks.
- CI: reproducible toolchain, strict-concurrency build, tests for native/FFI boundaries, supported targets, and release artifacts.

## Adoption gates

A. Inventory languages, deployables, module graph, public interfaces, persistence, unsafe code, and target constraints.  
B. Define the smallest stable Swift core API and versioned contracts at genuine process boundaries.  
C. Migrate target-by-target to Swift 6 complete concurrency checking.  
D. Isolate C/C++ through Clang modules or a narrow C ABI when direct C++ interop is unsuitable; test ownership and error propagation.  
E. Select storage from durability and multi-writer needs; implement orderly lifecycle.  
F. Profile and benchmark before selectively enabling LTO/CMO.  
G. Merge only after required CI, ABI compatibility checks, and review pass.

## Repository-specific scope

SAMBU owns language/syntax and semantic tooling contracts. Keep its grammar, parser, compiler/runtime interfaces, and compatibility guarantees authoritative; Swift modules may implement tooling or host components but must not silently redefine SAMBU syntax or ABI.



This is an adoption contract, not a claim that Swift code or a SwiftPM package already exists. Keep the repository's native language/toolchain authoritative where it owns a domain-specific compiler, runtime, or hardware interface. Swift integrations must be additive, versioned, and validated against existing consumers.

## Acceptance criteria

- Pinned toolchain and reproducible SwiftPM build for each Swift target.
- Complete strict-concurrency checks with no unexplained suppressions.
- Tests for isolation, cancellation, persistence recovery, and native-boundary ownership where applicable.
- Documented module/deployment graph and versioned external contracts.
- Benchmarks and CI evidence attached to implementation PRs.
