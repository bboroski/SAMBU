from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from sambu.articulatory import BUILTIN_ALIASES, KEYWORD_ALIASES


GRAMMAR_PATH = Path(__file__).resolve().parents[1] / "syntaxes" / "SAMBU.tmLanguage.json"


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

    def test_all_control_keywords_and_articulatory_spellings_are_highlighted(self):
        expression = re.compile(self.repository["keywords"]["match"])
        values = set(KEYWORD_ALIASES) | set(KEYWORD_ALIASES.values())
        literals = {"true", "false", "null", "ravum", "reva", "reven"}
        logical = {"and", "or", "not", "rava", "raven", "ravir"}
        for word in values - literals - logical:
            with self.subTest(word=word):
                self.assertIsNotNone(expression.search(word))

    def test_logical_operators_have_their_own_scope(self):
        expression = re.compile(self.repository["logical"]["match"])
        for word in ("and", "or", "not", "rava", "raven", "ravir"):
            with self.subTest(word=word):
                self.assertIsNotNone(expression.search(word))

    def test_boolean_and_null_literals_have_their_own_scope(self):
        expression = re.compile(self.repository["constants"]["match"])
        for word in ("true", "false", "null", "ravum", "reva", "reven"):
            with self.subTest(word=word):
                self.assertIsNotNone(expression.search(word))

    def test_every_articulatory_builtin_and_canonical_callable_is_highlighted(self):
        expression = re.compile(
            self.repository["builtins"]["patterns"][0]["match"]
        )
        names = set(BUILTIN_ALIASES) | set(BUILTIN_ALIASES.values())
        for name in names:
            with self.subTest(name=name):
                match = expression.search(name + "(")
                self.assertIsNotNone(match)
                self.assertEqual(match.group(0), name)

    def test_pascal_delphi_and_fortran_keywords_are_highlighted(self):
        expression = re.compile(self.repository["keywords"]["match"])
        dialect_words = {
            "program", "unit", "uses", "var", "const", "type", "begin", "end",
            "then", "to", "downto", "do", "function", "procedure", "interface",
            "implementation", "initialization", "finalization", "public",
            "private", "protected", "published", "property", "implicit", "none",
            "integer", "int", "real", "double", "precision", "logical",
            "character", "module", "contains", "recursive", "result",
            "subroutine", "print", "write", "call", "array",
        }
        for word in dialect_words:
            with self.subTest(word=word):
                self.assertIsNotNone(expression.search(word))

    def test_fortran_dotted_operators_and_logical_constants_are_highlighted(self):
        operators = re.compile(self.repository["fortran_operators"]["match"])
        constants = re.compile(self.repository["fortran_constants"]["match"])
        for token in (".and.", ".or.", ".not.", ".eqv.", ".neqv.", ".eq.", ".ne.", ".lt.", ".le.", ".gt.", ".ge."):
            with self.subTest(token=token):
                self.assertEqual(operators.search(token).group(0), token)
        for token in (".true.", ".false."):
            with self.subTest(token=token):
                self.assertEqual(constants.search(token).group(0), token)

    def test_pascal_and_fortran_comment_forms_are_registered(self):
        names = {pattern["name"] for pattern in self.repository["comments"]["patterns"]}
        self.assertTrue({
            "comment.line.number-sign.sambu",
            "comment.line.double-slash.pascal",
            "comment.line.exclamation.fortran",
            "comment.block.curly.pascal",
            "comment.block.parenthesized-pascal",
        }.issubset(names))

    def test_both_string_delimiters_and_glyph_strings_are_supported(self):
        string_patterns = self.repository["strings"]["patterns"]
        names = {pattern["name"] for pattern in string_patterns}

        self.assertTrue(
            {"string.quoted.single.sambu", "string.quoted.double.sambu"}.issubset(names)
        )
        glyph_scopes = {name for name in names if name.endswith(".glyph.sambu")}
        self.assertTrue(glyph_scopes, "glyph string scopes must be registered")
        self.assertTrue(
            all(name.startswith("string.quoted.") for name in glyph_scopes),
            f"unexpected glyph string scopes: {sorted(glyph_scopes)}",
        )

    def test_glyph_tokens_have_a_dedicated_scope(self):
        expression = re.compile(self.repository["glyph"]["match"])
        for token in ("[[", "]]", "}-", "--{", "::", ";;", ":;", ";:",
                      "+_", "/+-*", "*/", ":-", "-:", ";;-", ";-"):
            with self.subTest(token=token):
                match = expression.search(token)
                self.assertIsNotNone(match)
                self.assertEqual(match.group(0), token)


if __name__ == "__main__":
    unittest.main()
