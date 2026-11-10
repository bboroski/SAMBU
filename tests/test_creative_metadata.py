"""Tests for SAMBU's versioned creative metadata ontology."""
import unittest

from sambu.creative_metadata import (
    CREATIVE_CLUSTERS,
    CreativeMetadata,
    CreativeMetadataError,
    ONTOLOGY_VERSION,
    validate_metadata_document,
)


class CreativeMetadataTests(unittest.TestCase):
    def test_ontology_has_eight_stable_clusters(self):
        self.assertEqual(len(CREATIVE_CLUSTERS), 8)
        self.assertEqual(
            [cluster.cluster_id for cluster in CREATIVE_CLUSTERS],
            [f"T-{number:03d}" for number in range(1, 9)],
        )

    def test_metadata_round_trip_and_jsonld(self):
        item = CreativeMetadata.from_mapping({
            "cluster_id": "T-001",
            "theme": "cultural_celebration",
            "tone": "nostalgic_reverence",
            "key_symbols": ["fairground", "communal gathering"],
            "language": ["uk", "en"],
            "linguistic_register": "poetic_colloquial",
            "safety_flag": "CLEAN",
        })
        self.assertTrue(item.generation_eligible)
        self.assertEqual(item.to_dict()["ontology_version"], ONTOLOGY_VERSION)
        jsonld = item.to_jsonld()
        self.assertEqual(jsonld["@type"], "CreativeWork")
        self.assertNotIn("text", jsonld)
        self.assertNotIn("source_text", jsonld)

    def test_review_and_sanitized_flags_are_not_generation_eligible(self):
        for flag in (
            "NEEDS_REVIEW",
            "SANITIZED_ARGOT_ONLY",
            "SANITIZED_INTIMACY",
            "EXCLUDED_FROM_GENERATION",
        ):
            item = CreativeMetadata("T-004", "emotional_duality", "reflective", safety_flag=flag)
            self.assertFalse(item.generation_eligible)
        satire = CreativeMetadata(
            "T-007", "conflict_resilience", "satirical", safety_flag="CLEAN_SATIRE"
        )
        self.assertTrue(satire.generation_eligible)

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
