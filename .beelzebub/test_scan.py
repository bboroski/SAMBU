#!/usr/bin/env python3
"""Regression tests for Beelzebub's redacted diagnostics."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCANNER = Path(__file__).with_name("scan.py").resolve()


class RedactionTests(unittest.TestCase):
    def test_secret_value_never_appears_in_scan_output(self):
        token = "ghp_" + "A" * 36
        with tempfile.TemporaryDirectory(prefix="beelzebub-redaction-") as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            (root / "credential.txt").write_text(token + "\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCANNER), "--root", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            output = result.stdout + result.stderr
            self.assertEqual(result.returncode, 1)
            self.assertNotIn(token, output)
            self.assertIn("[BBZ-CREDENTIAL]", output)
            self.assertIn("credential.txt", output)
            self.assertIn("line=1", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
