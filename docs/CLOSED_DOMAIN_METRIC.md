# Closed-Domain Metric Model (CDM-1)

**Status:** experimental scientific-computing model; not an established theory of mass or a general-relativistic solver.

## Purpose

CDM-1 turns the idea of a bounded, non-exchanging domain into a machine-checkable research input. It provides:

- a finite, symmetric 4×4 Lorentzian metric snapshot;
- an explicit choice of metric boundary data;
- independent matter, energy, and information exchange policies;
- an optional energy-accounting check;
- a rest-energy/effective-mass consistency check.

It does **not** claim that geometric closure creates inertial mass, replace the Higgs mechanism, solve Einstein's equations, or infer physical properties from software or hardware boundaries.

## Correct physical scope

The profile in the supplied example is *isolated*: it explicitly forbids matter, energy, and information exchange. “Closed” in thermodynamics is often narrower: a closed system forbids matter exchange but may exchange energy. The three channels are therefore separate flags, not one implicit property.

A boundary condition is selected, not stacked: `dirichlet` fixes the chosen boundary metric data; `neumann` specifies normal-derivative data. They are alternative model choices. A production GR variational problem must define the actual boundary variables, gauge treatment, action, and boundary terms. For the Einstein–Hilbert action with fixed induced boundary metric, the Gibbons–Hawking–York term is part of the well-posed variational setup; a bare statement that the bulk curvature integral is “cancelled” by surface terms is not a complete derivation.

The standard matter stress-energy tensor is obtained by varying the **matter action** with respect to the inverse metric (sign conventions vary). Varying the gravitational Einstein–Hilbert action instead yields the Einstein tensor plus boundary contributions; it is not the same definition of (T_{\mu\nu}).

The relativistic mass-shell relation is
`E² = (pc)² + (mc²)²`.
At rest, `p = 0` and `E₀ = mc²`, so `m = E₀/c²`. If `E₀` is already defined as rest energy, momentum must not be added again to calculate rest mass. CDM-1 validates this energy-equivalent conversion only. It does not derive `E₀` from metric stiffness.

The proposed “metric stiffness creates mass” mechanism is retained as a **falsifiable research hypothesis** only. It needs an explicit action, degrees of freedom, boundary stress definition, dimensional analysis, conservation laws, and a prediction distinguishable from established models before it can be treated as a physical theory.

## Data contract

The canonical example is `data/physics/closed_domain_metric.example.json`; its structural schema is `data/physics/closed_domain_metric.schema.json`.

Required invariants:

1. Four coordinate dimensions and a declared Lorentzian signature (`-+++` or `+---`).
2. A finite, symmetric, non-degenerate 4×4 metric with the declared inertia.
3. Exactly one boundary-data mode (`dirichlet` or `neumann`).
4. Explicit boolean exchange flags; the isolated profile requires all three to be false.
5. When supplied, an energy ledger must close within its declared tolerance.
6. When supplied, `effective_rest_mass_kg` must equal `rest_energy_j / c²` within tolerance.

The validator uses only the Python standard library. Run:

```bash
python tools/validate_closed_domain.py data/physics/closed_domain_metric.example.json
python tools/validate_closed_domain.py --self-test
```

## Software-engineering transfer across the ecosystem

The mathematical analogy is implemented as ordinary engineering controls, never as a claim that software or hardware has a spacetime metric:

- **Boundary:** explicit ownership, allowed ingress/egress, and capability gates.
- **Metric snapshot:** versioned state/configuration snapshot with integrity checks.
- **Conservation ledger:** resource/event accounting with declared units and tolerances.
- **Deformation/pressure:** bounded resource pressure, queue depth, memory usage, or lifecycle load.
- **Effective mass:** derived value only when a measured/declared energy-equivalent input exists; never inferred from a closed boundary alone.
- **Evidence:** declared, observed, unknown, failed, and verified states remain distinct.

Project-specific boundaries are documented in each repository's `docs/CLOSED_DOMAIN_METRIC_INTEGRATION.md`. Existing platform and product guarantees are not expanded by this research pack.

## References

- Gibbons–Hawking–York boundary term and metric boundary data: [Respecting boundaries (2023)](https://link.springer.com/article/10.1007/s13194-023-00545-6).
- Stress-energy definition and Einstein–Hilbert variation: [Gravity lecture notes, University of Helsinki](https://www.mv.helsinki.fi/home/syrasane/gr/gr_lectures_6_2025.pdf).
- Higgs-field role in elementary particle masses: [CERN — The Higgs boson](https://home.cern/science/physics/higgs-boson/).
- Binding energy and the proton's mass: [CERN CMS — Higgs boson](https://cms.cern/index.php/physics/higgs-boson).
- Relativistic energy–momentum relation: [OpenStax — Relativistic Energy](https://openstax.org/books/university-physics-volume-3/pages/5-9-relativistic-energy).

## Release gates

CDM-1 may be used for data validation and controlled numerical experiments. A claim of a new physical mass mechanism requires independent peer review, an explicit derivation, dimensional/unit checks, limiting-case recovery, numerical stability analysis, and a testable prediction. A passing JSON validator is only evidence that an input satisfies this software contract.
