#!/usr/bin/env python3
"""Validate the Duck repository documentation contract without third-party packages."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAX_README_CHARS = 10_000
READMES = {
    "README.md": ("README.en.md", "README.ru.md", "Українська"),
    "README.en.md": ("README.md", "README.ru.md", "English"),
    "README.ru.md": ("README.md", "README.en.md", "Русский"),
}
BRAND_TOKENS = ("FFD600", "111111")
PRODUCT_SPEC = ROOT / "docs" / "PRODUCT_SYSTEM.md"


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def validate_readmes(errors: list[str]) -> int:
    total = 0
    for filename, required in READMES.items():
        path = ROOT / filename
        if not path.is_file():
            fail(f"Missing required language file: {filename}", errors)
            continue
        content = path.read_text(encoding="utf-8")
        length = len(content)
        total += length
        if length > MAX_README_CHARS:
            fail(f"{filename}: {length} characters exceeds {MAX_README_CHARS}", errors)
        for marker in required:
            if marker not in content:
                fail(f"{filename}: missing language/navigation marker {marker!r}", errors)
        for token in BRAND_TOKENS:
            if token not in content.upper():
                fail(f"{filename}: missing Duck design token {token}", errors)
        print(f"PASS {filename}: {length}/{MAX_README_CHARS} characters")
    return total


def validate_product_spec(errors: list[str]) -> None:
    if not PRODUCT_SPEC.is_file():
        fail("Missing docs/PRODUCT_SYSTEM.md", errors)
        return
    content = PRODUCT_SPEC.read_text(encoding="utf-8")
    for marker in ("CAP-10000", "Українська", "English", "Русский", "#FFD600", "#111111"):
        if marker not in content:
            fail(f"docs/PRODUCT_SYSTEM.md: missing required marker {marker!r}", errors)
    print(f"PASS docs/PRODUCT_SYSTEM.md: {len(content)} characters")


def main() -> int:
    errors: list[str] = []
    total = validate_readmes(errors)
    validate_product_spec(errors)
    if errors:
        print("\nDuck repository quality gate failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(f"\nDuck repository quality gate passed ({len(READMES)} language files; {total} README characters).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
