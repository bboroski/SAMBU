# Production Release Standard

**Repository:** bboroski/SAMBU  
**Default branch:** `main`  
**Project profile:** Python package with native/CMake subsystems  
**Existing workflow inventory:** 11 workflow file(s) were visible at the time this baseline was prepared.

## Purpose and scope

This document turns the six-domain, 666-control production-readiness model into an enforceable release process without flattening this repository's identity or replacing its current build system. It is a policy and implementation checklist, not a claim that every control is already active.

Preserve the existing Python packaging and native workflows; use the repository's existing `pyproject.toml`, CMake subdirectories, and test suite as the authoritative commands.

## 1. Repository architecture and ownership

- Keep application source, tests, documentation, automation, assets, and packaging responsibilities explicit. Do not reorganize established project layouts merely to match a generic template.
- Keep generated output, caches, local IDE state, secrets, and temporary files out of Git. Commit safe configuration examples only.
- Maintain `.gitattributes` for deterministic text handling and a project-appropriate `.gitignore`.
- Maintain `README.md`, a deliberate `LICENSE` decision, `SECURITY.md`, `CONTRIBUTING.md`, and `CODEOWNERS`. Missing items are findings to close; never invent a license or a security contact.
- Keep the default branch protected. Require pull requests, at least one independent approval (two for high-risk code), current branch state, resolved review conversations, passing required checks, stale-approval dismissal, and no force-push/deletion. Enable linear history only when the selected merge strategy supports it.

## 2. Git history, versioning, and review

- Use SemVer for released software: `MAJOR.MINOR.PATCH`; reserve pre-release identifiers for release candidates such as `v1.4.0-rc.1`.
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `test:`, `build:`, `ci:`, `chore:`, and `revert:`.
- Keep changes reviewable. Rebase/squash work-in-progress commits before merge only when doing so preserves authorship and traceability.
- Sign commits/tags where contributor keys and repository policy permit it. Do not commit signing keys.
- Require PR descriptions to state intent, risk, tests run, migration impact, and rollback approach for production-facing changes.

## 3. Local engineering quality

- Run the project's actual formatter, linter, static type checker, and tests before opening a PR. Tool choice must follow the repository's language and lockfiles.
- Use pre-commit/Husky or equivalent hooks for quick local checks; do not rely on hooks as the only CI control.
- Scan staged changes for secrets before push. Rotate any credential that was ever committed; deleting it in a later commit does not make it safe.
- Remove dead code and unused dependencies through reviewed changes, not blind automated deletion.
- Set coverage thresholds only after a trustworthy baseline exists. Prefer preventing coverage regressions over imposing an arbitrary percentage on legacy code.

## 4. CI/CD and supply-chain controls

- Preserve and extend the existing project-specific workflows; the baseline workflow added with this change is an additional repository hygiene check, not a replacement for build/test pipelines.
- Use explicit least-privilege workflow permissions. Pin third-party actions to verified full commit SHAs and review updates through Dependabot/Renovate.
- Use workflow concurrency cancellation for superseded PR runs and cache only reproducible dependencies/build outputs.
- Test supported runtimes and operating systems based on the project's actual support matrix. Add integration services only where required by the application.
- Run dependency vulnerability review and secret scanning. Use CodeQL/SAST where the language and repository size support it.
- Produce an SBOM (SPDX or CycloneDX) for distributable releases. Attach provenance and checksums to release artifacts.

## 5. Merge safety and recovery

- Enable reusable conflict resolution locally: `git config rerere.enabled true` and `git config merge.conflictstyle zdiff3`.
- During `git rebase main`, Git replays the topic commits onto `main`: in that conflict context, `--ours` is the upstream/rebased base and `--theirs` is the commit being replayed. During a normal `git merge main` from a topic branch, `--ours` is the topic branch and `--theirs` is `main`. Always inspect the diff; do not bulk-accept a side for lockfiles or generated files without regenerating and validating them.
- Use `git reflog` for local recovery, `git cherry-pick` for targeted fixes, and `git bisect` for regression isolation. Never force-update a shared branch to "fix" a conflict.

## 6. Documentation, release, and rollback

- Keep setup, architecture, configuration, API, support policy, and contribution instructions aligned with actual code.
- Automate changelog/release notes from reviewed commits. Never fabricate a version number or claim an artifact exists before a release workflow produces it.
- Freeze features before a release candidate. Validate the RC in staging and allow only reviewed fixes.
- Create signed annotated tags when signing is configured. Publish reproducible artifacts with SHA-256 checksums, SBOM, provenance, and release notes.
- Tag containers with immutable version and commit identifiers; reserve `latest` for channels where its mutability is understood.
- Define a rollback target, owner, deployment command, health checks, and data-migration rollback/forward-fix strategy before production deployment.
- After release, verify telemetry and critical user flows, sync hotfixes back to the development line, and close the release milestone only after unresolved work is explicitly carried forward.

## Current implementation status

### Added by this baseline change

- A `.github/workflows/production-baseline.yml` workflow runs on pull requests, pushes to `main`, and manual dispatch.
- The workflow enforces `git diff --check` and runs a dependency-free repository audit for JSON manifests, conflict markers, environment files, and missing release-governance controls.
- The audit reports readiness findings as warnings. This is deliberate: existing projects are at different maturity levels, and turning every legacy gap into a blocking check before remediation would create false-green/false-red CI behavior.

### Must still be configured or verified by a repository administrator

- Branch protection/ruleset requirements, required status checks, required reviewers and CODEOWNERS enforcement.
- GitHub secret scanning/Push Protection, CodeQL settings, dependency review policy, and private vulnerability reporting.
- Deployment environments, required approvers, environment secrets, GHCR permissions, signing identities, and release credentials.
- Successful full build/test runs on the supported platform matrix; this documentation change does not certify the application.

## Release acceptance checklist

- [ ] PR reviewed by an independent maintainer; all review conversations resolved.
- [ ] Required project-specific CI, tests, packaging, and platform checks pass.
- [ ] No secret, credential, private data, or unintended generated artifact is included.
- [ ] Dependencies and third-party Actions reviewed; workflow permissions are least-privilege.
- [ ] Version, changelog, migration notes, SBOM, provenance, and checksums are prepared where applicable.
- [ ] RC/staging verification and rollback target are documented.
- [ ] Release tag points to the reviewed commit; post-release health checks are green.

## Six-domain control map

| Control range | Domain | Required outcome |
|---|---|---|
| 001–111 | Architecture and governance | Stable layout, ownership, branch policy, version conventions |
| 112–222 | Local quality | Formatting, linting, typing, hooks, secret hygiene |
| 223–333 | CI/CD | Reproducible jobs, matrix, caches, security scans, coverage |
| 334–444 | Git safety | Rebase/merge correctness, conflict recovery, history traceability |
| 445–555 | Documentation and security | Maintainer guidance, vulnerability disclosure, API and changelog |
| 556–666 | Release and operations | RC, artifacts, SBOM, signed tags, monitoring and rollback |

The control ranges are an implementation map, not 666 individually automated tests. The project-specific build and test jobs remain authoritative.
