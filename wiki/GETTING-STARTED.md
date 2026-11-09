# Getting started

## Requirements

- Python 3.10 or newer.
- Git, if installing from a repository checkout.
- Optional host frameworks only when using their corresponding adapters: Flask, Django or FastAPI.

The core interpreter declares no mandatory third-party runtime dependencies.

## Install from a checkout

```bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
python -m pip install -e .
```

Check the installation:

```bash
sambu --version
```

The editable install makes the local source tree available to the Python environment. Use a virtual environment for isolated development.

## Run a first program

Create `hello.sambu`:

```sambu
let temperature = 300 * K
let mass = 6.6e-26 * kg
let result = maxwell(temperature, mass)

print(result.mean)
print(result.rms)
```

Run it:

```bash
sambu hello.sambu
```

This example uses built-in physical units and the Maxwell speed-distribution helper.

## Try the included examples

The repository README lists examples for several areas:

```bash
sambu examples/ideal_gas.sambu
sambu examples/oop_and_games.sambu
sambu examples/percentages.sambu
sambu examples/anatidae_biophysics.sambu
sambu examples/voxel_world.sambu
```

Examples are executable demonstrations, but their scientific and domain models remain parameterized tools rather than universal empirical claims.

## Run the test suite

```bash
python -m unittest discover -s tests -v
sambu-test tests --repeat 2
sambu-test tests --repeat 2 --json
```

The repeated runner can expose tests whose outcomes vary between runs. Its failure categories and suggested next steps are heuristic diagnostics, not guaranteed root-cause analysis.

## Optional web adapters

Install only what the host application needs:

```bash
python -m pip install -e ".[flask]"
python -m pip install -e ".[django]"
python -m pip install -e ".[fastapi]"
```

These are optional integration dependencies. The host application remains responsible for authentication, CSRF protection, persistence, deployment and authorization at protected data boundaries.

## Common commands

| Command | Purpose |
|---|---|
| `sambu --version` | Show installed CLI version |
| `sambu file.sambu` | Execute a SAMBU source file |
| `sambu-studio inspect PATH` | Inspect supported project configuration |
| `sambu-studio inspect PATH --format json` | Emit structured inspection output |
| `sambu-test tests --repeat 2` | Repeat test discovery and report flaky outcomes |

## Troubleshooting

**Command not found.** Confirm that the environment where SAMBU was installed is active. On Windows, use the matching virtual-environment Scripts directory; on Linux/macOS, use its bin directory.

**Import or dependency errors.** Re-run the editable installation with the intended Python interpreter: `python -m pip install -e .`.

**Unexpected syntax.** Check the supported grammar in [Syntax and control flow](SYNTAX-AND-CONTROL-FLOW.md). Do not assume that arbitrary Python syntax or imports are valid SAMBU syntax.

**A feature appears in Python documentation but not in a .sambu example.** Some capabilities are host-side Python APIs, not language built-ins. See [About SAMBU](ABOUT.md) and the relevant subsystem page.

## Next steps

- [Language tour](LANGUAGE-TOUR.md)
- [Types, units and numerics](TYPES-UNITS-AND-NUMERICS.md)
- [Object-oriented programming](OBJECT-ORIENTED-PROGRAMMING.md)
- [Testing and diagnostics](TESTING-AND-DIAGNOSTICS.md)
