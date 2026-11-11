#!/usr/bin/env python3
"""Conservative repository IP and secret review. Advisory by default; never rewrites files."""
from __future__ import annotations
import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SECRET_PATTERNS = (
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (?:OPENSSH|RSA|EC|DSA|PGP|ENCRYPTED)? ?PRIVATE KEY-----")),
    ("AWS_ACCESS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GITHUB_TOKEN", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("SLACK_TOKEN", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b")),
    ("GOOGLE_API_KEY", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("STRIPE_SECRET_KEY", re.compile(r"\bsk_live_[0-9a-zA-Z]{20,}\b")),
)
LICENSE_NAMES = ("LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING", "COPYING.LESSER")
SAFE_ENV_TEMPLATES = {".env.example", ".env.sample", ".env.template", ".env.dist"}

def load_policy(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("policy must be a JSON object with schema_version: 1")
    terms = data.get("trademark_watchlist", [])
    if not isinstance(terms, list) or any(not isinstance(x, str) or not x.strip() for x in terms):
        raise ValueError("trademark_watchlist must be an array of non-empty strings")
    scan = data.get("scan", {})
    if not isinstance(scan, dict):
        raise ValueError("scan must be an object")
    if not isinstance(scan.get("max_file_bytes", 1048576), int) or scan.get("max_file_bytes", 1048576) < 1024:
        raise ValueError("scan.max_file_bytes must be an integer >= 1024")
    for key in ("exclude_paths", "trademark_allow_paths"):
        value = scan.get(key, [])
        if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            raise ValueError(f"scan.{key} must be an array of strings")
    lic = data.get("license", {})
    if not isinstance(lic, dict) or not isinstance(lic.get("require_spdx_headers", False), bool):
        raise ValueError("license must be an object with a boolean require_spdx_headers")
    if not isinstance(lic.get("source_globs", []), list):
        raise ValueError("license.source_globs must be an array")
    return data

def scan_text(text: str, trademark_terms: list[str] | None = None) -> list[dict[str, Any]]:
    """Return redacted findings; matched secret values are never included."""
    findings: list[dict[str, Any]] = []
    for rule, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append({"code": rule, "line": text.count("\n", 0, match.start()) + 1,
                             "detail": "Potential credential or private-key marker"})
    for term in trademark_terms or []:
        pattern = re.compile(r"(?<![\w])" + re.escape(term) + r"(?![\w])", re.IGNORECASE)
        for match in pattern.finditer(text):
            findings.append({"code": "TRADEMARK_REVIEW", "line": text.count("\n", 0, match.start()) + 1,
                             "detail": f"Configured name requires contextual review: {term}"})
    return findings

def tracked_paths(root: Path) -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True)
    return [part.decode("utf-8", errors="surrogateescape") for part in result.stdout.split(b"\0") if part]

def excluded(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)

def audit(root: Path, policy: dict[str, Any], strict: bool = False) -> tuple[list[dict[str, Any]], int]:
    findings: list[dict[str, Any]] = []
    cfg = policy.get("scan", {})
    limit = cfg.get("max_file_bytes", 1048576)
    ignored = cfg.get("exclude_paths", [])
    allowed = cfg.get("trademark_allow_paths", [])
    watchlist = policy.get("trademark_watchlist", [])
    lic = policy.get("license", {})
    spdx_id = lic.get("spdx_id")

    for relative in tracked_paths(root):
        name = relative.replace("\\", "/")
        if excluded(name, ignored):
            continue
        path = root / relative
        try:
            if not path.is_file() or path.stat().st_size > limit:
                continue
            raw = path.read_bytes()
            if b"\0" in raw:
                continue
            text = raw.decode("utf-8", errors="replace")
        except OSError:
            continue
        terms = [] if name in allowed or excluded(name, allowed) else watchlist
        for item in scan_text(text, terms):
            findings.append({"path": name, **item})
        base = Path(name).name
        if base.startswith(".env") and base not in SAFE_ENV_TEMPLATES:
            findings.append({"path": name, "code": "TRACKED_ENV_FILE", "line": 1,
                             "detail": "Tracked environment file; verify it contains no credentials"})
        if spdx_id and lic.get("require_spdx_headers", False):
            if any(fnmatch.fnmatchcase(name, pattern) for pattern in lic.get("source_globs", [])):
                header = "\n".join(text.splitlines()[:30])
                if f"SPDX-License-Identifier: {spdx_id}" not in header:
                    findings.append({"path": name, "code": "SPDX_HEADER_MISSING", "line": 1,
                                     "detail": f"Expected SPDX-License-Identifier: {spdx_id} in first 30 lines"})

    has_license = any((root / item).is_file() for item in LICENSE_NAMES)
    if not has_license:
        findings.append({"path": "", "code": "LICENSE_OWNER_REVIEW", "line": 1,
                         "detail": "No root license file detected; repository owner must choose and approve licensing terms"})
    elif not spdx_id:
        findings.append({"path": "LICENSE", "code": "LICENSE_METADATA_REVIEW", "line": 1,
                         "detail": "A license file exists; verify its scope, provenance, and SPDX identifier"})
    blocking = {"PRIVATE_KEY", "AWS_ACCESS_KEY", "GITHUB_TOKEN", "SLACK_TOKEN",
                "GOOGLE_API_KEY", "STRIPE_SECRET_KEY", "TRACKED_ENV_FILE", "TRADEMARK_REVIEW"}
    return findings, sum(1 for item in findings if strict and item["code"] in blocking)

def escape_annotation(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A").replace(":", "%3A").replace(",", "%2C")

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default="compliance/repository-policy.json")
    parser.add_argument("--strict", action="store_true", help="Fail on high-confidence or configured review findings")
    args = parser.parse_args(argv)
    root = Path.cwd().resolve()
    try:
        policy = load_policy((root / args.policy).resolve())
        findings, failures = audit(root, policy, strict=args.strict)
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"Repository compliance audit could not run: {exc}", file=sys.stderr)
        return 2
    for item in findings:
        path, line, code, detail = item.get("path") or ".", item.get("line", 1), item["code"], item["detail"]
        print(f"{path}:{line}: {code}: {detail}")
        print(f"::warning file={escape_annotation(path)},line={line}::{escape_annotation(code + ': ' + detail)}")
    print(f"Repository compliance audit: {len(findings)} finding(s); mode={'strict' if args.strict else 'advisory'}.")
    print("No files, identifiers, Git metadata, or repository history were modified.")
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
