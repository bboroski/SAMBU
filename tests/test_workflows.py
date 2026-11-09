from __future__ import annotations

import unittest

from sambu.interpreter import execute


class WorkflowPrimitiveTests(unittest.TestCase):
    def run_sambu(self, source: str):
        output: list[str] = []
        result = execute(source, output=output.append)
        return result, output

    def test_gift_batch_is_atomic_and_updates_preview_balances(self):
        _, output = self.run_sambu("""
let result = gift_batch([
  ["g-1", "Ada", "Bo", 4],
  ["g-2", "Bo", "Cy", 1]
], [["Ada", 10], ["Bo", 2], ["Cy", 0]])
print(result.valid)
print(result.atomic)
print(result.execution)
print(result.total_gifted)
print(result.balances[0].owner)
print(result.balances[0].balance)
""")
        self.assertEqual(output, ["true", "true", "preview_only", "5", "Ada", "6"])

    def test_gift_batch_rejects_insufficient_balance_and_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, "insufficient balance"):
            execute('gift_batch([["g1", "Ada", "Bo", 11]], [["Ada", 10], ["Bo", 0]])')
        with self.assertRaisesRegex(ValueError, "duplicate gift id"):
            execute('gift_batch([["g1", "Ada", "Bo", 1], ["g1", "Bo", "Ada", 1]], [["Ada", 3], ["Bo", 3]])')

    def test_accreditation_status_requires_explicit_verification_and_dates(self):
        _, output = self.run_sambu("""
let cert = accreditation_record("SAMBU", "test-standard", "Issuer", "2026-01-01", "2027-01-01", ["audit-42"], true)
let state = accreditation_status(cert, "2026-11-09")
let expired = accreditation_status(cert, "2027-01-02")
print(state.status)
print(state.active)
print(expired.status)
""")
        self.assertEqual(output, ["active", "true", "expired"])

    def test_unverified_accreditation_does_not_become_active(self):
        _, output = self.run_sambu("""
let cert = accreditation_record("SAMBU", "standard", "Issuer", "2026-01-01", "2027-01-01", ["evidence"], false)
print(accreditation_status(cert, "2026-05-01").status)
""")
        self.assertEqual(output, ["unverified"])

    def test_association_records_evidence_and_does_not_claim_causation(self):
        _, output = self.run_sambu("""
let link = associate("module-a", "module-b", "depends_on", "manifest:line-4", 0.8)
print(link.status)
print(link.causation_claimed)
print(link.confidence)
""")
        self.assertEqual(output, ["unverified", "false", "0.8"])

    def test_signal_reports_remain_unverified_until_human_review(self):
        _, output = self.run_sambu("""
let report = signal_report("scanner", "package-x", "dependency-risk", "Version is outdated", ["lockfile:12"], "medium", 0.9)
print(report.status)
print(report.finding)
print(report.automated_action)
""")
        self.assertEqual(output, ["unverified_requires_review", "null", "none"])

    def test_pitch_score_is_bounded_and_transparent(self):
        _, output = self.run_sambu("""
let pitch = pitch_score(0.9, 0.8, 0.2, 0.1)
print(pitch.score)
print(pitch.decision)
""")
        self.assertEqual(output, ["0.52363636", "human_review_required"])

    def test_blast_plan_is_bounded_and_never_executes(self):
        _, output = self.run_sambu("""
let plan = blast_plan(1000, 100, 3, 4)
print(plan.chunk_count)
print(plan.max_in_flight)
print(plan.estimated_wave_count)
print(plan.requires_idempotency)
print(plan.execution)
""")
        self.assertEqual(output, ["10", "3", "4", "true", "plan_only"])

    def test_blast_plan_rejects_unsafe_limits(self):
        with self.assertRaises(ValueError):
            execute("blast_plan(1000001, 10, 2)")
        with self.assertRaises(ValueError):
            execute("blast_plan(10, 0, 2)")

    def test_parse_report_validates_without_execution(self):
        _, output = self.run_sambu("""
let report = parse_report("let x = 2 + 3")
print(report.valid)
print(report.statement_count)
print(report.execution)
let invalid = parse_report("let x = (2 +")
print(invalid.valid)
print(invalid.error_code)
""")
        self.assertEqual(output, ["true", "1", "not_run", "false", "SAMBU-P001"])

    def test_pattern_mining_finds_repetition_and_rhyme_families(self):
        _, output = self.run_sambu("""
let mined = mine_patterns("ночь точь ночь прочь", 2)
print(mined.word_count)
print(mined.repeated_words[0].pattern)
print(mined.repeated_words[0].frequency)
print(count(mined.rhyme_families))
""")
        self.assertEqual(output, ["4", "ночь", "2", "1"])

    def test_cluster_glue_builds_transitive_clusters(self):
        _, output = self.run_sambu("""
let result = cluster_glue([
  ["A", ["red", "core"]],
  ["B", ["core", "blue"]],
  ["C", ["blue"]],
  ["D", ["isolated"]]
])
print(result.cluster_count)
print(result.item_count)
print(result.clusters[0].size)
print(result.clusters[1].items[0])
""")
        self.assertEqual(output, ["2", "4", "3", "D"])

    def test_empty_cluster_glue_is_valid(self):
        _, output = self.run_sambu("""
let result = cluster_glue([])
print(result.cluster_count)
print(result.item_count)
""")
        self.assertEqual(output, ["0", "0"])


if __name__ == "__main__":
    unittest.main()
