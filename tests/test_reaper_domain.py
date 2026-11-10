import unittest

from sambu.reaper_domain import (
    CycleState, DomainStatus, MetricLimit, MetricObservation,
    advance_cycle, assess_metric, decide_consensus, evaluate_evolution_gate,
)


class DomainCapabilityTests(unittest.TestCase):
    def test_metric_nominal_and_warning(self):
        limits = MetricLimit("ms", 0.0, 100.0, 5.0)
        nominal = assess_metric(MetricObservation("latency", 50.0, "ms", "test"), limits)
        warning = assess_metric(MetricObservation("latency", 98.0, "ms", "test"), limits)
        self.assertEqual(nominal.status, DomainStatus.NOMINAL)
        self.assertEqual(warning.status, DomainStatus.WARNING)

    def test_metric_outside_envelope_is_critical(self):
        result = assess_metric(
            MetricObservation("temperature", 101.0, "C", "sensor", 4),
            MetricLimit("C", 0.0, 100.0),
        )
        self.assertEqual(result.status, DomainStatus.CRITICAL)

    def test_metric_requires_calibration_and_samples(self):
        result = assess_metric(
            MetricObservation("voltage", 12.0, "V", "sensor", 1, False),
            MetricLimit("V", 10.0, 14.0),
            minimum_samples=3,
        )
        self.assertEqual(result.status, DomainStatus.INCOMPLETE)
        self.assertIsNone(result.value)

    def test_metric_unit_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            assess_metric(
                MetricObservation("distance", 1.0, "km", "sensor"),
                MetricLimit("m", 0.0, 10.0),
            )

    def test_lifecycle_transition_and_rejection(self):
        self.assertEqual(advance_cycle(CycleState.DORMANT, CycleState.STAGED), CycleState.STAGED)
        with self.assertRaises(ValueError):
            advance_cycle(CycleState.DORMANT, CycleState.ACTIVE)

    def test_consensus_counts_distinct_nodes(self):
        result = decide_consensus(
            [("n1", "p1"), ("n2", "p1"), ("n3", "p2")], quorum=2
        )
        self.assertTrue(result.accepted)
        self.assertEqual(result.proposal_id, "p1")
        with self.assertRaises(ValueError):
            decide_consensus([("n1", "p1"), ("n1", "p1")], quorum=2)

    def test_consensus_without_quorum_is_inconclusive(self):
        result = decide_consensus(
            [("n1", "p1"), ("n2", "p2"), ("n3", "p3")], quorum=2
        )
        self.assertFalse(result.accepted)
        self.assertIsNone(result.proposal_id)

    def test_evolution_requires_evidence_and_rollback(self):
        blocked = evaluate_evolution_gate(["tests", "provenance"], ["tests"], rollback_ready=True)
        self.assertFalse(blocked.accepted)
        self.assertEqual(blocked.missing_evidence, ("provenance",))
        accepted = evaluate_evolution_gate(["tests"], ["tests"], rollback_ready=True)
        self.assertTrue(accepted.accepted)

    def test_evolution_rejects_missing_rollback(self):
        result = evaluate_evolution_gate(["tests"], ["tests"], rollback_ready=False)
        self.assertFalse(result.accepted)


if __name__ == "__main__":
    unittest.main()
