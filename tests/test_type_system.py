from __future__ import annotations

import unittest

from sambu import SambuTypeError, check_source, execute, parse, parse_ast
from sambu.ast import FunctionStatement, LetStatement


class SambuGradualTypeTests(unittest.TestCase):
    def test_unannotated_program_keeps_legacy_tuple_ast(self):
        source = "let count = 3\nfn double(value) { return value * 2 }"
        self.assertEqual(parse_ast(source).to_legacy(), parse(source))
        self.assertEqual(len(parse(source)[0]), 3)
        self.assertEqual(len(parse(source)[1]), 4)

    def test_binding_and_function_annotations_are_preserved(self):
        source = (
            "let items: Array<Number> = [1, 2]\n"
            "fn total(values: Array<Number>, scale: Number) -> Number { "
            "return sum(values) * scale }"
        )
        program = parse_ast(source)
        binding, function = program.statements
        self.assertIsInstance(binding, LetStatement)
        self.assertEqual(binding.type_annotation, "Array<Number>")
        self.assertIsInstance(function, FunctionStatement)
        self.assertEqual(function.parameter_types, ("Array<Number>", "Number"))
        self.assertEqual(function.return_type, "Number")
        legacy = program.to_legacy()
        self.assertEqual(legacy[0][3], {"type": "Array<Number>"})
        self.assertEqual(legacy[1][4]["parameter_types"], {
            "values": "Array<Number>",
            "scale": "Number",
        })
        self.assertEqual(legacy[1][4]["return_type"], "Number")

    def test_static_checker_accepts_well_typed_subset(self):
        source = """
let samples: Array<Number> = [1, 2, 3]
fn average(values: Array<Number>) -> Number {
    return sum(values) / count(values)
}
let result: Number = average(samples)
"""
        self.assertEqual(check_source(source), ())

    def test_static_checker_reports_binding_and_call_mismatches(self):
        source = """
fn greet(name: String) -> String {
    return name
}
let invalid: Number = greet(42)
"""
        messages = [item.message for item in check_source(source)]
        self.assertTrue(any("argument 1 of greet expects String" in item for item in messages))
        self.assertTrue(any("binding 'invalid' expects Number" in item for item in messages))

    def test_unknown_annotations_are_reported(self):
        diagnostics = check_source("let value: MissingType = 1")
        self.assertTrue(any(item.code == "SAMBU-T002" for item in diagnostics))
        self.assertTrue(any("unknown type 'MissingType'" in item.message for item in diagnostics))

    def test_runtime_checks_typed_bindings(self):
        execute("let values: Array<Number> = [1, 2, 3]")
        with self.assertRaises(SambuTypeError):
            execute('let values: Array<Number> = [1, "two"]')

    def test_runtime_checks_function_arguments_and_returns(self):
        execute("fn repeat(value: String) -> String { return value }\nrepeat(\"ok\")")
        with self.assertRaises(SambuTypeError):
            execute("fn repeat(value: String) -> String { return value }\nrepeat(7)")
        with self.assertRaises(SambuTypeError):
            execute('fn invalid() -> Number { return "not a number" }\ninvalid()')

    def test_custom_class_annotations_are_runtime_checked(self):
        execute("""
class Counter {
    fn init(self, start) { self.value = start }
}
let counter: Counter = Counter(4)
""")
        with self.assertRaises(SambuTypeError):
            execute("class Counter { fn init(self) { } }\nlet counter: Counter = 4")

    def test_interface_method_type_contracts_are_preserved(self):
        execute("""
interface Greeter {
    fn greet(self, name: String) -> String
}
class Friendly implements Greeter {
    fn greet(self, name: String) -> String { return name }
}
let greeter = Friendly()
greeter.greet("hello")
""")
        with self.assertRaises(Exception):
            execute("""
interface Greeter {
    fn greet(self, name: String) -> String
}
class Broken implements Greeter {
    fn greet(self, name: Number) -> Number { return name }
}
""")

    def test_trait_method_annotations_survive_composition(self):
        execute("""
trait Printable {
    fn render(self, value: String) -> String { return value }
}
class Label uses Printable {
}
let label = Label()
label.render("SAMBU")
""")

    def test_unary_expression_statements_remain_valid_at_block_start(self):
        source = "fn negate(value: Number) -> Number {\n  -value\n  return -value\n}"
        program = parse_ast(source)
        self.assertEqual(len(program.statements[0].body), 2)


if __name__ == "__main__":
    unittest.main()
