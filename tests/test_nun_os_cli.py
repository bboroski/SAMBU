from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import unittest

from sambu.cli import _os

FIXTURE = Path(__file__).parent / "fixtures" / "nun-os-profile.json"


class NUNOSCommandTests(unittest.TestCase):
    def test_profile_check_json(self):
        output = io.StringIO()
        with redirect_stdout(output):
            code = _os(["profile", "check", str(FIXTURE), "--json"])
        self.assertEqual(code, 0)
        self.assertIn('"profile_id": "nun-test-profile"', output.getvalue())
        self.assertIn('"services.dependency-graph"', output.getvalue())

    def test_required_planned_feature_fails_closed(self):
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = _os(["profile", "check", str(FIXTURE), "--require", "scheduler.preemptive"])
        self.assertEqual(code, 1)
        self.assertIn("rejected", errors.getvalue())

    def test_partial_requires_explicit_flag(self):
        fixture = FIXTURE.read_text(encoding="utf-8").replace('"status": "implemented"', '"status": "partial"', 1)
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            path = Path(directory) / "partial.json"
            path.write_text(fixture, encoding="utf-8")
            with redirect_stderr(io.StringIO()):
                self.assertEqual(_os(["profile", "check", str(path), "--require", "services.dependency-graph"]), 1)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(_os(["profile", "check", str(path), "--require", "services.dependency-graph", "--allow-partial"]), 0)


if __name__ == "__main__":
    unittest.main()
