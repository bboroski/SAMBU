# SAMBU / SAMBU Studio — state matrix

Snapshot date: 2026-11-10  
Repository: bboroski/SAMBU  
Default branch: main  
Main HEAD at audit start: 201b03cfbec6d6337d155151b89496b0f470a39a  
Latest main commit: Keep native IR tests active in Release builds (2026-11-10 07:39:40 UTC)  
Repository tree: 203 entries; 2 workflow files; Python package version 0.11.0.

This is an evidence ledger, not a feature promise. Status applies to the revision named above. A specification, example, or static inspector is not treated as a live integration.

## Status definitions

- Implemented and tested — executable code exists and a relevant test or CI step passed at the recorded revision.
- Implemented partially — executable code exists, but important semantics, coverage, compatibility or integration are incomplete.
- Specification only — documentation, examples or a model exists without the corresponding production-capable implementation.
- Blocked / not verified — evidence is missing, the required environment is unavailable, or behavior cannot yet be established.

## CI evidence for the main HEAD

The required read-only audit was performed before edits. The latest matching runs point to the exact main HEAD above:

| Workflow | Run | Head SHA | Result | Evidence |
|---|---:|---|---|---|
| SAMBU tests | [42776837286](https://github.com/bboroski/SAMBU/actions/runs/42776837286) | 201b03c... | success | Python 3.10, 3.11, 3.12, 3.13; web-integrations; engine-bridges |
| SAMBU native IR | [42776837263](https://github.com/bboroski/SAMBU/actions/runs/42776837263) | 201b03c... | success | C11 configure, Release build, CTest |
| Push on main | [42776837788](https://github.com/bboroski/SAMBU/actions/runs/42776837788) | 201b03c... | success | aggregate push workflow |

Each Python matrix job reports 294 unittest cases, 3 skipped, and a successful sambu-test tests --repeat 2 step. The percentages and Anatidae examples, other configured .sambu examples, SAMBU Machine checks, IDE CLI checks, Magento Studio static inspection, and voxel benchmark smoke command all completed successfully. Web integrations and the Bevy bridge check also passed. The native C11 job passed on this exact HEAD.

A previous native run on 11d4bfe... failed during the Release build because variables used only by C assert expressions became unused under NDEBUG and -Werror. The subsequent main commit re-enabled native IR tests in Release builds; the latest native run is green. This historical failure is not a current failure.

The Actions log also emitted a Node.js 20 deprecation warning for actions/checkout@v4 and actions/setup-python@v5. This is a maintenance warning, not a failed check.

## Component matrix

| Component | Status | Evidence in repository / CI | Risk, missing check, next step |
|---|---|---|---|
| Lexer | Implemented and tested | sambu/lexer.py; tests/test_source.py; stable lexical error codes and token spans | Expand malformed-input and Unicode/property-based coverage without changing token contracts |
| Parser | Implemented and tested | sambu/parser.py; parse_ast and legacy parse; parser error spans in tests/test_source.py | Add grammar conformance/fuzz tests before broad syntax growth |
| AST and source spans | Implemented and tested | Frozen typed AST dataclasses in sambu/ast.py; SourcePosition/SourceSpan in sambu/source.py; AST/source tests | Preserve spans through every new node and future lowering |
| Structured diagnostics | Implemented partially | SambuSyntaxError codes/spans; IDE diagnostic records in sambu/ide.py | Unify lexical, parser, semantic and runtime diagnostics under one stable public contract |
| Public API / compatibility | Implemented partially | Exports in sambu/__init__.py; parse legacy tuple adapter and parse_ast; package version 0.11.0 | Add explicit API compatibility tests and deprecation policy before changing exports or legacy tuple shapes |
| Static typing / dimensional semantics | Implemented partially | Runtime Quantity in sambu/values.py enforces dimension-safe arithmetic; native HIR carries scalar types | No complete pre-runtime semantic type/dimension pass; add one with source-ranged diagnostics |
| Python runtime / standard library | Implemented partially | sambu/runtime.py, sambu/concurrency.py, domain modules and runnable examples; CI exercises them | Runtime remains Python-hosted; specify contracts and test failure/resource boundaries before expanding built-ins |
| OOP | Implemented partially | Class/instance, init, fields, methods, single inheritance and override exercised in tests/test_oop_games.py; runtime has interface/trait/access machinery | Generics, complete static/class-member behavior and all super-dispatch cases are not established as complete |
| RPS / Tic-Tac-Toe built-ins | Implemented partially | Deterministic built-ins and tests for wins, draw, illegal moves, occupied cells and unreachable boards | Complete exhaustive outcome/turn/state matrix, including no move after terminal state, before calling rules complete |
| REPL / trace / debugger | Specification only | CLI supports file execution and tooling commands; no verified interactive REPL/trace/debugger contract in current tree | Define safe execution boundaries and testable trace events before implementation |
| LSP / semantic tokens / completion | Implemented partially | sambu/ide.py provides document inspection and bounded static completions; CI runs IDE inspect/workspace/complete commands | No verified LSP server or parser-aware semantic tokens; completion is not yet scope- or metadata-aware |
| IDE / Studio UX and theme | Implemented partially | Headless IDE services and sambu-studio CLI exist | No verified graphical editor/theme implementation; Diplomat Night remains roadmap, not a shipped GUI |
| Magento metadata / DI / XML | Implemented partially | sambu_studio/magento.py statically inspects DI preferences/plugins, communication topics, queue consumers, topology and publishers; tests cover valid/invalid XML and DTD/entity rejection | No Magento runtime, official XSD resolution, version-aware metadata catalog, GraphQL/MSI inspector or live service-contract validation |
| RabbitMQ / checkout reliability | Specification only | Queue XML samples and commerce workflow examples exist; no live broker adapter or durable outbox implementation was found | Require persisted idempotency, retries/DLX, explicit order states, inventory reservation and payment authorization/capture before any production claim |
| Native HIR / MIR / LIR | Implemented partially | C11 API in native/include/sambu/ir.h; implementation in native/src/ir.c; CMake/CTest and dedicated workflow; latest run passed | Experimental scalar kernel only: single block, no CFG/phi, parser bridge, optimization pipeline, serialization, object writer or machine-code backend |
| Native snapshots / fault-node graph / dump differencing | Specification only | Open issue [#17](https://github.com/bboroski/SAMBU/issues/17) describes portable snapshots, fault-node graphs and differential dump analysis | No implementation evidence yet; start with a versioned portable snapshot format and corruption/round-trip tests |
| Tests / CI | Implemented and tested | .github/workflows/tests.yml, .github/workflows/native.yml; Python 3.10–3.13, web integrations, Bevy bridge, C11 CTest; exact-HEAD runs above | Main branch protection endpoint reported required-check enforcement as off; do not infer merge gating from green runs alone |
| Packaging / dependencies | Implemented partially | pyproject.toml: Python >=3.10, no mandatory dependencies, optional web extras, CLI entry points | Add wheel/sdist build and installed-artifact smoke tests; preserve Python 3.10+ until a tested compatibility decision exists |
| Documentation / release notes | Implemented partially | README, language, integration, IDE, Magento and native architecture docs; CHANGELOG exists | Quality matrix/policy/catalog were absent at audit start; link validation and claims-to-code review remain to be added |
| Workflow permissions / security | Implemented partially | At audit start both workflows omitted explicit permissions; this branch adds contents: read and a stdlib regression test | Verify this branch CI before merge; review future workflows with the same least-privilege rule; branch-protection settings remain unclear |
| Performance | Implemented partially | benchmarks/benchmark_voxels.py and CI smoke run exist | No comparable SAMBU-vs-PHP benchmark or general runtime profile; make no speed claims without controlled measurements |

## Current pull-request and issue context

- Open PR [#16](https://github.com/bboroski/SAMBU/pull/16) proposes unit-return MIR/LIR terminators. It is still a draft; its observed check-runs were green, but draft state is preserved and it is not merged.
- Open PR [#18](https://github.com/bboroski/SAMBU/pull/18) concerns grammar and GitHub Linguist readiness notes.
- Open issue [#17](https://github.com/bboroski/SAMBU/issues/17) tracks native snapshots, fault-node graphs and differential dump analysis.

## Ranked backlog

1. P0 — CI security: keep explicit read-only workflow permissions and the regression test; validate the PR's own run before merge.
2. P1 — Native IR correctness: review and land the already-tested unit-return change only after PR #16 is intentionally marked ready; then add verifier boundary tests.
3. P1 — Native snapshot foundation: implement a versioned, portable, bounded snapshot format from issue #17, with round-trip, malformed-input and compatibility tests.
4. P1 — Static semantic analysis: add a pre-runtime type/dimension pass with source-ranged diagnostics; preserve current runtime behavior.
5. P2 — Language tooling: move completions from static keyword lists to parser/scope-aware results, then add LSP and semantic tokens.
6. P2 — OOP and games: close missing OOP contracts and exhaustive deterministic game-state coverage.
7. P2 — Studio/Magento: version metadata and XML checks first; keep GraphQL/MSI/service-contract support explicitly static until a real adapter exists.
8. P2 — Reliable commerce workflows: model outbox/idempotency/order-state transitions before any broker or checkout adapter.
9. P3 — REPL/debugging: introduce safe trace primitives before an interactive debugger.
10. P3 — Performance: add reproducible, comparable benchmarks and publish measurements only with environment and methodology.

## This iteration

The main-HEAD audit above was read-only. This branch adds explicit contents: read permissions to both CI workflows, a standard-library regression test, and the quality evidence documents. The PR's own workflow status must be read from its exact head SHA; the main-branch PASS above does not certify this branch.
