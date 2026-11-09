# SAMBU 0.1 language guide

## Design goal

SAMBU is a small scientific DSL whose syntax keeps equations visible while its runtime tracks physical dimensions. Its initial domain is statistical mechanics and introductory kinetic theory. The name expands to **Statistical Analysis & Modeling with Boltzmann Utilities**.

This is an interpreter prototype, not a claim that SAMBU solves the full Boltzmann equation or Landau kinetic equation. Those require numerical methods, boundary conditions, collision operators, and validation beyond the current release.

## Program structure

A program is a sequence of statements separated by a newline or `;`.

```sambu
let temperature = 300 * K
let mass = 6.6e-26 * kg
let stats = maxwell(temperature, mass)
print(stats.mean)
```

`let` creates an immutable name. Re-defining a name in the same program is an error. A program may contain comments beginning with `#`.

## Expressions

Supported values are numbers, strings, booleans, `null`, arrays, quantities, and records returned by scientific functions. Expressions support function calls, array indexing, and record-field access.

Operator precedence, highest to lowest:

1. Function calls, indexing, and field access
2. Unary `-`, `+`, `!`
3. `^` / `**` (right associative)
4. `*`, `/`
5. `+`, `-`
6. `<`, `<=`, `>`, `>=`
7. `==`, `!=`
8. `&&` / `and`
9. `||` / `or`

Use explicit multiplication for units: `300 * K`, not `300 K`.

## Physical quantities

All quantities are stored internally in SI base units. Addition, subtraction, and comparison require matching dimensions. Multiplication and division combine dimensions. Integer powers preserve dimensional meaning. Fractional powers of dimensioned quantities are deliberately rejected in 0.1.

### Built-in units

| Name | SI value |
|---|---:|
| `kg`, `g` | 1 kg, 0.001 kg |
| `m`, `cm`, `km` | 1 m, 0.01 m, 1000 m |
| `s`, `ms` | 1 s, 0.001 s |
| `K` | 1 kelvin |
| `mol` | 1 mole |
| `J`, `kJ`, `eV` | 1 J, 1000 J, 1.602176634e-19 J |
| `Pa`, `bar` | 1 Pa, 100000 Pa |
| `Hz`, `N`, `L` | hertz, newton, litre |

### Constants

`k_B`, `h`, `hbar`, `c`, `N_A`, `R`, `G`, `pi`, and `e` are predefined. SI exact values are used where defined; constants with measured values use the values documented in source code.

## Scientific standard library

| Function | Signature | Result |
|---|---|---|
| `thermal_energy` | `thermal_energy(T, dof=3)` | Mean equipartition energy, `(dof/2) k_B T` |
| `maxwell` | `maxwell(T, particle_mass)` | Record with `most_probable`, `mean`, `rms`, `component_sigma` (all speeds) |
| `boltzmann` | `boltzmann(E, T)` | Dimensionless factor `exp(-E/(k_B T))` |
| `partition` | `partition(energy_levels, T)` | Discrete sum of Boltzmann factors |
| `entropy` | `entropy(probabilities)` | Shannon/Gibbs entropy in nats; probabilities must sum to 1 |
| `sample_maxwell` | `sample_maxwell(T, particle_mass, count, seed=0)` | Reproducible Maxwell speed samples |
| `mean` | `mean(array)` | Arithmetic mean |
| `variance` | `variance(array)` | Unbiased sample variance |
| `sqrt`, `exp`, `log`, `abs` | scalar helpers | Elementary operations |
| `count` | `count(array)` | Number of array items |
| `print` | `print(value)` | Writes a formatted value to standard output |

`T` must be a positive temperature. Particle mass must be positive. `partition` accepts an array of energies. `entropy` accepts non-negative probabilities summing to one and returns nats (divide by `log(2)` for bits).

## Numerical scope and limitations

- The interpreter uses Python floating-point arithmetic (IEEE-754 double precision).
- Arrays are ordinary interpreted lists, not vectorized tensors.
- The Maxwell distribution helpers assume a classical ideal-gas particle with three translational degrees of freedom.
- `partition` is a finite discrete sum; it does not calculate a continuum density of states.
- `sample_maxwell` draws three independent Gaussian velocity components and returns their speed magnitude. Its default seed is `0` for repeatability.
- Unit conversion is implicit to SI at input; display formatting chooses a small set of common derived units.
- No file I/O, network access, imports, user-defined functions, loops, or arbitrary Python evaluation are exposed to SAMBU programs.

## Error model

Lexical and parse errors include line/column information. Runtime errors are surfaced by the CLI with the source filename. Dimension mismatch, invalid temperatures, invalid probabilities, unknown names, and duplicate bindings fail explicitly instead of silently coercing values.
