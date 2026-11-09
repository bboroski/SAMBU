from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from sambu.ide import IDEError, SambuIDE


class SambuIDEDocumentTests(unittest.TestCase):
    def test_inspect_builds_outline_and_token_snapshot(self):
        ide = SambuIDE()
        report = ide.open_document(
            "file:///workspace/duck.sambu",
            """
fn quack(value) {
  return value
}
class Duck {
  fn speak(self) {
    return "quack"
  }
}
""",
            version=1,
        )
        self.assertTrue(report.syntax_valid)
        self.assertGreater(report.token_count, 0)
        self.assertEqual([item.name for item in report.symbols], ["quack", "Duck"])
        self.assertEqual(report.symbols[1].children[0].name, "speak")
        self.assertEqual(ide.document_version("file:///workspace/duck.sambu"), 1)

    def test_unencodable_document_text_is_rejected_cleanly(self):
        ide = SambuIDE()
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            ide.open_document("untitled:unicode", "\ud800", version=1)

    def test_syntax_errors_become_source_diagnostics(self):
        ide = SambuIDE()
        report = ide.open_document("untitled:broken", "let invalid =\n", version=1)
        self.assertFalse(report.syntax_valid)
        self.assertEqual(len(report.diagnostics), 1)
        self.assertEqual(report.diagnostics[0].severity, "error")
        self.assertEqual(report.diagnostics[0].code, "SAMBU-P001")

    def test_reopening_document_requires_a_newer_version(self):
        ide = SambuIDE()
        uri = "file:///workspace/reopened.sambu"
        ide.open_document(uri, "let a = 1", version=1)
        with self.assertRaises(IDEError):
            ide.open_document(uri, "let a = 2", version=1)
        self.assertEqual(ide.document_version(uri), 1)

    def test_document_changes_reject_stale_versions(self):
        ide = SambuIDE()
        uri = "file:///workspace/main.sambu"
        ide.open_document(uri, "let a = 1", version=3)
        ide.change_document(uri, "let a = 2", version=4)
        self.assertEqual(ide.document_version(uri), 4)
        with self.assertRaises(IDEError):
            ide.change_document(uri, "let a = 3", version=4)
        with self.assertRaises(IDEError):
            ide.change_document("missing.sambu", "let a = 4", version=1)

    def test_completion_is_prefix_filtered_and_bounded(self):
        ide = SambuIDE()
        self.assertIn("channel", ide.complete("chan"))
        self.assertIn("class", ide.complete("cl"))
        self.assertEqual(len(ide.complete("", limit=3)), 3)
        with self.assertRaises(ValueError):
            ide.complete("", limit=0)

    def test_close_document_reports_if_it_was_open(self):
        ide = SambuIDE()
        ide.open_document("memory:one", "let a = 1")
        self.assertTrue(ide.close_document("memory:one"))
        self.assertFalse(ide.close_document("memory:one"))


class SambuIDEWorkspaceTests(unittest.TestCase):
    def test_workspace_and_code_sample_delegate_to_machine(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "main.sambu").write_text("fn main() { return 7 }\n", encoding="utf-8")
            ide = SambuIDE()
            report = ide.inspect_workspace(root)
            sample = ide.sample_code(root, denominator=100, seed=2)
            self.assertTrue(report.valid)
            self.assertEqual(report.files_checked, 1)
            self.assertEqual(sample.files_scanned, 1)
            self.assertGreaterEqual(sample.statements_sampled, 1)


if __name__ == "__main__":
    unittest.main()
