<div align="center">

<img src="assets/sambu-ducklings.svg" alt="A parent duck leading three ducklings across a calm pond" width="100%" />

# 🦆 SAMBU

### Statistical Analysis · Modeling · Systems · Trust

**A small language with a wide horizon.**

An experimental Python-hosted programming language and developer toolkit for scientific computing, dimensional analysis, explicit models, bounded concurrency, workflow automation and sparse voxel systems. SAMBU also includes bounded Pascal-style, Delphi/Object Pascal-style and Fortran-style source compatibility profiles that translate supported syntax into canonical SAMBU.

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

The next systems-language layer is developed under the **Cripple Systems Architecture**: safe-by-default memory and resource rules, bounded concurrency, actors, supervision, typed channels, then generics, compile-time semantics and a native toolchain. This is a staged C++-class capability target—not a claim of C++ source/ABI compatibility or a finished C++ replacement. The current implemented concurrency slice is documented below and in [the Cripple architecture](docs/CRIPPLE_SYSTEMS_ARCHITECTURE.md).

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
- Second, sound-built articulatory syntax with 200 generated lexemes: 25 grammar forms, 123 built-in aliases and 52 reserved future forms.
- Legacy tuple AST retained for compatibility.
- Immutable typed AST with source spans.
- Lexical scopes, immutable `let` bindings and user functions.
- Conditionals and bounded `for` loops.
- Arrays, records, function calls, indexing and field access.
- Classes, constructors, inheritance and the extended OOP slice.
- Bounded actor mailboxes, sequential actor-state transitions, dead-letter capture and hierarchical restart supervision.
- Typed, bounded, non-blocking software channels.
- Explicit runtime diagnostics with source locations.
- Pascal-style, Delphi/Object Pascal-style and Fortran-style source compatibility profiles, translated through the canonical SAMBU parser and interpreter.

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
| **Continuity & signal governance** | Evidence-bearing lifecycle cycles, hash-chained transitions, authenticated issuer checks, replay rejection and quarantine |
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
- Experimental cooperative generator scheduler, deterministic resource scopes and two-verifier authorization boundary in the Python host API.
- **Continuity core**: bounded lifecycle cycles with evidence fingerprints and verifiable event chains, plus fail-closed signal admission with issuer allow-lists, external signature verification and replay checks.
- **Sambu Machine**: layered architecture validation, deterministic 1:100 AST sampling, capability profiles and a bounded 10,000-signature Ghost Ledger.
- **Sambu IDE core**: source-aware document diagnostics, function/class outline, keyword completion and workspace inspection.
- **Effort Amplification**: evidence-backed improvement metric that rejects regressions and incomplete test runs.
- Optional Flask, Django and FastAPI adapters for Jiu-Jitsu host applications.

## 🧭 SAMBU Engineering Doctrine

SAMBU's five-letter engineering code is a second interpretation of its name:

| Letter | Engineering direction |
|---|---|
| **S** | Safety and staged sovereignty |
| **A** | Adaptive exploration |
| **M** | Managed recovery and memory |
| **B** | Branchable, board-layered design |
| **U** | Unforced interoperability and user sovereignty |

The principles are formalized in [SAMBU Engineering Doctrine](docs/SAMBU_ENGINEERING_DOCTRINE.md): plywood architecture, reproducible 1:100 code sampling, the 10,000-entry Ghost Ledger, Effort Amplification, capability-restricted Machine profiles, headless IDE services and the Mulberry Charlotte reference workload.

### SAMBU Machine

```bash
sambu machine architecture
sambu machine check examples
sambu machine sample examples/mulberry_charlotte.sambu --ratio 100 --seed 17
```

Machine validates the declared layer graph, parses source files, and selects reproducible AST samples. It does not yet perform full static type/effect analysis or native compilation.

### SAMBU IDE

```bash
sambu ide inspect examples/mulberry_charlotte.sambu
sambu ide workspace examples
sambu ide complete actor
```

The repository now includes **SAMBU Duck Studio**, a native desktop GUI built with Python's standard-library Tkinter toolkit. It reuses the existing headless IDE services for syntax diagnostics and symbol outlines, and adds a black-and-yellow editor workspace, file open/save, F5 execution, output panel, RU/EN interface switching and an Apple-device diagnostics view. It is a desktop editor shell, not yet an LSP client or a full-featured language server.

### Capability profiles

`SambuMachine(profile="sealed")` permits inspection and sampling. `sandbox` additionally allows execution in the SAMBU interpreter. `host` and `device` reserve future adapter boundaries; they do not grant implemented shell, network or hardware access. The `sandbox` profile is not an OS process sandbox.

### Mulberry Charlotte

`examples/mulberry_charlotte.sambu` is a deterministic arithmetic workload for scaling ingredient quantities, summing mass and calculating portions. It is an integration fixture, not a nutrition database. CI executes it to check the source/interpreter path.

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
sambu examples/supervised_runtime.sambu
sambu examples/articulatory_intro.sambu
```

The repository contains additional examples for workflows, text craft, territory models, community planning, queue design and other domain libraries.

### Run the Pascal, Delphi and Fortran compatibility profiles

The dialect bridge supports a documented procedural subset, not complete source or ABI compatibility with the original compilers and frameworks.

```bash
sambu dialect pascal examples/dialect_apps/pascal/invoice_calculator.pas
sambu dialect delphi examples/dialect_apps/delphi/actor_message_service.dpr
sambu dialect fortran examples/dialect_apps/fortran/thermal_energy_model.f90

# Validate without executing, or inspect the canonical translation
sambu dialect fortran examples/dialect_apps/fortran/maxwell_speed_profile.f90 --check
sambu dialect pascal examples/dialect_apps/pascal/probability_lab.pas --show-translated
```

Each profile has ten executable console examples. See the [dialect compatibility matrix and limitations](docs/DIALECT_COMPATIBILITY.md).

## 🗣️ Articulatory syntax — 200 native words

SAMBU has a second deterministic source surface built from ten semantic sound families, five vowel grades and four grammatical endings. Old spellings remain valid; new grammar words normalize to the same parser terminals, while built-in words call the existing runtime functions.

```sambu
kava temperature = 300 * K
kava particle_mass = 6.6e-26 * kg
kava profile = vava(temperature, particle_mass)

tava square(value) {
  tavum value * value
}

lava(profile.rms)
lava(square(5))
```

The complete 200-word wordbook, phonology, meanings and implementation status are in the [Articulatory Syntax specification](docs/ARTICULATORY_SYNTAX.md).

Explore the lexicon:

```bash
sambu lexicon
sambu lexicon --status active
sambu lexicon --status reserved
sambu lexicon --family V
sambu lexicon --json
```

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

### Actors, supervision and typed channels

The runtime now exposes sequential actors and explicit supervision directly to SAMBU programs:

```sambu
fn accumulate(state, message) {
  return state + message
}

let worker = actor(accumulate, 0, 32)
let control = supervisor("one_for_one", 3, 60)
supervise(control, worker)

actor_send(worker, 4)
actor_send(worker, 7)
let batch = actor_drain(worker, 16)
print(batch.processed)
print(actor_state(worker)) // 11

let telemetry = channel("text", 8)
channel_send(telemetry, "runtime: healthy")
print(channel_receive(telemetry))
```

Actors accept bounded JSON-shaped payloads, process messages in FIFO order and commit state only after a successful handler return. Supervisors support `one_for_one`, `one_for_all` and `rest_for_one` with rolling restart budgets. Failed messages are recorded in bounded dead-letter storage rather than silently retried.

For Python applications, `FiberScheduler` adds deterministic cooperative generator tasks, `ResourceScope` provides reverse-order cleanup, `ModuleMetadata` validates descriptive module records, and `DualAuthorizationGate` requires two independent verification callbacks.

**Concurrency boundary:** the generator scheduler is cooperative and runs on the calling Python thread; it is not native/preemptive/multicore threading. Actor state is serialized only through that actor's mailbox. Software channels are not hardware buses. The HSM verifier is a host adapter hook, not a bundled hardware security module. Static race/deadlock analysis, ownership checking and native fibers remain planned.


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
│   ├── concurrency.py     Cooperative fibers, actors, supervision and channels
│   ├── autonomy.py        Bounded task policy, evidence ledger and change preflight
│   ├── continuity.py     Evidence-fingerprinted cycles and provenance-checked signals
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
| Actor mailbox, sequential state commit and supervision strategies | **Implemented · experimental runtime slice** |
| Typed bounded software channels | **Implemented · experimental** |
| Cooperative Python generator scheduler | **Implemented · Python host API; not native fibers** |
| Reverse-order resource scope and dual-verifier gate | **Implemented · Python host APIs; HSM provider external** |
| Bounded autonomy policy, task manifests, evidence ledger and change preflight | **Implemented · experimental Python host API; no execution or merge authority** |
| Continuity lifecycle and signal admission | **Implemented · experimental Python host API; no scheduler, persistent replay store or bundled cryptographic provider** |
| Runtime SI quantities and scientific helpers | **Implemented** |
| Sparse voxel core and bounded CPU graph/mesh algorithms | **Implemented** |
| Starter engine bridge source | **Included · host integration required** |
| Judo, Aikido and Jiu-Jitsu | **Python host APIs** |
| Studio Magento XML inspection | **Implemented · read-only and limited** |
| Project/scaffold generator | **Implemented · generated framework files are starters** |
| Native machine-code compiler and self-hosted runtime | **Planned** |
| Full static type/effect/ownership checker | **Planned** |
| Native green fibers, OS-thread scheduler and multicore parallelism | **Planned** |
| Language-level borrow checking, RAII and static race/deadlock analysis | **Planned** |
| Complete graphical IDE and LSP server | **Planned** |
| Running Rails-style router, ORM, database and migration engine | **Planned** |

The future systems-language architecture and its acceptance criteria live in the [Language Evolution Architecture](docs/LANGUAGE_EVOLUTION.md). The [Autonomy Constitution](docs/AUTONOMY_CONSTITUTION.md) records auditable rules and baseline evidence. A proposal is not counted as an implemented feature.

## 🧭 Cripple Autonomy Core

The new **Cripple Autonomy Core** adds bounded planning and evidence governance to the Python host API. It is inspired by six engineering lenses—ALUCARD, GING, RAIDEN, DJINN, MADARA and SHANKS—covering capability limits, research discipline, supervised recovery, isolated extensions, adversarial design review and explicit human handoff.

- Immutable task manifests with declared capabilities and risk tiers.
- Resource budgets that are capped by policy, never expanded automatically.
- Deterministic plan fingerprints and a bounded, hash-chained experiment ledger.
- Change preflight for path scope, reversibility, tests, evidence and risk.
- Human review required above the configured autonomous risk ceiling.

This core does **not** execute arbitrary code, modify the repository, grant host permissions, merge pull requests or deploy software. OS-level sandboxing and isolated experiment execution remain planned.

### Continuity cycles and signal governance

`CycleController` provides bounded phases (`dormant → observing → preparing → active → recovering → archived`) with non-null evidence requirements, explicit halting, snapshot fingerprints and a verifiable hash chain. This is a structural evidence check, not validation of approval semantics; the host must verify evidence and authorization before advancing the lifecycle. `SignalGuard` admits bounded JSON signals only from allow-listed issuers, checks strictly increasing issuer sequences, and by default requires a signature verifier supplied by the host. Rejected inputs are quarantined with reason codes. Neither API executes signal content or grants capabilities; cycle state, signal cursors and decisions are in memory unless the host persists them.

The mapping from fictional cyclic-threat concepts to engineering safeguards—and the implementation's limitations—is documented in [Continuity Cycles and Signal Governance](docs/CONTINUITY_AND_SIGNAL_GUARD.md). A runnable host-API example is in `examples/continuity_guard.py`.

See the [Cripple Archetype Engineering Charter](docs/CRIPPLE_ARCHETYPE_CHARTER.md) and the [Cripple Systems Architecture](docs/CRIPPLE_SYSTEMS_ARCHITECTURE.md).

## 📚 Documentation

### Start learning

- [SAMBU Wiki — project encyclopedia](wiki/README.md)
- [Language reference](docs/LANGUAGE.md)
- [200-word articulatory syntax](docs/ARTICULATORY_SYNTAX.md)
- [GitHub language identity, TextMate grammar and Linguist admission status](docs/EDITOR_AND_GITHUB_LANGUAGE_SUPPORT.md)
- [Pascal, Delphi and Fortran dialect compatibility matrix and 30 applications](docs/DIALECT_COMPATIBILITY.md)
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
- [Cripple archetype engineering charter](docs/CRIPPLE_ARCHETYPE_CHARTER.md)
- [Test runner and failure autopsy](docs/TEST_AUTOPSY.md)
- [Continuity cycles and signal governance](docs/CONTINUITY_AND_SIGNAL_GUARD.md)

### Future architecture

- **Native compiler architecture:** [C11 IR kernel, HIR/MIR/LIR contracts, type/ownership design and staged backend roadmap](docs/NATIVE_COMPILER_ARCHITECTURE.md). The current native slice is experimental and does not yet emit machine code.
- **Native kernel:** [Build and test instructions](native/README.md).


- [Language Evolution Architecture](docs/LANGUAGE_EVOLUTION.md)
- [Cripple Systems Architecture — C++-class capability roadmap](docs/CRIPPLE_SYSTEMS_ARCHITECTURE.md)
- [SAMBU Engineering Doctrine, Machine and IDE](docs/SAMBU_ENGINEERING_DOCTRINE.md)
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


## 🦆 SAMBU Duck Studio — graphical IDE

Install the project and launch the desktop IDE:

```bash
python -m pip install -e .
sambu-ide
```

On Windows, Tkinter is normally included with the standard Python installer. The interface uses a charcoal-black workspace, vivid yellow duck-brand accents, a source editor, workspace browser, symbol outline, diagnostics and an integrated execution output panel. Use **Ctrl+O** to open, **Ctrl+S** to save and **F5** to run the current `.sambu` file. The interface language can be switched between Russian and English.

### Apple device diagnostics (Windows)

Open **iPhone / iPad** in the right-hand panel. The diagnostic view checks for `idevice_id` and `ideviceinfo`, enumerates devices exposed by the installed libimobiledevice build, and attempts to read `ProductType`, `ProductVersion` and `DeviceName` from an existing trusted pairing. On Windows it also queries Apple Mobile Device Service and present Plug-and-Play devices through PowerShell.

Install a supported Windows build of [libimobiledevice](https://libimobiledevice.org/) and make its command-line tools available on `PATH`. Install or repair [Apple Devices](https://apps.microsoft.com/detail/9np83lwlpz9k) / its Apple USB driver components where appropriate. Unlock the iPhone/iPad and accept the Trust prompt before expecting paired metadata.

**Diagnostic limits:** SAMBU does not bypass Apple's pairing or trust model. Model and iOS version are shown only when the device is enumerated and the pairing API returns those values. USB enumeration can reveal driver/service problems, but software cannot conclusively identify a charge-only cable or prove a physical port is defective. The diagnostic is read-only and does not back up, restore, pair or alter the device.

### Development and hardware validation

Run the desktop and device-diagnostic tests with:

```bash
python -m unittest discover -s tests -p test_device_diagnostics.py
python -m unittest discover -s tests
```

A hardware compatibility matrix should be populated by running the diagnostic against real iPhone/iPad models and supported Windows/libimobiledevice combinations. CI unit tests mock the device layer and do not claim physical-device coverage. Code signing and a signed Windows installer require a release certificate and should be configured as a release-pipeline secret; no unsigned build is represented as signed.
