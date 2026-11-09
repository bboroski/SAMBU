# Cripple Archetype Engineering Charter

**Baseline:** SAMBU 0.11.0 alpha  
**Status:** mixed — bounded autonomy policy core implemented as a Python-host API; native sandboxing, autonomous execution and self-modifying compilation remain planned.  
**Purpose:** turn six fictional/philosophical archetypes supplied by the project author into concrete, testable engineering constraints. The names are mnemonic labels for design patterns, not software dependencies or claims about canonical lore.

> **Constitutional boundary:** SAMBU may autonomously inspect declared inputs, construct plans, compare evidence and reject unsafe proposals. This layer does not execute arbitrary experiments, modify repository files, change its own policy, issue credentials, merge pull requests, deploy software or claim that a test passed without an external test result.

## 1. The six design lenses

Each letter is a separate engineering rule. The mapping is intentionally literal so that every character in each name contributes one requirement.

### 1.1 ALUCARD — power must remain bounded and inspectable

| Letter | Engineering rule | SAMBU mechanism | Acceptance condition |
|---|---|---|---|
| **A** | Adaptive quotas | Intersect a task's requested budget with immutable policy ceilings. Telemetry may recommend smaller budgets, never silently larger ones. | A task above a ceiling receives the component-wise capped budget and a list of clipped fields. |
| **L** | Leased authority | Grant only named capabilities for one declared task; host adapters own expiry and revocation. | An undeclared capability is denied; no ambient filesystem or network authority is implied. |
| **U** | Undoable transitions | Require reversible change plans, explicit rollback notes and preserved prior state for mutations. | Irreversible changes are rejected from the autonomous lane. |
| **C** | Containment | Keep task manifests, actor mailboxes and payloads bounded; isolate untrusted execution in a future OS process/container boundary. | Input limits are checked; no in-process Python callback is misrepresented as a sandbox. |
| **A** | Auditable history | Record experiment observations in an append-only SHA-256 hash chain. | Recomputed chain verification succeeds; mutated records fail verification. |
| **R** | Recovery ceilings | Use bounded retry/restart windows and escalate to supervisors. | Restart limits are finite; exhaustion remains visible and is never treated as success. |
| **D** | Deterministic replay inputs | Record canonical input fingerprints, seeds, method IDs and ordered observations. | Identical declared inputs produce identical fingerprints; full execution replay remains a later feature. |

### 1.2 GING — discovery must be systematic, not magical

| Letter | Engineering rule | SAMBU mechanism | Acceptance condition |
|---|---|---|---|
| **G** | Goal-bound inquiry | Every investigation begins with a falsifiable question, scope and success metric. | Hypotheses state what observation would support or refute them. |
| **I** | Isolated trials | Run experiments in disposable workspaces with fixed inputs and explicit resource limits. | Future runner must prove filesystem, network, process and time boundaries; the current ledger only records results. |
| **N** | Novelty and memory | Preserve discoveries, failed attempts, seeds and evidence references without storing raw secret inputs. | Duplicate experiment fingerprints can be detected; evidence is queryable and hash-verifiable. |
| **G** | Graduation gates | Move ideas through proposal → prototype → tested → reviewed → stable. | A documentation label cannot promote a capability; promotion requires code, tests, review and compatibility evidence. |

### 1.3 RAIDEN — reliability is a chain of accountable decisions

| Letter | Engineering rule | SAMBU mechanism | Acceptance condition |
|---|---|---|---|
| **R** | Recovery tiers | Local retry, child restart, sibling-group restart, parent escalation and terminal stop. | Every tier has a finite budget and produces an inspectable event. |
| **A** | Adaptive degradation | Reduce optional workload under pressure while preserving required invariants. | Degradation policy declares what may be dropped and what must never be dropped. |
| **I** | Incident supervision | Supervision trees own failure response and child lifecycle. | Cycles and multiple parents are rejected; escalation does not recurse without a ceiling. |
| **D** | Deterministic restoration | Restore the declared initial snapshot or a verified checkpoint; never replay a failed side effect blindly. | Restart semantics specify state, queued messages and dead-letter treatment. |
| **E** | Escalation budgets | Bound restarts, retries, elapsed logical work and incident history. | Exceeding a limit moves the component to an explicit failed state. |
| **N** | Neutral telemetry | Record facts, timestamps supplied by the host, counters and error identifiers separately from interpretation. | Monitoring never rewrites state or hides a failure to make a dashboard look healthy. |

### 1.4 DJINN — extension power is granted, never assumed

This is a metaphor for a capable but independent agent with its own boundaries; it is not an assertion about religious doctrine or a supernatural execution model.

| Letter | Engineering rule | SAMBU mechanism | Acceptance condition |
|---|---|---|---|
| **D** | Declared capabilities | A task lists every required capability in its manifest. | Undeclared operations are denied at the host boundary. |
| **J** | Job capsules | Bundle task identity, purpose, risk tier, seed and resource budget in an immutable manifest. | Plan digests are stable for identical manifests and policy. |
| **I** | Isolation profiles | Execute third-party code in a separate process/container/VM when such an executor is delivered. | No current in-process API is called a security sandbox. |
| **N** | Narrow interfaces | Pass validated data-transfer objects through small versioned ports. | Extensions cannot reach unrelated interpreter internals through an implicit global object. |
| **N** | Non-interference | Verify that a task cannot mutate another task's state or access undeclared resources. | Requires negative tests, OS-level enforcement and adversarial tests before being marked implemented. |

### 1.5 MADARA — strategy must survive adversarial review

| Letter | Engineering rule | SAMBU mechanism | Acceptance condition |
|---|---|---|---|
| **M** | Multiple models | Compare at least two candidate designs, including a no-change baseline, before high-impact refactoring. | The decision record states alternatives, costs and rejected options. |
| **A** | Adversarial challenge | Ask what breaks, who gains authority, what becomes irreversible and how failure is detected. | Security, compatibility and abuse cases are explicit review items. |
| **D** | Deterministic semantics | Define evaluation order, overflow, errors, cancellation and concurrency before optimizing. | Conformance fixtures pass across interpreter and future backends. |
| **A** | Architecture decisions | Store context, decision, alternatives and consequences in version-controlled records. | Material architectural changes have an ADR or a linked equivalent. |
| **R** | Reversible evolution | Prefer feature gates, migrations and rollbackable changes over destructive rewrites. | Rollback is testable, not merely promised in prose. |
| **A** | Acceptance evidence | Require tests, benchmarks, diagnostics and compatibility evidence for promotion. | A claim changes status only after its acceptance gate passes. |

### 1.6 SHANKS — strength includes knowing when to hand control over

| Letter | Engineering rule | SAMBU mechanism | Acceptance condition |
|---|---|---|---|
| **S** | Scoped trust | Bind permissions to a principal, task, resource and duration. | No global administrator capability is inherited by ordinary tasks. |
| **H** | Handoff contracts | Make ownership transfer explicit, including success, timeout, cancellation and compensation. | No resource or message silently disappears during handoff. |
| **A** | Authority separation | Keep proposal, review, approval, merge and deployment as separate responsibilities. | The autonomy core can propose or reject, but cannot merge or deploy. |
| **N** | Native interop contracts | Specify ABI, layouts, calling convention, ownership and error mapping before FFI. | No native plugin is advertised as stable without ABI and platform tests. |
| **K** | Knowledge continuity | Preserve semantic versioning, decision records, migration guides and evidence trails. | A maintainer can reconstruct why a feature exists and what depends on it. |
| **S** | Stewardship | Keep people responsible for high-impact choices and release authority. | High/critical-risk changes require human-governed review outside the autonomy lane. |

## 2. Implemented core: sambu.autonomy

The first code slice supplies deterministic policy and evidence primitives. It is a planning and preflight component, not an execution engine.

### 2.1 Resource ceilings

ResourceBudget defines maxima for steps, messages, payload bytes and retries. cap_to() computes the component-wise minimum and reports every clipped field. A task cannot enlarge the policy ceiling by asking for more.

### 2.2 Explicit task capsules

TaskManifest records a task name, purpose, requested capabilities, risk tier, deterministic seed and budget. SambuMachine.plan():

1. rejects capabilities absent from AutonomyPolicy.allowed_capabilities;
2. caps every requested resource limit;
3. withholds all grants when the task exceeds the autonomous risk ceiling;
4. produces a stable SHA-256 plan digest.

Default capabilities are intentionally narrow: compute, ledger.read and ledger.append. Network, filesystem, process launch, package installation and repository writes are not granted by default.

### 2.3 Evidence ledger

ExperimentLedger stores bounded records containing a falsifiable hypothesis, method identifier, input fingerprint, JSON-shaped outcome, seed and evidence references. Every entry links to the previous entry's digest. verify() recomputes the whole chain. Raw input payloads are fingerprinted rather than retained.

A valid hash chain proves only that the recorded sequence has not changed relative to its current contents. It does not prove that an experiment was honestly executed, that evidence is true, or that the host and its signing keys are trustworthy.

### 2.4 Change preflight

ChangeProposal describes intended paths, tests, evidence, risk and reversibility. SambuMachine.evaluate_change() returns one of:

- rejected — scope, evidence, test, reversibility or critical-risk constraints failed;
- human_review_required — structurally valid proposal exceeds the autonomous risk ceiling;
- ready_for_tests — the preflight passed and independent tests/review are still required.

No result means approved, merged, deployed or safe. By default, only changes below sambu/, tests/, docs/, examples/ and benchmarks/ enter the autonomous preflight scope. .github/, .git/, secrets, packaging metadata and build configuration are protected.

### Example

~~~python
from sambu import (
    AutonomyPolicy, ChangeProposal, ResourceBudget, RiskTier,
    SambuMachine, TaskManifest,
)

machine = SambuMachine(AutonomyPolicy(
    allowed_capabilities=frozenset({"compute", "ledger.append"}),
    maximum_budget=ResourceBudget(max_steps=20_000),
))

plan = machine.plan(TaskManifest(
    name="voxel.audit",
    purpose="Compare a deterministic voxel benchmark",
    capabilities=("compute", "ledger.append"),
    budget=ResourceBudget(max_steps=50_000),
    seed=41,
))

print(plan.status)              # ready
print(plan.effective_budget)    # max_steps capped at 20_000
print(plan.clipped_limits)      # ('max_steps',)

proposal = ChangeProposal(
    title="Optimize sparse traversal",
    summary="Replace a hot loop after benchmark comparison.",
    changed_paths=("sambu/voxels/grid.py", "tests/test_voxels.py"),
    risk=RiskTier.LOW,
    required_tests=("python -m unittest tests.test_voxels",),
    evidence_refs=("benchmark:baseline-2026-11", "test:voxel-regression"),
    reversible=True,
)
print(machine.evaluate_change(proposal).verdict)  # ready_for_tests
~~~

## 3. Status matrix

| Capability | Status | Evidence / boundary |
|---|---|---|
| Immutable task manifest and explicit capabilities | **Implemented · experimental Python API** | TaskManifest, AutonomyPolicy, tests |
| Component-wise resource capping | **Implemented · experimental Python API** | ResourceBudget.cap_to() |
| Deterministic policy-plan fingerprint | **Implemented · experimental Python API** | SambuMachine.plan() |
| Bounded append-only experiment journal | **Implemented · experimental Python API** | ExperimentLedger |
| Hash-chain integrity verification | **Implemented · experimental Python API** | ExperimentLedger.verify() |
| Reversible/path/evidence/test change preflight | **Implemented · experimental Python API** | SambuMachine.evaluate_change() |
| Actual process/container/VM sandbox | **Planned** | OS executor, syscall policy, filesystem/network tests |
| Automatic experiment execution | **Planned** | Isolated runner, fixed clock/entropy, resource telemetry |
| Automatic code modification or self-hosted recompilation | **Deferred** | Native compiler, ownership model, signed provenance, human release control |
| Automatic merge/deploy | **Intentionally out of scope** | Human/CI governed release pipeline |

## 4. Delivery gates

### Gate A — Policy correctness (this slice)
- positive and negative capability tests;
- budget capping and no-privilege-expansion tests;
- deterministic fingerprints;
- ledger chain verification and finite capacity;
- traversal, protected-path, irreversible, missing-evidence and high-risk rejection tests.

### Gate B — Isolated experiments
- subprocess/container executor with an explicit syscall and resource policy;
- fixed seed, clock and input snapshot;
- bounded CPU, memory, output, process count and wall-clock budget enforced outside the child;
- kill/reap semantics and captured stdout/stderr;
- no network or filesystem access unless explicitly provisioned;
- adversarial escape tests.

### Gate C — Evidence-driven improvement loop
- compare a baseline and at least one alternative;
- run tests and benchmark suites in an isolated workspace;
- preserve artifact hashes, environment fingerprint and command exit status;
- produce a patch proposal and rollback plan;
- require human review for medium/high/critical risk and all protected paths.

### Gate D — Native machine and IDE integration
- expose policy explanations and plan traces in the machine runtime;
- let the IDE display grants, clipped budgets, test evidence and unresolved risks;
- keep editor actions separate from approval authority;
- add language-level task manifests only after a typed/effect-aware semantic IR exists.

## 5. Non-negotiable laws

1. A capability is never inferred from a task's goal or natural-language prompt.
2. A larger budget is never granted merely because previous runs succeeded.
3. Failure is preserved as evidence; it is not relabeled as success.
4. An experiment's hash chain is integrity evidence, not proof of truth.
5. A preflight verdict is not a test result, security certification or release approval.
6. The autonomy core has no method that executes an arbitrary callable or writes repository files.
7. Self-improvement cannot weaken its own policy, erase its audit trail or approve its own release.
8. Native code and hardware access remain explicit, target-specific and independently reviewed.

**Engineering objective:** explore widely, grant narrowly, measure honestly, recover predictably and hand consequential authority to an accountable human.
