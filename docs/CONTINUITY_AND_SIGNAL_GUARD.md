# Continuity Cycles and Signal Governance

**Status:** implemented as experimental Python-host APIs in SAMBU 0.11.x. These primitives are not language keywords, an autonomous scheduler, a cryptographic implementation or a security sandbox.

This design note translates several systems ideas from a fictional cyclical machine threat into safeguards for ordinary software. It intentionally does not reproduce the source fiction's destructive solution. In SAMBU, continuity means preserving validated state and institutional memory without coercion, hidden control or irreversible destructive actions.

## Design translation

| Source idea | SAMBU engineering interpretation |
|---|---|
| Repeated galactic cycles | Explicit, bounded finite-state workflows with auditable transitions |
| A central relay and control hub | Make central dependencies visible; prefer replaceable interfaces and independent failure domains |
| A dormant vanguard that activates a larger system | Separate observation, preparation and activation; require evidence at each operational boundary |
| Indoctrination through persistent signals | Authenticate issuer provenance, reject replay, bound payloads and quarantine failures |
| A harvested civilization preserved as a machine archive | Preserve a digest of an approved snapshot; keep the payload and retention policy under host/user control |
| Modified thralls and proxy forces | Treat transformed external agents as untrusted; never inherit capabilities merely from their origin or role |
| An assumed organic/synthetic conflict | Do not encode inevitable conflict as a system premise; support cooperation through explicit, inspectable contracts |

The key inversion is deliberate: preservation is not permission to harm, deceive, coerce or silently override an operator. A system may stop, degrade safely, request review or archive a state; it must not claim that destructive action is necessary for continuity.

## 1. CycleController

`CycleController` provides a deterministic lifecycle state machine:

```text
DORMANT
   |
   v
OBSERVING -> PREPARING -> ACTIVE -> RECOVERING -> ARCHIVED
                  ^                    |
                  |____________________|
```

Any non-terminal phase may transition to `HALTED`. `HALTED` is terminal. A new cycle begins only through an explicit `ARCHIVED -> OBSERVING` transition.

Operational and archival transitions require JSON-shaped evidence. Evidence contents are not retained; a SHA-256 digest is attached to the event. Events are linked into a hash chain, and `verify()` recomputes ordering, legal transitions, cycle numbers and digests.

```python
from sambu import CycleController, CyclePhase

cycle = CycleController(max_cycles=3)
cycle.transition(
    CyclePhase.OBSERVING, "new workload received",
    evidence={"ticket": "ops-104"},
)
cycle.transition(
    CyclePhase.PREPARING, "preflight complete",
    evidence={"tests": ["unit", "contract"]},
)
cycle.transition(
    CyclePhase.ACTIVE, "operator-approved activation",
    evidence={"approval_ref": "review-27"},
)
cycle.transition(
    CyclePhase.RECOVERING, "work batch completed",
    evidence={"result": "success"},
)
archive = cycle.transition(
    CyclePhase.ARCHIVED, "snapshot recorded",
    evidence={"state_version": 12, "snapshot_ref": "snapshot-12"},
)
assert cycle.verify()
print(archive.evidence_digest)
```

The controller validates lifecycle metadata only. The host application owns execution, snapshot storage, retention, access control and operator approval. The digest is not a backup and cannot reconstruct the archived payload.

## 2. SignalEnvelope and SignalGuard

`SignalEnvelope` binds an issuer, strictly positive sequence number, canonical JSON payload, SHA-256 payload digest and optional signature. Its `payload` property returns a fresh decoded copy.

`SignalGuard` applies, in order:

1. bounded canonical JSON validation;
2. issuer allow-list check;
3. strictly increasing per-issuer sequence check;
4. signature verification through a supplied host callback;
5. acceptance or quarantine with a reason code.

Authentication is required by default. Without a verifier, a signed message is not accepted. In the explicitly weaker `require_authentication=False` mode, an unsigned message from an allow-listed issuer can be admitted, but the decision is marked `authenticated=False`. The sequence cursor advances only after acceptance. Decision history and cursors are bounded and held in memory.

```python
from sambu import SignalEnvelope, SignalGuard

# Demonstration only. Replace this callback with a reviewed signature
# provider that validates the actual signing scheme and key lifecycle.
def demo_verifier(issuer, sequence, payload_digest, signature):
    return signature == "demo-valid"

guard = SignalGuard(
    ("relay.alpha",),
    signature_verifier=demo_verifier,
)
envelope = SignalEnvelope.create(
    "relay.alpha", 1, {"intent": "measure", "sample": 17},
    signature="demo-valid",
)
decision = guard.accept(envelope)
assert decision.accepted and decision.authenticated
```

**Security boundary:** SAMBU does not implement public-key cryptography here. The callback must use a vetted cryptographic library or external trust provider, validate the signing key and bind the signature to the issuer, sequence and payload digest. A boolean callback is only as trustworthy as its implementation. The guard does not persist replay cursors; a host that needs replay protection across restarts must persist and restore trusted cursor state through its own protected storage.

## 3. Limits and non-goals

- No signal payload is executed, interpreted as a command or granted a capability.
- An allow-list identifies permitted issuers; it does not prove that an issuer is uncompromised.
- Hashes provide integrity fingerprints, not confidentiality, authenticity or durable storage.
- The in-memory event and decision histories are finite; capacity exhaustion raises an explicit error.
- Cycle events are hash-chained but not digitally signed or tamper-proof against a process owner who can rewrite memory.
- The controller does not provide distributed consensus, leader election, exactly-once delivery, a scheduler or cross-process coordination.
- A single central controller remains a possible availability bottleneck; deployment topology must be assessed separately.
- The module is a Python host API. It does not add new SAMBU grammar or built-ins.

## 4. Verification

Run:

```bash
python -m unittest tests.test_continuity -v
```

The tests cover legal and illegal lifecycle transitions, missing evidence, event and cycle ceilings, hash-chain tampering, issuer denial, missing/invalid signatures, verifier failure, replay rejection, defensive payload copies and bounded decision history.
