# SAMBU: Host-Independent Systems Evolution Architecture
**Baseline:** 0.11.0 alpha · **Status:** proposed architecture · **Scope:** language, compiler, runtime and systems ecosystem

## 1. Purpose and status

SAMBU evolves from a Python-hosted scientific interpreter into a typed, effect-aware, portable systems language. Preserve scientific quantities, OOP compatibility, Anatidae models, workflows, voxel computation, engine adapters and evidence-aware tooling while creating a staged route to native execution, ownership safety, concurrency and systems integration.

This is a target architecture, not a claim that the current release already provides every feature below. The 0.11 implementation has a lexer, recursive-descent statement parser, Pratt expression parser, legacy tuple AST, immutable typed AST with source spans, lexical scopes, immutable let bindings, field assignment, functions, loops, classes, inheritance, interfaces, traits, runtime SI quantities, percentage syntax, domain libraries, sparse voxel facilities, CLI tools and tests. It remains hosted by Python. It does not yet provide native compilation, a static type checker, borrow checking, affine ownership, a language-level async scheduler, green threads, lock-free guarantees, deterministic RAII or zero-cost native abstractions.

Status vocabulary is mandatory: **Implemented** means code and tests exist; **Experimental** means usable but not stable; **Planned** means design only; **Deferred** means dependent on a future backend, platform or validated provider. Roadmaps, names and examples do not change feature status.

## 1.0.1 Current Cripple runtime slice

The repository now includes the first bounded concurrency and safety primitives in `sambu.concurrency`:

- FIFO cooperative Python-generator scheduler with logical-tick sleep and per-run/per-fiber step budgets;
- actor mailboxes with payload bounds, defensive copies, sequential state commits and dead-letter records;
- hierarchical `one_for_one`, `one_for_all` and `rest_for_one` supervisors with rolling restart budgets;
- typed bounded software channels;
- reverse-order resource scopes, descriptive module-metadata validation and a two-verifier authorization boundary.
- immutable task manifests, explicit capability allow-lists, component-wise resource-budget capping, deterministic plan digests, a bounded SHA-256 experiment ledger and change preflight in `sambu.autonomy`; these are Python host APIs and do not execute code or modify files.

The language runtime exposes actors, supervision and typed-channel built-ins. The generator scheduler, resource scope and authorization helpers are Python host APIs. This is an experimental containment slice, not a native fiber scheduler or full parallel runtime. It does not add static race/deadlock analysis, RAII, ownership checking, HSM hardware access, device buses, native stacks or multicore execution.

The full feature contract, runnable examples, limits and C++-class capability roadmap are in [Systems Language Architecture](SYSTEMS_LANGUAGE_ARCHITECTURE.md). The six engineering domains are specified in [Engineering Capability and Reliability Charter](ENGINEERING_CAPABILITY_CHARTER.md). Current implementation is always subordinate to code and regression tests; the remainder of this document stays a future design unless marked otherwise.

## 1.1. Autonomy control specification and status audit

The companion [100-rule Autonomy Control Specification](AUTONOMY_CONSTITUTION.md) maps topology, syntax, safety, tooling and host-independence requirements to the 0.11 repository baseline. It preserves stable AUT-01–AUT-100 IDs, truthful statuses, current evidence and acceptance gates. The matrix is organized into two thematic series of 50 rules across ten blocks and is independently checked by tests/test_autonomy_constitution.py.

The 100-rule matrix complements, rather than replaces, the 101 lower-level language contracts in this document. Its purpose is to prevent architectural aspirations from being reported as shipped capabilities.

## 2. Core semantic invariants

**Law over convention.** Source has one defined meaning. Evaluation order, conversions, overflow, effects, ownership, cancellation and error propagation are specified before optimization. Unknown or ambiguous semantics are rejected.

**Static safety, explicit escape.** Prefer compile-time validation and safe abstractions. Dynamic host values, raw pointers, assembly, device registers and FFI require explicit boundaries. Guarantees apply only to the verified subset and declared target.

**Composition over hierarchy.** The future typed core favors structs, tagged unions, traits, generics and composition. Existing SAMBU classes and inheritance remain a compatibility feature; they are not silently removed. New APIs prefer traits and composition, with dynamic dispatch explicit.

**Determinism with stated scope.** Determinism covers evaluation, ordering, cleanup and reproducible builds. Randomness, clocks, concurrent completion, network partitions and hardware timing remain explicit inputs or nondeterministic effects.

**Physics as engineering analogy.** Stellar collapse, pressure, event horizons, accretion, density and radiation are metaphors for resource budgets, isolation, pipelines, compaction and failure recovery. They do not establish computational laws. Scientific models disclose assumptions, units, uncertainty and evidence.

## 3. Compiler and runtime architecture

The target pipeline is source validation; Unicode-aware lexing; parsing; name and module resolution; type and dimensional analysis; effect and ownership analysis; typed intermediate representation; optimization; target code generation; linking and packaging. The immutable typed AST and legacy tuple adapter remain stable during transition. A typed IR becomes the shared semantic authority for interpreter, bytecode engine and native backends.

The first type checker covers primitives, arrays, tuples, records, functions and SI dimensions. Use bounded local inference and declared public signatures. Next add algebraic data types, Option, Result, exhaustive matching, newtypes, traits, generic bounds and const parameters. Whole-program inference across open inheritance, effects and overloads is not a first-stage requirement.

Execution evolves from the interpreter reference to portable bytecode/VM if justified, then native backends. Target families: x86_64, ARM64 and RISC-V; WebAssembly and bare-metal profiles follow after their runtime contracts are testable. Self-hosting requires a documented bootstrap chain that rebuilds reproducibly. Python is the bootstrap host, not the intended final runtime dependency. Do not remove Python packaging until a standalone compiler, standard library, tests and distribution pipeline demonstrably replace it.

A future Sambu.toml manifest defines packages, target triples, features, profiles, capabilities and pinned dependencies. Content-addressed storage uses cryptographic digests, immutable lockfiles and verified provenance. Reproducibility means identical declared inputs and normalized environment; different targets need not produce identical binaries.

## 4. Type law, memory and effects

Bindings are immutable by default. Future var/mut modifiers authorize rebinding; mutation through a reference is a distinct effect. Preserve current let semantics. Option<T> models absence; Result<T,E> models expected failure. The ? operator propagates compatible results. Panics are reserved for violated internal invariants and contained at explicit process or task boundaries. Production APIs do not hide failure with unchecked unwrap.

Each owned resource has one owner. Moves transfer ownership; cloning is explicit. Shared borrows permit reads; exclusive borrows permit mutation. Lifetimes constrain references to owners. Drop is deterministic, scope-bound and non-failing by contract. Cycles are prevented by ownership design or handled through weak references and cycle-aware tools; static analysis cannot detect every dynamically constructed object cycle.

Effects identify IO, state, async, unsafe, nondeterminism and host capabilities. Pure functions cannot access external state. Fallible operations return typed errors. Retry policies state attempt ceilings, deadlines, backoff and idempotency requirements. Error context is preserved without promising a full stack trace is free.

Stack allocation is preferred when lifetime and size are known; heap allocation is explicit where enforceable. Box, shared ownership and arena APIs have distinct semantics. Allocators are injectable at defined scopes. Buffer bounds, alignment, initialization and aliasing are validated. Raw pointer arithmetic remains unsafe. The guarantee is rejection of invalid operations within the safe model, not elimination of every hardware fault.

## 5. Stellar resource lifecycle

**Main sequence — stable execution.** Use predictable allocation, bounded task pools, pooled network buffers, batched asynchronous storage and instrumentation. Pool sizes are configurable, not blindly equated to physical core count. NUMA placement, CPU affinity and priority inheritance are opt-in scheduler policies with target-specific semantics.

**Red giant — controlled expansion.** Apply quotas, bounded actor mailboxes, backpressure, cache-aware data and contention profiling. AoS and SoA are chosen by measured access patterns; neither is universally superior. Lock-free structures are optional specialized implementations with documented memory ordering.

**Supernova — fault boundary.** Capture diagnostics, symbols, source maps and thread state where supported; terminate or isolate failed tasks; recover from validated snapshots and journals. Crash upload is opt-in, privacy-preserving and redacted. Automated patch generation is advisory and never silently applies changes.

**Black-hole storage — tiered data.** Use hot RAM, warm local NVMe and cold remote/object storage. Measure latency and complexity; do not promise fixed O(1) access. Indexes, compression and migration are workload-specific, integrity-checked and recoverable.

## 6. Horizontal and universal integration

Distributed systems are libraries and capability-backed services, not magical language guarantees. Provide audited Raft/Paxos implementations, append-only logs, replication, sharding, discovery, health checks, load balancing, vector clocks, CRDTs, pub/sub, event sourcing, CQRS, sagas and circuit breakers. State consistency, conflict policy, delivery, persistence and partition behavior explicitly. Exactly-once effects cannot be promised by transport alone; use idempotency keys, transactional boundaries and deduplication.

Cloud profiles support containers, Kubernetes health endpoints, serverless packaging, gRPC, HTTP/3, QUIC, TLS 1.3, external configuration and vault adapters. Secrets are never embedded in source or logs. Cold-start and connection-scale claims require target-specific benchmarks.

Kernel and embedded profiles expose C ABI, register maps, GPIO, I2C, SPI, UART, PCIe, interrupts, DMA, MMIO, device trees, watchdogs, sleep states and bare-metal startup. These are target-specific libraries and unsafe wrappers, not universal core syntax. Ring 0, hypervisor and bootloader targets need separate threat models, linker scripts, memory maps and validation. Hard real-time claims require WCET analysis and bounded interrupt/scheduling behavior.

## 7. Reliability, security and observability

Structured supervision contains worker failure. Journals, WAL, snapshots, idempotency, dead-letter queues, retry budgets, graceful draining and degraded modes compose into explicit recovery workflows. At-least-once delivery is a transport contract; exactly-once processing requires transactional deduplication within a defined boundary. Chaos and fault-injection tools test assumptions; they do not certify resilience.

Cryptographic primitives come from reviewed implementations or vetted providers; home-grown cryptography is prohibited. Constant-time operations are explicit and compiler transformations preserve their contract. Secure randomness uses OS or hardware entropy through a documented provider. Key zeroization is best-effort unless target guarantees are proven. Code signing, verified registries, SBOMs, dependency advisories, audit chains, capability security, secure boot, TPM/HSM and remote attestation are optional integrations with threat models.

Observability includes structured logs, trace/span context, correlation identifiers, metrics, histograms, CPU/memory profiles, flame graphs, lock contention, allocation samples, hardware counters and source-mapped stack traces. eBPF and sanitizers are optional platform tools. Deterministic replay records external inputs and scheduling decisions where feasible; it cannot replay uncontrolled hardware or remote services exactly.

## 8. Normative contract index (101 consolidated requirements)

### Lexing and semantics
**001.** Tokens carry stable kinds, values and end-exclusive Unicode spans.
**002.** Unicode offsets are code points; LSP converts encodings.
**003.** Newline and semicolon separation follows one documented grammar.
**004.** Grammar changes require ambiguity and regression tests.
**005.** One precedence table serves parser, formatter and docs.
**006.** Operands and function arguments evaluate left-to-right.
**007.** Names resolve lexically inside isolated modules.
**008.** Formatting never changes program meaning.
**009.** Interpolation validates types and escapes output by context.
**010.** Macros are hygienic and preserve source provenance.

### AST and semantic analysis
**011.** Immutable typed AST is canonical; tuples are adapters.
**012.** Every AST and IR node retains its source origin.
**013.** Resolved names bind to declaration identities.
**014.** Visibility modifiers have one checked definition.
**015.** Parser recovery reports every skipped source range.
**016.** Diagnostic codes and fields are stable public contracts.
**017.** Errors explain cause, location and valid remediation.
**018.** Decidable semantic errors precede program execution.
**019.** Incremental caches include all semantic dependencies.
**020.** Interpreter and compiler share one typed semantic model.

### Types and algebra
**021.** Primitive and container values have explicit compiler types.
**022.** Local inference is bounded, deterministic and explainable.
**023.** Exported functions declare parameter and result types.
**024.** Lossy numeric conversions and overflow modes are explicit.
**025.** Known SI dimensions participate in static checking.
**026.** Struct and tuple fields have defined member types.
**027.** Sum variants contain typed payloads.
**028.** Closed sum matches cover every possible variant.
**029.** Typed absence uses Option<T>, not implicit null.
**030.** Result<T,E> and ? preserve typed error paths.

### Generics and contracts
**031.** Generics infer only within declared bounds.
**032.** Generic operations require explicit trait contracts.
**033.** Associated types have deterministic projection rules.
**034.** Conflicting trait implementations are rejected.
**035.** Generic variance is checked, otherwise invariant.
**036.** Newtypes remain distinct at compile time.
**037.** Const evaluation is terminating and resource-bounded.
**038.** Phantom parameters have no runtime storage.
**039.** Unsized values carry explicit metadata.
**040.** Recursive values require finite indirection.

### Ownership, memory and effects
**041.** Integer overflow is checked unless explicitly wrapped.
**042.** Bindings are immutable unless var or mut is explicit.
**043.** Mutation through aliases follows one sound rule.
**044.** Use-after-move is a compile-time error.
**045.** Incompatible shared and exclusive borrows are rejected.
**046.** References cannot outlive their source resources.
**047.** Owned resources close on all scope exit paths.
**048.** Raw memory requires explicit unsafe boundaries.
**049.** Effects expose IO, state, async and unsafe actions.
**050.** Pure functions cannot mutate observable external state.

### Functional composition
**051.** Allocation is measurable, bounded and reportable.
**052.** Function values carry parameter, result and effect types.
**053.** Closures obey explicit or inferred capture constraints.
**054.** Iterator lowering preserves observable semantics.
**055.** Lazy streams define cancellation and resource closure.
**056.** Pipelines preserve evaluation order and error propagation.
**057.** Partial application preserves the source function type.
**058.** Tail-call guarantees are target-specific and tested.
**059.** Pattern guards refine types without hiding missing cases.
**060.** Record updates preserve the original value.

### Concurrency
**061.** Memoization requires purity, stable keys and cache bounds.
**062.** Child tasks cannot silently outlive their parent scope.
**063.** Cancellation propagates and runs cleanup.
**064.** Channels define capacity, close and transfer behavior.
**065.** Actors serialize access to their owned state.
**066.** Queues are bounded or marked as unbounded risk.
**067.** Backpressure propagates from consumers to producers.
**068.** Scheduler fairness and starvation policy are documented.
**069.** Atomics expose validated memory-order choices.
**070.** Ordered parallel APIs preserve result order.

### Runtime and hardware
**071.** Deadlock tools report cycles, not proofs of safety.
**072.** OS IO is hidden behind a portable runtime interface.
**073.** Zero-cost claims require measurements per backend.
**074.** Custom allocators have explicit scope and ownership.
**075.** Layout attributes are opt-in and ABI-aware.
**076.** AoS or SoA follows measured access patterns.
**077.** SIMD defines lane, mask and fallback semantics.
**078.** Compile-time evaluation is deterministic and bounded.
**079.** FFI defines ABI, ownership, errors and unwinding.
**080.** Device access uses target-specific unsafe wrappers.

### Ecosystem and supply chain
**081.** Hardware counters expose resolution and overhead.
**082.** Module dependencies are imported explicitly.
**083.** Lockfiles pin resolved dependency versions.
**084.** Build inputs have content identities and provenance.
**085.** Reproducible builds normalize or declare environment inputs.
**086.** Formatter output is syntax-aware and idempotent.
**087.** Linter findings explain correctness, safety or cost.
**088.** Unit, integration, property and fuzz tests are reportable.
**089.** Executable documentation examples run in CI.
**090.** LSP edits honor negotiated source-position encodings.

### Security and evolution
**091.** Build-cache keys include toolchain and dependency hashes.
**092.** Source size and runtime structures have safety ceilings.
**093.** Untrusted programs receive no ambient host capabilities.
**094.** Host access is explicit, granted and auditable.
**095.** Errors serialize predictably across tools and runtimes.
**096.** Backends agree through differential semantic tests.
**097.** Performance regressions use repeatable benchmark baselines.
**098.** Breaking changes require major versioning or migration.
**099.** Deprecation includes warnings and a migration window.
**100.** Releases label stable, experimental and planned features.
**101.** Compatibility gate: every shipped feature includes specification, implementation, tests, documentation and measured limits.

## 9. Implementation stages and exit gates

**Stage 0 — Baseline consolidation.** Align docs with actual lexer, parser, runtime and OOP behavior; freeze compatibility adapters. Gate: documented behavior has regression coverage.

**Stage 1 — Semantic front end.** Add symbol resolution, declared signatures, primitive/container types, dimension constants and pre-execution diagnostics. Gate: statically decidable invalid programs fail before interpretation.

**Stage 2 — Algebraic safety.** Add enums, Option, Result, exhaustive matching, newtypes and checked casts. Gate: positive and negative type tests pass.

**Stage 3 — Effects and ownership.** Add explicit mutation, effect signatures, move/borrow analysis and deterministic cleanup in IR. Gate: invalid resource programs cannot reach code generation.

**Stage 4 — Portable execution.** Define bytecode/VM only if it improves portability or performance; maintain differential tests against the interpreter. Gate: semantics and resource limits agree.

**Stage 5 — Native and systems targets.** Add native backends, FFI, structured concurrency, embedded profiles and SIMD in independently testable slices. Gate: target-specific safety, cancellation and performance suites pass.

**Stage 6 — Self-hosting and supply chain.** Bootstrap the compiler and introduce the native Sambu manifest/store. Remove Python runtime dependence only after a full replacement is published and tested.

## 10. Illustrative syntax (not implemented)

~~~sambu
enum Motion { Still, Moving(Speed) }

fn travel(speed: Speed, time: Time) -> Result<Length, DomainError> {
  let distance = speed * time
  Ok(distance)
}
~~~

This is a direction sketch, not accepted source syntax until lexer, parser, checker, interpreter, formatter and documentation implement identical rules.

## 11. Release acceptance

- [ ] Public status labels distinguish implemented, experimental, planned and deferred.
- [ ] Grammar and semantics have positive, negative and fuzz tests.
- [ ] Dynamic boundaries validate inputs and declare trust assumptions.
- [ ] Scientific models document units, assumptions and error bounds.
- [ ] OOP, SI, percentages, workflows and voxel examples remain covered.
- [ ] Native targets share one semantic specification and differential corpus.
- [ ] Security, reproducibility and performance claims have target-specific evidence.
- [ ] Migration notes protect existing projects and public APIs.

## 12. Final architectural law

SAMBU becomes more powerful by making contracts sharper, not by accumulating keywords. The compiler establishes meaning before optimization; the runtime checks capabilities before execution; tools explain accepted, rejected and expensive operations. Physics guides models and metaphors, not unsupported guarantees. Every feature earns its status through implementation, tests, documentation and measured limits.

## 1.0.2 Engineering control specification and developer control plane

The five-letter engineering code and its acceptance gates are formalized in [SAMBU Engineering Control Specification](SAMBU_ENGINEERING_DOCTRINE.md). The current Python-hosted implementation provides `SambuMachine` (layer-contract validation, bounded workspace parsing, deterministic AST sampling, failure signatures and capability profiles) and `SambuIDE` (versioned source snapshots, syntax diagnostics, outline and lexical completion). These are experimental developer services, not a native compiler, full static analyzer, process sandbox, graphical IDE or LSP server.

The shared `examples/mulberry_charlotte.sambu` compatibility path now contains a small reproducible numeric batch-scaling fixture for CI.
