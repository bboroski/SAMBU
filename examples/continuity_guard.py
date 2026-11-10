"""Demonstration of SAMBU's continuity and signal-governance host APIs.

The verifier below is deliberately a stub for documentation/tests. It is not
cryptographic authentication and must not be used in production.
"""
from sambu import (
    CycleController,
    CyclePhase,
    SignalEnvelope,
    SignalGuard,
)


cycle = CycleController(max_cycles=2)
cycle.transition(
    CyclePhase.OBSERVING, "inspect incoming workload",
    evidence={"workload": "example-01"},
)
cycle.transition(
    CyclePhase.PREPARING, "validate the proposed plan",
    evidence={"checks_passed": 3},
)
cycle.transition(
    CyclePhase.ACTIVE, "activate reviewed work",
    evidence={"review_ref": "demo-review"},
)
cycle.transition(
    CyclePhase.RECOVERING, "record completion",
    evidence={"outcome": "ok"},
)
cycle.transition(
    CyclePhase.ARCHIVED, "archive state fingerprint",
    evidence={"version": 1, "state": "complete"},
)
print("cycle chain valid:", cycle.verify())

guard = SignalGuard(
    ("relay.alpha",),
    signature_verifier=lambda issuer, sequence, digest, signature: (
        signature == "demo-valid"
    ),
)
signal = SignalEnvelope.create(
    "relay.alpha", 1, {"kind": "telemetry", "value": 42},
    signature="demo-valid",
)
decision = guard.accept(signal)
print("signal:", decision.disposition.value, decision.reason)
