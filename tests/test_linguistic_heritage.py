import json
import unittest
from linguistic_heritage import ClaimStatus, analyze_yery, compare_vowels

class LinguisticHeritageTests(unittest.TestCase):
    def test_yery_profile_identity(self):
        profile = analyze_yery()
        self.assertEqual(profile["letter"]["glyph"], "Ы")
        self.assertEqual(profile["letter"]["lowercase"], "ы")
        self.assertEqual(profile["letter"]["unicode"]["uppercase"], "U+042B")

    def test_claims_are_evidence_labeled(self):
        statuses = {x["id"]: x["status"] for x in analyze_yery()["claims"]}
        self.assertEqual(statuses["yery-ligature"], ClaimStatus.ESTABLISHED.value)
        self.assertEqual(statuses["turkic-causation"], ClaimStatus.HYPOTHESIS.value)
        self.assertEqual(statuses["peter-ban"], ClaimStatus.UNSUPPORTED.value)

    def test_vowel_comparison_is_selective(self):
        result = compare_vowels(["i", "ɨ", "ɯ", "x"])
        self.assertEqual(set(result), {"i", "ɨ", "ɯ"})
        self.assertIn("central", result["ɨ"]["label"])

    def test_result_is_json_serializable(self):
        json.dumps(analyze_yery(), ensure_ascii=False)

if __name__ == "__main__":
    unittest.main()
