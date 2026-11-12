# Linguistic Heritage Engine integration

This repository is enrolled in the cross-repository Linguistic Heritage Engine initiative.

## Integration contract

- Canonical research core: [bboroski/SAMBU](https://github.com/bboroski/SAMBU), package path `linguistic_heritage/`.
- Data contract: `schemas/linguistic-heritage-letter.schema.json` in the canonical repository.
- Initial case study: Cyrillic Ы / ы.
- Evidence states: `established`, `qualified`, `hypothesis`, `unsupported`.

## Safe integration boundary

This change adds a declarative manifest only. It does not modify application runtime, dependencies, build scripts, secrets, or existing workflows. A project-specific adapter should be added only after the repository's language, entry points, and test framework have been reviewed.

## Research policy

Do not promote a hypothesis to a fact without a traceable source. Keep the history of the written grapheme distinct from the history of the spoken phoneme. Do not infer borrowing from sound similarity alone.

## Development workflow

All changes are proposed on `feature/linguistic-heritage-engine` and reviewed through a Pull Request. The default branch is not modified directly.
