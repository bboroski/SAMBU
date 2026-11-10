"""Command-line interface for the first MCL Studio inspection service."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .magento import inspect_module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mcl-studio",
        description="Static Magento XML inspection for MCL Studio (no Magento runtime required).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect = subparsers.add_parser("inspect", help="inspect Magento DI and message-queue XML")
    inspect.add_argument("path", type=Path, help="Magento module or project directory")
    inspect.add_argument("--format", choices=("text", "json"), default="text", dest="output_format")
    args = parser.parse_args(argv)

    try:
        report = inspect_module(args.path)
    except (OSError, ValueError) as exc:
        print(f"mcl-studio: {exc}", file=sys.stderr)
        return 2

    if args.output_format == "json":
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        summary = report.to_dict()["summary"]
        print(f"MCL Studio Magento inspection: {report.root}")
        print(
            "Files: {files_scanned} | preferences: {preferences} | plugins: {plugins} | "
            "topics: {topics} | consumers: {consumers} | exchanges: {exchanges} | "
            "bindings: {bindings} | publishers: {publishers}".format(**summary)
        )
        print(f"Errors: {report.error_count} | warnings: {report.warning_count}")
        for diagnostic in report.diagnostics:
            print(
                f"{diagnostic.severity.upper():7} {diagnostic.code} "
                f"{diagnostic.path}: {diagnostic.message}"
            )
        if report.is_valid:
            print("Static checks passed. This is not Magento XSD or runtime validation.")

    return 0 if report.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
