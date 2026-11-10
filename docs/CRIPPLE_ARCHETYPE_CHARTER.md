# Cripple Systems Engineering Constraints

**Baseline:** SAMBU 0.11.0 alpha  
**Status:** mixed — bounded policy and evidence APIs are implemented in the Python host layer; OS isolation, autonomous execution and native self-modification remain planned.

## Scope

This specification consolidates six engineering control groups into testable requirements. The implemented layer inspects declared task metadata, constructs bounded plans, records observations, verifies journal integrity and preflights proposed changes. It does not execute arbitrary experiments, write repository files, modify its own policy, issue credentials, merge pull requests, deploy software or claim test success without external results.

## 1. Resource and authority control

| Control | Requirement | Acceptance condition |
|---|---|---|
| Adaptive quotas | Intersect requested budgets with immutable policy ceilings; telemetry may only recommend lower limits. | Requests above a ceiling are component-wise capped and clipped fields are reported. |
| Leased capabilities | Grant named capabilities to one declared task; the host owns expiry and revocation. | Undeclared operations are denied; no ambient filesystem or network access is implied. |
| Reversible changes | Require rollback notes and preserved prior state for mutations. | Irreversible changes are excluded from the autonomous preflight lane. |
| Bounded containment | Cap manifests, queues and payloads; isolate untrusted execution at a future OS boundary. | Input limits are checked; an in-process callback is never described as a sandbox. |
| Auditable evidence | Store observations in an append-only SHA-256 chain. | Recomputed chains verify; altered records fail verification. |
| Recovery ceilings | Bound retries, restarts and escalation. | Exhaustion is explicit and never reported as success. |
| Replay identity | Record canonical input fingerprints, seeds, method IDs and ordered observations. | Identical declared inputs yield identical fingerprints; full execution replay remains unimplemented. |

## 2. Systematic discovery

Every investigation declares a falsifiable question, scope and success metric. Trials use fixed inputs, isolated workspaces and explicit resource limits. Preserve discoveries, failed attempts, seeds and evidence references without retaining secret payloads. Promote work through proposal → prototype → tested → reviewed → stable; a documentation label cannot promote a capability.

**Acceptance:** hypotheses identify supporting and refuting observations; duplicate fingerprints are detectable; evidence is queryable and hash-verifiable; promotion requires implementation, tests, review and compatibility evidence. A future runner must prove filesystem, network, process and time isolation.

## 3. Fault management

Use finite recovery tiers: local retry, child restart, sibling-group restart, parent escalation and terminal stop. Degrade optional work while preserving required invariants. Supervision trees own failure response and child lifecycle. Restore only declared initial snapshots or verified checkpoints; never blindly replay failed side effects. Record host-supplied timestamps, counters and error identifiers separately from interpretation.

**Acceptance:** every tier has a finite budget and event record; supervisor cycles and multiple parents are rejected; restart state, queued messages and dead letters are specified; limit exhaustion produces an explicit failed state.

## 4. Isolation and capability control

Tasks declare required capabilities in immutable manifests containing task identity, purpose, risk tier, seed and resource budget. Use narrow versioned interfaces and validated transfer objects. Third-party code requires a separate process, container or VM when an isolated executor is delivered. Verify non-interference with negative tests and OS-level enforcement.

**Acceptance:** undeclared operations are denied at the host boundary; equal manifests and policies yield stable plan digests; no current in-process API is called a security sandbox; extensions cannot reach unrelated interpreter internals through implicit globals.

## 5. Adversarial design review

Compare at least two candidate designs, including a no-change baseline, before high-impact refactoring. Review breakage, authority expansion, irreversible effects, abuse cases, compatibility and failure detection. Specify evaluation order, overflow, errors, cancellation and concurrency before optimization. Store decisions, alternatives and consequences as version-controlled records. Prefer feature gates and reversible migrations.

**Acceptance:** material changes link an architecture decision record; tests, benchmarks, diagnostics and compatibility evidence gate promotion; rollback is executable and tested.

## 6. Handoff and authority governance

Bind trust to principal, task, resource and duration. Define ownership transfer for success, timeout, cancellation and compensation. Separate proposal, review, approval, merge and deployment. Specify ABI, layouts, calling convention, ownership and error mapping before native interoperability. Preserve versioning, migration guides and evidence trails.

**Acceptance:** no global administrator capability is inherited by ordinary tasks; no resource or message silently disappears at handoff; the autonomy layer can propose or reject but cannot merge or deploy; high/critical-risk work requires accountable human review.

## Implemented API surface

- `ResourceBudget.cap_to()`: component-wise budget capping.
- `TaskManifest`, `AutonomyPolicy` and `SambuMachine.plan()`: immutable task declaration, capability checks and deterministic plan digest.
- `ExperimentLedger`: bounded append-only observations, input fingerprints and hash-chain verification.
- `ChangeProposal` and `SambuMachine.evaluate_change()`: scope, evidence, tests, risk and reversibility preflight.

Default capabilities remain narrow: `compute`, `ledger.read` and `ledger.append`. Network, filesystem, process launch, package installation and repository writes are not granted by default.

## Change verdicts

| Verdict | Meaning |
|---|---|
| `rejected` | Scope, evidence, tests, reversibility or critical-risk constraints failed. |
| `human_review_required` | The proposal is structurally valid but exceeds the autonomous risk ceiling. |
| `ready_for_tests` | Preflight passed; independent tests and review are still required. |

A preflight verdict is not approval, merge, deployment, safety certification or a test result. Protected paths include `.github/`, `.git/`, secrets, packaging metadata and build configuration.

## Delivery gates

1. **Policy correctness:** capability denial, budget capping, deterministic fingerprints, ledger integrity and protected-path tests.
2. **Isolated execution:** enforceable CPU, memory, output, process, filesystem and network quotas; kill/reap semantics; adversarial escape tests.
3. **Evidence-driven changes:** baseline/alternative comparison, reproducible environment fingerprints, artifact hashes, command exit status and rollback plan.
4. **Native integration:** typed/effect-aware IR, ABI validation and explicit ownership before native edits or self-hosting.

## Non-negotiable invariants

1. A task goal or prompt never grants a capability.
2. Previous success never expands a resource ceiling.
3. Failures remain visible evidence and are not relabeled as success.
4. A hash chain proves sequence integrity only, not truth.
5. Preflight is not test completion, certification or release approval.
6. The policy core cannot execute arbitrary callables or write repository files.
7. Self-improvement cannot weaken policy, erase its audit trail or approve its own release.
8. Native code and hardware access remain target-specific and independently reviewed.
