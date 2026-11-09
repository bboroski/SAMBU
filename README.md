<div align="center">

# SAMBU
### Statistical Analysis & Modeling with Boltzmann Utilities

[![Status: 0.8.0-alpha](https://img.shields.io/badge/status-0.8.0--alpha-informational?style=flat-square&color=3b82f6)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-success?style=flat-square)]()
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)]()

*An experimental interpreted language for scientific computation, explicit systems modeling, and enterprise architecture blueprints.*

</div>

---

## 🧭 Architectural Direction

**Neo-Modern Diplomat / Neo-Modern Developer** is the driving vision behind SAMBU: one coherent, elegant language bridging physical models, business processes, queue topologies, infrastructure plans, and domain-specific execution adapters. 

> **Note on Scope:** *Magento / Adobe Commerce* serves as an enterprise reference domain, not a hard-coded runtime dependency. SAMBU is an interpreter and modeling toolkit—not a native compiler, PHP replacement, RabbitMQ client, or production checkout override.

---

## ⚡ Core Capabilities

* **Foundational Runtime:** Immutable `let` bindings, lexical scopes, user-defined functions, control flow (`if`/`else`, bounded `for` loops), arrays, and records.
* **Object-Oriented Programming:** Classes, constructors, mutable instance fields, single class inheritance, interfaces, traits, abstract/final contracts, visibility, static members, and polymorphic dispatch.
* **SI Quantities & Dimensionality:** Native dimensional checks for arithmetic, comparisons, products, quotients, and integer powers.
* **Statistical Mechanics:** `thermal_energy`, `maxwell`, `boltzmann`, `partition`, `entropy`, and `sample_maxwell`.
* **Deterministic Systems & Domains:** Networks, influence propagation, negotiation, allocation, funnels, A/B screening, schedules, attendance, and unit economics.
* **Commerce & Queue Planning:** `queue_profile`, `retry_schedule`, `idempotency_key`, `order_pipeline`, community offers, and territory control.
* **Game Rules & Diagnostics:** Deterministic states for Rock-Paper-Scissors and Tic-Tac-Toe, alongside a public AST and error diagnostic API (`tokenize`, `parse`, `parse_ast`).
* **Text Craft Diagnostics:** Unicode-aware text metrics, approximate syllable counts, rhyme-tail grouping, line-level prosody, and alliteration analysis.
* **Workflow & Trust Models:** Atomic gift-batch previews, evidence-backed accreditation records, relationship links, human-reviewed signal reports, transparent proposal scoring, bounded batch plans, safe parser inspection, text mining, tag-based clustering and vocabulary-free structural mimicry.

---

Text analysis is deterministic and non-destructive: it reports patterns without rewriting a draft or judging literary quality. See `docs/text_craft.md` and `examples/text_craft.sambu` for the text-craft layer.

Workflow primitives are bounded, deterministic previews; they do not move money, issue credentials, publish allegations, or run external jobs. See `docs/workflows.md` and `examples/workflows.sambu`.

## 🚀 Quick Start

```bash
# Install package in editable mode
python -m pip install -e .

# Verify installation & run examples
sambu --version
sambu examples/ideal_gas.sambu
sambu examples/neo_modern_blueprint.sambu
sambu examples/oop_and_games.sambu
sambu examples/text_craft.sambu
sambu examples/workflows.sambu

# Run Magento static inspection via Studio
sambu-studio inspect examples/magento_reference
sambu-studio inspect examples/magento_reference --format json

# Run the test suite
python -m unittest discover -s tests -v
