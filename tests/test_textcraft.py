from __future__ import annotations

import unittest

from sambu.interpreter import execute


class TextCraftTests(unittest.TestCase):
    def run_sambu(self, source: str):
        output: list[str] = []
        result = execute(source, output=output.append)
        return result, output

    def test_multilingual_text_and_prosody_profiles(self):
        _, output = self.run_sambu("""
let draft = "Город хранит недосказанный разговор\\nВетер разбудит забытый двор"
let words = text_profile(draft)
let sound = prosody_profile(draft)
print(words.line_count)
print(words.word_count)
print(words.unique_word_count)
print(words.lexical_diversity)
print(sound.rhyme_density)
print(sound.rhyme_groups[0].key)
print(sound.syllable_counts[0])
print(syllables("разговор"))
print(rhyme_key("разговор"))
""")
        self.assertEqual(output, ["2", "8", "8", "1", "1", "ор", "12", "3", "ор"])

    def test_alliteration_is_reported_without_rewriting_text(self):
        _, output = self.run_sambu("""
let draft = "Молчит мрачный мотор"
let sound = prosody_profile(draft)
print(sound.lines[0].has_alliteration)
print(sound.alliterative_line_count)
""")
        self.assertEqual(output, ["true", "1"])

    def test_empty_text_is_safe(self):
        _, output = self.run_sambu("""
let words = text_profile("")
let sound = prosody_profile("")
print(words.word_count)
print(sound.rhyme_density)
print(syllables(""))
print(rhyme_key("---"))
""")
        self.assertEqual(output, ["0", "0", "0", ""])

    def test_text_builtins_validate_arguments(self):
        with self.assertRaises(TypeError):
            execute("text_profile(42)")
        with self.assertRaises(TypeError):
            execute('syllables("one", "two")')

    def test_is_operator_works_for_classes_and_interfaces(self):
        _, output = self.run_sambu("""
interface HasName { fn name(self) }
class Person implements HasName {
  fn name(self) { return "Ada" }
}
let person = Person()
print(person is Person)
print(person is HasName)
print(person is Person == true)
""")
        self.assertEqual(output, ["true", "true", "true"])


if __name__ == "__main__":
    unittest.main()
