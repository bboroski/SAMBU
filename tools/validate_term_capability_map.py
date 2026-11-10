#!/usr/bin/env python3
"""Verify every canonical glossary term has exactly one capability mapping."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "biology_500": ROOT / "data" / "biology" / "academic_terms_500.tsv",
    "reaper_engineering_50": ROOT / "data" / "reaper" / "engineering_patterns_50.tsv",
}
MAPPING = ROOT / "data" / "domain" / "term-capability-map.tsv"
FIELDS = [
    "source_dataset", "source_id", "category", "term_en", "term_ru",
    "capability_id", "owner_repo", "api_or_contract", "feature_family",
    "scope_boundary",
]
EXPECTED_COUNTS = {"biology_500": 500, "reaper_engineering_50": 50}
ALLOWED_OWNERS = {
    "SAMBU", "ToolNG", "ReaperCripple", "Kloz", "CO", "SaintSI",
    "Klipot", "NUN", "NUNLauncher", "Fragile-Baby", "Luci",
}


def read_tsv(path: Path, expected_header: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    if not path.is_file():
        return [], [f"missing file: {path.relative_to(ROOT)}"]
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames != expected_header:
                return [], [f"invalid header in {path.relative_to(ROOT)}"]
            return list(reader), []
    except (OSError, UnicodeError, csv.Error) as exc:
        return [], [f"cannot read {path.relative_to(ROOT)}: {exc}"]


def validate() -> list[str]:
    errors: list[str] = []
    expected: dict[tuple[str, str], tuple[str, str, str]] = {}
    for dataset, path in SOURCES.items():
        rows, read_errors = read_tsv(path, ["id", "category", "term_en", "term_ru"] + (
            ["engineering_mapping"] if dataset == "reaper_engineering_50" else []
        ))
        errors.extend(read_errors)
        if read_errors:
            continue
        if len(rows) != EXPECTED_COUNTS[dataset]:
            errors.append(
                f"{dataset}: expected {EXPECTED_COUNTS[dataset]} rows, found {len(rows)}"
            )
        for row in rows:
            key = (dataset, (row.get("id") or "").strip())
            expected[key] = (
                (row.get("category") or "").strip(),
                (row.get("term_en") or "").strip(),
                (row.get("term_ru") or "").strip(),
            )

    mappings, read_errors = read_tsv(MAPPING, FIELDS)
    errors.extend(read_errors)
    if read_errors:
        return errors

    actual: dict[tuple[str, str], dict[str, str]] = {}
    for line_number, row in enumerate(mappings, start=2):
        key = ((row.get("source_dataset") or "").strip(), (row.get("source_id") or "").strip())
        if key in actual:
            errors.append(f"line {line_number}: duplicate mapping for {key}")
            continue
        actual[key] = row
        if key[0] not in SOURCES:
            errors.append(f"line {line_number}: unknown source dataset {key[0]!r}")
        owner = (row.get("owner_repo") or "").strip()
        if owner not in ALLOWED_OWNERS:
            errors.append(f"line {line_number}: unknown owner repository {owner!r}")
        for field in ("capability_id", "api_or_contract", "feature_family", "scope_boundary"):
            if not (row.get(field) or "").strip():
                errors.append(f"line {line_number}: empty {field}")

    for key, source in expected.items():
        mapped = actual.get(key)
        if mapped is None:
            errors.append(f"missing mapping: {key}")
            continue
        for field, source_field in (
            ("category", "category"),
            ("term_en", "term_en"),
            ("term_ru", "term_ru"),
        ):
            if (mapped.get(field) or "").strip() != source[source_field]:
                errors.append(f"source mismatch for {key}: {field}")
    for key in actual.keys() - expected.keys():
        errors.append(f"mapping has no source record: {key}")

    if len(mappings) != sum(EXPECTED_COUNTS.values()):
        errors.append(f"expected 550 mappings, found {len(mappings)}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("OK: all 550 bilingual glossary/pattern records map to capability interfaces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
