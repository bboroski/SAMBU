# Types, units and numerics

## Runtime value model

The documented interpreter works with values such as:

- numeric values;
- strings;
- booleans;
- `null`;
- arrays;
- physical quantities;
- records returned by built-in domain functions;
- functions and objects in the extended language runtime.

This page describes runtime behavior and should not be mistaken for a claim that SAMBU already has a fully static compile-time type checker.

## Physical quantities

Physical quantities are stored in SI-normalized form with integer powers for five base dimensions:

1. mass;
2. length;
3. time;
4. temperature;
5. amount of substance.

A quantity is represented by a numeric value and a dimension vector. This enables dimensional validation during arithmetic.

Examples:

```sambu
let distance = 12 * m
let duration = 3 * s
let speed = distance / duration
print(speed)
```

The interpreter stores the result in SI units with dimensions of length divided by time.

## Dimensional rules

- Addition and subtraction require matching dimensions.
- Comparisons require matching dimensions.
- Multiplication combines dimension exponents.
- Division subtracts dimension exponents.
- Integer powers scale dimension exponents.
- Fractional powers of dimensioned quantities are rejected.
- A plain number can combine with a dimensionless quantity, but not arbitrarily with a dimensioned quantity.
- Non-finite quantity values are rejected.

These rules catch many unit mistakes at runtime.

## Built-in units

Documented units include:

| Symbol | Meaning |
|---|---|
| `kg`, `g` | kilogram, gram |
| `m`, `cm`, `km` | metre, centimetre, kilometre |
| `s`, `ms` | second, millisecond |
| `K` | kelvin |
| `mol` | mole |
| `J`, `kJ`, `eV` | joule, kilojoule, electronvolt |
| `Pa`, `bar` | pascal, bar |
| `Hz` | hertz |
| `N` | newton |
| `L` | litre |

Explicit multiplication is required: use `300 * K`, not `300 K`.

## Constants

The documented constants include `k_B`, `h`, `hbar`, `c`, `N_A`, `R`, `G`, `pi` and `e`. Exact and measured values are defined by the implementation.

## Numerical model and limitations

The language guide documents Python floating-point arithmetic using IEEE-754 double precision. Arrays are interpreted lists, not automatically vectorized tensors. The classical Maxwell helpers assume an ideal-gas particle with three translational degrees of freedom. Discrete partition functions use finite arrays of energy levels.

The language's scientific helpers validate their inputs, but they are not a substitute for a numerical-methods library, domain-specific validation or empirical evidence.

## Percentage values

An attached literal such as `12.5%` becomes the dimensionless number `0.125`. The helper functions in the percentage library validate finite, dimensionless inputs and reject invalid denominators rather than silently coercing them.

See [Percentage arithmetic in the source documentation](../docs/PERCENTAGES.md).

## Related pages

- [Scientific computing](SCIENTIFIC-COMPUTING.md)
- [Syntax and control flow](SYNTAX-AND-CONTROL-FLOW.md)
- [Domain libraries](DOMAIN-LIBRARIES.md)
