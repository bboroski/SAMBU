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
let draft = "Сервер проверяет входные данные\\nКлиент сохраняет результат"
let words = text_profile(draft)
let sound = prosody_profile(draft)
print(words.line_count)
print(words.word_count)
print(words.unique_word_count)
print(words.lexical_diversity)
print(sound.nonempty_line_count)
""")
        self.assertEqual(output, ["2", "7", "7", "1", "2"])

    def test_alliteration_is_reported_without_rewriting_text(self):
        _, output = self.run_sambu("""
let draft = "Модуль моделирует массив"
let sound = prosody_profile(draft)
print(sound.lines[0].has_alliteration)
print(sound.alliterative_line_count)
""")
        self.assertEqual(output, ["true", "1"])

    def test_section_headers_and_repeated_chorus_are_extracted(self):
        _, output = self.run_sambu("""
let draft = "[Verse 1]\\nНастройки профиля доступны\\n[Chorus]\\nSystem status is ready\\n[Verse 2]\\nThe client stores the result\\n[Припев]\\nSystem status is ready"
let structure = text_structure_profile(draft)
print(structure.header_count)
print(structure.section_count)
print(structure.section_kind_counts.chorus)
print(structure.refrain_groups[0].repeat_count)
print(structure.refrain_groups[0].line_count)
""")
        self.assertEqual(output, ["4", "4", "2", "2", "1"])

    def test_colon_and_parenthesized_section_labels_are_normalized(self):
        _, output = self.run_sambu("""
let draft = "[Verse:]\\nThe request is received\\n[Spoken Chorus:]\\nSystem status is ready\\n[Chorus:]\\nSystem status is ready\\n(Verse 2)\\nThe client stores the result"
let structure = text_structure_profile(draft)
print(structure.section_kind_counts.verse)
print(structure.section_kind_counts.chorus)
print(structure.refrain_groups[0].repeat_count)
print(structure.sections[1].performance_hint)
""")
        self.assertEqual(output, ["2", "2", "2", "spoken"])

    def test_explicit_performance_cues_are_extracted_without_inference(self):
        _, output = self.run_sambu("""
let draft = "*Display turns on*\\n(status: ready)\\nThe operator says \\"Open settings\\"\\npre-pre-processing"
let cues = performance_cues_profile(draft)
print(cues.stage_direction_count)
print(cues.parenthetical_aside_count)
print(cues.quoted_phrase_count)
print(cues.elongated_spelling_count)
print(cues.markers[0].kind)
print(cues.markers[0].line_number)
print(cues.scope)
""")
        self.assertEqual(output, [
            "1", "1", "1", "1", "stage_direction", "1",
            "explicit_written_cues_not_performance_or_emotion_inference",
        ])

    def test_multilingual_writing_systems_and_code_switching(self):
        _, output = self.run_sambu("""
let draft = "Параметры доступны today\\nEnglish labels\\nСистема готова"
let mix = language_mix_profile(draft)
print(mix.cyrillic_word_count)
print(mix.latin_word_count)
print(mix.code_switch_line_count)
print(mix.code_switch_lines[0])
print(mix.dominant_script)
""")
        self.assertEqual(output, ["4", "3", "1", "1", "cyrillic"])

    def test_han_and_latin_romanization_are_counted_as_scripts_not_languages(self):
        _, output = self.run_sambu("""
let draft = "清晨 qīng\\n朝日"
let mix = language_mix_profile(draft)
print(mix.script_character_counts.han)
print(mix.script_character_counts.latin)
print(mix.script_word_counts.han)
print(mix.script_word_counts.latin)
print(mix.multi_script_line_count)
print(mix.multi_script_lines[0])
print(mix.dominant_unicode_script)
print(mix.language_identification)
""")
        self.assertEqual(
            output,
            ["4", "4", "2", "1", "1", "1", "balanced", "not_performed"],
        )

    def test_japanese_and_korean_scripts_are_distinguished(self):
        _, output = self.run_sambu("""
let mix = language_mix_profile("漢字 かな カナ 한글")
print(mix.script_character_counts.han)
print(mix.script_character_counts.hiragana)
print(mix.script_character_counts.katakana)
print(mix.script_character_counts.hangul)
print(mix.multi_script_line_count)
""")
        self.assertEqual(output, ["2", "2", "2", "2", "1"])

    def test_marked_case_is_preserved_as_an_author_cue(self):
        _, output = self.run_sambu("""
let draft = "Server keeps staTUS"
let sound = prosody_profile(draft)
print(sound.marked_case_words[0])
print(sound.marked_case_word_count)
""")
        self.assertEqual(output, ["staTUS", "1"])

    def test_internal_rhyme_echoes_are_reported(self):
        _, output = self.run_sambu("""
let draft = "Код и вход проверяются"
let sound = prosody_profile(draft)
print(sound.internal_rhyme_line_count)
print(sound.internal_rhyme_density)
print(sound.lines[0].internal_rhyme_groups[0].key)
""")
        self.assertEqual(output, ["1", "1", "од"])

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
        with self.assertRaises(TypeError):
            execute("performance_cues_profile(42)")

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
