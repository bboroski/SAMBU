# SAMBU

**SAMBU** (Statistical Analysis & Modeling with Boltzmann Utilities) is an experimental interpreted language for scientific computation, explicit systems modeling and object-oriented programs.

Neo-Modern Diplomat / Neo-Modern Developer is the architectural direction: a small, deterministic language core with optional tooling and domain adapters. The scientific core handles SI-aware quantities and statistical-mechanics helpers. The systems layer models networks, operations, commerce queue invariants and strategy. SAMBU Studio adds read-only Magento project inspection as a separate package.

> **Status: 0.6.1 — experimental alpha.** SAMBU is not a PHP replacement, native compiler, general-purpose FFI bridge, RabbitMQ client, production checkout replacement, audio renderer or graphical IDE. The Magento inspector is static and read-only. Domain models validate plans; they do not execute external side effects.

## Quick start

~~~bash
python -m pip install -e .
sambu --version
sambu examples/ideal_gas.sambu
sambu examples/neo_modern_blueprint.sambu
sambu examples/oop_and_games.sambu
sambu-studio inspect examples/magento_reference
sambu-studio inspect examples/magento_reference --format json
python -m unittest discover -s tests -v
~~~

## A SAMBU program

~~~sambu
let temperature = 300 * K
let argon_mass = 6.6335209e-26 * kg
let speeds = maxwell(temperature, argon_mass)
print(speeds.rms)

let excitation = 0.025 * eV
print(boltzmann(excitation, temperature))
~~~

## Object-oriented programming

The 0.6.1 runtime supports classes, object construction, an optional init constructor, mutable public instance fields, instance methods, single inheritance and method overriding.

~~~sambu
class Animal {
  fn init(self, name) { self.name = name }
  fn speak(self) { return self.name + " makes a sound" }
}

class Dog extends Animal {
  fn speak(self) { return self.name + " barks" }
}

let pet = Dog("Rex")
print(pet.speak())
~~~

This is the first working OOP foundation, not yet a complete statically typed enterprise object system. Interfaces/protocols, traits, access modifiers, static members, generics, abstract classes, explicit super dispatch and compile-time class checking remain roadmap work. See [OOP and game rules](docs/GAMES_AND_OOP.md).

## Game rules as language features

- `rps_round(player_move, opponent_move)` resolves rock-paper-scissors using the canonical rules.
- `tic_tac_toe_state(board)` validates a 3×3 board and reports win, draw or next player.
- `tic_tac_toe_move(board, player, position)` returns a new board state and rejects illegal turns, occupied cells and moves after game end.

The game functions are deterministic CLI/runtime features; they do not provide a graphical game UI.

## Neo-Modern systems models

SAMBU includes planning functions for queue capacity, retry schedules, idempotency key naming, order-pipeline invariants, production briefs, community offers, unit economics, directed networks and territory capture. These are language-level models, not broker/database/payment operations.

See [Neo-Modern Blueprint](docs/NEO_MODERN_BLUEPRINT.md) and [Magento / Adobe Commerce architecture](docs/MAGENTO_COMMERCE.md).

## SAMBU Studio: Magento inspection

The optional `sambu_studio` package provides a read-only static XML inspector:

~~~bash
sambu-studio inspect /path/to/magento/module
sambu-studio inspect /path/to/magento/project --format json
~~~

It inventories DI preferences/plugins and message-queue topics, consumers, exchanges, bindings and publishers. It checks XML well-formedness, selected attributes, encodings, file-size limits, unsafe DTD/entity declarations and simple cross-file links. JSON output is versioned with `schema_version: 1`.

This is not official Magento XSD validation or merged runtime DI resolution. A clean report does not prove referenced PHP classes exist, DI compilation succeeds, RabbitMQ is reachable or an order was committed. It does not run shell commands, SSH/SFTP, SQL, cache operations, queue purge/replay or file mutations.

## Language capabilities

- Immutable `let` bindings, user-defined functions, lexical scopes, `return`, `if/else` and bounded `for` loops.
- Classes, instances, constructors, mutable instance fields, methods, single inheritance and overriding.
- Numbers, strings, booleans, arrays, records, function calls, indexing and field access.
- SI quantities with dimensional checks for arithmetic, comparison, multiplication, division and integer powers.
- Statistical mechanics: `thermal_energy`, `maxwell`, `boltzmann`, `partition`, `entropy` and `sample_maxwell`.
- Domain models for networks, negotiation, allocation, funnels, schedules, attendance, unit economics and territory control.
- Commerce planning: `queue_profile`, `retry_schedule`, `idempotency_key` and `order_pipeline`.
- Game rules: rock-paper-scissors and legal tic-tac-toe state transitions.
- Source-aware diagnostics and immutable typed AST nodes through `parse_ast()`; `parse()` preserves its legacy tuple AST.
- Separate read-only Magento XML inspection through `sambu-studio`.

## Project layout

~~~text
sambu/             lexer, typed AST, parser, interpreter, OOP runtime and domain models
sambu_studio/      optional static Magento inspection tools and CLI
examples/          runnable language programs and Magento XML fixtures
tests/             dependency-free unittest suite
docs/              language, domains, commerce, OOP, IDE and architecture guidance
.github/           GitHub Actions matrix for Python 3.10–3.13
~~~

## Roadmap

1. Static dimensional/type analysis over typed AST with structured diagnostics.
2. Semantic tokens, scope-aware completion and LSP.
3. Finish the OOP model: interfaces/protocols, visibility, static members, explicit parent dispatch and class-aware semantic diagnostics.
4. Reconcile and expand Magento metadata analysis with version-pinned XSD/DI data.
5. Add read-only RabbitMQ/DB/cache telemetry through optional least-privilege adapters.
6. Add deterministic REPL sessions, execution trace and debugger primitives.
7. Establish reproducible CPU/memory benchmarks before optimization or PHP performance comparisons.
8. Build the graphical Studio and Diplomat Night theme on stable editor services, with accessibility tests.

MIT license. See LICENSE.
