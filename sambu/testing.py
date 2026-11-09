"""Repeatable unittest runner with a compact diagnostic autopsy."""
from __future__ import annotations
import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
import unittest

@dataclass(frozen=True, slots=True)
class TestFailure:
    iteration: int
    test_id: str
    category: str
    summary: str
    traceback: str

@dataclass(frozen=True, slots=True)
class TestRunSnapshot:
    iteration: int
    total: int
    passed: int
    failed: int
    errors: int
    skipped: int
    expected_failures: int
    output: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

@dataclass(frozen=True, slots=True)
class AutotestReport:
    runs: tuple[TestRunSnapshot, ...]
    failures: tuple[TestFailure, ...]
    flaky_tests: tuple[str, ...]

    @property
    def all_passed(self) -> bool:
        return bool(self.runs) and all(run.total > 0 and run.failed == 0 and run.errors == 0 for run in self.runs)

    def to_dict(self) -> dict[str, object]:
        return {
            "all_passed": self.all_passed,
            "runs": [run.to_dict() for run in self.runs],
            "failures": [asdict(item) for item in self.failures],
            "flaky_tests": list(self.flaky_tests),
            "autopsy": autopsy(self),
        }

def _failure_category(traceback: str) -> str:
    if "AssertionError" in traceback: return "assertion"
    if "ModuleNotFoundError" in traceback or "ImportError" in traceback: return "dependency_or_import"
    if "TimeoutError" in traceback or "timed out" in traceback.casefold(): return "timeout"
    if "PermissionError" in traceback: return "permission"
    if "SyntaxError" in traceback: return "syntax"
    if "TypeError" in traceback: return "type"
    if "ValueError" in traceback: return "value"
    return "runtime_or_unknown"

def _summary(traceback: str) -> str:
    lines = [line.strip() for line in traceback.splitlines() if line.strip()]
    if not lines: return "No traceback text was captured"
    for line in reversed(lines):
        if re.search(r"(Error|Exception|AssertionError):", line): return line[:240]
    return lines[-1][:240]

class _TrackingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes: dict[str, str] = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes[test.id()] = "passed"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes[test.id()] = "failed"

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes[test.id()] = "error"

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes[test.id()] = "skipped"

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.outcomes[test.id()] = "expected_failure"

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.outcomes[test.id()] = "failed"

def run_autotests(start_dir: str | Path = "tests", *, pattern: str = "test_*.py", repeat: int = 1) -> AutotestReport:
    """Discover and run a test suite one or more times (maximum five)."""
    directory = Path(start_dir)
    if not directory.exists() or not directory.is_dir():
        raise ValueError(f"test directory does not exist: {directory}")
    if not isinstance(pattern, str) or not pattern.strip() or "/" in pattern or "\\" in pattern:
        raise ValueError("pattern must be a non-empty filename pattern")
    if isinstance(repeat, bool) or not isinstance(repeat, int) or not 1 <= repeat <= 5:
        raise ValueError("repeat must be an integer from 1 to 5")
    snapshots: list[TestRunSnapshot] = []
    failures: list[TestFailure] = []
    observed: dict[str, set[str]] = {}

    for iteration in range(1, repeat + 1):
        suite = unittest.TestLoader().discover(str(directory), pattern=pattern)
        from io import StringIO
        output = StringIO()
        result = unittest.TextTestRunner(stream=output, verbosity=2, resultclass=_TrackingResult).run(suite)
        outcomes = result.outcomes
        for test_id, outcome in outcomes.items():
            observed.setdefault(test_id, set()).add(outcome)
        for test, trace in result.failures:
            failures.append(TestFailure(iteration, test.id(), "assertion", _summary(trace), trace))
        for test, trace in result.errors:
            failures.append(TestFailure(iteration, test.id(), _failure_category(trace), _summary(trace), trace))
        snapshots.append(TestRunSnapshot(
            iteration, result.testsRun,
            sum(v == "passed" for v in outcomes.values()),
            sum(v == "failed" for v in outcomes.values()),
            sum(v == "error" for v in outcomes.values()),
            sum(v == "skipped" for v in outcomes.values()),
            sum(v == "expected_failure" for v in outcomes.values()),
            output.getvalue(),
        ))
    flaky = tuple(sorted(
        test_id for test_id, states in observed.items()
        if "passed" in states and ({"failed", "error"} & states)
    ))
    return AutotestReport(tuple(snapshots), tuple(failures), flaky)

def autopsy(report: AutotestReport) -> dict[str, object]:
    """Summarize failures heuristically; this does not infer certain root causes."""
    categories: dict[str, int] = {}
    for failure in report.failures:
        categories[failure.category] = categories.get(failure.category, 0) + 1
    recommendations: list[str] = []
    if categories.get("assertion"):
        recommendations.append("Compare expected and actual values; inspect the smallest failing assertion.")
    if categories.get("dependency_or_import"):
        recommendations.append("Check optional extras, package installation, and import paths.")
    if categories.get("timeout"):
        recommendations.append("Isolate network or timing dependencies and add bounded timeouts.")
    if categories.get("type") or categories.get("value"):
        recommendations.append("Inspect input contracts, runtime types, and boundary validation.")
    if report.flaky_tests:
        recommendations.append("Repeat flaky tests with deterministic fixtures and isolate shared state.")
    if not recommendations and report.all_passed:
        recommendations.append("No failing tests were observed in the recorded runs.")
    return {
        "status": "passed" if report.all_passed else "needs_attention",
        "failure_categories": categories,
        "flaky_tests": list(report.flaky_tests),
        "recommendations": recommendations,
        "limitations": "Classification is heuristic; inspect the complete traceback before changing code.",
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sambu-test", description="Run SAMBU tests and summarize repeated failures.")
    parser.add_argument("start_dir", nargs="?", default="tests")
    parser.add_argument("--pattern", default="test_*.py")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args(argv)
    try:
        report = run_autotests(args.start_dir, pattern=args.pattern, repeat=args.repeat)
    except (OSError, ValueError) as exc:
        print(f"sambu-test: {exc}", file=sys.stderr)
        return 2
    if args.json_output:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        for run in report.runs:
            print(f"Run {run.iteration}: {run.passed} passed, {run.failed} failed, {run.errors} errors, {run.skipped} skipped / {run.total} total")
        summary = autopsy(report)
        print(f"Autopsy: {summary['status']}")
        for category, count in summary["failure_categories"].items():
            print(f"  {category}: {count}")
        for recommendation in summary["recommendations"]:
            print(f"  -> {recommendation}")
        if report.flaky_tests: print("Flaky tests: " + ", ".join(report.flaky_tests))
    return 0 if report.all_passed else 1

if __name__ == "__main__":
    raise SystemExit(main())

__all__ = ["TestFailure", "TestRunSnapshot", "AutotestReport", "run_autotests", "autopsy", "main"]
