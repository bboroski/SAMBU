#!/usr/bin/env python3
"""Validate the repository's trilingual README and shared Duck UI contract.

This gate checks static repository evidence only. It does not claim that a GUI,
hardware target, boot image, or platform integration has been runtime-qualified.
"""
from __future__ import annotations

import json
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
MATERIAL_SELECTORS = (".duck-glass", ".duck-metal", ".duck-paper")


def validate_readmes(errors: list[str]) -> int:
    total = 0
    repo_name = ROOT.name
    for filename, required in READMES.items():
        path = ROOT / filename
        if not path.is_file():
            errors.append(f"Missing required language file: {filename}")
            continue
        content = path.read_text(encoding="utf-8")
        total += len(content)
        if not content.strip():
            errors.append(f"{filename}: file is empty")
        if len(content) > MAX_README_CHARS:
            errors.append(
                f"{filename}: {len(content)} characters exceeds {MAX_README_CHARS}"
            )
        for marker in required:
            if marker not in content:
                errors.append(f"{filename}: missing language/navigation marker {marker!r}")
        for token in BRAND_TOKENS:
            if token not in content.upper():
                errors.append(f"{filename}: missing Duck design token {token}")
        print(f"PASS {filename}: {len(content)}/{MAX_README_CHARS} characters")

    if not any(repo_name.casefold() in (ROOT / name).read_text(encoding="utf-8").casefold()
               for name in READMES if (ROOT / name).is_file()):
        errors.append(f"No README identifies the canonical repository name {repo_name!r}")
    return total


def validate_design_system(errors: list[str]) -> None:
    css_path = ROOT / "assets" / "duck-ui" / "duck-ui.css"
    tokens_path = ROOT / "design" / "duck-ui.tokens.json"
    guide_path = ROOT / "design" / "DUCK_UI_SYSTEM.md"

    if not css_path.is_file():
        errors.append("Missing assets/duck-ui/duck-ui.css")
    else:
        css = css_path.read_text(encoding="utf-8")
        for selector in MATERIAL_SELECTORS:
            if selector not in css:
                errors.append(f"assets/duck-ui/duck-ui.css: missing {selector}")
        for token in ("#0D0D0D", "#FFD600"):
            if token not in css.upper():
                errors.append(f"assets/duck-ui/duck-ui.css: missing {token}")

    if not tokens_path.is_file():
        errors.append("Missing design/duck-ui.tokens.json")
    else:
        try:
            tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
            serialized = json.dumps(tokens, ensure_ascii=False).upper()
            for token in ("FFD600", "0D0D0D"):
                if token not in serialized:
                    errors.append(f"design/duck-ui.tokens.json: missing {token}")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(f"design/duck-ui.tokens.json: invalid JSON ({exc})")

    if not guide_path.is_file():
        errors.append("Missing design/DUCK_UI_SYSTEM.md")
    elif "Duck Black / Yellow" not in guide_path.read_text(encoding="utf-8"):
        errors.append("design/DUCK_UI_SYSTEM.md: missing shared design contract marker")


def validate_optional_product_spec(errors: list[str]) -> None:
    path = ROOT / "docs" / "PRODUCT_SYSTEM.md"
    if not path.is_file():
        return
    content = path.read_text(encoding="utf-8")
    for marker in ("CAP-10000", "Українська", "English", "Русский", "#FFD600", "#111111"):
        if marker not in content:
            errors.append(f"docs/PRODUCT_SYSTEM.md: missing required marker {marker!r}")
    print(f"PASS docs/PRODUCT_SYSTEM.md: {len(content)} characters")


def main() -> int:
    errors: list[str] = []
    total = validate_readmes(errors)
    validate_design_system(errors)
    validate_optional_product_spec(errors)
    if errors:
        print("\nDuck repository quality gate failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(
        "\nDuck repository quality gate passed "
        f"({len(READMES)} language files; {total} README characters; "
        "design tokens and material surfaces validated)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
