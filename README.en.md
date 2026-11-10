<div align="center">

<img src="assets/architecture-map.svg" alt="Layered architecture of the computation environment" width="100%" />

# MCL — Multidomain Computation Language

### Computation language · scientific modeling · systems workflows

**Formalize. Compute. Verify.**

MCL is an experimental interpreted environment and Python toolkit for scientific computing, explicit modeling, systems architecture, bounded workflows, and sparse voxel structures.

[Українська](README.md) · [English](README.en.md) · [Русский](README.ru.md)

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-26866B?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/bboroski/SAMBU/tests.yml?branch=main&style=for-the-badge&label=checks)](https://github.com/bboroski/SAMBU/actions)

</div>

---

> **Maturity: experimental alpha.** The interpreter, selected domain modules, and command-line tools are implemented and testable. A native compiler, complete static type/effect system, finished LSP IDE, and some integrations remain development goals.

## Purpose

MCL combines an interpreted language with a Python package for scientific, engineering-modeling, and workflow tasks. Its priorities are explicit assumptions, bounded operations, reproducible results, inspectable contracts, and modular evolution.

## Capability map

| Area | Implemented capabilities |
|---|---|
| **Language core** | Lexer/parser, immutable source-aware AST, scopes, functions, bounded loops, arrays, records, classes, and inheritance. |
| **Scientific computing** | SI quantities, dimensional checks, physical constants, thermal energy, velocity distributions, Boltzmann factors, partition sums, entropy, and reproducible sampling. |
| **Sparse geometry** | Bounded chunks, affine coordinate frames, Morton keys, surface meshing, 3D DDA, sparse octrees, graph Laplacians, and VOX interchange. |
| **Engineering models** | Architecture graphs, inference routing, UI/MVC/RBAC models, workflows, trust checks, and reversible patches. |
| **Runtime experiments** | Bounded actor mailboxes, sequential state commits, dead-letter records, supervision, and typed software channels; these are not native parallel execution. |
| **Developer tools** | Command-line interface, read-only XML catalog inspector, Tkinter IDE, test runner, and architecture-profile inspection. |
| **Text analysis** | Deterministic section/refrain parsing, script-mix inspection, approximate prosody, written performance cues, and nine metadata clusters. |

### Articulatory grammar

An additional syntax surface is defined by **10 semantic consonant families × 5 vowel grades × 4 grammatical endings = 200 forms**. This is a parser-level formal grammar, not natural-language understanding or model-generated code. See [ARTICULATORY_SYNTAX](docs/ARTICULATORY_SYNTAX.md).

<img src="assets/articulatory-syntax.svg" alt="Formal articulatory grammar matrix" width="100%" />

### Sparse voxel pipeline

<img src="assets/voxel-pipeline.svg" alt="Conversion of occupied cells into spatial structures and geometry" width="100%" />

Starter adapters are available for Unity, Unreal Engine, Godot, Bevy, and Open 3D Engine. A profile or starter source does not imply a complete or hardware-validated plugin.

## Quick start

**Requirements:** Python 3.10+ and Git. The core interpreter has no mandatory third-party runtime dependencies.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
mcl --version
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
mcl hello.sambu
mcl -c 'print("Hello from MCL")'
~~~

The .sambu extension and existing sambu* commands remain for compatibility. The new mcl* commands are the recommended interface.

## Developer tools

| Command | Purpose |
|---|---|
| mcl | Run files or inline code; generate project scaffolds. |
| mcl-ide | Launch the lightweight Tkinter IDE. |
| mcl-studio inspect PATH | Read-only inspection of supported commerce-catalog XML. |
| mcl-test tests --repeat 2 | Repeat tests and summarize outcome variation. |
| mcl machine architecture | Validate declared architecture layers. |
| mcl machine sample FILE --ratio 100 --seed 17 | Reproducible AST sampling. |

The IDE supports editing, file open/save, F5 execution, output, diagnostics, and RU/EN switching. It is not yet an LSP client. Complete static type/effect analysis and native compilation are not claimed as implemented.

## Text analytics and metadata

Analysis functions describe structure rather than rate artistic quality: sections, exact refrain repeats, compact hooks, writing-system mix, approximate syllables, spelling-based rhyme groups, internal echoes, and written performance cues. They do not predict popularity, infer a speaker's identity or emotional state, or rewrite authored text.

The annotation ontology contains nine clusters. Supplied corpus examples are marked NEEDS_REVIEW; they are test fixtures, not approved training data.

See [Text Craft](docs/text_craft.md), [Creative Data Governance](docs/CREATIVE_DATA_GOVERNANCE.md), and [Open System and Hook Craft](docs/OPEN_SYSTEM_AND_HOOK_CRAFT.md).

## Engineering principles

- **Safety:** explicit permissions and trust boundaries.
- **Adaptive exploration:** reproducible, hypothesis-driven experiments.
- **Managed recovery:** bounded memory, queues, work, and retries.
- **Branchable design:** modular layers and explicit contracts.
- **Interoperability:** stable interfaces and integrator choice.

Inspection and interpreter sandbox profiles are not operating-system security sandboxes. Reserved host/device adapters do not grant automatic shell, network, or hardware access.

## Verification and status

~~~bash
python -m unittest discover -s tests -v
mcl-test tests --repeat 2
mcl-test tests --repeat 2 --json
~~~

**Implemented:** interpreted language core, Python modules, scientific helpers, sparse voxel operations, selected actor/channel primitives, CLI tools, architecture inspection, and IDE services.

**Evolving:** static analysis, ownership/effect semantics, richer IDE integration, native toolchain stages, and host/device adapters.

**Not claimed as complete:** native compiler, self-hosting, full C++ ABI or other-language compatibility, production web framework, automatic deployment, or full LSP IDE.

## Documentation and contribution

- [Articulatory Syntax](docs/ARTICULATORY_SYNTAX.md) · [Engineering Doctrine](docs/SAMBU_ENGINEERING_DOCTRINE.md)
- [Systems Architecture](docs/CRIPPLE_SYSTEMS_ARCHITECTURE.md) · [Voxel Reference](docs/VOXELS.md)
- [Creative Data Governance](docs/CREATIVE_DATA_GOVERNANCE.md) · [IDE Guide](docs/DUCK_STUDIO.md)
- [Source](https://github.com/bboroski/SAMBU/tree/main) · [Issues](https://github.com/bboroski/SAMBU/issues)

External API, platform, and file-format identifiers remain unchanged for interoperability. Internal naming migration must not silently alter the format of existing source files.

## License

MIT — see [LICENSE](LICENSE).
