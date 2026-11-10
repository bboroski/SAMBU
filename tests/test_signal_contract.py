from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class TextSignalContractTests(unittest.TestCase):
    def test_schema_and_neutral_fixture_are_version_aligned(self):
        schema = json.loads(
            (ROOT / "schemas" / "text-signal-envelope.schema.json").read_text(encoding="utf-8")
        )
        fixture = json.loads(
            (ROOT / "examples" / "multilingual_signal_envelope.sample.json").read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        self.assertEqual(fixture["schema_version"], 1)
        self.assertFalse(fixture["raw_text_stored"])
        self.assertEqual(schema["properties"]["raw_text_stored"]["const"], False)

    def test_representations_do_not_collapse_script_and_language(self):
        fixture = json.loads(
            (ROOT / "examples" / "multilingual_signal_envelope.sample.json").read_text(encoding="utf-8")
        )
        representations = fixture["representations"]
        self.assertEqual(representations[0]["script_profile"], ["Han"])
        self.assertEqual(representations[0]["language_hint"], "zh-Hans")
        self.assertEqual(representations[1]["script_profile"], ["Latin"])
        self.assertIsNone(representations[1]["language_hint"])
        self.assertEqual(fixture["language_identification"], "caller_supplied")
        self.assertEqual(fixture["translation_status"], "not_performed")
        self.assertEqual(fixture["semantic_status"], "not_assessed")

    def test_metadata_fixture_contains_no_source_text_fields(self):
        fixture = json.loads(
            (ROOT / "examples" / "multilingual_signal_envelope.sample.json").read_text(encoding="utf-8")
        )

        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)

        self.assertFalse({"text", "raw_text", "translated_text", "transcript"} & set(keys(fixture)))


if __name__ == "__main__":
    unittest.main()
