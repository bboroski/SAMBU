from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    Path(".github/workflows/tests.yml"),
    Path(".github/workflows/native.yml"),
)


class WorkflowPermissionTests(unittest.TestCase):
    def test_ci_workflows_grant_only_read_access_to_repository_contents(self):
        for relative_path in WORKFLOWS:
            with self.subTest(workflow=str(relative_path)):
                lines = (ROOT / relative_path).read_text(encoding="utf-8").splitlines()
                self.assertIn("permissions:", lines)
                permissions_index = lines.index("permissions:")
                self.assertIn("jobs:", lines)
                self.assertLess(permissions_index, lines.index("jobs:"))

                scopes = []
                for line in lines[permissions_index + 1:]:
                    if line and not line[0].isspace():
                        break
                    if line.strip():
                        scopes.append(line)

                self.assertEqual(scopes, ["  contents: read"])


if __name__ == "__main__":
    unittest.main()
