from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = {"Implemented", "Partial", "Planned", "Deferred"}
EXPECTED = {
    "AUT-01": "Partial", "AUT-02": "Implemented", "AUT-03": "Partial",
    "AUT-04": "Partial", "AUT-05": "Partial", "AUT-06": "Planned",
    "AUT-07": "Partial", "AUT-08": "Planned", "AUT-09": "Partial",
    "AUT-10": "Planned", "AUT-11": "Partial", "AUT-12": "Partial",
    "AUT-13": "Implemented", "AUT-14": "Partial", "AUT-15": "Planned",
    "AUT-16": "Implemented", "AUT-17": "Planned", "AUT-18": "Partial",
    "AUT-19": "Planned", "AUT-20": "Partial", "AUT-21": "Partial",
    "AUT-22": "Deferred", "AUT-23": "Planned", "AUT-24": "Partial",
    "AUT-25": "Partial", "AUT-26": "Planned", "AUT-27": "Partial",
    "AUT-28": "Deferred", "AUT-29": "Partial", "AUT-30": "Partial",
    "AUT-31": "Partial", "AUT-32": "Planned", "AUT-33": "Implemented",
    "AUT-34": "Partial", "AUT-35": "Deferred", "AUT-36": "Planned",
    "AUT-37": "Partial", "AUT-38": "Implemented", "AUT-39": "Planned",
    "AUT-40": "Deferred", "AUT-41": "Partial", "AUT-42": "Partial",
    "AUT-43": "Partial", "AUT-44": "Partial", "AUT-45": "Partial",
    "AUT-46": "Planned", "AUT-47": "Implemented", "AUT-48": "Partial",
    "AUT-49": "Planned", "AUT-50": "Deferred",
    "AUT-51": "Partial", "AUT-52": "Partial", "AUT-53": "Partial",
    "AUT-54": "Partial", "AUT-55": "Partial", "AUT-56": "Planned",
    "AUT-57": "Partial", "AUT-58": "Planned", "AUT-59": "Partial",
    "AUT-60": "Partial", "AUT-61": "Partial", "AUT-62": "Partial",
    "AUT-63": "Partial", "AUT-64": "Deferred", "AUT-65": "Partial",
    "AUT-66": "Planned", "AUT-67": "Planned", "AUT-68": "Partial",
    "AUT-69": "Partial", "AUT-70": "Partial", "AUT-71": "Partial",
    "AUT-72": "Partial", "AUT-73": "Partial", "AUT-74": "Planned",
    "AUT-75": "Planned", "AUT-76": "Partial", "AUT-77": "Planned",
    "AUT-78": "Partial", "AUT-79": "Partial", "AUT-80": "Partial",
    "AUT-81": "Planned", "AUT-82": "Partial", "AUT-83": "Planned",
    "AUT-84": "Partial", "AUT-85": "Planned", "AUT-86": "Partial",
    "AUT-87": "Planned", "AUT-88": "Planned", "AUT-89": "Partial",
    "AUT-90": "Partial", "AUT-91": "Partial", "AUT-92": "Partial",
    "AUT-93": "Partial", "AUT-94": "Planned", "AUT-95": "Partial",
    "AUT-96": "Partial", "AUT-97": "Partial", "AUT-98": "Partial",
    "AUT-99": "Planned", "AUT-100": "Planned",
}


class AutonomyConstitutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "docs" / "AUTONOMY_CONSTITUTION.md"
        cls.content = path.read_text(encoding="utf-8")
        cls.rows = re.findall(
            r"^\| (AUT-\d{2,3}) \| ([^|]+) \| (Implemented|Partial|Planned|Deferred) \|",
            cls.content,
            flags=re.MULTILINE,
        )

    def test_exactly_one_hundred_ordered_unique_contracts_exist(self):
        ids = [row[0] for row in self.rows]
        self.assertEqual(ids, [f"AUT-{i:02d}" for i in range(1, 101)])
        self.assertEqual(len(ids), len(set(ids)))

    def test_statuses_match_reviewed_repository_baseline(self):
        actual = {rule_id: status for rule_id, _, status in self.rows}
        self.assertEqual(actual, EXPECTED)
        self.assertTrue(set(actual.values()).issubset(STATUS))

    def test_each_constitutional_block_contains_ten_contracts(self):
        blocks = re.split(r"^## Block [IVX]+ — .+$", self.content, flags=re.MULTILINE)[1:]
        self.assertEqual(len(blocks), 10)
        for block in blocks:
            ids = re.findall(r"^\| (AUT-\d{2,3}) \|", block, flags=re.MULTILINE)
            self.assertEqual(len(ids), 10)

    def test_two_series_of_fifty_and_101_contracts_are_linked(self):
        architecture = (ROOT / "docs" / "LANGUAGE_EVOLUTION.md").read_text(encoding="utf-8")
        self.assertIn("100-rule Autonomy Constitution", architecture)
        self.assertIn("two thematic series of 50 rules", architecture)
        contracts = re.findall(
            r"^\*\*(\d{3})\.\*\*", architecture, flags=re.MULTILINE
        )
        self.assertEqual(contracts, [f"{i:03d}" for i in range(1, 102)])

    def test_quality_catalog_indexes_all_constitutional_rules(self):
        catalog = (ROOT / "docs" / "quality" / "RULE_CATALOG.md").read_text(encoding="utf-8")
        ids = re.findall(r"^\| (AUT-\d{2,3}) \|", catalog, flags=re.MULTILINE)
        self.assertEqual(ids, [f"AUT-{i:02d}" for i in range(1, 101)])
        self.assertIn("SAM-Q-SEC-001", catalog)
        self.assertIn("LANG-001–LANG-020", catalog)
        self.assertIn("LANG-091–101", catalog)

    def test_autonomy_boundaries_are_not_overclaimed(self):
        for phrase in (
            "not itself implement every capability",
            "no SAMBU object format",
            "no SAMBU calling convention",
            "cannot yet compile its compiler",
            "no language-level task scheduler",
            "Python packaging",
        ):
            self.assertIn(phrase.lower(), self.content.lower())

    def test_constitution_is_linked_from_language_architecture(self):
        architecture = (ROOT / "docs" / "LANGUAGE_EVOLUTION.md").read_text(encoding="utf-8")
        self.assertIn("AUTONOMY_CONSTITUTION.md", architecture)


if __name__ == "__main__":
    unittest.main()
