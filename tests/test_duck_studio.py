from __future__ import annotations

import unittest

from sambu_studio.duck_gui import (
    Summary,
    file_rows_from_report,
    health_label,
    summary_from_report,
)


class DuckStudioSummaryTests(unittest.TestCase):
    def test_summary_extracts_all_inspection_counts(self):
        payload = {
            "summary": {
                "files_scanned": 5, "preferences": 2, "plugins": 3, "topics": 2,
                "consumers": 2, "exchanges": 1, "bindings": 2, "publishers": 1,
                "errors": 0, "warnings": 1,
            }
        }
        self.assertEqual(
            summary_from_report(payload),
            Summary(5, 2, 3, 2, 2, 1, 2, 1, 0, 1),
        )

    def test_empty_report_counts_remain_zero(self):
        self.assertEqual(
            summary_from_report({"summary": {}}),
            Summary(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        )

    def test_health_prioritises_errors_then_warnings(self):
        self.assertEqual(
            health_label(Summary(0, 0, 0, 0, 0, 0, 0, 0, 1, 3)),
            ("ACTION REQUIRED", "red"),
        )
        self.assertEqual(
            health_label(Summary(0, 0, 0, 0, 0, 0, 0, 0, 0, 2)),
            ("REVIEW SUGGESTED", "amber"),
        )
        self.assertEqual(
            health_label(Summary(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)),
            ("STATIC CHECKS PASSED", "green"),
        )

    def test_file_inventory_surfaces_warning_and_error_status(self):
        report = {
            "files_scanned": [
                "etc/di.xml", "etc/queue_consumer.xml", "etc/queue_topology.xml"
            ],
            "preferences": [{"path": "etc/di.xml"}],
            "consumers": [{"path": "etc/queue_consumer.xml"}],
            "diagnostics": [
                {"path": "etc/queue_consumer.xml", "severity": "warning"},
                {"path": "etc/queue_topology.xml", "severity": "error"},
            ],
        }
        self.assertEqual(
            file_rows_from_report(report),
            [
                ("etc/di.xml", "1", "PASSED"),
                ("etc/queue_consumer.xml", "1", "REVIEW"),
                ("etc/queue_topology.xml", "0", "ERROR"),
            ],
        )

    def test_severity_priority_uses_highest_finding_per_file(self):
        report = {
            "files_scanned": ["etc/di.xml"],
            "diagnostics": [
                {"path": "etc/di.xml", "severity": "warning"},
                {"path": "etc/di.xml", "severity": "error"},
            ],
        }
        self.assertEqual(
            file_rows_from_report(report),
            [("etc/di.xml", "0", "ERROR")],
        )

    def test_missing_supported_files_produces_review_row(self):
        self.assertEqual(
            file_rows_from_report({"files_scanned": []}),
            [("No supported XML files found", "0", "REVIEW")],
        )


if __name__ == "__main__":
    unittest.main()
