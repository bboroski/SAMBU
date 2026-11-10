import tempfile
import unittest
from pathlib import Path

from sambu.biology_domain import (
    BiologyCatalogue,
    BiologyCatalogueError,
    BiologyTerm,
    TermAnnotation,
    annotation_digest,
    validate_catalogue,
)


ROOT = Path(__file__).resolve().parents[1]


class BiologyDomainTests(unittest.TestCase):
    def setUp(self):
        self.catalogue = BiologyCatalogue.load()

    def test_all_500_records_and_five_categories_validate(self):
        report = validate_catalogue()
        self.assertTrue(report.valid, report.errors)
        self.assertEqual(report.term_count, 500)
        self.assertEqual(set(report.category_counts.values()), {100})

    def test_bilingual_search_is_category_filterable(self):
        english = self.catalogue.search("Transcription", language="en")
        russian = self.catalogue.search("Транскрипция", language="ru")
        self.assertEqual(english[0].term_id, russian[0].term_id)
        scoped = self.catalogue.search(
            "selection", language="en", categories=["genetics_evolution"]
        )
        self.assertTrue(scoped)
        self.assertTrue(all(item.category == "genetics_evolution" for item in scoped))

    def test_stable_id_lookup(self):
        item = self.catalogue.get(1)
        self.assertEqual(item.term_en, "Transcription")
        with self.assertRaises(BiologyCatalogueError):
            self.catalogue.get(9999)

    def test_annotation_requires_evidence_and_note(self):
        annotation = self.catalogue.annotate(
            1, evidence_ref="docs/lesson-1.md",
            note="Educational glossary cross-reference",
            tags=["education", "molecular"],
        )
        self.assertEqual(annotation.term_id, 1)
        self.assertEqual(annotation.tags, ("education", "molecular"))
        with self.assertRaises(ValueError):
            self.catalogue.annotate(1, evidence_ref="", note="note")

    def test_annotation_digest_is_order_independent(self):
        first = TermAnnotation(1, "source-a", "note-a", ("bio",))
        second = TermAnnotation(2, "source-b", "note-b", ("data",))
        self.assertEqual(annotation_digest([first, second]), annotation_digest([second, first]))

    def test_invalid_records_are_rejected(self):
        with self.assertRaises(BiologyCatalogueError):
            BiologyCatalogue([
                BiologyTerm(1, "molecular_cell", "", "Тест"),
            ])

    def test_bad_header_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.tsv"
            path.write_text("id\tterm\n1\titem\n", encoding="utf-8")
            with self.assertRaises(BiologyCatalogueError):
                BiologyCatalogue.load(path)


if __name__ == "__main__":
    unittest.main()
