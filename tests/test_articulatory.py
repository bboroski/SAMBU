from __future__ import annotations

import unittest

from sambu.articulatory import (
    ACTIVE_WORDS,
    ARTICULATORY_WORDS,
    BUILTIN_ALIASES,
    KEYWORD_ALIASES,
    RESERVED_WORDS,
    filter_articulatory_words,
    lookup_articulatory_word,
)
from sambu.ide import SambuIDE
from sambu.interpreter import execute
from sambu.lexer import tokenize


class ArticulatoryWordbookTests(unittest.TestCase):
    def test_wordbook_has_exactly_200_unique_two_syllable_words(self):
        words = [entry.word for entry in ARTICULATORY_WORDS]
        self.assertEqual(len(words), 200)
        self.assertEqual(len(set(words)), 200)
        self.assertTrue(all("-" in entry.pronunciation for entry in ARTICULATORY_WORDS))
        self.assertEqual(len(ACTIVE_WORDS) + len(RESERVED_WORDS), 200)

    def test_wordbook_is_the_full_ten_by_five_by_four_matrix(self):
        self.assertEqual(len({entry.family_code for entry in ARTICULATORY_WORDS}), 10)
        self.assertEqual(len({entry.grade_code for entry in ARTICULATORY_WORDS}), 5)
        self.assertEqual(len({entry.coda for entry in ARTICULATORY_WORDS}), 4)
        for family in "ktrmsvdnpl":
            self.assertEqual(len(filter_articulatory_words(family=family)), 20)

    def test_all_lexemes_have_compositional_meanings_and_status(self):
        for entry in ARTICULATORY_WORDS:
            self.assertTrue(entry.meaning)
            self.assertIn(entry.status, {"keyword", "builtin", "reserved"})
            self.assertEqual(entry.word, entry.pronunciation.replace("-", ""))

    def test_keyword_and_builtin_aliases_resolve_to_existing_targets(self):
        self.assertEqual(len(KEYWORD_ALIASES), 25)
        self.assertEqual(len(BUILTIN_ALIASES), 123)
        self.assertIn("lava", BUILTIN_ALIASES)
        self.assertEqual(BUILTIN_ALIASES["lava"], "print")
        self.assertIn("word_info", BUILTIN_ALIASES.values())
        self.assertIn("wordbook", BUILTIN_ALIASES.values())
        self.assertIsNotNone(lookup_articulatory_word("kava"))
        self.assertIsNone(lookup_articulatory_word("not-a-sambu-word"))

    def test_filter_supports_active_reserved_family_and_exact_status(self):
        self.assertEqual(len(filter_articulatory_words(status="active")), len(ACTIVE_WORDS))
        self.assertEqual(len(filter_articulatory_words(status="reserved")), len(RESERVED_WORDS))
        self.assertEqual(len(filter_articulatory_words(family="structure")), 20)
        self.assertEqual(len(filter_articulatory_words(status="keyword")), len(KEYWORD_ALIASES))
        with self.assertRaises(ValueError):
            filter_articulatory_words(status="imaginary")


class ArticulatorySyntaxTests(unittest.TestCase):
    def test_keyword_aliases_keep_original_spelling_and_source_span(self):
        tokens = tokenize("kava answer = 7")
        alias = next(token for token in tokens if token.lexeme == "kava")
        self.assertEqual(alias.value, "let")
        self.assertEqual(alias.lexeme, "kava")
        self.assertEqual(alias.span.start.offset, 0)
        self.assertEqual(alias.span.end.offset, 4)

    def test_articulatory_program_executes_through_existing_interpreter(self):
        source = """
kava temperature = 300 * K
kava particle_mass = 6.6e-26 * kg
kava profile = vava(temperature, particle_mass)

tava square(value) {
  tavum value * value
}

teva square(5) > 0 {
  lava(profile.rms)
  lava(square(5))
} teven {
  lava(0)
}
"""
        output: list[str] = []
        result = execute(source, output=output.append)
        self.assertEqual(result, 25.0)
        self.assertEqual(len(output), 2)
        self.assertTrue(output[0].endswith("m/s"))
        self.assertEqual(output[1], "25")

    def test_boolean_articulation_maps_to_logical_operators_and_literals(self):
        result = execute(
            "kava ready = ravum rava ravir reva\n"
            "ready raven reva"
        )
        self.assertTrue(result)

    def test_class_and_method_articulation_maps_to_oop_grammar(self):
        source = """
kaven Animal {
  tava sound(self) {
    tavum "quack"
  }
}
kaven Duck kavir Animal {}
kava bird = Duck()
bird.sound()
"""
        self.assertEqual(execute(source), "quack")

    def test_builtin_articulation_maps_to_the_same_implementation(self):
        self.assertEqual(execute("viva(25)"), 5.0)
        self.assertEqual(execute("sqrt(25)"), 5.0)

    def test_word_info_and_wordbook_are_queryable_from_sambu_source(self):
        source = """
kava entry = leven("kava")
kava active_words = levir("active")
[entry.status, entry.target, count(active_words)]
"""
        result = execute(source)
        self.assertEqual(result[0], "keyword")
        self.assertEqual(result[1], "let")
        self.assertEqual(result[2], len(ACTIVE_WORDS))

    def test_reserved_words_are_discoverable_but_not_executable_aliases(self):
        from sambu.lexer import SambuSyntaxError

        with self.assertRaises(SambuSyntaxError):
            execute("kava value = kava")
        self.assertEqual(execute('leven("kava").status'), "keyword")
        self.assertEqual(
            execute('count(levir("reserved"))'),
            len(RESERVED_WORDS),
        )

    def test_ide_completion_includes_active_articulatory_forms(self):
        ide = SambuIDE()
        self.assertIn("kava", ide.complete("kav"))
        self.assertIn("tava", ide.complete("tav"))
        self.assertIn("vava", ide.complete("vav"))
        self.assertIn("lava", ide.complete("lav"))


if __name__ == "__main__":
    unittest.main()
