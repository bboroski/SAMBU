import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_term_capability_map import MAPPING, validate  # noqa: E402


class TermCapabilityMapTests(unittest.TestCase):
    def test_every_source_record_has_a_valid_mapping(self):
        self.assertEqual(validate(), [])

    def test_mapping_contains_550_records(self):
        lines = MAPPING.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines) - 1, 550)

    def test_biology_and_reaper_sources_are_both_present(self):
        rows = MAPPING.read_text(encoding="utf-8").splitlines()[1:]
        counts = Counter(row.split("\t", 1)[0] for row in rows)
        self.assertEqual(counts["biology_500"], 500)
        self.assertEqual(counts["reaper_engineering_50"], 50)


if __name__ == "__main__":
    unittest.main()
