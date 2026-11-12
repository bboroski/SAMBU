# Object Design and Component Architecture Standard

**Standard ID:** OOD-2026.11  
**Version:** 1.0.0  
**Applies to:** SAMBU  
**Status:** Proposed in this pull request; effective after review and merge  
**Basis:** Modern, language-neutral adaptation of the object-design principles in Bruce Eckel's *Thinking in Java* (especially the concepts introduced across chapters 1–17).

> This is not a Java migration and does not require an object-oriented architecture in every subsystem. It establishes design tests for responsibility, boundaries, ownership, substitutability and reliability. The repository's product brief, platform constraints, native ABI, security policy and existing architecture take precedence over superficial uniformity.

## 1. Design objective

Build software from small, cohesive components that expose intentional contracts and hide replaceable implementation details. A component exists to provide a clearly named service to its collaborators. Its public contract must be smaller and more stable than its implementation.

The purpose is not to maximize classes, interfaces or abstraction layers. Use the simplest model that makes the domain, ownership and failure behavior explicit.

## 2. Core design rules

1. **Model the problem domain.** Name modules and types after real responsibilities. Keep parsing, policy, orchestration, persistence, presentation and platform access separate when they change for different reasons.
2. **Define a narrow interface.** Public APIs describe supported operations, inputs, outputs, invariants and failure modes. Internal state and implementation details remain private unless exposure is an intentional compatibility commitment.
3. **Prefer cohesion and low coupling.** A component should have one clear reason to change. Depend on the smallest contract needed; avoid circular imports, hidden global state and broad manager objects.
4. **Prefer composition over inheritance.** Assemble behavior from owned collaborators, data and adapters. Use inheritance only for a genuine substitutable subtype, not merely to reuse code or share fields.
5. **Enforce substitutability.** A subtype must preserve the documented preconditions, postconditions, invariants and error semantics of its base contract. It must not strengthen caller obligations, weaken guarantees or surprise callers with hidden side effects.
6. **Use polymorphism at real variation points.** Prefer protocols, interfaces, traits, function tables or adapters where implementations must be interchangeable. Avoid repeated type switches and unsafe downcasts as the normal extension mechanism.
7. **Preserve type information.** Use generics, tagged unions, enums, validated schemas and explicit result types at boundaries. Avoid untyped containers, Any/void-pointer escape hatches and stringly typed state unless a narrow, documented boundary requires them.
8. **Make state transitions explicit.** Define valid states, allowed transitions, ownership of mutation and recovery behavior. Prefer immutable values for observations, messages and cross-module contracts.
9. **Make failures first-class.** Distinguish invalid input, unavailable capability, permission denial, timeout, resource exhaustion, corruption and internal fault. Do not swallow errors, return ambiguous sentinels or convert unknown state into success.
10. **Choose collections by semantics.** Select a list, map, set, queue, ring buffer or fixed-capacity table according to ordering, uniqueness, bounds and measured operation cost. Document capacity and complexity where they are part of the contract.

## 3. Resource lifetime and ownership

- Every resource has an identifiable owner and a documented lifetime.
- Prefer deterministic cleanup: RAII/scope guards in C++, structured ownership in Swift, context managers in Python, and explicit acquire/release contracts in C and other low-level code.
- Do not rely on finalizers or garbage-collection timing for correctness, locks, files, device handles, memory-mapped regions or shutdown.
- Define allocation policy, alignment, maximum size, failure behavior and cleanup responsibility. In constrained systems, prefer caller-owned buffers and bounded storage where appropriate.
- Never expose an internal mutable buffer beyond its valid lifetime. Copy, borrow or transfer ownership explicitly.

## 4. Concurrency and asynchronous work

- Document which execution context owns mutable state.
- Prefer immutable messages, single-owner state machines, actors or bounded queues before introducing shared mutable state.
- Every lock has a narrow scope and a documented lock order; never call unknown callbacks while holding internal locks.
- Define cancellation, deadlines, shutdown and back-pressure. Do not create unbounded queues or detached background work without an explicit lifecycle.
- Test races, re-entrancy, timeout and shutdown behavior where concurrency exists. A thread-safe label requires evidence.

## 5. Language and platform adaptation

Apply the intent using the native idioms of the repository:

- **C:** opaque structs, const boundaries, explicit ownership, status enums, caller-provided storage and documented function-table contracts.
- **C++:** RAII, value semantics, smart ownership, narrow interfaces and explicit exception guarantees; avoid deep inheritance and naked ownership.
- **Swift:** value types and protocols where appropriate, explicit actor/isolation boundaries, structured concurrency and deterministic resource scopes.
- **Python:** small modules, validated data models, Protocol/ABC at real extension points, context managers and explicit exception contracts.
- **Java/Kotlin:** interfaces, generics, immutable data where practical, structured resource handling and explicit concurrency contracts.
- **JavaScript/TypeScript:** module boundaries, schema validation, discriminated unions and explicit async cancellation/error handling.
- **Kernel, firmware and bare metal:** do not introduce runtime facilities forbidden by the target. Use explicit ABI, fixed-capacity data, caller-owned memory, bounded execution and interrupt-context rules.

The age of a language feature or example in the source book is not a reason to adopt it. Use currently supported idioms and the project's documented toolchain.

## 6. Contracts and integration

- Treat each public module boundary as a versioned contract when independently released or consumed.
- Validate all external data, manifests, serialized records and hardware observations at ingress.
- Keep adapters at system boundaries; domain logic must not depend on a concrete OS, UI toolkit, device, database or external repository.
- Define compatibility policy, deprecation path and migration notes for breaking changes.
- No cross-repository source import, execution or implicit shared state. Integrate through reviewed interfaces and versioned data contracts.

## 7. Verification requirements

For a material design or behavior change, provide applicable evidence for:

- contract tests for public inputs, outputs and failure modes;
- positive, negative, boundary and regression cases;
- ownership, cleanup and resource-exhaustion behavior;
- concurrency, timeout and shutdown behavior where applicable;
- ABI/schema compatibility where applicable;
- target-specific qualification separately from host tests, emulators and static analysis;
- measured performance evidence before complexity is introduced for speed.

Document any check that is not applicable or could not be run. Never claim hardware, security, performance or production qualification without evidence that directly supports the claim.

## 8. Anti-patterns to reject

- giant classes or modules with unrelated responsibilities;
- deep inheritance used only for code reuse;
- base classes that expose mutable implementation state;
- public mutable fields without a contract;
- repeated type switches, unchecked casts or unvalidated data at module boundaries;
- cyclic dependencies, hidden service locators and implicit global singletons;
- unbounded work queues, detached tasks and undocumented lock ordering;
- silent exception suppression, ambiguous status codes or false success;
- abstraction layers with no independent responsibility or test value.

## 9. Pull request design checklist

- [ ] The changed component has a single, explainable responsibility.
- [ ] Public contract and private implementation are clearly separated.
- [ ] Composition was considered before inheritance; substitutability is demonstrated if inheritance is used.
- [ ] Types, state transitions, ownership and failure cases are explicit.
- [ ] Resource cleanup and concurrency behavior are bounded and testable.
- [ ] Existing APIs, ABI, schemas and product constraints remain compatible or have a migration plan.
- [ ] Native checks and relevant tests were run; results and limitations are stated.
- [ ] Documentation and examples reflect actual implementation status.

## 10. Repository-specific architecture adapter

Preserve SAMBU's Python-hosted language/runtime, lexer/parser, AST, evaluator, CLI, IDE and separately scoped C/Rust/Swift adapters. Model syntax and semantics with explicit typed nodes; keep parser, runtime, tooling and integrations behind stable contracts. Prefer Protocol/ABC or callable adapter contracts only where substitution is demonstrated. Scientific quantities, dimensions, reproducible sampling and plugin manifests remain explicit domain invariants.

This adapter is a preservation boundary, not a replacement architecture. Any exception to this standard must name the affected subsystem, explain the constraint, identify compensating tests and receive review in the relevant pull request.
