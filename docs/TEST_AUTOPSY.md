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
