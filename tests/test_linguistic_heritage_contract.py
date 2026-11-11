import json
import unittest
from pathlib import Path

RECORD = Path(__file__).resolve().parents[1] / "data" / "linguistic-heritage" / "cyrillic-letter-y.json"

class LinguisticHeritageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_identity_and_version(self):
        self.assertEqual(self.record["schema_version"], "linguistic-heritage.letter.v1")
        self.assertEqual(self.record["grapheme"], "Ы")
        self.assertEqual(self.record["lowercase"], "ы")

    def test_graphic_and_phonetic_histories_are_separate(self):
        self.assertIn("historical_graphics", self.record)
        self.assertIn("phoneme_profile", self.record)
        self.assertIn("historical_phonology", self.record)
        self.assertNotIn("Ъ becomes [ɨ] in every context", self.record["historical_phonology"].get("claim", ""))

    def test_uncertainty_and_interpretation_are_explicit(self):
        self.assertIn("confidence", self.record["historical_graphics"])
        self.assertIn("status", self.record["interpretive_layer"])
        self.assertEqual(self.record["interpretive_layer"]["status"], "cultural_interpretation_not_historical_evidence")
        self.assertTrue(self.record["claims_policy"]["label_hypotheses_and_metaphors"])

    def test_comparative_claims_are_not_equivalences(self):
        self.assertIn("polish_y", self.record["comparative_slavic"])
        self.assertIn("ukrainian_y", self.record["comparative_slavic"])
        self.assertIn("not identical", self.record["comparative_slavic"]["polish_y"])

    def test_references_are_linked(self):
        self.assertGreaterEqual(len(self.record["references"]), 2)
        for source in self.record["references"]:
            self.assertTrue(source["url"].startswith("https://"))

if __name__ == "__main__":
    unittest.main()
