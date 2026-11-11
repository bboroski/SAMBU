from __future__ import annotations

import unittest

from sambu import EMOJI_SYNTAX, execute, tokenize


class EmojiProgrammingTests(unittest.TestCase):
    def test_public_alias_table_covers_core_language_forms(self):
        self.assertEqual(EMOJI_SYNTAX["📦"], ("IDENT", "let"))
        self.assertEqual(EMOJI_SYNTAX["📣"], ("IDENT", "print"))
        self.assertEqual(EMOJI_SYNTAX["✖️"], ("OP", "*"))
        self.assertEqual(EMOJI_SYNTAX["🟰🟰"], ("OP", "=="))

    def test_emoji_tokens_keep_lexemes_and_unicode_source_spans(self):
        source = "📦 value 🟰 2 ✖️ 3"
        tokens = tokenize(source)
        declaration = next(token for token in tokens if token.lexeme == "📦")
        assignment = next(token for token in tokens if token.lexeme == "🟰")
        multiplication = next(token for token in tokens if token.lexeme == "✖️")

        self.assertEqual((declaration.kind, declaration.value), ("IDENT", "let"))
        self.assertEqual((declaration.start_offset, declaration.end_offset), (0, 1))
        self.assertEqual((assignment.kind, assignment.value), ("OP", "="))
        self.assertEqual((multiplication.kind, multiplication.value), ("OP", "*"))
        self.assertEqual(multiplication.end_offset - multiplication.start_offset, 2)
        self.assertEqual(multiplication.lexeme, "✖️")

    def test_emoji_syntax_executes_functions_conditionals_and_loops(self):
        source = """📦 answer 🟰 6 ✖️ 7
🧱 twice(value) {
    ↩️ value ➕ value
}
📣(twice(answer))
❓ answer 🟰🟰 42 {
    📣("Emoji syntax is active")
} 🙃 {
    📣("The calculation changed")
}
🔁 item 🧺 [1, 2, 3] {
    📣(item)
}"""
        output: list[str] = []
        result = execute(source, output=output.append)

        self.assertEqual(result, 3.0)
        self.assertEqual(output, ["84", "Emoji syntax is active", "1", "2", "3"])

    def test_emoji_inside_strings_and_comments_are_not_rewritten(self):
        source = '📣("📦 is text, not a declaration") # 🧱 is a comment\n'
        output: list[str] = []
        execute(source, output=output.append)
        self.assertEqual(output, ["📦 is text, not a declaration"])

    def test_ordinary_sambu_tokens_remain_unchanged(self):
        output: list[str] = []
        execute("let value = 2 + 3\nprint(value)", output=output.append)
        self.assertEqual(output, ["5"])


if __name__ == "__main__":
    unittest.main()
