# MoonTreach

This repository uses the canonical MoonTreach engine and reusable workflow hosted by `bboroski/Hellduck`, pinned to immutable core revision `edc139b8e08f098b708ce846ac0af60f206e7efb`.

## What it does

- Computes changed paths from the exact base/head commit range.
- Selects only checks mapped to changed files; unknown paths, missing diffs, oversized changes and merge-group candidates fail closed to the configured full suite.
- Runs configured commands as argument arrays without shell interpolation and applies per-command timeouts.
- Runs the full configured suite on GitHub `merge_group` candidates.
- Uploads a machine-readable evidence report with SHAs, changed files, matched rules, selected checks, outcomes and elapsed time.

The authoritative repository contract is `moontreach.json` at the repository root. The workflow checks the exact PR merge ref, or the synthetic merge-group commit, rather than testing an unrelated branch head.

## Operation and safety

The workflow uses read-only `contents` permissions, does not persist checkout credentials, and does not receive repository secrets. MoonTreach never merges PRs, rewrites branches, resolves semantic conflicts, or bypasses branch protection.

A passing MoonTreach check is evidence for the configured checks only. Enable the check as a required branch-protection or ruleset check only after reviewing actual CI results. Human review and existing required checks remain authoritative.

## Local commands

```bash
python tools/moontreach/engine.py validate --root . --config moontreach.json
python tools/moontreach/engine.py plan --root . --config moontreach.json --base BASE_SHA --head HEAD_SHA
python tools/moontreach/engine.py run --root . --config moontreach.json --base BASE_SHA --head HEAD_SHA --report artifacts/moontreach-evidence.json
```

The engine source is maintained centrally in Hellduck; these commands are intended for use from a checkout of that core repository or through the reusable workflow.
