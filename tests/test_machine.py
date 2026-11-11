from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from sambu.machine import (
    CapabilityDeniedError,
    CodeSampler,
    CodeSamplingError,
    EffortAmplification,
    FailureLedger,
    PlywoodDesign,
    PlywoodLayer,
    SambuMachine,
    default_plywood_design,
)
from sambu.interpreter import execute


class PlywoodDesignTests(unittest.TestCase):
    def test_reference_laminate_is_valid_and_topologically_ordered(self):
        design = default_plywood_design()
        result = design.validate()
        self.assertTrue(result.valid, result.issues)
        self.assertEqual(result.order[0], "source_surface")
        self.assertLess(result.order.index("runtime_core"), result.order.index("domain_services"))
        self.assertLess(result.order.index("machine_control"), result.order.index("ide_services"))

    def test_missing_contract_dependency_is_rejected(self):
        design = PlywoodDesign((
            PlywoodLayer("foundation", "foundation", provides=("source",)),
            PlywoodLayer("editor", "tooling", depends_on=("foundation",), requires=("compiler",)),
        ))
        result = design.validate()
        self.assertFalse(result.valid)
        self.assertTrue(any("compiler" in issue for issue in result.issues))

    def test_dependency_cycle_is_rejected(self):
        design = PlywoodDesign((
            PlywoodLayer("left", "core", depends_on=("right",)),
            PlywoodLayer("right", "core", depends_on=("left",)),
        ))
        result = design.validate()
        self.assertFalse(result.valid)
        self.assertTrue(any("cycle" in issue for issue in result.issues))

    def test_unknown_layer_dependency_is_reported_without_exception(self):
        design = PlywoodDesign((
            PlywoodLayer("editor", "tooling", depends_on=("missing-runtime",)),
        ))
        result = design.validate()
        self.assertFalse(result.valid)
        self.assertTrue(any("unknown dependency" in issue for issue in result.issues))


class CodeSamplerTests(unittest.TestCase):
    def test_one_in_one_hundred_ast_sampling_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "many.sambu"
            path.write_text(
                "\n".join(f"let value_{index} = {index}" for index in range(200)),
                encoding="utf-8",
            )
            sampler = CodeSampler()
            first = sampler.sample(path, denominator=100, seed=77)
            second = sampler.sample(path, denominator=100, seed=77)
            self.assertEqual(first.statements_found, 200)
            self.assertEqual(first.statements_sampled, 2)
            self.assertEqual(
                [item.fingerprint for item in first.samples],
                [item.fingerprint for item in second.samples],
            )
            self.assertEqual(first.samples, second.samples)

    def test_nonempty_small_file_still_contributes_one_sample(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "small.sambu"
            path.write_text("let answer = 42\nprint(answer)\n", encoding="utf-8")
            report = CodeSampler().sample(path, denominator=100)
            self.assertEqual(report.statements_found, 2)
            self.assertEqual(report.statements_sampled, 1)

    def test_invalid_source_and_symlinks_are_not_sampled(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid = Path(directory) / "invalid.sambu"
            invalid.write_text("let broken =", encoding="utf-8")
            with self.assertRaises(CodeSamplingError):
                CodeSampler().sample(invalid)
            link = Path(directory) / "linked.sambu"
            try:
                link.symlink_to(invalid)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks unavailable")
            with self.assertRaises(CodeSamplingError):
                CodeSampler().sample(link)

    def test_sampler_enforces_aggregate_workspace_source_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "first.sambu").write_text("1", encoding="utf-8")
            (root / "second.sambu").write_text("2", encoding="utf-8")
            sampler = CodeSampler(max_source_bytes=100, max_total_source_bytes=1)
            with self.assertRaisesRegex(CodeSamplingError, "total bytes"):
                sampler.sample(root, denominator=100)

    def test_sample_excerpt_is_exact_and_byte_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "long.sambu"
            path.write_text('let label = "' + ("x" * 50_000) + '"', encoding="utf-8")
            report = CodeSampler().sample(path)
            self.assertEqual(report.statements_sampled, 1)
            self.assertLessEqual(
                len(report.samples[0].excerpt.encode("utf-8")),
                8_192 + len("\\n… <sample truncated>".encode("utf-8")),
            )
            self.assertTrue(report.samples[0].excerpt.startswith("let label = "))


class FailureLedgerTests(unittest.TestCase):
    def test_failures_are_deduplicated_redacted_and_roundtrip(self):
        ledger = FailureLedger(capacity=4)
        first = ledger.record(
            RuntimeError("token=secret-value failure"),
            source="let x = 1",
            category="runtime",
            context="example",
        )
        repeated = ledger.record(
            RuntimeError("token=secret-value failure"),
            source="let x = 1",
            category="runtime",
            context="example",
        )
        self.assertEqual(first.fingerprint, repeated.fingerprint)
        self.assertEqual(repeated.occurrences, 2)
        self.assertNotIn("secret-value", repeated.message)
        restored = FailureLedger.from_json(ledger.to_json())
        self.assertEqual(restored.snapshot(), ledger.snapshot())

    def test_failure_ledger_is_bounded_to_ten_thousand(self):
        with self.assertRaises(ValueError):
            FailureLedger(capacity=10_001)
        ledger = FailureLedger(capacity=2)
        ledger.record("first")
        ledger.record("second")
        ledger.record("third")
        self.assertEqual(ledger.count, 2)
        self.assertEqual([item.message for item in ledger.snapshot()], ["second", "third"])

    def test_invalid_ledger_schema_is_rejected(self):
        with self.assertRaises(ValueError):
            FailureLedger.from_json('{"schema_version": 99, "capacity": 2, "records": []}')

    def test_ledger_import_rejects_tampered_fingerprint(self):
        import json

        ledger = FailureLedger()
        ledger.record("original failure", source="let x = 1", context="fixture")
        payload = json.loads(ledger.to_json())
        payload["records"][0]["message"] = "tampered failure"
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            FailureLedger.from_json(json.dumps(payload))

    def test_ledger_schema_rejects_boolean_version(self):
        with self.assertRaises(ValueError):
            FailureLedger.from_json('{"schema_version": true, "capacity": 1, "records": []}')


class AmplificationEffortTests(unittest.TestCase):
    def test_effort_is_accepted_only_with_improvement_and_all_tests_pass(self):
        report = EffortAmplification.evaluate(
            {"latency_ms": 100, "memory_mb": 200},
            {"latency_ms": 90, "memory_mb": 180},
            lower_is_better=("latency_ms", "memory_mb"),
            effort_hours=2,
            tests_passed=100,
            tests_total=100,
        )
        self.assertTrue(report.accepted)
        self.assertAlmostEqual(report.mean_improvement_percent, 10.0)
        self.assertAlmostEqual(report.amplification_index, 5.0)

    def test_regression_or_failed_test_rejects_amplification(self):
        report = EffortAmplification.evaluate(
            {"latency_ms": 100, "memory_mb": 100},
            {"latency_ms": 90, "memory_mb": 110},
            lower_is_better=("latency_ms", "memory_mb"),
            effort_hours=1,
            tests_passed=99,
            tests_total=100,
        )
        self.assertFalse(report.accepted)
        self.assertEqual(report.regressions, ("memory_mb",))

    def test_effort_amplification_rejects_unknown_metric_direction(self):
        with self.assertRaisesRegex(ValueError, "unknown metrics"):
            EffortAmplification.evaluate(
                {"latency_ms": 10},
                {"latency_ms": 9},
                lower_is_better=("memory_mb",),
                effort_hours=1,
                tests_passed=1,
                tests_total=1,
            )


class SambuMachineTests(unittest.TestCase):
    def test_workspace_check_records_invalid_source_and_validates_architecture(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "good.sambu").write_text("let answer = 42\n", encoding="utf-8")
            (root / "bad.sambu").write_text("let answer =\n", encoding="utf-8")
            machine = SambuMachine()
            report = machine.check_workspace(root)
            self.assertFalse(report.valid)
            self.assertEqual(report.files_checked, 2)
            self.assertEqual(report.valid_files, 1)
            self.assertEqual(len(report.issues), 1)
            self.assertEqual(machine.failures.count, 1)
            self.assertTrue(report.architecture.valid)

    def test_machine_runs_source_and_records_runtime_failures(self):
        machine = SambuMachine()
        self.assertEqual(machine.run_source("let x = 4 + 5\nprint(x)", output=lambda _: None), 9)
        with self.assertRaises(ZeroDivisionError):
            machine.run_source("let x = 1 / 0", context="broken.sambu")
        self.assertEqual(machine.failures.count, 1)

    def test_restriction_levels_deny_capabilities_by_default(self):
        sealed = SambuMachine(profile="sealed")
        with self.assertRaises(CapabilityDeniedError):
            sealed.run_source("print(42)", output=lambda _: None)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.sambu").write_text("let answer = 42\n", encoding="utf-8")
            self.assertTrue(sealed.check_workspace(root).valid)
            self.assertTrue(sealed.inspect_architecture()["valid"])
            self.assertEqual(sealed.sample_code(root).files_scanned, 1)

        sandbox = SambuMachine(profile="sandbox")
        self.assertEqual(sandbox.run_source("1 + 1"), 2)
        with self.assertRaises(ValueError):
            SambuMachine(profile="unsealed")

    def test_mulberry_charlotte_reference_workload_executes(self):
        example = Path(__file__).resolve().parents[1] / "examples" / "mulberry_charlotte.sambu"
        output: list[str] = []
        execute(example.read_text(encoding="utf-8"), output=output.append)
        self.assertEqual(output[0], "Batch scaling fixture")
        self.assertEqual(output[1], "12")
        self.assertEqual(
            [float(value) for value in output[2:8]],
            [270.0, 135.0, 180.0, 4.5, 390.0, 270.0],
        )
        self.assertEqual(float(output[-1]), 108.75)


if __name__ == "__main__":
    unittest.main()
