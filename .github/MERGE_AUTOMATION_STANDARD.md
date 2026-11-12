# GitHub Merge Automation Standard

**Scope:** this repository and its project-specific architecture. This standard governs integration and release safety; it does not impose a shared application architecture, language, directory layout, or build system.

## 1. Source of truth

- Discover the repository's default branch from GitHub metadata. The configured default branch—not an assumed branch name—is the integration target.
- Product, CI, security, and documentation changes are developed on topic branches and proposed through pull requests.
- The default branch is the canonical current state. A PR head is the incoming change set.
- Never use a force push or administrative bypass to make a PR appear mergeable.

## 2. Branch and PR discovery

Before changing or merging anything, inventory:
- default branch and its current head SHA;
- open, draft, closed, and merged pull requests;
- head/base branch names and SHAs;
- changed paths, patch size, review state, required checks, and mergeability;
- related PRs that touch the same paths or implement overlapping requirements.

Do not infer that two PRs are duplicates solely because their titles or branch names match. Cross-repository changes must be checked against each project's own source, tests, and release contract.

## 3. Safe conflict resolution

Resolve conflicts per file and per semantic unit—not by blindly choosing all current-side or all incoming-side changes.

1. Re-read the base version, incoming version, surrounding code, tests, and documented project invariants.
2. Preserve valid behavior from both sides when the requirements are compatible.
3. Keep the base branch's established contracts unless the PR explicitly and safely changes them.
4. Re-generate lockfiles and generated artifacts only with the repository's declared toolchain.
5. Re-run focused tests and the complete required CI after conflict resolution.
6. If the correct behavior cannot be established from code, tests, or requirements, leave the conflict unresolved and request a human decision.

A conflict-free textual merge is not proof of a correct semantic merge.

## 4. Merge-readiness gate

A PR is eligible for merge only when all of the following are true:

- It is open, not draft, and GitHub reports it mergeable without conflicts.
- The latest PR head SHA has not changed since the final inspection.
- Every required status check for that repository has succeeded on the latest head.
- Required reviews are satisfied; no active changes-requested review remains.
- All required review threads are resolved.
- CodeQL and secret-scanning checks have completed successfully where configured.
- Project-specific tests, build, packaging, and release checks have passed.
- The proposed merge method is allowed by that repository's ruleset.

A skipped, pending, cancelled, missing, or unknown required check is not a passing check. Never mark a check as required before it has emitted successfully at least once on a PR in this repository.

## 5. Merge execution

- Prefer the repository's permitted linear-history method (squash or rebase where configured).
- Use GitHub auto-merge only after all required checks and review gates are configured and verified.
- Re-check the PR's current head SHA immediately before merging; use an expected-head-SHA guard where the merge API supports it.
- Never merge with admin privileges to bypass a failing or missing gate.
- Preserve release tags, published artifacts, migrations, and backward-compatibility guarantees unless the PR explicitly owns those changes.

## 6. Old-PR rehabilitation

Classify each open PR as: ready, needs-rebase, conflict, checks-failing, review-blocked, draft/incomplete, duplicate, superseded, or stale-but-valuable.

- Merge only unique, reviewed changes that pass the merge-readiness gate.
- Rebase or update a branch only after inspecting its diff and confirming that the new base will not erase project work.
- Close a duplicate or superseded PR only after identifying the replacement and confirming that no unique commits or review decisions would be lost.
- Do not delete branches or close PRs merely because they are old.
- Preserve review history and report unresolved blockers explicitly.

## 7. CI and security requirements

- Set explicit least-privilege permissions at workflow or job level.
- Use workflow concurrency groups to prevent stale duplicate runs.
- Analyze languages actually present in the repository. Choose CodeQL build modes per language and repository build system:
  - use none for interpreted languages and supported compiled languages when a build is unnecessary;
  - use autobuild only where the build layout can be detected reliably;
  - use manual only with verified repository-specific build commands.
- Keep secret scanning enabled on pull requests, default-branch pushes, and a scheduled run.
- Keep GitHub Actions dependencies under Dependabot updates.
- Do not claim that a security scan, branch rule, or setting is enabled until its workflow run or GitHub setting has been verified.

## 8. Architecture preservation

This policy is intentionally shared; implementation is not. Each repository retains its own language mix, targets, CI matrix, packaging, release process, and module boundaries. Shared automation must adapt to those existing contracts rather than rewrite them.
