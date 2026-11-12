# Engineering Standard

**Standard ID:** PERSONA-ENG-STD  
**Version:** 1.0.0  
**Applies to:** this repository and its independently released components  
**Status:** normative baseline; repository-specific profile is authoritative for local scope

## 1. Purpose and precedence

This standard defines the minimum engineering controls shared across the bboroski repository ecosystem. It does not define a shared application architecture, runtime, language, build system, release cadence, or product roadmap.

The file `.engineering/profile.json` is the repository-specific overlay. Where a local architecture or safety boundary is narrower than a general recommendation here, the narrower boundary wins. Existing documented contracts, platform constraints, licenses, and repository-specific build/test procedures remain in force.

## 2. Architecture preservation

1. Preserve this repository's product identity, domain, language choices, module boundaries, public APIs, data formats, and native build system.
2. Do not introduce a common runtime, framework, dependency, folder layout, or cross-repository import merely to make repositories look alike.
3. Integrate repositories only through explicit, documented, versioned contracts and adapters. No implicit shared-memory, filesystem, process, or hardware access is assumed.
4. Prefer additive and backward-compatible changes. Breaking changes require rationale, migration guidance, compatibility impact, and an independently reviewable change.
5. Keep experimental, partial, target-dependent, and production-qualified capabilities visibly distinct.

## 3. Change control

1. Implement changes on a focused topic branch and propose them through a Pull Request.
2. Keep a PR small enough to review; split unrelated work.
3. Describe intent, affected components/contracts, alternatives, risk, compatibility, tests, documentation, and rollback.
4. Inspect the complete diff. Never accept conflict sides wholesale without understanding file semantics.
5. Do not bypass failing checks, required review, repository policies, or protected-branch controls.
6. Never claim a PR is merged, a feature is released, or a deployment succeeded before the corresponding system confirms it.

## 4. Verification and evidence

1. Run the repository's native build, test, lint, static-analysis, and documentation checks relevant to the change. Use the exact commands documented by this repository.
2. Add or update positive, negative, boundary, and regression tests for behavior changes.
3. Test the current PR head, not an earlier local state.
4. Treat host tests, emulators, simulations, static analysis, and design previews only as the evidence they actually provide. They do not imply hardware qualification or real-world operation.
5. Record exact commands and outcomes. Mark unavailable checks as not run, explain why, and identify the remaining risk.
6. Do not add fake tests, synthetic “success” output, invented benchmarks, or unsupported capability claims.

## 5. Security, privacy, and supply chain

1. Apply least privilege to workflows, tokens, credentials, local services, and application capabilities.
2. Do not commit secrets, credentials, private user data, machine-specific paths, or generated sensitive artifacts.
3. Review dependency additions, versions, licenses, provenance, and known vulnerabilities.
4. New workflows default to read-only permissions. Grant write access only to the specific job that needs it and document the reason.
5. Treat external inputs, downloaded artifacts, manifests, and inter-repository data as untrusted until validated.
6. Destructive operations require explicit target identification, confirmation, bounded scope, and a recovery plan.
7. Document privacy behavior and data-flow boundaries. Do not infer consent to upload or transmit local data.

## 6. Documentation and decisions

1. Update documentation when behavior, interfaces, commands, configuration, support claims, or operational procedures change.
2. Keep examples executable or explicitly label them as illustrative.
3. Record significant architecture decisions and their consequences in the repository's established ADR/design location; do not create a second competing decision system.
4. Keep README and translated variants scope-equivalent where the project maintains them.
5. State limitations and non-goals alongside capability claims.

## 7. Release and operations

1. A merged change is not automatically a release.
2. Release readiness requires passing applicable native checks, reviewed dependencies, documented compatibility, known-issue disclosure, and a rollback/recovery path appropriate to the product.
3. Platform-specific or hardware-specific claims require evidence from that target class.
4. Maintain independent versioning and release decisions for independent repositories and components.

## 8. Required evidence gates

Every material change must address the following gates. “Not applicable” is allowed only with a short reason.

| Gate | Minimum evidence |
|---|---|
| Profile validation | `.engineering/validate.py` passes |
| Native project checks | Existing project build/test workflows pass, or missing evidence is disclosed |
| Architecture and compatibility | Affected boundaries and public contracts reviewed |
| Security and privacy | Secrets, permissions, data flow, dependencies, and destructive effects reviewed |
| Documentation | User/developer/operational docs updated or marked not applicable with reason |
| Human review | Independent review appropriate to repository policy |
| Target qualification | Required for platform/hardware claims; otherwise explicitly not applicable |

## 9. Status vocabulary

Use these labels precisely; they are not interchangeable:

- **PROPOSED** — suggested, not implemented.
- **PLANNED** — accepted for future work, not implemented.
- **IMPLEMENTED** — code or configuration exists; verification may still be pending.
- **TESTED** — specified tests were run and passed; scope of tests must be stated.
- **VERIFIED** — the stated acceptance criteria have evidence.
- **MERGED** — the change is present in the target branch.
- **RELEASED** — a versioned release was published.
- **BLOCKED** — progress is stopped by a stated dependency, failure, or decision.

A design mockup, open PR, passing metadata check, or host test must not be described as a production release or hardware qualification.

## 10. Ternary decision model

Use the project's risk model where useful:

- **-1 / reject:** regression, unsafe boundary, failed invariant, or insufficient evidence.
- **0 / hold:** unknown, incomplete, or not yet verified; gather evidence.
- **+1 / accept:** acceptance criteria pass and required review is complete.

A score never overrides a failed mandatory gate or human approval requirement.

## 11. Definition of Done

A change is done only when its scope is implemented, relevant native checks have been run, results are recorded, security and compatibility have been considered, documentation is accurate, the complete diff has been reviewed, and required review/merge/release steps are confirmed. Unavailable target evidence remains an explicit limitation, not an implied success.

## 12. Enforcement boundary

The `Engineering Standard / profile-validation` workflow validates the machine-readable local profile. Existing repository workflows remain responsible for native builds and tests. Repository administrators must configure the profile-validation check and applicable native checks as required status checks in branch protection/rulesets before GitHub can block merges on them. This change does not silently rewrite branch protection or bypass existing rules.
