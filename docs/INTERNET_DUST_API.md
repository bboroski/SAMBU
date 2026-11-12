# Internet Dust API v1

**Status:** Proposed contract; documentation only. No runtime capability is implied until an implementation and tests exist.

## Purpose and boundaries

This API models the fictional “Internet Dust” concept as an optional, deterministic computational domain. It does not claim that such particles or a metro-wide physical system exist. Adapters must preserve each repository's existing safety, resource, and platform boundaries.

## Shared data contract

A particle record contains `id`, `position_m[3]`, `velocity_m_s[3]`, `mass_kg`, `radius_m`, `charge_c`, optional `magnetic_moment_a_m2[3]`, `temperature_k`, and `provenance`. Unknown values are null/absent, never silently replaced with zero. Coordinates are metres; time is seconds; temperature is kelvin; charge is coulombs; fields use SI units.

A simulation frame contains `schema_version`, `simulation_id`, `sequence`, `time_s`, `environment`, `particles`, `model_profile`, `random_seed`, and `evidence`. Every computed value is labelled as simulated; observations and estimates remain distinguishable.

## Shared operations

- `validate_profile(profile)`: validate ranges, units, model support, and resource limits.
- `ingest_particles(records)`: validate and normalize records without inventing missing measurements.
- `step(frame, dt_s)`: advance one bounded simulation step when supported.
- `query_state(region, time_range)`: return a bounded snapshot.
- `export_frame(format, frame)`: serialize a versioned frame.
- `health()`: report availability, capability level, and resource status.

## Physical-model rules

Use SI dimensional checks. Brownian motion may use a Langevin/stochastic model; drag depends on the flow regime and particle size. Rayleigh scattering is valid only when the size parameter is much smaller than one. Coulomb inverse-square behavior applies to idealized point charges in the appropriate medium. A 293 K environment is a configurable reference, not proof of equilibrium. The weak nuclear interaction is not a meaningful macroscopic dust-force term; nuclear binding is outside the default model. Navier–Stokes describes the carrier fluid, not individual grains.

## Compatibility and safety

Contracts are versioned independently of implementation. Unknown fields are ignored only where explicitly marked extensible; required unknown enum values fail closed. Bound particle counts, time steps, memory, CPU, and payload sizes. No network listener, hardware access, privileged operation, or automatic execution is introduced by this specification. Consumers must negotiate capabilities before use.

## Repository adapter: scientific model engine

SAMBU owns reference equations, dimensional analysis, deterministic sampling, and high-level simulation orchestration. Expose Python-facing operations:
- `dust.profile.create(config) -> SimulationProfile`
- `dust.particles.sample(profile, seed, count) -> Particle[]`
- `dust.fields.evaluate(points, field_config) -> FieldSample[]`
- `dust.simulate.run(profile, initial_state, steps) -> SimulationResult`
- `dust.analysis.statistics(result) -> DistributionSummary`

Model packages: spatial density, electrostatics, Langevin/Brownian motion, drag/flow coupling, optical scattering, acoustics, and optional magnetic dipoles. Each model declares assumptions, validity domain, units, solver, and uncertainty. Quantum effects are an explicitly separate optional micro-model, not a default macroscopic solver. Results must be reproducible from a recorded seed and profile; tests compare invariants and dimensional consistency rather than brittle exact floating-point output.

## Acceptance criteria

- Contract and schema versions are explicit.
- Invalid dimensions, non-finite values, negative mass/radius, out-of-range charge, oversized payloads, and unsupported capabilities are rejected or explicitly marked unknown.
- Unit tests cover valid, invalid, boundary, overflow, and missing-evidence cases.
- Documentation and CI distinguish specification from implemented behavior.
