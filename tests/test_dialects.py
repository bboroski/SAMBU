from __future__ import annotations

import unittest
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory

from sambu.dialects import DialectSyntaxError, execute_dialect, transpile
from sambu.parser import parse_ast
from sambu.cli import main as sambu_main


class PascalDialectTests(unittest.TestCase):
    def test_typed_declarations_functions_and_output_translate_and_execute(self):
        source = """
program Invoice;
function doubled(value: real): real;
begin
  doubled := value * 2;
end;
var amount: real;
begin
  amount := 21;
  writeln(doubled(amount));
  writeln(300 * K);
end.
"""
        output: list[str] = []
        result = execute_dialect(source, "pascal", output=output.append)
        self.assertEqual(str(result), "300 K")  # final unit-valued expression
        self.assertEqual(output, ["42", "300 K"])

    def test_inclusive_counted_loop_is_translated(self):
        source = """
program Squares;
begin
  for index := 1 to 3 do
  begin
    writeln(index * index);
  end;
end.
"""
        result = transpile(source, "pascal")
        parse_ast(result.generated_source)
        self.assertIn("range(1, (3) + 1)", result.generated_source)

    def test_immutable_bindings_reject_reassignment(self):
        source = """
program Invalid;
var amount: real;
begin
  amount := 10;
  amount := 20;
end.
"""
        with self.assertRaises(DialectSyntaxError):
            transpile(source, "pascal")


class DefaultOutputDialectTests(unittest.TestCase):
    def test_execute_dialect_uses_print_when_no_callback_is_supplied(self):
        source = "program OutputDemo;\nbegin\n  writeln(42);\nend."
        captured = StringIO()
        with redirect_stdout(captured):
            execute_dialect(source, "pascal")
        self.assertEqual(captured.getvalue(), "42\n")


class DelphiDialectTests(unittest.TestCase):
    def test_object_pascal_function_and_actor_builtins_work(self):
        source = """
program ActorDemo;
function accumulate(state: real; message: real): real;
begin
  accumulate := state + message;
end;
var worker: actor_ref;
begin
  worker := actor(accumulate, 0, 8);
  actor_send(worker, 5);
  actor_send(worker, 7);
  actor_drain(worker, 2);
  writeln(actor_state(worker));
end.
"""
        output: list[str] = []
        execute_dialect(source, "delphi", output=output.append)
        self.assertEqual(output, ["12"])

    def test_aliases_accept_object_pascal_name(self):
        source = "program Demo;\nbegin\n  writeln(1);\nend."
        result = transpile(source, "object pascal")
        self.assertEqual(result.dialect, "delphi")


class DialectCliTests(unittest.TestCase):
    def test_cli_check_and_show_translated_modes(self):
        source = "program CliDemo;\nbegin\n  writeln(42);\nend."
        with TemporaryDirectory() as directory:
            path = Path(directory) / "demo.pas"
            path.write_text(source, encoding="utf-8")

            checked = StringIO()
            with redirect_stdout(checked):
                self.assertEqual(
                    sambu_main(["dialect", "pascal", str(path), "--check"]),
                    0,
                )
            self.assertIn("syntax OK", checked.getvalue())

            translated = StringIO()
            with redirect_stdout(translated):
                self.assertEqual(
                    sambu_main(["dialect", "pascal", str(path), "--show-translated"]),
                    0,
                )
            self.assertIn("print(42)", translated.getvalue())


class FortranDialectTests(unittest.TestCase):
    def test_program_declarations_do_loop_and_logical_operators(self):
        source = """
program LoopDemo
implicit none
integer :: limit
limit = 3
do index = 1, limit
  print *, index ** 2
end do
if (limit .gt. 2 .and. .true.) then
  print *, .true.
else
  print *, .false.
end if
end program LoopDemo
"""
        output: list[str] = []
        execute_dialect(source, "fortran", output=output.append)
        self.assertEqual(output, ["1", "4", "9", "true"])

    def test_si_unit_symbol_case_is_preserved(self):
        source = """
program Energy
implicit none
real :: temperature
real :: energy
temperature = 300 * K
energy = 1e-21 * J
print *, energy
end program Energy
"""
        result = transpile(source, "fortran")
        self.assertIn("300 * K", result.generated_source)
        self.assertIn("1e-21 * J", result.generated_source)
        parse_ast(result.generated_source)

    def test_unsupported_mutation_and_constructs_fail_closed(self):
        source = """
program Invalid
integer :: value
value = 1
value = 2
end program Invalid
"""
        with self.assertRaises(DialectSyntaxError):
            transpile(source, "fortran")
        with self.assertRaises(DialectSyntaxError):
            transpile("program Bad\nwhile (x)\nend program Bad", "fortran")


if __name__ == "__main__":
    unittest.main()
