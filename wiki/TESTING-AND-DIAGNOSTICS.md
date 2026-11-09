# Testing and diagnostics

## Running tests

The repository uses Python's standard-library unittest discovery and provides a SAMBU test runner.

```bash
python -m unittest discover -s tests -v
sambu-test tests --repeat 2
sambu-test tests --repeat 2 --json
```

The runner performs fresh test discovery for each run and records passed, failed, errored, skipped and expected-failure counts.

## Flaky-test detection

Repeated runs make variation visible. A test is flagged as flaky when its outcome changes across runs, for example passing once and failing or erroring later.

The runner is a diagnostic aid. Its traceback categories and suggested next steps are heuristic; they do not establish a certain root cause. Inspect the complete traceback before changing code.

The current runner supports one to five repetitions per invocation. It runs tests with the permissions of the current Python process, so use a trusted test suite and an isolated environment.

## Lexer and parser diagnostics

The source-aware parser retains line and column information and end-exclusive source ranges.

The package exposes:
- `SourcePosition`;
- `SourceSpan`;
- `Token`;
- `SambuSyntaxError`;
- `tokenize()`;
- `parse()`;
- `parse_ast()`.

The legacy `parse()` result remains available for existing interpreter clients. New tooling should prefer the immutable typed AST returned by `parse_ast()`.

The documented lexical/parser diagnostic family includes stable codes for unexpected characters, unterminated strings and syntax errors. Exact codes must be checked against the current implementation before being used as a permanent external contract.

## Property and regression tests

For changes to core language behavior, add tests for:
- expected successful programs;
- invalid syntax;
- boundary values;
- source locations;
- dimensional mismatches;
- runtime error paths;
- legacy AST compatibility where relevant;
- deterministic output where promised;
- resource ceilings;
- interaction between the modified subsystem and dependent modules.

Every discovered defect should become a repeatable regression case.

## CI and release checks

The root README exposes a CI status badge. The framework guide documents a supported Python version test matrix and a read-only repository audit. Do not infer that a scheduled audit is allowed to push, merge or rewrite the source repository.

## Reporting a defect

A useful report includes:
- SAMBU version and Python version;
- operating system;
- exact command;
- minimal source or Python reproducer;
- expected result;
- actual result;
- complete traceback or diagnostic;
- whether the result repeats consistently.

## Further reading

- [Automated test runner and autopsy](../docs/TEST_AUTOPSY.md)
- [Contributing](CONTRIBUTING.md)
