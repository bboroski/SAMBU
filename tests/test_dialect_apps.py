from __future__ import annotations

import unittest
from pathlib import Path

from sambu.dialects import transpile
from sambu.interpreter import execute
from sambu.parser import parse_ast


ROOT = Path(__file__).resolve().parents[1] / "examples" / "dialect_apps"


class DialectApplicationTests(unittest.TestCase):
    def test_each_dialect_has_ten_parseable_executable_applications(self):
        for dialect in ("pascal", "delphi", "fortran"):
            with self.subTest(dialect=dialect):
                paths = sorted((ROOT / dialect).glob("*.sambu"))
                self.assertEqual(len(paths), 10, f"{dialect} suite must contain exactly ten apps")
                for path in paths:
                    with self.subTest(application=path.name):
                        source = path.read_text(encoding="utf-8")
                        result = transpile(source, dialect)
                        self.assertEqual(result.dialect, dialect)
                        self.assertEqual(
                            len(result.source_lines),
                            len(result.generated_source.splitlines()),
                        )
                        parse_ast(result.generated_source)
                        output: list[str] = []
                        execute(result.generated_source, output=output.append)
                        self.assertTrue(output, "application should produce a visible result")


if __name__ == "__main__":
    unittest.main()
