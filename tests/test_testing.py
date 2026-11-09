from __future__ import annotations
import unittest
from sambu.testing import AutotestReport, TestFailure, TestRunSnapshot, autopsy

class AutotestAutopsyTests(unittest.TestCase):
    def test_failure_categories_and_flaky_detection_summary(self):
        report=AutotestReport(
            runs=(TestRunSnapshot(1,3,2,1,0,0,0,""),TestRunSnapshot(2,3,3,0,0,0,0,"")),
            failures=(TestFailure(1,"tests.test_demo.Demo.test_value","assertion","AssertionError: expected 2","AssertionError: expected 2"),),
            flaky_tests=("tests.test_demo.Demo.test_value",),
        )
        result=autopsy(report)
        self.assertEqual(result["status"],"passed")
        self.assertEqual(result["failure_categories"]["assertion"],1)
        self.assertIn("tests.test_demo.Demo.test_value",result["flaky_tests"])
    def test_empty_run_is_not_a_pass(self):
        report=AutotestReport((TestRunSnapshot(1,0,0,0,0,0,0,""),),(),())
        self.assertFalse(report.all_passed)

if __name__ == "__main__": unittest.main()
