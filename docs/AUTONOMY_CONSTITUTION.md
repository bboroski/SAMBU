# SAMBU Autonomy Constitution — 50 engineering rules

**Purpose:** translate the 50 autonomy and compiler-topology rules into an auditable engineering baseline for SAMBU. This document is normative for design review; it does not itself implement a feature.

## Status vocabulary

- **Implemented** — the current repository contains working code and tests for the stated, narrowly scoped behavior.
- **Partial** — a useful subset exists, but the full rule or its stated guarantee is not met.
- **Planned** — a design and acceptance gate exist; the feature is not implemented.
- **Deferred** — implementation depends on a future native backend, runtime, target ABI or another prerequisite.

A status applies to the evidence stated in that row, not to an aspirational interpretation of the rule. No rule is considered complete merely because a name, proposal, architecture document or example mentions it.

## Block I — Architecture, compilation and topological connectivity

| ID | Engineering rule | Baseline status | Current evidence and limitation | Acceptance gate |
|---|---|---|---|---|
| AUT-01 | Topological independence | Partial | Core runtime has no third-party runtime dependencies, but the interpreter is hosted by Python and packaging uses a Python build backend. | Publish a dependency graph, isolate host adapters and prove a bootstrap path without undeclared runtime dependencies. |
| AUT-02 | Closed grammar nodes | Implemented | SAMBU owns its lexer and recursive-descent/Pratt parser; no external parser generator is required at runtime. | Grammar conformance corpus covers every token, production, precedence and rejection case. |
| AUT-03 | Recursion and cycle resilience | Partial | Recursive functions are bounded by a call-depth guard; there is no trampoline or stack-safe evaluator for arbitrary recursion. | Add explicit evaluation frames or a verified trampoline; test deep recursion, cycles and cancellation budgets. |
| AUT-04 | Autonomous execution paths | Partial | The interpreter evaluates its own parsed representation; a compiler IR and independent code-generation graph do not yet exist. | Specify phase contracts and verify source → AST → typed IR → executable transformations. |
| AUT-05 | Structural integrity under module removal | Partial | The core works without optional Flask/Django/FastAPI integrations, but still requires the Python host and standard library. | Define a minimal core profile and test builds with every optional adapter removed. |
| AUT-06 | Built-in linker | Planned | No SAMBU object format, symbol linker or final native-binary linker is implemented. | Link relocatable objects with symbol, relocation, visibility and deterministic-order tests. |
| AUT-07 | Deep nested structures | Partial | Arrays, records and recursive AST nodes are supported; parser/evaluator safety still relies on host recursion and bounded runtime behavior. | Add explicit nesting budgets, stack-safe traversal and fuzz tests for deeply nested input. |
| AUT-08 | Isolated module compilation | Planned | The current source pipeline parses and executes a program; there is no stable module/import interface or separate compilation unit. | Define module identity, visibility, interface files, dependency DAG and independent compilation cache. |
| AUT-09 | Internal name routing | Partial | Lexical environments and local shadowing exist; a package/module namespace and collision policy are not complete. | Add qualified names, import aliases, deterministic resolution and ambiguity diagnostics. |
| AUT-10 | Homogeneous type graph | Planned | Runtime values are dynamic Python objects; SI quantities check dimensions dynamically, not through a unified static type graph. | Implement canonical type identities, unification, trait constraints and serializable typed interfaces. |

## Block II — Syntax flow and expressiveness

| ID | Engineering rule | Baseline status | Current evidence and limitation | Acceptance gate |
|---|---|---|---|---|
| AUT-11 | Smooth paradigm composition | Partial | Imperative statements, functions, OOP, traits/interfaces and domain functions coexist; advanced functional, generic and concurrent forms are absent. | Specify common value, effect and ownership semantics across supported paradigms. |
| AUT-12 | Complete branching vocabulary | Partial | `if`, `else`, boolean operators and loops are implemented; exhaustive pattern matching and algebraic-case analysis are not. | Add typed pattern matching with exhaustiveness and unreachable-arm diagnostics. |
| AUT-13 | Minimal syntactic ambiguity | Implemented | A precedence-aware Pratt parser and parser regression tests define the current expression grammar. | Maintain positive, negative, ambiguity and differential parser tests for every grammar revision. |
| AUT-14 | Deterministic dataflow | Partial | Expression evaluation order is defined by the interpreter, but there is no explicit dataflow/effect IR. | Specify evaluation order, dependencies, effects and determinism in a typed intermediate representation. |
| AUT-15 | Syntax evolution without semantic drift | Planned | The project has a compatibility-aware roadmap, but no complete extension or language-version negotiation mechanism. | Require versioned grammar changes, migration notes and old/new conformance suites. |
| AUT-16 | Explicit scope boundaries | Implemented | Blocks and functions use lexical child environments; `let` bindings are immutable and shadowing rules are tested. | Preserve scope invariants through modules, closures, generics and future optimization passes. |
| AUT-17 | Vectorization and path optimization | Planned | Scientific and sparse-voxel algorithms exist, but there is no compiler vectorizer or optimizer over typed IR. | Add semantics-preserving optimization passes with differential tests and target benchmarks. |
| AUT-18 | Readable and rhythmic syntax | Partial | The current grammar is compact and documented; a canonical formatter and style checker are not part of the core toolchain. | Publish a stable formatter, idempotence tests and layout rules. |
| AUT-19 | Dead-branch detection | Planned | There is no general control-flow graph analyzer for unreachable statements or constant-dead branches. | Build CFG reachability and constant-condition diagnostics with soundness boundaries. |
| AUT-20 | Dynamic resource redistribution | Partial | `v_vector_stream` and `wetland_ecosystem_loop` calculate bounded plans; neither starts workers or redistributes live resources. | Implement a supervised scheduler only after task lifecycle, backpressure, cancellation and telemetry contracts exist. |

## Block III — Isolation and safety

| ID | Engineering rule | Baseline status | Current evidence and limitation | Acceptance gate |
|---|---|---|---|---|
| AUT-21 | Runtime error quarantine | Partial | The CLI formats known language/runtime failures; this is not process isolation and arbitrary host failures can still escape. | Define language error values, panic boundaries and subprocess isolation for untrusted programs. |
| AUT-22 | Memory perimeter protection | Deferred | Memory safety is currently provided by the Python host; SAMBU has no ownership checker, raw-pointer model or native memory sandbox. | Introduce ownership/borrowing and verify each native backend's memory safety boundary. |
| AUT-23 | Branch-local type/state verification | Planned | No static type checker or typestate analysis currently validates every branch. | Type-check CFG joins, pattern arms, resource states and error paths before code generation. |
| AUT-24 | Resilience to external noise | Partial | Pure built-ins are deterministic for fixed inputs; OS, clock, network, filesystem and scheduling effects are not formalized as language effects. | Declare effect boundaries and inject clocks, entropy, I/O and cancellation through explicit capabilities. |
| AUT-25 | Self-contained resource management | Partial | The interpreter and test runner need no separate SAMBU daemon; execution still relies on Python and host services for external I/O. | Provide a minimal runtime profile with explicit host capabilities and no hidden service dependency. |
| AUT-26 | Symmetric resource lifecycle | Planned | There is no deterministic RAII/drop system or affine resource checker in the language. | Pair acquisition and release in typed IR; test every return, error, cancellation and unwind path. |
| AUT-27 | Encapsulation enforcement | Partial | Classes support visibility metadata and access checks; a complete module privacy and capability boundary is not implemented. | Test private/protected access across inheritance, modules, reflection and FFI boundaries. |
| AUT-28 | Race-free concurrency | Deferred | The current interpreter has no language-level task scheduler, ownership-aware parallel memory model or race detector. | Define structured concurrency, Send/Sync-like constraints, cancellation and sanitizer-backed race tests. |
| AUT-29 | Minimal deterministic entry point | Partial | CLI accepts one source file or `-c` input; there is no language-level `main` signature or lifecycle contract. | Define one entry-point ABI, arguments, exit result, initialization and teardown order. |
| AUT-30 | Autonomous diagnostics and profiling | Partial | Source spans, stable lexer/parser diagnostic codes and test failure analysis exist; unified tracing and runtime profiling do not. | Add structured diagnostics, trace IDs, allocation/latency metrics and reproducible profiling reports. |

## Block IV — Toolchain and ecosystem closure

| ID | Engineering rule | Baseline status | Current evidence and limitation | Acceptance gate |
|---|---|---|---|---|
| AUT-31 | Built-in code audit | Partial | SAMBU Studio inspects selected application architecture/configuration; there is no general compiler-grade source and type/effect auditor. | Add a native `sambu check` pipeline with diagnostics, rule IDs and stable machine-readable output. |
| AUT-32 | Documentation generation | Planned | Documentation is maintained as project files; no source/doc-comment extraction and cross-reference generator is shipped. | Generate API and module references from parsed declarations and verify links/examples in CI. |
| AUT-33 | Reproducible built-in tests | Implemented | The repository ships `sambu-test` and a Python-hosted test suite with repeat execution and failure summaries. | Preserve deterministic seeds, isolation, property/fuzz hooks and per-target test manifests. |
| AUT-34 | Repository-independent packages | Partial | Distribution uses Python packaging; there is no canonical SAMBU package manifest, lock format or content-addressed module store. | Specify package metadata, integrity hashes, reproducible resolution and offline vendor mode. |
| AUT-35 | Cross-platform translator | Deferred | A portable interpreted source exists, but there is no SAMBU compiler targeting multiple CPU/OS architectures. | Share a target-neutral IR across at least two independently tested code-generation backends. |
| AUT-36 | Interactive REPL | Planned | CLI supports files and one-shot `-c`; persistent incremental parsing/evaluation is not implemented. | Add incremental lexer/parser state, multiline input, scope reset and recoverable diagnostics. |
| AUT-37 | Formal grammar specification | Partial | The user guide describes precedence and syntax; a complete independently consumable EBNF/PEG specification is not yet the parser's verified source of truth. | Publish normative grammar and prove parser/grammar agreement with generated conformance tests. |
| AUT-38 | Versioned compatibility | Implemented | `parse()` preserves the tuple AST; `parse_ast()` exposes typed nodes and a legacy conversion with source spans. | Keep exact compatibility fixtures and explicit deprecation/migration policy for every public AST change. |
| AUT-39 | Cache and memory-layout optimization | Planned | Sparse voxel and tier-planning facilities exist; no measured CPU-cache layout optimizer is present. | Benchmark cache-sensitive layouts on declared targets before adopting alignment or placement claims. |
| AUT-40 | Stable ABI | Deferred | No SAMBU calling convention, symbol mangling, object ABI or FFI compatibility matrix exists. | Version and test calling conventions, data layout, error representation and ABI compatibility per target. |

## Block V — Sovereignty, usability and evolution

| ID | Engineering rule | Baseline status | Current evidence and limitation | Acceptance gate |
|---|---|---|---|---|
| AUT-41 | Complete self-documentation | Partial | Language, domain and architecture guides exist, but not every public API and compiler rule is covered by a single normative reference. | Establish one versioned language reference with tested examples and generated API index. |
| AUT-42 | Minimal boilerplate | Partial | Expressions, functions and domain built-ins keep common tasks concise; macros, generics and richer declarations are absent. | Add abstractions only when they reduce repeated code without obscuring effects or ownership. |
| AUT-43 | Community sovereignty | Partial | The project is MIT-licensed and accepts contributions; a documented governance, release and compatibility process is not complete. | Publish maintainer succession, RFC, review, voting and security-response policies. |
| AUT-44 | Form/semantics alignment | Partial | Current syntax has documented behavior, but the full language lacks one normative specification covering all execution and error rules. | Define observable semantics before optimization and verify with executable conformance tests. |
| AUT-45 | Adaptive complexity | Partial | The interpreter supports small scientific programs and a growing domain library; large systems projects need static types, modules and resource semantics. | Keep a small core while adding opt-in, composable typed and systems layers. |
| AUT-46 | Controlled deprecation | Planned | Compatibility is valued, but no formal deprecation window, warning category or removal schedule is specified. | Require deprecation notices, replacement paths, at least one compatibility window and migration tests. |
| AUT-47 | Predictable execution | Implemented | The present interpreter is synchronous, uses bounded loops/ranges and a call-depth guard, and has no hidden language scheduler. | Preserve explicit side effects and budgets as asynchronous execution is introduced. |
| AUT-48 | Application-to-systems reach | Partial | Scientific, workflow, OOP, voxel and integration models cover application work; native OS, embedded and kernel programming are not supported. | Add capability-scoped FFI, target profiles, no-std core and hardware validation only after ABI and ownership gates. |
| AUT-49 | Language-level metaprogramming | Planned | Built-ins and Python-side extension points exist, but SAMBU compile-time macros, hygienic expansion and reflection contracts do not. | Add hygienic macros with bounded expansion, provenance spans and compile-time/runtime separation. |
| AUT-50 | Full bootstrap autonomy | Deferred | SAMBU is interpreted by Python; it cannot yet compile its compiler or maintain its own complete toolchain independently. | Bootstrap in stages: self-hosted lexer/parser, then checker/IR, compiler, package manager and test runner; reproduce builds from a trusted seed. |

## Dependency and sovereignty boundary

“Zero third-party runtime dependencies” is not the same as “self-hosted” or “independent of the host.” The current core has no declared third-party runtime dependencies, but the interpreter executes on Python and installation uses the Python packaging toolchain. The project must not claim native compilation, an internal linker, a stable ABI, race-free parallel execution or self-hosting until their respective gates pass.

The first practical sovereignty milestone is not a custom kernel or a claim of total independence. It is a documented and testable core dependency graph: lexer → parser → AST → semantic analysis → typed IR → interpreter/backend, with optional integrations isolated behind explicit interfaces.

## Evolution policy

1. Every new capability receives a stable rule ID, status, owner, tests and documented exit gate.
2. A proposal never upgrades a status. Only merged implementation plus passing conformance tests can do that.
3. Changes to tokens, precedence, name resolution, evaluation order, public AST shape or error behavior require compatibility fixtures and migration notes.
4. Performance claims require repeatable target-specific benchmarks. Safety claims require negative tests and explicit scope.
5. No stage may silently weaken existing OOP, SI-dimension, percentage, Anatidae, workflow or voxel behavior.

See [the 101-contract language evolution architecture](LANGUAGE_EVOLUTION.md) for the lower-level compiler/type/runtime contracts.
