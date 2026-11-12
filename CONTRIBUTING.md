# Contributing to SAMBU

SAMBU is a language/runtime project with Python tooling, native components, and optional engine adapters. Keep changes within the owning subsystem; do not replace the compiler/runtime architecture with repository-wide generic scaffolding.

## Required workflow

1. Open or link an Issue for behavioral, architecture, security, or compatibility changes.
2. Create a focused branch: `feat/<topic>`, `fix/<topic>`, `docs/<topic>`, or `security/<topic>`.
3. Keep public language/runtime behavior documented in the relevant README and `docs/` contract.
4. Preserve offline operation of catalogues and validators. Network-dependent integrations must remain separately testable.
5. Never commit credentials, private keys, production data, generated build output, or local environment files.

## Validation

Run the same baseline used by project CI:

```bash
python -m pip install -e .
python tools/validate_biology_terms.py
python tools/validate_reaper_domain.py
python -m unittest discover -s tests -v
sambu-test tests --repeat 2
```

For web integration changes:

```bash
python -m pip install -e ".[web]"
python -m unittest discover -s tests -p test_integrations.py -v
```

For the Bevy adapter:

```bash
cargo check --manifest-path engine_adapters/bevy/Cargo.toml
```

Run relevant example/CLI checks from `.github/workflows/tests.yml` when changing those surfaces. Do not claim a platform or adapter is supported unless its corresponding build/test completed.

## Commits and releases

Use Conventional Commit subjects: `feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `test:`, `build:`, `ci:`, or `chore:`. Use `!:` and a `BREAKING CHANGE:` footer for breaking changes. Releases follow SemVer (`MAJOR.MINOR.PATCH`); update the changelog and compatibility notes before tagging.

## Pull request checklist

- Explain the user-visible or compiler/runtime impact.
- Identify affected language contracts, native targets, and adapters.
- List exact validation commands and results.
- Add/update tests for behavior changes.
- Describe migration and rollback for breaking changes.
- Request review for changes in `.github/`, `src/`, native interfaces, and release/security configuration.
