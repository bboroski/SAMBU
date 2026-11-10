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

    def test_section_headers_and_repeated_chorus_are_extracted(self):
        _, output = self.run_sambu("""
let draft = "[Verse 1]\\nПишу короткий первый фрагмент\\n[Chorus]\\nОдин мотив возвращается\\n[Verse 2]\\nДругой короткий фрагмент\\n[Припев]\\nОдин мотив возвращается"
let structure = text_structure_profile(draft)
print(structure.header_count)
print(structure.section_count)
print(structure.section_kind_counts.chorus)
print(structure.refrain_groups[0].repeat_count)
print(structure.refrain_groups[0].line_count)
""")
        self.assertEqual(output, ["4", "4", "2", "2", "1"])

    def test_multilingual_writing_systems_and_code_switching(self):
        _, output = self.run_sambu("""
let draft = "Пишу українською today\\nEnglish remains\\nТекст повертається"
let mix = language_mix_profile(draft)
print(mix.cyrillic_word_count)
print(mix.latin_word_count)
print(mix.code_switch_line_count)
print(mix.code_switch_lines[0])
print(mix.dominant_script)
""")
        self.assertEqual(output, ["4", "3", "1", "1", "cyrillic"])

    def test_marked_case_is_preserved_as_an_author_cue(self):
        _, output = self.run_sambu("""
let draft = "Ветер разбудит вОды"
let sound = prosody_profile(draft)
print(sound.marked_case_words[0])
print(sound.marked_case_word_count)
""")
        self.assertEqual(output, ["вОды", "1"])

    def test_internal_rhyme_echoes_are_reported(self):
        _, output = self.run_sambu("""
let draft = "Пора и гора звучат в строке"
let sound = prosody_profile(draft)
print(sound.internal_rhyme_line_count)
print(sound.internal_rhyme_density)
print(sound.lines[0].internal_rhyme_groups[0].key)
""")
        self.assertEqual(output, ["1", "1", "ора"])

    def test_empty_text_is_safe(self):
        _, output = self.run_sambu("""
let words = text_profile("")
let sound = prosody_profile("")
let structure = text_structure_profile("")
let mix = language_mix_profile("")
print(words.word_count)
print(sound.rhyme_density)
print(syllables(""))
print(rhyme_key("---"))
print(structure.section_count)
print(mix.word_count)
""")
        self.assertEqual(output, ["0", "0", "0", "", "0", "0"])

    def test_text_builtins_validate_arguments(self):
        with self.assertRaises(TypeError):
            execute("text_profile(42)")
        with self.assertRaises(TypeError):
            execute('syllables("one", "two")')
        with self.assertRaises(TypeError):
            execute("language_mix_profile(42)")

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
