# SAMBU

SAMBU (Statistical Analysis & Modeling with Boltzmann Utilities) is an experimental interpreted language for scientific computation and explicit systems modeling.

Its scientific core includes SI-aware quantities, dimensional validation, Maxwell speed statistics, Boltzmann factors, partition sums, entropy and reproducible sampling. Its systems layer models networks, negotiation, resource allocation, operational funnels, commerce queue plans and game mechanics.

Neo-Modern Diplomat / Neo-Modern Developer is the architectural direction: one coherent language for physical models, business processes, infrastructure plans and domain-specific execution adapters. Magento / Adobe Commerce is an enterprise reference domain, not a hard-coded runtime dependency.

Status: 0.6.0 — experimental alpha. SAMBU is not yet a PHP replacement, native compiler, PHP FFI bridge, RabbitMQ client, production checkout replacement, audio renderer or graphical IDE. SAMBU Studio now includes a read-only static Magento XML inspector. It does not connect to production infrastructure or mutate projects.
> **Status:** 0.5.1 — experimental alpha. SAMBU is an interpreter and modeling toolkit, not a Magento module, RabbitMQ client, production checkout replacement, symbolic algebra system, or validated computational-physics package. Domain functions validate production briefs, community offers, territory rounds and commerce architecture plans; they do not connect to external services or render audio.

## Quick start

~~~bash
python -m pip install -e .
sambu --version
sambu examples/ideal_gas.sambu
sambu examples/neo_modern_blueprint.sambu
sambu-studio inspect examples/magento_reference
sambu-studio inspect examples/magento_reference --format json
python -m unittest discover -s tests -v
~~~

## SAMBU language

~~~sambu
let temperature = 300 * K
let argon_mass = 6.6335209e-26 * kg
let speeds = maxwell(temperature, argon_mass)
print(speeds.rms)

let excitation = 0.025 * eV
print(boltzmann(excitation, temperature))
~~~

The runtime currently supports immutable bindings, user functions, lexical scopes, control flow, arrays/records, SI quantities and scientific/domain built-ins. The next language milestones are a typed AST, static dimension/type diagnostics, async execution contracts and versioned PHP interop adapters. They are roadmap items, not shipped language features yet.

## Neo-Modern systems models

SAMBU provides deterministic planning models for commerce queues, retry schedules, idempotency keys, order-pipeline invariants, music-production briefs, introductory-class conversion, multi-session package economics, resource allocation, directed networks and ownership-aware territory rounds.

These are language-level models. They do not connect to external systems or guarantee business outcomes.

## SAMBU Studio: Magento inspection

The separate sambu_studio package exposes:

~~~bash
sambu-studio inspect /path/to/magento/module
sambu-studio inspect /path/to/magento/project --format json
~~~
- Immutable `let` bindings, user-defined functions, lexical scopes, `return`, `if` / `else`, and bounded `for` loops.
- Numbers, strings, booleans, arrays, records, function calls, indexing, and field access.
- SI quantities with dimensional checks for addition, subtraction, comparison, multiplication, division, and integer powers.
- Statistical-mechanics functions: `thermal_energy`, `maxwell`, `boltzmann`, `partition`, `entropy`, and `sample_maxwell`.
- Systems functions: networks, influence propagation, negotiation, allocation, funnels, A/B screening, schedules, attendance, and unit economics.
- Commerce planning functions: `queue_profile`, `retry_schedule`, `idempotency_key`, and `order_pipeline`.
- Production brief validation with `audio_profile`; no DAW or audio-rendering engine is included.
- Community offer metrics with `studio_offer`, reusing multi-session package economics and a configurable introductory conversion target.
- Ownership-aware territory rounds with `capture_node`, extending `capture_tower` resistance calculations.
- Source-aware lexer and parser diagnostics with stable codes and end-exclusive token spans.
- Public immutable typed AST nodes through `parse_ast()`, while `parse()` preserves the established tuple AST for existing clients.
- Object-oriented classes, constructors, instance fields, methods, single inheritance and method overriding.
- Deterministic game rules: `rps_round`, `tic_tac_toe_state` and `tic_tac_toe_move`.

## Object-oriented programming and games

SAMBU supports classes, constructors, mutable instance fields, methods and single inheritance. The first OOP slice deliberately excludes interfaces, traits, visibility modifiers, generics and static type checking. Built-in game functions implement rock-paper-scissors and legal tic-tac-toe state transitions. See [OOP and game rules](docs/GAMES_AND_OOP.md) and run `sambu examples/oop_and_games.sambu`.

The scanner inventories DI preferences and plugins, communication topics and handlers, queue consumers, topology exchanges/bindings and publishers. It checks XML well-formedness, selected attribute constraints, common connection names and simple cross-file references. JSON output is versioned with schema_version 1.

This is a static inspection aid, not official Magento XSD validation and not Magento's merged runtime configuration. A clean report cannot prove that referenced PHP classes exist, DI compilation succeeds, a message is delivered or an order is committed. It reads files only; it does not run bin/magento, SSH, SFTP, SQL, RabbitMQ management commands or file mutations.

See docs/IDE.md, docs/MAGENTO_COMMERCE.md and docs/NEO_MODERN_DEVELOPER.md.

## Language capabilities

- Immutable bindings, user-defined functions, lexical scopes, return, if/else and bounded for loops.
- Numbers, strings, booleans, arrays, records, function calls, indexing and field access.
- SI quantities with dimensional checks for arithmetic, comparison, multiplication, division and integer powers.
- Statistical mechanics: thermal_energy, maxwell, boltzmann, partition, entropy and sample_maxwell.
- Domain models: networks, influence, negotiation, allocation, funnels, A/B screening, schedules, attendance, unit economics, queues, production profiles, community offers and territory control.
- Public source-location and syntax-diagnostic API: SourcePosition, SourceSpan, Token, SambuSyntaxError, tokenize and parse.

## Project layout

~~~text
sambu/             lexer, parser, interpreter, units and domain models
sambu_studio/      optional Studio inspection services and CLI
examples/          runnable SAMBU programs and Magento XML fixtures
tests/             dependency-free unittest suite
docs/              language, domains, commerce, IDE and architecture roadmap
.github/           GitHub Actions test matrix
~~~

## Roadmap

1. Add node-level AST spans and typed intermediate representation while preserving the current tuple AST API.
2. Build a dimensional/type semantic analyzer, semantic tokens and context-aware completions.
3. Add LSP services and version-aware Magento metadata.
4. Extend Studio with XSD validation, DI merge analysis and project symbol navigation.
5. Add safe read-only queue/DB observability adapters.
6. Add optional REPL plots, execution tracing and debugger services.
7. Design async and PHP interop only after explicit semantics and benchmark baselines.
8. Package the GUI, workspaces and Diplomat Night theme with accessibility checks.
The planned SAMBU Studio / Diplomat Night environment is specified separately from the interpreter. The parser now provides typed, source-ranged nodes as the foundation for semantic diagnostics, semantic tokens and LSP support. The graphical IDE, semantic analyzer, LSP server, context completion, REPL, tracing, debugger and theme remain roadmap items, not features claimed to exist. See [IDE architecture](docs/IDE.md).

## Project layout

```text
sambu/       lexer, typed AST, parser, OOP runtime, units and domain models
examples/    runnable SAMBU programs
tests/       dependency-free unittest suite
docs/        language, domain, commerce and IDE specifications
.github/     GitHub Actions test matrix
```

## Roadmap

1. Add a static dimensional analyzer over the typed AST, with stable diagnostic codes and exact source ranges.
2. Add semantic tokens and a language-server protocol implementation.
3. Add context-aware completion from lexical scopes, built-in signatures and versioned adapter metadata.
4. Add REPL plotting and execution tracing without weakening deterministic CLI behavior.
5. Build opt-in Magento adapters as separate packages, with explicit version compatibility and integration tests.
6. Expand queue, event, and workflow models with invariant checks and simulation.
7. Add numerical solvers only with convergence tests, documented assumptions, and reproducible benchmarks.

## License

MIT license. See LICENSE.
