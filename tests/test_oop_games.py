from __future__ import annotations

import unittest

from sambu import execute
from sambu.runtime import SambuRuntimeError


class ObjectOrientedLanguageTests(unittest.TestCase):
    def test_constructor_fields_methods_inheritance_and_override(self):
        output: list[str] = []
        execute(
            "class Animal { "
            "fn init(self, name) { self.name = name } "
            "fn speak(self) { return self.name + ' makes a sound' } "
            "} "
            "class Dog extends Animal { "
            "fn speak(self) { return self.name + ' barks' } "
            "} "
            "let pet = Dog('Rex') "
            "print(pet.speak())",
            output=output.append,
        )
        self.assertEqual(output, ["Rex barks"])

    def test_inherited_method_and_mutable_instance_fields(self):
        output: list[str] = []
        execute(
            "class Counter { "
            "fn init(self, start) { self.value = start } "
            "fn increment(self) { self.value = self.value + 1; return self.value } "
            "} "
            "let counter = Counter(4) "
            "counter.increment() "
            "print(counter.value)",
            output=output.append,
        )
        self.assertEqual(output, ["5"])

    def test_method_requires_explicit_self_parameter(self):
        with self.assertRaises(SambuRuntimeError):
            execute("class Broken { fn method() { return 1 } }")

    def test_invalid_base_class_is_rejected(self):
        with self.assertRaises(SambuRuntimeError):
            execute("let value = 1 class Broken extends value { fn init(self) { } }")

    def test_constructor_arity_is_checked(self):
        with self.assertRaises(TypeError):
            execute("class Empty { } let value = Empty(1)")


class BuiltInGameTests(unittest.TestCase):
    def test_rock_paper_scissors_rules(self):
        output: list[str] = []
        execute(
            "let result = rps_round('rock', 'scissors') "
            "let tie = rps_round('paper', 'paper') "
            "print(result.outcome) print(result.winner) print(tie.outcome)",
            output=output.append,
        )
        self.assertEqual(output, ["win", "player", "draw"])

    def test_rock_paper_scissors_rejects_unknown_move(self):
        with self.assertRaises(ValueError):
            execute("rps_round('rock', 'lizard')")

    def test_tic_tac_toe_turns_and_win(self):
        output: list[str] = []
        execute(
            "let empty = ['.', '.', '.', '.', '.', '.', '.', '.', '.'] "
            "let one = tic_tac_toe_move(empty, 'X', 0) "
            "let two = tic_tac_toe_move(one.board, 'O', 3) "
            "let three = tic_tac_toe_move(two.board, 'X', 1) "
            "let four = tic_tac_toe_move(three.board, 'O', 4) "
            "let five = tic_tac_toe_move(four.board, 'X', 2) "
            "print(five.status) print(five.winner) print(five.moves_remaining)",
            output=output.append,
        )
        self.assertEqual(output, ["won", "X", "4"])

    def test_tic_tac_toe_rejects_illegal_turn_and_occupied_cell(self):
        with self.assertRaises(ValueError):
            execute("tic_tac_toe_move(['.', '.', '.', '.', '.', '.', '.', '.', '.'], 'O', 0)")
        with self.assertRaises(ValueError):
            execute("tic_tac_toe_move(['X', '.', '.', '.', '.', '.', '.', '.', '.'], 'O', 0)")

    def test_tic_tac_toe_rejects_unreachable_boards(self):
        with self.assertRaises(ValueError):
            execute("tic_tac_toe_state(['O', '.', '.', '.', '.', '.', '.', '.', '.'])")
        with self.assertRaises(ValueError):
            execute("tic_tac_toe_state(['X', 'X', 'X', 'O', 'O', 'O', '.', '.', '.'])")


if __name__ == "__main__":
    unittest.main()
