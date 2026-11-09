<div align="center">

# 🦆 SAMBU

### Statistical Analysis · Modeling · Systems · Trust

**A small language with a wide horizon.**

[![Version](https://img.shields.io/badge/version-0.11.0--alpha-6D5DF9?style=for-the-badge)](https://github.com/bboroski/SAMBU)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-208A69?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/bboroski/SAMBU/tests.yml?branch=main&style=for-the-badge&label=checks)](https://github.com/bboroski/SAMBU/actions)

*An experimental interpreted language connecting scientific calculation, object-oriented models, system architecture, evidence-aware workflows, and developer tools.*

</div>

---

## ✨ The idea

SAMBU is built around three principles:

| 🧭 Principle | What it means |
|---|---|
| **Make assumptions visible** | Explicit dimensions, model inputs, permissions, evidence and bounded limits |
| **Make components composable** | One interpreter with focused scientific, systems, UI and integration layers |
| **Make changes inspectable** | Structured diagnostics, deterministic previews, repeatable tests and reversible patches |

> 🧪 **Project status:** SAMBU is experimental alpha software. It is an interpreter and modeling toolkit—not a native compiler, a replacement for Django or Flask, a wallet oracle, or a production certification authority.

## 🧬 Capability map

| Layer | What SAMBU provides |
|---|---|
| 🧠 **Language core** | Lexer, parser, interpreter, typed AST, source spans, lexical scopes, functions, conditionals, bounded loops, arrays and records |
| 🧩 **Object-oriented programming** | Classes, constructors, inheritance, interfaces, traits, abstract/final contracts, visibility, static members and polymorphism |
| 📐 **Scientific computing** | SI quantities, dimensional checks, statistical mechanics, Maxwell distribution, Boltzmann factors, partition functions and entropy |
| 💯 **Percentage arithmetic** | Attached percentage literals, modulo, discounts, relative changes, percentage points, ratio conversion and clamping |
| 🦆 **Anatidae models** | Feather barrier, counter-current exchange, vision, gas exchange, bill filtering, salt balance, flight energetics, flocking and behaviour |
| 🏗️ **Judo** | Architecture graphs, service contracts, dependency checks, fault-domain declarations and deployment-order planning |
| 🥋 **Aikido** | Provider-neutral model routing, capability matching, budget preflight, fallback chains, bounded retries and telemetry |
| 🖥️ **Jiu-Jitsu** | Serializable UI trees, MVC controllers, modal stacks, role-based access and dual-action buttons |
| 🌐 **Web adapters** | Optional Django, Flask and FastAPI integration for host-authenticated Jiu-Jitsu applications |
| 🛡️ **Trust & portfolio checks** | SHA-256 content integrity, trusted-issuer allow-lists, evidence dates, expiry checks and weighted verification coverage |
| 🧱 **Chunking & patching** | Lazy bounded chunks, workload manifests, stale-edit detection, conflict checks and reversible text patches |
| 🧊 **Voxel systems** | Affine frames, sparse chunks, Morton order, octree, surface meshing, DDA raycast, Spielman-style spectral graphs and engine payloads |
| 🧪 **Autotest autopsy** | Repeatable test runs, flaky-test detection, failure categories and diagnostic recommendations |
| 🔎 **Studio & analysis** | Magento XML inspection, declarative filtering, workflow previews, Unicode-aware text craft and prosody diagnostics |

## 🚀 Quick start

~~~bash
# Install the interpreter and tools
python -m pip install -e .

# Check the installation
sambu --version

# Run scientific, OOP and domain examples
sambu examples/ideal_gas.sambu
sambu examples/oop_and_games.sambu
sambu examples/percentages.sambu
sambu examples/anatidae_biophysics.sambu
sambu examples/voxel_world.sambu

# Inspect a Magento module without launching Magento
sambu-studio inspect examples/magento_reference
sambu-studio inspect examples/magento_reference --format json

# Run tests
python -m unittest discover -s tests -v
sambu-test tests --repeat 2
~~~

### 🌐 Optional web integrations

Install only the framework adapter you need:

~~~bash
python -m pip install -e ".[django]"
python -m pip install -e ".[flask]"
python -m pip install -e ".[fastapi]"
~~~

The core interpreter has no mandatory third-party dependencies. Host applications remain responsible for authentication, CSRF protection, per-user persistence, deployment, and authorization at protected data boundaries.

## 💯 Percentages that read clearly

An attached percent sign converts percentage points into a dimensionless ratio. A whitespace-separated percent sign is the modulo operator.

~~~sambu
let rate = 15%
let price = 240
let savings = percent_of(price, 15)
let discounted = price - savings

print(rate)             # 0.15
print(discounted)       # 204
print(10 % 3)           # 1
print(percent_change(80, 100))  # 25
~~~

The standard library includes percent_of, apply_percent, reduce_by_percent, percentage, percent_change, percent_to_ratio, ratio_to_percent, percentage_points and clamp_percent.

📘 [Read the percentage guide](docs/PERCENTAGES.md)

## 🦆 Scientific models inspired by waterfowl

SAMBU includes a parameterized modeling slice inspired by the supplied Anatidae brief:

~~~sambu
let limb = countercurrent_exchange(310 * K, 280 * K, 75%)
let coat = plumage_insulation(0.9, 25%, 10%)
let flight = flight_energy_budget((10 * J) / (1 * s), 5 * s, 60 * J)

print(limb.venous_return)
print(coat.effective_index)
print(flight.energy_required)
print(flight.is_sufficient)
~~~

These are configurable teaching models, not claims that every duck shares identical physiology. Efficiency, insulation, wetness, flight power and energy reserves are inputs supplied by the researcher. Species-specific coefficients require species-specific evidence.

📘 [Explore Anatidae models](docs/ANATIDAE_MODELS.md)

## 🧊 Sparse voxels and engine bridges

SAMBU 0.11 adds a renderer-neutral voxel core and native SAMBU built-ins:

~~~sambu
let world = voxel_grid(16)
voxel_set(world, 0, 0, 0, 2)
voxel_set(world, 1, 0, 0, 2)
let mesh = voxel_mesh(world)
let tree = voxel_octree(world)
let graph = voxel_spectral_profile(world)
let field = voxel_solve_field(graph, [1, -1])
print(mesh.face_count)
print(tree.node_count)
print(graph.matrix_nonzeros)
~~~

The core provides affine spatial frames, signed Morton keys, sparse chunk storage, dirty-chunk frame budgets, exposed-face meshing, 3D DDA ray traversal, JSON interchange and a basic MagicaVoxel VOX importer/exporter. Sparse octrees skip empty regions; a graph layer exposes CSR Laplacians, preconditioned conjugate-gradient solves and a bounded Spielman–Srivastava-style effective-resistance sparsifier.

Starter bridges are included for **Unity, Unreal Engine, Godot, Bevy and O3DE**. Unlisted engines consume the generic payload or implement a small adapter. The bridges are integration source—not prebuilt plugins or proof of production compatibility with every version.

GPU kernels currently mark exposed voxel faces; a separate prefix-sum/compaction and geometry-emission stage is still required for a complete GPU mesher. CPU meshing is a reference face-culling path, not yet a greedy mesher. CPU spectral resistance sampling is intentionally size-limited and should not be mistaken for a GPU solver.

📘 [Voxel architecture](docs/VOXELS.md) · [Engine integration matrix](engine_adapters/README.md) · [CPU benchmark](benchmarks/benchmark_voxels.py)

## 🖥️ Interfaces with two explicit actions

Jiu-Jitsu can expose one visual control with two distinct action paths. Each path can have its own permission, and the caller must state its intent.

~~~python
from sambu.jiu_jitsu import DualActionButton, ViewController

button = DualActionButton(
    "save-or-preview",
    "Save / Preview",
    primary_action="save",
    secondary_action="preview",
    primary_label="Save",
    secondary_label="Preview",
)

controller = ViewController("editor").dual_action(
    button.identifier,
    save_handler,
    preview_handler,
    primary_permission="document:save",
    secondary_permission="document:preview",
)

# Dispatch with {"intent": "primary"} or {"intent": "secondary"}.
~~~

No ambiguous action is guessed. Permission checks are independent for the selected branch.

📘 [Explore web adapters and UI contracts](docs/INTEGRATIONS.md)

## 🛡️ Trust that explains its limits

Portfolio verification checks supplied artifact content against SHA-256 digests, checks issuer names against a configured allow-list, validates evidence dates, and reports weighted coverage with per-item reasons.

**Integrity is not identity.** A matching hash does not prove who created a file, who owns an asset, whether a credential is legally recognized, or whether a wallet contains funds. Stronger provenance requires a host-controlled signature-verification provider and explicit trust roots.

📘 [Read the trust and portfolio guide](docs/TRUST_AND_PORTFOLIOS.md)

## 🧱 Universal chunking. Reversible change.

- **Chunking:** lazy immutable batches, item ceilings, deterministic chunk counts and bounded concurrency plans.
- **Patching:** exact source preconditions, overlap rejection, stale-edit detection, SHA-256 receipts and rollback previews.
- **Workflow planning:** inspect and calculate first; external execution remains an explicit host responsibility.

Nothing silently starts workers or writes project files.

📘 [Chunking and patching](docs/CHUNKING_AND_PATCHING.md)

## 🧪 Autotests with an autopsy

~~~bash
# Run the suite twice to expose flaky tests
sambu-test tests --repeat 2

# Export a structured diagnostic report
sambu-test tests --repeat 2 --json
~~~

The runner records outcomes, flags tests that pass in one run and fail in another, groups failures by heuristic category, and suggests what to inspect next. Its autopsy is a diagnostic aid—not an oracle that can infer a certain root cause from a traceback.

📘 [Test runner and autopsy](docs/TEST_AUTOPSY.md)

## 🗺️ Repository at a glance

~~~text
sambu/
├── lexer.py · parser.py · ast.py · runtime.py
├── values.py · percentages.py · anatidae.py · voxel_builtins.py
├── voxels/  # Sparse grids, frames, octree, graph Laplacian and adapters
├── chunking.py · patching.py · trust.py · testing.py
├── judo.py · aikido.py · jiu_jitsu.py
└── integrations/
    ├── django.py
    ├── flask.py
    └── fastapi.py

sambu_studio/       # Read-only project inspection tools
docs/               # Language references, architecture and integration guides
examples/           # Runnable language and Python examples
tests/              # Regression and contract tests
~~~

## 📚 Documentation

| Guide | Focus |
|---|---|
| [Language reference](docs/LANGUAGE.md) | Implemented syntax, runtime, AST and OOP |
| [Language evolution](docs/LANGUAGE_EVOLUTION.md) | Typed compiler, ownership, concurrency, native targets and 101 consolidated contracts |
| [Autonomy constitution](docs/AUTONOMY_CONSTITUTION.md) | 50 auditable rules, baseline status and implementation acceptance gates |
| [Frameworks](docs/FRAMEWORKS.md) | Judo, Aikido and Jiu-Jitsu |
| [Anatidae models](docs/ANATIDAE_MODELS.md) | Thermoregulation and flight models |
| [Voxel systems](engine_adapters/README.md) | Sparse voxel core, spectral solvers and game-engine adapters |
| [Percentages](docs/PERCENTAGES.md) | Percentage syntax and arithmetic |
| [Web integrations](docs/INTEGRATIONS.md) | Django, Flask and FastAPI |
| [Trust & portfolios](docs/TRUST_AND_PORTFOLIOS.md) | Evidence and content integrity |
| [Chunking & patching](docs/CHUNKING_AND_PATCHING.md) | Bounded streams and reversible edits |
| [Test autopsy](docs/TEST_AUTOPSY.md) | Repeated tests and failure diagnostics |
| [Text craft](docs/text_craft.md) | Text structure, rhyme and prosody |
| [Workflow models](docs/workflows.md) | Evidence-aware records and bounded plans |
| [Studio architecture](docs/IDE.md) | Project inspection and IDE roadmap |

## 🔐 Design principles

1. **Explicit over implicit** — visible assumptions, permissions and external boundaries.
2. **Bounded by default** — limits on input sizes, chunks, loops, retries and recursion.
3. **Inspectable outputs** — source spans, stable diagnostics, structured reports and previews.
4. **Reversible changes** — validate before applying; preserve the original snapshot.
5. **Honest trust** — distinguish content integrity from identity and real-world authority.
6. **Compatibility-aware evolution** — extend the language without casually breaking existing APIs.

## 🚦 Status

SAMBU is evolving alpha software. Core language features and new utilities are experimental. Django, Flask and FastAPI adapters are optional; a renderer, identity provider, durable storage, cryptographic trust roots and production deployment profile are supplied by the integrating application.

## 🤝 Contributing

Focused pull requests, reproducible bug reports, tests and documentation improvements are welcome. Include a minimal reproducer and run:

~~~bash
python -m unittest discover -s tests -v
~~~

## 📄 License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

### **SAMBU — model clearly. compose carefully. verify honestly.** 🦆

</div>
