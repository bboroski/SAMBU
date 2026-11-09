# SAMBU

**SAMBU** — **S**tatistical **A**nalysis & **M**odeling with **B**oltzmann **U**tilities — is an experimental, interpreted domain-specific language for compact scientific calculations inspired by statistical mechanics and kinetic theory.

SAMBU combines readable equations, SI-aware quantities, dimensional checks, Maxwell speed statistics, Boltzmann weights, and reproducible sampling with compact models for stakeholder networks, negotiation ranges, marketing funnels, event operations, and resource-allocation scenarios. The interpreter is written in Python 3.10+ and has no runtime dependencies.

> **Status:** 0.2.0 — experimental alpha. SAMBU is not yet a general-purpose language, a symbolic algebra system, or a validated computational-physics package. Its built-ins are small reference implementations intended for learning and experimentation.

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
| `examples/neo_modern_diplomat.sambu` | Stakeholder network, influence paths, and a negotiation interval |
| `examples/community_hub.sambu` | Weekly wellness schedule, attendance, funnel, A/B estimate, pricing, and channel metrics |
| `examples/territory_control.sambu` | Resource allocation and a tower-capture rule |

## Project layout

```text
sambu-language/
├── sambu/                 # lexer, parser, interpreter, units, domain models, CLI
├── examples/              # runnable SAMBU source files
├── tests/                 # dependency-free unittest suite
├── docs/                  # language guide and domain-model assumptions
└── .github/workflows/     # CI test matrix
```

## Roadmap

1. Add numeric arrays and vectorized operations with explicit shape rules.
2. Add numerical ODE/PDE and kinetic-equation solvers only with tested methods, convergence checks, and explicit tolerances.
3. Add richer network/game simulation primitives and event-driven execution.
4. Stabilize the language specification and package API before a 1.0 release.

## License

MIT. See [LICENSE](LICENSE).

## SAMBU 0.2 — functions and systems models

The 0.2 release adds user-defined functions, lexical scopes, `return`, `if` / `else`, and bounded `for ... in` loops. The standard library now includes `range`, `sum`, `min`, `max`, plus a systems-modeling layer:

- **Networks:** `network`, `network_metrics`, `influence` for directed stakeholder graphs and bounded influence diffusion.
- **Negotiation:** `negotiate` for bargaining-range overlap and `allocate` for proportional resource distribution.
- **Growth and experiments:** `funnel` for stage conversion and `ab_test` for a two-proportion screening test.
- **Events and business operations:** `weekly_schedule`, `attendance`, `channel_metrics`, `package_pricing`, and `unit_economics` for recurring sessions, occupancy, acquisition efficiency, and package economics.
- **Strategy prototypes:** `capture_tower` for a single resource-versus-resistance action.

New runnable programs: `examples/neo_modern_diplomat.sambu`, `examples/community_hub.sambu`, and `examples/territory_control.sambu`. Read [Domain Models](docs/DOMAINS.md) for assumptions and limitations. These are transparent scenario models, not real-world outcome predictors or integrations with CRM, VOIP, payment, or social platforms.
