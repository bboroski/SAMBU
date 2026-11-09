from __future__ import annotations
import unittest
from sambu.interpreter import execute

class AnatidaeModelTests(unittest.TestCase):
    def run_sambu(self, source: str) -> list[str]:
        output=[]
        execute(source, output=output.append)
        return output
    def test_countercurrent_exchange_uses_supplied_efficiency(self):
        out=self.run_sambu(
            "let x = countercurrent_exchange(310 * K, 280 * K, 75%)\n"
            "print(x.venous_return)\nprint(x.arterial_outlet)"
        )
        self.assertEqual(out,["302.5 K","287.5 K"])
    def test_plumage_model_is_dimensionless_and_configurable(self):
        out=self.run_sambu("let p = plumage_insulation(0.9, 25%, 10%)\nprint(p.effective_index)")
        self.assertEqual(out,["0.6075"])
    def test_flight_energy_budget_respects_units(self):
        out=self.run_sambu(
            "let f = flight_energy_budget((10 * J) / (1 * s), 5 * s, 60 * J)\n"
            "print(f.energy_required)\nprint(f.energy_remaining)\nprint(f.is_sufficient)"
        )
        self.assertEqual(out,["50 J","10 J","true"])
    def test_migration_speed_and_pressure_ratio(self):
        out=self.run_sambu(
            "print(migration_speed(150 * km, 10800 * s))\n"
            "print(oxygen_pressure_ratio(12 * Pa, 20 * Pa))"
        )
        self.assertEqual(out,["13.888889 m/s","0.6"])
    def test_incompatible_units_rejected(self):
        with self.assertRaises(ValueError):
            execute("countercurrent_exchange(310 * K, 280 * Pa, 75%)")

if __name__ == "__main__": unittest.main()
