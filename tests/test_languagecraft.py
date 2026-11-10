from __future__ import annotations

import unittest

from sambu.interpreter import execute


class LanguageCraftTests(unittest.TestCase):
    def run_sambu(self, source: str):
        output: list[str] = []
        result = execute(source, output=output.append)
        return result, output

    def test_complete_source_to_grammar_pipeline(self):
        _, output = self.run_sambu("""
let source = craft_source(
  "core-seed", "declaration grammar", "original design", "author-created examples",
  ["binding", "name", "assignment mark", "numeric expression"]
)
let cut = craft_cut(source, ["binding", "name", "assignment mark", "numeric expression"])
let let_token = craft_token(cut, "binding", "LET", "let", "immutable binding", "keyword")
let name_token = craft_token(cut, "name", "IDENT", "name", "identifier", "identifier")
let assign_token = craft_token(cut, "assignment mark", "ASSIGN", "=", "assignment operator", "operator")
let number_token = craft_token(cut, "numeric expression", "NUMBER", "number", "numeric literal", "literal")
let program_rule = craft_rule("Program", ["Statement"])
let statement_rule = craft_rule("Statement", ["$LET", "$IDENT", "$ASSIGN", "$NUMBER"])
let blueprint = craft_assemble(
  "Seed Language", [source],
  [let_token, name_token, assign_token, number_token],
  [program_rule, statement_rule],
  "Program"
)
let report = craft_master(blueprint)
print(report.status)
print(report.ready)
print(report.token_count)
print(report.production_count)
print(report.grammar_reachability)
print(report.token_coverage)
print(report.source_coverage)
""")
        self.assertEqual(output, ["ready", "true", "4", "2", "1", "1", "1"])

    def test_missing_terminal_reference_blocks_readiness(self):
        _, output = self.run_sambu("""
let source = craft_source("seed", "grammar", "original", "author-created", ["statement"])
let cut = craft_cut(source, ["statement"])
let token = craft_token(cut, "statement", "IDENT", "name", "identifier", "identifier")
let rule = craft_rule("Program", ["$MISSING"])
let blueprint = craft_assemble("Broken", [source], [token], [rule], "Program")
let report = craft_master(blueprint)
print(report.ready)
print(report.status)
print(report.error_count)
print(report.errors[0])
""")
        self.assertEqual(output, ["false", "blocked", "1", "LC007 undefined terminal reference: $MISSING"])

    def test_unused_rules_and_tokens_are_warnings_not_silent_success(self):
        _, output = self.run_sambu("""
let source = craft_source("seed", "grammar", "original", "author-created", ["statement", "unused"])
let cut = craft_cut(source, ["statement", "unused"])
let used = craft_token(cut, "statement", "IDENT", "name", "identifier", "identifier")
let unused = craft_token(cut, "unused", "UNUSED", "unused", "unused word", "keyword")
let program = craft_rule("Program", ["$IDENT"])
let orphan = craft_rule("Orphan", [])
let blueprint = craft_assemble("Draft", [source], [used, unused], [program, orphan], "Program")
let report = craft_master(blueprint)
print(report.ready)
print(report.status)
print(report.warning_count)
print(report.grammar_reachability)
print(report.token_coverage)
""")
        self.assertEqual(output, ["true", "ready_with_warnings", "3", "0.5", "0.5"])

    def test_duplicate_lexemes_are_reported_as_collisions(self):
        _, output = self.run_sambu("""
let source = craft_source("seed", "grammar", "original", "author-created", ["first", "second"])
let cut = craft_cut(source, ["first", "second"])
let first = craft_token(cut, "first", "FIRST", "name", "first name", "identifier")
let second = craft_token(cut, "second", "SECOND", "name", "second name", "identifier")
let rule = craft_rule("Program", ["$FIRST", "$SECOND"])
let blueprint = craft_assemble("Collision", [source], [first, second], [rule], "Program")
let report = craft_master(blueprint)
print(report.ready)
print(report.errors[0])
""")
        self.assertEqual(output, ["false", "LC005 duplicate lexeme 'name': FIRST and SECOND"])

    def test_source_and_cut_reject_invalid_material(self):
        with self.assertRaises(ValueError):
            execute('craft_source("seed", "grammar", "original", "note", ["same", "same"])')
        with self.assertRaises(ValueError):
            execute('let source = craft_source("seed", "grammar", "original", "note", ["known"])\ncraft_cut(source, ["missing"])')
        with self.assertRaises(ValueError):
            execute('let source = craft_source("seed", "grammar", "original", "note", ["known"])\nlet cut = craft_cut(source, ["known"])\ncraft_token(cut, "known", "BAD", "two words", "bad", "keyword")')

    def test_rule_accepts_epsilon_but_rejects_malformed_terminal(self):
        _, output = self.run_sambu("""
let empty = craft_rule("Optional", [])
print(empty.lhs)
print(empty.rhs)
""")
        self.assertEqual(output, ["Optional", "[]"])
        with self.assertRaises(ValueError):
            execute('craft_rule("Program", ["$lowercase"])')


if __name__ == "__main__":
    unittest.main()
