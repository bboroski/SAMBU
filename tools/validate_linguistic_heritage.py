#!/usr/bin/env python3
"""Validate the shared Linguistic Heritage letter profile without third-party packages."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

DEFAULT_RECORD = Path(__file__).resolve().parents[1] / "data/linguistic-heritage/cyrillic-letter-y.json"
ALLOWED_CLAIM_STATES = {"established", "qualified", "hypothesis", "unsupported"}

def validate(record: dict) -> list[str]:
    errors: list[str] = []
    required = {"id", "glyph", "lowercase", "unicode", "claims", "schema_version",
                "script", "phoneme_profile", "historical_graphics", "historical_phonology",
                "comparative_slavic", "orthographic_history", "interpretive_layer",
                "claims_policy", "references"}
    missing = sorted(required - record.keys())
    if missing:
        return ["missing required keys: " + ", ".join(missing)]
    if record["schema_version"] != "linguistic-heritage.letter.v1":
        errors.append("unsupported schema_version")
    if (record["glyph"], record["lowercase"]) != ("Ы", "ы"):
        errors.append("glyph/lowercase must identify Cyrillic Ы / ы")
    if record["unicode"] != {"uppercase": "U+042B", "lowercase": "U+044B"}:
        errors.append("Unicode code points must be U+042B and U+044B")
    if record["interpretive_layer"].get("status") != "cultural_interpretation_not_historical_evidence":
        errors.append("interpretive layer must not be presented as historical evidence")
    for flag in ("separate_grapheme_history_from_sound_history",
                 "label_hypotheses_and_metaphors",
                 "require_primary_witness_for_exact_manuscript_dates"):
        if record["claims_policy"].get(flag) is not True:
            errors.append(f"claims_policy.{flag} must be true")
    claims = record["claims"]
    if not isinstance(claims, list) or not claims:
        errors.append("claims must be a non-empty list")
    else:
        ids = set()
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict):
                errors.append(f"claim[{index}] must be an object")
                continue
            for key in ("id", "statement", "status", "rationale"):
                if not claim.get(key):
                    errors.append(f"claim[{index}] missing {key}")
            if claim.get("status") not in ALLOWED_CLAIM_STATES:
                errors.append(f"claim[{index}] has invalid status")
            if claim.get("id") in ids:
                errors.append(f"duplicate claim id: {claim.get('id')}")
            ids.add(claim.get("id"))
    refs = record["references"]
    if not isinstance(refs, list) or len(refs) < 2:
        errors.append("at least two references are required")
    else:
        for index, source in enumerate(refs):
            if not isinstance(source, dict) or not str(source.get("url", "")).startswith("https://"):
                errors.append(f"reference[{index}] must contain an HTTPS URL")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", nargs="?", type=Path, default=DEFAULT_RECORD)
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate(record)
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print(f"OK: {args.record} conforms to linguistic-heritage.letter.v1")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
