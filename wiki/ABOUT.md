# About SAMBU

## Overview

**SAMBU** is an experimental interpreted programming language and modeling toolkit. It combines a compact domain-specific language with Python APIs for scientific calculations, object-oriented models, architecture planning, workflow analysis, content-integrity checks, bounded data processing, voxel computation and developer tooling.

The repository describes the language as a small language with a wide horizon. Its design emphasis is not maximum implicit magic; it is visible assumptions, composable components and inspectable changes.

## Name

The repository's current README uses the expansion **Statistical Analysis · Modeling · Systems · Trust**. An older language guide used **Statistical Analysis & Modeling with Boltzmann Utilities**. The broader current expansion reflects the project's growth beyond its original statistical-mechanics interpreter. Treat the older wording as historical context rather than a second language name.

## Project identity

| Property | Current repository information |
|---|---|
| Repository | [bboroski/SAMBU](https://github.com/bboroski/SAMBU) |
| Package | `sambu-language` |
| Repository version label | `0.11.0-alpha` |
| Implementation | Python |
| Minimum Python | 3.10 |
| License | MIT |
| Maturity | Alpha / experimental |
| Main command | `sambu` |
| Tooling commands | `sambu-studio`, `sambu-test` |

The language is interpreted. It should not be described as a native ahead-of-time compiler or as a replacement for Python, Django, Flask, FastAPI, a database, a game engine or a production certification authority.

## Why the project exists

SAMBU aims to make assumptions and boundaries visible while allowing different computational domains to share one consistent environment. The same project can express a scientific calculation in SAMBU syntax, model an architecture in Python, inspect selected project configuration, or prepare a portable voxel payload.

The project therefore has two related surfaces:

1. **The SAMBU language** — syntax, lexer, parser, AST, interpreter, runtime values and language built-ins.
2. **The SAMBU Python toolkit** — modules and command-line utilities that provide richer host-side models and integrations.

These surfaces are related but not interchangeable. A capability available from a Python import is not necessarily a construct in the SAMBU language itself.

## Design principles

1. **Explicit over implicit.** Inputs, dimensions, permissions, assumptions and external boundaries should be visible.
2. **Composable components.** Scientific, system, UI and integration layers should remain focused and independently usable.
3. **Inspectable changes.** Diagnostics, previews, test results and reversible patches should explain what happened.
4. **Bounded by default.** Loops, samples, retries, chunks, parser inputs and other expensive operations should have documented limits.
5. **Honest trust.** Integrity checks must not be presented as proof of identity, ownership or legal authority.
6. **Compatibility-aware evolution.** New capabilities should be added without casually breaking existing interfaces.
7. **Measured performance.** Performance claims should be supported by repeatable benchmarks rather than intuition.

## Project boundaries

SAMBU includes calculators, models, plans, static inspection and starter integration code. Those do not imply automatic external execution. For example:

- A queue plan does not publish a RabbitMQ message.
- An order pipeline checklist does not create or confirm a Magento order.
- A UI model does not ship a browser renderer.
- A provider-neutral AI router does not include vendor credentials or make a network request by itself.
- A voxel engine bridge is source code for a host project, not a prebuilt plugin for every engine.
- A portfolio hash check does not authenticate a person or prove asset ownership.

## Related pages

- [Getting started](GETTING-STARTED.md)
- [Language tour](LANGUAGE-TOUR.md)
- [Frameworks](FRAMEWORKS.md)
- [Design philosophy and roadmap](DESIGN-PHILOSOPHY-AND-ROADMAP.md)
