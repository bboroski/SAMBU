# Owner Working Profile & Engineering Translation

**Version:** 1.0  
**Updated:** 2026-11-12  
**Scope:** project execution preferences and engineering rules for this repository  
**Owner:** repository maintainer

> This document translates recurring project and collaboration preferences into operational engineering guidance. It is not a clinical psychological assessment, diagnosis, or a public biography. It deliberately excludes speculative claims about private life, health, relationships, emotions, and other personal matters.

## 1. Working profile: observed preferences

The maintainer's recurring requests show the following project-facing preferences:

- **Systems thinking:** understand the repository as a product with architecture, interfaces, tests, documentation, release lifecycle and dependencies—not merely as a collection of files.
- **Originality with coherence:** preserve a distinct product identity while using shared ecosystem-wide quality rules.
- **Execution over appearance:** distinguish implemented behavior from proposals, mockups, plans and incomplete work.
- **High quality bar:** favor reproducible builds, meaningful tests, security boundaries, explicit evidence and maintainable documentation.
- **Autonomy with guardrails:** automate repeatable analysis and validation, but keep consequential changes reviewable, auditable and reversible.
- **Iterative creation:** explore broadly, then narrow scope into small, testable increments and complete release milestones.
- **Precision:** avoid filler, duplicated concepts, vague status claims and unnecessary process overhead.
- **Cross-disciplinary design:** allow engineering, product design and creative direction to inform one another without weakening technical contracts.

These are working preferences inferred from project interactions. They should guide collaboration, not be treated as fixed personality traits.

## 2. Product identity and architectural sovereignty

1. This repository retains its own mission, name, architecture, API, data model, dependencies, license, maintainers and release cadence.
2. Shared standards govern quality and collaboration; they do not prescribe identical internal implementations.
3. Do not turn independent projects into one inseparable monolith.
4. Do not duplicate another repository's kernel, runtime, registry or control-plane ownership.
5. Integrate through explicit, versioned contracts, documented adapters and compatibility tests.
6. Preserve existing behavior unless a change is intentional, documented and tested.
7. Do not overwrite project-specific documentation with generic ecosystem language.
8. Any cross-repository dependency must identify its owner, version/range, failure mode and compatibility policy.

## 3. Decision and execution protocol

For every non-trivial change:

1. **Understand:** inspect README, source layout, build system, tests, workflows, license and relevant architecture records.
2. **Define:** state the user problem, scope, non-goals, acceptance criteria and affected interfaces.
3. **Plan:** split work into small independently reviewable changes; identify risks and rollback.
4. **Implement:** follow local conventions and keep changes minimal and cohesive.
5. **Verify:** run the repository's relevant formatter, static checks, tests and build; report unavailable target/hardware checks explicitly.
6. **Document:** update usage, architecture, limitations and status where behavior changes.
7. **Review:** inspect the diff for accidental scope expansion, secrets, license issues, compatibility breaks and unsupported claims.
8. **Deliver:** use a focused branch and pull request; merge only after required checks and human/repository policy approval.

Do not ask for information that can be established safely from repository evidence. Ask before irreversible, destructive, security-sensitive or externally visible decisions when intent is ambiguous.

## 4. Definition of done

A change is complete only when all applicable conditions hold:

- acceptance criteria are met;
- implementation exists (not merely a plan or mockup);
- relevant automated tests pass;
- build and platform evidence are accurately reported;
- documentation matches actual behavior;
- security and privacy implications are reviewed;
- compatibility and migration impacts are addressed;
- failure behavior and rollback are understood;
- the final diff contains no unrelated changes;
- remaining limitations are explicitly listed.

Use status labels consistently:

- **Implemented:** present in source and verified by relevant tests.
- **Partial:** some behavior exists, with explicit missing parts.
- **Planned:** documented intention; no claim of working implementation.
- **Blocked:** cannot proceed due to a named dependency or missing evidence.
- **Unverified:** implementation may exist, but required evidence is unavailable.

A green host CI run is not proof of physical hardware qualification. A checksum is not proof of publisher identity. A design preview is not a live application. A draft PR is not a production release.

## 5. Quality attributes

Evaluate changes against the attributes relevant to this product:

- correctness and deterministic behavior;
- clear module ownership and low coupling;
- secure defaults and least privilege;
- explicit trust boundaries and input validation;
- privacy by minimization and local-first handling where applicable;
- observability without leaking secrets or personal data;
- accessibility and usable failure states for user-facing software;
- portability and target-specific qualification;
- maintainability, reproducibility and documented dependencies;
- performance proportional to measured requirements.

## 6. Automation and autonomous improvement

Automation should progress through controlled stages:

**Observe → Analyze → Recommend → Prepare patch → Test → Review → Approve → Release → Measure.**

Default policy:

- read-only discovery before mutation;
- no silent destructive operations;
- no automatic production deployment from an unreviewed generated patch;
- least-privilege credentials and workflow permissions;
- pinned or bounded dependencies with update policy;
- auditable logs that avoid secrets and unnecessary personal data;
- reproducible evidence for every generated recommendation;
- human approval for security-sensitive, data-loss, privilege, release and cross-repository changes;
- rollback path for every automated mutation that can affect users or production state.

Autonomy is a product capability only when its boundaries, permissions, tests and failure modes are implemented—not because a roadmap describes it.

## 7. Scope and prioritization

Use four queues:

1. **Release blockers:** correctness, security, data loss, broken build or critical user journey.
2. **Committed milestone:** the smallest complete increment with measurable acceptance criteria.
3. **Next improvements:** valuable work intentionally deferred from the current milestone.
4. **Research:** experiments and speculative concepts that must not silently enter production scope.

Limit work in progress. Prefer a verified, usable increment over a large collection of unfinished features. New ideas belong in a backlog until they are selected deliberately.

## 8. Collaboration and communication

- Be direct, precise and outcome-oriented.
- Preserve the maintainer's stated intent and repository identity.
- Bring a proposed solution, not only a list of problems.
- Separate verified facts, assumptions and recommendations.
- Do not claim a command, test, merge, deployment or hardware check occurred unless evidence confirms it.
- Report what changed, why, how it was tested, and what remains.
- Keep pull requests focused and reviewable.
- Prefer fewer, higher-value clarification questions; never guess across a destructive or security-critical boundary.

## 9. Creative and product direction

Originality is a design goal, not permission to compromise usability or correctness.

- Give each product a recognizable identity grounded in its purpose.
- Avoid generic filler, duplicated features and decorative complexity.
- Keep shared visual/design systems accessible and adaptable to the product.
- Treat experimental concepts as experiments until user value and feasibility are demonstrated.
- Preserve creative freedom inside explicit technical and safety constraints.

## 10. Repository-specific integration boundary

The section below is authoritative for how this shared working profile applies here. The repository's existing architecture, README, tests, license and accepted ADRs remain authoritative for implementation details.

**Repository:** `bboroski/SAMBU`

**Project-specific application:** Language, scientific modelling and automation environment. Keep language/runtime/tooling ownership here; integrate with NUN only through explicit versioned contracts. Do not move SAMBU language semantics into the NUN kernel.

### Local implementation rules

- Read this repository's current architecture and ownership records before changing code.
- Apply the shared working profile through this project's native language, build, test and release conventions.
- Do not import another project's internal modules merely to make implementations look uniform.
- Any integration must be opt-in, versioned, tested and documented in this repository.
- Keep project-specific roadmap and status claims evidence-based.

## 11. Maintenance

Review this document when the repository's mission, ownership boundaries or release governance materially changes. Update it through a normal pull request. Do not treat it as a substitute for architecture decision records, contribution guidance, security policy or technical specifications.
