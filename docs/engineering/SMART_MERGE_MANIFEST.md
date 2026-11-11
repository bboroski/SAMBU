# Smart Merge Manifest — Main Branch Governance

**Status:** Repository engineering standard  
**Version:** 1.0  
**Adopted through:** Pull request  
**Scope:** All development, maintenance, documentation, infrastructure, and release changes in this repository.

This policy defines the expected path from a proposed change to a safe merge. It complements this repository's existing build and test workflows; it does not replace project-specific engineering requirements.

## 1. Main branch is protected

- Treat the default branch (`main` in this repository) as the integration source of truth.
- Integrate changes through pull requests. Do not push directly to the protected branch during normal development.
- Disable force-pushes and branch deletion for `main` and maintained release branches.
- Require the repository's stable, relevant CI checks to pass before merge. Select check names from actual workflow runs; do not invent or require checks that this repository does not produce.
- Require resolution of review conversations before merge.
- Enforce linear history when the repository's release and contribution model supports it.
- Use signed commits where the team has a reliable signing-key policy. Do not enable a setting that would lock out legitimate maintainers without a recovery path.

Branch protection and rulesets are GitHub repository settings, not files in the Git tree. Configure them in **Settings → Branches** or **Settings → Rules → Rulesets** after confirming the real status-check names and reviewer availability.

## 2. Pull requests are atomic change contracts

- Keep each PR focused on one coherent purpose. Split broad work into dependent, reviewable PRs.
- Use Draft PRs for work that is not ready for review.
- Explain the problem, proposed solution, important alternatives, and observable impact.
- Link an issue or design decision when one exists; do not fabricate ticket identifiers.
- Include reproducible test instructions and evidence for UI/API changes.
- State breaking changes, migration requirements, operational risks, and rollback steps.
- Review the complete diff before requesting review. Remove debug output, accidental files, temporary code, and secrets.
- Prefer Conventional Commit prefixes in PR titles when they are useful to the repository's release tooling: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `build:`, `ci:`, `chore:`.

## 3. Review is a quality and knowledge-transfer step

- Request reviewers who understand the affected subsystem. Maintain `CODEOWNERS` only when real, active GitHub users or teams are known; never add guessed team names.
- Separate blocking correctness/security issues from questions, suggestions, and cosmetic nits.
- Do not approve your own PR. Where multiple maintainers exist, require at least one independent approval; adapt approval requirements for single-maintainer repositories so the workflow does not become impossible to merge.
- Resolve every blocking review thread and record the decision behind significant design trade-offs.
- AI-assisted review may suggest issues or tests, but it is not an approval and cannot replace accountable human review.

## 4. CI quality gates

Use this repository's existing workflows and project commands as the source of truth.

- Run formatting, lint, static analysis, unit tests, and relevant integration tests on pull requests.
- Run broader end-to-end, platform, performance, and regression suites according to change risk and the capabilities of this project.
- Keep security and dependency checks active where supported. Never put credentials or tokens in workflow logs or committed files.
- Make documentation validation/build checks part of CI where documentation tooling exists.
- Keep required status-check names stable. If path filters are used, provide an always-running aggregate/check job so a skipped workflow cannot leave a required check permanently pending.
- Treat flaky tests as defects: report retries, assign an owner, track remediation, and time-limit quarantine. Do not silently convert persistent failures into success.
- Use dependency-aware test selection only when the repository's dependency graph and fallback behavior are trustworthy.
- Use isolated preview environments for UI/API changes when the deployment stack supports them; do not introduce infrastructure solely to satisfy a generic checklist.

## 5. Merge and release strategy

- Default to **Squash and merge** for ordinary feature and bug-fix PRs when linear history is enabled.
- Use **Rebase and merge** only when individual commits are meaningful and the repository benefits from retaining them.
- Reserve merge commits for release or integration branches where preserving branch topology is intentional.
- Enable a merge queue only when concurrent PR throughput makes it valuable and its required checks are fully configured.
- A successful merge is not automatically a production release. Use the repository's established deployment/release workflow, staged rollout, feature flags, and rollback mechanism where applicable.
- Remove temporary feature flags after rollout and track their cleanup.

## 6. Documentation changes belong with code

- Update relevant README, API/schema, configuration examples, operational instructions, and user-facing docs in the same PR as the behavior they describe.
- Record significant architecture decisions as ADRs in `docs/adr/` using **Context, Decision, Consequences, Status**.
- Generate API/config/CLI reference material from source schemas or commands when practical.
- Keep changelog and release notes aligned with the repository's actual release process. Do not introduce a generator that conflicts with existing versioning conventions.
- Validate Markdown, links, examples, and documentation builds using the tools already adopted by this repository.

## 7. Operational safety and measurement

- Prefer short-lived branches and frequent integration. Use feature flags to merge incomplete user-facing work safely when appropriate.
- Do not bypass CI because a change is urgent. Emergency changes still require the strongest feasible automated checks and a documented follow-up review.
- Track PR cycle time, time to first review, failed-change rate, recovery time, and flaky-test frequency when repository activity is sufficient to make the metrics meaningful.
- Use blameless incident reviews to improve tests, automation, and ownership rather than assign personal blame.

## 8. Merge readiness checklist

A PR is ready to merge only when:
- [ ] The change has one clear purpose and a reviewable scope.
- [ ] Relevant CI checks pass on the current PR head.
- [ ] Required independent review is complete, where applicable.
- [ ] Blocking conversations are resolved.
- [ ] Tests and documentation match the behavior being changed.
- [ ] Security, compatibility, migration, and rollback risks are addressed.
- [ ] The selected merge method matches repository policy.

## 9. Repository-specific configuration rule

This manifest is intentionally technology-neutral. Existing workflows, build systems, tests, deployment configuration, branch names, release conventions, and documentation languages remain authoritative for this repository. Any stronger gate must be based on a check that actually exists and can run reliably. Changes to branch protection, required reviewers, merge queue, secrets, or deployment environments must be configured and verified in GitHub settings by an administrator.
