"""Structured educational biology catalogue and evidence-linked annotations.

The module supports glossary search, category reporting and metadata annotation.
It does not generate laboratory protocols, diagnoses or biological interventions.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import csv
import hashlib
import json
from pathlib import Path
import sys
from collections.abc import Iterable
from typing import Any


EXPECTED_CATEGORIES = frozenset({
    "molecular_cell",
    "genetics_evolution",
    "ecology_environment",
    "physiology_anatomy",
    "immunology_microbiology_virology",
})
def _default_catalogue_path() -> Path:
    checkout_path = Path(__file__).resolve().parents[1] / "data" / "biology" / "academic_terms_500.tsv"
    if checkout_path.is_file():
        return checkout_path
    return Path(sys.prefix) / "share" / "sambu" / "data" / "biology" / "academic_terms_500.tsv"


DEFAULT_CATALOGUE = _default_catalogue_path()


class BiologyCatalogueError(ValueError):
    """Raised when a glossary or its annotation references are invalid."""


@dataclass(frozen=True)
class BiologyTerm:
    term_id: int
    category: str
    term_en: str
    term_ru: str


@dataclass(frozen=True)
class TermAnnotation:
    term_id: int
    evidence_ref: str
    note: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class CatalogueValidation:
    valid: bool
    term_count: int
    category_counts: dict[str, int]
    errors: tuple[str, ...]


class BiologyCatalogue:
    """Read-only glossary index with stable IDs and bilingual substring search."""

    def __init__(self, terms: Iterable[BiologyTerm]):
        materialized = tuple(terms)
        errors = self._validate_terms(materialized)
        if errors:
            raise BiologyCatalogueError("; ".join(errors))
        self._terms = materialized
        self._by_id = {term.term_id: term for term in materialized}
        self._category_counts = dict(sorted(
            Counter(term.category for term in materialized).items()
        ))

    @staticmethod
    def _validate_terms(terms: tuple[BiologyTerm, ...]) -> list[str]:
        errors: list[str] = []
        ids: set[int] = set()
        bilingual: set[tuple[str, str]] = set()
        for index, term in enumerate(terms, start=1):
            if not isinstance(term.term_id, int) or isinstance(term.term_id, bool) or term.term_id < 1:
                errors.append(f"record {index}: term_id must be a positive integer")
                continue
            if term.term_id in ids:
                errors.append(f"record {index}: duplicate term_id {term.term_id}")
            ids.add(term.term_id)
            if term.category not in EXPECTED_CATEGORIES:
                errors.append(f"record {index}: unsupported category {term.category!r}")
            if not term.term_en.strip() or not term.term_ru.strip():
                errors.append(f"record {index}: bilingual labels must not be empty")
            key = (term.term_en.casefold(), term.term_ru.casefold())
            if key in bilingual:
                errors.append(f"record {index}: duplicate bilingual term {key!r}")
            bilingual.add(key)
        if ids and ids != set(range(1, len(terms) + 1)):
            errors.append("term IDs must form a contiguous range starting at 1")
        return errors

    @classmethod
    def load(cls, path: str | Path = DEFAULT_CATALOGUE) -> "BiologyCatalogue":
        source = Path(path)
        try:
            with source.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle, delimiter="\t")
                expected = ["id", "category", "term_en", "term_ru"]
                if reader.fieldnames != expected:
                    raise BiologyCatalogueError(
                        f"invalid glossary header: expected {expected!r}"
                    )
                records = []
                for line_number, row in enumerate(reader, start=2):
                    try:
                        term_id = int((row.get("id") or "").strip())
                    except ValueError as exc:
                        raise BiologyCatalogueError(
                            f"line {line_number}: invalid term ID"
                        ) from exc
                    records.append(BiologyTerm(
                        term_id=term_id,
                        category=(row.get("category") or "").strip(),
                        term_en=(row.get("term_en") or "").strip(),
                        term_ru=(row.get("term_ru") or "").strip(),
                    ))
        except (OSError, UnicodeError, csv.Error) as exc:
            raise BiologyCatalogueError(f"unable to load catalogue: {exc}") from exc
        return cls(records)

    def __len__(self) -> int:
        return len(self._terms)

    def get(self, term_id: int) -> BiologyTerm:
        if not isinstance(term_id, int) or isinstance(term_id, bool):
            raise TypeError("term_id must be an integer")
        try:
            return self._by_id[term_id]
        except KeyError as exc:
            raise BiologyCatalogueError(f"unknown biology term ID: {term_id}") from exc

    def search(
        self,
        query: str,
        *,
        language: str = "any",
        categories: Iterable[str] | None = None,
        limit: int = 50,
    ) -> tuple[BiologyTerm, ...]:
        if not isinstance(query, str):
            raise TypeError("query must be a string")
        if language not in ("any", "en", "ru"):
            raise ValueError("language must be any, en or ru")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        allowed_categories = None if categories is None else set(categories)
        if allowed_categories is not None and not allowed_categories <= EXPECTED_CATEGORIES:
            raise ValueError("one or more category filters are unsupported")
        needle = query.strip().casefold()
        matches: list[BiologyTerm] = []
        for term in self._terms:
            if allowed_categories is not None and term.category not in allowed_categories:
                continue
            candidates = (
                (term.term_en,) if language == "en"
                else (term.term_ru,) if language == "ru"
                else (term.term_en, term.term_ru)
            )
            if not needle or any(needle in candidate.casefold() for candidate in candidates):
                matches.append(term)
                if len(matches) >= limit:
                    break
        return tuple(matches)

    def category_counts(self) -> dict[str, int]:
        return dict(self._category_counts)

    def annotate(
        self,
        term_id: int,
        *,
        evidence_ref: str,
        note: str,
        tags: Iterable[str] = (),
    ) -> TermAnnotation:
        """Attach a descriptive catalogue note; this does not validate a biological claim."""
        self.get(term_id)
        if not isinstance(evidence_ref, str) or not evidence_ref.strip():
            raise ValueError("evidence_ref must be non-empty")
        if not isinstance(note, str) or not note.strip():
            raise ValueError("note must be non-empty")
        materialized_tags = tuple(tags)
        if any(not isinstance(tag, str) or not tag.strip() for tag in materialized_tags):
            raise ValueError("tags must contain non-empty strings")
        normalized_tags = tuple(sorted(set(materialized_tags)))
        return TermAnnotation(term_id, evidence_ref.strip(), note.strip(), normalized_tags)


def validate_catalogue(path: str | Path = DEFAULT_CATALOGUE) -> CatalogueValidation:
    try:
        catalogue = BiologyCatalogue.load(path)
    except BiologyCatalogueError as exc:
        return CatalogueValidation(False, 0, {}, (str(exc),))
    counts = catalogue.category_counts()
    errors = []
    if len(catalogue) != 500:
        errors.append(f"expected 500 terms, found {len(catalogue)}")
    if set(counts) != EXPECTED_CATEGORIES:
        errors.append("category coverage does not match the five declared domains")
    if any(count != 100 for count in counts.values()):
        errors.append("each declared domain must contain 100 terms")
    return CatalogueValidation(not errors, len(catalogue), counts, tuple(errors))


def annotation_digest(annotations: Iterable[TermAnnotation]) -> str:
    """Return a deterministic SHA-256 digest for annotation metadata."""
    rows = [asdict(item) for item in annotations]
    rows.sort(key=lambda item: (item["term_id"], item["evidence_ref"], item["note"], tuple(item["tags"])))
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    validate = commands.add_parser("validate", help="validate all 500 glossary records")
    validate.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    summary = commands.add_parser("summary", help="show per-domain record counts")
    summary.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    search = commands.add_parser("search", help="search bilingual glossary records")
    search.add_argument("query")
    search.add_argument("--language", choices=("any", "en", "ru"), default="any")
    search.add_argument("--category", action="append", default=[])
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    args = parser.parse_args()
    try:
        if args.action == "validate":
            report = validate_catalogue(args.catalogue)
            if not report.valid:
                for error in report.errors:
                    print(f"ERROR: {error}")
                return 1
            print(f"OK: {report.term_count} bilingual records in {len(report.category_counts)} domains")
            return 0
        catalogue = BiologyCatalogue.load(args.catalogue)
        if args.action == "summary":
            for category, count in catalogue.category_counts().items():
                print(f"{category}\t{count}")
            return 0
        for term in catalogue.search(
            args.query, language=args.language,
            categories=args.category or None, limit=args.limit,
        ):
            print(f"{term.term_id}\t{term.category}\t{term.term_en}\t{term.term_ru}")
        return 0
    except (BiologyCatalogueError, TypeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
