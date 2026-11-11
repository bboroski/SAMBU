#!/usr/bin/env python3
"""Regression tests for the Beelzebub repository scanner (stdlib only)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCANNER = Path(__file__).with_name("scan.py").resolve()


class ScannerTests(unittest.TestCase):
    def run_scan(self, files: dict[str, str], fail_on: str = "never"):
        with tempfile.TemporaryDirectory(prefix="beelzebub-test-") as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            for name, content in files.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            report = Path(directory) / "report.json"
            result = subprocess.run(
                [sys.executable, str(SCANNER), "--root", str(root),
                 "--report", str(report), "--fail-on", fail_on],
                text=True, capture_output=True, check=False,
            )
            payload = json.loads(report.read_text(encoding="utf-8"))
            return result, payload

    def test_clean_repository_passes(self):
        result, report = self.run_scan({"src/app.py": "print('hello')\n"})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["summary"]["findings"], 0)

    def test_private_key_is_critical_and_redacted(self):
        result, report = self.run_scan(
            {"config/key.txt": "-----BEGIN RSA PRIVATE KEY-----\n"},
            fail_on="critical",
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["summary"]["by_severity"]["critical"], 1)
        self.assertNotIn("PRIVATE KEY-----", json.dumps(report))

    def test_aws_access_key_is_detected(self):
        result, report = self.run_scan(
            {"config/cloud.env": "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\n"},
            fail_on="critical",
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["findings"][0]["rule_id"], "aws_access_key")

    def test_github_token_is_detected_without_value_disclosure(self):
        token = "ghp_" + "A" * 36
        result, report = self.run_scan(
            {"config/token.txt": token + "\n"}, fail_on="critical"
        )
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(token, json.dumps(report))

    def test_dependency_manifest_is_inventoried(self):
        result, report = self.run_scan({"requirements.txt": "requests==2.32.0\n"})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["summary"]["dependency_manifests"], 1)
        self.assertEqual(report["dependency_inventory"][0]["path"], "requirements.txt")


if __name__ == "__main__":
    unittest.main(verbosity=2)
