# Beelzebub 66 — repository security contract

**Policy version:** 1.0.0  
**Scope:** this repository's source, dependencies, build pipeline, release artifacts and security events.  
**Operating model:** local-first, least privilege, evidence before enforcement.

This is a 66-control security baseline. A rule marked *policy/future integration* is a requirement, not a claim that a runtime sensor, OS agent, signing service or central threat exchange is already deployed. The local scanner is read-only apart from its JSON report. Findings are reviewable evidence; they never authorize destructive remediation by themselves.

## I. Reconnaissance and detection (01–11)

1. **Asset inventory** — enumerate source, executable, configuration, dependency and generated-artifact paths.
2. **Integrity measurement** — calculate SHA-256 digests for selected critical files and compare against an explicitly trusted baseline.
3. **Malware indicators** — detect known signatures and suspicious code combinations; report evidence and confidence, not unsupported verdicts.
4. **Secret discovery** — scan for private keys, access tokens, passwords and credential-like assignments; redact matched values.
5. **Dependency analysis** — inventory manifests and lockfiles; check advisories using a trusted vulnerability source when configured.
6. **Supply-chain provenance** — record package source, version, checksum and publisher/provenance metadata where available.
7. **Obfuscation detection** — flag suspicious encoded payloads, dynamic loading and concealed execution patterns for review.
8. **Change intelligence** — compare pull-request changes with repository history and identify unexpected high-risk modifications.
9. **Configuration audit** — inspect security-relevant settings, exposed services, permissions and unsafe defaults.
10. **Binary inspection** — inventory unknown executable artifacts and compare hashes; use format-specific scanners where available.
11. **Event correlation** — correlate independent findings by file, commit, dependency and time window without treating one weak signal as proof.

## II. Interception and containment (12–22)

12. **Least privilege** — grant each job and process only the permissions it needs; default to read-only CI tokens.
13. **Process isolation** — run untrusted builds and tests in disposable, restricted runners or containers.
14. **System-call policy** — use supported OS/container controls (seccomp, AppArmor, sandbox profiles) where the deployment platform supports them.
15. **Filesystem protection** — protect source, policy, signing keys and release paths; detect unexpected writes and deletions.
16. **System configuration protection** — monitor registry or equivalent OS settings only on platforms where they exist.
17. **Network egress control** — restrict outbound destinations for build/test jobs and log exceptional connections.
18. **IPC protection** — constrain named pipes, sockets and other inter-process channels according to platform capabilities.
19. **Memory safety controls** — enable compiler hardening and OS mitigations; never corrupt pointers or manipulate another process's memory.
20. **Persistence detection** — audit startup entries, scheduled tasks, services and equivalent persistence mechanisms where applicable.
21. **Build-environment isolation** — separate untrusted pull-request jobs from deployment credentials and production systems.
22. **Safe quarantine** — preserve the original, capture hashes and metadata, and move a suspect artifact only under an explicit, reversible policy.

## III. Source-code protection (23–33)

23. **Pre-merge validation** — scan changed files and run relevant security tests before merge.
24. **Independent review** — require review for authentication, cryptography, permissions, build and release logic.
25. **Protected default branch** — require pull requests, checks and appropriate approvals; prohibit unreviewed direct pushes.
26. **History integrity** — audit force-pushes, rewritten history and unexpected changes to protected refs.
27. **Source substitution detection** — compare generated, vendored and critical files against reviewed provenance or pinned digests.
28. **Unsafe API review** — flag dangerous deserialization, shell execution, dynamic evaluation and insecure cryptographic APIs.
29. **Input validation** — validate untrusted input at trust boundaries and test malformed, oversized and adversarial values.
30. **Serialization safety** — use safe parsers, bounded inputs and explicit schemas; avoid unsafe object deserialization.
31. **Cryptographic correctness** — use maintained libraries, authenticated encryption and secure random generation; never invent primitives.
32. **Authorization checks** — test server-side permission boundaries and deny-by-default access decisions.
33. **Dynamic-code controls** — restrict plugin loading, runtime compilation and execution of generated code.

## IV. Build and release integrity (34–44)

34. **Pre-build gate** — validate policy, secrets, dependencies and source state before compiling.
35. **Ephemeral build workers** — use disposable workers with no unnecessary persistent credentials or caches.
36. **Pinned dependencies** — pin direct dependencies and use supported lockfiles.
37. **Lockfile verification** — detect unexpected lockfile drift and require reviewed dependency updates.
38. **Toolchain integrity** — pin compiler, package manager, build image and CI actions to trusted versions or immutable digests.
39. **Environment validation** — allowlist build variables and prevent untrusted input from controlling privileged commands.
40. **CI secret isolation** — expose deployment secrets only to trusted protected-branch/release jobs.
41. **Artifact scanning** — inspect outputs for embedded credentials, unexpected executables and policy violations.
42. **SBOM generation** — produce a machine-readable component inventory for supported release builds.
43. **Artifact signing** — sign release artifacts when managed signing keys and verification are configured.
44. **Provenance and reproducibility** — retain build metadata, checksums and provenance attestations; compare reproducible builds where feasible.

## V. Resilience and recovery (45–55)

45. **Continuous integrity checks** — re-check critical files and release artifacts at defined lifecycle points.
46. **Repeat-attack detection** — correlate recurring indicators and preserve incident timelines.
47. **Ransomware indicators** — detect rapid mass rewrites, extension changes and suspicious file-encryption patterns in monitored environments.
48. **Backup tamper detection** — monitor backup deletion or modification and keep backups outside the build runner's trust boundary.
49. **Critical-change approval** — require explicit review for changes to security policy, workflows, keys and recovery mechanisms.
50. **Trusted checkpoints** — retain immutable, verified source and release checkpoints.
51. **Trusted-state recovery** — restore only from verified commits and artifacts; preserve forensic evidence first.
52. **Recovery testing** — periodically test restoration and verify hashes and application health.
53. **Incident analysis** — record timeline, scope, evidence, containment and follow-up actions.
54. **False-positive handling** — provide documented suppressions with owner, rationale, scope and expiry; never silently ignore findings.
55. **Rule evolution** — update detection rules through reviewed, versioned changes with regression tests.

## VI. Cross-repository coordination (56–66)

56. **Repository registry** — maintain an explicit inventory of enrolled repositories and their default branches.
57. **Local project profile** — detect languages, build systems and release surfaces; keep project-specific exceptions local and reviewable.
58. **Policy versioning** — pin a policy version per repository and report drift from the approved baseline.
59. **Autonomous local agent** — keep scanning and reporting functional when the central coordinator is unavailable.
60. **Signed threat exchange** — exchange minimal, signed indicators only after a verified trust channel is deployed.
61. **Update authenticity** — verify signatures, schema version, freshness and replay protection before accepting central policy updates.
62. **Repository discovery** — propose newly discovered repositories for enrollment; do not silently grant permissions or change branch rules.
63. **Component discovery** — detect new files, manifests and build components during scans and update inventory.
64. **Incident correlation** — correlate indicators across enrolled repositories while preserving local evidence and ownership.
65. **Audit and reporting** — produce per-repository reports and a cross-repository status view with evidence and timestamps.
66. **Self-health verification** — test scanner, policy, workflow, report generation and update verification; fail visibly when a control is unavailable.

## Enforcement model

- **Active baseline:** local read-only secret-pattern scan, dependency-manifest inventory, JSON report and CI execution where the repository's Beelzebub workflow/scanner is present.
- **Policy controls:** source review, protected branches, CI permissions, dependency pinning and artifact handling; enable through repository settings and workflow configuration.
- **Platform-dependent controls:** OS process/network/filesystem monitoring, system-call restrictions, runtime memory protections and ransomware behavior detection. These require a separately deployed, platform-specific agent and are not provided by a GitHub source scanner.
- **Future federation:** signed threat exchange and central orchestration remain inactive until identity, key management, schema validation, privacy and replay protection are implemented and tested.

## Safety invariants

Beelzebub does not autonomously delete source, kill processes, rewrite history, force-push, replace dependencies, alter production systems or quarantine user data. It emits evidence and proposed remediations. Any enforcement beyond CI findings requires explicit repository policy, reversible actions and an auditable approval path.

## Repository-specific adapter

This file is committed separately in each repository. The adapter must be completed from that repository's actual language/build/release inventory; no language, runtime or OS capability is assumed from the repository name alone.

### Local adapter: bboroski/SAMBU

New programming language: prioritize compiler/parser inputs, code generation, package resolution, toolchain pinning and fuzz/property tests for parsers. Apply native compiler hardening where supported.

**Enrollment status:** policy added on the Beelzebub foundation branch; merge and CI validation are still required before this becomes an enforced default-branch control.
