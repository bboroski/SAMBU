<div align="center">

<img src="assets/sambu-ducklings.svg" alt="SAMBU duck family — project illustration" width="100%" />

# SAMBU

### Statistical Analysis · Modeling · Systems · Trust

**A small language with a wide horizon.**

An experimental, Python-hosted language and toolkit for scientific computation, explicit models, workflows, system design and sparse voxel worlds.

[![Version](https://img.shields.io/badge/version-0.11.0--alpha-536D8E?style=for-the-badge)](https://github.com/bboroski/SAMBU)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-26866B?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/bboroski/SAMBU/tests.yml?branch=main&style=for-the-badge&label=checks)](https://github.com/bboroski/SAMBU/actions)

[Start here](#-start-in-three-steps) · [Language](#-the-language) · [Capabilities](#-capability-map) · [Tools](#-developer-experience) · [Docs](#-documentation)

</div>

---

> **Maturity: experimental alpha.** The interpreter, selected domain modules and developer commands are implemented and testable. Native compilation, a complete static type/effect system, a full LSP-based IDE and several host integrations remain future work.

## What SAMBU is

SAMBU combines a compact interpreted language for <code>.sambu</code> programs with a Python package for scientific, architectural and workflow-oriented tasks. Its engineering priorities are explicit assumptions, bounded operations, inspectable results and modular evolution.

## Capability map

<img src="assets/architecture-map.svg" alt="SAMBU layered architecture: source surfaces, language runtime, science, voxel systems and engineering toolkit" width="100%" />

| Area | Capabilities |
|---|---|
| **Language runtime** | Hand-written lexer/parser, immutable source-aware AST, scopes, functions, bounded loops, arrays, records, classes and inheritance. |
| **Scientific computing** | SI quantities, dimensional checks, physical constants, thermal energy, Maxwell speeds, Boltzmann factors, partition sums, entropy and reproducible sampling. |
| **Sparse voxel systems** | Bounded chunks, affine frames, Morton keys, exposed-face meshing, 3D DDA, sparse octrees, graph Laplacians and VOX interchange. |
| **Engineering modules** | Judo architecture graphs; Aikido inference routing; Jiu-Jitsu UI/MVC/RBAC models; evidence-aware workflows, trust checks and reversible patching. |
| **Runtime experiments** | Bounded actors, sequential state commits, dead-letter capture, restart supervision and typed software channels. Not native parallel execution. |
| **Developer tools** | <code>sambu</code> CLI, <code>sambu-studio</code> read-only Magento XML inspector, <code>sambu-ide</code> Tkinter desktop shell, <code>sambu-test</code> and SAMBU Machine. |

### Articulatory syntax

A deterministic second source surface is generated from **10 semantic consonant families × 5 vowel grades × 4 grammatical endings = 200 forms**. The current wordbook contains 25 grammar forms, 129 built-in forms and 46 reserved forms.

<img src="assets/articulatory-syntax.svg" alt="SAMBU articulatory syntax: ten semantic families, five vowel grades, four grammatical roles and 200 lexical forms" width="100%" />

This is a regular parser-level syntax layer — not natural-language interpretation or model-generated code. See [the complete specification](docs/ARTICULATORY_SYNTAX.md).

### Sparse voxel processing

<img src="assets/voxel-pipeline.svg" alt="SAMBU sparse voxel pipeline from occupied cells to spatial indexes, geometry and renderer-neutral outputs" width="100%" />

Starter bridge source covers Unity, Unreal Engine, Godot, Bevy and Open 3D Engine. A bridge profile does not imply a finished or hardware-validated plugin.

## Start in three steps

**Requirements:** Python 3.10+, Git. The core interpreter has no mandatory third-party runtime dependencies.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
sambu --version
~~~

Create <code>hello.sambu</code>:

~~~sambu
let temperature = 300 * K
let particle_mass = 6.6e-26 * kg
let profile = maxwell(temperature, particle_mass)
print(profile.most_probable)
print(profile.mean)
print(profile.rms)
~~~

Run it:

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

## The language

SAMBU supports declarations, expressions, user functions, conditionals, bounded iteration, arrays, records, field access and an experimental object model.

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

Quantities use SI-normalized values. Addition and comparison require compatible dimensions; multiplication and division combine dimension exponents. Documented range and loop paths enforce a 100,000-item ceiling.

Articulatory example:

~~~sambu
kava temperature = 300 * K
kava particle_mass = 6.6e-26 * kg
kava profile = vava(temperature, particle_mass)
lava(profile.rms)
~~~

## Developer experience

| Command | Purpose |
|---|---|
| <code>sambu</code> | Run source or inline code; generate project scaffolds. |
| <code>sambu-ide</code> | Launch the lightweight Tkinter editor. |
| <code>sambu-studio inspect PATH</code> | Inspect supported Magento / Adobe Commerce XML. |
| <code>sambu-test tests --repeat 2</code> | Repeat tests and summarize variation. |
| <code>sambu machine architecture</code> | Validate declared architecture layers. |
| <code>sambu machine sample FILE --ratio 100 --seed 17</code> | Reproducible AST sampling. |

The IDE includes editing, open/save, F5 execution, output, diagnostics and RU/EN switching. It is not yet an LSP client. Machine supports architecture inspection and deterministic sampling, not full static type/effect analysis or native compilation.

Optional host adapters:

~~~bash
python -m pip install -e ".[flask]"
python -m pip install -e ".[django]"
python -m pip install -e ".[fastapi]"
~~~

Authentication, transport security, persistence and authorization remain the host application's responsibility.

## Creative data and semantic metadata

SAMBU includes a versioned, metadata-only creative ontology (`2026.12`) with nine human-assigned clusters, including surreal juxtaposition and wordplay. It validates bounded records, keeps legacy `2026.11` entries readable and exports reviewed metadata as JSON-LD.

```bash
sambu creative clusters
sambu creative clusters --json
sambu creative validate examples/creative_metadata.sample.json
```

This is deterministic annotation and validation, not an automatic classifier, embedding model, fine-tuning pipeline or self-learning system. Source text is not stored in metadata records. `NEEDS_REVIEW` remains the default; `CLEAN` and `CLEAN_SATIRE` require a pseudonymous `review_ref` and timezone-aware `reviewed_at` before `generation_eligible` becomes true. Text Craft measures structure and sound; a human curator assigns thematic and safety metadata.

See [Creative Data Governance](docs/CREATIVE_DATA_GOVERNANCE.md) and the [Creative Metadata JSON Schema](schemas/creative-metadata.schema.json).

## Engineering principles

SAMBU's five-part doctrine:

- **Safety** — explicit capabilities and trust boundaries.
- **Adaptive exploration** — reproducible, hypothesis-led experiments.
- **Managed recovery** — bounded memory, queues, work and retries.
- **Branchable design** — modular layers and explicit contracts.
- **Unforced interoperability** — stable interfaces and user choice.

Machine adds capability profiles, deterministic 1:100 AST sampling and a bounded Ghost Ledger. The sealed profile is for inspection; sandbox permits execution in the SAMBU interpreter. Neither is an OS security sandbox. Host/device profiles reserve future adapters; they do not grant shell, network or hardware access.

## Verification

~~~bash
python -m unittest discover -s tests -v
sambu-test tests --repeat 2
sambu-test tests --repeat 2 --json
~~~

Reproducible voxel benchmarks are also included. Compare performance only under the same workload and build conditions.

## Scope and roadmap

**Implemented:** interpreted language core, Python domain modules, scientific helpers, sparse voxel operations, selected actor/channel primitives, CLI tools, Machine inspection, IDE services and the Tkinter editor shell.

**Evolving:** static analysis, ownership/effect semantics, richer IDE integration, native toolchain stages and expanded host/device adapters.

**Not claimed as complete:** native compiler, self-hosting, C++ ABI compatibility, full Pascal/Delphi/Fortran compatibility, production web framework, automatic deployment, OS sandbox or full LSP IDE.

## Documentation

- [Articulatory Syntax](docs/ARTICULATORY_SYNTAX.md) · [Engineering Doctrine](docs/SAMBU_ENGINEERING_DOCTRINE.md)
- [Systems Architecture](docs/CRIPPLE_SYSTEMS_ARCHITECTURE.md) · [Voxel Reference](docs/VOXELS.md)
- [Creative Data Governance](docs/CREATIVE_DATA_GOVERNANCE.md) · [Creative Metadata JSON Schema](schemas/creative-metadata.schema.json) · [Studio Guide](docs/DUCK_STUDIO.md)
- [Source and tests](https://github.com/bboroski/SAMBU/tree/main) · [Issues](https://github.com/bboroski/SAMBU/issues)

## Contributing & license

Focused pull requests are welcome. Include a minimal reproducer, expected/actual behavior, relevant tests and any security or domain assumptions. MIT — see [LICENSE](LICENSE).

<div align="center">

**SAMBU — model clearly. compose carefully. verify honestly.** 🦆

*Stay curious. Follow the trail. Keep the flock moving.*

</div>
