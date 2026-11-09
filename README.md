<div align="center">

<img src="assets/sambu-ducklings.svg" alt="A parent duck leading three ducklings across a calm pond" width="100%" />

# 🦆 SAMBU

### Statistical Analysis · Modeling · Systems · Trust

**A small language with a wide horizon.**

An experimental, Python-hosted language and toolkit for scientific calculation, explicit models, system architecture, workflows and sparse voxel worlds.

[![Version](https://img.shields.io/badge/version-0.11.0--alpha-536D8E?style=for-the-badge)](https://github.com/bboroski/SAMBU)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-26866B?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/bboroski/SAMBU/tests.yml?branch=main&style=for-the-badge&label=checks)](https://github.com/bboroski/SAMBU/actions)
[![Wiki](https://img.shields.io/badge/docs-SAMBU_Wiki-4F8A83?style=for-the-badge)](wiki/README.md)

[Getting started](#-getting-started) · [Language](#-the-language) · [Capabilities](#-the-flock-of-capabilities) · [Documentation](#-documentation) · [Contributing](#-contributing)

</div>

---

> [!IMPORTANT]
> **Project status: experimental alpha.** SAMBU is an interpreted language and a collection of Python-hosted modeling and developer tools. It is not yet a native systems-language compiler, a complete static type checker, a production web framework, or an automatic deployment system. This README separates what works today from what remains a design target.

## 🌿 What is SAMBU?

SAMBU brings a compact source language and a broader Python toolkit together under one project.

The language began as a scientific DSL for statistical mechanics and dimensional calculations. It has grown to include functions, bounded control flow, object-oriented constructs, percentage arithmetic, domain models and sparse voxel operations. Around the interpreter, the repository provides architecture models, workflow utilities, evidence-aware checks, project inspection and engine-bridge source.

The project is guided by three simple ideas:

| Principle | In practice |
|---|---|
| **Make assumptions visible** | Show dimensions, model inputs, permissions, evidence and resource limits. |
| **Make components composable** | Keep the interpreter, scientific models, system tools and host integrations in focused layers. |
| **Make changes inspectable** | Provide source-aware diagnostics, deterministic previews, repeatable tests and reversible edits. |

### Two surfaces, one project

It is important to distinguish the language from the Python toolkit:

| Surface | How you use it | Examples |
|---|---|---|
| **SAMBU language** | Write and run `.sambu` files | `let`, `fn`, `if`, `for`, classes, quantities, percentage and voxel built-ins |
| **SAMBU Python toolkit** | Import modules from Python | Judo, Aikido, Jiu-Jitsu, trust, chunking, patching and voxel data structures |
| **Command-line tools** | Run installed commands | `sambu`, `sambu-studio`, `sambu-test` |

A Python API is not automatically a language keyword or built-in. Each capability is documented on the surface where it actually runs.

## 🐣 The flock of capabilities

### Language core

- Hand-written lexer and parser.
- Legacy tuple AST retained for compatibility.
- Immutable typed AST with source spans.
- Lexical scopes, immutable `let` bindings and user functions.
- Conditionals and bounded `for` loops.
- Arrays, records, function calls, indexing and field access.
- Classes, constructors, inheritance and the extended OOP slice.
- Explicit runtime diagnostics with source locations.

### Science and numeric modeling

- SI-normalized physical quantities and dimensional checks.
- Built-in units and physical constants.
- Statistical-mechanics helpers: thermal energy, Maxwell speeds, Boltzmann factors, discrete partition sums and entropy.
- Reproducible Maxwell sampling with an explicit seed.
- Percentage literals and validated arithmetic helpers.

### Object models and deterministic games

- Classes, constructors, methods and inheritance.
- Interfaces and reusable traits.
- Abstract/final declarations and class-level members in the extended OOP implementation.
- Deterministic rock-paper-scissors resolution.
- Validated tic-tac-toe state transitions and minimax move selection.

### Domain and systems toolkit

| Subsystem | What it models |
|---|---|
| **Anatidae** 🦆 | Parameterized waterfowl thermoregulation, feather barriers, vision, respiration, feeding, salt balance and flight-energy models |
| **Judo** 🏗️ | Component graphs, contracts, dependency rules, ownership and deployment-order planning |
| **Aikido** 🥋 | Provider-neutral inference routing, capability matching, budgets, fallbacks, bounded retries and telemetry |
| **Jiu-Jitsu** 🖥️ | Serializable UI trees, MVC controllers, modal flows, role-based access and explicit action dispatch |
| **Workflow models** | Evidence-linked records, relationship graphs, bounded batch plans, prioritization and pattern analysis |
| **Trust tools** 🛡️ | SHA-256 content-integrity checks, issuer allow-lists, evidence dates and verification coverage |
| **Chunking & patching** | Lazy bounded batches, stale-edit detection, conflict checks and reversible text patches |

### Sparse voxel systems

SAMBU includes a sparse voxel core with:

- occupied-cell storage and bounded chunks;
- affine voxel frames and signed Morton keys;
- dirty-chunk frame planning;
- exposed-face surface meshing;
- 3D DDA ray traversal;
- sparse octrees;
- CSR graph Laplacians and bounded spectral graph tools;
- MagicaVoxel VOX interchange;
- renderer-neutral payloads and starter engine bridges.

Starter bridge source is provided for **Unity, Unreal Engine, Godot, Bevy and Open 3D Engine**. Additional engine identifiers may expose generic payload profiles only; a profile name is not a claim of a tested native plugin.

### Developer tools

- `sambu` — execute SAMBU programs and create project scaffolds.
- `sambu-studio` — read-only inspection of selected Magento / Adobe Commerce XML configuration.
- `sambu-test` — repeated test runs, flaky-test detection and structured failure summaries.
- Reproducible voxel benchmark scripts.
- Optional Flask, Django and FastAPI adapters for Jiu-Jitsu host applications.

## 🚀 Getting started

### Requirements

- Python **3.10 or newer**.
- Git for cloning the repository.
- Optional web framework dependencies only when using the corresponding adapter.

The core interpreter has no mandatory third-party runtime dependencies.

### Install from source

```bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
```

Verify the installation:

```bash
sambu --version
```

### Your first SAMBU program

Create `hello.sambu`:

```sambu
let temperature = 300 * K
let particle_mass = 6.6e-26 * kg
let result = maxwell(temperature, particle_mass)

print(result.most_probable)
print(result.mean)
print(result.rms)
```

Run it:

```bash
sambu hello.sambu
```

You can also execute a one-line program directly:

```bash
sambu -c 'print("Hello from SAMBU")'
```

### Explore the examples

```bash
sambu examples/ideal_gas.sambu
sambu examples/boltzmann_weights.sambu
sambu examples/percentages.sambu
sambu examples/oop_and_games.sambu
sambu examples/anatidae_biophysics.sambu
sambu examples/voxel_world.sambu
```

The repository contains additional examples for workflows, text craft, territory models, community planning, queue design and other domain libraries.

## 🧭 A quick language tour

### Physical quantities

```sambu
let distance = 12 * m
let duration = 3 * s
let speed = distance / duration

print(speed)
```

Quantities are stored in SI-normalized form. Addition, subtraction and comparison require compatible dimensions; multiplication and division combine dimension exponents.

### Percentage syntax

An attached percent sign converts percentage points into a dimensionless ratio. The spaced infix operator is modulo.

```sambu
let discount = 15%
let price = 240
let savings = percent_of(price, 15)
let final_price = price - savings

print(discount)       # 0.15
print(final_price)    # 204
print(10 % 3)         # 1
print(percent_change(80, 100))  # 25
```

### Functions and bounded loops

```sambu
fn square(value) {
  return value * value
}

for number in range(1, 5) {
  print(square(number))
}
```

The documented `range` and `for` paths enforce a 100,000-item ceiling.

### Objects

```sambu
class Animal {
  fn init(self, name) {
    self.name = name
  }

  fn speak(self) {
    return self.name + " makes a sound"
  }
}

class Duck extends Animal {
  fn speak(self) {
    return self.name + " says quack"
  }
}

let duckling = Duck("Pip")
print(duckling.speak())
```

The object model is still experimental. It uses the interpreter's Python-managed runtime; it does not provide a native object ABI or Rust-style ownership guarantees.

### Sparse voxels

```sambu
let world = voxel_grid(16, 100000)
voxel_set(world, 0, 0, 0, 2)
voxel_set(world, 1, 0, 0, 2)
voxel_set(world, 2, 0, 0, 3)

let mesh = voxel_mesh(world)
let octree = voxel_octree(world)

print(voxel_count(world))
print(mesh.face_count)
print(octree.node_count)
```

For the graph solver, engine payloads, frame budgeting and GPU bridge notes, see the [voxel reference](docs/VOXELS.md).

## 🧰 Project creation and commands

SAMBU includes a lightweight project generator:

```bash
# Create a convention-based project
sambu new pond_app

# Run its generated entry point
sambu pond_app/src/main.sambu

# Generate model/controller/view/migration/test starter files
sambu generate scaffold Post title:string body:text --path pond_app
```

The scaffold generator is implemented. **SAMBU Rails is not yet a running web framework:** generated route, controller, template, ORM and migration specifications are starters; there is no active native HTTP server, database adapter, router, view renderer or migration runner.

| Command | Purpose |
|---|---|
| `sambu --version` | Print the installed version |
| `sambu program.sambu` | Run a source file |
| `sambu -c '...'` | Run source passed on the command line |
| `sambu new NAME` | Create a starter project |
| `sambu generate scaffold MODEL fields...` | Generate starter application files |
| `sambu-studio inspect PATH` | Inspect selected Magento XML configuration |
| `sambu-test tests --repeat 2` | Repeat the test suite and report outcome variation |

### Optional web adapters

Install only what your host application uses:

```bash
python -m pip install -e ".[flask]"
python -m pip install -e ".[django]"
python -m pip install -e ".[fastapi]"

# Or install all three optional adapters
python -m pip install -e ".[web]"
```

The host application remains responsible for authentication, CSRF protection, per-user persistence, deployment, transport security and authorization at protected data boundaries.

## 🧪 Testing and quality checks

Run the complete test suite:

```bash
python -m unittest discover -s tests -v
```

Repeat it to help expose flaky tests:

```bash
sambu-test tests --repeat 2
sambu-test tests --repeat 2 --json
```

Run the voxel reference benchmark:

```bash
python benchmarks/benchmark_voxels.py --size 16 --repeats 3
python benchmarks/benchmark_voxels.py --size 6 --include-spectral --json
```

The CI workflow currently tests Python **3.10, 3.11, 3.12 and 3.13**, runs the unit suite and repeat runner, executes representative language examples, checks the Magento inspector, exercises optional web integrations and checks the Bevy bridge.

The test autopsy groups failures heuristically. It is a diagnostic aid, not an oracle that can infer a certain root cause from a traceback.

## 🗺️ Architecture at a glance

```text
SAMBU repository
│
├── sambu/                 Language runtime and Python toolkit
│   ├── lexer.py           Tokenization
│   ├── parser.py          Parsing and AST construction
│   ├── ast.py             Immutable source-aware AST
│   ├── interpreter.py     Program execution
│   ├── values.py          Runtime records and SI quantities
│   ├── judo.py            Architecture modeling
│   ├── aikido.py          Inference orchestration
│   ├── jiu_jitsu.py       UI / MVC / RBAC model
│   ├── voxels/            Sparse voxel and graph systems
│   └── integrations/      Optional web-framework adapters
│
├── sambu_studio/          Read-only project inspection tools
├── engine_adapters/       Starter game-engine bridge source
├── examples/              Runnable SAMBU and Python examples
├── benchmarks/            Reproducible performance harnesses
├── tests/                 Regression and contract tests
├── docs/                  Detailed technical references
├── wiki/                  Project encyclopedia
└── assets/                Project artwork
```

## 🔬 What is implemented — and what is not

SAMBU is deliberately honest about its current boundaries.

| Area | Current state |
|---|---|
| Interpreter, lexer, parser and source-aware AST | **Implemented · experimental** |
| Functions, scopes, control flow, arrays and records | **Implemented** |
| OOP, interfaces, traits and game-state helpers | **Implemented · alpha API** |
| Runtime SI quantities and scientific helpers | **Implemented** |
| Sparse voxel core and bounded CPU graph/mesh algorithms | **Implemented** |
| Starter engine bridge source | **Included · host integration required** |
| Judo, Aikido and Jiu-Jitsu | **Python host APIs** |
| Studio Magento XML inspection | **Implemented · read-only and limited** |
| Project/scaffold generator | **Implemented · generated framework files are starters** |
| Native machine-code compiler and self-hosted runtime | **Planned** |
| Full static type/effect/ownership checker | **Planned** |
| Language-level async scheduler and native concurrency model | **Planned** |
| Complete graphical IDE and LSP server | **Planned** |
| Running Rails-style router, ORM, database and migration engine | **Planned** |

The future systems-language architecture and its acceptance criteria live in the [Language Evolution Architecture](docs/LANGUAGE_EVOLUTION.md). The [Autonomy Constitution](docs/AUTONOMY_CONSTITUTION.md) records auditable rules and baseline evidence. A proposal is not counted as an implemented feature.

## 📚 Documentation

### Start learning

- [SAMBU Wiki — project encyclopedia](wiki/README.md)
- [Language reference](docs/LANGUAGE.md)
- [Frameworks: Judo, Aikido and Jiu-Jitsu](docs/FRAMEWORKS.md)
- [Percentage arithmetic](docs/PERCENTAGES.md)

### Explore the domains

- [Anatidae comparative models](docs/ANATIDAE_MODELS.md)
- [Domain models](docs/DOMAINS.md)
- [Neo-Modern planning blueprint](docs/NEO_MODERN_BLUEPRINT.md)
- [Workflow models](docs/workflows.md)
- [Chunking and reversible patching](docs/CHUNKING_AND_PATCHING.md)
- [Trust and portfolio checks](docs/TRUST_AND_PORTFOLIOS.md)

### Systems and tooling

- [Sparse voxel architecture](docs/VOXELS.md)
- [Game-engine adapter matrix](engine_adapters/README.md)
- [Django, Flask and FastAPI integrations](docs/INTEGRATIONS.md)
- [Magento / Adobe Commerce architecture and inspector](docs/MAGENTO_COMMERCE.md)
- [SAMBU Studio and IDE roadmap](docs/IDE.md)
- [Test runner and failure autopsy](docs/TEST_AUTOPSY.md)

### Future architecture

- [Language Evolution Architecture](docs/LANGUAGE_EVOLUTION.md)
- [SAMBU Rails proposal](docs/SAMBU_RAILS.md)
- [Autonomy Constitution](docs/AUTONOMY_CONSTITUTION.md)

## 🦆 The SAMBU design principles

The duck is a project mascot, not a restriction on what the language can do. The flock is a useful image for the project's architecture: independent components, clear coordination and a shared direction.

1. **Curiosity before convention** — explore alternatives, but preserve evidence of what works.
2. **Explicit over implicit** — assumptions, dimensions, permissions and side effects stay visible.
3. **Small core, wide horizon** — keep the language approachable and its tooling modular.
4. **Bounded by default** — place limits on work, memory, retries and input sizes.
5. **Inspectable by design** — explain diagnostics, transformations and model outputs.
6. **Safe experiments** — isolate prototypes and preserve a route back to a known-good state.
7. **Evolution with memory** — retain compatibility notes, decision history and regression tests.
8. **Honest maturity** — separate implemented behavior from proposals and unfinished integrations.

## 🤝 Contributing

Focused pull requests, reproducible bug reports, tests and documentation improvements are welcome.

A useful report includes:
- SAMBU and Python versions;
- operating system and exact command;
- a minimal reproducer;
- expected and actual behavior;
- complete diagnostic output.

Before submitting a change, run:

```bash
python -m unittest discover -s tests -v
```

For language changes, include valid and invalid source cases, boundary tests and compatibility checks. For domain models, document assumptions and limitations. For integrations, describe the host responsibilities and security boundary.

## 📄 License

SAMBU is distributed under the MIT License. See [LICENSE](LICENSE).

---

<div align="center">

**SAMBU — model clearly. compose carefully. verify honestly.**

*Stay curious. Follow the trail. Keep the flock moving.* 🐣

</div>
