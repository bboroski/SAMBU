# RCME native module

Repository-specific native C11 adapter for the Recursive Cross-Domain Matrix Engine.

## Scope
- Caller-owned matrix views; no heap allocation, global mutable state, or implicit I/O.
- Checked matrix multiplication and transpose.
- One bounded recursive composition: normalize(M × A × transpose(M) + B).
- Frobenius normalization, residual measurement, finite-value and dimension checks.
- Domain-specific diagonal weighting for: Scientific modeling and reproducible quantum-inspired numerical experiments

## Build and test
```sh
cc -std=c11 -Wall -Wextra -Werror -pedantic -Ircme/include \
  rcme/src/rcme.c rcme/src/rcme_domain.c rcme/tests/test_rcme.c -lm -o rcme-test
./rcme-test
```

This module is an isolated additive slice. It does not modify existing application APIs, infer physical laws, execute hardware operations, or claim quantum speedup. Quantum, biological, pipeline, and geospatial inputs must be supplied by separately validated domain adapters.
