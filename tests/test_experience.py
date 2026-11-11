from __future__ import annotations
import unittest
from sambu.experience import ExperienceJournal

class ExperienceJournalTests(unittest.TestCase):
    def test_opt_in_required(self):
        journal=ExperienceJournal()
        self.assertFalse(journal.record("compile","completed",duration_ms=12))
        self.assertEqual(journal.summary().sample_count,0)
    def test_metrics_and_recommendations(self):
        journal=ExperienceJournal(opt_in=True,minimum_sample=3)
        journal.record("parse","completed",duration_ms=10)
        journal.record("build","failed",duration_ms=30,friction_code="missing_toolchain")
        journal.record("build","abandoned",duration_ms=20,friction_code="missing_toolchain")
        report=journal.summary()
        self.assertEqual(report.sample_count,3)
        self.assertAlmostEqual(report.completion_rate,100/3)
        self.assertAlmostEqual(report.failure_rate,100/3)
        self.assertEqual(report.median_duration_ms,20.0)
        self.assertTrue(report.sample_is_actionable)
        self.assertEqual(journal.next_actions(),("missing_toolchain",))
    def test_bounded_buffer(self):
        journal=ExperienceJournal(opt_in=True,capacity=2,minimum_sample=1)
        journal.record("a","completed",duration_ms=1)
        journal.record("b","failed",duration_ms=2)
        journal.record("c","abandoned",duration_ms=3)
        self.assertEqual(journal.summary().sample_count,2)
        self.assertEqual(journal.summary().median_duration_ms,2.5)
    def test_withdrawal_clears(self):
        journal=ExperienceJournal(opt_in=True)
        journal.record("open","failed",friction_code="navigation")
        journal.set_consent(False)
        self.assertEqual(journal.summary().sample_count,0)
        self.assertFalse(journal.record("open","completed"))
    def test_codes_and_durations_validate(self):
        journal=ExperienceJournal(opt_in=True)
        with self.assertRaises(ValueError): journal.record("user@example.com","completed")
        with self.assertRaises(ValueError): journal.record("build","failed",duration_ms=-1)
        with self.assertRaises(ValueError): journal.record("build","failed",friction_code="private note")

if __name__=="__main__": unittest.main()
