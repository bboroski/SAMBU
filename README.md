# SAMBU

**SAMBU** — **S**tatistical **A**nalysis & **M**odeling with **B**oltzmann **U**tilities — is an experimental, interpreted domain-specific language for compact scientific calculations inspired by statistical mechanics and kinetic theory.

The first release focuses on readable equations, SI-aware quantities, dimensional checks, Maxwell speed statistics, Boltzmann weights, simple partition functions, and reproducible sampling. The interpreter is written in Python 3.10+ and has no runtime dependencies.

> **Status:** 0.1.0 — early prototype. SAMBU is not yet a general-purpose language, a symbolic algebra system, or a validated computational-physics package. Its built-ins are small reference implementations intended for learning and experimentation.

## Quick start

```bash
python -m pip install -e .
sambu examples/ideal_gas.sambu
```

Or run a one-liner:

```bash
sambu -c 'let T = 300 * K; print(thermal_energy(T))'
```

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

## A SAMBU program

```sambu
# Argon at room temperature
let temperature = 300 * K
let argon_mass = 6.6335209e-26 * kg

let speeds = maxwell(temperature, argon_mass)
print("most probable speed:")
print(speeds.most_probable)
print("root-mean-square speed:")
print(speeds.rms)

let excitation = 0.025 * eV
print("Boltzmann population factor:")
print(boltzmann(excitation, temperature))
```

## Language at a glance

- `let name = expression` creates an immutable binding.
- Newlines or semicolons separate statements.
- Numbers support decimal and scientific notation (`1.38e-23`).
- Strings use single or double quotes; comments begin with `#`.
- Operators: `+ - * / ^`, comparisons, `&&`, `||`, and `!`.
- Arrays: `[0 * eV, 0.02 * eV, 0.04 * eV]`.
- Record fields: `maxwell(T, m).rms`.
- Units participate in arithmetic and reject incompatible addition/comparison.

See [the language guide](docs/LANGUAGE.md) for the grammar, built-ins, units, and design notes.

## Included examples

| File | Demonstrates |
|---|---|
| `examples/ideal_gas.sambu` | Thermal energy and Maxwell speed scales |
| `examples/boltzmann_weights.sambu` | Boltzmann factors, a discrete partition function, and Shannon/Gibbs entropy in nats |

## Project layout

```text
sambu-language/
├── sambu/                 # lexer, parser, interpreter, units, CLI
├── examples/              # runnable SAMBU source files
├── tests/                 # dependency-free unittest suite
├── docs/                  # language guide and design notes
└── .github/workflows/     # CI test matrix
```

## Roadmap

1. Formalize the grammar and error locations.
2. Add functions, scopes, and structured control flow.
3. Add numeric arrays and vectorized operations.
4. Add differential-equation and kinetic-equation solvers only with tested numerical methods and explicit solver tolerances.
5. Stabilize the language specification before a 1.0 release.

## License

MIT. See [LICENSE](LICENSE).
