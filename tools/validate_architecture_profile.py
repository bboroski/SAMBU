#!/usr/bin/env python3
"""Validate a repository's modular-monolith composition profile without executing products."""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "ARCHITECTURE_PROFILE.json"
SCHEMA = "bboroski.modular-monolith-profile.v1"
MODES = {
    "modular-monolith", "static-library", "static-web", "freestanding-kernel",
    "host-tool", "research-workstream", "scaffold", "design-specification",
}
MATURITY = {
    "experimental-alpha", "host-diagnostics", "host-tested-core", "static-portal",
    "early-kernel-bringup", "architecture-proposal", "experimental-foundation",
    "workspace-prototype", "scaffold-only", "design-specification",
}
STATUSES = {"implemented", "partial", "planned", "specified", "not-present"}
INTEGRATION = {
    "in-process", "static-link", "versioned-contract", "metadata-only",
    "isolated-target", "planned", "not-applicable",
}
PROFILE_STATES = {"declared", "blocked", "not-applicable", "not-yet-verified"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate(data: Any, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["profile root must be an object"]
    if data.get("schema_version") != SCHEMA:
        errors.append("unsupported schema_version")
    if data.get("project") != root.name:
        errors.append(f"project must match repository directory {root.name!r}")
    if data.get("maturity") not in MATURITY:
        errors.append("unsupported maturity")

    architecture = data.get("architecture")
    if not isinstance(architecture, dict):
        errors.append("architecture must be an object")
        architecture = {}
    if architecture.get("mode") not in MODES:
        errors.append("unsupported architecture.mode")
    for key in ("scope", "runtime_boundary", "composition_rule"):
        value = architecture.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"architecture.{key} is required")

    array_fields = (
        "entrypoints", "components", "dependencies", "preserved_boundaries",
        "forbidden_composition", "build_profiles", "gaps",
    )
    for field in array_fields:
        if not isinstance(data.get(field), list):
            errors.append(f"{field} must be an array")

    referenced_paths: list[tuple[str, str]] = []
    entrypoints = data.get("entrypoints", [])
    if isinstance(entrypoints, list):
        for index, item in enumerate(entrypoints):
            if not isinstance(item, dict):
                errors.append(f"entrypoints[{index}] must be an object")
                continue
            path, kind = item.get("path"), item.get("kind")
            if not isinstance(path, str) or not path or not isinstance(kind, str) or not kind:
                errors.append(f"entrypoints[{index}] requires path and kind")
            else:
                referenced_paths.append((f"entrypoints[{index}]", path))

    component_ids: set[str] = set()
    components = data.get("components", [])
    if isinstance(components, list):
        for index, item in enumerate(components):
            if not isinstance(item, dict):
                errors.append(f"components[{index}] must be an object")
                continue
            ident = item.get("id")
            if not isinstance(ident, str) or not SLUG.fullmatch(ident):
                errors.append(f"components[{index}].id must be a lowercase slug")
            elif ident in component_ids:
                errors.append(f"duplicate component id: {ident}")
            else:
                component_ids.add(ident)
            responsibility = item.get("responsibility")
            if not isinstance(responsibility, str) or not responsibility.strip():
                errors.append(f"components[{index}].responsibility is required")
            if item.get("status") not in STATUSES:
                errors.append(f"components[{index}].status is unsupported")
            if item.get("integration") not in INTEGRATION:
                errors.append(f"components[{index}].integration is unsupported")

    dependencies = data.get("dependencies", [])
    if isinstance(dependencies, list):
        for index, item in enumerate(dependencies):
            if not isinstance(item, dict):
                errors.append(f"dependencies[{index}] must be an object")
                continue
            if not item.get("project") or not item.get("relationship"):
                errors.append(f"dependencies[{index}] requires project and relationship")
            if not isinstance(item.get("runtime_dependency"), bool):
                errors.append(f"dependencies[{index}].runtime_dependency must be boolean")

    for field in ("preserved_boundaries", "forbidden_composition", "gaps"):
        value = data.get(field, [])
        if isinstance(value, list) and any(
            not isinstance(entry, str) or not entry.strip() for entry in value
        ):
            errors.append(f"{field} entries must be non-empty strings")

    profile_ids: set[str] = set()
    build_profiles = data.get("build_profiles", [])
    if isinstance(build_profiles, list):
        for index, item in enumerate(build_profiles):
            if not isinstance(item, dict):
                errors.append(f"build_profiles[{index}] must be an object")
                continue
            ident = item.get("id")
            if not isinstance(ident, str) or not SLUG.fullmatch(ident):
                errors.append(f"build_profiles[{index}].id must be a lowercase slug")
            elif ident in profile_ids:
                errors.append(f"duplicate build profile id: {ident}")
            else:
                profile_ids.add(ident)
            if item.get("status") not in PROFILE_STATES:
                errors.append(f"build_profiles[{index}].status is unsupported")
            commands = item.get("commands")
            if not isinstance(commands, list) or any(
                not isinstance(command, str) or not command.strip() for command in commands
            ):
                errors.append(f"build_profiles[{index}].commands must be an array of command strings")
            evidence = item.get("evidence")
            if not isinstance(evidence, list):
                errors.append(f"build_profiles[{index}].evidence must be an array")
            else:
                for evidence_index, path in enumerate(evidence):
                    if not isinstance(path, str) or not path:
                        errors.append(
                            f"build_profiles[{index}].evidence[{evidence_index}] must be a path"
                        )
                    else:
                        referenced_paths.append(
                            (f"build_profiles[{index}].evidence[{evidence_index}]", path)
                        )

    repository_root = root.resolve()
    for label, relative_path in referenced_paths:
        candidate = (root / relative_path).resolve()
        if not candidate.is_relative_to(repository_root):
            errors.append(f"{label} escapes repository root: {relative_path}")
        elif not candidate.exists():
            errors.append(f"{label} does not exist: {relative_path}")
    return errors


def self_test() -> None:
    sample = {
        "schema_version": SCHEMA,
        "project": "fixture",
        "maturity": "scaffold-only",
        "architecture": {
            "mode": "scaffold",
            "scope": "validator fixture",
            "runtime_boundary": "no executable runtime",
            "composition_rule": "do not infer an application from metadata",
        },
        "entrypoints": [],
        "components": [],
        "dependencies": [],
        "preserved_boundaries": ["No code execution"],
        "forbidden_composition": ["No inferred runtime"],
        "build_profiles": [{
            "id": "metadata-only",
            "status": "declared",
            "commands": [],
            "evidence": ["README.md"],
        }],
        "gaps": ["Implementation pending"],
    }
    with tempfile.TemporaryDirectory() as temporary_directory:
        root = Path(temporary_directory) / "fixture"
        root.mkdir()
        (root / "README.md").write_text("fixture", encoding="utf-8")
        if validate(sample, root):
            raise AssertionError("valid profile fixture was rejected")
        invalid = dict(sample)
        invalid["schema_version"] = "invalid"
        if not validate(invalid, root):
            raise AssertionError("invalid schema version was accepted")
        traversal = dict(sample)
        traversal["build_profiles"] = [{
            "id": "escape-test", "status": "declared",
            "commands": [], "evidence": ["../outside.txt"],
        }]
        if not validate(traversal, root):
            raise AssertionError("path traversal was accepted")
    print("Architecture profile validator self-test passed.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    try:
        data = json.loads(PROFILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {PROFILE.name}: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Architecture profile check failed for {ROOT.name}.")
        return 1
    print(
        f"Architecture profile check passed for {ROOT.name}: "
        f"{len(data['components'])} components, {len(data['build_profiles'])} build profiles."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
