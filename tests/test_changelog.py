from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"


class ChangelogHistoryTests(unittest.TestCase):
    def test_all_published_release_sections_remain_present_once(self):
        content = CHANGELOG.read_text(encoding="utf-8")
        versions = re.findall(r"^## (0\.\d+\.\d+) — ", content, flags=re.MULTILINE)
        expected = [
            "0.11.0", "0.10.0", "0.9.0", "0.8.0", "0.7.0", "0.6.0",
            "0.5.1", "0.5.0", "0.4.0", "0.3.0", "0.2.0", "0.1.0",
        ]
        self.assertEqual(versions, expected)


if __name__ == "__main__":
    unittest.main()
