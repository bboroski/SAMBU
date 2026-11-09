from __future__ import annotations

import json
import unittest
from dataclasses import replace

from sambu.autonomy import (
    AutonomyPolicy,
    CapabilityDenied,
    ChangeProposal,
    ExperimentLedger,
    LedgerFull,
    ResourceBudget,
    RiskTier,
    SambuMachine,
    TaskManifest,
    fingerprint,
)


class ResourceBudgetTests(unittest.TestCase):
    def test_budget_is_componentwise_capped_and_reports_each_clipped_limit(self):
        requested = ResourceBudget(
            max_steps=50_000,
            max_messages=50,
            max_payload_bytes=900_000,
            max_retries=3,
        )
        maximum = ResourceBudget(
            max_steps=10_000,
            max_messages=100,
            max_payload_bytes=262_144,
            max_retries=1,
        )

        effective, clipped = requested.cap_to(maximum)

        self.assertEqual(effective, ResourceBudget(
            max_steps=10_000,
            max_messages=50,
            max_payload_bytes=262_144,
            max_retries=1,
        ))
        self.assertEqual(
            clipped, ("max_steps", "max_payload_bytes", "max_retries")
        )

    def test_boolean_values_are_not_accepted_as_integer_budgets(self):
        with self.assertRaises(ValueError):
            ResourceBudget(max_steps=True)


class SambuMachineTests(unittest.TestCase):
    def test_task_plan_grants_only_allowed_capabilities_and_caps_budget(self):
        policy = AutonomyPolicy(
            allowed_capabilities=frozenset({"compute", "ledger.append"}),
            maximum_budget=ResourceBudget(max_steps=100, max_messages=10),
        )
        machine = SambuMachine(policy)
        manifest = TaskManifest(
            "voxel.scan",
            "Inspect a bounded voxel batch",
            ("ledger.append", "compute"),
            ResourceBudget(max_steps=500, max_messages=5),
        )

        plan = machine.plan(manifest)

        self.assertTrue(plan.admitted)
        self.assertEqual(plan.granted_capabilities, ("compute", "ledger.append"))
        self.assertEqual(plan.effective_budget.max_steps, 100)
        self.assertEqual(plan.effective_budget.max_messages, 5)
        self.assertEqual(plan.clipped_limits, ("max_steps",))
        self.assertEqual(len(plan.digest), 64)

    def test_policy_can_deny_every_capability_and_change_root(self):
        policy = AutonomyPolicy(
            allowed_capabilities=frozenset(),
            allowed_change_roots=(),
        )
        machine = SambuMachine(policy)
        with self.assertRaises(CapabilityDenied):
            machine.plan(TaskManifest("no.cap", "No permissions", ("compute",)))
        result = machine.evaluate_change(ChangeProposal(
            title="Blocked path",
            summary="No repository path is allowed.",
            changed_paths=("sambu/new.py",),
            required_tests=("python -m unittest",),
            evidence_refs=("evidence:no-op",),
        ))
        self.assertEqual(result.verdict, "rejected")

    def test_unknown_or_unapproved_capability_is_denied(self):
        machine = SambuMachine()
        manifest = TaskManifest(
            "fetch.remote",
            "Fetch a remote dependency",
            ("network.connect",),
        )
        with self.assertRaises(CapabilityDenied):
            machine.plan(manifest)

    def test_risk_above_ceiling_requires_review_and_grants_nothing(self):
        machine = SambuMachine()
        plan = machine.plan(TaskManifest(
            "release.publish",
            "Publish a release candidate",
            ("compute",),
            risk=RiskTier.HIGH,
        ))
        self.assertEqual(plan.status, "human_review_required")
        self.assertEqual(plan.granted_capabilities, ())
        self.assertFalse(plan.admitted)

    def test_plan_is_deterministic_for_equivalent_capability_order(self):
        machine = SambuMachine()
        first = machine.plan(TaskManifest(
            "test.run", "Run deterministic checks", ("compute", "ledger.read"), seed=17
        ))
        second = machine.plan(TaskManifest(
            "test.run", "Run deterministic checks", ("ledger.read", "compute"), seed=17
        ))
        changed_seed = machine.plan(TaskManifest(
            "test.run", "Run deterministic checks", ("compute", "ledger.read"), seed=18
        ))
        self.assertEqual(first.digest, second.digest)
        self.assertNotEqual(first.digest, changed_seed.digest)

    def test_manifest_rejects_invalid_seed_values(self):
        with self.assertRaises(ValueError):
            TaskManifest("seed.bad", "Invalid seed", ("compute",), seed=True)
        with self.assertRaises(ValueError):
            TaskManifest("seed.bad", "Invalid seed", ("compute",), seed=2 ** 80)

    def test_audit_reports_that_execution_and_self_modification_are_disabled(self):
        audit = SambuMachine().audit()
        self.assertTrue(audit["ledger_valid"])
        self.assertFalse(audit["execution_enabled"])
        self.assertFalse(audit["self_modification_enabled"])
        self.assertFalse(audit["merge_enabled"])


class ExperimentLedgerTests(unittest.TestCase):
    def test_machine_records_reproducible_hash_chained_evidence(self):
        machine = SambuMachine()
        first = machine.record_experiment(
            "bounded scheduler preserves FIFO order",
            "fifo-regression",
            {"tasks": ["a", "b"]},
            {"order": ["a", "b"], "passed": True},
            ("tests/test_concurrency.py::test_fifo",),
            seed=17,
        )
        second = machine.record_experiment(
            "bounded scheduler preserves FIFO order",
            "fifo-regression",
            {"tasks": ["a", "b"]},
            {"order": ["a", "b"], "passed": True},
            ("tests/test_concurrency.py::test_fifo",),
            seed=17,
        )

        independent = ExperimentLedger()
        same_first = independent.record(
            "bounded scheduler preserves FIFO order",
            "fifo-regression",
            fingerprint({"tasks": ["a", "b"]}),
            {"order": ["a", "b"], "passed": True},
            ("tests/test_concurrency.py::test_fifo",),
            seed=17,
        )

        self.assertEqual(first.digest, same_first.digest)
        self.assertNotEqual(first.digest, second.digest)
        self.assertEqual(second.sequence, 2)
        self.assertEqual(second.previous_digest, first.digest)
        self.assertTrue(machine.ledger.verify())
        self.assertEqual(machine.ledger.find_by_input(first.input_digest), (first, second))
        exported = json.loads(machine.ledger.export_json())
        self.assertEqual(exported["format"], "sambu.experiment-ledger/v1")
        self.assertEqual(len(exported["records"]), 2)
        tampered = replace(first, outcome_json='{"order":["b","a"],"passed":true}')
        machine.ledger._records[0] = tampered
        self.assertFalse(machine.ledger.verify())
        machine.ledger._records[0] = first
        self.assertTrue(machine.ledger.verify())
        copy = first.outcome
        copy["passed"] = False
        self.assertTrue(first.outcome["passed"])

    def test_ledger_rejects_non_json_or_non_finite_observations(self):
        ledger = ExperimentLedger()
        with self.assertRaises(TypeError):
            ledger.record("h", "m", fingerprint({}), {"value": float("nan")}, ("test",))
        with self.assertRaises(TypeError):
            ledger.record("h", "m", fingerprint({}), {"resource": object()}, ("test",))

    def test_ledger_requires_a_digest_and_evidence_reference(self):
        ledger = ExperimentLedger()
        with self.assertRaises(ValueError):
            ledger.record("h", "m", "not-a-digest", {}, ("test",))
        with self.assertRaises(ValueError):
            ledger.record("h", "m", fingerprint({}), {}, ())

    def test_ledger_capacity_is_finite(self):
        ledger = ExperimentLedger(max_records=1)
        ledger.record("first", "unit-test", fingerprint(1), {"ok": True}, ("test:first",))
        with self.assertRaises(LedgerFull):
            ledger.record("second", "unit-test", fingerprint(2), {"ok": True}, ("test:second",))


class ChangeGateTests(unittest.TestCase):
    def setUp(self):
        self.machine = SambuMachine()

    def proposal(self, **overrides):
        values = {
            "title": "Improve parser diagnostics",
            "summary": "Attach a stable source range to a parser error.",
            "changed_paths": ("sambu/parser.py", "tests/test_parser.py"),
            "risk": RiskTier.LOW,
            "required_tests": ("python -m unittest tests.test_parser",),
            "evidence_refs": ("baseline:parser-tests",),
            "reversible": True,
        }
        values.update(overrides)
        return ChangeProposal(**values)

    def test_low_risk_reversible_change_passes_preflight_not_merge(self):
        result = self.machine.evaluate_change(self.proposal())
        self.assertEqual(result.verdict, "ready_for_tests")
        self.assertTrue(result.may_enter_review)
        self.assertIn("still required", result.reasons[0])

    def test_medium_risk_change_requires_human_review(self):
        result = self.machine.evaluate_change(self.proposal(risk=RiskTier.MEDIUM))
        self.assertEqual(result.verdict, "human_review_required")

    def test_critical_risk_is_rejected_from_autonomous_lane(self):
        result = self.machine.evaluate_change(self.proposal(risk=RiskTier.CRITICAL))
        self.assertEqual(result.verdict, "rejected")
        self.assertTrue(any("critical-risk" in reason for reason in result.reasons))

    def test_path_traversal_and_protected_configuration_are_rejected(self):
        traversal = self.machine.evaluate_change(self.proposal(
            changed_paths=("../.github/workflows/tests.yml",)
        ))
        protected = self.machine.evaluate_change(self.proposal(
            changed_paths=("pyproject.toml",)
        ))
        self.assertEqual(traversal.verdict, "rejected")
        self.assertEqual(protected.verdict, "rejected")

    def test_irreversible_or_unsubstantiated_changes_are_rejected(self):
        irreversible = self.machine.evaluate_change(self.proposal(reversible=False))
        no_tests = self.machine.evaluate_change(self.proposal(required_tests=()))
        no_evidence = self.machine.evaluate_change(self.proposal(evidence_refs=()))
        self.assertEqual(irreversible.verdict, "rejected")
        self.assertEqual(no_tests.verdict, "rejected")
        self.assertEqual(no_evidence.verdict, "rejected")


if __name__ == "__main__":
    unittest.main()
