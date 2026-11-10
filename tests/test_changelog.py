from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"


class ChangelogHistoryTests(unittest.TestCase):
    def test_all_published_release_sections_remain_present_once(self):
        content = CHANGELOG.read_text(encoding="utf-8")
        versions = re.findall(r"^## (0\\.\\d+\\.\\d+) — ", content, flags=re.MULTILINE)
        expected = [f"0.{minor}.0" for minor in range(11, 0, -1)]
        expected[1] = "0.10.0"
        self.assertEqual(versions, expected)
        self.assertIn("## 0.5.1 — 2026-11-09", content)


if __name__ == "__main__":
    unittest.main()
