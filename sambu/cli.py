"""Command-line entry point for SAMBU."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from . import __version__
from .interpreter import execute
from .lexer import SambuSyntaxError
from .runtime import SambuRuntimeError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sambu",
        description="SAMBU — a small scientific language for statistical mechanics and kinetic theory.",
    )
    parser.add_argument("file", nargs="?", help="SAMBU source file (.sambu)")
    parser.add_argument("-c", "--code", help="execute source passed as a string")
    parser.add_argument("--version", action="version", version=f"SAMBU {__version__}")
    args = parser.parse_args(argv)

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
