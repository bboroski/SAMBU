# SAMBU — Scientific Modeling & Automation Environment

**A scientific language and engineering environment for reproducible computation, modeling, and automation.**

SAMBU is an experimental interpreted language with a Python toolchain. It combines a language core, scientific computation, domain modules, sparse-voxel modeling, workflow models, and developer tools.

[Українська](README.md) · [English](README.en.md) · [Русский](README.ru.md) · [Source repository](https://github.com/bboroski/SAMBU)

## Capabilities

- **Language core:** lexer/parser, source-spanned AST, functions, scopes, arrays, records, classes, and bounded loops.
- **Scientific models:** SI quantities, dimensional checks, physical constants, statistical mechanics, and reproducible sampling.
- **Spatial data:** sparse voxel grids, chunks, Morton keys, octrees, surface geometry, and graph operations.
- **Engineering tools:** CLI, Tkinter IDE, test runner, architecture checks, and workflow utilities.
- **Text metadata:** deterministic analysis of structure, repetition, approximate prosody, and semantic markers. This is data analysis, not text generation or a judgment of artistic quality.

## Quick start

Requirements: Python 3.10+ and Git. The interpreter has no mandatory third-party runtime dependencies.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
sambu --version
~~~

Run a program:

~~~bash
sambu examples/ideal_gas.sambu
sambu -c 'print("Hello from SAMBU")'
~~~

The <code>sambu</code> command, <code>sambu</code> Python package, and <code>.sambu</code> extension remain as compatibility interfaces. The new CLI alias is <code>sambu</code>.

## Tools and verification

~~~bash
python -m pytest
sambu --help
~~~

The IDE supports file editing, execution, output, and basic diagnostics. It is **not** a full LSP IDE. A native compiler and a complete static type/effect system remain future development areas.

## Architecture and boundaries

SAMBU is a Python-hosted alpha project. Flask, Django, and FastAPI adapters are optional. An adapter or integration profile does not imply a finished production integration.

- [Articulatory grammar](docs/ARTICULATORY_SYNTAX.md)
- [Ecosystem architecture](docs/ECOSYSTEM_ARCHITECTURE.md)
- [Multilingual signal pipeline](docs/MULTILINGUAL_SIGNAL_PIPELINE.md)

## Technical identity

**SAMBU** is the canonical environment name and the new CLI alias. Historical distribution, Python-package, and language-extension names remain for compatibility with existing scripts and imports; replacing them requires a separate API migration.

## License

MIT. See [LICENSE](LICENSE).


## One-knob launch

- **Windows:** double-click `one.cmd` or run it from a terminal.
- **Any OS:** `python one.py` runs this project's default workflow; `python one.py check` runs headless verification.
- Desktop/IDE projects launch their application after checks; system and embedded modules build and test their host version.
- Host tests do not replace qualification on the target board, device, or production fixture.

## NUN system and Android platform

The canonical registry now includes two additional independent projects:

- **NUN** — an early x86-64 OS boot foundation with pinned native adapters from Kloz, CO, SaintSI and the ReaperCripple supervisor.
- **NUNLauncher** — an Android HOME application with app discovery, search and launch through LauncherApps.

Fortran, Pascal and Delphi/Object Pascal are planned as user-space toolchains, runtimes and SDKs over a stable C ABI, not as privileged kernel code. See the [registry](ecosystem/registry.json) and [ecosystem architecture](docs/ECOSYSTEM_ARCHITECTURE.md).
