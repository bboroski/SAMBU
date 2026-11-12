from __future__ import annotations

import unittest

from sambu import GLYPH_SYNTAX_VERSION, GLYPH_TOKEN_ALIASES, parse, parse_ast, tokenize
from sambu.lexer import SambuSyntaxError
from sambu.ast import FunctionStatement, IfStatement, LetStatement


class GlyphSyntaxTests(unittest.TestCase):
    def test_registry_is_versioned_and_every_alias_is_atomic(self):
        self.assertEqual(GLYPH_SYNTAX_VERSION, "1.0")
        for spelling, (expected_kind, expected_value) in GLYPH_TOKEN_ALIASES.items():
            with self.subTest(spelling=spelling):
                token = tokenize(spelling)[0]
                self.assertEqual(token.kind, expected_kind)
                self.assertEqual(token.value, expected_value)
                self.assertEqual(token.lexeme, spelling)
                self.assertEqual(token.start_offset, 0)
                self.assertEqual(token.end_offset, len(spelling))

    def test_binding_separator_and_arithmetic_aliases_parse(self):
        source = "let answer :: 40;; print(answer +_ 2)"
        program = parse_ast(source)
        self.assertEqual(len(program.statements), 2)
        self.assertIsInstance(program.statements[0], LetStatement)
        # The historical tuple AST remains the compatibility API.
        self.assertEqual(len(parse(source)), 2)

    def test_symbolic_block_delimiters_parse_function(self):
        source = """fn square(value) --{
    return value /+-* value
}-
print(square(5))
"""
        program = parse_ast(source)
        self.assertIsInstance(program.statements[0], FunctionStatement)
        self.assertEqual(program.statements[0].name, "square")

    def test_alternate_block_delimiters_and_comparison_alias_parse(self):
        source = """if amount ]-= 10 --{
    print("small")
}- 
"""
        program = parse_ast(source)
        self.assertIsInstance(program.statements[0], IfStatement)

    def test_longest_match_wins_for_overlapping_spellings(self):
        source = "let x :: 1;;- print(x)"
        tokens = tokenize(source)
        self.assertIn(("SEMI", ";", ";;-"), [
            (token.kind, token.value, token.lexeme) for token in tokens
        ])
        self.assertNotIn(":", [token.value for token in tokens])

    def test_doubled_brackets_preserve_nested_array_literals(self):
        source = "let matrix :: [[1, 2], [3, 4]]"
        tokens = tokenize(source)
        bracket_values = [token.value for token in tokens if token.value in {"[", "]"}]
        self.assertEqual(bracket_values, ["[", "[", "]", "[", "]", "]"])
        self.assertEqual(len(parse(source)), 1)

    def test_raw_multiline_string_is_verbatim(self):
        source = "let note :: $$first line\nsecond /* line */$$;; print(note)"
        tokens = tokenize(source)
        literal = next(token for token in tokens if token.kind == "STRING")
        self.assertEqual(literal.value, "first line\nsecond /* line */")
        self.assertEqual(literal.lexeme, "$$first line\nsecond /* line */$$")
        self.assertEqual(literal.line, 1)
        self.assertEqual(literal.end_line, 2)
        self.assertEqual(len(parse(source)), 2)

    def test_block_comment_is_ignored_and_tracks_following_position(self):
        source = "let x :: 1 /* ignored\n symbols */;; print(x)"
        tokens = tokenize(source)
        print_token = next(token for token in tokens if token.value == "print")
        self.assertEqual((print_token.line, print_token.column), (2, 15))
        self.assertEqual(len(parse(source)), 2)

    def test_newline_inside_block_comment_separates_statements(self):
        source = "let x :: 1 /* comment\n*/ print(x)"
        self.assertEqual(len(parse(source)), 2)

    def test_unterminated_block_comment_has_stable_diagnostic(self):
        with self.assertRaises(SambuSyntaxError) as caught:
            tokenize("/* never closed")
        self.assertEqual(caught.exception.code, "SAMBU-L003")
        self.assertEqual(caught.exception.span.start.offset, 0)
        self.assertEqual(caught.exception.span.end.offset, len("/* never closed"))

    def test_unterminated_raw_string_has_stable_diagnostic(self):
        with self.assertRaises(SambuSyntaxError) as caught:
            tokenize("$$never closed")
        self.assertEqual(caught.exception.code, "SAMBU-L004")
        self.assertEqual(caught.exception.span.start.offset, 0)
        self.assertEqual(caught.exception.span.end.offset, len("$$never closed"))

    def test_legacy_syntax_still_parses(self):
        source = "fn add(a, b) { return a + b }\nprint(add(2, 3))"
        self.assertEqual(len(parse(source)), 2)


if __name__ == "__main__":
    unittest.main()
