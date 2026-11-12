# SAMBU — Smart Integration Pipeline

## Purpose

This document records the merge and verification contract for the canonical repository **SAMBU**. The workflow `.github/workflows/smart-pipeline.yml` adds a stable repository-integrity check; it complements rather than replaces the project's build, unit, integration, sanitizer, and platform-specific workflows.

## Automated checks

Existing CI: `tests.yml` (Python 3.10–3.13, unit/CLI/example tests), `web-integrations` and `engine-bridges` jobs, plus `duck-quality-gate.yml`, `ecosystem-contracts.yml`, `native.yml`, and platform workflows.

The Smart Pipeline check validates:
- the canonical trilingual onboarding files (`README.md`, `README.en.md`, and `README.ru.md`);
- the presence and non-empty UTF-8 content of Markdown documentation under `docs/`;
- JSON files in project configuration directories (`ecosystem/`, `schemas/`, `manifests/`, `registry/`, `spec/`, `profiles/`, and `design/`, when present);
- Python source syntax without importing or executing application modules;
- YAML syntax for every workflow under `.github/workflows/`;
- the existing shared Duck quality gate and dedicated documentation verifier, when those scripts are present.

Project-specific CI workflows remain independent checks. A green Smart Pipeline result is not, by itself, evidence that all native builds or integration tests passed.

## Pull-request and merge policy

1. Develop on a short-lived feature/fix branch. Do not push directly to `main`.
2. Open a pull request targeting `main`; update the branch from the latest base before final review.
3. Resolve semantic conflicts manually. Do not use blanket conflict auto-resolution for source code, schemas, or generated artifacts.
4. Merge with **Squash and Merge** after the Smart Pipeline check, every applicable project-specific CI check, and the repository's review requirements have passed.
5. Keep `main` non-deletable and reject non-fast-forward updates. Require pull requests and the required status checks in an **active GitHub ruleset**.

## Required GitHub settings

The workflow file cannot activate repository rulesets or branch protection by itself. In GitHub repository settings, create or update an active ruleset targeting `main` and require:
- pull requests before merging;
- the status check **Smart Pipeline / Repository Integrity**;
- every applicable project-specific CI check listed above;
- review approval appropriate to the repository's contributor model;
- stale approval dismissal or approval of the latest push where available;
- linear history, no force-push, and no branch deletion.

Do not enable automatic merging until these requirements are active and the required check names have been selected. This repository workflow intentionally does not merge PRs, bypass reviews, or write generated files back to contributor branches.

## Documentation synchronization

When a change affects public interfaces, command-line flags, configuration formats, schemas, events, module relationships, or supported platforms, update the corresponding README language variants and relevant files in `docs/` in the same pull request. Update architecture diagrams and API/schema descriptions with the implementation. Add an explicit “Documentation impact” note to the PR description when no documentation change is needed.

API documentation generation is only run when this repository has a real, maintained generator and a deterministic command for it. The pipeline does not invent an OpenAPI/TypeDoc/Sphinx command or commit speculative output.

## Coverage and concurrency policy

An 80% coverage threshold should be enabled per test suite only after that suite publishes a reliable coverage report and has a measured baseline. The Smart Pipeline does not report a fabricated coverage percentage. Concurrency, race, sanitizer, and performance checks remain in the project's native CI where the applicable runtime and hardware model are known.
