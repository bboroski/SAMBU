# SAMBU Native Compiler Architecture

**Status:** staged architecture and implementation contract.  
**Baseline:** Python-hosted interpreter plus an experimental, backend-independent C11 IR kernel in \`native/\`.  
**Important:** This document is not a claim that LLVM code generation, a native runtime, or production-grade static analysis already exists.

## 1. Objective and compatibility boundary

SAMBU is evolving from a Python-hosted language and toolkit toward an optional native compilation path. Both paths must coexist during migration:

- **Compatibility path:** current lexer, parser, source-aware AST, interpreter and Python toolkit.
- **Native path:** source front end → typed HIR → SSA MIR → target-neutral LIR → backend → object/link stage.
- **Boundary rule:** Python objects may remain in the compatibility interpreter and developer tools, but must never appear in the native execution ABI or native hot path.

Native compilation remains opt-in until supported language constructs pass semantic-equivalence tests. Existing \`.sambu\` programs must not silently change behavior when the native backend is selected.

## 2. Compiler pipeline and IR contract

### 2.1 Canonical pipeline

\`\`\`text
UTF-8 source
    │
    ▼
Lexer / parser ──► source-aware AST
                       │
                       ▼
                 typed HIR
                       │
                       ▼
                 SSA MIR + CFG
                       │
                       ▼
                 target-neutral LIR
                       │
                       ▼
              backend adapter (LLVM first)
                       │
                       ▼
             object files / linker / debug info
\`\`\`

The AST is a front-end artifact, not the native ABI. The first native kernel exposes a typed scalar HIR expression API and lowering path. Parser bridging and statement/function lowering remain later work.

### 2.2 HIR — source semantics

HIR preserves source-level intent while removing parser-specific details. Each node carries a canonical type, end-exclusive source span, operation tag and typed child references. Effect and ownership annotations are added after those analyses have formal rules.

HIR is backend-independent. It must not contain Python object references, interpreter environments or host callbacks.

### 2.3 MIR — optimization contract

MIR must guarantee:
- every SSA value has exactly one definition;
- every operation has explicit operand and result types;
- every block ends in exactly one terminator;
- control-flow joins use typed \`phi\` nodes;
- values dominate their uses;
- side effects are explicit and ordered;
- source locations survive lowering for diagnostics and debug information.

The current C11 kernel implements typed SSA values, including operand-free unit-return terminators, and checks dense definitions, operand-before-use and a final return for a **single basic block**. It does not yet implement CFG, dominance analysis or phi nodes. The verifier must become CFG-aware before multi-block code is admitted.

### 2.4 LIR — target-neutral machine operations

LIR makes data movement and operations explicit. It uses virtual registers and target-independent operations; physical register assignment, instruction selection and ABI lowering belong to a backend adapter.

The current LIR is a small virtual-register representation of the first MIR subset. It is not x86-64 or AArch64 machine code.

### 2.5 Allocation and symbol identity

Compiler-owned short-lived nodes use arenas. An arena must guarantee requested alignment, use overflow-checked size arithmetic and have explicit reset/dispose lifetimes. Pointers become invalid after reset.

Identifiers and canonical names use a compiler-lifetime interner. Interned strings remain stable until interner disposal. Original source spelling remains separate from canonical symbol identity so diagnostics and formatting can reproduce what the programmer typed.

### 2.6 IR stability, serialization and LTO

IR serialization is a future versioned contract, not a dump of C structs. The format must define:
- magic bytes, schema version and endianness;
- canonical type and opcode identifiers;
- length limits and checked offsets;
- source/module identity and dependency hashes;
- deterministic ordering;
- validation before allocation or execution;
- invalidation rules for compiler, target and ABI changes.

Never serialize pointers, padding bytes, native struct layouts or arena addresses. LTO may consume only verified, version-compatible IR.

## 3. Type, effect and ownership system

### 3.1 Type checking strategy

Use bidirectional typing as the primary algorithm:
- infer local expression types where no expected type is available;
- check function boundaries, generic instantiations and public APIs against explicit types;
- use unification for inference variables;
- report the smallest source span that explains a contradiction.

A Hindley–Milner core can inform inference, but SAMBU records, traits, effects, ownership and dimensional types require explicit extensions. Choosing an inference algorithm does not automatically provide Rust's type system.

### 3.2 Type layers

Implement in this order:
1. primitives, arrays, records, tuples and function types;
2. generic functions and nominal data types;
3. traits with compile-time resolution and monomorphization;
4. algebraic data types and exhaustive pattern matching;
5. const generics for dimensions and fixed-size buffers;
6. GADT-like refinement after termination, exhaustiveness and inference rules are specified.

GADTs and const generics must share compile-time resource limits and diagnostic rules.

### 3.3 Effects

Functions declare or infer effect rows such as \`IO\`, \`State\`, \`Async\`, \`Unsafe\` and \`Device\`. Pure functions have an empty effect set. The optimizer may rely on purity only when the checker proves it; an annotation alone is not proof.

### 3.4 Ownership and resources

Use ownership and borrowing as the default memory-safety model:
- one owning value at a time;
- immutable shared borrows and exclusive mutable borrows;
- lexical lifetimes and explicit moves;
- moved-from bindings become unusable;
- resource destructors run exactly once in reverse initialization order.

Use arenas/regions for compiler data and explicitly scoped temporary workloads. Shared cyclic graphs may use reference counting with a tested cycle strategy, but reference counting must not silently replace ownership for all values. Unsafe operations live behind explicit audited boundaries.

Linear types can strengthen resource APIs, but the first ownership checker should prefer a tractable move/borrow model over a large collection of partially specified features.

## 4. Runtime and memory layout

The native runtime needs a narrow, versioned ABI:
- primitive values and POD aggregates pass without boxing;
- strings and dynamic collections carry explicit length, capacity and allocator metadata;
- stack allocation is allowed only when escape analysis proves the lifetime;
- heap and stack ownership are distinct in the type/lowering model;
- custom allocators are explicit values or module configuration, never hidden globals;
- RAII/drop is deterministic;
- reflection and dynamic type metadata are opt-in.

The runtime must not require CPython. Platform libc use can be minimized behind a portability layer; a no-stdlib mode is a separate embedded target, not a default promise.

## 5. Backend and optimization strategy

### 5.1 Backend selection

Keep the IR independent of the selected compiler backend. The first production candidate is an LLVM adapter using the supported C API. Cranelift remains an alternative if compile latency and runtime benchmarks justify a Rust-facing adapter. Do not maintain two backends before one is correct.

A backend adapter declares target triple, data layout, supported features, ABI version and diagnostics mapping. It rejects unsupported IR explicitly instead of generating subtly incorrect code.

### 5.2 Optimization order

1. verifier and canonicalization;
2. constant folding and propagation;
3. dead-code elimination;
4. common-subexpression elimination where effects permit;
5. inlining guided by code size and profile data;
6. loop analysis and scalar replacement;
7. vectorization only with proven aliasing, alignment and numeric semantics;
8. PGO and LTO after stable module identity and reproducible object emission.

Fast-math is opt-in and carries a documented IEEE/error contract. Do not replace division with reciprocal multiplication unless the selected numeric mode permits changed rounding and exception behavior.

### 5.3 Build and debug artifacts

Incremental compilation keys include source content, imported interface hashes, compiler version, target triple, feature flags and ABI version. Debug output maps generated instructions back to \`.sambu\` source spans. Cross-compilation is supported only for targets with a tested sysroot, linker and runtime.

## 6. Concurrency model

Build structured concurrency before exposing low-level task primitives:
- task scopes own child tasks and join or cancel them before scope exit;
- cancellation is cooperative and has explicit cleanup semantics;
- async functions lower to state machines;
- scheduler workers use bounded work queues and work stealing;
- channels declare capacity, ownership transfer and cancellation behavior;
- atomics require explicit memory ordering;
- actor mailboxes are bounded and back-pressure aware;
- supervision restarts are limited by policy and preserve failure evidence.

A deadlock checker can prove only restricted lock protocols. It must state its assumptions and must not claim general deadlock freedom for arbitrary lock-based programs. OS integrations (io_uring, epoll, kqueue, IOCP) sit behind a platform interface.

## 7. Scientific types and numeric semantics

SI dimensions are phantom compile-time types where possible and erase after successful checking. Runtime values store canonical numeric representation only when conversion is required at a boundary.

Numeric contracts:
- integer overflow behavior is defined and tested (checked in safe/debug mode; explicit wrapping operations when requested);
- default floating behavior follows documented IEEE semantics;
- FMA and fast-math are selected under an explicit numerical policy;
- dimensional compatibility is checked in generic functions;
- compile-time constants are evaluated only when exact and target-independent;
- arbitrary-precision integers/rationals are opt-in;
- CPU/GPU/FPGA providers implement the same trait-level contract and advertise precision/error bounds.

## 8. Voxel and simulation kernel

The native voxel API uses validated views over contiguous memory:
- SoA storage for hot per-voxel fields;
- Morton/Z-order traversal where workload benchmarks support it;
- checked chunk dimensions and index arithmetic;
- deterministic partitioning for parallel mesh generation;
- LOD streaming with bounded memory budgets;
- octree/SVO allocators behind ownership-safe handles;
- GPU compute adapters behind explicit capability discovery;
- deterministic floating-point mode for simulation reproducibility.

Existing Python voxel structures and engine adapter examples remain compatibility/prototype surfaces. They are not evidence of a completed native GPU path. Compression identifiers such as SNAP/PCC require a formal format, test vectors and decoder fuzzing before entering a stable ABI.

## 9. Security and trust boundaries

Security properties are enforced by code, not descriptive profile names:
- capability tokens are explicit and unforgeable within the runtime model;
- the default sandbox grants no host or device access;
- syscalls are mediated by platform adapters and fail closed;
- safe and unsafe modules have a clear boundary;
- secret buffers support explicit zeroization with compiler-resistant primitives;
- trust comparisons use constant-time functions where required;
- audit events are append-only and bounded/rotated under policy;
- signed packages include publisher identity, content digest and verification policy;
- untrusted IR is validated before deserialization and never executed during parsing.

seccomp-bpf, pledge/unveil, memory tagging, CHERI and formal verification are platform-specific hardening layers. Their absence must be reported as unavailable, not silently emulated.

## 10. Tooling, ecosystem and migration

Required staged tools:
- source formatter with idempotence tests;
- LSP diagnostics, completion and semantic tokens from the canonical parser/semantic model;
- debugger mappings and value renderers;
- profiler symbols that preserve SAMBU function and source names;
- package manager with locked dependencies and content hashes;
- build graph with deterministic actions and cache keys;
- reproducible documentation and API extraction;
- fuzzed lexer/parser/IR deserializers and property-based semantic tests.

Migration is gradual:
1. parse legacy \`.sambu\` with the compatibility front end;
2. lower only the supported subset into native HIR;
3. reject unsupported constructs with precise diagnostics;
4. permit explicit interpreter fallback;
5. keep C ABI/FFI adapters narrow and versioned;
6. stabilize standard-library APIs through RFCs and edition gates.

A Python-to-SAMBU transpiler is a separate migration utility. It can preserve behavior only for a declared Python subset; arbitrary Python programs cannot be translated losslessly.

## 11. Delivery milestones and acceptance gates

| Milestone | Scope | Exit gate |
|---|---|---|
| N0 — IR kernel | arena, interner, typed HIR subset, SSA MIR, verifier, virtual-register LIR | C11 build, sanitizers, verifier-negative tests |
| N1 — Front-end bridge | AST-to-HIR lowering, symbol table and diagnostics | source corpus lowers with unchanged interpreter results |
| N2 — Semantic core | type inference, effects, ownership/borrow checking, pattern analysis | soundness tests, compile-fail suite and fuzzing |
| N3 — Native backend | LLVM adapter, object emission, linking and debug info | executable fixtures match interpreter semantics |
| N4 — Optimization | CFG/phi, SSA passes, incremental cache, PGO/LTO | reproducible benchmarks and semantic equivalence |
| N5 — Runtime | ownership-aware values, structured concurrency and platform IO | stress tests, race tests and fault injection |
| N6 — Scientific/voxel native path | erased SI types, SoA, SIMD and optional GPU | numerical error budgets and workload benchmarks |
| N7 — Ecosystem hardening | package manager, LSP/debugger, signing and sandboxing | security review and reproducible release artifacts |

A milestone is complete only when implementation, negative tests, documentation and CI acceptance criteria agree. An enum, placeholder or design document alone is not implementation.

## 12. Current implementation inventory

Implemented in this repository:
- Python lexer/parser, source-aware AST and interpreter;
- scientific dimensions/quantities, domain models and percentage arithmetic;
- experimental actors, supervisors and typed software channels;
- Python voxel structures and example engine adapters;
- C11 native IR kernel: arena allocation, string interning, typed scalar HIR, single-block SSA MIR, MIR verifier, virtual-register LIR and LIR verifier.

Not yet implemented by the native kernel:
- parser-to-HIR bridge and statement-level lowering;
- multi-block CFG, phi nodes, dominance analysis and optimization passes;
- type inference, effect checking, ownership/borrow checking and const generics;
- IR serialization, incremental compilation and LTO;
- LLVM/Cranelift adapter, object generation, linker integration or machine code;
- native heap/runtime, work-stealing scheduler or async IO;
- native SIMD/GPU voxel kernels, sandboxing, package manager and LSP server.

Publish these as two separate inventories: working compatibility features and native-backend readiness.
