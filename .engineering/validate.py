#!/usr/bin/env python3
"""Validate the repository-local Engineering Standard profile (stdlib only)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / ".engineering" / "profile.json"
STANDARD = ROOT / "ENGINEERING_STANDARD.md"
REQUIRED_GATES = {
    "profile-validation",
    "native-project-checks",
    "architecture-and-compatibility-review",
    "security-and-privacy-review",
    "documentation-review",
    "human-review",
    "target-qualification-when-applicable",
}
REQUIRED_STATUSES = {
    "PROPOSED", "PLANNED", "IMPLEMENTED", "TESTED",
    "VERIFIED", "MERGED", "RELEASED", "BLOCKED",
}

def fail(message: str) -> None:
    print(f"ENGINEERING STANDARD FAIL: {message}", file=sys.stderr)

def main() -> int:
    errors: list[str] = []
    if not PROFILE.is_file():
        errors.append("missing .engineering/profile.json")
    if not STANDARD.is_file():
        errors.append("missing ENGINEERING_STANDARD.md")
    if not (ROOT / "README.md").is_file():
        errors.append("missing README.md")
    if errors:
        for item in errors:
            fail(item)
        return 1

    try:
        data = json.loads(PROFILE.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"profile is not readable valid JSON: {exc}")
        return 1

    if data.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if data.get("standard_id") != "PERSONA-ENG-STD":
        errors.append("standard_id must equal PERSONA-ENG-STD")

    repository = data.get("repository")
    if not isinstance(repository, str) or "/" not in repository:
        errors.append("repository must be a non-empty owner/name string")
    expected = os.environ.get("GITHUB_REPOSITORY")
    if expected and repository != expected:
        errors.append(f"profile repository {repository!r} does not match checkout {expected!r}")

    project = data.get("project")
    if not isinstance(project, dict):
        errors.append("project must be an object")
        project = {}
    for key in ("domain", "mission", "maturity"):
        if not isinstance(project.get(key), str) or not project[key].strip():
            errors.append(f"project.{key} must be a non-empty string")

    architecture = data.get("architecture")
    if not isinstance(architecture, dict) or architecture.get("preserve_existing_boundaries") is not True:
        errors.append("architecture.preserve_existing_boundaries must be true")
        architecture = {}
    for key in ("primary_technologies", "explicit_non_goals"):
        value = architecture.get(key)
        if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
            errors.append(f"architecture.{key} must be a non-empty string array")

    safety = data.get("safety_boundaries")
    if not isinstance(safety, list) or not safety or any(not isinstance(x, str) or not x.strip() for x in safety):
        errors.append("safety_boundaries must be a non-empty string array")

    native = data.get("native_validation")
    if not isinstance(native, dict):
        errors.append("native_validation must be an object")
        native = {}
    if native.get("status") not in {"defined", "discovery-required", "target-evidence-pending"}:
        errors.append("native_validation.status must identify the verification maturity")
    commands = native.get("commands")
    if not isinstance(commands, list) or any(not isinstance(x, str) or not x.strip() for x in commands):
        errors.append("native_validation.commands must be an array of command strings (empty only when no verified command exists)")

    gates = data.get("required_gates")
    if not isinstance(gates, list):
        errors.append("required_gates must be an array")
        gates = []
    missing_gates = REQUIRED_GATES - set(gates)
    if missing_gates:
        errors.append("required_gates missing: " + ", ".join(sorted(missing_gates)))

    merge = data.get("merge_policy")
    if not isinstance(merge, dict):
        errors.append("merge_policy must be an object")
        merge = {}
    if merge.get("pull_request_required") is not True:
        errors.append("merge_policy.pull_request_required must be true")
    if merge.get("bypass_required_checks") is not False:
        errors.append("merge_policy.bypass_required_checks must be false")
    if merge.get("release_requires_separate_qualification") is not True:
        errors.append("merge_policy.release_requires_separate_qualification must be true")

    statuses = data.get("status_vocabulary")
    if not isinstance(statuses, list) or not REQUIRED_STATUSES.issubset(set(statuses)):
        errors.append("status_vocabulary must include all eight standard statuses")

    if errors:
        for item in errors:
            fail(item)
        return 1

    print(f"ENGINEERING STANDARD PASS: {repository}")
    print("Profile schema, repository identity, architecture guardrails, evidence gates, and merge policy are valid.")
    print("This check validates governance metadata only; it does not replace native builds, tests, reviews, or target qualification.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
