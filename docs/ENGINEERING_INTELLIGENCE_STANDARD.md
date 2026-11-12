# Engineering Intelligence Standard
## OSINT → DevSecOps → Autonomous Engineering

**Scope:** shared engineering policy for the bboroski repository ecosystem  
**Applicability:** adapt controls to each repository's actual language, build system, runtime, threat model, and product scope  
**Compatibility rule:** this standard supplements project-specific architecture; it does not replace local build, release, security, or governance workflows.

## Purpose

Use engineering intelligence to reduce uncertainty and improve decisions. Every finding must be traceable to evidence, every proposed change must be bounded, and every release must be reproducible and reversible. The standard is a control framework, not a claim that every control is already implemented.

## I. Engineering intelligence and principles (1–15)

1. **Outcome first:** every change must solve a documented user, reliability, security, or maintenance problem.
2. **Stability over activity:** do not trade a working release for unverified feature volume.
3. **Separate evidence from inference:** label observations, hypotheses, and conclusions distinctly.
4. **Independent verification:** confirm critical findings through tests, static analysis, or a second independent method.
5. **Treat missing signals as findings:** absent tests, stale workflows, missing owners, and silent monitoring require investigation.
6. **Challenge the hypothesis:** actively seek counterexamples and alternative root causes.
7. **Timestamp evidence:** record the commit, tool version, environment, and time for every material finding.
8. **Price the change:** weigh risk, maintenance cost, performance impact, and user value before implementation.
9. **Think from the caller's perspective:** assess API consumers, operators, maintainers, and end users.
10. **Prefer the smallest sound design:** avoid abstractions and dependencies without a measurable benefit.
11. **Respect project identity:** preserve the repository's purpose, language, conventions, and supported platforms.
12. **Verify provenance:** investigate unexpected packages, generated files, binaries, scripts, and workflow changes.
13. **Plan recovery before mutation:** define rollback or forward-fix steps for risky changes.
14. **Audit details:** check path casing, encodings, permissions, line endings, environment variables, and platform differences.
15. **Least privilege by default:** grant each user, workflow, token, and process only the permissions it needs.

## II. Discovery and change planning (16–30)

16. **Write an actionable task:** define objective, scope, non-goals, constraints, and acceptance criteria.
17. **Inventory before editing:** inspect README files, source trees, manifests, tests, workflows, licenses, and release configuration.
18. **Record the baseline:** capture default branch, base commit SHA, clean/dirty state, and current CI status.
19. **Map dependencies:** identify callers, downstream modules, public interfaces, and affected repositories.
20. **Follow local conventions:** use the existing style, naming, formatting, localization, and contribution rules.
21. **Choose stack-native tools:** do not impose tooling that conflicts with the repository's actual language or build system.
22. **Specify failure behavior:** document error types, exit codes, retries, timeouts, logging, and recovery.
23. **Define contracts:** preserve API, ABI, CLI, IPC, network, file-format, and schema compatibility.
24. **Identify critical paths:** locate single points of failure, cycles, shared state, and high-risk dependencies.
25. **Prepare rollback:** state how to revert files, data migrations, configuration, and releases.
26. **Isolate experiments:** use feature branches, disposable test data, containers, or virtual machines where appropriate.
27. **Test supported platforms:** account for operating systems, CPU architectures, compilers, and runtime versions declared by the project.
28. **Assign ownership:** make implementation, review, security, testing, and release responsibilities explicit.
29. **Make work reproducible:** record exact build, test, lint, and packaging commands.
30. **Reserve validation time:** include time for regression testing, conflict resolution, and release verification.

## III. Codebase observation and quality audit (31–50)

31. **Audit the whole change surface:** inspect source, configuration, scripts, docs, tests, generated assets, and CI.
32. **Enforce module boundaries:** detect accidental coupling, dependency inversion violations, and leaked internals.
33. **Measure architecture health:** identify duplication, oversized modules, cyclic dependencies, and excessive complexity.
34. **Inspect concurrency:** test asynchronous flows, thread safety, locking, cancellation, and race conditions.
35. **Track resource ownership:** validate memory, file handles, sockets, subprocesses, and connection lifetimes.
36. **Use logs as evidence:** find recurring failures, warnings, latency spikes, and operational anomalies.
37. **Remove only proven dead code:** verify references and behavior before deleting files or compatibility paths.
38. **Check side effects:** test adjacent components and downstream consumers affected by a change.
39. **Detect nondeterminism:** investigate flaky tests, hidden global state, time dependence, and unseeded randomness.
40. **Handle errors explicitly:** do not swallow exceptions or report success after partial failure.
41. **Track measurable regressions:** compare build size, runtime, memory, test duration, and error counts against a baseline.
42. **Preserve reproducible evidence:** keep minimal test cases, stack traces, environment details, and safe input fixtures.
43. **Locate each finding:** include file, symbol, line, commit, reproduction steps, and affected version.
44. **Fix root causes:** avoid patches that merely hide symptoms or suppress diagnostics.
45. **Add regression coverage:** convert confirmed defects into automated tests whenever practical.
46. **Review before execution:** inspect unknown scripts, build hooks, binaries, and third-party actions before running them.
47. **Use synthetic or sanitized data:** prevent private user data, credentials, and production records from entering tests or logs.
48. **Measure resource use:** track CPU, memory, storage, network, and power where relevant to the product.
49. **Test failure paths:** cover malformed input, unavailable services, timeouts, cancellation, disk-full, and resource exhaustion.
50. **Stop on uncertainty:** pause expansion when the current change is unverified or its blast radius is unknown.

## IV. Collaboration and interface governance (51–65)

51. **Convert feedback into evidence:** turn user reports into reproducible cases and acceptance criteria.
52. **Protect compatibility:** assess all consumers before changing public interfaces or data formats.
53. **Name for clarity:** use stable, descriptive names for modules, symbols, tests, and configuration.
54. **Record architectural decisions:** document material trade-offs and alternatives in ADRs.
55. **Avoid dependency inflation:** add packages only when ownership, license, maintenance, and benefit are understood.
56. **Keep commits coherent:** use focused changes and meaningful commit messages.
57. **Keep PRs reviewable:** group related changes and explain behavior, risks, and verification.
58. **Require independent review:** review correctness, security, maintainability, and compatibility—not just formatting.
59. **Document non-obvious behavior:** comments should explain constraints and reasoning, not restate code.
60. **Keep secrets out of Git:** use approved secret stores and rotate credentials exposed in history.
61. **Protect personal and operational data:** redact logs, fixtures, issue reports, and CI artifacts.
62. **Verify trusted contributions:** provenance does not replace tests or review.
63. **Version integration contracts:** define compatibility rules for cross-repository APIs and schemas.
64. **Update user-facing docs:** align README, changelog, setup, migration, and operations guidance with actual behavior.
65. **Separate permissions:** developers, CI jobs, release bots, and autonomous agents must have distinct scopes.

## V. OSINT, DevSecOps, and supply-chain security (66–85)

66. **Use authorized scope only:** passive public-source research and active testing must remain within legal and explicitly authorized boundaries.
67. **Make builds reproducible:** pin toolchains and dependencies where supported; record provenance and build inputs.
68. **Harden CI identities:** use read-only defaults, narrowly scoped permissions, and short-lived credentials.
69. **Protect production branches:** require review and relevant checks; prohibit unreviewed direct pushes where governance permits.
70. **Retain evidence responsibly:** store CI reports and artifacts with access controls and explicit retention periods.
71. **Record artifact provenance:** include version, source commit, digest, build parameters, and signing information.
72. **Run static checks:** apply formatters, linters, type checks, SAST, and project-specific analyzers.
73. **Review repository history:** investigate unexpected commits, workflow edits, permission changes, and suspicious file additions.
74. **Audit the dependency graph:** inspect direct and transitive dependencies, advisories, maintainers, and package sources.
75. **Keep manifests consistent:** validate lockfiles, package manifests, submodules, and declared runtime versions.
76. **Verify release artifacts:** check signatures, hashes, provenance attestations, and correspondence to reviewed source.
77. **Test defensively:** use unit, integration, fuzz, stress, and regression tests in controlled environments.
78. **Check determinism:** repeat critical tests and builds to identify hidden environmental dependencies.
79. **Triage vulnerabilities:** assess exploitability, reachability, severity, affected versions, and remediation status.
80. **Limit infrastructure assessment:** inspect DNS, TLS, and exposed services only for owned or explicitly authorized assets.
81. **Secure network clients:** validate certificates, use TLS, set timeouts, constrain redirects, and handle failures safely.
82. **Keep private code private:** use local or contractually approved scanners for confidential source and artifacts.
83. **Validate configuration hygiene:** detect committed secrets, unsafe defaults, leaked paths, and environment-specific assumptions.
84. **Maintain a technical relationship graph:** map repositories, modules, packages, workflows, APIs, owners, and external services.
85. **Respect legal and privacy boundaries:** do not use leaked credentials, private personal data, unauthorized access, or covert targeting.

## VI. Analysis, reporting, and continuous improvement (86–100)

86. **Answer the audit questions:** what failed, where, why, under which conditions, and what is the safest correction?
87. **Rate evidence separately:** distinguish confirmed defects, likely risks, and unverified hypotheses.
88. **Perform root-cause analysis:** connect symptoms to the originating condition and contributing factors.
89. **Detect change anomalies:** investigate unexpected dependency, complexity, binary-size, performance, and failure-rate changes.
90. **Write actionable reports:** summarize impact, evidence, severity, owner, remediation, and verification.
91. **Use BLUF:** put the principal finding and decision first.
92. **State unknowns:** disclose untested areas, missing evidence, and limits of confidence.
93. **Compare scenarios:** present a minimal safe fix, a complete improvement, and a rollback or containment option.
94. **Keep tests honest:** do not weaken assertions, skip failing suites, or hide warnings to manufacture green CI.
95. **Secure delivery:** verify approvals, checks, signatures, permissions, provenance, and release notes.
96. **Apply data lifecycle rules:** remove temporary artifacts and expired sensitive data under documented retention policy.
97. **Run postmortems:** capture causes, impact, detection gaps, corrective actions, and owners.
98. **Update defenses:** turn new failure modes and threat intelligence into controls and regression tests.
99. **Automate repeatable work:** promote validated manual checks into scripts, CI jobs, and reusable tools.
100. **Measure outcomes:** report verified gains in reliability, security, performance, usability, or maintainability—not activity counts.

## Repository adoption contract

Each repository must:
- retain its own architecture, build, test, release, and security workflows;
- map each applicable principle to an existing control, a planned control, or an explicitly accepted exception;
- record evidence and the commit SHA for completed controls;
- classify controls as `implemented`, `partial`, `planned`, `not-applicable`, or `blocked`;
- never claim that a control passed when it was not executed;
- use feature branches and pull requests for changes to the protected production branch;
- merge only after required checks pass, conflicts are resolved, and the current PR head has been reviewed.

## Evidence record

For every material finding or control, record: `id`, `repository`, `commit_sha`, `observed_at`, `source`, `evidence`, `confidence`, `severity`, `owner`, `status`, `remediation`, and `verification`.

## Release gate

A green documentation or hygiene check is not a production certification. A release is eligible only when the repository's applicable build, test, security, compatibility, and packaging checks pass; unresolved high-severity risks are dispositioned; and rollback instructions are current.
