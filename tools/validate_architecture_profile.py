#!/usr/bin/env python3
"""Validate a repository's modular-monolith composition profile without executing products."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "ARCHITECTURE_PROFILE.json"
SCHEMA = "bboroski.modular-monolith-profile.v1"
MODES = {"modular-monolith", "static-library", "static-web", "freestanding-kernel", "host-tool", "research-workstream", "scaffold", "design-specification"}
MATURITY = {"experimental-alpha", "host-diagnostics", "host-tested-core", "static-portal", "early-kernel-bringup", "architecture-proposal", "experimental-foundation", "workspace-prototype", "scaffold-only", "design-specification"}
STATUSES = {"implemented", "partial", "planned", "specified", "not-present"}
INTEGRATION = {"in-process", "static-link", "versioned-contract", "metadata-only", "isolated-target", "planned", "not-applicable"}
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def validate(data, root=ROOT):
    errors = []
    if not isinstance(data, dict): return ["profile root must be an object"]
    if data.get("schema_version") != SCHEMA: errors.append("unsupported schema_version")
    if data.get("project") != root.name: errors.append(f"project must match repository directory {root.name!r}")
    if data.get("maturity") not in MATURITY: errors.append("unsupported maturity")
    arch = data.get("architecture")
    if not isinstance(arch, dict): errors.append("architecture must be an object"); arch = {}
    if arch.get("mode") not in MODES: errors.append("unsupported architecture.mode")
    for key in ("scope", "runtime_boundary", "composition_rule"):
        if not isinstance(arch.get(key), str) or not arch[key].strip(): errors.append(f"architecture.{key} is required")
    for key in ("entrypoints", "components", "dependencies", "preserved_boundaries", "forbidden_composition", "build_profiles", "gaps"):
        if not isinstance(data.get(key), list): errors.append(f"{key} must be an array")
    paths = []
    for i, item in enumerate(data.get("entrypoints", []) if isinstance(data.get("entrypoints"), list) else []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not item.get("kind"):
            errors.append(f"entrypoints[{i}] requires path and kind"); continue
        paths.append((f"entrypoints[{i}]", item["path"]))
    component_ids = set()
    for i, item in enumerate(data.get("components", []) if isinstance(data.get("components"), list) else []):
        if not isinstance(item, dict): errors.append(f"components[{i}] must be an object"); continue
        ident = item.get("id")
        if not isinstance(ident, str) or not SLUG.fullmatch(ident): errors.append(f"components[{i}].id must be a lowercase slug")
        elif ident in component_ids: errors.append(f"duplicate component id: {ident}")
        component_ids.add(ident)
        for key in ("responsibility",): 
            if not isinstance(item.get(key), str) or not item[key].strip(): errors.append(f"components[{i}].{key} is required")
        if item.get("status") not in STATUSES: errors.append(f"components[{i}].status is unsupported")
        if item.get("integration") not in INTEGRATION: errors.append(f"components[{i}].integration is unsupported")
    for i, item in enumerate(data.get("dependencies", []) if isinstance(data.get("dependencies"), list) else []):
        if not isinstance(item, dict) or not item.get("project") or not item.get("relationship"): errors.append(f"dependencies[{i}] requires project and relationship"); continue
        if not isinstance(item.get("runtime_dependency"), bool): errors.append(f"dependencies[{i}].runtime_dependency must be boolean")
    for field in ("preserved_boundaries", "forbidden_composition", "gaps"):
        value = data.get(field, [])
        if isinstance(value, list) and any(not isinstance(x, str) or not x.strip() for x in value): errors.append(f"{field} entries must be non-empty strings")
    profile_ids = set()
    for i, item in enumerate(data.get("build_profiles", []) if isinstance(data.get("build_profiles"), list) else []):
        if not isinstance(item, dict): errors.append(f"build_profiles[{i}] must be an object"); continue
        ident = item.get("id")
        if not isinstance(ident, str) or not SLUG.fullmatch(ident): errors.append(f"build_profiles[{i}].id must be a lowercase slug")
        elif ident in profile_ids: errors.append(f"duplicate build profile id: {ident}")
        profile_ids.add(ident)
        if item.get("status") not in {"declared", "blocked", "not-applicable", "not-yet-verified"}: errors.append(f"build_profiles[{i}].status is unsupported")
        if not isinstance(item.get("commands"), list) or any(not isinstance(x, str) or not x.strip() for x in item.get("commands", [])): errors.append(f"build_profiles[{i}].commands must be an array of command strings")
        if not isinstance(item.get("evidence"), list): errors.append(f"build_profiles[{i}].evidence must be an array")
        else:
            for j, path in enumerate(item["evidence"]):
                if not isinstance(path, str): errors.append(f"build_profiles[{i}].evidence[{j}] must be a path"); continue
                paths.append((f"build_profiles[{i}].evidence[{j}]", path))
    for field, path in paths:
        candidate = (root / path).resolve()
        if not candidate.is_relative_to(root.resolve()): errors.append(f"{field} escapes repository root: {path}")
        elif not candidate.exists(): errors.append(f"{field} does not exist: {path}")
    return errors

def self_test():
    sample = {"schema_version":SCHEMA,"project":"fixture","maturity":"scaffold-only","architecture":{"mode":"scaffold","scope":"fixture","runtime_boundary":"none","composition_rule":"no executable composition claimed"},"entrypoints":[],"components":[],"dependencies":[],"preserved_boundaries":["No code execution"],"forbidden_composition":["No inferred runtime"],"build_profiles":[{"id":"metadata-only","status":"declared","commands":[],"evidence":["README.md"]}],"gaps":["Implementation pending"]}
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp); (root/"README.md").write_text("fixture",encoding="utf-8")
        if validate(sample,root): raise AssertionError("valid fixture was rejected")
        broken=dict(sample); broken["schema_version"]="wrong"
        if not validate(broken,root): raise AssertionError("invalid fixture was accepted")
    print("Architecture profile validator self-test passed.")

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args()
    if args.self_test: self_test()
    try: data=json.loads(PROFILE.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: print(f"ERROR: cannot read {PROFILE.name}: {exc}",file=sys.stderr); return 2
    errors=validate(data)
    if errors:
        for error in errors: print(f"ERROR: {error}")
        print(f"Architecture profile check failed for {ROOT.name}."); return 1
    print(f"Architecture profile check passed for {ROOT.name}: {len(data['components'])} components, {len(data['build_profiles'])} build profiles.")
    return 0
if __name__ == "__main__": raise SystemExit(main())
