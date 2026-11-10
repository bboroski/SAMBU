<div align="center">

<img src="assets/sambu-ducklings.svg" alt="SAMBU duck family — project illustration" width="100%" />

# SAMBU

### Statistical Analysis · Modeling · Systems · Trust

**A small language with a wide horizon.**

An experimental, Python-hosted language and toolkit for scientific computing, explicit modeling, systems architecture, workflows and sparse voxel worlds.

[Українська](README.md) · [English](README.en.md) · [Русский](README.ru.md)

[![Version](https://img.shields.io/badge/version-0.11.0--alpha-536D8E?style=for-the-badge)](https://github.com/bboroski/SAMBU)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-26866B?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/bboroski/SAMBU/tests.yml?branch=main&style=for-the-badge&label=checks)](https://github.com/bboroski/SAMBU/actions)

[Quick start](#-quick-start) · [Language](#-the-sambu-language) · [Capabilities](#-capability-map) · [Developer tools](#-developer-tools) · [Documentation](#-documentation)

</div>

---

> **Maturity: experimental alpha.** The interpreter, selected domain modules and CLI tools are implemented and testable. A native compiler, complete static type/effect system, full LSP IDE and some integrations remain development goals.

## What is SAMBU?

SAMBU combines an interpreted language for .sambu programs with a Python package for scientific, architectural and workflow tasks. Its engineering priorities are explicit assumptions, bounded operations, inspectable results and modular evolution.

## Capability map

<img src="assets/architecture-map.svg" alt="SAMBU layered architecture: language surfaces, runtime, scientific modules, voxel systems and engineering toolkit" width="100%" />

| Area | Available capabilities |
|---|---|
| **Language core** | Hand-written lexer/parser, immutable source-aware AST, scopes, functions, bounded loops, arrays, records, classes and inheritance. |
| **Scientific computing** | SI quantities, dimensional checks, physical constants, thermal energy, Maxwell speeds, Boltzmann factors, partition sums, entropy and reproducible sampling. |
| **Sparse voxel systems** | Bounded chunks, affine frames, Morton keys, surface meshing, 3D DDA, sparse octrees, graph Laplacians and VOX interchange. |
| **Engineering modules** | Judo architecture graphs; Aikido inference routing; Jiu-Jitsu UI/MVC/RBAC models; workflows, trust checks and reversible patching. |
| **Runtime experiments** | Bounded actors, sequential state commits, dead-letter capture, supervision and typed software channels. These are not native parallel execution. |
| **Developer tools** | sambu CLI, sambu-studio read-only Magento XML inspector, sambu-ide Tkinter IDE shell, sambu-test and SAMBU Machine. |
| **Creative-text analysis** | Deterministic section/refrain and compact-hook diagnostics, script-mix inspection, approximate prosody, explicit performance cues and nine-cluster metadata ontology (2026.12). |

### Articulatory syntax

A deterministic second syntax surface is generated as a matrix: **10 semantic consonant families × 5 vowel grades × 4 grammatical endings = 200 forms**. The current wordbook contains 25 grammar forms, 137 built-ins and 38 reserved forms.

<img src="assets/articulatory-syntax.svg" alt="SAMBU articulatory syntax matrix with ten semantic families, five vowel grades and four grammatical roles" width="100%" />

This is a formal parser-level syntax layer, not natural-language interpretation or model-generated code. Read the [full specification](docs/ARTICULATORY_SYNTAX.md).

### Sparse voxel pipeline

<img src="assets/voxel-pipeline.svg" alt="SAMBU sparse voxel pipeline from occupied cells to spatial structures, geometry and renderer-neutral payloads" width="100%" />

Starter bridge source is available for Unity, Unreal Engine, Godot, Bevy and Open 3D Engine. A bridge profile or starter source does not mean a complete, packaged or hardware-validated plugin.

## Quick start

**Requirements:** Python 3.10+ and Git. The core interpreter has no mandatory third-party runtime dependencies.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
sambu --version
~~~

Create hello.sambu:

~~~sambu
let temperature = 300 * K
let particle_mass = 6.6e-26 * kg
let profile = maxwell(temperature, particle_mass)
print(profile.most_probable)
print(profile.mean)
print(profile.rms)
~~~

Run:

~~~bash
sambu hello.sambu
# or
sambu -c 'print("Hello from SAMBU")'
~~~

Explore:

~~~bash
sambu examples/ideal_gas.sambu
sambu examples/boltzmann_weights.sambu
sambu examples/oop_and_games.sambu
sambu examples/voxel_world.sambu
sambu examples/supervised_runtime.sambu
~~~

## The SAMBU language

The language supports declarations, expressions, user functions, conditionals, bounded iteration, arrays, records, field access and an experimental object model.

~~~sambu
fn square(value) {
  return value * value
}
for number in range(1, 5) {
  print(square(number))
}
let distance = 12 * m
let duration = 3 * s
print(distance / duration)
~~~

Physical quantities use SI-normalized values. Addition and comparison require compatible dimensions; multiplication and division combine dimension exponents. Documented loop and range paths enforce a 100,000-item ceiling.

Articulatory example:

~~~sambu
kava temperature = 300 * K
kava particle_mass = 6.6e-26 * kg
kava profile = vava(temperature, particle_mass)
lava(profile.rms)
~~~

## Developer tools

| Command | Purpose |
|---|---|
| sambu | Run files or inline code; generate project scaffolds. |
| sambu-ide | Launch the lightweight Tkinter IDE. |
| sambu-studio inspect PATH | Read-only inspection of supported Magento / Adobe Commerce XML. |
| sambu-test tests --repeat 2 | Repeat tests and summarize outcome variation. |
| sambu machine architecture | Validate declared architecture layers. |
| sambu machine sample FILE --ratio 100 --seed 17 | Reproducible AST sampling. |

The IDE includes editing, file open/save, F5 execution, output, diagnostics and RU/EN switching. It is not yet an LSP client. Machine supports architecture inspection and deterministic sampling, not complete static type/effect analysis or native compilation.

Optional host adapters:

~~~bash
python -m pip install -e ".[flask]"
python -m pip install -e ".[django]"
python -m pip install -e ".[fastapi]"
~~~

Authentication, transport security, persistence and authorization remain the host application's responsibility.

## Creative text analysis and semantic metadata

Text Craft provides deterministic, descriptive signals for text:

- section headings and exact repeated blocks;
- visible Latin, Cyrillic and other writing-system mixes;
- approximate syllable counts, spelling-based rhyme groups, internal echoes and alliteration;
- explicit written markers such as stage directions, parenthetical notes, quoted phrases and hyphenated repetitions.

All bundled examples are neutral synthetic fixtures: service messages, interface states, catalog records and technical descriptions. They are not derived from user-authored poems, lyrics or private source material.

`hook_profile(text)` reports compact 2–4-line structure, repeated terms and lines, approximate rhyme groups and syllable spread. It does not predict audience response. `performance_cues_profile(text)` extracts written markers and source positions; it does not infer emotion, speaker identity or actual delivery.

The metadata-only ontology is versioned at **2026.12** and contains nine human-assigned clusters (T-001…T-009). The validator checks supplied annotations; it does not classify unannotated text, generate embeddings or fine-tune a model.

~~~bash
sambu creative clusters --json
sambu creative validate examples/creative_metadata_examples.sample.json --json
sambu examples/performance_cues.sambu
~~~

See [Text Craft](docs/text_craft.md), [Hook Craft and open-system models](docs/OPEN_SYSTEM_AND_HOOK_CRAFT.md) and [Creative Data Governance](docs/CREATIVE_DATA_GOVERNANCE.md).
## Engineering doctrine

Five governing principles:

- **Safety** — explicit capabilities and trust boundaries.
- **Adaptive exploration** — reproducible, hypothesis-driven experiments.
- **Managed recovery** — bounded memory, queues, work and retries.
- **Branchable design** — modular layers and explicit contracts.
- **Unforced interoperability** — stable interfaces and user choice.

Machine adds capability profiles, deterministic 1:100 AST sampling and a bounded Ghost Ledger. Sealed allows inspection; sandbox allows execution in the SAMBU interpreter. Neither is an OS security sandbox. Host and device profiles reserve future adapters; they do not grant shell, network or hardware access.

## Verification

~~~bash
python -m unittest discover -s tests -v
sambu-test tests --repeat 2
sambu-test tests --repeat 2 --json
~~~

Reproducible voxel benchmarks are also included. Compare performance only under equivalent workloads and build configurations.

## Status and roadmap

**Implemented:** interpreted language core, Python domain modules, scientific helpers, sparse voxel operations, selected actor/channel primitives, CLI tools, Machine inspection, IDE services and the Tkinter editor shell.

**Evolving:** static analysis, ownership/effect semantics, richer IDE integration, native toolchain stages and host/device adapters.

**Not represented as complete:** native compiler, self-hosting, C++ ABI compatibility, full Pascal/Delphi/Fortran compatibility, production web framework, automatic deployment, OS sandbox or full LSP IDE.

## Documentation

- [Articulatory Syntax](docs/ARTICULATORY_SYNTAX.md) · [Engineering Doctrine](docs/SAMBU_ENGINEERING_DOCTRINE.md)
- [Systems Architecture](docs/CRIPPLE_SYSTEMS_ARCHITECTURE.md) · [Voxel Reference](docs/VOXELS.md)
- [Creative Data Governance](docs/CREATIVE_DATA_GOVERNANCE.md) · [Studio Guide](docs/DUCK_STUDIO.md)
- [Source and tests](https://github.com/bboroski/SAMBU/tree/main) · [Issues](https://github.com/bboroski/SAMBU/issues)

## Contributing and license

Focused pull requests are welcome. Include a minimal reproducer, expected and actual behavior, relevant tests and any domain or security assumptions. MIT — see [LICENSE](LICENSE).

<div align="center">

**SAMBU — model clearly. compose carefully. verify honestly.** 🦆

</div>

## NUN Mesh integration

<p align="center"><img src="assets/nun-mesh.svg" width="100%" alt="SAMBU highlighted within the NUN Mesh project ecosystem"></p>

SAMBU is the language and developer-tooling layer. Its Tkinter IDE and Duck Studio remain separate applications; ToolNG embeds only the portable policy/workflow core, not the Python interpreter. [Integration guide](docs/ECOSYSTEM_INTEGRATION.md) · [Klipot portal](https://github.com/bboroski/Klipot) · [Shared protocol](https://github.com/bboroski/Klipot/blob/main/docs/INTEGRATION_PROTOCOL.md)
