#!/usr/bin/env python3
"""Validate the 50-entry engineering reference catalogue.

The catalogue is a technical terminology and design-reference dataset, not executable
code, a hardware specification, or a source of operational authority.
"""
from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

DATA_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "reaper"
    / "engineering_patterns_50.tsv"
)
FIELDS = ["id", "category", "term_en", "term_ru", "engineering_mapping"]
EXPECTED_COUNT = 50
EXPECTED_CATEGORIES = {
    "data_pipeline",
    "physical_modeling",
    "infrastructure_resilience",
    "lifecycle_governance",
    "distributed_intelligence",
}


def validate() -> list[str]:
    if not DATA_FILE.is_file():
        return [f"Dataset not found: {DATA_FILE}"]
    try:
        with DATA_FILE.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames != FIELDS:
                return [f"Invalid header: expected {FIELDS!r}, got {reader.fieldnames!r}"]
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        return [f"Unable to read dataset: {exc}"]

    errors: list[str] = []
    if len(rows) != EXPECTED_COUNT:
        errors.append(f"Expected {EXPECTED_COUNT} records, found {len(rows)}")

    ids: list[int] = []
    category_counts: Counter[str] = Counter()
    terms: set[str] = set()
    for line, row in enumerate(rows, start=2):
        try:
            term_id = int((row.get("id") or "").strip())
        except ValueError:
            errors.append(f"Line {line}: id must be an integer")
            continue
        ids.append(term_id)
        category = (row.get("category") or "").strip()
        category_counts[category] += 1
        if category not in EXPECTED_CATEGORIES:
            errors.append(f"Line {line}: unknown category {category!r}")
        for field in FIELDS[2:]:
            if not (row.get(field) or "").strip():
                errors.append(f"Line {line}: empty {field}")
        key = (row.get("term_en") or "").strip().casefold()
        if key in terms:
            errors.append(f"Line {line}: duplicate English term {key!r}")
        terms.add(key)

    if ids != list(range(1, EXPECTED_COUNT + 1)):
        errors.append("IDs must be unique and contiguous from 1 through 50")
    if set(category_counts) != EXPECTED_CATEGORIES:
        errors.append("Category coverage does not match the five declared domains")
    if any(count != 10 for count in category_counts.values()):
        errors.append("Each declared domain must contain exactly 10 records")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: 50 engineering reference patterns validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
