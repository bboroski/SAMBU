from __future__ import annotations

import unittest

from sambu.lexer import SambuSyntaxError, tokenize
from sambu.parser import parse
from sambu.source import SourcePosition, SourceSpan


class SourceSpanTests(unittest.TestCase):
    def test_token_span_is_end_exclusive_and_tracks_unicode_offsets(self):
        source = "let café = 3\nprint(café)"
        tokens = tokenize(source)
        name = next(token for token in tokens if token.value == "café")

        self.assertEqual(name.span.start, SourcePosition(4, 1, 5))
        self.assertEqual(name.span.end, SourcePosition(8, 1, 9))
        self.assertFalse(name.span.is_empty)

    def test_multiline_tokens_and_eof_have_exact_positions(self):
        source = "let x = 1\nprint(x)"
        tokens = tokenize(source)
        print_token = next(token for token in tokens if token.value == "print")
        eof = tokens[-1]

        self.assertEqual(print_token.span.start, SourcePosition(10, 2, 1))
        self.assertEqual(eof.span, SourceSpan.point(SourcePosition(len(source), 2, 9)))

    def test_lexer_error_has_stable_code_and_offending_character_span(self):
        with self.assertRaises(SambuSyntaxError) as caught:
            tokenize("@")

        error = caught.exception
        self.assertEqual(error.code, "SAMBU-L001")
        self.assertEqual(error.span, SourceSpan(
            SourcePosition(0, 1, 1), SourcePosition(1, 1, 2)
        ))
        self.assertEqual((error.line, error.column), (1, 1))
        self.assertIn("(line 1, column 1)", str(error))

    def test_unterminated_string_span_runs_to_eof(self):
        with self.assertRaises(SambuSyntaxError) as caught:
            tokenize('"abc')

        error = caught.exception
        self.assertEqual(error.code, "SAMBU-L002")
        self.assertEqual(error.span.start, SourcePosition(0, 1, 1))
        self.assertEqual(error.span.end, SourcePosition(4, 1, 5))

    def test_parser_error_points_to_unexpected_token(self):
        with self.assertRaises(SambuSyntaxError) as caught:
            parse("let = 1")

        error = caught.exception
        self.assertEqual(error.code, "SAMBU-P001")
        self.assertEqual(error.span.start, SourcePosition(4, 1, 5))
        self.assertEqual(error.span.end, SourcePosition(5, 1, 6))

    def test_source_span_rejects_reversed_offsets(self):
        with self.assertRaises(ValueError):
            SourceSpan(SourcePosition(2, 1, 3), SourcePosition(1, 1, 2))


if __name__ == "__main__":
    unittest.main()
