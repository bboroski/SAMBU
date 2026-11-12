# NEURO-CORE — SAMBU integration architecture

**Status:** SPECIFIED. This is an implementation contract, not a claim of completed implementation or qualification.

## Mission
language, compiler and semantic infrastructure. The repository retains its independent release, ownership, dependency and security boundary; cross-repository coordination occurs only through versioned contracts.

## Assigned NEURO-CORE clusters
1. **KERNEL + DELPHI (74)** — privilege boundaries, kernel interfaces, memory/process invariants, deterministic decision services.
2. **LUA + TRICKSTER (74)** — sandboxed scripting, capability policies, synthetic honeypots, adversarial test fixtures.
3. **BRAIN + NEUROBIOLOGY (74)** — validated-event learning, model evaluation, drift detection, explainable recommendations.
4. **SCENARIOS + SCRUPLES (74)** — threat scenarios, ethical constraints, policy proofs, misuse and impact reviews.
5. **DO + WHAT (74)** — action planning, typed workflows, idempotency, rollback and observable execution.
6. **GIRL + FUDGE (74)** — human-centered interaction, safe defaults, accessibility, uncertainty and consent handling.
7. **QUANTUM + HUMAN (74)** — post-quantum cryptographic agility, key lifecycle, human approval for irreversible actions.
8. **FREE + DEAD (74)** — least-privilege extension points, dependency reachability, dead-code removal with proof.
9. **JOY + GYM (74)** — developer feedback, reproducible test labs, fuzzing, fault injection and chaos experiments.

## Delivery state machine
Every item moves monotonically through SPECIFIED → DESIGNED → IMPLEMENTED → TESTED → VERIFIED → INTEGRATED → RELEASED. A state transition requires an evidence record; labels or checklist ticks alone are not evidence.

Minimum evidence per item: stable ID; owner; source commit/PR; acceptance criteria; test command and environment; CI run URL; artifact or log digest; reviewer; rollback note. A failed gate leaves the item in its prior state. RELEASED requires an immutable version/tag and independently successful release workflow.

## Security invariants
- Ring 0 is reserved for minimal platform-specific kernel/driver code. Shared policy, AI, scripting, orchestration and telemetry run unprivileged.
- Lua is an isolated runtime with memory, instruction and wall-clock quotas, capability allowlists, no ambient authority, and a killable host boundary.
- Trickster honeypots are isolated from production identities, networks and user data; use synthetic credentials/data only.
- Neurobiology learning accepts only validated, provenance-bearing, privacy-reviewed events. Training is reproducible, evaluated offline and rollbackable; no online self-modification of privileged policy.
- Quantum means deployable post-quantum cryptography with algorithm agility, key rotation and interoperability tests (e.g. NIST-standardized ML-KEM/ML-DSA where applicable), not quantum-computing claims.
- Human approval is required for destructive, externally visible, privilege-changing or otherwise irreversible actions. Approval is bound to exact action parameters and expires.
- Dead-code removal requires dependency/call-graph evidence, build-matrix checks and tests proving public ABI/API compatibility; preserve an easy revert.
- Gym includes unit/integration tests, fuzzing, sanitizers where supported, fault injection and bounded chaos experiments. Production chaos is opt-in and never targets user data.
- Model or rule outputs are advisory; deterministic policy gates remain authoritative. No self-granted permissions, self-merging, self-signing or self-release.

## Distributed Neuro Bus contract
The bus transports signed, versioned envelopes only; it does not execute remote code. Required fields: schema_version, event_id, producer, component_version, timestamp, event_type, scope, payload_digest, provenance, classification, expiry, signature/key_id. Consumers validate schema, signature, expiry, replay window, producer authorization and payload digest before use. Default-deny unknown event types; bounded queues, backpressure, deduplication and audit logging are mandatory. Sensitive payloads remain local unless an explicit data-sharing policy permits transfer.

## 666 portfolio accounting
The nine clusters contain 74 work items each: 9 × 74 = 666 system-wide. The same canonical item may have repository-specific implementation tasks, but those are child tasks and must not be counted as additional canonical innovations. The 13 repositories are independently qualified; this document does not claim that 666 items are implemented.

## Repository-specific boundary
**SAMBU** — language, compiler and semantic infrastructure.

Host the typed event/rule schema, deterministic policy DSL and Lua sandbox adapter; never embed an unrestricted interpreter in Ring 0.

## Acceptance gates
1. Contract tests verify this repository's public interfaces and forbidden privilege boundaries.
2. Negative tests prove fail-closed behavior for malformed, unsigned, expired, replayed or unauthorized inputs where relevant.
3. Regression and fuzz tests cover parsers, state transitions and resource exhaustion.
4. Integration tests use version-pinned peer contracts and synthetic fixtures.
5. Release evidence includes SPDX SBOM, SHA-256 artifact digests and provenance attestation when supported; attestations must be generated by the CI identity, not fabricated JSON.
6. Hardware-specific claims require target hardware/toolchain evidence; host tests are reported separately.
7. No automatic merge or publication: branch protection, required checks and human review remain authoritative.


**Repository-specific engineering rule:** Require deterministic compilation, resource quotas, signed policy bundles and reproducible compiler tests.
