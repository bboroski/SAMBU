markdown
<div align="center">

# SAMBU
### Statistical Analysis & Modeling with Boltzmann Utilities

[![Status: 0.6.0-alpha](https://img.shields.io/badge/status-0.6.0--alpha-informational?style=flat-square&color=3b82f6)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-success?style=flat-square)]()
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)]()

*An experimental interpreted language for scientific computation, explicit systems modeling, and enterprise architecture blueprints.*

</div>

---

## Architectural Direction

**Neo-Modern Diplomat / Neo-Modern Developer** is the driving vision behind SAMBU: one coherent, elegant language bridging physical models, business processes, queue topologies, infrastructure plans, and domain-specific execution adapters. 

> **Note on Scope:** *Magento / Adobe Commerce* serves as an enterprise reference domain, not a hard-coded runtime dependency. SAMBU is an interpreter and modeling toolkit—not a native compiler, PHP replacement, RabbitMQ client, or production checkout override.

---

## Core Capabilities

* **Foundational Runtime:** Immutable `let` bindings, lexical scopes, user-defined functions, control flow (`if`/`else`, bounded `for` loops), arrays, and records.
* **Object-Oriented Programming:** Classes, constructors, mutable instance fields, methods, and single inheritance.
* **SI Quantities & Dimensionality:** Native dimensional checks for arithmetic, comparisons, products, quotients, and integer powers.
* **Statistical Mechanics:** `thermal_energy`, `maxwell`, `boltzmann`, `partition`, `entropy`, and `sample_maxwell`.
* **Deterministic Systems & Domains:** Networks, influence propagation, negotiation, allocation, funnels, A/B screening, schedules, attendance, and unit economics.
* **Commerce & Queue Planning:** `queue_profile`, `retry_schedule`, `idempotency_key`, `order_pipeline`, community offers, and territory control.
* **Game Rules & Diagnostics:** Deterministic states for Rock-Paper-Scissors and Tic-Tac-Toe, alongside a public AST and error diagnostic API (`tokenize`, `parse`, `parse_ast`).

---

## Quick Start

```bash
# Install package in editable mode
python -m pip install -e .

# Verify installation & run examples
sambu --version
sambu examples/ideal_gas.sambu
sambu examples/neo_modern_blueprint.sambu
sambu examples/oop_and_games.sambu

# Run Magento static inspection via Studio
sambu-studio inspect examples/magento_reference
sambu-studio inspect examples/magento_reference --format json

# Run the test suite
python -m unittest discover -s tests -v

```

---

## Language Syntax Preview

```sambu
let temperature = 300 * K
let argon_mass = 6.6335209e-26 * kg
let speeds = maxwell(temperature, argon_mass)
print(speeds.rms)

let excitation = 0.025 * eV
print(boltzmann(excitation, temperature))

```

---

## SAMBU Studio: Static Magento Inspector

The optional `sambu_studio` package provides a read-only static analyzer for Magento architecture:

* Inventories DI preferences, plugins, communication topics, queue consumers, topology exchanges, and publishers.
* Validates XML well-formedness, attribute constraints, common connection names, and cross-file references.
* **Safe by Design:** Reads files locally only. It does not execute `bin/magento`, establish SSH/SQL/RabbitMQ connections, or perform file mutations.

---

## Project Layout

```text
sambu/              Lexer, typed AST, parser, OOP runtime, SI units & domain models
sambu_studio/       Optional Studio inspection services and CLI
examples/           Runable SAMBU programs and Magento XML fixtures
tests/              Dependency-free unittest suite
docs/               Language specifications, domains, commerce, IDE & roadmap
.github/            GitHub Actions test matrix

```

---

## Roadmap

1. **Static Analyzer:** Build a dimensional/type semantic analyzer over the typed AST with stable error codes and exact source spans.
2. **LSP & Tokens:** Implement Language Server Protocol support and contextual semantic tokens.
3. **Contextual Completion:** Add intelligent scope and version-aware adapter metadata completion.
4. **Interactive Diagnostics:** Introduce REPL plotting and non-intrusive execution tracing.
5. **Modular Adapters:** Package opt-in Magento integration adapters with strict version contracts.
6. **Simulation Engine:** Expand queue, event, and workflow models with invariant checks.

---

## License

Distributed under the **MIT License**. See [LICENSE](https://www.google.com/search?q=LICENSE) for details.

```

<ElicitationsGroup message="Explore related aspects of the SAMBU architecture:">
  <Elicitation label="Review the OOP and game rules documentation" query="Show me the details of the OOP class inheritance model and deterministic game rule functions in SAMBU."/>
  <Elicitation label="Examine the Neo-Modern Developer manifesto" query="Explain the core principles of the Neo-Modern Developer and Neo-Modern Diplomat architectural framework."/>
  <Elicitation label="Explore the SAMBU Studio Magento inspection schema" query="What are the specific XML structures and inspection rules supported by SAMBU Studio?"/>
</ElicitationsGroup>

```
