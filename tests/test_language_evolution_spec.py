import re
import unittest
from pathlib import Path


class LanguageEvolutionSpecificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(__file__).resolve().parents[1] / "docs" / "LANGUAGE_EVOLUTION.md"
        cls.content = cls.path.read_text(encoding="utf-8")

    def test_all_contracts_are_present_in_order(self):
        ids = re.findall(r"^\*\*(\d{3})\.\*\*", self.content, flags=re.MULTILINE)
        self.assertEqual(ids, [f"{i:03d}" for i in range(1, 102)])

    def test_actual_baseline_and_future_status_are_explicit(self):
        for phrase in ("hosted by Python", "does not yet provide native compilation",
                       "borrow checking", "Planned", "Deferred"):
            self.assertIn(phrase.lower(), self.content.lower())

    def test_systems_domains_are_covered(self):
        for phrase in ("bare-metal", "NUMA", "HTTP/3", "QUIC", "CRDTs",
                       "TPM/HSM", "eBPF", "WCET", "Sambu.toml", "content-addressed"):
            self.assertIn(phrase.lower(), self.content.lower())


if __name__ == "__main__":
    unittest.main()
