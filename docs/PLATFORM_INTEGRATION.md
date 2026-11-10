# Unified Platform Integration Contract

**Contract version:** 1.0  
**Status:** architectural baseline; implementation status is stated per repository below.  
**Purpose:** define a shared, testable vocabulary for composing all nine repositories without circular dependencies, hidden authority or fictional capability claims.

This contract replaces narrative archetypes with engineering terms: capability governance, bounded resource budgets, immutable evidence records, deterministic lifecycle control, failure supervision, typed policy manifests, isolated workers and versioned interoperability.

## Local responsibility

SAMBU owns the language and developer-tooling plane: parsing, AST representation, interpreter execution, workflow/policy modeling, architecture validation and reproducible source inspection. The current runtime is Python-hosted and experimental. Its capability profiles do not enforce an operating-system boundary, and native compilation, complete static type/effect analysis and a production plugin ABI remain roadmap work.

## 1. System decomposition

| Plane | Repository | Technical responsibility | Current boundary |
|---|---|---|---|
| Composition | [Klipot](https://github.com/bboroski/Klipot) | System composition, manifest validation, dependency planning and controlled integration | Architecture specification; do not assume an implemented orchestrator until code and tests exist |
| Language and workflow | [SAMBU](https://github.com/bboroski/SAMBU) | Language runtime, AST inspection, declarative workflows, policy models and developer tooling | Experimental Python-hosted language/tooling; native compiler and OS sandbox are not delivered |
| Operator interface | [ToolNG](https://github.com/bboroski/ToolNG) | Local Windows diagnostics, evidence presentation and user-approved reports | C17/Win32 application; read-only device diagnostics |
| Production integration | [ReaperCripple](https://github.com/bboroski/ReaperCripple) | Embedded bring-up, BSP adapters, fixture validation, calibration and manufacturing traceability | C11 framework; hardware qualification remains board- and fixture-specific |
| Platform foundation | [Kloz](https://github.com/bboroski/Kloz) | Fixed-capacity memory, status ABI and versioned platform operations | Freestanding-oriented C11 substrate |
| Lifecycle control | [CO](https://github.com/bboroski/CO) | Deterministic component lifecycle, bounded polling and reverse-order cleanup | Allocation-free C11 runtime; no preemptive scheduler |
| Runtime assurance | [SaintSI](https://github.com/bboroski/SaintSI) | Heartbeat observation, timeout evaluation and accidental-corruption detection | Allocation-free C11 monitor; no autonomous reset or cryptographic trust |
| Kernel substrate | [NUN](https://github.com/bboroski/NUN) | Kernel boot contract, architecture entry, memory and execution boundaries | Specification-only; no bootable kernel implementation exists |
| Bootstrap supervisor | [NUNLauncher](https://github.com/bboroski/NUNLauncher) | Kernel image validation and versioned boot-information handoff | Specification-only; no bootloader or image installer exists |

## 2. Dependency direction

The intended composition is layered, not a shared mutable monolith:

```text
                Operator / Product / Factory Station
                    |             |             |
                 ToolNG       Firmware       SAMBU tools
                                  |
                          Klipot manifests
                         and integration plan
                                  |
                +-----------------+-----------------+
                |                 |                 |
            Lifecycle         Assurance       Production
               CO              SaintSI       ReaperCripple
                \                 |                 /
                 \                |                /
                    Platform contracts and adapters
                                  |
                                 Kloz
                                  |
                           Board / SoC / OS
```

The diagram describes intended integration boundaries, not a claim that every repository currently links to every other repository. Each library remains independently buildable. An application, firmware integration layer or station adapter owns the concrete composition and translates result codes explicitly.

**Allowed dependency direction:**

- Kloz defines portable primitives and platform contracts; it does not import higher-level policy.
- CO and SaintSI remain independent; an integration adapter may pass observed lifecycle progress to the monitor.
- ReaperCripple may consume platform and lifecycle interfaces through explicit adapters after target qualification; its board layer remains authoritative for electrical and silicon-specific behavior.
- SAMBU may validate manifests, model dependencies and produce reproducible plans; its current Python runtime is not a native OS isolation boundary.
- ToolNG may use selected portable policy logic, but its Windows UI and device discovery remain in its own application boundary.
- Klipot may validate and describe compositions; it must not silently rewrite component policy, bypass local approval or assume ownership of hardware.
- NUNLauncher validates an image and constructs a versioned boot-information block before handoff; it does not own kernel memory management or drivers.
- NUN revalidates the received boot context and owns the kernel execution boundary. Kloz platform services and SaintSI observation remain optional adapters; the kernel stays independently buildable.

No project may create a reverse dependency merely to obtain a helper function. Shared contracts belong at the lowest stable interface or in a separately versioned schema.

## 3. Common component contract

Any component exposed across a repository boundary should declare:

1. **Identity:** stable component ID, semantic version and contract version.
2. **Layout:** ABI version and structure size for C interfaces; fixed-width integer fields; explicit alignment and reserved fields.
3. **Capabilities:** named operations required and provided; unknown capabilities fail closed.
4. **Ownership:** caller-owned buffers and explicit lifetimes; no hidden allocation or ambient global state.
5. **Budgets:** maximum memory, messages, payload bytes, work steps, retries and execution time where measurable.
6. **Failure behavior:** stable result code, state transition and cleanup behavior.
7. **Evidence:** source revision, configuration fingerprint, test result and hardware/fixture identity where relevant.

Do not serialize native pointers, compiler-dependent bitfields or raw structure padding as a portable interchange format. Use versioned schemas for cross-process and cross-language payloads.

## 4. Capability and resource governance

Use least-privilege capability profiles and component-wise resource ceilings. A requester may consume less than the approved budget, but cannot enlarge policy limits by requesting more.

Recommended resource dimensions:

- memory bytes and fixed-capacity object count;
- queue depth and message payload bytes;
- execution steps or CPU-time budget;
- wall-clock deadline and cancellation latency;
- retry/restart count within a rolling interval;
- log/event capacity and explicit loss policy.

Normal, degraded and recovery modes must be explicit states. Degraded mode may shed only declared optional work; it must preserve safety invariants and report every suppressed operation. There is no universal emergency mode that removes all limits. A recovery path must remain bounded and auditable.

## 5. State, events and evidence

Use monotonic sequence numbers for ordered local events and host-supplied monotonic ticks for elapsed-time calculations. Tick frequency, width, wrap behavior and clock domain must be documented by the platform adapter.

Separate three storage classes:

- **Transient telemetry ring:** fixed capacity, explicit overwrite/drop policy and loss counter.
- **Append-only evidence journal:** versioned records linked by hashes when durable audit history is required; persistence, access control and retention are host responsibilities.
- **Checkpoint/snapshot:** immutable, versioned recovery input that is validated before restore.

A hash chain detects later changes relative to the current record sequence; it does not prove that the original event was true. CRC is suitable for accidental corruption checks, not authentication, signatures or adversarial integrity. Do not describe a volatile ring as durable storage.

## 6. Lifecycle, supervision and recovery

A component lifecycle should expose explicit states such as COLD, INITIALIZING, READY, RUNNING, DEGRADED, STOPPING, STOPPED and FAULTED. Only valid transitions are accepted.

Recommended sequence:

1. validate the entire manifest and capability set before side effects;
2. initialize in declared dependency order;
3. record the stage that completed and its cleanup callback;
4. on failure, roll back in reverse order, including the failing stage when partial acquisition is possible;
5. preserve the original error and any cleanup errors;
6. permit restart only through an explicit finite retry budget;
7. declare recovery complete only after required health and progress checks pass.

A heartbeat means only that a caller reported progress. It does not certify correctness. A monitor reports; the application-level safety policy decides whether to shed load, stop, reset or request operator intervention. Hardware watchdogs, reset lines and safe outputs require board-level proof and verified actuator paths.

## 7. Declarative rules and extension isolation

Business and workflow rules should be represented as versioned, typed manifests or a documented DSL rather than hidden conditionals. Validate syntax, schema version, dependencies, capabilities, limits and invariants before execution. Keep the interpreter/runtime separate from policy definitions.

Extensions must receive only declared capabilities and narrow versioned data-transfer objects. A Python callback, thread boundary or naming convention is not a security sandbox. OS-level isolation requires a real process/container/VM boundary, OS-enforced filesystem and network policy, CPU/memory/process limits, cancellation, kill/reap semantics and adversarial tests.

Background work should use bounded queues, explicit deadlines, cancellation, backpressure and observable outcomes. Do not create unbounded workers or fire-and-forget tasks with no owner.

## 8. Distributed coordination

When components span machines, exchange versioned health and capability events asynchronously. Eventual consistency is acceptable only for fields whose staleness is explicitly tolerated. Use leases, sequence numbers, expiry and bounded anti-entropy; do not use a best-effort heartbeat as a replacement for quorum or transactional safety.

Peer isolation, routing changes and automatic bans belong to a separately reviewed network policy. The embedded libraries in this stack do not, by themselves, implement a distributed cluster or a gossip protocol.

## 9. Fault injection and verification

Use deterministic fault injection in host tests and controlled hardware-in-the-loop fixtures:

- callback failure at every initialization and shutdown stage;
- exhausted queue, memory and retry budgets;
- tick wraparound, clock stalls and deadline expiry;
- corrupted or out-of-order evidence records;
- unavailable capability, incomplete device evidence and stale heartbeat;
- worker cancellation, timeout and process termination;
- version mismatch, missing adapter and dependency cycle.

Never inject destructive faults into production hardware or energized equipment without a reviewed test plan, safe fixture and approved recovery path. A host test does not qualify a board port.

## 10. Repository-specific implementation status

| Repository | Implemented foundation | Integration work that remains separate |
|---|---|---|
| Klipot | Static operator portal, canonical-registry projection, module navigation, browser simulations and cross-repository manifest validator | Automated registry generation and live release-status synchronization remain separate roadmap work |
| SAMBU | Interpreter, AST, Python tooling, declared layer checks, deterministic sampling, bounded actors and policy/evidence primitives | Full static semantics, native compiler, enforced OS sandbox, production plugin ABI and external worker supervisor |
| ToolNG | Local C17/Win32 diagnostics, evidence scoring, bounded local reports and user-initiated exports | More UI accessibility, tested adapters and device-specific qualification |
| ReaperCripple | C11 runtime supervision, BSP family adapters, bounded telemetry, calibration and manufacturing callbacks | Exact board/fixture qualification, real MES transport integration and hardware-in-the-loop evidence |
| Kloz | C11 status ABI, caller-owned arena and versioned platform operations | Target ports, linker/startup validation, MMIO/DMA ordering and hardware qualification |
| CO | C11 lifecycle state machine, bounded poll step and cleanup after partial initialization | External scheduling policy, priority/deadline service and board-level watchdog adapter |
| SaintSI | C11 heartbeat registry, rollover-safe elapsed-time checks and CRC-32 | Windowed monitoring, event journal and separately reviewed watchdog/security adapters |
| NUN | Specification-only kernel architecture and capability-composition contracts | Kernel source, boot path, linker script, driver interfaces, host tests and target qualification |
| NUNLauncher | Specification-only image validation and boot handoff contract | Bootloader source, parser tests, signature verification, recovery flow and target qualification |

## 11. Autonomy, update propagation and rollback\n\nEach repository is an independently owned unit: it keeps its own source, toolchain, configuration, tests, release tags and rollback procedure. Cross-repository links are declared by versioned manifests and explicit adapters. An optional adapter may be absent without breaking the provider or consumer core. Required dependencies must remain acyclic and must be validated before side effects. Klipot is an operator-facing metadata plane, never a firmware runtime dependency.\n\nDependabot checks GitHub Actions weekly in all nine repositories and Python package dependencies in SAMBU. Updates are proposed as pull requests, and the ecosystem contract guard validates manifest identity, declared dependencies and update safety. Repositories with portable one-knob verification run that check in CI; ToolNG retains its native Windows validation path. Automatic merge and automatic installation are disabled.\n\nThis is automatic dependency-update proposal and CI infrastructure, not a claim that all products already contain an in-app updater or publish binary releases. When versioned application artifacts are available, installation must verify provenance, integrity/signature, supported platform and contract compatibility. Keep the previous known-good version available for rollback. Kernel, bootloader and firmware updates additionally require a target-specific recovery path and explicit operator approval; unattended flashing and boot-chain replacement are prohibited.\n\nNUN and NUNLauncher are specification-only today. Their manifests register intended boundaries and compatibility, not executable features or target support.\n\n## 12. Release gates

A cross-repository release is ready only when:

- every changed public contract has a version and migration note;
- dependency direction is acyclic and machine-checked where possible;
- resource ceilings and failure behavior have positive and negative tests;
- all code examples compile or are explicitly labelled pseudocode;
- host tests pass and target-specific tests are reported separately;
- no roadmap item is presented as implemented;
- security, hardware and operator-facing claims match measured evidence.

**Core rule:** compose through explicit contracts, constrain every resource, preserve evidence, recover within finite budgets and leave consequential authority with the responsible application or operator.
