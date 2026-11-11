# SAMBU
**Scientific Modeling & Automation Environment**

[Українська](README.md) · [English](README.en.md) · [Русский](README.ru.md)

An experimental Python-hosted environment for programming, scientific modeling and reproducible workflows.

## Features
- Language core with lexer/parser, AST, functions, scopes, arrays and records.
- SI quantities, dimensional checks, physical constants and reproducible sampling.
- Sparse voxel grids, chunks, Morton keys, octrees and graph operations.
- Static semantic analysis, CLI, Tkinter IDE and test runner.
- Partial C11 native-compiler slice; not a complete compiler.

## Run and test
```bash
python -m pip install -e .
python -m pytest
python one.py check
```

## Scope
The native compiler does not provide a complete source-to-machine-code pipeline. The IDE is not a full LSP implementation. Experimental features are not production-ready.

## Project documentation
![Duck Studio workspace](docs/images/duck-studio-overview.webp)

![Duck Studio reports](docs/images/duck-studio-reports-findings.webp)

![Duck Studio XML inspector](docs/images/duck-studio-xml-inspector.webp)

## Related
[Duck Studio](docs/DUCK_STUDIO.md) · [IDE](docs/IDE.md) · [semantic analysis](docs/SEMANTIC_ANALYSIS.md)

[Luci](https://github.com/bboroski/Luci) · [Hellduck](https://github.com/bboroski/Hellduck)

## License
MIT

---
**两情若是久长时，又岂在朝朝暮暮。**
*When love is lasting, must two hearts be together every day?*
— Qin Guan, 《鹊桥仙》
