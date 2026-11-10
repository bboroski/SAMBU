# MCL Systems Architecture for MCL

**Baseline:** MCL 0.11.0 alpha + experimental concurrency slice  
**Status:** mixed — the first runtime primitives are implemented; the native systems-language architecture is a staged proposal.  
**Purpose:** define an original, safe-by-default systems language with the breadth expected from a modern C++-class language, without copying C++ syntax, ABI, implementation or library code.

## 1. What “C++-class” means here

The goal is capability breadth, not source or binary compatibility with C++. MCL should eventually support the full systems-programming lifecycle:

- native compilation, separate compilation, modules, linking and reproducible packages;
- static type checking, generics, constraints, compile-time evaluation and reflection;
- classes, value types, interfaces/traits, overloads, operator protocols and zero-cost abstractions;
- deterministic resource lifetime, explicit ownership, borrowing and safe interoperability;
- containers, algorithms, ranges, text, time, files, networking, processes, diagnostics and numerics;
- cooperative tasks, actors, channels, structured concurrency, parallel execution and supervision;
- target-specific FFI, C ABI, SIMD, GPU and embedded/system interfaces;
- formatter, linter, build system, package manager, debugger, profiler, sanitizer and test tooling.

This is a long-term compatibility target for engineering capability. It does **not** mean that MCL accepts C++ source, exposes the C++ ABI, or already implements the complete surface above.

C++ is an evolving reference point: C++23 is published and C++26 work is tracked by WG21. MCL should review the standards process and engineering guidance periodically, but choose its own semantics and stable subset rather than chase every proposal. See the [ISO C++ status page](https://isocpp.org/std/status), the [WG21 editors' report for the 2026 working draft](https://www9.open-std.org/JTC1/SC22/WG21/docs/papers/2026/n5047.html), and the [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines).

## 2. MCL design laws

1. **One meaning per program.** Evaluation order, conversions, overflow, error propagation and cancellation must be specified before optimization.
2. **Safe by default.** Raw pointers, unbounded allocation, unchecked casts and direct device access belong behind explicit unsafe capabilities.
3. **Ownership is visible.** Every resource has one declared owner or a documented shared-ownership protocol.
4. **Bounded work.** Tasks, mailboxes, buffers, retries, recursion and diagnostics have limits with explicit failure behavior.
5. **Isolation before parallelism.** Actors own mutable state; messages cross boundaries as validated payloads; shared memory requires a synchronization contract.
6. **Failure is data.** A fault is recorded, contained and surfaced. The runtime must not silently turn failure into success.
7. **Recovery is finite.** Supervisors have restart strategies, rolling budgets and escalation paths. Infinite restart loops are not recovery.
8. **Ports are typed.** Software channels validate their declared value type; hardware ports require a target adapter and device-specific validation.
9. **Close is a protocol.** Resource cleanup is deterministic and reverse-ordered; physical safety is confirmed only by a real driver's acknowledgement.
10. **No fictional guarantees.** A Python-hosted generator scheduler is not a native fiber runtime; an HSM adapter interface is not an HSM; a proposal is not a shipped feature.

## 3. Implemented experimental runtime slice

The following APIs exist in `mcl.concurrency` and are exported from the `mcl` package.

### 3.1 Cooperative fibers — `FiberScheduler`

`FiberScheduler` accepts Python generator functions, resumes them in deterministic FIFO round-robin order, and understands `yield_now()` and `sleep_ticks(n)`. Sleep advances a logical scheduler clock; it does not block the host thread. Each resume counts as one scheduler step. Global and per-fiber step budgets cap work.

~~~python
from mcl import FiberScheduler, yield_now, sleep_ticks

scheduler = FiberScheduler(max_tasks=128, max_total_steps=20_000)

def worker(label):
    yield yield_now()
    yield sleep_ticks(2)
    return label

first = scheduler.spawn(worker, "north", name="north-worker")
second = scheduler.spawn(worker, "south", name="south-worker")
report = scheduler.run()
print(scheduler.result(first), scheduler.result(second), report.completed)
~~~

**Boundary:** these are cooperative Python generator tasks on the calling OS thread. They are not preemptive, do not run in parallel on CPU cores, do not allocate custom native stacks, and do not provide a language-level `yield` statement. There is no OS-thread migration because this scheduler creates no OS threads. It still performs explicit logical task switches at yield points.

### 3.2 Actors — bounded mailboxes and serialized state

An actor owns a JSON-shaped state value and a FIFO mailbox. Its handler has the signature `handler(state, message) -> next_state`. The runtime copies and validates the input state, message and returned state. The next state is committed only after a successful handler result. A failed message is placed in a bounded dead-letter log; partial mutations to the handler's working copy are not committed.

Payload limits currently include a maximum UTF-8 encoded size, nesting depth and item count. Unsupported host objects, non-finite floats and non-string object keys are rejected.

The language exposes these built-ins:

| Built-in | Contract |
|---|---|
| `actor(handler, initial_state, mailbox_capacity=256)` | Create an actor; handler accepts exactly two arguments |
| `actor_send(actor, message)` | Enqueue a bounded, validated message |
| `actor_drain(actor, max_messages=1)` | Process up to the specified number of messages sequentially |
| `actor_state(actor)` | Return a defensive copy of actor state |

~~~mcl
fn add(state, message) {
  return state + message
}

let counter = actor(add, 0, 32)
actor_send(counter, 4)
actor_send(counter, 7)

let report = actor_drain(counter, 16)
print(report.processed)
print(actor_state(counter)) // 11
~~~

This serialization guarantee applies to messages drained by the actor runtime. It does not make arbitrary Python globals, other actors' states or external devices magically race-free.

### 3.3 Hierarchical supervisors

A supervisor can own actors or child supervisors. Supported strategies:

- `one_for_one` — restart only the failed child;
- `one_for_all` — restart every child of the supervisor;
- `rest_for_one` — restart the failed child and children registered after it.

Each supervisor has a rolling restart window, a maximum restart count and a bounded event history. Exceeding the budget marks the supervisor failed and reports the failure to its parent. An actor restart resets its state to the declared initial snapshot, increments its generation, keeps its pending mailbox and does not silently replay the failed message; that message is recorded as a dead letter.

Language built-ins are `supervisor(strategy, max_restarts=3, window_seconds=60)`, `supervise(supervisor, child)`, and `supervisor_status(supervisor)`.

~~~mcl
fn guarded(state, message) {
  if (message == 0) {
    return 1 / 0
  }
  return state + message
}

let worker = actor(guarded, 5, 16)
let root = supervisor("one_for_one", 3, 60)
supervise(root, worker)

actor_send(worker, 0)
let attempt = actor_drain(worker)
print(attempt.status)         // active after a successful supervised restart
print(actor_state(worker))    // 5: initial state restored
~~~

A restart is not proof of recovery. The failed message, event history and restart count remain inspectable. Production applications must decide whether to retry, compensate, dead-letter or escalate each operation.

### 3.4 Typed software channels

`TypedChannel` and the MCL built-ins `channel(type, capacity=64)`, `channel_send`, and `channel_receive` provide bounded, non-blocking FIFO queues for `int`, `integer`, `float`, `number`, `text`, `string`, `bool`, and `boolean`.

~~~mcl
let radio = channel("text", 8)
channel_send(radio, "shelter-status: ready")
print(channel_receive(radio))
~~~

A type mismatch, full queue or empty receive fails explicitly. These are software channels, not a GPIO, UART, radio, power bus or verified hardware port. Those require typed device descriptors, permissions and host/target drivers.

### 3.5 Resource scopes, metadata and dual authorization

Python APIs:

- `ResourceScope` registers resources, releases transferred ownership and closes remaining resources in reverse acquisition order. It attempts every close and reports all failures. A closer returning `False` means it did not confirm a safe state.
- `ModuleMetadata` validates required descriptive fields. It is not a compiler header or identity credential.
- `DualAuthorizationGate` requires two independently supplied verifiers for a protected operation. The hardware verifier may delegate to a TPM/HSM provider, but no hardware key store or cryptographic protocol is bundled.

~~~python
from mcl import ResourceScope, DualAuthorizationGate

with ResourceScope(name="radio-session") as scope:
    radio = scope.own(open_radio_device())

gate = DualAuthorizationGate(
    local_verifier=check_operator_approval,
    hardware_verifier=verify_hsm_signature,
)
gate.authorize(local_approval, signed_hardware_approval)
~~~

The example's device and verification functions are host adapters, not built-ins supplied by MCL. A successful callback is only as trustworthy as the implementation and trust roots behind it.

## 4. What is deliberately not claimed yet

| Capability | Status |
|---|---|
| FIFO cooperative Python generator scheduler | Implemented · experimental host API |
| Actor queues, bounded payloads and sequential state commits | Implemented · experimental; available in MCL source |
| Hierarchical restart supervisors and budgets | Implemented · experimental host/runtime API |
| Typed bounded software channels | Implemented · experimental; available in MCL source |
| Reverse-order resource scopes | Implemented · experimental host API |
| Two-verifier authorization boundary | Implemented · adapter primitive; no bundled HSM |
| Native green threads and native stack allocator | Planned |
| Preemptive/parallel multicore scheduling | Planned |
| Static race, deadlock and effect analysis | Planned |
| Language-level RAII, ownership and borrow checking | Planned |
| Generic types, concepts/constraints and compile-time evaluation | Planned |
| Native compiler, optimizer, linker and stable ABI | Planned |
| Hardware I/O backends and device-specific HSM integration | Deferred to target adapters |

## 5. C++-class capability map

The roadmap is defined by semantic layers, not by superficial keyword matching.

| Language area | Required MCL contract |
|---|---|
| Front end | Complete grammar, modules, imports, namespaces, diagnostics and stable source maps |
| Type system | Primitives, structs, classes, enums, tagged unions, generics, constraints, inference and explicit conversions |
| Compile-time | Constant evaluation, compile-time assertions, reflection metadata and deterministic build-time computation |
| Abstraction | Traits/interfaces, overload resolution, operator protocols, closures and monomorphization where justified |
| Memory | Ownership, move semantics, borrowing, lifetimes, arenas, allocators, alignment and explicit unsafe FFI |
| Errors | Typed `Result` / `Option`, propagation, panic boundaries and cleanup guarantees |
| Runtime | Bytecode or native execution, stack/heap policy, scheduler, actors, supervision, cancellation and parallelism |
| Standard library | Containers, algorithms, iterators/ranges, text/Unicode, math/units, time, filesystem, process, networking and synchronization |
| Systems access | C ABI, FFI, atomics, SIMD, GPU, embedded profiles, MMIO and hardware drivers |
| Toolchain | Compiler, linker, package/build system, formatter, linter, tests, debugger, profiler and sanitizer integrations |

MCL should not reproduce C++'s undefined-behavior surface as a compatibility requirement. The preferred direction is a safer subset with explicit unsafe boundaries and documented performance costs. A native backend must prove that safe abstractions do not impose hidden allocation or dispatch costs when those costs can be removed.

## 6. Delivery sequence and acceptance gates

**Stage A — Runtime containment (current slice).** Actors, message limits, typed channels, bounded cooperative scheduling, supervision, resource scopes and test coverage. Gate: deterministic tests cover ordering, failure, restart budgets, cancellation, queue limits and cleanup.

**Stage B — Semantic safety.** Add a typed semantic IR, symbol resolution, structured errors, Option/Result, resource effects and static diagnostics. Gate: invalid programs fail before execution where statically decidable.

**Stage C — Ownership and generic abstraction.** Add structs/enums, generics, trait bounds, move/borrow rules, lifetimes, explicit mutation and deterministic destruction. Gate: negative ownership tests and reference interpreter agree.

**Stage D — Modules and build graph.** Add packages, module interfaces, separate compilation, lockfiles, dependency hashes and deterministic builds. Gate: clean builds and incremental builds produce equivalent public interfaces.

**Stage E — Native backend.** Add portable bytecode or a native target after profiling justifies it; then code generation, linker, ABI and C interoperability. Gate: differential conformance corpus, sanitizer runs and reproducible toolchain tests.

**Stage F — Parallel systems runtime.** Add OS-thread workers, atomics, structured parallelism, cancellation, work stealing and NUMA-aware placement only after memory model and ownership rules are enforced. Gate: race detectors, stress tests, starvation/fairness tests and target-specific benchmarks.

**Stage G — Self-hosting and ecosystem.** Build standard libraries, formatter, package manager, debugger, profiler, language server and a reproducible bootstrap compiler. Gate: the toolchain can rebuild itself and verify release provenance.

No stage is considered complete because its syntax appears in a design document. Every feature must include specification, code, positive and negative tests, diagnostics, documentation and measured limits.

## 7. Compatibility and governance

- Preserve existing `parse()` tuple AST and public Python APIs until a documented major migration.
- Introduce new syntax behind explicit language editions or feature gates.
- Keep the reference interpreter as an executable semantic oracle while a native backend is developed.
- Record architecture decisions, threat models, supported targets and deprecation windows.
- Reject changes that promise “race-free”, “panic-free”, “zero-cost”, “zero-migration” or “hardware-secure” behavior without a precise scope and reproducible evidence.

**Final law:** make the safe path the easy path, the unsafe path visible, failures recoverable, and every performance promise measurable.


## 8. Evidence-led autonomy: six archetype design lenses

The six project archetypes are formalized one letter at a time in the
[MCL Archetype Engineering Charter](MCL_ARCHETYPE_CHARTER.md). Their
purpose is to add engineering constraints, not fictional superpowers:

- **ALUCARD:** adaptive quotas, leased capabilities, undoable transitions,
  containment, auditable evidence, recovery ceilings and deterministic inputs.
- **GING:** goal-bound inquiry, isolated trials, novelty memory and graduation gates.
- **RAIDEN:** recovery tiers, controlled degradation, incident supervision,
  deterministic restoration, escalation budgets and neutral telemetry.
- **DJINN:** declared capabilities, immutable job capsules, isolation profiles,
  narrow interfaces and non-interference verification.
- **MADARA:** competing models, adversarial challenge, deterministic semantics,
  architecture records, reversible changes and acceptance evidence.
- **SHANKS:** scoped trust, explicit handoffs, authority separation, native
  interoperability contracts, knowledge continuity and human stewardship.

### 8.1. Current autonomy implementation

The experimental Python-host API in `mcl.autonomy` implements:
immutable task manifests, declared capability checks, component-wise resource
capping, risk-ceiling review, deterministic plan fingerprints, a bounded
append-only SHA-256 experiment ledger, and reversible/path/test/evidence
preflight for proposed changes.

It deliberately has no arbitrary-code executor, filesystem writer, policy
self-modifier, repository merge function or deployment function. An accepted
preflight means only that the proposal may proceed to independent tests and
review. The module does not create an OS security boundary.

### 8.2. Next engineering gates

1. Add architecture decision records and a machine-readable feature maturity
   registry, with promotion requiring linked tests and evidence.
2. Build a subprocess/container experiment runner with enforceable CPU, memory,
   output, process, filesystem and network quotas.
3. Add baseline-versus-alternative benchmark plans and reproducible environment
   fingerprints; never interpret a hash as proof that evidence is true.
4. Surface plans, clipped budgets, capability grants and review reasons in
   MCL Studio before allowing any IDE action.
5. Add native ownership/effect analysis before considering automatic source
   edits or a native self-hosting loop.

Human review remains mandatory for high-impact policy, packaging, CI, secrets,
release and deployment changes.
