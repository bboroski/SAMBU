#!/usr/bin/env python3
"""Validate the repository's IP provenance manifest using only Python's stdlib."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "ip-governance" / "manifest.json"
HEX64 = re.compile(r"^[0-9a-f]{64}$")

def fail(message: str) -> None:
    print(f"IP governance: ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

def main() -> int:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read manifest: {exc}")

    required = {"schema_version", "object_id", "repository", "rights", "artifacts"}
    missing = sorted(required - data.keys())
    if missing:
        fail("missing top-level fields: " + ", ".join(missing))
    if data["schema_version"] != "1.0":
        fail("unsupported schema_version (expected 1.0)")
    if not isinstance(data["repository"], str) or not data["repository"].startswith("https://github.com/"):
        fail("repository must be a canonical GitHub HTTPS URL")
    expected_id = "urn:uoi:github:" + data["repository"].removeprefix("https://github.com/").rstrip("/")
    if data["object_id"] != expected_id:
        fail("object_id does not match the canonical repository locator")
    rights = data["rights"]
    if not isinstance(rights, dict) or not isinstance(rights.get("license_expression"), str):
        fail("rights.license_expression must be a string (use NOASSERTION if unknown)")
    if not isinstance(rights.get("rights_holders"), list):
        fail("rights.rights_holders must be an array; do not invent ownership")
    if not isinstance(data["artifacts"], list):
        fail("artifacts must be an array")

    seen: set[str] = set()
    for item in data["artifacts"]:
        if not isinstance(item, dict):
            fail("each artifact must be an object")
        path_text, digest = item.get("path"), item.get("sha256")
        if not isinstance(path_text, str) or not path_text or path_text in seen:
            fail(f"invalid or duplicate artifact path: {path_text!r}")
        seen.add(path_text)
        rel = Path(path_text)
        if rel.is_absolute() or ".." in rel.parts:
            fail(f"artifact path escapes repository: {path_text}")
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            fail(f"invalid SHA-256 for artifact: {path_text}")
        target = (ROOT / rel).resolve()
        if ROOT.resolve() not in target.parents:
            fail(f"artifact path escapes repository: {path_text}")
        if not target.is_file():
            fail(f"artifact does not exist: {path_text}")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            fail(f"SHA-256 mismatch: {path_text}")

    print(f"IP governance: OK — {len(data['artifacts'])} artifact(s), {data['object_id']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
