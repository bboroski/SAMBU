#!/usr/bin/env python3
"""Validate Conventional Commit messages and pull-request titles without executing PR code."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HEADER = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([a-z0-9][a-z0-9._/-]*\))?(!)?: [^\s].+$"
)
MAX_HEADER = 72


def validate(message: str, label: str) -> list[str]:
    message = message.strip("\n")
    if not message:
        return [f"{label}: empty commit message"]
    subject = message.splitlines()[0].strip()
    errors: list[str] = []
    if not HEADER.fullmatch(subject):
        errors.append(
            f"{label}: {subject!r} does not follow "
            "type(scope): description / type!: description"
        )
    if len(subject) > MAX_HEADER:
        errors.append(f"{label}: header is {len(subject)} chars; limit is {MAX_HEADER}")
    return errors


def main() -> int:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        print("GITHUB_EVENT_PATH is required", file=sys.stderr)
        return 2

    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    pr = event.get("pull_request")
    if not pr:
        print("This validator is designed for pull_request events.", file=sys.stderr)
        return 2

    errors = validate(pr.get("title", ""), "pull request title")
    base = pr.get("base", {}).get("sha", "")
    head = pr.get("head", {}).get("sha", "")
    if not base or not head:
        print("The pull request base/head SHA is missing.", file=sys.stderr)
        return 2

    try:
        raw = subprocess.check_output(
            ["git", "log", "--format=%H%x1f%B%x1e", f"{base}..{head}"],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        print(exc.output, file=sys.stderr)
        print("Unable to inspect the complete pull-request commit range.", file=sys.stderr)
        return 2

    commits = [item for item in raw.split("\x1e") if item.strip()]
    if not commits:
        errors.append("pull request contains no inspectable commits")

    for record in commits:
        fields = record.strip("\n").split("\x1f", 1)
        sha = fields[0][:12] if fields else "unknown"
        message = fields[1] if len(fields) > 1 else ""
        errors.extend(validate(message, f"commit {sha}"))

    if errors:
        print("\n".join(f"::error::{item}" for item in errors))
        print(f"Conventional Commit validation failed: {len(errors)} issue(s).")
        return 1

    print(f"Conventional Commit validation passed for {len(commits)} commit(s) and the PR title.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
