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


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == "new":
        return _new_project(arguments[1:])
    if arguments and arguments[0] == "generate":
        return _generate(arguments[1:])

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
    except (SambuSyntaxError, SambuRuntimeError, ValueError, TypeError, ZeroDivisionError, IndexError, AttributeError) as exc:
        print(f"{filename}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
