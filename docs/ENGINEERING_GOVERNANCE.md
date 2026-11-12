# Engineering Governance

**Scope:** this repository, its application/runtime, public interfaces, build and release processes.  
**Authority:** this document sets review expectations; it does not claim that every control is already enforced by platform settings.

## Principles

1. Preserve the product's purpose, existing behavior, public API, data formats and project history.
2. Make small, independently reviewable and reversible changes.
3. Require evidence for capability, security, performance, compatibility and test claims.
4. Keep dependencies and workflow permissions to the minimum required.
5. Make errors, limits, failure states and unsupported platforms explicit.
6. Update documentation with behavior; a specification or mock-up is not an implemented feature.
7. Do not treat a blank debt register, missing check or skipped test as proof of quality.

## Change and review policy

- Start from the current `main` and use a short-lived branch for each coherent change.
- Do not push directly to a protected branch or bypass configured review/check rules.
- Keep PRs small. Describe purpose, affected modules, API/data impact, risk, evidence, migration and rollback.
- Require applicable CI checks to pass on the current PR head. Resolve blocking review threads before merge.
- Merge dependent changes sequentially and rerun checks after each integration.
- Do not claim branch protection or required approvals are active until the repository settings have been inspected.

## Quality and security

- Add meaningful tests for normal, boundary and failure behavior.
- Run the repository's real formatter, lint, static analysis, tests, build and documentation checks where available.
- Validate untrusted input, file paths, authorization, configuration and error paths.
- Never commit secrets, credentials, personal data or machine-specific paths.
- Review dependency vulnerabilities, licenses and workflow permissions when dependencies or automation change.
- Treat API, schema, configuration, persisted data and hardware handoff as versioned contracts.

## Application and documentation

Test the real user journeys and interfaces that the product actually provides. Apply accessibility, keyboard navigation, contrast, responsive behavior and reduced-motion checks to relevant UI changes. Do not add a GUI to a headless product without a product requirement.

Keep the root `README.md` at or below 5,000 characters. Use current, repository-owned screenshots of the actual application; omit screenshots where no GUI exists, or clearly label architecture diagrams. Do not invent commands, metrics, support claims, badges or screenshots. Keep maintained language variants aligned and end the root README with a correctly translated Chinese love quotation.

## Definition of Done

A change is complete only when acceptance criteria are met, applicable tests and checks have real results, contracts and compatibility are reviewed, documentation matches implementation, remaining limitations are recorded, and the PR is independently reviewable. Unknown behavior stays **not assessed** until evidence exists.
