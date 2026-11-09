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
}


class AutonomyConstitutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "docs" / "AUTONOMY_CONSTITUTION.md"
        cls.content = path.read_text(encoding="utf-8")
        cls.rows = re.findall(
            r"^\| (AUT-\d{2}) \| ([^|]+) \| (Implemented|Partial|Planned|Deferred) \|",
            cls.content,
            flags=re.MULTILINE,
        )

    def test_exactly_fifty_ordered_unique_contracts_exist(self):
        ids = [row[0] for row in self.rows]
        self.assertEqual(ids, [f"AUT-{i:02d}" for i in range(1, 51)])
        self.assertEqual(len(ids), len(set(ids)))

    def test_statuses_match_reviewed_repository_baseline(self):
        actual = {rule_id: status for rule_id, _, status in self.rows}
        self.assertEqual(actual, EXPECTED)
        self.assertTrue(set(actual.values()).issubset(STATUS))

    def test_each_constitutional_block_contains_ten_contracts(self):
        blocks = re.split(r"^## Block [IVX]+ — .+$", self.content, flags=re.MULTILINE)[1:]
        self.assertEqual(len(blocks), 5)
        for block in blocks:
            ids = re.findall(r"^\| (AUT-\d{2}) \|", block, flags=re.MULTILINE)
            self.assertEqual(len(ids), 10)

    def test_self_hosting_linker_abi_and_concurrency_are_not_claimed(self):
        for phrase in (
            "not itself implement a feature", "object format",
            "calling convention", "cannot yet compile its compiler",
            "no language-level task scheduler",
        ):
            self.assertIn(phrase, self.content)

    def test_constitution_is_linked_from_language_architecture(self):
        architecture = (ROOT / "docs" / "LANGUAGE_EVOLUTION.md").read_text(encoding="utf-8")
        self.assertIn("AUTONOMY_CONSTITUTION.md", architecture)


if __name__ == "__main__":
    unittest.main()
