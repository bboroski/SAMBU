# Native IR micro-pass contract

## Constant folding

`sambu_mir_fold_constants` performs one deterministic, local rewrite pass over a verified MIR v1 function. It does not create new SSA values or change their order. A binary instruction is replaced in place by the matching constant instruction only when both inputs are known constants and the result can be computed without changing the language's arithmetic failure boundary.

## Deliberate non-folding cases

- Signed integer addition, subtraction, or multiplication that would overflow.
- Integer division by zero or the undefined signed case `INT64_MIN / -1`.
- Floating-point division by positive or negative zero.
- Non-finite floating-point operands or results.

Those instructions remain executable operations in MIR. This keeps the pass conservative and prevents the optimizer from hiding runtime errors or introducing C undefined behavior.

## Pass invariants

- The input and output must pass `sambu_mir_verify`.
- SSA value IDs and instruction order remain unchanged.
- Only pure arithmetic/comparison instructions with constant inputs are eligible.
- The optional folded-count output reports the exact number of rewritten instructions.
- Running the pass again is idempotent and reports zero additional folds.
- The pass is deterministic for identical MIR input.

This is a first micro-pass, not a control-flow optimizer, register allocator, machine-code backend, or performance claim. Extend it only with an explicit semantic contract and regression tests for boundary arithmetic.
