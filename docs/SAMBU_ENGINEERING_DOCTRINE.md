# SAMBU Engineering Doctrine, Machine and IDE

**Baseline:** SAMBU 0.11.0  
**Status:** Machine and headless IDE services are implemented as experimental Python APIs and CLI commands. This doctrine is the design contract; graphical editor, LSP transport, static type analysis and privileged host/device execution remain roadmap items.

This document turns eight user-supplied concepts into implementable engineering rules. Character archetypes are design metaphors, not copied lore or claims about canon.

## 1. The SAMBU five-letter engineering code

SAMBU retains its historical scientific expansion. This is a second, engineering interpretation:

| Letter | Engineering law | Core question | Main mechanism |
|---|---|---|---|
| **S** | **Safety and staged sovereignty** | What is this component allowed to do? | Capability profiles, bounded inputs, explicit trust boundaries |
| **A** | **Adaptive exploration** | What can be learned safely and cheaply? | Hypothesis-driven experiments, deterministic 1:100 AST sampling |
| **M** | **Managed recovery and memory** | How are failures contained and remembered? | Actors, supervisors, bounded ten-thousand-entry Ghost Ledger |
| **B** | **Branchable, board-layered design** | Can one layer evolve without destabilizing the whole? | Plywood layering, explicit contracts, dependency graph, reversible changes |
| **U** | **Unforced interoperability and user sovereignty** | Can users integrate, leave, fork and upgrade without coercion? | Stable interfaces, adapters, compatibility tests and migration records |

The letters define a closed engineering loop:

`S` constrains an experiment → `A` selects evidence → `M` records outcomes → `B` isolates and validates a change → `U` preserves compatibility and user choice → the next cycle begins with better evidence.

## 2. Character-inspired engineering patterns

The supplied character set is converted into six non-literal engineering patterns:

### Alucard — controlled release of capability

The metaphor of restriction levels becomes least-privilege profiles. A component receives only the operations it needs. Increasing privilege requires an explicit profile change and must not happen because code asks for it.

Current `MachineProfile` levels:

| Profile | Level | Granted work |
|---|---:|---|
| `sealed` | 0 | Workspace parsing, deterministic sampling and architecture inspection |
| `sandbox` | 1 | Level 0 plus execution in the restricted SAMBU interpreter |
| `host` | 2 | Reservation for a future host-adapter boundary |
| `device` | 3 | Reservation for a future device-adapter boundary |

The `host` and `device` levels are reservation points, not implementations of shell execution, network access, GPIO, MMIO or HSM access. A profile name never grants a capability that lacks an implemented adapter. Unknown profiles fail closed.

### Ging Freecss — exploration with receipts

A research-oriented toolchain should make it easy to inspect unfamiliar code, test a hypothesis, branch an experiment and keep the discovery even when the experiment fails. The 1:100 sampler provides a repeatable sample of typed AST statements. It does not randomly rewrite code or silently alter project files.

Every sample carries path, source range, node kind and a SHA-256 fingerprint. The seed and ratio are recorded so another developer can reproduce the same sample against the same source snapshot.

### Raijin — accountable supervision

The supervisor tree is the operational authority for actors. Failure is contained within a named boundary, restarts are limited by a rolling budget, and exhausted budgets escalate to a parent. Each recovery action is inspectable. No process is declared healthy merely because it restarted.

### Djinn — hidden capability boundaries

Extensions, plugins and host callbacks are untrusted until a host has declared and validated what they may access. SAMBU should avoid ambient authority: a module must not receive filesystem, process, network or hardware power simply because it was imported.

The current profiles provide a conservative permission vocabulary. A future plugin sandbox requires OS-level isolation, resource limits, signed provenance and an explicit IPC contract; a Python callback alone is not a sandbox.

### Uchiha Madara — reject the all-controlling monolith

The language must not force one global implementation, one mutable global state or one mandatory deployment shape. Keep layers replaceable, permit independent backends and forks, and use reversible migrations. A central coordinator may report and validate; it must not silently rewrite every project or override local policy.

### Shanks — compatibility as diplomacy

A strong ecosystem keeps protocols stable enough for independent tools to cooperate. Prefer adapters and versioned contracts over hard-coded provider assumptions. Breaking changes require a migration guide, deprecation interval and compatibility tests. Users retain the ability to export their source, evidence and project data.

## 3. Plywood design — a laminated architecture

“Plywood design” means build SAMBU from thin, replaceable layers. Each layer has one role, declares dependencies, publishes capabilities and states what it requires from lower layers.

The reference design validates this dependency order:

1. `source_surface` — `.sambu` text and source entry points.
2. `syntax_foundation` — tokens, parser, typed AST and source spans.
3. `runtime_core` — runtime values and execution.
4. `domain_services` — scientific, voxel and domain operations.
5. `machine_control` — workspace checks, sampling and failure ledger.
6. `ide_services` — document inspection, outlines, diagnostics and completion.
7. `verification` — quality evidence and test contracts.

`PlywoodDesign` checks:
- valid and unique layer names;
- permitted layer roles;
- known dependencies;
- dependency cycles;
- duplicate capability providers;
- requirements supplied by declared dependencies;
- a bounded number of layers.

It returns a topological order or explicit issues. A layer cannot claim a service that no dependency provides. This is an architecture-contract validator, not yet a static analyzer for every Python import or runtime call.

Python API:

~~~python
from sambu import PlywoodLayer, PlywoodDesign

design = PlywoodDesign((
    PlywoodLayer("syntax", "foundation", provides=("typed-ast",)),
    PlywoodLayer(
        "editor", "tooling",
        depends_on=("syntax",),
        requires=("typed-ast",),
        provides=("diagnostics",),
    ),
))
print(design.validate().valid)
print(design.topological_order())
~~~

## 4. Rule one-in-one-hundred — specific code sampling

The principle is not “read only one percent and trust the result.” It is a bounded audit aid that selects concrete syntax-tree statements without requiring the whole codebase to be inspected manually in every pass.

`CodeSampler` operates on `.sambu` files and typed AST nodes:

1. Find source files in a file or workspace.
2. Refuse symlink roots/files; skip hidden and generated dependency directories.
3. Enforce file-count, per-file source-byte and aggregate workspace-byte budgets (2 MB per source by default, 32 MB across a workspace).
4. Parse each source file. Invalid files fail the sampling operation instead of disappearing from the report.
5. Rank AST statements by SHA-256 of `seed | relative path | source offset | node kind`.
6. Select `ceil(statement_count / N)` statements per file, with at least one sample for every non-empty file.
7. Return source ranges, excerpts and fingerprints.

The default is `N = 100`, seed `0`. Sampling is stratified per file so a small but important source file is not erased by a large module. The same source, path, seed and ratio produce the same sample.

~~~bash
sambu machine sample examples/mulberry_charlotte.sambu --ratio 100 --seed 17
sambu machine sample . --ratio 100 --seed 17 --json
~~~

The result is a sample, never a proof of correctness. Critical modules still require complete tests, review, threat analysis and boundary checks.

## 5. Ten thousand dead spirits — Ghost Ledger

“Ten thousand dead spirits” is the project's failure-memory metaphor. A `GhostLedger` stores up to **10,000 unique failure fingerprints** by default. It preserves engineering memory without retaining complete source files or arbitrary local program state.

Each record contains:
- stable SHA-256 fingerprint;
- error class and bounded category;
- redacted error message;
- source-content hash, not the source text;
- short bounded context label;
- occurrence count.

Repeated identical failures increment a counter instead of filling the ledger with duplicates. When capacity is reached, the oldest distinct record is evicted. Export uses a versioned JSON schema; import validates the schema and capacity. The ledger is in memory unless the caller explicitly exports it.

Secrets such as `password=`, `token=`, authorization values and URL credentials are redacted before storage. Redaction is a defense-in-depth filter, not a guarantee that all proprietary or personal data can be detected. Do not put secrets in error messages or context labels.

~~~python
from sambu import GhostLedger

ghosts = GhostLedger()  # default ceiling: 10,000 unique signatures
ghosts.record(
    RuntimeError("token=do-not-store this request failed"),
    source="let answer = 1 / 0",
    category="runtime",
    context="calculation-example",
)
print(ghosts.count)
snapshot = ghosts.to_json()
~~~

The Machine records parser/workspace failures and runtime failures it executes through `run_source`. It does not upload reports automatically.

## 6. Effort amplification — measure engineering leverage

“Усилие усиления” is formalized as **Effort Amplification**. The question is whether engineering time produced a measurable improvement without regressing another declared quality metric.

For every metric, record baseline `b` and candidate `c`:

- higher-is-better: `gain = (c - b) / b × 100`;
- lower-is-better: `gain = (b - c) / b × 100`.

Then:

`mean_gain = arithmetic_mean(all metric gains)`

`amplification_index = mean_gain / engineering_hours`

The report is accepted only when all declared tests pass, every metric improves or remains neutral, and mean gain is positive. Regressions are listed explicitly. The index is a comparison aid, not a universal scientific measure: teams must use the same workload, hardware, metric set and measurement protocol when comparing candidates.

~~~python
from sambu import EffortAmplification

report = EffortAmplification.evaluate(
    {"latency_ms": 100.0, "memory_mb": 200.0},
    {"latency_ms": 90.0, "memory_mb": 180.0},
    lower_is_better=("latency_ms", "memory_mb"),
    effort_hours=2.0,
    tests_passed=100,
    tests_total=100,
)
print(report.accepted)
print(report.amplification_index)
~~~

A candidate that is faster but breaks compatibility or fails tests is not an accepted improvement.

## 7. SAMBU Machine — project control plane

`SambuMachine` composes the engineering mechanisms:

- a validated plywood dependency model;
- workspace parsing and syntax issue collection;
- deterministic AST sampling;
- a bounded Ghost Ledger;
- a staged capability profile;
- a source execution entry point for the safe interpreter.

Current CLI:

~~~bash
sambu machine architecture
sambu machine architecture --json
sambu machine check .
sambu machine check . --json
sambu machine sample examples/mulberry_charlotte.sambu --ratio 100 --seed 17
~~~

`machine check` parses `.sambu` sources and validates the reference layer graph. It does not yet perform name resolution, full static type checking, effect analysis, import graph resolution or native compilation. A green result means the documented checks passed, not that every property of the application is correct.

## 8. SAMBU IDE — editor services before editor chrome

`SambuIDE` is a **headless editor-service core**. The goal is to build semantic services first and let a future terminal, graphical or LSP client consume one stable API.

Implemented services:
- versioned document snapshots and SHA-256 content identities;
- UTF-8 source-size guard;
- token count and syntax diagnostics with source ranges;
- top-level function, class, interface and trait outline;
- class-method outline;
- bounded keyword and builtin prefix completion;
- workspace parsing and deterministic code sampling through Machine.

Current CLI:

~~~bash
sambu ide inspect examples/mulberry_charlotte.sambu
sambu ide inspect examples/mulberry_charlotte.sambu --format json
sambu ide workspace .
sambu ide complete actor
~~~

Not yet implemented: graphical editor, LSP transport, semantic type-aware completion, hover/type inference, refactoring, debugger UI, formatter, live execution preview and source maps into native code. The current completion list is lexical, not a semantic symbol engine.

## 9. Mulberry Charlotte — reference integration workload

“Шарлотка из шелковицы” is the named end-to-end sample: a small and understandable program that exercises the interpreter with reproducible portion scaling, ingredient totals, and a useful output report.

The recipe values are illustrative example inputs, not a nutritional or food-safety database. The fixture is useful because its arithmetic has clear invariants:

- scaling from 8 to 12 portions multiplies every quantity by 1.5;
- all ingredient quantities and the total mass remain positive;
- total mass equals the sum of the declared base, filling and topping;
- per-portion mass equals total mass divided by target portions;
- execution output is deterministic for the same source and runtime.

~~~bash
sambu examples/mulberry_charlotte.sambu
sambu machine check examples
sambu machine sample examples/mulberry_charlotte.sambu --ratio 100 --seed 17
sambu ide inspect examples/mulberry_charlotte.sambu
~~~

This is not an artificial claim that a dessert is a systems benchmark. It is a compact integration specimen: familiar data, visible arithmetic, known expected properties and a stable file that can pass through Machine, IDE, parser, interpreter and CI.

## 10. Acceptance gates

| Principle | Minimum evidence |
|---|---|
| S — Safety | Profile tests; denied capability tests; input and resource bounds |
| A — Adaptive exploration | Stable sample fingerprints; seed replay; malformed-source rejection |
| M — Managed recovery | FIFO actor tests; restart budget tests; 10,000-entry cap; redaction and serialization tests |
| B — Branchable design | Cycle/missing-provider tests; topological order; reversible migration plan |
| U — Interoperability | Public API compatibility tests; stable schemas; explicit adapters; exportable JSON |
| Machine | One command to parse-check a workspace and emit machine-readable evidence |
| IDE | Versioned document snapshots, source-aware diagnostics and deterministic outline |
| Charlotte | Reproducible arithmetic invariants and CI execution |

## 11. Non-negotiable limits

- The `sandbox` profile is a capability policy for Machine operations; it is not an OS process sandbox.
- The current interpreter has a narrow builtin surface and no direct filesystem/network/process builtin, but Python host code remains trusted code.
- `host` and `device` profiles reserve future extension points; they do not implement adapters or grant real system access.
- The 1:100 sampler is not a test substitute, security audit or statistical confidence guarantee.
- The Ghost Ledger is not a forensic vault, telemetry service or automatic cloud sync.
- Effort Amplification is only as sound as declared metrics and controlled measurements.
- The plywood graph checks declared layer contracts, not every dependency hidden in Python.
- SAMBU IDE is not yet a graphical IDE or full language server.

**Final rule:** an idea becomes part of SAMBU only when its semantics, implementation, tests, documentation, limits and evidence agree.
