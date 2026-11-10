from __future__ import annotations

import unittest

from sambu import (
    CREATIVE_PREFERENCE_FEATURES,
    CreativeLearningError,
    CreativeLearningProfile,
)


class CreativeLearningProfileTests(unittest.TestCase):
    def test_collection_is_disabled_by_default_and_needs_explicit_opt_in(self):
        profile = CreativeLearningProfile()
        self.assertFalse(profile.enabled)
        with self.assertRaises(CreativeLearningError):
            profile.record_feedback("rhythm", "prefer")

    def test_records_only_aggregate_preferences(self):
        profile = CreativeLearningProfile(enabled=True)
        profile.record_feedback("rhythm", "prefer")
        profile.record_feedback("rhythm", "prefer")
        result = profile.record_feedback("rhythm", "avoid")
        self.assertEqual(result["prefer"], 2)
        self.assertEqual(result["avoid"], 1)
        self.assertAlmostEqual(result["preference_score"], 1 / 3)
        self.assertEqual(profile.event_count, 3)

    def test_unknown_features_and_choices_are_rejected(self):
        profile = CreativeLearningProfile(enabled=True)
        with self.assertRaises(CreativeLearningError):
            profile.record_feedback("raw_text", "prefer")
        with self.assertRaises(CreativeLearningError):
            profile.record_feedback("rhythm", "maybe")

    def test_event_budget_is_enforced(self):
        profile = CreativeLearningProfile(enabled=True, max_events=1)
        profile.record_feedback("clean_language", "prefer")
        with self.assertRaises(CreativeLearningError):
            profile.record_feedback("rhythm", "prefer")
        self.assertEqual(profile.remaining_events, 0)

    def test_json_round_trip_does_not_reenable_collection(self):
        profile = CreativeLearningProfile(enabled=True)
        profile.record_feedback("naturalness", "prefer")
        profile.record_feedback("clean_language", "prefer")
        exported = profile.to_json()
        restored = CreativeLearningProfile.from_json(exported)
        self.assertFalse(restored.enabled)
        self.assertEqual(restored.event_count, 2)
        self.assertEqual(restored.preference("clean_language")["prefer"], 1)
        self.assertNotIn("source_text", exported)
        self.assertNotIn("draft", exported)

    def test_invalid_snapshot_is_rejected(self):
        with self.assertRaises(CreativeLearningError):
            CreativeLearningProfile.from_json("{not-json}")
        empty = CreativeLearningProfile().to_dict()
        empty["event_count"] = 1
        with self.assertRaises(CreativeLearningError):
            CreativeLearningProfile.from_json(__import__("json").dumps(empty))

    def test_feature_registry_is_stable_and_includes_clean_language(self):
        self.assertIn("clean_language", CREATIVE_PREFERENCE_FEATURES)
        self.assertEqual(len(CREATIVE_PREFERENCE_FEATURES), 10)


if __name__ == "__main__":
    unittest.main()
