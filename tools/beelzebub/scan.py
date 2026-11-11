#!/usr/bin/env python3
"""Beelzebub local repository scanner. Stdlib only; read-only except its JSON report."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build", "target",
    ".next", ".gradle", ".idea",
}
SKIP_FILES = {"scan.py"}
MAX_FILE_BYTES = 2 * 1024 * 1024
DEPENDENCY_FILES = {
    "package.json", "package-lock.json", "npm-shrinkwrap.json", "yarn.lock",
    "pnpm-lock.yaml", "requirements.txt", "poetry.lock", "Pipfile",
    "Pipfile.lock", "pyproject.toml", "Cargo.toml", "Cargo.lock",
    "go.mod", "go.sum", "Gemfile", "Gemfile.lock", "composer.json",
    "composer.lock", " pom.xml", "build.gradle", "build.gradle.kts",
    "gradle.lockfile", "Podfile", "Podfile.lock",
}

# Construct sensitive markers from fragments so the scanner does not match itself.
PEM_MARKER = "BEGIN " + "(RSA|OPENSSH|EC|DSA) " + "PRIVATE KEY"
PATTERNS = [
    ("private_key", re.compile(PEM_MARKER), "critical"),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "critical"),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"), "critical"),
    ("credential_assignment", re.compile(
        r"""(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\b\s*[:=]\s*["']?([A-Za-z0-9_./+=-]{20,})"""
    ), "high"),
]
PLACEHOLDERS = {
    "your_token_here", "changeme", "replace_me", "example", "placeholder",
    "xxxxxxxxxxxxxxxxxxxx", "00000000000000000000",
}

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def iter_files(root: Path, report: Path):
    report_abs = report.resolve()
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        base = Path(current)
        for name in sorted(files):
            path = base / name
            if name in SKIP_FILES or path.resolve() == report_abs:
                continue
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                size = path.stat().st_size
            except OSError:
                continue
            if size <= MAX_FILE_BYTES:
                yield path, size

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--report", default="beelzebub-report.json", help="JSON report path")
    parser.add_argument("--fail-on", choices=("critical", "high", "never"), default="high")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report_path = Path(args.report)
    if not report_path.is_absolute():
        report_path = (Path.cwd() / report_path).resolve()
    if not root.is_dir():
        print("Beelzebub: repository root is not a directory", file=sys.stderr)
        return 2

    findings = []
    inventory = []
    scanned = 0
    skipped_binary = 0

    for path, size in iter_files(root, report_path):
        relative = path.relative_to(root).as_posix()
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:8192]:
            skipped_binary += 1
            continue
        scanned += 1
        digest = hashlib.sha256(raw).hexdigest()
        if path.name in DEPENDENCY_FILES or path.name.lower() in {
            "requirements-dev.txt", "requirements-prod.txt"
        }:
            inventory.append({"path": relative, "size": size, "sha256": digest})

        text = raw.decode("utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for kind, pattern, severity in PATTERNS:
                match = pattern.search(line)
                if not match:
                    continue
                candidate = match.group(1) if match.lastindex else match.group(0)
                if candidate.lower() in PLACEHOLDERS:
                    continue
                findings.append({
                    "rule_id": kind,
                    "severity": severity,
                    "path": relative,
                    "line": line_no,
                    "message": "Potential credential detected; value redacted.",
                    "evidence_sha256": hashlib.sha256(match.group(0).encode()).hexdigest(),
                })
                break

    counts = {level: sum(1 for item in findings if item["severity"] == level)
              for level in ("critical", "high")}
    report = {
        "schema_version": "1.0",
        "engine": "Beelzebub",
        "engine_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(root),
        "mode": "read-only",
        "summary": {
            "files_scanned": scanned,
            "binary_files_skipped": skipped_binary,
            "dependency_manifests": len(inventory),
            "findings": len(findings),
            "by_severity": counts,
        },
        "dependency_inventory": inventory,
        "findings": findings,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))

    blocking = counts["critical"] > 0 or (
        args.fail_on == "high" and counts["high"] > 0
    )
    if args.fail_on == "critical":
        blocking = counts["critical"] > 0
    if args.fail_on == "never":
        blocking = False
    return 1 if blocking else 0

if __name__ == "__main__":
    raise SystemExit(main())
