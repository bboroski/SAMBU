"""Build and inspect a reproducible SAMBU genesis manifest.

This example records initial conditions; it does not execute a gas simulation.
"""
from sambu.nun import (
    BoundaryProfile,
    GenesisSpec,
    NunEngine,
    PrimordialState,
)


spec = GenesisSpec(
    "ideal-gas.initial-state",
    version="1.0.0",
    origin=PrimordialState(
        {
            "temperature_K": 300.0,
            "particle_mass_kg": 6.6e-26,
            "particle_count": 1000,
        },
        seed=17,
        provenance="illustrative example parameters",
    ),
    boundary=BoundaryProfile(
        mode="isolated",
        invariants=("mass", "particle_count"),
    ),
    required_fields=("temperature_K", "particle_mass_kg", "particle_count"),
    assumptions=(
        "initial temperature is spatially uniform",
        "particle mass is constant across the sample",
    ),
)

report = NunEngine().prepare(spec)
if not report.is_valid:
    for finding in report.findings:
        print(f"{finding.severity}: {finding.code}: {finding.message}")
    raise SystemExit(1)

assert report.manifest is not None
print(f"Genesis manifest: {report.manifest.digest}")
print(f"Boundary mode: {report.manifest.payload['boundary']['mode']}")
print(f"Seed: {report.manifest.payload['origin']['seed']}")
