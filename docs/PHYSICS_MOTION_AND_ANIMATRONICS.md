# SAMBU physics, motion and animatronic reference models

This layer turns selected physical relationships into deterministic, testable functions. It is a numerical reference library; it is not a real-time simulator, safety-certified controller, or hardware driver.

## Function groups

| Function | Relationship | Units |
|---|---|---|
| `newton_force` | (F=ma) | kg, m/s² → N |
| `kinetic_energy` | (E_k=mv²/2) | kg, m/s → J |
| `spring_damper_force` | (F=-(kx+cv)) | m, m/s, N/m, N·s/m → N |
| `constant_acceleration` | (x=x₀+v₀t+at²/2) | SI kinematics |
| `thermal_response` | first-order thermal relaxation | °C, seconds |
| `rc_voltage` | first-order RC response, (	au=RC) | V, Ω, F, seconds |
| `sample_quintic_trajectory` | rest-to-rest quintic interpolation | caller-defined position units |
| `sample_animatronic_joint` | joint-range and velocity/acceleration constrained trajectory | radians and seconds |

## Multi-stage motion flow

1. **Describe:** provide start, target, duration and physical limits.
2. **Validate:** reject non-finite values, invalid ranges and infeasible peak velocity/acceleration.
3. **Plan:** use the analytic quintic profile with zero velocity and acceleration at both endpoints.
4. **Sample:** evaluate position, velocity and acceleration at a caller-selected time.
5. **Verify:** compare samples against expected invariants in unit and property tests.
6. **Adapt:** a separate platform adapter may translate a validated setpoint into device-specific units.

The library stops at stage 4. Stage 6 is deliberately not implemented here: it requires a separate safety policy, sensor feedback, watchdog, hardware-specific limits and operator authorization.

## Reproducibility and compaction

Functions are pure and stateless; equal inputs produce equal outputs. Motion samples are generated on demand rather than retaining an unbounded frame history. Callers choose sample cadence and retain only the frames needed by their renderer or actuator supervisor.

## Verification

Run `python -m unittest discover -s tests -v` or the repository's standard `python one.py check`. Tests cover equation outputs, invalid domains, endpoint continuity, motion limits and deterministic repeated sampling.
