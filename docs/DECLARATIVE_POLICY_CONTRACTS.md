# SAMBU declarative policy contracts for NUN

SAMBU is the policy-authoring and language layer in the NUN ecosystem. Its role is to express reviewed workflow intent and export versioned declarations. It is not the authority for hardware limits, operating-system permissions or production approvals.

## Policy pipeline

A policy intended for another repository should pass through these stages:

1. **Author** — write a declarative workflow using the SAMBU language or a documented schema-backed format.
2. **Parse** — produce an AST with source spans so validation errors can point to the exact source location.
3. **Validate** — check names, types, bounded iteration, required capabilities, input ranges and allowed operations.
4. **Normalize** — serialize a stable, versioned policy artifact without executable Python objects or hidden ambient authority.
5. **Preflight** — let Klipot verify the component graph and required capability providers.
6. **Bind** — let the consuming repository map policy operations to its own reviewed adapter functions.
7. **Audit** — record policy version, input profile, result and evidence references.

The current SAMBU interpreter, CLI, workflow and Machine APIs provide only selected pieces of this path. A production-ready NUN policy compiler/exporter and complete static effect system are not claimed as implemented here.

## DSL semantics and domain clarity

A DSL is useful when it reduces accidental complexity and makes domain rules explicit. It should not hide behavior behind puzzles or undocumented conventions. Names, source spans, error messages and documentation must expose the rule being applied.

Use:
- explicit input and output types;
- bounded loops and bounded collections;
- declared capabilities and side effects;
- deterministic rule ordering;
- schema-versioned output;
- fixtures for valid, invalid and boundary inputs.

Never treat a manifest or user-authored policy as trusted executable code.

## Resource budgets and hard ceilings

A policy may declare the maximum resources it requests: memory bytes, queue slots and caller-defined work units. The target runtime decides whether the request fits its approved profile. An emergency policy may omit optional work but may not enlarge the board's memory, current, voltage, clock or thermal limits.

A declarative resource request does not enforce itself. Kloz provides fixed-capacity accounting; ReaperCripple remains responsible for board-specific electrical and production constraints.

## Replication consistency and fencing

Policies are immutable artifacts identified by version or digest. Distribution of a policy may be asynchronous, but each node must state which version it has admitted. Eventual consistency is acceptable for non-critical policy catalogs; it is not acceptable for an unresolved firmware or actuator policy revision.

Where multiple controllers can act on one target, policy admission must be coupled to the target's authoritative epoch/fencing mechanism. A stale policy holder must not continue destructive work.

## Reproducible inputs and event traces

Record the policy version, schema version, relevant input hashes, deterministic seed where applicable, and decision result. Use checkpoints only when their schema and provenance are retained. Log rotation and retention remain explicit; append-only does not mean infinite storage or automatic immutability.

The same policy version and same declared inputs should produce the same plan unless the policy explicitly declares nondeterminism. Hardware measurements, wall-clock time and external services must be explicit inputs rather than hidden globals.

## Execution isolation and sandbox boundaries

SAMBU's in-process restricted execution modes are not OS process isolation. A policy evaluator must still enforce operation allow-lists, memory and iteration bounds. A host that loads an untrusted extension must execute it out of process or in a reviewed VM/WASM sandbox with explicit I/O permissions and resource quotas.

SAMBU actor/mailbox experiments are bounded runtime primitives; they do not imply native parallel execution or an independently scheduled daemon. On bare-metal integrations, work should be split into cooperative bounded steps and driven by the owning runtime.

## Contract hand-off

Klipot maintains the cross-repository schemas:
- `nun.ecosystem.v1` — component graph and declared dependencies;
- `nun.capability.v1` — component provides/requires and execution boundary;
- resource profile — hard ceilings and overflow semantics;
- `nun.event.v1` — producer, sequence, monotonic time, severity and data classification.

ToolNG and ReaperCripple own the final interpretation of a policy in their domains. SAMBU must not bypass their local safety checks. Until a schema-backed exporter and consumer adapter are implemented and tested, the relationship is a documented integration target, not a runtime dependency.
