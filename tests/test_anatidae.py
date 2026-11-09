from __future__ import annotations
import unittest

from sambu.anatidae import AnatidaeProfile
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

    def test_plumage_insulation_and_feather_barrier_are_parameterized(self):
        out=self.run_sambu(
            "let p = plumage_insulation(0.9, 25%, 10%)\n"
            "let f = feather_barrier_profile(1, 90%, 80%, 10%, 20%)\n"
            "print(p.effective_index)\nprint(f.effective_insulation_index)"
        )
        self.assertEqual(out,["0.6075","0.5832"])

    def test_flight_energy_and_muscle_fuel_profile(self):
        out=self.run_sambu(
            "let f = flight_energy_budget((10 * J) / (1 * s), 5 * s, 60 * J)\n"
            "let m = flight_muscle_profile((8 * J) / (1 * s), (2 * J) / (1 * s), 5 * s, 75%)\n"
            "print(f.energy_required)\nprint(f.energy_remaining)\n"
            "print(m.fat_oxidation_energy_estimate)\nprint(m.anaerobic_fraction)"
        )
        self.assertEqual(out,["50 J","10 J","30 J","0.2"])

    def test_migration_speed_and_oxygen_pressure_ratio(self):
        out=self.run_sambu(
            "print(migration_speed(150 * km, 10800 * s))\n"
            "print(oxygen_pressure_ratio(12 * Pa, 20 * Pa))"
        )
        self.assertEqual(out,["13.888889 m/s","0.6"])

    def test_gas_exchange_filter_and_salt_balance(self):
        out=self.run_sambu(
            "let gas = avian_gas_exchange(100, 21%, 40%, 20 * Pa)\n"
            "let bill = bill_lamella_filter(2, 0.5, 100)\n"
            "let salt = salt_balance(20, 5, 16)\n"
            "print(gas.oxygen_uptake_proxy)\nprint(bill.retention_fraction)\n"
            "print(salt.net_salt_balance_rate)"
        )
        self.assertEqual(out,["8.4","0.75","-1"])

    def test_visual_imprinting_sleep_and_magnetic_models(self):
        out=self.run_sambu(
            "let eyes = visual_system_profile(330, 0.8, true, true)\n"
            "let window = imprinting_window(14, 12, 16)\n"
            "let sleep = hemispheric_sleep_budget(20, 10%, 100%)\n"
            "let compass = magnetic_heading(5, 12, 50%)\n"
            "print(eyes.panoramic_fraction)\nprint(window.inside_configured_window)\n"
            "print(sleep.edge_bird_count_estimate)\nprint(compass.corrected_heading_degrees)"
        )
        self.assertEqual(out,["0.9166666666666666","true","2","359"])

    def test_digestive_grinding_model(self):
        out=self.run_sambu("let g = digestive_grinding(10, 20%, 3)\nprint(g.estimated_particle_size)")
        self.assertEqual(out,["5.12"])

    def test_incompatible_units_rejected(self):
        with self.assertRaises(ValueError):
            execute("countercurrent_exchange(310 * K, 280 * Pa, 75%)")

    def test_parameterized_taxon_profile_has_no_fabricated_defaults(self):
        profile=AnatidaeProfile(
            taxon="Anatidae / example population",
            foraging_mode="dabbling",
            diving_mode="surface",
            evidence_refs=("source:field-study-01",),
        ).to_record()
        self.assertEqual(profile.get("profile_status"),"parameterized_not_taxonomically_verified")
        self.assertIsNone(profile.get("countercurrent_efficiency"))
        self.assertEqual(profile.get("evidence_refs"),["source:field-study-01"])


if __name__ == "__main__":
    unittest.main()
