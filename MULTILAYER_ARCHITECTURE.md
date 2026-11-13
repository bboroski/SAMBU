# Multi-Axis Layer Architecture

**Architecture:** NUN Mesh — Multi-Axis Layer Fabric (MALF)  
**Repository:** `bboroski/SAMBU`  
**Role:** Scientific modeling, language engineering and automation environment  
**Architecture status:** Target boundary contract; implementation status remains evidence-based.  
**Maturity:** Experimental alpha; Python-hosted workflow with a partial native compiler slice.

## Purpose

This document defines how this repository can grow in depth without turning into a dependency tangle. “Layering” means more than folders: it combines structural layers, vertical feature slices, trust boundaries, lifecycle stages and independent operational/assurance planes. Existing source layout is not to be moved merely to match this document.

## 1. Structural layers

| ID | Layer | Responsibility |
|---|---|---|
| L0 | **Experience** | CLI, GUI, portal, operator workflows; no business rules here. |
| L1 | **Interface contracts** | Public APIs, commands, schemas, ABI, events and versioned message formats. |
| L2 | **Application orchestration** | Use cases, workflows, sequencing, retries and transaction boundaries. |
| L3 | **Domain kernel** | Core models, invariants, algorithms and deterministic business logic. |
| L4 | **Policy and capability** | Authorization, safety gates, resource limits, maturity and allowed-operation policy. |
| L5 | **Ports and contracts** | Abstract clocks, storage, device, network, filesystem, compiler and platform interfaces. |
| L6 | **Adapters and platform** | Concrete OS, board, browser, hardware, protocol and external-service implementations. |
| L7 | **State and data** | Schemas, registries, persistence, caches, artifacts, migrations and provenance. |
| L8 | **Runtime and delivery** | Processes, boot, packaging, deployment, build graph, configuration and operational lifecycle. |
| L9 | **Assurance and evidence** | Unit/integration/system tests, static analysis, benchmarks, logs, attestations and qualification evidence. |

Layers are logical boundaries, not mandatory directory names. A small library may collapse several layers into a few files; a larger application may split one layer into multiple modules.

## 2. Dependency direction

- Experience (L0) calls application use cases (L2) through stable interfaces (L1); it never owns domain rules.
- Application orchestration (L2) coordinates domain logic (L3) and policies (L4) through ports (L5).
- Concrete adapters (L6) implement ports; the domain must not import an OS, GUI, vendor SDK or device driver.
- State (L7) is accessed through ports and repositories; schemas and migrations are versioned.
- Runtime/delivery (L8) composes implementations. It may depend on inner layers, never the reverse.
- Assurance (L9) verifies public behavior and boundaries; tests must not be the only place where a capability is implemented.

**Allowed flow:** outer surface → application → domain/policy → port → adapter/platform.  
**Forbidden flow:** domain → GUI/OS/vendor adapter; adapter → hidden global state; cross-repository direct source inclusion without a versioned contract.

## 3. Five orthogonal axes

1. **Structural axis:** L0–L9 above.
2. **Vertical-slice axis:** each feature travels through only the layers it needs, from entry point to domain action, adapter, persisted result and tests.
3. **Trust axis:** untrusted input → parse/normalize → validate → policy/capability decision → explicitly authorized effect → auditable result. No layer may silently skip a gate.
4. **Lifecycle axis:** design → configure → build → verify → package → deploy/boot → operate → recover/rollback → retire. Each transition has an owner and evidence.
5. **Observability axis:** events, diagnostics, metrics and provenance are emitted at boundaries; telemetry is bounded, privacy-aware and never treated as proof beyond what it actually observes.

## 4. Repository-specific layer placement

### L0 — Developer experience
CLI, Tkinter IDE, Studio, examples and workflow entry points. Keep interface state and presentation separate from language semantics.

### L1 — Language and tool contracts
Lexer/parser entry points, AST/IR schemas, module manifest, plugin/adapter descriptors and stable CLI command contracts.

### L2 — Use-case orchestration
Project loading, check/run/test workflows, tool invocation and compiler pipeline coordination.

### L3 — Language and scientific domain
Syntax, symbols/scopes, types, semantics, units/dimensions, constants, spatial models and deterministic transformations.

### L4 — Execution and capability policy
Explicit rules for imports, filesystem, processes, devices, network and resource limits. Unknown origins or effects remain denied until an implemented gate says otherwise.

### L5 — Compiler/runtime ports
Typed interfaces for source input, diagnostics, module resolution, filesystem and target code generation.

### L6 — Backend and host adapters
Python host adapter, optional native backend, platform-specific toolchains and IDE adapters. Keep native compilation claims scoped to the currently implemented slice.

### L7 — Project and artifact data
Versioned modules, schemas, examples, scientific datasets, compiler artifacts and reproducible workflow metadata.

### L8 — Runtime and packaging
Python packaging, command-line launch, native build configuration and platform packaging; do not imply a complete native source-to-machine-code path.

### L9 — Language and compiler verification
Parser/semantic tests, conformance fixtures, dimensional correctness, deterministic output, backend tests and architecture boundary checks.


## 5. Vertical slices to preserve

1. **Source → static check:** CLI/IDE input → parser contract → AST and semantic domain → diagnostic policy → evidence-rich report.
2. **Source → compiler artifact:** Source → typed IR → validated lowering → backend adapter → artifact; unsupported stages must fail explicitly, never fabricate completion.
3. **Scientific workflow:** Versioned model input → dimensional validation → deterministic calculation/sampling → persisted result and reproducibility metadata.

## 6. Cross-cutting planes

- **Security and trust:** least privilege, explicit consent, input validation, secret hygiene, safe defaults and explicit denial of unsupported operations.
- **Reliability:** bounded memory/time/work, deterministic failure states, cancellation and rollback where meaningful.
- **Compatibility:** version public API/ABI, schemas, manifests and persisted data; reject unsupported versions clearly.
- **Observability:** structured, redacted diagnostics with source and confidence; avoid claiming that a recommendation or simulation equals an executed action.
- **Accessibility and usability:** relevant to user-facing surfaces; keyboard operation, clear errors and reduced-motion support where applicable.
- **Performance:** benchmark the real target path; optimize only after correctness and target constraints are measured.

## 7. Integration with the NUN Mesh

Repositories remain independently buildable and releasable. Cross-project links are **contracts**, not implicit runtime dependencies. Every integration must state provider, consumer, contract/version, optionality, failure behavior, security boundary and verification evidence. A manifest entry, adapter-ready label or architecture diagram does not prove runtime integration.

## 8. Incremental implementation sequence

1. Map existing source files and public APIs to L0–L9 without relocating code.
2. Identify cycles, hidden globals, cross-layer calls and unguarded side effects.
3. Introduce or tighten L1/L5 contracts before changing implementations.
4. Extract deterministic domain behavior (L3) from UI, OS and platform code.
5. Gate effects through L4; put concrete integrations behind L6 adapters.
6. Version L7 schemas and L8 build/runtime composition.
7. Add L9 tests for allowed dependencies, failures, limits and target-specific evidence.
8. Refactor one vertical slice at a time; retain compatibility shims only with a removal plan.

## 9. Definition of done

A change is complete only when its owning layer is clear; dependencies point inward; contracts are versioned; failure and authorization behavior are tested; evidence matches the claimed maturity; and documentation distinguishes **implemented**, **partial**, **planned** and **not verified**.

## Repository-specific guardrails

Do not label SAMBU a complete native compiler, universal sandbox, operating system or unrestricted automation runtime. A declaration, preview or planned backend is not evidence of execution. Keep host process/device/network access behind explicit adapters and authorization.
