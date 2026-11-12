# Jun-Jun — SAMBU

Jun-Jun is this repository's conservative engineering guardian.

## Project role
Scientific Modeling & Automation Environment

## Mission
Preserve interpreter semantics, AST checks, reproducible scientific calculations and native C11 boundary.

## What runs
The GitHub Actions workflow `.github/workflows/jun-jun-guard.yml` runs on pushes, pull requests and manual dispatch. It performs a bounded, read-only hygiene pass over tracked source-like files:
- detects common merge-conflict markers;
- detects high-confidence private-key and common cloud/GitHub token markers;
- reports file and line only, never the matching secret value.

## Safety boundaries
Jun-Jun does **not** modify files, install dependencies, execute project code, access deployment secrets, publish artifacts, merge pull requests, or claim that a build / test / hardware qualification succeeded. This first stage is intentionally observation-only.

## Configuration
See [`.jun-jun/policy.json`](.jun-jun/policy.json). Project-specific checks should be added only after their exact commands and platform requirements are verified.

## Local expectations
Run the repository's documented build and test commands separately. A green Jun-Jun job means only that the listed hygiene checks passed; it is not a product security certification.
