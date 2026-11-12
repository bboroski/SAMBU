# Default-branch ruleset import

This directory contains the repository-specific, importable production ruleset in `main.json`.

## Required application

1. Open **Settings → Rules → Rulesets** in this repository.
2. For a repository that already has an active main/default-branch ruleset, edit that ruleset in place and reconcile its required checks with `main.json`. Do not simply add a second overlapping ruleset: active rulesets are cumulative.
3. For a repository without an active default-branch ruleset, import `main.json` as a new ruleset.
4. Set enforcement to **Active**, target the default branch, save, then verify the effective ruleset and run a test pull request.

## Enforced policy

- Pull request required; direct push to the default branch is blocked.
- Deletion and non-fast-forward updates are blocked.
- Linear history required; merge commits are excluded. Use **Squash** or **Rebase**.
- Stale approvals are dismissed and review threads must be resolved.
- Conventional Commit messages are required, including a 72-character subject limit.
- Every check listed in `main.json` must pass against the latest base branch.
- No bypass actors are configured.

## Review-count decision

The initial approving-review count is **0** because these repositories currently have one confirmed maintainer. Requiring an approval from a second person before a second maintainer exists would deadlock normal changes. Once an independent maintainer is appointed, raise the count to **1**, enable Code Owner review, and require approval of the last push.

## Signing

The ruleset does not require signed commits for every PR commit: commits created by automation or the GitHub API may not carry the maintainer's signing key. Release tags are separately required to be annotated and cryptographically verified by `release-preflight.yml`.

## Repository-specific reconciliation

- Existing active rulesets must be updated, not layered. Keep only status contexts actually emitted by this repository's PR workflows.
- The previous `9circ` ruleset contains unrelated SAMBU/Python matrix contexts. Replace those stale contexts with the baseline contexts in this repository's `main.json`.
- `Hellduck` has no active branch ruleset; import this file and activate it.
- Do not mark a check as required until it has emitted successfully at least once on a PR in this repository.

## Release blockers

A protected branch is only one release gate. Review `RELEASE_POLICY.md`, make an explicit license decision, verify the security scan, build the SBOM, and sign the release tag before publication.
