# SAMBU semantic analysis

**Status:** implemented conservative first pass · **API:** `sambu.analyze`, `sambu.analyze_ast` · **CLI:** `sambu check`

SAMBU's semantic pass runs after parsing and before execution. It consumes the immutable,
source-aware AST and never evaluates the program or invokes its built-ins.

## Current checks

- lexical name resolution for values, functions, classes, interfaces and traits;
- duplicate declarations within one lexical scope;
- function parameter and local-scope handling, including nested blocks and loop variables;
- function-call arity for statically known SAMBU functions;
- invalid top-level `return`;
- definite primitive numeric-operator and comparison mismatches;
- source-ranged diagnostics with stable `SAMBU-SEM-*` codes.

The analyzer reuses the runtime's canonical built-in and SI-unit registries. It deliberately
treats dynamic object members, host-provided values, unknown function results and domain
library return types as unknown rather than guessing. This keeps the first pass conservative
and avoids rejecting valid dynamic SAMBU programs.

## Usage

```python
from sambu import analyze

report = analyze("""
fn square(value) { return value * value }
let answer = square(12)
""")

if not report.valid:
    for diagnostic in report.diagnostics:
        print(diagnostic.code, diagnostic.span, diagnostic.message)
```

```sh
sambu check path/to/program.sambu
sambu check path/to/program.sambu --json
```

The check command reports syntax and semantic failures and exits non-zero when errors exist.
It does not run the source program.

## Deliberate limits

This is a static-analysis foundation, not yet a complete static type system. SAMBU source
does not currently declare parameter or return types. The analyzer therefore does not claim
sound whole-program typing, SI-dimension checking before execution, generic inference,
ownership/borrow checking, effect checking, exhaustive matching, module resolution or
interprocedural return inference. Those features require explicit language-level type and
module contracts. Runtime checks remain authoritative for dynamic and domain-specific values.

## Compatibility

The existing `parse()` tuple AST, `parse_ast()` typed AST, interpreter and runtime behavior
are unchanged. Analysis is opt-in through the API or CLI. No source is executed during checking.
