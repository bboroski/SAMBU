from __future__ import annotations
import unittest
from sambu.interpreter import execute

class PercentageSyntaxTests(unittest.TestCase):
    def run_sambu(self, source: str) -> list[str]:
        output=[]
        execute(source, output=output.append)
        return output
    def test_postfix_percent_literal(self):
        self.assertEqual(self.run_sambu("print(15%)"), ["0.15"])
        self.assertEqual(self.run_sambu("print((25 + 5)%)"), ["0.3"])
    def test_spaced_percent_is_modulo(self):
        self.assertEqual(self.run_sambu("print(10 % 3)"), ["1"])
    def test_percentage_builtins(self):
        output=self.run_sambu(
            "print(percent_of(240, 12.5))\n"
            "print(apply_percent(200, 10))\n"
            "print(reduce_by_percent(200, 25))\n"
            "print(percentage(30, 120))\n"
            "print(percent_change(80, 100))\n"
            "print(percent_to_ratio(15))\n"
            "print(ratio_to_percent(0.15))\n"
            "print(percentage_points(18, 12.5))\n"
            "print(clamp_percent(120))"
        )
        self.assertEqual(output, ["30","220","150","25","25","0.15","15","5.5","100"])
    def test_invalid_denominators_and_discount(self):
        with self.assertRaises(ZeroDivisionError): execute("percentage(1, 0)")
        with self.assertRaises(ZeroDivisionError): execute("percent_change(0, 1)")
        with self.assertRaises(ValueError): execute("reduce_by_percent(100, 101)")
    def test_percent_operator_rejects_dimensions(self):
        with self.assertRaises((TypeError, ValueError)): execute("print((1 * m) % 2)")

if __name__ == "__main__": unittest.main()
