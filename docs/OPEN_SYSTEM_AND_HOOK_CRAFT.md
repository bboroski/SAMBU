# SAMBU Open-System Dynamics and Hook Craft

This note records the bounded numerical and creative-analysis additions introduced alongside the interpreter built-ins.

## Scientific models

- `planck_time()` returns the Planck time scale as an SI time quantity.
- `canonical_ensemble(levels, T)` computes a stable finite-state canonical distribution. Its partition value is referenced to the lowest supplied energy, so adding a constant offset to every energy does not overflow the sum.
- `microcanonical_ensemble(levels, E, tolerance)` selects all discrete states inside the supplied energy window and assigns equal probability.
- `markov_relaxation(levels, p0, T, rate, elapsed)` applies the exact solution of `dp/dt = rate * (pi - p)`, where `pi` is the canonical stationary distribution. This is a reversible continuous-time Markov reset process with detailed balance.
- `lindblad_dephase(rho, rate, elapsed)` supports a real, symmetric two-level density matrix. It preserves trace and populations and multiplies off-diagonal coherence by `exp(-rate * elapsed)`.
- `onsager_flux(gradients, coefficients)` computes `J = -L X` for a symmetric finite matrix and reports `Xᵀ L X`. It checks symmetry and dissipation for the supplied gradient; it does not prove global positive semidefiniteness for every possible gradient.
- `phonon_decay(amplitude, rate, elapsed)` computes exponential decay of one scalar mode.

These are intentionally small models, not a full quantum simulator. The Markov population model is not a Lindblad solver; the dephasing model has no complex phase or Hamiltonian term. All rates use inverse-time quantities such as `Hz`, and all elapsed times use quantities such as `s`.

## Creative hook diagnostics

`hook_profile(text)` reports a compact 2–4-line form, approximate end-rhyme groups, syllable-count spread, internal spelling echoes, repeated terms and exact repeated lines. It does not create lyrics, infer lexical stress, judge semantic coherence or claim that a hook will be catchy. Its outputs are measurable cues for revision, not an artistic grade.

The existing `text_structure_profile` remains responsible for locating sections and detecting repeated chorus blocks. The new hook profile complements it at the line level.
