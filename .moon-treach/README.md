# MoonTreach

MoonTreach is the shared, path-aware CI accelerator and read-only merge-evidence assistant for the bboroski repository fleet.

## How it works

- **Change-aware planning:** changed paths select only the matching configured suites. Missing or unreliable Git history, or changes to MoonTreach's own policy/workflow, select every configured suite.
- **Parallel tests:** GitHub Actions expands the plan into independent matrix jobs and cancels obsolete runs for the same ref.
- **Native test commands:** every suite uses explicit argv arrays and the repository's documented commands. No shell command is assembled from untrusted config.
- **PR Radar:** a manual, read-only fleet inventory groups repeated normalized titles as review candidates; it never closes or merges PRs.
- **Merge Intelligence:** PR inspection reads mergeability, check runs and commit statuses. Results are BLOCKED, WAITING_FOR_EVIDENCE or REVIEW_CANDIDATE; that last result is not merge authorization.

## Run

Open Actions → MoonTreach → Run workflow. Use `force_all` to run every configured suite. On SAMBU, `run_pr_radar` runs the cross-repository inventory. An optional `MOONTREACH_TOKEN` repository secret gives the inventory a higher API rate limit; the tool never prints or persists it.

The shared engine lives at `.github/actions/moontreach/` in SAMBU. Other repositories pin that action to an immutable commit SHA.

## Safety

MoonTreach does not merge, auto-approve, rebase, force-push, delete branches, repair conflicts, change permissions, or bypass branch protection. Missing check evidence is never reported as success. A repeated PR title is only a deduplication lead, not proof of duplicate code.

A passing host test does not prove physical hardware, target firmware, emulator or release qualification unless the repository has an explicit check for that evidence. A repository with no configured suites remains unverified.
