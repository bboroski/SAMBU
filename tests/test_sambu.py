from __future__ import annotations

import math
import unittest

from sambu.interpreter import execute
from sambu.lexer import SambuSyntaxError
from sambu.runtime import SambuRuntimeError


class SambuTests(unittest.TestCase):
    def run_sambu(self, source: str):
        output: list[str] = []
        result = execute(source, output=output.append)
        return result, output

    def test_arithmetic_and_variables(self):
        result, out = self.run_sambu("let x = 2 + 3 * 4\nprint(x)")
        self.assertEqual(result, 14.0)
        self.assertEqual(out, ["14"])

    def test_units_and_dimension_check(self):
        _, out = self.run_sambu("let energy = 1.5 * k_B * (300 * K)\nprint(energy)")
        self.assertIn("J", out[0])
        self.assertNotEqual(out[0], "0 J")
        with self.assertRaises(ValueError):
            execute("let impossible = (1 * m) + (1 * s)")

    def test_maxwell_distribution(self):
        _, out = self.run_sambu(
            "let stats = maxwell(300 * K, 6.6335209e-26 * kg)\nprint(stats.rms)"
        )
        self.assertTrue(out[0].endswith("m/s"))
        self.assertGreater(float(out[0].split()[0]), 0.0)

    def test_boltzmann_factor(self):
        _, out = self.run_sambu("print(boltzmann(0 * J, 300 * K))")
        self.assertEqual(out, ["1"])

    def test_deterministic_sampling(self):
        _, out1 = self.run_sambu(
            "let xs = sample_maxwell(300 * K, 6.6e-26 * kg, 4, 42)\nprint(xs)"
        )
        _, out2 = self.run_sambu(
            "let xs = sample_maxwell(300 * K, 6.6e-26 * kg, 4, 42)\nprint(xs)"
        )
        self.assertEqual(out1, out2)

    def test_partition_and_entropy(self):
        _, out = self.run_sambu(
            "let z = partition([0 * J, 1e-21 * J], 300 * K)\n"
            "print(z)\nprint(entropy([0.5, 0.5]))"
        )
        self.assertGreater(float(out[0]), 1.0)
        self.assertAlmostEqual(float(out[1]), math.log(2), places=7)

    def test_duplicate_binding_is_rejected(self):
        with self.assertRaises(SambuRuntimeError):
            execute("let x = 1\nlet x = 2")

    def test_syntax_error(self):
        with self.assertRaises(SambuSyntaxError):
            execute("let x = (2 + 3")


if __name__ == "__main__":
    unittest.main()
