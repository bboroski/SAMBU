# Engineering Governance, Brand and Delivery Standard

> Revision: 2026-11-11 · Scope: this repository · Status: proposed baseline for review

## 1. Brand position and customer voice

**Customer-first message formula:** For **[audience]** who need **[job / problem]**, this project provides **[verified capability]** so they can **[measurable outcome]**. Evidence: **[test, benchmark, demonstration or documented limitation]**.

Voice of Customer (VoC) rules:
- Start with the user's problem and task, not internal architecture or feature counts.
- Use the customer's vocabulary from support requests, issues and observed workflows; distinguish direct quotes from paraphrases.
- Explain what is possible today, what remains experimental, what is planned and what is unsupported.
- Prefer measurable outcomes and verifiable screenshots/logs over adjectives such as "revolutionary", "unlimited" or "production-ready".
- Do not publish private user data, credentials, local paths or unapproved customer quotations.

## 2. Visual brand system

- Primary identity: Duck Black / Yellow. Black and graphite carry structure; signal yellow marks primary actions, focus, active selection and progress.
- Alert red is reserved for failure and destructive states; information blue for neutral information; gray establishes secondary hierarchy; white carries readable content.
- Use the canonical palette in `design/duck-ui.tokens.json`, the design contract in `design/DUCK_UI_SYSTEM.md` and shared styles in `assets/duck-ui/duck-ui.css`.
- Keep the exact repository name in titles, package metadata, badges, API prefixes and cross-repository links. Do not invent aliases or rename projects inside shared standards.
- Use one primary mark per visual surface. Avoid logo repetition, decorative yellow floods, low-contrast text and motion that competes with task content.
- Web, desktop, CLI and specification-only repositories share the same semantic hierarchy; adapt native controls rather than adding an unrelated UI framework solely for branding.

## 3. Marketing and technical-debt positioning

Technical debt is an engineering liability, not a finished customer feature. Position its remediation as a **reliability / capability investment** only when a concrete plan and evidence exist:
1. Describe the customer-visible risk or friction.
2. Record the affected component, impact, likelihood and current workaround.
3. Define a remediation milestone, owner role, acceptance criteria and rollback.
4. Measure the improvement (latency, failure rate, build time, support burden, compatibility or security exposure).
5. Publish the outcome after tests; do not re-label unresolved debt as a premium feature or claim a fix before it ships.

Market grid for each release:

| Audience | Job to be done | Message | Proof | Channel | Call to action |
|---|---|---|---|---|---|
| New users | Understand fit and limitations | One-sentence value proposition | Quick start and verified demo | README / landing page | Try the verified workflow |
| Active users | Complete a known task faster or safer | Workflow improvement | Before/after metric or test | Release notes / changelog | Upgrade or review changes |
| Integrators | Assess compatibility and contracts | Stable interfaces and boundaries | API docs, version matrix, CI | Integration guide | Validate the adapter |
| Maintainers | Reduce risk and delivery friction | Quality and maintainability | Audit log, CI, debt register | Engineering docs | Review / contribute |

## 4. RACI and decision rights

Roles are responsibilities, not assumed people. Assign named owners in the repository settings or issue tracker; never invent names.

| Work item | Product / Repository owner | Technical lead | Contributor | Reviewer / QA | Documentation / Release |
|---|---|---|---|---|---|
| Roadmap and scope | A | R | C | C | I |
| Architecture and public contracts | C | A/R | C | C | I |
| Implementation | I | A | R | C | I |
| Test strategy and evidence | I | A | R | R | I |
| Security / privacy review | A | R | C | R | I |
| User documentation and localization | A | C | R | C | R |
| Release notes and claims | A | C | I | C | R |
| Technical-debt register | A | R | R | C | I |

R = Responsible; A = Accountable (exactly one A per decision); C = Consulted; I = Informed.

## 5. Documentation quality KPIs

These are target thresholds, not claimed current measurements.

| KPI | Target | Measurement |
|---|---:|---|
| Public behavior changes with matching docs | 100% | PRs changing public behavior that also update docs / all such PRs |
| README language parity (UK / EN / RU) | 100% | Same feature, setup, limitations and release state in all three versions |
| Release documentation freshness | 100% | Each release updates changelog, README status and relevant guides |
| Broken internal documentation links | 0 | Automated link check on default branch |
| API / CLI contract coverage | 100% | Public commands and interfaces documented with examples and failure behavior |
| Undocumented experimental claims | 0 | Marketing claim inventory checked against code and test evidence |
| Debt records with owner role, severity and exit criteria | 100% | Required fields present in each active debt item |

Review docs in the same PR as implementation. Reconcile Ukrainian, English and Russian user-facing documentation together; do not let translation silently change feature scope or safety limits.

## 6. Strict PR-based GitFlow

- `main`: protected, releasable history. No direct pushes; all changes arrive through reviewed pull requests.
- `develop`: integration branch when a release train needs it. Keep it synchronized with `main`; do not create it in a specification-only repository unless the maintainer adopts that release model.
- `feature/<issue>-<slug>`: new capabilities, branched from `develop` (or `main` when no `develop` exists).
- `bugfix/<issue>-<slug>`: non-urgent fixes to integration branch.
- `release/<version>`: stabilization, docs, version metadata and release checks; no unrelated features.
- `hotfix/<issue>-<slug>`: urgent production fix branched from `main`; merge to `main`, then back-merge to `develop`.
- Every PR names its base branch, links an issue or explains why one is unnecessary, lists tests and evidence, identifies risk and includes a rollback note for risky changes.
- Merge only after required reviews and CI succeed. Prefer squash merge for focused work; preserve merge commits when release history requires explicit branch topology.
- Delete merged short-lived branches. Tag releases immutably and maintain a changelog.

## 7. Pull-request and release gates

Every PR must pass:
1. Scope and compatibility review; preserve repository identity, public interfaces and documented platform boundaries.
2. Relevant unit, integration, architecture, security and smoke tests; attach actual command output or CI links.
3. Documentation, changelog and UK / EN / RU parity for user-facing changes.
4. Accessibility and visual checks for UI changes: keyboard-only, visible focus, contrast, reduced motion and responsive layouts.
5. Dependency and secret scan where the repository supports them.
6. Reviewer approval and clean merge base.
7. For release PRs: version, changelog, known limitations, supported platform evidence and rollback procedure.

## 8. Technical-debt audit

Maintain a debt record with: ID, component/path, symptom, root cause (known / suspected), customer impact, probability, severity, workaround, dependencies, owner role, remediation approach, estimate, acceptance tests, target release and rollback.

Triage:
- **P0 critical:** active security/data-loss risk or release-blocking corruption — stop release and mitigate immediately.
- **P1 high:** major user workflow blocked, severe reliability or compatibility failure — prioritize before new feature work.
- **P2 medium:** recurring friction or maintainability cost with bounded workaround — schedule into a planned cycle.
- **P3 low:** cleanup, duplication or polish — batch when touching adjacent code.

Audit cadence: at each release and at least once per quarter for active repositories. Close an item only when acceptance evidence is attached; otherwise keep it open with a revised plan. Never hide debt by changing labels.

## 9. Repository-specific adaptation

The standard does not imply that every repository has a GUI, a production release or a supported hardware target. Apply visual rules to actual surfaces; use diagrams and terminal output in CLI/specification projects. Claims and release readiness must match the repository's real code and evidence.
