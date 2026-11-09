# Scientific computing

## Purpose

SAMBU began as a compact scientific DSL for statistical mechanics and introductory kinetic theory. Its scientific layer keeps equations readable while carrying physical dimensions through runtime calculations.

It provides deterministic calculation helpers for teaching, exploration and small modeling tasks. The interpreter is not a general-purpose PDE solver and does not claim to solve the full Boltzmann or Landau kinetic equations.

## Example: Maxwell speed distribution

```sambu
let temperature = 300 * K
let particle_mass = 6.6e-26 * kg
let stats = maxwell(temperature, particle_mass)

print(stats.most_probable)
print(stats.mean)
print(stats.rms)
print(stats.component_sigma)
```

The helper returns characteristic speeds for a classical ideal-gas particle with three translational degrees of freedom.

## Scientific built-ins

The documented standard-library surface includes:

| Function | Purpose |
|---|---|
| `thermal_energy(T, dof=3)` | Equipartition mean energy |
| `maxwell(T, particle_mass)` | Characteristic Maxwell speeds |
| `boltzmann(E, T)` | Boltzmann factor |
| `partition(energy_levels, T)` | Finite discrete partition sum |
| `entropy(probabilities)` | Shannon/Gibbs entropy in nats |
| `sample_maxwell(T, particle_mass, count, seed=0)` | Reproducible speed samples |
| `mean(array)` | Arithmetic mean |
| `variance(array)` | Unbiased sample variance |
| `sqrt`, `exp`, `log`, `abs` | Elementary numeric operations |

Input constraints are enforced. Temperature and particle mass must be positive; entropy probabilities must be non-negative and sum to one; dimensional arithmetic must remain consistent.

## Reproducibility

The Maxwell sampler has a seed parameter and defaults to seed 0 in the documented implementation. This makes the sample sequence repeatable for identical inputs and implementation behavior.

Reproducibility does not imply empirical validity. A model's assumptions, parameter choices and units must still match the research question.

## Numerical scope

- Physical quantities are SI-normalized.
- Numeric operations use Python floating-point values.
- Arrays are interpreted lists rather than vectorized numerical tensors.
- The partition helper calculates a finite discrete sum.
- Fractional powers of dimensional quantities are intentionally rejected.
- The helpers do not replace SciPy, NumPy or specialist simulation software for large numerical workloads.

## Evidence and model discipline

A scientific function should expose its assumptions and not silently hard-code species- or experiment-specific values. The Anatidae models follow this principle by accepting parameters for efficiency, wetness, flight power, visual characteristics and other quantities.

## Further reading

- [Types, units and numerics](TYPES-UNITS-AND-NUMERICS.md)
- [Anatidae model guide](../docs/ANATIDAE_MODELS.md)
- [Domain models](../docs/DOMAINS.md)
