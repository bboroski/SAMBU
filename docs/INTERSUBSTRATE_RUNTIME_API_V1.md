# Cross-substrate runtime and ecosystem API v1

**Status:** reference contract and limited host implementation  
**Canonical owner:** SAMBU  
**Applies to:** the independently versioned repositories in the connected engineering ecosystem  
**Version:** 1.0.0

## 1. Purpose

This contract turns the requested runtime topics into implementable, testable boundaries: synchronization, event transport, resource descriptors, memory ownership, execution isolation, observability, integrity, and lifecycle. It extends the existing SAMBU module-manifest and ecosystem-integration contracts; it does not replace them.

The ecosystem remains federated. Each repository owns its source, ABI, tests, release cadence, and security boundary. Shared contracts are negotiated at integration boundaries; they do not imply that every module is linked into one executable, that all modules use the same runtime, or that a registry entry grants access to another repository.

The initial host reference implementation is `sambu/ecosystem_runtime.py`. It implements strict validation and canonical JSON serialization for event envelopes and resource descriptors, plus a bounded, thread-safe, in-process queue. It is not a network broker, RPC service, OS scheduler, container runtime, driver framework, or security authority.

## 2. Contract principles

1. **Explicit versions:** every message and descriptor carries `schema_version`; incompatible semantics require a major-version change.
2. **Stable identity:** messages, traces, resources, and modules use stable IDs. Human-readable names are labels, not keys.
3. **Bounded resources:** payloads, queues, metadata, retries, and resource tables have limits and defined overflow behavior.
4. **No silent loss:** a full queue rejects publication; the producer must retry, persist, or report backpressure according to its own policy.
5. **Ownership before access:** descriptors declare owner, lifetime, state, and rights. A descriptor is not a pointer, a capability grant, or proof that a device exists.
6. **No implicit side effects:** discovery and validation are read-only. Hardware writes, process execution, network transmission, and privilege changes require explicit platform adapters and authorization.
7. **Provenance and evidence:** every operational claim records its source, observed time, version, validation stage, and evidence. A mock or simulation is not target evidence.
8. **Portable core, optional adapters:** hardware registers, interrupts, OS syscalls, cloud queues, databases, and BCI interfaces stay behind target-specific adapters.
9. **Deterministic failure:** invalid, stale, unsupported, full, or unauthorized operations produce typed errors instead of guessing or coercing.
10. **Fail closed:** unknown capability, principal, schema, algorithm, or target is denied by default.

## 3. Event envelope

The canonical control-plane message is JSON in UTF-8. It is a metadata/control transport, not a binary ABI and not a high-rate telemetry codec.

Required fields:

| Field | Meaning |
|---|---|
| `schema_version` | Exact envelope schema version; initially `1.0.0` |
| `message_id` | Canonical UUID identifying this message |
| `producer.module_id` | Stable module ID from the ecosystem registry |
| `producer.version` | Producer build or release version |
| `event_type` | Lowercase dotted event name, e.g. `runtime.resource.changed` |
| `sequence` | Non-negative producer-local sequence number |
| `occurred_at` | RFC 3339 timestamp including UTC offset |
| `payload` | JSON object validated by the event-specific schema |

Optional `trace` fields carry `correlation_id` and `causation_id`. These are identifiers only; a trace ID does not create distributed tracing until adapters propagate it across actual service boundaries.

Credentials, bearer tokens, private keys, raw neural signals, secrets, and device-private content MUST NOT be embedded in an event payload. Authentication context is established by the receiving transport adapter and is not inferred from producer-supplied JSON.

Canonical serialization uses UTF-8, sorted object keys, compact separators, and rejects NaN/Infinity. The reference implementation limits an encoded envelope to 256 KiB. A high-rate or binary channel must define a separate versioned codec and conformance vectors; do not serialize a native C structure by copying its in-memory bytes.

## 4. Resource descriptor

A resource descriptor is a portable declaration of a resource, not the resource itself. It records:

- stable `resource_id` and `resource_type`;
- `owner_module_id`;
- lifetime: `call`, `session`, `process`, `persistent`, or `device`;
- state: `declared`, `ready`, `busy`, `degraded`, `released`, or `faulted`;
- explicit rights: `observe`, `read`, `write`, `execute`, and/or `configure`;
- optional size and power-of-two alignment;
- declared capabilities and bounded metadata.

Descriptors MUST NOT contain raw pointers, physical addresses, MMIO addresses, credentials, or implicit ownership transfer. Memory handles, file descriptors, DMA mappings, device handles, and process IDs are meaningful only inside their owning adapter and lifetime.

## 5. Synchronization, bus, and delivery semantics

The reference bus is deliberately local and bounded. It serializes and validates before acquiring its queue lock, then atomically appends one complete encoded message. If capacity is exhausted, publication returns `False` and does not overwrite earlier events. Receive is FIFO. The lock protects only the queue; callbacks and I/O must never execute while it is held.

Distributed delivery is a later adapter contract. A network transport must specify acknowledgement, retry budget, idempotency, ordering scope, duplicate handling, timeouts, congestion/backpressure, and shutdown semantics. Exactly-once delivery is not claimed; the default target is at-least-once transport plus idempotent consumers, or best-effort telemetry where explicitly declared.

For embedded C interfaces, use fixed-width fields, explicit structure size and ABI version, caller-owned buffers, documented alignment, and defined error codes. Wire encoding must specify byte order and field widths. Do not transmit a C struct's padding or pointer values.

## 6. Security, integrity, and audit

- Authentication identifies the caller at the transport boundary; authorization checks a capability and a resource right for each operation.
- Role names are policy inputs, not secrets. The receiver evaluates roles against a versioned policy.
- A token is short-lived, scoped, audience-bound, and stored outside the event payload. The reference library does not issue or verify credentials.
- End-to-end encryption belongs to a real transport adapter with an explicit key-management and rotation policy. The local JSON queue is not encrypted.
- SHA-256 may identify an artifact or detect content changes. A digest alone does not prove publisher identity or authorization.
- CRC is for accidental corruption detection, not cryptographic authenticity.
- Audit records are append-oriented and include actor, action, resource, decision, timestamp, correlation ID, and evidence reference. Redact secrets and personal data.
- Unknown principal, unknown role, revoked capability, invalid signature, and untrusted origin fail closed.

## 7. Memory, processes, and hardware

Virtual memory, page tables, process isolation, containers, syscalls, preemption, interrupt controllers, DMA, MMIO, and drivers are operating-system or board responsibilities. They cannot be emulated by a JSON descriptor or a documentation-only module.

NUN owns kernel address-space, process, syscall, exception, and interrupt implementation. Kloz owns portable fixed-capacity memory and platform-operation contracts. ReaperCripple owns board-specific BSP and manufacturing/fixture adapters. CO remains a deterministic lifecycle component, not an RTOS or scheduler. NUNLauncher validates images before handoff; it does not execute them.

For any hardware operation record target CPU/SoC, package, board revision, toolchain, ABI, linker/startup files, memory map, fixture/calibration, and target evidence. Host tests are a prerequisite, not a substitute for emulator or physical qualification.

## 8. Observability and performance

Every actual cross-module request should preserve message ID, correlation ID, producer version, start/end time, outcome, and bounded diagnostic context. Metrics should distinguish count, duration, queue depth, rejected publications, retries, and resource exhaustion. Latency and throughput claims require named workloads, target hardware, repetitions, percentile method, and raw results.

Cache policy, load balancing, horizontal/vertical scaling, database replication/sharding/indexing, and query optimization are service-specific concerns. They are not enabled by publishing an event contract. Use them only where a repository actually owns a database or deployed service.

## 9. Requested feature catalogue: 50 controls

| # | Requested capability | Contract / implementation boundary |
|---:|---|---|
| 1 | Synchronization protocols | Versioned ordering, sequence, acknowledgement, timeout, and backpressure policy per adapter |
| 2 | Data bus | Bounded local reference queue now; distributed broker is adapter work |
| 3 | Resource descriptors | JSON descriptor schema and strict host validator |
| 4 | Virtual memory | NUN kernel responsibility; not supplied by this control-plane library |
| 5 | Process containers | OS/runtime isolation; planned only where process model exists |
| 6 | Microservices | Optional deployment topology, never a dependency of bare-metal modules |
| 7 | Node orchestration | Klipot/Hellduck/Luci registry and planning boundary; no runtime cluster scheduler claim |
| 8 | Response latency | Measure per target and workload; no unmeasured SLA |
| 9 | Channel throughput | Measure bytes/events per second with payload and loss policy |
| 10 | State caching | Explicit TTL, invalidation, owner, and stale-state behavior required |
| 11 | Stream serialization | Canonical bounded JSON reference codec; binary codecs require separate versions |
| 12 | Packet deserialization | Strict UTF-8/JSON decode and schema validation in reference library |
| 13 | Binary interfaces | Fixed-width C ABI, struct-size/version checks; never dump native struct memory |
| 14 | Syscalls | NUN kernel API, only when implemented and tested |
| 15 | Hardware interrupts | NUN interrupt path and board ports; no generic cross-platform IRQ abstraction claim |
| 16 | Device drivers | ReaperCripple BSP and future NUN drivers, gated by target evidence |
| 17 | Layer abstraction | Separate domain, contract, adapter, transport, and hardware layers |
| 18 | Logic encapsulation | Module-owned state and explicit public interfaces |
| 19 | Object polymorphism | Language/runtime-local feature; does not imply cross-language ABI compatibility |
| 20 | Inheritance | Language-specific semantics; versioned interfaces preferred at module boundaries |
| 21 | Type reflection | Explicit schema/type metadata; runtime reflection remains language-specific |
| 22 | Structure metadata | Manifests, schemas, build IDs, source and evidence provenance |
| 23 | Block hashing | Digest content and artifacts; SHA-256 is not a signature |
| 24 | End-to-end encryption | Not implemented by reference queue; transport/key-management adapter required |
| 25 | Token authentication | Not implemented by reference queue; scoped token verifier required at boundary |
| 26 | Access authorization | Default-deny capability and resource-right checks at adapter boundary |
| 27 | Role-based permissions | Policy-layer mapping; roles never replace resource-level checks |
| 28 | Action audit | Append-oriented event contract; repository must provide durable storage |
| 29 | Event logging | Bounded and redacted local event reporting; retention is repository-specific |
| 30 | Request tracing | Correlation/causation IDs in envelope; propagation adapters still required |
| 31 | Metrics monitoring | Queue and operation counters; target measurements remain to be added |
| 32 | Load balancing | Service deployment concern, not a property of the event schema |
| 33 | Horizontal scaling | Stateless service/partition design where applicable; not for bare-metal cores |
| 34 | Vertical scaling | Resource/target sizing with measured budgets |
| 35 | Cluster fault tolerance | Local fault reporting exists in some modules; cluster failover is not implemented |
| 36 | Channel redundancy | Transport adapter design: primary/secondary path, health and failover evidence |
| 37 | Database replication | Not applicable unless a repository owns a persistent database |
| 38 | Data sharding | Partition keys and ownership required; not currently enabled by the contract |
| 39 | Field indexing | Database-specific; registry indexes remain local to their owners |
| 40 | Query optimization | Query plans and fixed workload benchmarks required where a database exists |
| 41 | JIT compilation | Not implemented by this API; SAMBU compiler/runtime work is separate |
| 42 | Bytecode interpretation | SAMBU interpreter is an existing language capability; cross-module bytecode ABI is not implied |
| 43 | Garbage collection | No cross-repository GC contract; use explicit ownership in C and host-runtime semantics in Python |
| 44 | Memory management | Kloz caller-owned arena and NUN early allocator are existing, separate mechanisms |
| 45 | Resource leaks | Add bounded lifetime tests, cleanup-path tests, and target instrumentation per module |
| 46 | Thread locks | Local queue uses a narrow lock; CO callers remain responsible for external serialization |
| 47 | Deadlocks | No general deadlock detector; lock ordering and bounded callbacks are required |
| 48 | Data races | Protected local queue; each shared-memory/interrupt path needs its own race analysis |
| 49 | Atomic operations | Queue enqueue is atomic within its lock; target atomics require ABI/ISA qualification |
| 50 | Transactional integrity | Publish is all-or-nothing for one message; multi-resource transactions require an explicit coordinator |

## 10. Substrate evolution research model

The SEGA lineage is used as an engineering analogy, not as proof of direct historical equivalence. System 16 illustrates split responsibilities across CPUs and shared memory; Genesis add-ons illustrate the cost of heterogeneous buses and ownership; Saturn illustrates why parallel hardware needs tooling, synchronization and a coherent abstraction; Dreamcast illustrates networked application surfaces. The useful design lesson is to specify ownership, ABI, synchronization, and tooling before multiplying execution engines.

The Internet-Dust concept from *Metropolitan* is treated as speculative fiction and a simulation domain. Charged particles, dipole polarization, Brownian motion, electromagnetic fields and turbulent flow can inspire a multi-agent field simulator, but the equations do not establish a practical data network, quantum computer, antenna, or brain interface. A future simulator may exchange bounded state snapshots over the same event contract; it must label synthetic state, numerical assumptions, solver limits and physical validation status. Quantum entanglement does not provide instantaneous controllable communication, and no neural injection or memory-write capability is claimed.

A trans-substrate adapter may eventually translate semantic state between software runtimes or validated BCI devices. It must be opt-in, consent-based, isolated, auditable, reversible where technically possible, and backed by clinical/device-specific safety evidence. Until then, `biological`, `dust-field`, and `quantum` are research-domain labels only.

## 11. Acceptance gates

- [ ] Schema fixtures cover valid, missing, unknown-version, malformed-ID, stale, and oversized input.
- [ ] Event queue tests cover FIFO, capacity rejection, and concurrent producer/consumer operation.
- [ ] Resource descriptor tests cover ownership, invalid rights, size, alignment, and release state.
- [ ] Each repository has a local profile naming owned features, adapters, non-goals, and acceptance tests.
- [ ] CI runs host tests; target projects separately record cross-build, emulator, and hardware evidence.
- [ ] Security claims identify the actual transport, key management, principal, and policy.
- [ ] Performance claims include reproducible measurements.
- [ ] Merge occurs only after an independently reviewed PR and passing required checks.

**Implementation status:** the envelope, descriptor, serializer/deserializer, and bounded local queue are the initial host reference. All other capabilities retain the maturity and target constraints described above until code and evidence exist.
