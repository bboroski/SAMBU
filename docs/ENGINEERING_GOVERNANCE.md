# Engineering Governance, Product Voice and Technical Debt

**Standard:** Duck Black / Yellow Engineering System 3.0  
**Applies to:** this repository, its releases, documentation, user-facing surfaces and integrations.  
**Status:** normative for new work; existing behavior remains unchanged until separately implemented and verified.

## 1. Operating principles

1. **Evidence before claims.** A product statement must map to source code, a test, a reproducible workflow or a clearly labelled roadmap item.
2. **One source of truth.** Repository identifiers, public APIs, configuration keys and module boundaries keep their canonical names.
3. **Small, reversible changes.** Prefer scoped pull requests, explicit migrations and a rollback path for risky changes.
4. **Security and privacy by default.** Minimize permissions, collected data, retention and third-party dependencies.
5. **Accessible by design.** Keyboard access, visible focus, readable contrast, reduced-motion support and clear error states are acceptance criteria.
6. **Documentation ships with behavior.** A feature is not complete while the README, relevant guides, examples and release notes describe a different state.
7. **No speculative completion.** A specification, mock-up, scaffold, placeholder or roadmap item is not an implemented capability.

## 2. Brand, visual identity and Voice of Customer

### Visual identity

The shared visual baseline is **Duck Black / Yellow**: black and graphite provide structure; yellow identifies primary actions, focus and active selection. Red is reserved for errors and destructive states, cyan for information, gray for neutral hierarchy and white for readable content. Use the canonical tokens in `design/duck-ui.tokens.json` and the shared UI rules in `design/DUCK_UI_SYSTEM.md`.

Use the existing repository name exactly as written. Do not create alternate product names, abbreviations or marks that obscure repository identity. Keep marks crisp, correctly proportioned and legible on dark and light backgrounds. Do not add a second visual system without a documented platform or accessibility reason.

### Voice of Customer (VoC)

Collect feedback through documented support conversations, issue reports, review notes and explicitly consented research. Do not infer customer sentiment from private data or unapproved telemetry. Remove personal data before sharing examples.

Translate feedback into a traceable loop:

`customer observation -> problem statement -> evidence -> scoped change -> validation -> release note -> follow-up`

Record the affected user type, context, frequency, severity and evidence source. Distinguish a single report from a recurring pattern. Do not turn an anecdote into a universal claim.

### Product voice

Use language that is direct, technically precise, calm, specific and respectful. Lead with the user problem and concrete outcome. Explain limits, prerequisites and failure states. Avoid absolute claims such as “perfect”, “unbreakable”, “fully secure” or “works everywhere” unless an explicit, independently verifiable scope supports them.

Preferred message shape:

`problem -> verified capability -> measurable/user-visible outcome -> limitation -> next action`

For Ukrainian, English and Russian materials, preserve the same feature scope, limitations, version numbers and command behavior. Translation must not introduce a stronger claim than the canonical source.

### Positioning technical debt responsibly

Do not rename unresolved technical debt as a premium feature. Premium engineering value comes from making debt visible and controlling it: an owned debt register, risk-ranked remediation, compatibility guarantees, test evidence, migration tools and predictable release management. Market those capabilities only when the repository actually provides them.

A marketing claim may use one of these states:

- **Implemented:** present in the shipped code and covered by appropriate tests.
- **Verified:** exercised in a reproducible supported environment; evidence is linked.
- **Experimental:** available but limited, unstable or explicitly opt-in.
- **Planned:** not yet shipped; describe as roadmap, not current capability.
- **Unsupported:** outside the tested product boundary; never imply support.

### Marketing content grid

| Audience | User problem | Message | Required proof | Suitable format | CTA |
|---|---|---|---|---|---|
| Evaluator | Cannot judge fit | State scope, requirements and limitations | Current README, support matrix, reproducible demo | Landing page / overview | Review requirements |
| Developer | Integration cost is unclear | Explain APIs, setup and extension points | Working example, API docs, CI evidence | Technical guide | Try the documented workflow |
| Operator | Reliability is uncertain | Explain observability, failure states and recovery | Tests, diagnostics, release notes | Case note / operations guide | Run the validation checklist |
| Maintainer | Change risk is unclear | Explain governance and migration discipline | PR history, tests, debt register | Engineering brief | Open a scoped issue |

Every campaign asset must have an owner, audience, source evidence, last-reviewed date and a clear CTA. Do not fabricate customer quotes, logos, benchmarks, adoption counts, security certifications or performance improvements.

## 3. RACI responsibility matrix

Roles are responsibilities, not assumptions about named individuals. One role is Accountable (A) for each decision. A person may hold multiple roles in a small team, but the distinction remains explicit.

| Workstream | Product owner | Tech lead | Contributor | QA / Security | Release owner |
|---|---|---|---|---|---|
| Scope and acceptance criteria | A | R | C | C | I |
| Architecture and public contracts | C | A/R | C | C | I |
| Implementation | I | A | R | C | I |
| UI tokens and accessibility | C | A | R | R | I |
| Documentation and localization | A | C | R | C | I |
| Tests and CI evidence | I | A | R | R | I |
| Security/privacy review | I | C | R | A | I |
| Release notes and versioning | C | R | I | C | A |
| Technical debt acceptance | A | R | C | C | I |
| Production rollback decision | I | R | C | C | A |

**R** = Responsible for doing the work; **A** = Accountable for the outcome; **C** = Consulted before decision; **I** = Informed.

## 4. Documentation KPIs and review cadence

Measure documentation quality through repository artifacts and CI. Do not collect personal telemetry to satisfy these targets.

| KPI | Target | Measurement |
|---|---:|---|
| Behavior-changing PRs with docs review | 100% | PR checklist and review |
| README build/setup commands verified | 100% of documented commands | CI smoke checks or recorded manual verification |
| Broken internal documentation links on main | 0 | Documentation link checker |
| Feature claims with an implementation state | 100% | README and guide audit |
| Locale parity for supported README languages | 100% of supported feature scope | Translation checklist |
| High/critical debt entries with owner and next action | 100% | Debt register |
| Release notes for user-visible changes | 100% | Release checklist |
| Accessibility and reduced-motion checks for UI changes | 100% of applicable PRs | UI acceptance checklist |

Targets are governance thresholds, not statements that the current repository already meets them. Review every release and perform a full documentation/debt audit at least quarterly. Any exception must have an owner, reason and review date.

## 5. Strict GitFlow and pull-request policy

### Branch model

- `main` is the protected, releasable integration branch. Do not commit directly to it.
- Create short-lived branches from the current `main`: `feat/<issue>-<slug>`, `fix/<issue>-<slug>`, `docs/<issue>-<slug>`, `refactor/<issue>-<slug>`, `chore/<issue>-<slug>` or `hotfix/<issue>-<slug>`.
- Use `release/<version>` only when a coordinated release branch is required by the project.
- Keep a branch focused on one independently reviewable objective. Prefer a lifetime of five working days or less; split larger work.
- Rebase or update against the current base before review. Never force-push a shared branch or rewrite commits others depend on.

### Commit and PR rules

- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `build:`, `ci:` and `chore:`.
- Every PR states context, behavior change, evidence, risks, limitations and rollback/migration notes when applicable.
- Require all relevant CI checks to pass. A red or missing required check blocks merge unless a documented emergency exception is approved and recorded.
- Require at least one independent approval. Require two reviewers for security-sensitive changes, data migrations, public API breaks or permission changes where team capacity allows.
- Update README, localized variants, design tokens, examples and release notes in the same PR when their content changes.
- Use the repository's configured merge strategy; prefer a single coherent merge commit or squash when the project policy permits. Do not silently change repository merge settings as part of a feature PR.
- Tag releases using the project's versioning policy. Hotfixes branch from `main`, receive expedited review and are merged back into the normal development flow.

Branch protection and rulesets are platform settings. This document defines the required policy; do not claim that GitHub enforcement is active unless the repository ruleset has been inspected and verified.

## 6. Technical debt audit and register

### Audit domains

Review architecture and module boundaries, security/privacy, dependencies and supply chain, test coverage, error handling, performance/resource use, accessibility, documentation drift, build/release automation and compatibility.

### Risk score

Score each issue from 1 to 5 for **impact** and **likelihood**. Calculate `risk = impact × likelihood`:

- 1–4: Low
- 5–9: Moderate
- 10–16: High
- 17–25: Critical

Record remediation effort separately (1–5). A high score is not automatically a reason for a disruptive rewrite; prioritize user harm, exploitability, recurrence, scope and available mitigations.

### Required register fields

Each entry contains: stable ID, subsystem, evidence/link, debt category, user or operational impact, impact score, likelihood score, risk score, remediation estimate, owner, mitigation, target milestone/date, acceptance decision and status.

Allowed statuses: `identified`, `triaged`, `planned`, `in_progress`, `mitigated`, `resolved`, `accepted`.

Accepted debt requires a named owner, documented reason, mitigation and expiry/review date. Security-critical debt cannot be accepted solely to meet a release date. Re-score when usage, exposure or system boundaries change.

### Audit cadence

Run a baseline audit before a major release and at least once per quarter. Re-audit sooner after a security incident, repeated production failure, major dependency change or public-contract break. Review cross-repository debt where components share tokens, schemas, workflows or runtime dependencies.

Do not invent debt entries to make the register look complete. Mark an area **not assessed** until evidence has been collected. Close an item only after the remediation is merged and the verification evidence is recorded.

## 7. Definition of Done

A change is complete only when its acceptance criteria, implementation, applicable tests, security/accessibility checks, documentation, localization and release notes agree. Known limitations and follow-up debt are recorded. Generated previews are labelled as previews; a mock-up is never evidence of a running feature.

**The standard optimizes for truthful product claims, controlled change, maintainable systems and user trust.**


## Operational debt register
The live, evidence-based findings and quarterly audit status are maintained in [`docs/TECHNICAL_DEBT_REGISTER.md`](TECHNICAL_DEBT_REGISTER.md). Keep the register synchronized with CI, incident reviews, accepted-risk decisions and remediation PRs.
