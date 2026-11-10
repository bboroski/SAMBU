#!/usr/bin/env python3
"""Validate the repository-local 500-term academic biology glossary."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "biology"
    / "academic_terms_500.tsv"
)
EXPECTED_FIELDS = ["id", "category", "term_en", "term_ru"]
EXPECTED_COUNT = 500
EXPECTED_CATEGORIES = {
    "molecular_cell",
    "genetics_evolution",
    "ecology_environment",
    "physiology_anatomy",
    "immunology_microbiology_virology",
}


def validate() -> list[str]:
    errors: list[str] = []
    if not DATA_FILE.is_file():
        return [f"Dataset not found: {DATA_FILE}"]

    try:
        with DATA_FILE.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=chr(9))
            if reader.fieldnames != EXPECTED_FIELDS:
                return [
                    "Invalid header: expected "
                    + "|".join(EXPECTED_FIELDS)
                    + ", got "
                    + "|".join(reader.fieldnames or [])
                ]
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        return [f"Unable to read dataset: {exc}"]

    if len(rows) != EXPECTED_COUNT:
        errors.append(f"Expected {EXPECTED_COUNT} records, found {len(rows)}")

    seen_ids: set[int] = set()
    seen_terms: set[tuple[str, str]] = set()
    for line_number, row in enumerate(rows, start=2):
        raw_id = (row.get("id") or "").strip()
        try:
            term_id = int(raw_id)
        except ValueError:
            errors.append(f"Line {line_number}: invalid integer id {raw_id!r}")
            continue

        if term_id in seen_ids:
            errors.append(f"Line {line_number}: duplicate id {term_id}")
        seen_ids.add(term_id)

        category = (row.get("category") or "").strip()
        if category not in EXPECTED_CATEGORIES:
            errors.append(f"Line {line_number}: unknown category {category!r}")

        term_en = (row.get("term_en") or "").strip()
        term_ru = (row.get("term_ru") or "").strip()
        if not term_en:
            errors.append(f"Line {line_number}: empty English term")
        if not term_ru:
            errors.append(f"Line {line_number}: empty Russian term")

        key = (term_en.casefold(), term_ru.casefold())
        if key in seen_terms:
            errors.append(f"Line {line_number}: duplicate bilingual term {key!r}")
        seen_terms.add(key)

    expected_ids = set(range(1, EXPECTED_COUNT + 1))
    if seen_ids != expected_ids:
        missing = sorted(expected_ids - seen_ids)
        unexpected = sorted(seen_ids - expected_ids)
        errors.append(f"ID range mismatch; missing={missing}, unexpected={unexpected}")

    present_categories = {row.get("category", "").strip() for row in rows}
    if present_categories != EXPECTED_CATEGORIES:
        errors.append(
            "Category coverage mismatch; missing="
            + repr(sorted(EXPECTED_CATEGORIES - present_categories))
            + ", unexpected="
            + repr(sorted(present_categories - EXPECTED_CATEGORIES))
        )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: 500 bilingual biology terms; IDs, categories and fields validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
