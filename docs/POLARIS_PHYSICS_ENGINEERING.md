# Polaris Physics Engineering (PPE)

**Status: specification / planned.** This is an engineering proposal, not a claim of implemented algorithms or available physical telemetry. Physical terms are computational abstractions.

## Five subsystems
1. **Anti-corpuscular control:** detect incompatible states, duplicate work, resource contention, stale records and dependency cycles. Report conflicts; never silently delete data or cancel valid work.
2. **Corpuscular-wave model:** immutable discrete entities plus versioned events propagated over a bounded graph. Define identity, ordering, deduplication, backpressure and cancellation.
3. **Technical mechanics:** measurable resource budgets, load, queue pressure, latency, contention and state transitions. Use explicit units; avoid uncalibrated force scores.
4. **Cardio-thermodynamics:** heartbeat/liveness and thermal/load telemetry are separate signals. Distinguish measured, estimated and unavailable values; use hysteresis.
5. **Leaf-flight mechanics:** seeded stochastic scheduling for low-priority work with bounded exploration, fairness and deterministic fallback.

## Safety and data contract
- Events carry ID, source, kind, schema version, monotonic tick and correlation ID.
- Metrics declare unit, sampling interval, source and confidence/status.
- Bound queues, graph depth, retries, memory and execution time.
- Unknown data stays unknown; missing telemetry is never zero.
- No destructive cleanup, remote execution, kernel writes or device mutation is implied.
- APIs are opt-in and backward compatible; experimental modules use feature flags.

## Conformance tests
Deterministic replay; duplicate/out-of-order events; overflow, cancellation and backpressure; state invariants and cycle detection; resource bounds/timeouts; dimensional checks; benchmarks against recorded baselines.

## Delivery gates
`planned` → `partial` → `implemented` only with code, tests and appropriate benchmark/evidence. Hardware claims require target-board evidence.

## Repository-specific scope
Scientific computing: typed SI quantities, deterministic particle state, wave/event propagation, dimensional analysis and reproducible simulation. Test conservation, dimensional consistency, convergence and reproducibility.


## Classical physics foundations

The five entries below are **classical branches of physics**, not an exhaustive list of all physics. They provide a shared educational and technical taxonomy. A repository may document, model or implement only the parts justified by its actual purpose.

### 1. Mechanics
**Scope:** motion, rest, forces, mass, momentum, energy, rotation, equilibrium and interactions of bodies.

- Core concepts: position, displacement, velocity, acceleration, mass, force, momentum, work and energy.
- Representative laws: Newton's three laws; conservation of linear momentum and mechanical energy (under their applicable conditions); rotational dynamics.
- Core relations: `F = ma`, `p = mv`, `W = ∫F·dr`, `E_k = mv²/2`.
- SI quantities: metre (m), second (s), kilogram (kg), newton (N), joule (J), pascal (Pa).
- Computational concerns: coordinate frames, initial/boundary conditions, integration error, stability, conservation drift and collision/contact assumptions.

### 2. Thermodynamics
**Scope:** heat, work, temperature, internal energy, entropy, equilibrium and macroscopic properties of matter.

- Core concepts: system and surroundings, state variables, heat transfer, work, phase, thermal equilibrium and entropy.
- Representative laws: zeroth law (thermal equilibrium), first law (energy conservation), second law (entropy direction), third law (low-temperature entropy limit).
- Core relation: `ΔU = Q − W` when `W` denotes work done by the system; sign conventions must be stated.
- SI quantities: kelvin (K), joule (J), watt (W), pascal (Pa), kilogram (kg).
- Computational concerns: control-volume definition, heat/work sign convention, equation-of-state validity, energy balance and distinction between measured temperature and inferred load.

### 3. Electrodynamics
**Scope:** electric charge, current, voltage, electric and magnetic fields, electromagnetic forces, circuits and electromagnetic radiation.

- Core concepts: charge, current density, potential, electric field, magnetic flux density, induction and field energy.
- Representative laws: Maxwell's equations, Lorentz force law, charge conservation and (for lumped circuits) Ohm's and Kirchhoff's laws.
- Core relations: `F = q(E + v × B)`, `∇·E = ρ/ε₀`, `∇×E = −∂B/∂t`.
- SI quantities: coulomb (C), ampere (A), volt (V), ohm (Ω), tesla (T), farad (F), henry (H).
- Computational concerns: field/circuit assumptions, boundary conditions, gauge choices where relevant, numerical stability and electromagnetic compatibility.

### 4. Optics
**Scope:** light propagation and its interaction with matter, including reflection, refraction, imaging, interference, diffraction and polarization.

- Core concepts: wavelength, frequency, refractive index, focal length, intensity and polarization.
- Representative principles: geometric ray optics, Snell's law, reflection law, Fermat's principle and wave-optics interference/diffraction.
- Core relation: `n₁ sin(θ₁) = n₂ sin(θ₂)`; angles are measured from the normal.
- SI quantities: metre (m), second (s), hertz (Hz), candela (cd), lumen (lm), lux (lx).
- Computational concerns: distinguish ray and wave approximations, define optical media and geometry, track units and avoid claiming image fidelity without calibration.

### 5. Acoustics
**Scope:** sound as a mechanical wave in a medium, including propagation, frequency, amplitude, resonance, absorption and perception.

- Core concepts: pressure variation, particle displacement, frequency, wavelength, sound speed, intensity and impedance.
- Representative principles: wave equation, superposition, reflection, refraction, diffraction, resonance and Doppler effect.
- Core relations: `v = fλ`; sound-pressure level `Lₚ = 20 log₁₀(pᵣₘₛ/p₀)`, with the reference pressure and environment stated.
- SI quantities: pascal (Pa), metre (m), second (s), hertz (Hz), watt per square metre (W/m²).
- Computational concerns: specify the propagation medium and boundary conditions, sampling rate, anti-aliasing, calibration and logarithmic reference.

## Cross-domain modeling and implementation rules

1. Store quantities with explicit SI units or a documented unit system; never add unlike dimensions.
2. State assumptions, coordinate frames, reference conditions, boundary/initial conditions and sign conventions.
3. Separate measured, estimated, simulated and unavailable values; preserve source, timestamp, calibration and uncertainty.
4. Validate dimensional consistency, conservation laws where applicable, numerical convergence, deterministic reproducibility and bounded resource use.
5. Use domain-appropriate models: a software heartbeat is not a thermal measurement; scheduler load is not force; image pixels are not automatically calibrated optical measurements.
6. Keep scientific reference material separate from executable capability claims. Mark a feature implemented only after repository-local code, tests and reproducible evidence support it.
7. Treat these five branches as a classical foundation; quantum mechanics, relativity, particle/nuclear physics, condensed-matter physics and other specializations remain outside this introductory taxonomy.

## Repository-specific application
**Repository mapping:** scientific-computing modules may expose typed SI quantities, deterministic solvers, particle/wave simulations and reproducible numerical experiments. Keep this as a domain reference until code and validation evidence exist.
