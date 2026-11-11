from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sambu.satan import (
    ChangePipeline, ChangeProposal, DependencyGraph, MeshError, Nexus,
    PipelineDecision, PythonContractIndex, create_envelope, forward_envelope,
    verify_envelope,
)


KEY_A = b"a" * 32
KEY_B = b"b" * 32
SECRETS = {"repo-a": KEY_A, "repo-b": KEY_B}


class MeshTests(unittest.TestCase):
    def test_origin_signature_and_relay_chain_verify(self):
        event = create_envelope(
            event_id="evt-1", kind="security.finding", origin="repo-a",
            payload={"fingerprint": "abc"}, secret=KEY_A, now=100,
        )
        self.assertTrue(verify_envelope(event, node_secrets=SECRETS, now=101))
        relayed = forward_envelope(event, relay="repo-b", secret=KEY_B)
        self.assertTrue(verify_envelope(relayed, node_secrets=SECRETS, now=101))
        self.assertEqual(relayed.hop_count, 1)
        self.assertEqual(relayed.previous_digest, event.digest())

    def test_tampering_expiry_and_unknown_kinds_are_rejected(self):
        event = create_envelope(
            event_id="evt-2", kind="security.finding", origin="repo-a",
            payload={"severity": "high"}, secret=KEY_A, now=100, ttl_seconds=10,
        )
        tampered = type(event)(**{**event.to_dict(), "payload": {"severity": "critical"}})
        with self.assertRaises(MeshError):
            verify_envelope(tampered, node_secrets=SECRETS, now=101)
        with self.assertRaises(MeshError):
            verify_envelope(event, node_secrets=SECRETS, now=111)
        with self.assertRaises(MeshError):
            create_envelope(event_id="evt-x", kind="arbitrary", origin="repo-a",
                            payload={}, secret=KEY_A, now=100)


class NexusTests(unittest.TestCase):
    def test_event_ingestion_is_idempotent_and_collision_safe(self):
        event = create_envelope(
            event_id="evt-3", kind="repository.registered", origin="repo-a",
            payload={"name": "repo-a"}, secret=KEY_A, now=100,
        )
        with Nexus() as nexus:
            self.assertTrue(nexus.ingest(event, node_secrets=SECRETS, now=101))
            self.assertFalse(nexus.ingest(event, node_secrets=SECRETS, now=101))
            nexus.register_repository("repo-a", metadata={"team": "core"}, now=100)
            self.assertEqual(nexus.repositories()[0]["repo_id"], "repo-a")

    def test_threat_memory_counts_repeated_observations(self):
        with Nexus() as nexus:
            nexus.remember_threat(fingerprint="a" * 64, category="dependency",
                                  severity="high", evidence={"cve": "CVE-X"}, now=1)
            nexus.remember_threat(fingerprint="a" * 64, category="dependency",
                                  severity="high", evidence={"cve": "CVE-X"}, now=2)
            self.assertEqual(nexus.find_threat("a" * 64)["occurrences"], 2)


class DependencyTests(unittest.TestCase):
    def test_ast_index_and_transitive_impact(self):
        index = PythonContractIndex()
        provider = index.parse("core.auth", "def authenticate(token):\n    return True\n")
        consumer = index.parse("api.routes", "from core.auth import authenticate\n")
        graph = DependencyGraph()
        graph.index_python(provider)
        graph.index_python(consumer)
        self.assertEqual(graph.affected("core.auth"), ("api.routes", "core.auth"))
        changed = graph.changed_contract("core.auth", "def validate(token):\n    return False\n")
        self.assertEqual(changed["removed"], ("authenticate",))
        self.assertTrue(changed["review_required"])


class PipelineTests(unittest.TestCase):
    def proposal(self, risk="low", paths=("src/app.py",)):
        return ChangeProposal("Improve parser", "Bounded parser change", paths,
                              ("python -m unittest",), ("issue:12",), risk)

    def test_failed_gates_stop_pipeline(self):
        pipeline = ChangePipeline()
        self.assertEqual(pipeline.evaluate(self.proposal(), tests_passed=False,
                         security_passed=True).decision, PipelineDecision.NEEDS_TESTS)
        self.assertEqual(pipeline.evaluate(self.proposal(), tests_passed=True,
                         security_passed=False).decision, PipelineDecision.NEEDS_SECURITY_REVIEW)

    def test_high_risk_requires_explicit_approval(self):
        pipeline = ChangePipeline()
        result = pipeline.evaluate(self.proposal("high"), tests_passed=True,
                                   security_passed=True)
        self.assertEqual(result.decision, PipelineDecision.NEEDS_HUMAN_APPROVAL)
        approved = pipeline.evaluate(self.proposal("high"), tests_passed=True,
                                     security_passed=True, human_approved=True)
        self.assertEqual(approved.decision, PipelineDecision.READY_FOR_PULL_REQUEST)

    def test_protected_paths_require_approval(self):
        pipeline = ChangePipeline()
        result = pipeline.evaluate(self.proposal(paths=(".github/workflows/ci.yml",)),
                                   tests_passed=True, security_passed=True)
        self.assertEqual(result.decision, PipelineDecision.NEEDS_HUMAN_APPROVAL)


if __name__ == "__main__":
    unittest.main()
