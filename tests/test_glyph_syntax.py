from __future__ import annotations

import unittest

from sambu import (
    ArrayExpr, BinaryExpr, FieldExpr, FunctionStatement, IfStatement,
    LetStatement, GLYPH_ALIASES, GLYPH_SYNTAX_VERSION, parse_ast,
)
from sambu.lexer import SambuSyntaxError, tokenize


class GlyphSyntaxTests(unittest.TestCase):
    def test_profile_and_public_registry(self):
        self.assertEqual(GLYPH_SYNTAX_VERSION, "SGS-1")
        self.assertIn("}-", GLYPH_ALIASES)
        self.assertIn("]-=", GLYPH_ALIASES)
        self.assertNotIn("[[", GLYPH_ALIASES)
        self.assertNotIn("]]", GLYPH_ALIASES)

    def test_function_and_operator_aliases_reach_typed_ast(self):
        function = parse_ast("}- square(x) --{ return x */ x }").statements[0]
        self.assertIsInstance(function, FunctionStatement)
        self.assertIsInstance(function.body[0].value, BinaryExpr)
        self.assertEqual(function.body[0].value.operator, "*")

    def test_double_brackets_remain_two_tokens_and_nested_arrays_work(self):
        tokens = tokenize("[[1], [2]]")
        self.assertEqual([t.value for t in tokens if t.value in ("[", "]")], ["[", "[", "]", "[", "]", "]"])

    def test_nested_arrays_and_member_access(self):
        program = parse_ast("let values = [[1, 2], [3, 4]];; let result = model::rms")
        values, result = program.statements
        self.assertIsInstance(values, LetStatement)
        self.assertIsInstance(values.value, ArrayExpr)
        self.assertEqual(len(values.value.items), 2)
        self.assertIsInstance(result.value, FieldExpr)
        self.assertEqual(result.value.name, "rms")

    def test_else_transition_builds_if_else_ast(self):
        conditional = parse_ast("if (1 :- 2) --{ print(1) }{ print(0) }").statements[0]
        self.assertIsInstance(conditional, IfStatement)
        self.assertEqual(len(conditional.then_body), 1)
        self.assertEqual(len(conditional.else_body), 1)

    def test_separators_and_operator_aliases(self):
        source = "let a = 4 +_ 2;; let b = a /+-* 3;: let c = b :- 30"
        a, b, c = parse_ast(source).statements
        self.assertEqual(a.value.operator, "+")
        self.assertEqual(b.value.operator, "+")
        self.assertEqual(c.value.operator, "<")

    def test_multiline_glyph_string(self):
        source = 'let note = "{first line\\nsecond line}"'
        string = next(token for token in tokenize(source) if token.kind == "STRING")
        self.assertEqual(string.value, "first line\nsecond line")
        self.assertEqual(string.lexeme, '"{first line\\nsecond line}"')

    def test_dollar_delimited_raw_multiline_string(self):
        source = """let raw = $$first line
second line$$"""
        token = next(item for item in tokenize(source) if item.kind == "STRING")
        self.assertEqual(token.value, "first line\nsecond line")
        self.assertEqual(token.lexeme, "$first line\nsecond line$")

    def test_escaped_dollar_delimiter_is_preserved_as_content(self):
        source = r"$$left \$$ right$$"
        token = next(item for item in tokenize(source) if item.kind == "STRING")
        self.assertEqual(token.value, "left $$ right")

    def test_unterminated_raw_glyph_string_reports_error(self):
        with self.assertRaises(SambuSyntaxError) as caught:
            tokenize("$$unfinished")
        self.assertEqual(caught.exception.code, "SAMBU-L004")

    def test_unterminated_multiline_glyph_string_reports_error(self):
        with self.assertRaises(SambuSyntaxError) as caught:
            tokenize('let note = "{unfinished')
        self.assertEqual(caught.exception.code, "SAMBU-L003")


if __name__ == "__main__":
    unittest.main()
