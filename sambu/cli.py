"""Command-line entry point for SAMBU."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .interpreter import execute
from .lexer import SambuSyntaxError
from .runtime import SambuRuntimeError


def _new_project(argv: list[str]) -> int:
    from .project import ProjectGenerationError, create_project

    parser = argparse.ArgumentParser(prog="sambu new")
    parser.add_argument("name", help="lowercase application name, e.g. blog_app")
    parser.add_argument("--path", type=Path, help="destination directory (defaults to NAME)")
    args = parser.parse_args(argv)
    try:
        created = create_project(args.name, args.path)
    except ProjectGenerationError as exc:
        print(f"sambu new: {exc}", file=sys.stderr)
        return 2
    destination = args.path if args.path is not None else Path(args.name)
    print(f"Created SAMBU project {args.name!r} at {destination} ({len(created)} files).")
    print("Run: sambu " + str(destination / "src" / "main.sambu"))
    return 0


def _generate(argv: list[str]) -> int:
    from .project import ProjectGenerationError, generate_scaffold

    parser = argparse.ArgumentParser(prog="sambu generate")
    subparsers = parser.add_subparsers(dest="action", required=True)
    scaffold = subparsers.add_parser("scaffold", help="generate model/controller/view starters")
    scaffold.add_argument("model", help="PascalCase singular model name, e.g. Post")
    scaffold.add_argument("fields", nargs="+", help="field declarations such as title:string")
    scaffold.add_argument("--path", type=Path, default=Path("."), help="SAMBU project root")
    args = parser.parse_args(argv)
    try:
        created = generate_scaffold(args.path, args.model, args.fields)
    except ProjectGenerationError as exc:
        print(f"sambu generate scaffold: {exc}", file=sys.stderr)
        return 2
    print(f"Generated {len(created)} scaffold files for {args.model}.")
    for path in created:
        print(f"  {path}")
    print("Note: generated MVC, routing, ORM and migration files are starters, not an active web runtime.")
    return 0


def _machine(argv: list[str]) -> int:
    import json
    from .machine import SambuMachine

    parser = argparse.ArgumentParser(prog="sambu machine")
    commands = parser.add_subparsers(dest="action", required=True)
    check = commands.add_parser("check", help="parse-check every .sambu file in a workspace")
    check.add_argument("path", type=Path)
    check.add_argument("--json", action="store_true", dest="as_json")
    sample = commands.add_parser("sample", help="take a deterministic sample of typed AST statements")
    sample.add_argument("path", type=Path)
    sample.add_argument("--ratio", type=int, default=100, help="sample one statement per N statements in each file")
    sample.add_argument("--seed", type=int, default=0)
    sample.add_argument("--json", action="store_true", dest="as_json")
    architecture = commands.add_parser("architecture", help="validate the reference plywood layer graph")
    architecture.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    machine = SambuMachine(profile="sealed")
    try:
        if args.action == "check":
            report = machine.check_workspace(args.path)
            if args.as_json:
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(f"SAMBU Machine: {report.valid_files}/{report.files_checked} source files parsed")
                for issue in report.issues:
                    print(f"{issue.path}:{issue.line}:{issue.column}: {issue.code}: {issue.message}")
                for issue in report.architecture.issues:
                    print(f"architecture: {issue}")
            return 0 if report.valid else 1
        if args.action == "sample":
            report = machine.sample_code(args.path, denominator=args.ratio, seed=args.seed)
            if args.as_json:
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(
                    f"Sampled {report.statements_sampled}/{report.statements_found} AST statements "
                    f"from {report.files_scanned} files at 1:{report.denominator} (seed={report.seed})."
                )
                for item in report.samples:
                    print(f"\n{item.path}:{item.start_line}-{item.end_line} [{item.statement_type}]")
                    print(item.excerpt)
            return 0
        result = machine.inspect_architecture()
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print("SAMBU plywood architecture")
            print(" -> ".join(result["order"]))
            for issue in result["issues"]:
                print(f"ERROR: {issue}")
        return 0 if result["valid"] else 1
    except Exception as exc:
        print(f"sambu machine: {exc}", file=sys.stderr)
        return 2


def _ide(argv: list[str]) -> int:
    import json
    from .ide import SambuIDE

    parser = argparse.ArgumentParser(prog="sambu ide")
    commands = parser.add_subparsers(dest="action", required=True)
    inspect = commands.add_parser("inspect", help="inspect one .sambu document")
    inspect.add_argument("path", type=Path)
    inspect.add_argument("--format", choices=("text", "json"), default="text")
    workspace = commands.add_parser("workspace", help="parse-check a .sambu workspace")
    workspace.add_argument("path", type=Path)
    workspace.add_argument("--format", choices=("text", "json"), default="text")
    complete = commands.add_parser("complete", help="list built-in and keyword completions")
    complete.add_argument("prefix", nargs="?", default="")
    complete.add_argument("--limit", type=int, default=50)
    args = parser.parse_args(argv)
    ide = SambuIDE()
    try:
        if args.action == "inspect":
            source = args.path.read_text(encoding="utf-8")
            report = ide.open_document(str(args.path.resolve()), source)
            if args.format == "json":
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(f"{report.uri} — {'syntax OK' if report.syntax_valid else 'syntax errors'}")
                print(f"Lines: {report.line_count} | tokens: {report.token_count} | SHA-256: {report.sha256}")
                for symbol in report.symbols:
                    print(f"{symbol.kind:10} {symbol.name} ({symbol.start_line}-{symbol.end_line})")
                    for child in symbol.children:
                        print(f"  {child.kind:8} {child.name} ({child.start_line}-{child.end_line})")
                for diagnostic in report.diagnostics:
                    print(
                        f"{diagnostic.line}:{diagnostic.column}: "
                        f"{diagnostic.code}: {diagnostic.message}"
                    )
            return 0 if report.syntax_valid else 1
        if args.action == "workspace":
            report = ide.inspect_workspace(args.path)
            if args.format == "json":
                print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
            else:
                print(f"SAMBU IDE: {report.valid_files}/{report.files_checked} files parsed")
                for issue in report.issues:
                    print(f"{issue.path}:{issue.line}:{issue.column}: {issue.code}: {issue.message}")
            return 0 if report.valid else 1
        values = ide.complete(args.prefix, limit=args.limit)
        print("\n".join(values))
        return 0
    except Exception as exc:
        print(f"sambu ide: {exc}", file=sys.stderr)
        return 2


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "new":
        return _new_project(arguments[1:])
    if arguments and arguments[0] == "generate":
        return _generate(arguments[1:])
    if arguments and arguments[0] == "machine":
        return _machine(arguments[1:])
    if arguments and arguments[0] == "ide":
        return _ide(arguments[1:])

    parser = argparse.ArgumentParser(
        prog="sambu",
        description="SAMBU — a scientific language and convention-based project toolkit.",
    )
    parser.add_argument("file", nargs="?", help="SAMBU source file (.sambu)")
    parser.add_argument("-c", "--code", help="execute source passed as a string")
    parser.add_argument("--version", action="version", version=f"SAMBU {__version__}")
    args = parser.parse_args(arguments)

    if bool(args.file) == bool(args.code):
        parser.error("provide exactly one source file or -c/--code")

    if args.code is not None:
        source = args.code
        filename = "<command>"
    else:
        path = Path(args.file)
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"sambu: cannot read {path}: {exc}", file=sys.stderr)
            return 2
        filename = str(path)

    try:
        execute(source)
    except (SambuSyntaxError, SambuRuntimeError, RuntimeError, ValueError, TypeError, ZeroDivisionError, IndexError, AttributeError) as exc:
        print(f"{filename}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
