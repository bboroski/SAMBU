import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from sambu import analyze
from sambu.parser import parse_ast
from sambu.semantics import analyze_ast
from sambu.cli import main as sambu_main


class SemanticAnalysisTests(unittest.TestCase):
    def test_valid_program_with_functions_scopes_and_builtins(self):
        source = """
let scale = 2
fn twice(value) {
    return value * scale
}
let values = [twice(2), twice(3)]
print(sum(values))
"""
        report = analyze(source)
        self.assertTrue(report.valid, report.to_dict())
        self.assertEqual(report.diagnostics, ())

    def test_unknown_value_has_stable_source_ranged_diagnostic(self):
        report = analyze("let answer = missing + 1")
        self.assertFalse(report.valid)
        diagnostic = report.diagnostics[0]
        self.assertEqual(diagnostic.code, "SAMBU-SEM-001")
        self.assertEqual(diagnostic.span.start.line, 1)
        self.assertEqual(diagnostic.span.start.column, 14)
        self.assertGreater(diagnostic.span.end.offset, diagnostic.span.start.offset)

    def test_duplicate_local_binding_is_reported(self):
        report = analyze("let item = 1\nlet item = 2")
        self.assertEqual(
            [item.code for item in report.diagnostics],
            ["SAMBU-SEM-002"],
        )

    def test_function_arity_is_checked_before_execution(self):
        report = analyze("fn add(a, b) { return a + b }\nlet value = add(1)")
        self.assertIn("SAMBU-SEM-007", [item.code for item in report.diagnostics])

    def test_return_outside_function_is_rejected(self):
        report = analyze("return 42")
        self.assertIn("SAMBU-SEM-003", [item.code for item in report.diagnostics])

    def test_definite_primitive_type_error_is_reported(self):
        report = analyze('let invalid = 1 + "two"')
        self.assertIn("SAMBU-SEM-004", [item.code for item in report.diagnostics])

    def test_dynamic_method_calls_and_unknown_return_types_are_allowed(self):
        source = """
class Counter {
    fn init(self, start) { self.value = start }
    fn get(self) { return self.value }
}
let counter = Counter(1)
let result = counter.get()
"""
        report = analyze(source)
        self.assertTrue(report.valid, report.to_dict())

    def test_cli_check_reports_json_without_executing_source(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "sample.sambu"
            path.write_text("let answer = unknown_value\\nprint(answer)\\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                exit_code = sambu_main(["check", str(path), "--json"])
        self.assertEqual(exit_code, 1)
        self.assertIn("SAMBU-SEM-001", output.getvalue())
        self.assertIn("unknown_value", output.getvalue())

    def test_ast_api_does_not_require_source_reparsing(self):
        report = analyze_ast(parse_ast("let answer = 42"))
        self.assertTrue(report.valid)
        self.assertEqual(report.declarations, 1)


if __name__ == "__main__":
    unittest.main()
