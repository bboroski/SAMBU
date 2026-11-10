from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from sambu.articulatory import BUILTIN_ALIASES, KEYWORD_ALIASES


GRAMMAR_PATH = (
    Path(__file__).resolve().parents[1]
    / "syntaxes"
    / "SAMBU.tmLanguage.json"
)


def _all_patterns(value):
    """Yield nested TextMate patterns without depending on a grammar parser."""
    if isinstance(value, dict):
        if any(key in value for key in ("match", "begin", "end")):
            yield value
        for child in value.values():
            yield from _all_patterns(child)
    elif isinstance(value, list):
        for child in value:
            yield from _all_patterns(child)


class SambuEditorGrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grammar = json.loads(GRAMMAR_PATH.read_text(encoding="utf-8"))
        cls.repository = cls.grammar["repository"]

    def test_grammar_declares_the_native_sambu_extension_and_scope(self):
        self.assertEqual(self.grammar["name"], "SAMBU")
        self.assertEqual(self.grammar["scopeName"], "source.sambu")
        self.assertIn("sambu", self.grammar["fileTypes"])

    def test_every_textmate_regular_expression_compiles(self):
        for pattern in _all_patterns(self.grammar):
            for key in ("match", "begin", "end"):
                expression = pattern.get(key)
                if expression is not None:
                    with self.subTest(key=key, expression=expression):
                        re.compile(expression)

    def test_every_active_articulatory_keyword_is_highlighted(self):
        expression = re.compile(self.repository["keywords"]["match"])
        canonical_and_articulated = set(KEYWORD_ALIASES)
        canonical_and_articulated.update(KEYWORD_ALIASES.values())
        for word in canonical_and_articulated:
            with self.subTest(word=word):
                self.assertIsNotNone(expression.search(word))

    def test_every_articulatory_builtin_alias_is_highlighted_as_a_call(self):
        expression = re.compile(
            self.repository["builtins"]["patterns"][0]["match"]
        )
        for alias in BUILTIN_ALIASES:
            with self.subTest(alias=alias):
                match = expression.search(alias + "(")
                self.assertIsNotNone(match)
                self.assertEqual(match.group(0), alias)

    def test_both_string_delimiters_are_supported(self):
        string_patterns = self.repository["strings"]["patterns"]
        self.assertEqual(
            {pattern["name"] for pattern in string_patterns},
            {"string.quoted.single.sambu", "string.quoted.double.sambu"},
        )


if __name__ == "__main__":
    unittest.main()
