# SAMBU 0.4 language guide

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

`let` creates an immutable name. Re-defining a name in the same scope is an error. Built-in units and constants are predeclared (`kg`, `g`, `m`, `s`, `K`, `J`, `eV`, `k_B`, `h`, `c`, and others); top-level bindings cannot redefine those names. Nested blocks and functions have child scopes and may shadow an outer name. A program may contain comments beginning with `#`.

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

All quantities are stored internally in SI base units. Addition, subtraction, and comparison require matching dimensions. Multiplication and division combine dimensions. Integer powers preserve dimensional meaning. Fractional powers of dimensioned quantities remain deliberately rejected.

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
- User-defined functions and bounded loops are available in 0.4. No file I/O, network access, imports, mutable assignment, or arbitrary Python evaluation are exposed to SAMBU programs.

## Error model

Lexical and parse errors include one-based line/column information, a stable code, and an end-exclusive source range. Runtime errors are surfaced by the CLI with the source filename. Dimension mismatch, invalid temperatures, invalid probabilities, unknown names, and duplicate bindings fail explicitly instead of silently coercing values.

### Source locations and parser API (0.4)

The public package exports `SourcePosition`, `SourceSpan`, `Token`, `SambuSyntaxError`, `tokenize`, and `parse`.

- `SourcePosition(offset, line, column)` uses a zero-based Python string offset (Unicode code points) and one-based line and column numbers.
- `SourceSpan(start, end)` is end-exclusive. Its `is_empty` property identifies a point range.
- Each lexer `Token` retains the original `kind`, `value`, `line`, and `column` fields and adds a `span` property, `end_line`, `end_column`, `start_offset`, and `end_offset`.
- `SambuSyntaxError` retains `line` and `column`, and adds `code` and `span`. Its human-readable exception string keeps the existing line/column format.
- Current diagnostic codes are `SAMBU-L001` (unexpected character), `SAMBU-L002` (unterminated string literal), and `SAMBU-P001` (parser syntax error).

`parse(source)` continues to return the established tuple-based AST so existing interpreter clients do not break. Node-level AST spans and a typed AST representation are follow-up work; the current span contract covers tokens and syntax diagnostics. LSP integrations must convert code-point offsets to the negotiated position encoding.

## Control flow and functions

User-defined functions use lexical scope and return values:

```sambu
fn square(x) { return x * x }
print(square(12))
```

Conditionals use `if` and optional `else`; conditions are evaluated as booleans/truthy values:

```sambu
if (temperature > 300 * K) {
  print("above reference temperature")
} else {
  print("at or below reference temperature")
}
```

Bounded iteration uses `for name in array_or_range { ... }`. The standard `range(stop)`, `range(start, stop)`, and `range(start, stop, step)` functions generate integer arrays. `sum`, `min`, `max`, and `len` are also available. Both `range` and `for` enforce a 100,000-item safety cap. Blocks create child scopes; `let` names are immutable. Local bindings can shadow standard-library names. See [Domain Models](DOMAINS.md) for the application library.
