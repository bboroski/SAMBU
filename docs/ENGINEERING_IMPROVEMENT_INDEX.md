# Engineering Improvement Index

> Repository-specific execution map for the shared engineering improvement standard. This file records controls and evidence; it does not claim that every improvement is already implemented.

**Baseline review:** 2026-11-11  
**Default branch:** `main`  
**Project scope:** Python-hosted language tooling, IDE/studio surfaces, scientific and spatial modules, and a separately scoped C11 native slice.

## 1. Non-negotiable rules

- Preserve the repository's purpose, public behavior, supported platforms, API contracts, data formats and development history unless a separately reviewed migration explicitly changes them.
- Treat the existing source, manifests, tests and release process as the source of truth. Do not impose another project's architecture, language, UI or deployment model.
- Prefer small, isolated, reversible changes. One PR should address one coherent objective and state its acceptance criteria, affected components, risks and rollback path.
- Do not delete unknown files, disable existing checks, replace real tests with mocks, or describe a plan, scaffold, mock-up or open PR as a shipped feature.
- Use truthful states: **not assessed**, **planned**, **implemented**, **verified**, **experimental**, **blocked** and **unsupported**. A configured workflow is not a passed workflow.
- Never commit secrets, tokens, personal data, generated machine-specific paths or unreviewed binaries.

## 2. Repository evidence map

The current repository scope and user-facing capabilities are described in [README](../README.md). The following paths were discovered during structural inventory; their presence does not imply that they passed in this review.

### CI and automation
- [tests.yml](../.github/workflows/tests.yml)
- [native.yml](../.github/workflows/native.yml)
- [swift-backend.yml](../.github/workflows/swift-backend.yml)
- [duck-quality-gate.yml](../.github/workflows/duck-quality-gate.yml)

### Tests and validation sources
- [tests/](../tests/)
- [native/tests/](../native/tests/)

### Existing governance and project rules
- [ENGINEERING_GOVERNANCE.md](./ENGINEERING_GOVERNANCE.md)
- [TECHNICAL_DEBT_REGISTER.md](./TECHNICAL_DEBT_REGISTER.md)
- [ANTI_TERADAYN_PROTOCOL.md](./ANTI_TERADAYN_PROTOCOL.md)
- [EXPERIENCE_ENGINEERING.md](./EXPERIENCE_ENGINEERING.md)

- Pull request checklist: [repository template](../.github/pull_request_template.md).

**Verification boundary:** this inventory did not execute the project's build, test suite, target hardware, security scanner or release process. Use the check results attached to each PR's exact head commit as the execution evidence. Missing or skipped checks remain unverified.

## 3. Required engineering workstreams

### Architecture and code
Map entry points, modules, ownership, data flow and external boundaries before refactoring. Identify cycles, duplicated logic, dead code, uncontrolled global state and unnecessary abstractions. Keep interfaces narrow and errors explicit. Refactor only with behavior-preserving tests or a documented migration.

### Application and user experience
Audit real user journeys, command/API flows and GUI surfaces where they exist. Check loading, empty, error, disabled and recovery states; keyboard access, focus, contrast, responsive layout and reduced motion where applicable. A firmware library, kernel substrate, CLI or headless service must not be forced to grow a GUI merely to satisfy a generic checklist.

### Testing and compatibility
Use meaningful unit, integration, functional, regression, smoke and target-specific tests as appropriate to the project. Cover normal, boundary and failure paths. Preserve supported behavior and formats; document unsupported platforms and hardware qualifications. Do not invent coverage percentages or claim hardware validation from host CI.

### Build and CI/CD
Keep builds reproducible and workflows least-privileged. Run the project's native formatter, lint, type/static analysis, tests, build, documentation and security checks where configured. A new check must fail on a real defect and produce actionable output; do not add permanently green placeholder jobs.

### Security and dependencies
Review input validation, authorization, secret handling, file/path access, logging, network boundaries, workflow permissions, dependency vulnerabilities and license compatibility. Update dependencies in small, compatible groups and retain lockfiles or other reproducibility controls. Record severity, exposure and remediation evidence for findings.

### API, configuration and data
Treat public APIs, schemas, configuration keys, persistence formats and boot/runtime handoff structures as contracts. Validate inputs and outputs, define error behavior and timeouts, version incompatible changes, and provide tested migrations and recovery procedures for destructive data operations.

### Performance and operations
Measure startup, latency, memory, CPU, I/O, network activity and artifact size before optimizing. Add structured logs, diagnostics and metrics only where they improve fault isolation. Do not log secrets or introduce cache/parallel/distributed complexity without evidence.

### Documentation and visual assets
Keep root `README.md` under 5,000 characters, focused on purpose, current capabilities, real setup/test commands, limitations, useful docs and a small number of relevant cross-links. Use only current, repository-owned screenshots of the actual application. If no GUI exists, omit screenshots or clearly label a genuine architecture diagram; never present a mock-up as a screenshot. End the root README with a correctly translated Chinese love quotation. Keep English/Ukrainian/Russian variants aligned wherever maintained.

## 4. Change delivery and integration

1. Capture the current `main` SHA, repository state and baseline check results before code changes.
2. Create a short-lived branch from current `main`; do not work directly on a protected branch.
3. Split architecture, application, security, test, CI, dependency and documentation work into independent PRs when they can be reviewed separately.
4. Include evidence: exact commands, workflow links, affected platforms, screenshots/logs where relevant, API/data compatibility, known limitations and rollback steps.
5. Review the full diff and generated artifacts. Reject unexplained file deletion, broad formatting churn and unrelated dependency changes.
6. Merge only after applicable checks pass on the current PR head, blocking review threads are resolved and required approvals/rules are satisfied. If merge order matters, integrate sequentially and rerun checks after each merge.
7. Verify the resulting `main` commit and retain the PR, commit and test evidence. Do not bypass protections or treat a pending/skipped check as success.

## 5. Technical-debt register

Record each confirmed issue with a stable ID, subsystem, evidence, user/operational impact, severity, likelihood, owner/role, mitigation, proposed action, target milestone and status. Prioritize critical security, data-loss and service-blocking failures before cosmetic cleanup. Accepted debt needs a reason, compensating control and review date. An empty register means **not yet recorded**, not **no technical debt**.

## 6. Definition of Done

- Scope and acceptance criteria are explicit; the change is isolated and reversible.
- Relevant tests exercise success, boundary and failure behavior.
- Build, lint, static, security and documentation checks applicable to the change have actual results.
- API, configuration, data and platform compatibility have been reviewed.
- README and relevant guides match the shipped behavior; screenshots and claims are genuine.
- Known limitations and remaining debt are recorded without overstating completion.
- The PR is independently reviewable and the target branch remains buildable.

**Current status:** repository structure and existing controls have been mapped. Application behavior, complete architecture, runtime security, performance, hardware qualification and end-to-end workflows still require repository-specific execution and review.
