from __future__ import annotations

import unittest

from sambu import (
    BinaryExpr,
    CallExpr,
    ClassStatement,
    ExpressionStatement,
    FieldExpr,
    ForStatement,
    FunctionStatement,
    IfStatement,
    LetStatement,
    NameExpr,
    SetFieldStatement,
    parse,
    parse_ast,
)
from sambu.lexer import SambuSyntaxError


class TypedAstTests(unittest.TestCase):
    def test_parse_keeps_the_legacy_tuple_shape(self):
        source = "let x = 2 + 3\nprint(x)"
        self.assertEqual(
            parse(source),
            [
                ("let", "x", ("binary", "+", ("literal", 2.0), ("literal", 3.0))),
                ("expr", ("call", ("name", "print"), [("name", "x")])),
            ],
        )
        self.assertEqual(parse_ast(source).to_legacy(), parse(source))

    def test_expression_and_statement_spans_include_parentheses_and_calls(self):
        source = "let café = (2 + 3)\nprint(café)"
        program = parse_ast(source)
        declaration = program.statements[0]
        output = program.statements[1]

        self.assertIsInstance(declaration, LetStatement)
        self.assertIsInstance(declaration.value, BinaryExpr)
        self.assertEqual(source[declaration.span.start.offset:declaration.span.end.offset],
                         "let café = (2 + 3)")
        self.assertEqual(source[declaration.value.span.start.offset:declaration.value.span.end.offset],
                         "(2 + 3)")
        self.assertEqual(source[output.span.start.offset:output.span.end.offset],
                         "print(café)")
        self.assertIsInstance(output.expression, CallExpr)
        self.assertIsInstance(output.expression.callee, NameExpr)
        self.assertEqual(program.span.start.offset, 0)
        self.assertEqual(program.span.end.offset, len(source))

    def test_nested_statement_spans_cover_complete_blocks(self):
        source = (
            "fn square(x) { return x * x }\n"
            "if (true) { let y = square(2) } else { print(\"no\") }\n"
            "for item in [1, 2] { print(item) }"
        )
        program = parse_ast(source)
        function, conditional, loop = program.statements

        self.assertIsInstance(function, FunctionStatement)
        self.assertIsInstance(conditional, IfStatement)
        self.assertIsInstance(loop, ForStatement)
        expected = source.splitlines()
        for node, source_line in zip(program.statements, expected):
            self.assertEqual(
                source[node.span.start.offset:node.span.end.offset],
                source_line,
            )
        self.assertEqual(len(conditional.then_body), 1)
        self.assertEqual(len(conditional.else_body), 1)

    def test_unary_expression_statements_are_parsed_inside_all_block_kinds(self):
        source = (
            "fn unary_function() {\\n"
            "  -1\\n"
            "}\\n"
            "if true {\\n"
            "  !false\\n"
            "}\\n"
            "for item in [1] {\\n"
            "  +item\\n"
            "}"
        )
        function, conditional, loop = parse_ast(source).statements

        for statement, operator in (
            (function.body[0], "-"),
            (conditional.then_body[0], "!"),
            (loop.body[0], "+"),
        ):
            self.assertIsInstance(statement, ExpressionStatement)
            self.assertIsInstance(statement.expression, UnaryExpr)
            self.assertEqual(statement.expression.operator, operator)

    def test_postfix_field_and_index_spans_are_end_exclusive(self):
        source = "let result = stats.rms[0]"
        declaration = parse_ast(source).statements[0]
        self.assertIsInstance(declaration, LetStatement)
        expression = declaration.value
        self.assertEqual(source[expression.span.start.offset:expression.span.end.offset],
                         "stats.rms[0]")
        self.assertEqual(expression.index.span.start.offset, len(source) - 2)
        self.assertEqual(expression.index.span.end.offset, len(source) - 1)
        self.assertIsInstance(expression.target, FieldExpr)


    def test_class_and_field_assignment_have_typed_spans_and_legacy_form(self):
        source = """class Counter {
  fn init(self, start) { self.value = start }
  fn read(self) { return self.value }
}
let counter = Counter(3)"""
        program = parse_ast(source)
        declaration = program.statements[0]
        self.assertIsInstance(declaration, ClassStatement)
        self.assertEqual(
            source[declaration.span.start.offset:declaration.span.end.offset],
            """class Counter {
  fn init(self, start) { self.value = start }
  fn read(self) { return self.value }
}""",
        )
        assignment = declaration.methods[0].body[0]
        self.assertIsInstance(assignment, SetFieldStatement)
        self.assertEqual(
            source[assignment.span.start.offset:assignment.span.end.offset],
            "self.value = start",
        )
        self.assertEqual(program.to_legacy(), parse(source))

    def test_program_span_includes_leading_and_trailing_trivia(self):
        source = "\n  let x = 1\n"
        program = parse_ast(source)
        self.assertEqual(program.span.start.offset, 0)
        self.assertEqual(program.span.end.offset, len(source))
        statement = program.statements[0]
        self.assertEqual(source[statement.span.start.offset:statement.span.end.offset],
                         "let x = 1")

    def test_empty_program_has_an_eof_point_span(self):
        program = parse_ast("")
        self.assertEqual(program.statements, ())
        self.assertTrue(program.span.is_empty)
        self.assertEqual(program.span.start.offset, 0)

    def test_missing_expression_reports_the_actual_eof_position(self):
        source = "let x ="
        with self.assertRaises(SambuSyntaxError) as caught:
            parse(source)

        error = caught.exception
        self.assertEqual(error.code, "SAMBU-P001")
        self.assertEqual(error.span.start.offset, len(source))
        self.assertEqual((error.line, error.column), (1, len(source) + 1))


if __name__ == "__main__":
    unittest.main()
