import json
import unittest
from pathlib import Path

RECORD = Path(__file__).resolve().parents[1] / "data" / "linguistic-heritage" / "cyrillic-letter-y.json"
CLAIM_STATES = {"established", "qualified", "hypothesis", "unsupported"}

class LinguisticHeritageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_identity_and_unicode(self):
        self.assertEqual(self.record["schema_version"], "linguistic-heritage.letter.v1")
        self.assertEqual((self.record["glyph"], self.record["lowercase"]), ("Ы", "ы"))
        self.assertEqual(self.record["unicode"], {"uppercase": "U+042B", "lowercase": "U+044B"})

    def test_grapheme_and_sound_histories_are_separate(self):
        self.assertIn("historical_graphics", self.record)
        self.assertIn("historical_phonology", self.record)
        self.assertIn("phoneme_profile", self.record)
        self.assertTrue(self.record["claims_policy"]["separate_grapheme_history_from_sound_history"])

    def test_claims_have_reviewable_status(self):
        self.assertTrue(self.record["claims"])
        for claim in self.record["claims"]:
            self.assertTrue(claim["id"] and claim["statement"] and claim["rationale"])
            self.assertIn(claim["status"], CLAIM_STATES)

    def test_interpretation_is_not_historical_evidence(self):
        self.assertEqual(self.record["interpretive_layer"]["status"], "cultural_interpretation_not_historical_evidence")
        self.assertTrue(self.record["claims_policy"]["label_hypotheses_and_metaphors"])

    def test_slavic_comparison_is_qualified(self):
        self.assertIn("not identical", self.record["comparative_slavic"]["polish_y"])
        self.assertIn("not an exact equivalent", self.record["comparative_slavic"]["ukrainian_y"])

    def test_references_are_https(self):
        self.assertGreaterEqual(len(self.record["references"]), 2)
        self.assertTrue(all(item["url"].startswith("https://") for item in self.record["references"]))

if __name__ == "__main__":
    unittest.main()
