import unittest

from sambu.serendipity import (
    SambuObservation, SambuSource, co_occurring_pairs, evidence_completeness,
    observation_timeline, robust_outlier_indices, validate_observations,
)


class SerendipityTests(unittest.TestCase):
    def event(self, key, at, **kwargs):
        return SambuObservation(key, at, key, "historical", occurred_at=at, **kwargs)

    def test_evidence_and_timeline_are_separate_from_truth(self):
        early = self.event("early", "2020-01-01T00:00:00Z", confidence=0.7,
                           sources=(SambuSource("s1", "primary-document"),
                                    SambuSource("s2", "instrument")))
        late = self.event("late", "2021-01-01T00:00:00Z")
        self.assertEqual([x.event_id for x in observation_timeline([late, early])],
                         ["early", "late"])
        self.assertGreater(evidence_completeness(early)["coverage_score"], 0)

    def test_rejects_naive_time_and_duplicate_ids(self):
        a = self.event("dup", "2020-01-01T00:00:00")
        b = self.event("dup", "2020-01-02T00:00:00Z")
        errors = validate_observations([a, b])
        self.assertTrue(any("duplicate" in error for error in errors))
        self.assertTrue(any("UTC offset" in error for error in errors))

    def test_co_occurrence_does_not_claim_causation(self):
        a = self.event("a", "2020-01-01T00:00:00Z", tags=("solar",))
        b = self.event("b", "2020-01-01T00:01:00Z", tags=("solar",))
        self.assertEqual(co_occurring_pairs([a, b], 120), [("a", "b", ("solar",))])

    def test_median_mad_flags_extreme_measurement(self):
        self.assertEqual(robust_outlier_indices([10, 11, 9, 10, 10, 100]), [5])
        self.assertEqual(robust_outlier_indices([1, 2, 3, 4]), [])


if __name__ == "__main__":
    unittest.main()
