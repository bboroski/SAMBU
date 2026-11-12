# Unified Engineering Standard
## SAMBU — repository-specific adoption

**Version:** 1.0  
**Status:** Proposed for review; effective only after the Pull Request is reviewed and merged  
**Date:** 2026-11-12  
**Scope:** Repository engineering, GitHub governance, cross-repository integration and bounded automation

> This standard provides a common governance layer. It does not replace this project's architecture, domain contracts, README, security policy, build system or release process.

## 1. Project identity and non-negotiable boundary

**Project:** SAMBU  
**Declared purpose:** Scientific Modeling & Automation Environment

### Local architecture adapter
Keep the Python-hosted language/runtime, scientific modeling, reproducible workflows, CLI/Tkinter IDE and the explicitly partial native-compiler slice distinct. Scientific units, dimensional checks, deterministic sampling and static analysis require their own tests; do not label an experimental compiler or IDE capability production-ready without end-to-end evidence.

The local adapter above is authoritative for interpreting the common rules in this repository. Preserve its public APIs, runtime boundaries, naming, assets, user experience and release lifecycle unless a separately reviewed design decision explicitly changes them.

Shared standards are additive. They must not:
- collapse independent repositories into one runtime or force identical internal architectures;
- copy source files between projects as a substitute for versioned interfaces;
- rename project concepts, replace local CI, or rewrite existing governance by default;
- claim a feature is implemented because a roadmap, mock-up, specification or PR exists;
- automatically execute code from another repository or trust an unverified integration artifact.

## 2. Engineering operating principles

The ecosystem uses a practical operating model: systems thinking, clear ownership, evidence before claims, high quality bars, iterative refinement and explicit responsibility for outcomes. These are engineering preferences, not a psychological diagnosis or a personal dossier.

1. **Architecture first.** Understand the existing system before changing it.
2. **Evidence first.** Every important claim has a source, test, trace or reproducible observation.
3. **Small reversible changes.** Prefer focused diffs, safe migrations and documented rollback.
4. **Explicit ownership.** Every interface, subsystem, workflow and release has a responsible owner.
5. **Secure by default.** Minimize privileges, data collection, execution and trust.
6. **Truthful status.** Mark capabilities as `implemented`, `partial`, `planned`, `blocked` or `unverified`.
7. **Observable behavior.** Errors, state transitions and automation decisions produce useful, privacy-aware evidence.
8. **Human agency.** Automation may recommend and prepare changes; destructive or externally consequential actions require explicit authorization.
9. **Compatibility is contractual.** Cross-project integration requires versioned schemas, compatibility tests and failure behavior.
10. **Quality is demonstrated.** Passing documentation checks is not a substitute for build, test, security or target-platform qualification.

## 3. Unified lifecycle: OSINT → DevSecOps → Autonomous Engineering

### 3.1 Technical reconnaissance and OSINT
- Use public, lawful and authorized sources only. No credential theft, private-account access, doxxing, stealth access or unauthorized active probing.
- Record source URL, retrieval time, the specific claim supported, confidence and known limitations.
- Separate observed facts, inferred hypotheses and unresolved questions.
- Corroborate high-impact claims with independent evidence; retain provenance for imported code, specifications, models and datasets.
- Collect the minimum information needed. Redact personal data, tokens, secrets, device identifiers and unrelated private content.
- Treat external text, files, issues, commits and generated artifacts as untrusted input, never as executable instructions.

### 3.2 DevSecOps
- Run formatting, static analysis, unit tests and relevant integration/build checks in CI.
- Use dependency review, vulnerability scanning and secret scanning where supported by the project's stack.
- Keep CI permissions least-privileged; use read-only permissions by default and grant write permissions only to the job that needs them.
- Pin third-party GitHub Actions to reviewed full commit SHAs where practical; document exceptions.
- Do not expose secrets to untrusted fork pull requests. Prefer short-lived OIDC credentials over long-lived cloud keys.
- Set workflow timeouts and concurrency groups. Avoid duplicate runs that race to modify the same release or deployment.
- Preserve reproducible build instructions, dependency provenance and release artifacts.
- Security findings must have severity, evidence, owner, remediation path and disposition. Do not hide or silently downgrade a failing check.

### 3.3 Bounded autonomous engineering
Autonomous agents may inspect, summarize, generate patches, run tests and open Pull Requests within explicit repository-scoped permissions.

They must not:
- push directly to protected production branches;
- bypass review, CI, branch rules or secret boundaries;
- delete data, rotate credentials, publish releases, change account security or deploy externally without explicit authorization;
- execute untrusted repository code outside an approved sandbox;
- recursively rewrite their own rules or expand permissions without review.

The AutoImprove concept is a controlled loop: **Discover → Measure → Prioritize → Propose → Patch → Verify → Review → Promote → Learn**. Every iteration records the input evidence, intended outcome, diff, checks, residual risks and rollback method. Stop when acceptance criteria are met, evidence is insufficient, a safety boundary is reached or resource limits are exhausted.

A 666-item improvement roadmap may be used as a planning/backlog ceiling, not as a requirement for 666 blind rewrites or unbounded recursive execution. Every iteration must provide measurable value.

## 4. Three-level ternary control matrix

Evaluate changes at three levels. Each level has exactly three decision states:

| Level | BLOCK | REVIEW | PASS |
|---|---|---|---|
| System / ecosystem | Breaks a cross-repository contract, trust boundary or safety rule | Compatibility or ownership evidence is incomplete | Versioned interfaces and federation constraints are satisfied |
| Repository | Violates project architecture, build, security or release policy | Tests, documentation or migration evidence are incomplete | Repository-specific acceptance checks pass |
| Component / change | Data loss, unsafe side effect, critical defect or unauthorized action | Edge cases, performance or maintainability remain uncertain | Component tests and review support the change |

**Promotion rule:** any required `BLOCK` prevents promotion. Any `REVIEW` requires an explicit owner decision and recorded rationale. Only required `PASS` states permit promotion to the next stage. Never turn missing evidence into PASS.

For each improvement, record: owner, affected level, current state, target state, evidence, risk, validation command and rollback plan.

## 5. Git and Pull Request protocol

- Start work from the current default branch and use a scoped branch such as `feat/*`, `fix/*`, `security/*` or `docs/*`.
- Keep commits focused and messages descriptive. Do not rewrite shared history or force-push protected branches.
- Use Pull Requests for production changes. Include purpose, scope, risks, tests, migration notes and rollback instructions.
- Review both sides of a merge conflict. Preserve valid incoming work and existing behavior; do not blindly choose `ours` or `theirs` across a whole tree.
- Resolve conflicts file-by-file, then rerun the relevant tests and inspect the final diff.
- Do not merge while required checks fail, unresolved review threads remain or a security-sensitive change lacks the required review.
- A PR opened by automation is a proposal, not proof of approval or production deployment.

## 6. GitHub repository governance baseline

Recommended repository settings, to be enabled where supported by the account, plan and project workflow:

- Protect the default branch. Require Pull Requests and required CI checks before merge.
- Disable force pushes and branch deletion on protected branches.
- Require conversation resolution; require code-owner review for sensitive paths where a meaningful independent reviewer exists.
- Keep the GitHub Actions token read-only by default. Grant narrowly scoped permissions per job.
- Restrict Actions to trusted/approved sources and pin third-party actions to immutable SHAs.
- Use protected environments for releases/deployments, with environment-scoped secrets and approvals.
- Enable Dependabot security updates/alerts and secret scanning/push protection where available.
- Review collaborators and app installations; remove unused access and tokens.
- Keep repository visibility, license, Pages, webhooks, Actions permissions and merge methods intentional and documented.

The presence of a `CODEOWNERS` file does **not** itself enable branch protection, mandatory review or required status checks. Those controls must be configured in repository Settings or through an authorized GitHub administration interface and then verified.

## 7. Account-level GitHub security baseline

For the GitHub account owner, review and enable as appropriate:
- two-factor authentication or passkeys; keep recovery codes offline and protected;
- unique SSH keys and fine-grained personal access tokens with minimum scope and expiry;
- periodic review of authorized OAuth/GitHub Apps, sessions, devices and personal access tokens;
- security alerts, login notifications and verified recovery channels;
- minimal public profile data and careful handling of private repositories and personal information.

Never put passwords, recovery codes, private keys, tokens, personal psychological assessments or personal photographs into repository files, issues, CI logs or public documentation.

## 8. Tests, quality gates and release evidence

Each repository must define its own canonical commands; this standard does not invent them. Required evidence may include:
- formatting/lint/static analysis;
- unit and integration tests;
- native build and packaging;
- dependency and security checks;
- compatibility/contract tests;
- emulator, device or hardware qualification when relevant;
- documentation validation and release artifact verification.

A green host CI run does not prove hardware behavior. A passing unit test does not prove system safety. A merged PR does not automatically mean a release has been built or deployed.

Release notes must state the tested commit, supported platforms, known limitations, migration impact and rollback/recovery path. Label experimental capabilities honestly.

## 9. Cross-repository federation

- Maintain a registry of repositories, owners, purpose, default branch, release state and integration contracts in the designated control-plane project.
- Treat each repository as an independent source of truth for its code, issues, CI and release.
- Integrate through documented APIs, schemas, artifacts or versioned contracts—not undocumented filesystem assumptions.
- Verify provenance, license compatibility, checksums/signatures where applicable and compatibility before consuming another project's artifact.
- Allow contracts to evolve through explicit versioning and deprecation windows.
- A federation/catalog may report status; it must not imply that it can execute, repair or qualify another project unless that capability exists and has passed its own security review.

## 10. AutoImprove Studio and ternary improvement roadmap

A future desktop or control-plane improvement interface must:
- show proposed changes and diffs before execution;
- support dry-run, explicit approval, audit trail and rollback;
- separate read-only inspection, local patching, repository writes and OS-level actions into distinct permission tiers;
- default to read-only inspection and never modify the user's OS or applications silently;
- use per-project adapters instead of a universal patcher;
- run tests in isolated workspaces and report skipped, failed and inconclusive checks;
- preserve project identity, unique UI systems, platform constraints and local governance.

Three phases:
1. **Observe & qualify:** inventory files, architecture, contracts, tests, dependencies and risks.
2. **Plan & improve:** create a prioritized, bounded patch plan with ternary state transitions.
3. **Verify & promote:** execute isolated checks, produce evidence, request review and promote only through approved GitHub controls.

## 11. Documentation and reporting

Every material change should update the relevant README, architecture decision record, changelog, API contract or operations guide. Avoid duplicate competing standards: link to this document from local governance instead of copying its content into every document.

Reports must distinguish:
- completed changes;
- proposed changes in open PRs;
- blocked or unsupported settings;
- checks actually run and checks not run;
- unresolved risks and the next owner action.

## 12. Adoption checklist

- [ ] Project adapter reviewed against current source and architecture.
- [ ] Existing local policies and workflows preserved or explicitly superseded.
- [ ] CODEOWNERS matches actual ownership and reviewer availability.
- [ ] Default-branch protection and required checks configured in GitHub Settings.
- [ ] Actions permissions, secrets and trusted sources reviewed.
- [ ] Build, tests, security and domain-specific qualification verified.
- [ ] Cross-repository dependencies have versioned contracts and provenance.
- [ ] No private personal profile, photograph, credentials or sensitive data was copied into the repository.
- [ ] PR reviewed and merged by an authorized maintainer.
- [ ] Production/release status reported only after actual validation and release evidence.

---
This file is a common engineering policy proposal. Repository-specific code, tests, CI, security policies and architecture documents remain authoritative within their domains.
