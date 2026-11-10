from __future__ import annotations

import unittest

from sambu.interpreter import execute


class HookCraftTests(unittest.TestCase):
    def test_compact_hook_reports_structure_without_claiming_quality(self):
        output: list[str] = []
        execute("""
let hook = hook_profile("Город хранит разговор\\nНочь приносит приговор\\nГород хранит разговор\\nНочь меняет декор")
print(hook.line_count)
print(hook.within_compact_range)
print(hook.end_rhyme_density)
print(hook.repeated_line_groups[0].repeat_count)
print(hook.scope)
""", output=output.append)
        self.assertEqual(output[:2], ["4", "true"])
        self.assertEqual(output[2], "1")
        self.assertEqual(output[3], "2")
        self.assertIn("textual_heuristics", output[4])

    def test_empty_and_oversized_hooks_receive_explicit_warning(self):
        output: list[str] = []
        execute("""
let hook = hook_profile("Одна строка")
print(hook.line_count)
print(hook.within_compact_range)
print(hook.warnings[0])
""", output=output.append)
        self.assertEqual(
            output,
            ["1", "false", "HOOK_OUTSIDE_COMPACT_2_TO_4_LINE_RANGE"],
        )


if __name__ == "__main__":
    unittest.main()
