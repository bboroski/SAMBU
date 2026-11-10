from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "domains" / "mass-effect" / "reapers" / "terms.seed.json"

VALID_DOMAINS = {
    "reaper.bio",
    "reaper.physics",
    "reaper.systems",
    "reaper.history",
    "reaper.ai",
}
VALID_CLASSIFICATIONS = {
    "canon-name",
    "canon-mechanic",
    "descriptive-extension",
    "speculative-fiction",
    "engineering-analogy",
}
VALID_SOURCE_KINDS = {
    "game-text",
    "codex-or-dialogue",
    "user-supplied-reference",
    "editorial-normalization",
    "engineering-transfer",
}


class ReaperDomainSeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        cls.terms = cls.catalog["terms"]

    def test_seed_covers_all_five_domains(self) -> None:
        self.assertEqual(
            {term["domain"] for term in self.terms},
            VALID_DOMAINS,
        )

    def test_term_ids_are_unique_and_domain_scoped(self) -> None:
        identifiers = [term["id"] for term in self.terms]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for term in self.terms:
            self.assertRegex(term["id"], r"^[a-z][a-z0-9]*(\.[a-z0-9-]+)+$")
            self.assertTrue(term["id"].startswith(term["domain"] + "."))

    def test_records_have_valid_bilingual_and_provenance_fields(self) -> None:
        for term in self.terms:
            with self.subTest(term=term.get("id")):
                self.assertEqual(term["schema_version"], 1)
                self.assertIn(term["domain"], VALID_DOMAINS)
                self.assertTrue(term["term_en"].strip())
                self.assertTrue(term["term_ru"].strip())
                self.assertIn(term["classification"], VALID_CLASSIFICATIONS)
                self.assertIn(term["source_kind"], VALID_SOURCE_KINDS)

    def test_seed_does_not_claim_to_be_the_full_500_term_corpus(self) -> None:
        self.assertEqual(
            self.catalog["catalog_status"],
            "representative-seed-not-full-500-entry-import",
        )


if __name__ == "__main__":
    unittest.main()
