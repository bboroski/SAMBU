from __future__ import annotations

import unittest

from sambu.nun import (
    BoundaryProfile,
    GenesisSpec,
    NunEngine,
    NunError,
    PrimordialState,
)


class PrimordialStateTests(unittest.TestCase):
    def test_values_are_defensive_copies_and_digest_is_stable(self):
        first = PrimordialState(
            {"temperature_K": 300.0, "nested": {"count": 2}},
            seed=17,
            provenance="test fixture",
        )
        second = PrimordialState(
            {"nested": {"count": 2}, "temperature_K": 300.0},
            seed=17,
            provenance="test fixture",
        )
        self.assertEqual(first.digest, second.digest)

        exported = first.values
        exported["nested"]["count"] = 99
        self.assertEqual(first.values["nested"]["count"], 2)

    def test_digest_changes_when_seed_or_provenance_changes(self):
        baseline = PrimordialState({"value": 1}, seed=5)
        other_seed = PrimordialState({"value": 1}, seed=6)
        other_source = PrimordialState({"value": 1}, seed=5, provenance="measured")
        self.assertNotEqual(baseline.digest, other_seed.digest)
        self.assertNotEqual(baseline.digest, other_source.digest)

    def test_rejects_non_finite_numbers_and_invalid_seed(self):
        with self.assertRaises(NunError):
            PrimordialState({"temperature": float("nan")})
        with self.assertRaises(NunError):
            PrimordialState({"temperature": 1.0}, seed=True)
        with self.assertRaises(NunError):
            PrimordialState({"temperature": 1.0}, seed=-1)

    def test_rejects_non_json_values_and_invalid_field_names(self):
        with self.assertRaises(NunError):
            PrimordialState({"value": object()})
        with self.assertRaises(NunError):
            PrimordialState({"bad field": 1})


class BoundaryProfileTests(unittest.TestCase):
    def test_isolated_and_periodic_modes_reject_external_inputs(self):
        for mode in ("isolated", "periodic"):
            with self.subTest(mode=mode):
                with self.assertRaises(NunError):
                    BoundaryProfile(mode=mode, external_inputs=("radiation",))

    def test_rejects_non_string_mode(self):
        with self.assertRaises(NunError):
            BoundaryProfile(mode=[])

    def test_exchange_mode_requires_explicit_inputs(self):
        with self.assertRaises(NunError):
            BoundaryProfile(mode="exchange")
        profile = BoundaryProfile(
            mode="exchange",
            invariants=("charge",),
            external_inputs=("radiation",),
        )
        self.assertEqual(profile.external_inputs, ("radiation",))

    def test_boundary_labels_are_unique_and_non_conflicting(self):
        with self.assertRaises(NunError):
            BoundaryProfile(invariants=("mass", "mass"))
        with self.assertRaises(NunError):
            BoundaryProfile(
                mode="exchange",
                invariants=("mass",),
                external_inputs=("mass",),
            )


class NunEngineTests(unittest.TestCase):
    def setUp(self):
        self.spec = GenesisSpec(
            "ideal-gas.initial-state",
            origin=PrimordialState(
                {"temperature_K": 300.0, "particle_mass_kg": 6.6e-26},
                seed=17,
                provenance="test fixture",
            ),
            boundary=BoundaryProfile(
                mode="isolated",
                invariants=("mass", "particle_count"),
            ),
            required_fields=("temperature_K", "particle_mass_kg"),
            assumptions=("uniform initial state",),
        )

    def test_valid_spec_produces_repeatable_content_addressed_manifest(self):
        engine = NunEngine()
        first = engine.prepare(self.spec)
        second = engine.prepare(self.spec)

        self.assertTrue(first.is_valid)
        self.assertEqual(first.findings, ())
        self.assertIsNotNone(first.manifest)
        self.assertEqual(first.manifest.digest, second.manifest.digest)
        self.assertEqual(len(first.manifest.digest), 64)
        self.assertEqual(
            first.manifest.payload["schema"],
            "sambu.nun.genesis/v1",
        )
        self.assertEqual(
            first.manifest.payload["origin"]["seed"],
            17,
        )

    def test_missing_required_fields_fail_closed_without_manifest(self):
        incomplete = GenesisSpec(
            "incomplete-run",
            origin=PrimordialState({"temperature_K": 300.0}),
            required_fields=("temperature_K", "particle_mass_kg"),
        )
        report = NunEngine().prepare(incomplete)
        self.assertFalse(report.is_valid)
        self.assertIsNone(report.manifest)
        self.assertEqual(report.errors[0].code, "NUN-STATE-001")
        self.assertIn("particle_mass_kg", report.errors[0].message)

    def test_manifest_size_limit_returns_a_finding(self):
        report = NunEngine(max_manifest_bytes=32).prepare(self.spec)
        self.assertFalse(report.is_valid)
        self.assertIsNone(report.manifest)
        self.assertEqual(report.errors[0].code, "NUN-MANIFEST-001")

    def test_spec_rejects_duplicate_requirements_and_assumptions(self):
        state = PrimordialState({"value": 1})
        with self.assertRaises(NunError):
            GenesisSpec("bad-spec", origin=state, required_fields=("value", "value"))
        with self.assertRaises(NunError):
            GenesisSpec("bad-spec", origin=state, assumptions=("same", "same"))

    def test_report_serialization_is_a_fresh_copy(self):
        report = NunEngine().prepare(self.spec)
        first = report.to_dict()
        first["manifest"]["origin"]["values"]["temperature_K"] = -1
        second = report.to_dict()
        self.assertEqual(
            second["manifest"]["origin"]["values"]["temperature_K"],
            300.0,
        )


if __name__ == "__main__":
    unittest.main()
