#!/usr/bin/env python3
"""Single-entrypoint developer workflow for SAMBU."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build" / "native"


def run(label: str, command: list[str]) -> None:
    print(f"\n==> {label}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def build_native() -> None:
    cmake = shutil.which("cmake")
    if not cmake:
        raise RuntimeError("CMake is required for the native IR kernel. Install CMake and retry.")
    run("Configure native IR kernel", [cmake, "-S", "native", "-B", str(BUILD), "-DBUILD_TESTING=ON"])
    run("Build native IR kernel", [cmake, "--build", str(BUILD), "--parallel"])
    run("Test native IR kernel", [shutil.which("ctest") or "ctest", "--test-dir", str(BUILD), "--output-on-failure"])


def check() -> None:
    run("Validate academic biology glossary", [sys.executable, "tools/validate_biology_terms.py"])
    run("Validate Reaper-inspired engineering catalogue", [sys.executable, "tools/validate_reaper_domain.py"])
    run("Validate closed-domain metric model", [sys.executable, "tools/validate_closed_domain.py", "data/physics/closed_domain_metric.example.json"])
    run("Self-test closed-domain metric validator", [sys.executable, "tools/validate_closed_domain.py", "--self-test"])
    run("Python unit tests", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    for sample in (
        "examples/percentages.sambu",
        "examples/anatidae_biophysics.sambu",
        "examples/ecosystem_primitives.sambu",
        "examples/voxel_world.sambu",
        "examples/supervised_runtime.sambu",
    ):
        run(f"SAMBU smoke test: {sample}", [sys.executable, "-m", "sambu", sample])
    build_native()


def launch_ide() -> None:
    from sambu_ide.app import main
    result = main()
    if isinstance(result, int) and result:
        raise SystemExit(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="SAMBU one-knob build, test and IDE launcher.")
    parser.add_argument("command", nargs="?", choices=("check", "build", "run"), default="run")
    args = parser.parse_args()
    try:
        if args.command == "build":
            build_native()
        elif args.command == "check":
            check()
        else:
            check()
            launch_ide()
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"SAMBU one-knob failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
