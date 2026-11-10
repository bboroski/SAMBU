from __future__ import annotations

import unittest

from sambu.script_profiles import inspect_script_profile, unicode_script


class UnicodeScriptProfileTests(unittest.TestCase):
    def test_latin_text_keeps_codepoint_offsets(self):
        value = "café_42"
        profile = inspect_script_profile(value)

        self.assertEqual(profile.scripts, ("Latin",))
        self.assertFalse(profile.mixed)
        self.assertFalse(profile.confusable_mixing)
        self.assertEqual("".join(run.text for run in profile.runs), value)
        self.assertEqual(profile.runs[0].start_offset, 0)
        self.assertEqual(profile.runs[-1].end_offset, len(value))

    def test_latin_cyrillic_homoglyph_mixture_is_flagged(self):
        value = "pаypal"  # The second character is Cyrillic small a.
        profile = inspect_script_profile(value)

        self.assertEqual(profile.scripts, ("Latin", "Cyrillic"))
        self.assertTrue(profile.mixed)
        self.assertTrue(profile.confusable_mixing)
        self.assertEqual("".join(run.text for run in profile.runs), value)

    def test_greek_and_coptic_are_distinguished(self):
        self.assertEqual(unicode_script("α"), "Greek")
        self.assertEqual(unicode_script("\u03e2"), "Coptic")

    def test_egyptian_hieroglyphs_have_a_distinct_profile(self):
        profile = inspect_script_profile("\U00013000\U00013001")

        self.assertEqual(profile.scripts, ("Egyptian Hieroglyphic",))
        self.assertFalse(profile.mixed)
        self.assertEqual(profile.runs[0].text, "\U00013000\U00013001")

    def test_combining_mark_attaches_without_changing_source(self):
        value = "e\u0301"
        profile = inspect_script_profile(value)

        self.assertEqual(profile.scripts, ("Latin",))
        self.assertEqual(profile.runs[0].text, value)
        self.assertEqual(profile.runs[0].end_offset, 2)
        self.assertEqual(value, "e\u0301")

    def test_invalid_single_character_argument_is_rejected(self):
        with self.assertRaises(ValueError):
            unicode_script("ab")


if __name__ == "__main__":
    unittest.main()
