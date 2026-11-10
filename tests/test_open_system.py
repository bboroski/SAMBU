from __future__ import annotations

import math
import unittest

from sambu.interpreter import execute


class OpenSystemTests(unittest.TestCase):
    def run_sambu(self, source: str) -> list[str]:
        output: list[str] = []
        execute(source, output=output.append)
        return output

    def test_planck_time_and_canonical_ensemble(self):
        output = self.run_sambu("""
let tau = planck_time()
let ensemble = canonical_ensemble([0 * J, 0 * J], 300 * K)
print(tau)
print(ensemble.partition_relative)
print(ensemble.probabilities[0])
print(ensemble.probabilities[1])
print(ensemble.entropy_nats)
""")
        self.assertIn("s", output[0])
        self.assertEqual(output[1:4], ["2", "0.5", "0.5"])
        self.assertAlmostEqual(float(output[4]), math.log(2), places=7)

    def test_microcanonical_energy_window(self):
        output = self.run_sambu("""
let ensemble = microcanonical_ensemble([0 * J, 1 * J, 2 * J], 1.5 * J, 0.5 * J)
print(ensemble.degeneracy)
print(ensemble.probabilities[1])
print(ensemble.probabilities[2])
print(ensemble.entropy_nats)
""")
        self.assertEqual(output[:3], ["2", "0.5", "0.5"])
        self.assertAlmostEqual(float(output[3]), math.log(2), places=7)

    def test_markov_relaxation_conserves_population_and_relaxes(self):
        output = self.run_sambu("""
let evolved = markov_relaxation([0 * J, 0 * J], [1, 0], 300 * K, 1 * Hz, 1 * s)
print(evolved.populations[0])
print(evolved.populations[1])
print(evolved.relaxation_factor)
""")
        self.assertAlmostEqual(float(output[0]) + float(output[1]), 1.0, places=12)
        self.assertAlmostEqual(float(output[0]), 0.5 + 0.5 * math.exp(-1), places=7)
        self.assertAlmostEqual(float(output[1]), 0.5 - 0.5 * math.exp(-1), places=7)
        self.assertAlmostEqual(float(output[2]), math.exp(-1), places=7)

    def test_two_level_lindblad_dephasing_preserves_trace_and_populations(self):
        output = self.run_sambu("""
let state = lindblad_dephase([[0.5, 0.2], [0.2, 0.5]], 1 * Hz, 1 * s)
print(state.trace)
print(state.matrix[0][0])
print(state.matrix[1][1])
print(state.matrix[0][1])
""")
        self.assertEqual(output[:3], ["1", "0.5", "0.5"])
        self.assertAlmostEqual(float(output[3]), 0.2 * math.exp(-1), places=7)

    def test_onsager_flux_and_nonnegative_dissipation(self):
        output = self.run_sambu("""
let transport = onsager_flux([3, 4], [[2, 0], [0, 1]])
print(transport.fluxes[0])
print(transport.fluxes[1])
print(transport.entropy_production)
""")
        self.assertEqual(output, ["-6", "-4", "34"])

    def test_exponential_phonon_relaxation(self):
        output = self.run_sambu("print(phonon_decay(2, 2 * Hz, 1 * s))")
        self.assertAlmostEqual(float(output[0]), 2 * math.exp(-2), places=7)

    def test_invalid_thermodynamic_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            execute("canonical_ensemble([0 * J], 0 * K)")
        with self.assertRaises(ValueError):
            execute("markov_relaxation([0 * J, 1 * J], [1, -0.1], 300 * K, 1 * Hz, 1 * s)")
        with self.assertRaises(ValueError):
            execute("microcanonical_ensemble([0 * J], 10 * J, 0 * J)")
        with self.assertRaises(ValueError):
            execute("lindblad_dephase([[0.5, 0.9], [0.9, 0.5]], 1 * Hz, 1 * s)")
        with self.assertRaises(ValueError):
            execute("onsager_flux([1, 2], [[1, 0], [0, -1]])")


if __name__ == "__main__":
    unittest.main()
