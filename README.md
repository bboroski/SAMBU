# SAMBU

**SAMBU** — **S**tatistical **A**nalysis & **M**odeling with **B**oltzmann **U**tilities — is an experimental, interpreted language for scientific computation and explicit systems modeling.

Its scientific core includes SI-aware quantities, dimensional validation, Maxwell speed statistics, Boltzmann factors, partition sums, entropy, and reproducible sampling. Its systems layer models networks, negotiation ranges, resource allocation, operational funnels, events, and commerce queue designs.

**Neo-Modern Diplomat** is the architectural direction: one coherent language for physical models, business processes, infrastructure plans, and domain-specific execution adapters. Magento / Adobe Commerce is the first enterprise-commerce reference domain, not a hard-coded dependency of the language runtime.

> **Status:** 0.6.0 — experimental alpha. SAMBU is an interpreter and modeling toolkit, not a Magento module, RabbitMQ client, production checkout replacement, symbolic algebra system, or validated computational-physics package. Domain functions validate production briefs, community offers, territory rounds and commerce architecture plans; they do not connect to external services or render audio.

## Quick start

```bash
python -m pip install -e .
sambu examples/ideal_gas.sambu
sambu examples/neo_modern_blueprint.sambu
sambu examples/commerce_queue.sambu
python -m unittest discover -s tests -v
```

## A SAMBU program

```sambu
let temperature = 300 * K
let argon_mass = 6.6335209e-26 * kg
let speeds = maxwell(temperature, argon_mass)
print(speeds.rms)

let excitation = 0.025 * eV
print(boltzmann(excitation, temperature))
```

## Commerce architecture model

```sambu
let queue = queue_profile("heavy_orders", 4, 8, 3, true)
let retries = retry_schedule(4, 2, 2, 30)
let key = idempotency_key("checkout", "cart-42")

print(queue.max_in_flight)
print(queue.dead_letter_queue)
print(retries)
print(key)
```

These primitives help make worker concurrency, retry timing, dead-letter routing, and idempotency conventions explicit and testable. They are planning models, not broker configuration or transaction execution. See [Magento / Adobe Commerce architecture](docs/MAGENTO_COMMERCE.md).

## Language capabilities

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

## Neo-Modern Diplomat blueprint

The four-domain blueprint connects production briefs, enterprise order orchestration, community operations and resource-based territory mechanics. Its runnable example is `examples/neo_modern_blueprint.sambu`; implementation boundaries are documented in [Neo-Modern Blueprint](docs/NEO_MODERN_BLUEPRINT.md).

## IDE direction

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

MIT. See [LICENSE](LICENSE).
