# Octopus Ippon Release Protocol — SAMBU

This workflow validates the existing Python-hosted language and packages its source and wheel distributions.

## Entry points
- Existing test workflows remain authoritative for pull-request validation.
- `workflow_dispatch` executes the release checks and uploads evidence without publishing.
- A pushed `v*` tag publishes only after the Python 3.10–3.13 test matrix and packaging job pass.

## Release gates
1. Install the project independently on Python 3.10, 3.11, 3.12 and 3.13.
2. Run unit tests and the SAMBU test runner twice.
3. Validate machine architecture and example catalogues using JSON output.
4. Execute representative language programs.
5. On Python 3.12, require the tag to match `project.version` in `pyproject.toml`.
6. Build sdist and wheel, run Twine metadata validation, generate SPDX JSON SBOM and SHA-256 checksums.
7. Generate GitHub build-provenance attestations, upload evidence and publish only from a version tag.

## Safety boundaries
- This workflow does not publish to PyPI; it creates a GitHub Release with auditable package artifacts.
- It does not modify `main`, create tags or change package version.
- A failed compatibility or packaging gate blocks publication.
- Experimental language features remain experimental; passing CI is not a production-readiness claim.

## 666-iteration rollout model
The 666 count is a controlled improvement backlog, not 666 fake test passes or 666 commits. Each real iteration must include a concrete change, a reproducible test, retained evidence and a rollback path. The workflow serves as the acceptance gate for each iteration.
