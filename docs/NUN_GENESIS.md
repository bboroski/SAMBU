# Nun — reproducible genesis and initial conditions

**Status:** implemented Python host API, experimental.  
**Module:** `sambu.nun`  
**Scope:** immutable initial-state snapshots, declarative boundary profiles and deterministic genesis manifests.

## 1. Initial-state data model

The module defines reproducible starting conditions for simulations and system workflows. It separates the declared initial payload from its boundary profile, then derives a canonical manifest and content digest.

| Input concept | Technical representation | Responsibility |
|---|---|---|
| Starting values | Immutable initial-state snapshot | Capture declared values and an explicit random seed |
| Boundary conditions | State plus boundary profile | Keep input data separate from external exchange rules |
| Scenario declaration | Versioned initial-state manifest | Validate required fields and derive a stable content digest |
| Later execution | Lifecycle controller | Record subsequent state transitions and evidence; initial-state capture does not own runtime lifecycle |

The core rule is **state first, boundaries explicit, initialization reproducible**.

## 2. Public API

The module exports:

- `PrimordialState` — immutable snapshot of a JSON-shaped mapping, an unsigned 64-bit seed, a provenance label and a SHA-256 digest.
- `BoundaryProfile` — declarative boundary mode, named invariants and explicit external inputs.
- `GenesisSpec` — a versioned scenario declaration with required fields and human-readable assumptions.
- `NunEngine` — validates a specification and produces a `GenesisReport`.
- `GenesisManifest` — canonical manifest payload and digest, suitable for comparison, cache keys and attaching to a separate evidence record.
- `GenesisFinding`, `GenesisReport`, and `NunError` — structured diagnostics and validation errors.

### Minimal example

```python
from sambu.nun import (
    BoundaryProfile, GenesisSpec, NunEngine, PrimordialState,
)

spec = GenesisSpec(
    "ideal-gas.initial-state",
    origin=PrimordialState(
        {"temperature_K": 300.0, "particle_mass_kg": 6.6e-26},
        seed=17,
        provenance="measured-or-declared-inputs",
    ),
    boundary=BoundaryProfile(
        mode="isolated",
        invariants=("mass", "particle_count"),
    ),
    required_fields=("temperature_K", "particle_mass_kg"),
    assumptions=("uniform initial temperature",),
)

report = NunEngine().prepare(spec)
if not report.is_valid:
    raise ValueError(report.to_dict())

manifest = report.manifest
assert manifest is not None
print(manifest.digest)
```

Run the complete example:

```bash
python examples/nun_genesis.py
```

## 3. Boundary contract

`BoundaryProfile` supports three explicit metadata modes:

| Mode | Contract |
|---|---|
| `isolated` | No external inputs may be declared |
| `exchange` | At least one external input must be named |
| `periodic` | Represents a cyclic boundary declaration; external inputs are not accepted |

`invariants` and `external_inputs` are unique identifier lists. A name cannot be declared in both lists. These fields document the model contract; they do **not** prove conservation or apply boundary conditions to a numerical solver.

## 4. Reproducibility and limits

- Object keys are canonicalized in sorted order; list order is preserved.
- The seed and provenance label contribute to the initial-state digest.
- The manifest includes the original values, boundary declaration, required fields and assumptions. Its SHA-256 digest is stable for identical normalized inputs.
- Nested input data must be JSON-shaped and finite. Non-finite floats, arbitrary Python objects, invalid field identifiers and excessive nesting or item counts are rejected.
- Initial-state payloads are limited to 256 KiB; manifests are limited to 1 MiB by default. The manifest limit is configurable up to 16 MB.
- Accessors return fresh dictionaries. Editing a returned object does not change the stored snapshot or its digest.

A digest provides content identity and tamper detection when compared with a trusted expected value. It is **not** a digital signature, proof of measurement, trusted timestamp or verification of the source named in `provenance`.

## 5. Composition with existing SAMBU layers

Initial-state capture does not duplicate other subsystems:

- **Architecture validation API** (legacy namespace `Judo`) validates component architecture, contracts and dependency order.
- **Continuity** governs explicit lifecycle transitions and its evidence hash chain.
- **NUN** records the initial conditions from which an experiment or system is declared.

A validated report can be supplied as evidence to a separately managed Continuity cycle:

```python
from sambu.continuity import CycleController, CyclePhase

controller = CycleController()
controller.transition(
    CyclePhase.OBSERVING,
    "register validated initial conditions",
    evidence=report.to_dict(),
)
assert controller.verify()
```

This records a transition; it does not launch a simulation or execute an operational workflow.

## 6. Explicit non-goals

The initial-state module does not solve differential equations, infer missing scientific values, enforce physical conservation, generate random samples, run a simulation, start workers, access files or networks, mutate a project, or grant host/device capabilities. Scientific units and dimensional checks remain the responsibility of the relevant SAMBU scientific APIs and the consuming model.

## 7. Verification

```bash
python -m unittest discover -s tests -p "test_nun.py" -v
python -m unittest discover -s tests -v
```

Regression coverage includes deterministic identity, defensive copies, boundary-mode constraints, missing required fields, finite-number checks, bounded manifests and safe failure behavior.
