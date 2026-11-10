# Automated tests and test autopsy

Run the repository suite with the standard library or the SAMBU runner:

~~~bash
python -m unittest discover -s tests -v
sambu-test tests --repeat 2
sambu-test tests --repeat 2 --json
~~~

sambu-test discovers a fresh suite for each run and records passed, failed, errored, skipped and expected-failure counts. Repeated runs make pass/fail variation visible; tests that pass in one run and fail or error in another are listed as flaky.

The autopsy groups tracebacks into heuristic categories (assertion, import or dependency, timeout, permission, syntax, type, value, and runtime or unknown) and suggests the next diagnostic step. It does not infer a certain root cause. Inspect the complete traceback before changing implementation.

Limits: one to five runs per invocation; the runner executes tests in the selected directory with the current Python process permissions. Use isolated environments and trusted test suites.

## Machine Failure Ledger

SAMBU Machine includes a bounded in-memory `FailureLedger` for recurring failure signatures. It stores up to 10,000 unique records by default, deduplicates repeated fingerprints, increments occurrence counts and evicts the oldest distinct signature at capacity. Records contain a redacted error message, error class, bounded context and a source hash rather than the full source file.

Export and import use a versioned JSON schema. Redaction covers common credential patterns but cannot guarantee detection of every secret or personal datum; error messages and context labels must never be used as secret containers. The ledger is not a forensic vault or automatic telemetry service.

The Machine can record source parsing/workspace errors and failures from its explicit `run_source` entry point. Ordinary `sambu-test` execution does not silently upload or persist test contents in this ledger.
