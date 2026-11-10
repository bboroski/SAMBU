from __future__ import annotations

import unittest
from dataclasses import replace

from sambu.continuity import (
    CycleCapacityError,
    CycleController,
    CyclePhase,
    SignalCapacityError,
    SignalDisposition,
    SignalEnvelope,
    SignalGuard,
    TransitionDenied,
)


class CycleControllerTests(unittest.TestCase):
    def test_cycle_requires_evidence_and_records_a_verifiable_lifecycle(self):
        controller = CycleController(max_cycles=2)
        with self.assertRaises(TransitionDenied):
            controller.transition(CyclePhase.OBSERVING, "start without a mission")
        controller.transition(CyclePhase.OBSERVING, "begin observation", evidence={"goal": "inspect"})
        controller.transition(CyclePhase.PREPARING, "plan checked", evidence={"checks": 4})
        controller.transition(CyclePhase.ACTIVE, "authorized activation", evidence={"approval": "review-1"})
        controller.transition(CyclePhase.RECOVERING, "work completed", evidence={"result": "ok"})
        archived = controller.transition(CyclePhase.ARCHIVED, "snapshot committed", evidence={"state": [1, 2, 3]})
        self.assertEqual(controller.phase, CyclePhase.ARCHIVED)
        self.assertEqual(controller.archive_digest, archived.evidence_digest)
        self.assertEqual(len(archived.evidence_digest), 64)
        self.assertTrue(controller.verify())

    def test_illegal_transition_does_not_change_state(self):
        controller = CycleController()
        with self.assertRaises(TransitionDenied):
            controller.transition(CyclePhase.ACTIVE, "skip preparation", evidence={"ok": True})
        self.assertEqual(controller.phase, CyclePhase.DORMANT)
        self.assertEqual(controller.events, ())

    def test_cycle_count_is_bounded_and_halt_is_terminal(self):
        controller = CycleController(max_cycles=1)
        for phase, evidence in (
            (CyclePhase.OBSERVING, {"goal": 1}),
            (CyclePhase.PREPARING, {"plan": 1}),
            (CyclePhase.ACTIVE, {"approval": 1}),
            (CyclePhase.RECOVERING, {"result": 1}),
            (CyclePhase.ARCHIVED, {"snapshot": 1}),
        ):
            controller.transition(phase, "advance", evidence=evidence)
        with self.assertRaises(CycleCapacityError):
            controller.transition(CyclePhase.OBSERVING, "start another", evidence={"goal": 2})
        controller.transition(CyclePhase.HALTED, "operator stopped")
        with self.assertRaises(TransitionDenied):
            controller.transition(CyclePhase.OBSERVING, "restart", evidence={"goal": 3})
        self.assertTrue(controller.verify())

    def test_event_capacity_is_bounded(self):
        controller = CycleController(max_events=1)
        controller.transition(CyclePhase.OBSERVING, "start", evidence={"goal": 1})
        with self.assertRaises(CycleCapacityError):
            controller.transition(CyclePhase.PREPARING, "prepare", evidence={"plan": 1})

    def test_event_chain_detects_tampering(self):
        controller = CycleController()
        event = controller.transition(CyclePhase.OBSERVING, "start", evidence={"goal": 1})
        self.assertTrue(controller.verify())
        controller._events[0] = replace(event, reason="rewritten")
        self.assertFalse(controller.verify())


class SignalGuardTests(unittest.TestCase):
    def setUp(self):
        self.guard = SignalGuard(
            ("relay.alpha",),
            signature_verifier=lambda issuer, sequence, digest, signature: signature == "valid",
        )

    def envelope(self, sequence=1, *, issuer="relay.alpha", signature="valid", payload=None):
        return SignalEnvelope.create(
            issuer, sequence, {"command": "observe"} if payload is None else payload,
            signature=signature,
        )

    def test_signed_allowlisted_signal_is_accepted_and_sequence_committed(self):
        result = self.guard.accept(self.envelope())
        self.assertEqual(result.disposition, SignalDisposition.ACCEPTED)
        self.assertTrue(result.authenticated)
        self.assertEqual(self.guard.sequence_cursors, {"relay.alpha": 1})

    def test_unknown_issuer_and_replayed_sequence_are_quarantined(self):
        unknown = self.guard.accept(self.envelope(issuer="relay.unknown"))
        accepted = self.guard.accept(self.envelope(sequence=4))
        replay = self.guard.accept(self.envelope(sequence=4))
        self.assertEqual(unknown.reason, "issuer_not_allowed")
        self.assertTrue(accepted.accepted)
        self.assertEqual(replay.reason, "replay_or_out_of_order")
        self.assertEqual(self.guard.sequence_cursors["relay.alpha"], 4)

    def test_missing_or_invalid_signature_fails_closed(self):
        missing = self.guard.accept(self.envelope(signature=None))
        invalid = self.guard.accept(self.envelope(sequence=2, signature="bad"))
        self.assertEqual(missing.reason, "signature_required")
        self.assertEqual(invalid.reason, "signature_invalid")
        self.assertEqual(self.guard.sequence_cursors, {})

    def test_verifier_failure_is_quarantined(self):
        guard = SignalGuard(("relay.alpha",), signature_verifier=lambda *args: 1 / 0)
        result = guard.accept(self.envelope())
        self.assertEqual(result.reason, "signature_verifier_error")
        self.assertEqual(guard.sequence_cursors, {})

    def test_truthy_non_boolean_verifier_result_is_not_authentication(self):
        guard = SignalGuard(("relay.alpha",), signature_verifier=lambda *args: "yes")
        result = guard.accept(self.envelope())
        self.assertEqual(result.reason, "signature_invalid")
        self.assertFalse(result.authenticated)
        self.assertEqual(guard.sequence_cursors, {})

    def test_reentrant_verifier_cannot_commit_the_same_sequence_twice(self):
        nested_results = []
        nested_once = False
        guard = None

        def verifier(issuer, sequence, digest, signature):
            nonlocal nested_once
            if not nested_once:
                nested_once = True
                nested_results.append(guard.accept(self.envelope(sequence=sequence)))
            return True

        guard = SignalGuard(("relay.alpha",), signature_verifier=verifier)
        outer = guard.accept(self.envelope(sequence=1))
        self.assertTrue(nested_results[0].accepted)
        self.assertEqual(outer.reason, "replay_or_out_of_order")
        self.assertEqual(sum(item.accepted for item in guard.decisions), 1)
        self.assertEqual(guard.sequence_cursors["relay.alpha"], 1)

    def test_non_authenticating_mode_is_explicit_and_marks_signal_unauthenticated(self):
        guard = SignalGuard(("relay.alpha",), require_authentication=False)
        result = guard.accept(self.envelope(signature=None))
        self.assertTrue(result.accepted)
        self.assertFalse(result.authenticated)

    def test_payload_property_is_a_defensive_copy(self):
        envelope = self.envelope()
        payload = envelope.payload
        payload["command"] = "overwrite"
        self.assertEqual(envelope.payload["command"], "observe")

    def test_payload_size_and_history_are_bounded(self):
        guard = SignalGuard(
            ("relay.alpha",),
            signature_verifier=lambda *args: True,
            max_payload_bytes=20,
            max_decisions=2,
        )
        too_large = guard.accept(self.envelope(payload={"data": "x" * 100}))
        self.assertEqual(too_large.reason, "payload_invalid_or_too_large")
        accepted = guard.accept(self.envelope(sequence=1, payload={"ok": True}))
        self.assertTrue(accepted.accepted)
        with self.assertRaises(SignalCapacityError):
            guard.accept(self.envelope(sequence=2))


if __name__ == "__main__":
    unittest.main()
