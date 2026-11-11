#!/usr/bin/env python3
"""Check shared repository identity, localization, and Duck UI contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.name
README_FILES = ("README.md", "README.en.md", "README.ru.md")
MAX_README_CHARS = 10_000


def read_heading(content: str) -> str | None:
    html = re.search(r"<h1\b[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL)
    if html:
        return re.sub(r"<[^>]+>", "", html.group(1)).strip()
    markdown = re.search(r"(?m)^#\s+(.+?)\s*$", content)
    return markdown.group(1).strip() if markdown else None


def validate() -> list[str]:
    errors: list[str] = []
    for relative in README_FILES:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"Missing localized README: {relative}")
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"Cannot read {relative}: {exc}")
            continue
        if len(content) > MAX_README_CHARS:
            errors.append(f"{relative} is {len(content)} characters; limit is {MAX_README_CHARS}")
        heading = read_heading(content)
        if not heading:
            errors.append(f"{relative} has no H1 title")
        elif heading != REPOSITORY:
            errors.append(f"{relative} title must preserve {REPOSITORY!r}; found {heading!r}")

    tokens_path = ROOT / "design" / "duck-ui.tokens.json"
    if not tokens_path.is_file():
        errors.append("Missing design/duck-ui.tokens.json")
    else:
        try:
            tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
            colors = tokens.get("color", {})
            if tokens.get("system") != "Duck Black / Yellow":
                errors.append("Duck UI token system must be 'Duck Black / Yellow'")
            if colors.get("canvas", "").upper() != "#0D0D0D":
                errors.append("Duck UI canvas token must be #0D0D0D")
            if colors.get("accent", "").upper() != "#FFD600":
                errors.append("Duck UI accent token must be #FFD600")
        except (OSError, UnicodeError, json.JSONDecodeError, AttributeError) as exc:
            errors.append(f"Invalid Duck UI token file: {exc}")
    if not (ROOT / "design" / "DUCK_UI_SYSTEM.md").is_file():
        errors.append("Missing design/DUCK_UI_SYSTEM.md")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Repository contract check failed for {REPOSITORY}.")
        return 1
    print(f"Repository contract check passed for {REPOSITORY}: canonical identity, 3 localized READMEs, 10,000-character limit, and Duck Black / Yellow tokens.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
