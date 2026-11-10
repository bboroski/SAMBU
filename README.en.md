<p align="center"><img src="assets/duck-ui/duck-mark.svg" alt="SAMBU mark" width="92"></p>
<h1 align="center">SAMBU</h1>
<p align="center"><strong>Scientific Modeling &amp; Automation Environment</strong></p>
<p align="center">
<img src="https://img.shields.io/badge/STATUS-EXPERIMENTAL%20ALPHA-FFD600?style=for-the-badge&labelColor=111111" alt="Experimental alpha">
<img src="https://img.shields.io/badge/CORE-PYTHON%20%2B%20C11-FFD600?style=for-the-badge&labelColor=111111" alt="Python and C11">
<img src="https://img.shields.io/badge/LICENSE-MIT-FFD600?style=for-the-badge&labelColor=111111" alt="MIT">
</p>
<p align="center"><a href="README.md">🇺🇦 Українська</a> · <a href="README.en.md">🇬🇧 English</a> · <a href="README.ru.md">🇷🇺 Русский</a></p>

---

**SAMBU brings programming, scientific modeling, and reproducible workflows into one experimental engineering environment.** It is built for people who need inspectable models, controlled computation, and results that can be tested.

## Value and capabilities

- **Language core:** lexer/parser, AST with source spans, functions, scopes, arrays, records, classes, and bounded loops.
- **Scientific layer:** SI quantities, dimensional checks, physical constants, statistical mechanics, and reproducible sampling.
- **Spatial data:** sparse voxel grids, chunks, Morton keys, octrees, surface geometry, and graph operations.
- **Tooling:** CLI, Tkinter IDE, test runner, architecture checks, and workflow models.
- **Text metadata:** deterministic structural analysis, repetition, approximate prosody, and semantic markers.
- **Native compiler slice:** a separate C11 track with typed HIR/MIR/LIR and IR checks; it is not yet a complete native compiler.

## Quick start

Requires Python 3.10+ and Git. The interpreter has no mandatory third-party runtime dependencies.

~~~bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
sambu --version
~~~

Run an example and the checks:

~~~bash
sambu examples/ideal_gas.sambu
sambu -c 'print("Hello from SAMBU")'
python -m pytest
python one.py check
~~~

On Windows, <code>one.cmd</code> is available. <code>python one.py</code> runs the project's standard workflow.

## Architecture and limits

SAMBU is a Python-hosted experimental alpha. The IDE supports file editing, execution, output, and basic diagnostics, but is not yet a full LSP IDE. The native compiler slice does not yet include a complete source-parser bridge, CFG/phi-node support, an optimization pipeline, an object writer, or machine-code generation. A complete static type and effect system remains future work.

## Quality management

| Control | Acceptance criterion |
|---|---|
| Reproducibility | Identical inputs and settings produce verifiable results |
| Quality | pytest, CLI smoke tests, and architecture checks |
| Scope | Experimental features are labelled accurately |
| Compatibility | API changes include explicit migration notes |
| Integrations | An adapter does not imply a completed production integration |

Documentation: [grammar](docs/ARTICULATORY_SYNTAX.md) · [ecosystem architecture](docs/ECOSYSTEM_ARCHITECTURE.md) · [multilingual pipeline](docs/MULTILINGUAL_SIGNAL_PIPELINE.md) · [wiki](wiki/README.md).

## Ecosystem

SAMBU is the language and modeling layer. Related projects: [ToolNG](https://github.com/bboroski/ToolNG), [ReaperCripple](https://github.com/bboroski/ReaperCripple), [Kloz](https://github.com/bboroski/Kloz), [CO](https://github.com/bboroski/CO), [SaintSI](https://github.com/bboroski/SaintSI), [Klipot](https://github.com/bboroski/Klipot), [NUN](https://github.com/bboroski/NUN), [NUNLauncher](https://github.com/bboroski/NUNLauncher), [Fragile-Baby](https://github.com/bboroski/Fragile-Baby), and [Luci](https://github.com/bboroski/Luci).

## License and contributions

MIT — see [LICENSE](LICENSE). Review the architecture and tests before contributing. Changes should be scoped, reproducible, and documented.

---

**Made with love for knowledge, engineering, and people.**