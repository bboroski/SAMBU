# GitHub Merge Automation Standard

**ID:** GMAS-1.0
**Status:** Repository adoption proposal
**Effective:** After review and merge
**Scope:** Branch discovery, merge analysis, conflict handling, CI evidence, Pull Request preparation and historical PR recovery.

> This standard is an additive GitHub governance layer. The repository's own architecture, APIs, toolchain, tests, release process and project-specific engineering rules remain authoritative.

## 1. Non-negotiable architecture boundary

1. Treat each repository as an independent product and source of truth.
2. Discover and document its native architecture before proposing a merge or refactor.
3. Do not impose a common runtime, directory layout, naming scheme, build system, dependency set or release cadence.
4. Preserve project-specific workflows and required checks. Add this audit as a supplemental control; never replace native CI.
5. Do not copy code or configuration between repositories merely to make them look alike.
6. A green merge audit is not a build, integration, security, hardware or production-readiness certification.

## 2. Branch and Pull Request discovery

Automation must discover rather than assume repository state:

- Read the repository's actual default branch from GitHub metadata. Do not hard-code `main` as a universal rule.
- Enumerate branches and open PRs with pagination. Record base/head refs and SHAs, draft state, creation/update timestamps, mergeability, reviews, status checks and changed paths.
- Identify branches without PRs as candidates only. Their intent and target branch must be reviewed before opening a PR.
- Classify PRs as: `draft`, `ready`, `blocked-conflict`, `blocked-ci`, `blocked-review`, `stale`, `duplicate-candidate`, `merge-ready`, `merged` or `closed-unmerged`.
- Never delete a branch, close a PR, retarget a PR or discard commits merely because it appears old or duplicated.

A PR's displayed mergeability can be temporarily unknown while GitHub calculates it. Re-fetch metadata before making a decision.

## 3. Merge direction and terminology

For a PR targeting a base branch:

- **Current / base / target** is the code already on the destination branch.
- **Incoming / head / source** is the proposed PR branch.
- In a normal merge with the base checked out, Git's `ours` refers to the current side and `theirs` refers to the incoming side. Rebase, cherry-pick and custom merge drivers can change the practical meaning; verify the operation before relying on these labels.

Every conflict report must identify the repository, PR number, target ref/SHA, source ref/SHA and exact conflicting paths.

## 4. Merge decision model

| Condition | Automation decision |
|---|---|
| No overlapping changes and Git produces a clean three-way merge tree | Mark merge-analysis PASS; continue to native CI and review gates |
| Same file changed on both sides, but Git can merge cleanly | Mark REVIEW when the file is architecture-, security-, API-, build- or release-sensitive |
| Git reports a content, add/add, modify/delete, rename or directory conflict | BLOCK automatic merge; prepare a per-file review report |
| CI is failing, pending, missing or not applicable | BLOCK promotion until the repository's required checks are verified |
| Required review is missing, changes are requested or review threads remain unresolved | BLOCK promotion |
| Head SHA changed after validation | Re-run merge analysis and all relevant checks |
| Scope, provenance, generated-file source or migration behavior is unclear | REVIEW; do not guess |

A clean merge tree means only that Git can combine the trees without unresolved textual conflicts. It does not mean that the application works.

## 5. Safe conflict-resolution protocol

1. Freeze the evidence: capture the exact base and head SHAs, merge base, changed-file lists and current CI/review state.
2. Inspect the base-side and head-side diffs independently. Read the complete affected functions/configuration/schema, not only conflict markers.
3. Resolve each file according to its semantics and project ownership:
   - **Keep current** only when the target branch's implementation is intentionally authoritative and the incoming behavior is not required.
   - **Take incoming** only when the PR change is intended, compatible and validated against current project behavior.
   - **Combine manually** when both sides contain required behavior.
   - **Regenerate** lockfiles, generated code or compiled artifacts with the repository's canonical tool where possible; do not hand-edit generated output without a project-specific reason.
4. Require explicit path-level rationale for every side selection. Record it in the PR description or review discussion.
5. Re-run formatters, unit/integration tests, build/package checks and domain-specific validation affected by the resolution.
6. Inspect the final diff against the current base and confirm no unrelated files or behavior were lost.
7. Re-check the head SHA and target branch immediately before merge.

**Forbidden:** repository-wide `git checkout --ours .`, `git checkout --theirs .`, blind conflict-marker replacement, force-pushing protected branches, silently discarding a side, or auto-merging a conflict based solely on file age/name.

Automatic resolution is allowed only for a deterministic, explicitly documented, path-scoped rule whose owner, validation command and rollback are defined. No global incoming/current default exists.

## 6. CI and quality gates

- Keep each project's existing CI and required status checks authoritative.
- Use least-privilege workflow permissions; default to read-only. Grant write permissions only to a dedicated job that demonstrably needs them.
- Protect workflows against concurrent runs for the same PR while allowing unrelated PRs to proceed.
- Set finite job timeouts and pin third-party Actions to reviewed immutable commit SHAs where practical.
- Do not expose secrets to untrusted fork code. Never run `pull_request_target` with an untrusted checkout.
- Report check names, conclusions, skipped checks and unavailable evidence. A missing check is not PASS.
- Do not infer test commands from another repository. Use the project's documented scripts and existing workflow matrix.
- A CI result from an older head SHA is stale evidence and must not authorize a merge of a newer head.

The included audit workflow is informational about GitHub commit status and check-runs and blocking for unresolved merge conflicts / whitespace errors. It does not replace native test workflows or configure branch protection.

## 7. Pull Request preparation contract

Every automated or manually prepared PR should include:

- concise, project-specific title and purpose;
- base and head branch names;
- summary of changes and affected subsystems;
- files with architecture/API/security/build/release impact;
- merge-conflict findings and path-level decisions;
- native CI checks run, results, skipped checks and commands;
- review/ownership requirements;
- migration, compatibility and rollback notes;
- explicit limitations and unverified claims.

Keep exploratory work in Draft until scope, tests and acceptance criteria are ready. Do not mark a PR ready merely because it is conflict-free.

## 8. Historical Pull Request recovery

For every existing open PR:

1. Refresh PR metadata and compare its head against the current target branch.
2. Group duplicate or overlapping proposals by changed paths, API surface and intent; identify a canonical PR without closing the others automatically.
3. Check whether the branch is still needed, whether its commits are unique, and whether dependencies must land first.
4. Recompute mergeability and inspect conflicts against the current target.
5. Verify required CI on the exact head SHA and inspect reviews / unresolved threads.
6. Update the branch only through a normal merge/rebase process that preserves authorship and is reviewed; never force-push shared work by default.
7. Merge only when all repository-specific gates pass and the authorized merge method is known.
8. Leave blocked, draft, duplicate-candidate and ambiguous PRs open with a clear reason and next action.

A historical backlog is not a batch-merge instruction. Age alone is not a reason to merge, close or delete.

## 9. Promotion gate

A PR is eligible for merge only when all applicable items are true:

- [ ] Target branch and source head are confirmed and current.
- [ ] Merge analysis is clean; or all conflicts have documented per-path resolutions.
- [ ] The final diff contains no unintended deletions or unrelated changes.
- [ ] Native required CI checks pass on the current head SHA.
- [ ] Required approvals are present and requested changes are addressed.
- [ ] Required conversations are resolved.
- [ ] Migration, security, compatibility and release impacts are understood.
- [ ] Merge method matches repository policy.
- [ ] Rollback/recovery path is known for material behavior changes.

Use GitHub auto-merge only when repository rules are configured and all required checks/reviews are enforced. Otherwise require an authorized maintainer to perform the merge.

## 10. Audit record and rollback

For every audit, retain: timestamp, repository, PR number, base/head refs and SHAs, merge-base SHA, mergeability result, conflict paths, status/check-run evidence, review state, decision, actor and follow-up action. Avoid logging secrets or unrelated personal data.

Never rewrite protected-branch history as a rollback. Prefer a reviewed revert commit or documented recovery procedure. If a merge causes a regression, stop further automated promotions until the failure is understood.

## 11. Repository-local adapter and adoption

Each repository may add a local adapter describing its architecture-sensitive paths, canonical test/build commands, code owners, generated files, migration rules and allowed merge methods. Local adapters may make the standard stricter; they must not weaken security or review gates without an explicit documented owner decision.

This document and the accompanying audit workflow are proposals until merged. Account-level security settings, branch protection/rulesets, repository permissions and release credentials are not changed by this adoption PR.
