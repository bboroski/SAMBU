# Merge Automation Runtime

This repository uses .github/workflows/merge-automation-coordinator.yml as a guarded Auto-Merge coordinator.

## Activation gates

The coordinator only considers open, non-draft PRs targeting the repository's actual default branch. It requires:
- current GitHub mergeability state MERGEABLE; conflicts block promotion;
- GitHub review decision APPROVED;
- at least one reported check/status context, all completed with an accepted success conclusion;
- a stable head SHA across the final re-fetch;
- a merge method enabled in repository settings.

The merge method defaults to squash. Set the repository Actions variable MERGE_METHOD to merge or rebase to select another enabled method.

## Per-repository serialization and ordering

One coordinator run executes at a time per repository. Before activation it checks whether any open PR already has an Auto-Merge request. If so, that PR holds the repository promotion lock and no second PR is activated.

When the lock is free, the coordinator selects the oldest currently eligible PR by createdAt. After a PR merges or closes, the next qualifying event rescans the live queue. GitHub Actions concurrency itself is not a strict FIFO scheduler; ordering is enforced by the live oldest-eligible selection and the single-active-Auto-Merge lock. Manual Auto-Merge activation outside this coordinator can affect ordering and should be avoided when strict serialized promotion is desired.

If the active PR becomes blocked after activation, the lock remains occupied until the PR merges or an authorized maintainer disables Auto-Merge. This is deliberate fail-closed behavior.

## CI refresh and merge queues

The coordinator re-evaluates PRs after PR updates, review submissions/dismissals, completed check suites, and successful status updates. A changed head SHA invalidates prior evidence. GitHub re-evaluates required checks and approvals before completing Auto-Merge. If a repository requires a merge queue, GitHub controls queue admission; native CI must support the merge_group event.

## Conflict handling and data preservation

Conflicted PRs are never auto-merged. The coordinator does not choose ours or theirs, rewrite source files, rebase, force-push, or resolve conflicts automatically. Conflicts remain visible for path-scoped human resolution. After a resolution or branch update, the new head SHA must pass CI and review gates again.

## Branch cleanup

After a PR is merged, the workflow may delete its source branch only when it belongs to this repository, is not the default branch, and is not referenced by another open PR. Fork branches are never deleted. Protected-branch or permission failures are reported and left for an administrator.

## Audit and notifications

Every coordinator run writes its decision and relevant PR evidence to the GitHub Actions job summary. Successful Auto-Merge activation also posts a PR comment. Workflow failures are visible as failed GitHub Actions runs and can trigger the repository's normal GitHub notifications.

## Security boundaries

The workflow uses pull_request_target only for trusted metadata operations. It does not check out, build, or execute PR head code. Permissions are limited to reading checks/statuses and managing PR Auto-Merge and guarded source-branch cleanup. It never changes branch protection/rulesets, bypasses required reviews/checks, force-pushes, or merges around GitHub's rules.
