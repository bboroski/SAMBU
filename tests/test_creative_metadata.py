"""Tests for SAMBU's versioned creative metadata ontology."""
import json
from pathlib import Path
import unittest

from sambu.creative_metadata import (
    CREATIVE_CLUSTERS,
    CreativeMetadata,
    CreativeMetadataError,
    ONTOLOGY_VERSION,
    validate_metadata_document,
)


class CreativeMetadataTests(unittest.TestCase):
    REVIEW = {
        "review_ref": "reviewer-pseudonym-01",
        "reviewed_at": "2026-11-10T18:00:00Z",
    }
    def test_ontology_has_nine_stable_clusters(self):
        self.assertEqual(len(CREATIVE_CLUSTERS), 9)
        self.assertEqual(
            [cluster.cluster_id for cluster in CREATIVE_CLUSTERS],
            [f"T-{number:03d}" for number in range(1, 10)],
        )
        self.assertEqual(CREATIVE_CLUSTERS[-1].theme, "surreal_juxtaposition")

    def test_metadata_round_trip_and_jsonld(self):
        item = CreativeMetadata.from_mapping({
            "cluster_id": "T-001",
            "theme": "cultural_celebration",
            "tone": "neutral_informational",
            "key_symbols": ["event_calendar", "public_schedule"],
            "language": ["uk", "en"],
            "linguistic_register": "informational_prose",
            "safety_flag": "CLEAN",
            **self.REVIEW,
        })
        self.assertTrue(item.generation_eligible)
        self.assertEqual(item.to_dict()["ontology_version"], ONTOLOGY_VERSION)
        self.assertEqual(CreativeMetadata.from_mapping(item.to_dict()), item)
        jsonld = item.to_jsonld()
        self.assertEqual(jsonld["@type"], "CreativeWork")
        self.assertEqual(jsonld["reviewReference"], self.REVIEW["review_ref"])
        self.assertEqual(jsonld["dateReviewed"], self.REVIEW["reviewed_at"])
        self.assertNotIn("text", jsonld)
        self.assertNotIn("source_text", jsonld)

    def test_review_and_sanitized_flags_are_not_generation_eligible(self):
        for flag in (
            "NEEDS_REVIEW",
            "SANITIZED_ARGOT_ONLY",
            "SANITIZED_INTIMACY",
            "EXCLUDED_FROM_GENERATION",
        ):
            item = CreativeMetadata("T-004", "emotional_duality", "neutral_comparative", safety_flag=flag)
            self.assertFalse(item.generation_eligible)
        satire = CreativeMetadata(
            "T-007", "conflict_resilience", "neutral_procedural",
            safety_flag="CLEAN_SATIRE", **self.REVIEW
        )
        self.assertTrue(satire.generation_eligible)

    def test_generation_eligibility_requires_review_evidence(self):
        unreviewed_clean = CreativeMetadata(
            "T-001", "cultural_celebration", "neutral_informational",
            safety_flag="CLEAN",
        )
        self.assertFalse(unreviewed_clean.generation_eligible)

    def test_review_evidence_must_be_complete_and_timezone_aware(self):
        with self.assertRaisesRegex(CreativeMetadataError, "must be provided together"):
            CreativeMetadata(
                "T-001", "cultural_celebration", "nostalgic",
                safety_flag="CLEAN", review_ref="reviewer-01",
            )
        with self.assertRaisesRegex(CreativeMetadataError, "timezone offset"):
            CreativeMetadata(
                "T-001", "cultural_celebration", "nostalgic",
                safety_flag="CLEAN",
                review_ref="reviewer-01",
                reviewed_at="2026-11-10T18:00:00",
            )
        with self.assertRaises(CreativeMetadataError):
            CreativeMetadata(
                "T-001", "cultural_celebration", "nostalgic",
                safety_flag="CLEAN",
                review_ref="reviewer-01",
                reviewed_at="not-a-date",
            )

    def test_ontology_2026_11_records_remain_readable(self):
        legacy = CreativeMetadata.from_mapping({
            "cluster_id": "T-008",
            "theme": "linguistic_hybridity",
            "tone": "playful",
            "ontology_version": "2026.11",
        })
        self.assertEqual(legacy.ontology_version, "2026.11")
        self.assertFalse(legacy.generation_eligible)

    def test_new_cluster_requires_new_ontology_version(self):
        with self.assertRaisesRegex(CreativeMetadataError, "requires ontology_version 2026.12"):
            CreativeMetadata(
                "T-009", "surreal_juxtaposition", "playful",
                ontology_version="2026.11",
            )
        current = CreativeMetadata("T-009", "surreal_juxtaposition", "playful")
        self.assertEqual(current.ontology_version, "2026.12")

    def test_unknown_cluster_and_fields_are_rejected(self):
        with self.assertRaises(CreativeMetadataError):
            CreativeMetadata("T-999", "unknown", "neutral")
        with self.assertRaises(CreativeMetadataError):
            CreativeMetadata.from_mapping({
                "cluster_id": "T-001",
                "theme": "celebration",
                "tone": "joyful",
                "raw_text": "must not be stored here",
            })

    def test_bounds_and_hash_validation(self):
        with self.assertRaises(CreativeMetadataError):
            CreativeMetadata.from_mapping({
                "cluster_id": "T-001",
                "theme": "celebration",
                "tone": "joyful",
                "key_symbols": ["symbol"] * 17,
            })
        with self.assertRaises(CreativeMetadataError):
            CreativeMetadata.from_mapping({
                "cluster_id": "T-001",
                "theme": "celebration",
                "tone": "joyful",
                "content_sha256": "not-a-hash",
            })

    def test_synthetic_examples_fixture_is_valid_and_not_generation_eligible(self):
        sample_path = Path(__file__).resolve().parents[1] / "examples" / "creative_metadata_examples.sample.json"
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        records = validate_metadata_document(payload)
        self.assertEqual(len(records), 9)
        self.assertEqual({item.cluster_id for item in records}, {
            f"T-{number:03d}" for number in range(1, 10)
        })
        self.assertTrue(all(item.ontology_version == "2026.12" for item in records))
        self.assertTrue(all(item.safety_flag == "NEEDS_REVIEW" for item in records))
        self.assertTrue(all(not item.generation_eligible for item in records))

    def test_document_accepts_object_or_bounded_array(self):
        record = {
            "cluster_id": "T-008",
            "theme": "linguistic_hybridity",
            "tone": "playful",
            "language": ["uk", "en"],
            "safety_flag": "NEEDS_REVIEW",
        }
        self.assertEqual(len(validate_metadata_document(record)), 1)
        self.assertEqual(len(validate_metadata_document([record, record])), 2)
        with self.assertRaises(CreativeMetadataError):
            validate_metadata_document([])


if __name__ == "__main__":
    unittest.main()
