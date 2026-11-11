#!/usr/bin/env python3
"""Beelzebub: read-only repository security baseline (Python standard library only).

This scanner never modifies or deletes repository files. High-confidence credential
exposures fail CI; context-dependent code patterns are advisory only.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

MAX_FILE_BYTES = 2 * 1024 * 1024
SKIP_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".tox",
    "build", "dist", "target", "vendor", ".next", ".idea",
}

SECRET_PATTERNS = (
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "BBZ-GITHUB-TOKEN"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"), "BBZ-GITHUB-PAT"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "BBZ-AWS-ACCESS-KEY"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "BBZ-GOOGLE-API-KEY"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "BBZ-SLACK-TOKEN"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "BBZ-PRIVATE-KEY"),
)

GENERIC_CREDENTIAL = re.compile(
    r"""(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|passwd)\b"""
    r"""\\s*[:=]\\s*["']([^"'\\s]{20,})["']"""
)
PLACEHOLDERS = (
    "example", "sample", "placeholder", "changeme", "change_me",
    "your_", "replace", "dummy", "not-a-secret", "redacted",
)

ADVISORIES = (
    (re.compile(r"\b(?:eval|exec)\s*\("), "BBZ-DYNAMIC-EXEC", "Dynamic code execution needs a human security review."),
    (re.compile(r"\bsubprocess\.[A-Za-z_]+\s*\([^\\n]{0,240}shell\s*=\s*True"), "BBZ-SHELL-TRUE", "Shell execution can create command-injection risk; validate inputs and avoid shell=True."),
    (re.compile(r"\bpickle\.loads?\s*\("), "BBZ-PICKLE", "Pickle can execute code while deserializing untrusted data."),
    (re.compile(r"\byaml\.load\s*\("), "BBZ-UNSAFE-YAML", "Review YAML loader choice; use a safe loader for untrusted input."),
)

def _credential_hits(line: str) -> list[str]:
    hits: list[str] = []
    for pattern, rule in SECRET_PATTERNS:
        if pattern.search(line):
            hits.append(rule)
    generic = GENERIC_CREDENTIAL.search(line)
    if generic:
        value = generic.group(1).lower()
        if not any(word in value for word in PLACEHOLDERS):
            hits.append("BBZ-HIGH-CONFIDENCE-CREDENTIAL")
    return hits

def self_test() -> None:
    synthetic = "token = '" + "gh" + "p_" + ("A" * 36) + "'"
    assert "BBZ-GITHUB-TOKEN" in _credential_hits(synthetic)
    assert not _credential_hits('API_KEY = "replace-me-with-a-real-value"')
    assert "BBZ-DYNAMIC-EXEC" in [rule for pattern, rule, _ in ADVISORIES if pattern.search("eval(user_input)")]
    print("Beelzebub self-test: PASS")

def _github_escape(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A").replace(":", "%3A").replace(",", "%2C")

def _iter_files(root: Path):
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [
            name for name in dirs
            if name not in SKIP_DIRS and not (Path(current) / name).is_symlink()
        ]
        for name in files:
            path = Path(current) / name
            if path.is_symlink():
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue
            yield path

def scan(root: Path) -> int:
    critical = 0
    advisory = 0
    scanned = 0

    for path in _iter_files(root):
        try:
            raw = path.read_bytes()
        except (OSError, PermissionError):
            continue
        if b"\x00" in raw[:8192]:
            continue
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("utf-8", errors="replace")

        scanned += 1
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        for line_no, line in enumerate(content.splitlines(), start=1):
            for rule in _credential_hits(line):
                critical += 1
                message = f"[{rule}] Possible credential exposure. Revoke/rotate the credential; do not paste its value into an issue."
                print(f"::error file={_github_escape(rel)},line={line_no}::{_github_escape(message)}")
            if suffix in {".py", ".pyw", ".js", ".mjs", ".cjs"}:
                for pattern, rule, message in ADVISORIES:
                    if pattern.search(line):
                        advisory += 1
                        print(f"::warning file={_github_escape(rel)},line={line_no}::{_github_escape('[' + rule + '] ' + message)}")

        if rel.startswith(".github/workflows/") and path.suffix.lower() in {".yml", ".yaml"}:
            lower = content.lower()
            if "pull_request_target:" in lower and re.search(r"(?m)^\s*permissions:\s*write-all\s*$", lower):
                advisory += 1
                print(f"::warning file={_github_escape(rel)}::[BBZ-PRIVILEGED-PR] Review pull_request_target with write-all permissions.")

    print(f"Beelzebub scan complete: files={scanned}, credential_findings={critical}, advisory_findings={advisory}")
    if critical:
        print("Beelzebub verdict: BLOCKED. Rotate exposed credentials, remove them from the working tree, then re-run the scan.")
        return 1
    print("Beelzebub verdict: PASS (advisories are non-blocking and require human review).")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Beelzebub repository security scan.")
    parser.add_argument("--root", default=".", help="Repository root (default: current directory).")
    parser.add_argument("--self-test", action="store_true", help="Run scanner self-tests without scanning files.")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Beelzebub: repository root does not exist: {root}", file=sys.stderr)
        return 2
    return scan(root)

if __name__ == "__main__":
    raise SystemExit(main())
