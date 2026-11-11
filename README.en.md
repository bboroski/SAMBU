<p align="center"><img src="assets/duck-ui/duck-mark.svg" alt="SAMBU mark" width="92"></p>
<h1 align="center">SAMBU</h1>
<p align="center"><strong>Scientific Modeling & Automation Environment</strong></p>
<p align="center"><strong>Experimental alpha</strong></p>
<p align="center"><a href="README.md">🇺🇦 Українська</a> · <a href="README.en.md">🇬🇧 English</a> · <a href="README.ru.md">🇷🇺 Русский</a></p>
<sub>Updated: 2026-11-11</sub>


## Contents

- [Current capabilities](#current-capabilities)
- [Quick start and verification](#quick-start-and-verification)
- [Architecture and verified scope](#architecture-and-verified-scope)
- [Duck Studio screenshots](#duck-studio-screenshots)
- [Engineering quality](#engineering-quality)
- [Documentation map](#documentation-map)
- [NUN Mesh and related repositories](#nun-mesh-and-related-repositories)
- [Design and documentation](#design-and-documentation)
- [License](#license)

> **SAMBU** — SAMBU is an experimental Python-hosted environment for programming, scientific modeling and reproducible workflows.

## Current capabilities
- Language core with lexer/parser, AST, functions, scopes, arrays, records and emoji syntax aliases.
- Scientific layer with SI quantities, dimensional checks, physical constants and reproducible sampling.
- Sparse voxel grids, chunks, Morton keys, octrees and graph operations.
- CLI, Tkinter IDE, test runner and a partial C11 native-compiler slice.

## Quick start and verification
```bash
python -m pip install -e .
python -m pytest
python one.py check
```

## Architecture and verified scope
The native compiler slice is not a complete source-to-machine-code toolchain. The IDE is not a full LSP implementation. Experimental features must not be described as production-ready.

## Duck Studio screenshots

These repository images show the application workspace, reports and XML inspector.

<p align="center"><img src="docs/images/duck-studio-overview.webp" alt="Duck Studio main workspace" width="960"></p>
<p align="center"><em>Duck Studio — main workspace</em></p>

<p align="center"><img src="docs/images/duck-studio-reports-findings.webp" alt="Duck Studio reports and findings" width="960"></p>
<p align="center"><em>Reports and findings</em></p>

<p align="center"><img src="docs/images/duck-studio-xml-inspector.webp" alt="Duck Studio XML inspector" width="960"></p>
<p align="center"><em>XML inspector</em></p>

## Engineering quality
- Run the checks appropriate to the target platform; host CI is not hardware qualification.
- Mark capabilities as implemented, partial or planned according to code, tests and evidence.
- A mockup, specification or open pull request is not proof of a production-ready feature.
- External integrations must be explicit, versioned, isolated and testable.

## Documentation map

- [Duck Studio](docs/DUCK_STUDIO.md)
- [IDE and editor](docs/IDE.md)
- [Native compiler architecture](docs/NATIVE_COMPILER_ARCHITECTURE.md)
- [Emoji programming](docs/EMOJI_PROGRAMMING.md)
- [Ecosystem architecture](docs/ECOSYSTEM_ARCHITECTURE.md)

## NUN Mesh and related repositories

<p align="center"><img src="assets/nun-mesh.svg" alt="NUN Mesh repository contracts and integration boundaries" width="960"></p>
[SAMBU](https://github.com/bboroski/SAMBU) · [ToolNG](https://github.com/bboroski/ToolNG) · [ReaperCripple](https://github.com/bboroski/ReaperCripple) · [Kloz](https://github.com/bboroski/Kloz) · [CO](https://github.com/bboroski/CO) · [SaintSI](https://github.com/bboroski/SaintSI) · [Klipot](https://github.com/bboroski/Klipot) · [NUN](https://github.com/bboroski/NUN) · [NUNLauncher](https://github.com/bboroski/NUNLauncher)

Each repository retains its canonical name, code, APIs, release lifecycle and ownership boundaries. Integration means versioned contracts, not automatic merging of independent runtimes.

## Design and documentation
The shared interface direction is **Duck Black / Yellow**: deep black `#111111` surfaces and signal-yellow `#FFD600` accents for actions and state, readable typography, accessible contrast, keyboard navigation and reduced-motion support. See [design/DUCK_UI_SYSTEM.md](design/DUCK_UI_SYSTEM.md) when present.

## License
MIT

---
**Built with care for engineering, clarity and people.**
