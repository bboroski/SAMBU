import math
import unittest

from sambu.physics import (
    constant_acceleration, first_order_response, kinetic_energy, newton_force,
    rc_voltage, sample_animatronic_joint, sample_quintic_trajectory,
    spring_damper_force, thermal_response,
)


class PhysicsTests(unittest.TestCase):
    def test_newton_and_energy(self):
        self.assertEqual(newton_force(2.0, 3.0), 6.0)
        self.assertEqual(kinetic_energy(2.0, 3.0), 9.0)

    def test_spring_damper(self):
        self.assertEqual(spring_damper_force(0.1, 0.2, 100.0, 5.0), -11.0)

    def test_constant_acceleration(self):
        state = constant_acceleration(0.0, 2.0, 3.0, 2.0)
        self.assertEqual(state.position, 10.0)
        self.assertEqual(state.velocity, 8.0)
        self.assertEqual(state.acceleration, 3.0)

    def test_first_order_and_thermal_response(self):
        expected = 1.0 + 9.0 * math.exp(-1.0)
        self.assertAlmostEqual(first_order_response(10.0, 1.0, 1.0, 1.0), expected)
        self.assertAlmostEqual(thermal_response(100.0, 20.0, 2.0, 2.0), 20.0 + 80.0 / math.e)

    def test_rc_uses_resistance_times_capacitance(self):
        self.assertAlmostEqual(rc_voltage(0.0, 5.0, 1000.0, 0.001, 1.0), 5.0 * (1.0 - math.exp(-1.0)))

    def test_quintic_endpoints_and_midpoint(self):
        start = sample_quintic_trajectory(0.0, 1.0, 2.0, 0.0)
        mid = sample_quintic_trajectory(0.0, 1.0, 2.0, 1.0)
        end = sample_quintic_trajectory(0.0, 1.0, 2.0, 2.0)
        self.assertEqual((start.position, start.velocity, start.acceleration), (0.0, 0.0, 0.0))
        self.assertAlmostEqual(mid.position, 0.5)
        self.assertAlmostEqual(mid.velocity, 0.9375)
        self.assertAlmostEqual(mid.acceleration, 0.0)
        self.assertEqual((end.position, end.velocity, end.acceleration), (1.0, 0.0, 0.0))

    def test_animatronic_joint_bounds_and_limits(self):
        state = sample_animatronic_joint(-0.5, 0.5, 0.5, 2.0, -1.0, 1.0, 1.0, 2.0)
        self.assertAlmostEqual(state.position, 0.0)
        with self.assertRaises(ValueError):
            sample_animatronic_joint(0.0, 2.0, 0.2, 1.0, -1.0, 1.0, 10.0, 10.0)
        with self.assertRaises(ValueError):
            sample_animatronic_joint(0.0, 1.0, 0.2, 0.1, -1.0, 1.0, 1.0, 1.0)

    def test_invalid_domains_rejected(self):
        with self.assertRaises(ValueError):
            newton_force(-1.0, 2.0)
        with self.assertRaises(ValueError):
            first_order_response(0.0, 1.0, 0.0, 1.0)
        with self.assertRaises(ValueError):
            constant_acceleration(0.0, 1.0, 0.0, -1.0)

    def test_sampling_is_deterministic(self):
        first = sample_quintic_trajectory(1.0, 4.0, 3.0, 1.2)
        second = sample_quintic_trajectory(1.0, 4.0, 3.0, 1.2)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
