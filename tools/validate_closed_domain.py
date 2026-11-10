#!/usr/bin/env python3
"""Validate a CDM-1 closed-domain metric input using only the stdlib."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

C = 299_792_458.0
VALID_SIGNATURES = {"-+++": (1, 3), "+---": (3, 1)}


def _number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(float(value))


def _eigenvalues_symmetric(matrix: list[list[float]]) -> list[float]:
    """Jacobi diagonalization; returns the eigenvalue estimates of a 4x4 symmetric matrix."""
    a = [[float(v) for v in row] for row in matrix]
    n = len(a)
    for _ in range(100 * n * n):
        p, q, largest = 0, 1, 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(a[i][j]) > largest:
                    p, q, largest = i, j, abs(a[i][j])
        if largest < 1e-14:
            break
        apq = a[p][q]
        if abs(apq) < 1e-30:
            continue
        tau = (a[q][q] - a[p][p]) / (2.0 * apq)
        sign = 1.0 if tau >= 0 else -1.0
        t = sign / (abs(tau) + math.sqrt(1.0 + tau * tau))
        c = 1.0 / math.sqrt(1.0 + t * t)
        s = t * c
        app, aqq = a[p][p], a[q][q]
        a[p][p] = app - t * apq
        a[q][q] = aqq + t * apq
        a[p][q] = a[q][p] = 0.0
        for k in range(n):
            if k == p or k == q:
                continue
            akp, akq = a[k][p], a[k][q]
            a[k][p] = a[p][k] = c * akp - s * akq
            a[k][q] = a[q][k] = s * akp + c * akq
    return [a[i][i] for i in range(n)]


def validate(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be a JSON object"]

    required = ("schema_version", "domain_id", "coordinates", "metric_tensor", "boundary", "exchange_policy")
    for key in required:
        if key not in data:
            errors.append(f"missing required field: {key}")
    if errors:
        return errors

    if data["schema_version"] != "1.0.0":
        errors.append("schema_version must be '1.0.0'")
    if not isinstance(data["domain_id"], str) or not data["domain_id"].strip():
        errors.append("domain_id must be a non-empty string")

    coords = data["coordinates"]
    if not isinstance(coords, dict) or coords.get("dimension") != 4:
        errors.append("coordinates.dimension must be 4")
        coords = {}
    signature = coords.get("signature")
    if signature not in VALID_SIGNATURES:
        errors.append("coordinates.signature must be '-+++' or '+---'")

    metric = data["metric_tensor"]
    matrix_ok = (
        isinstance(metric, list) and len(metric) == 4
        and all(isinstance(row, list) and len(row) == 4 for row in metric)
        and all(_number(v) for row in metric for v in row)
    )
    if not matrix_ok:
        errors.append("metric_tensor must be a finite numeric 4x4 matrix")
    else:
        scale = max(1.0, max(abs(float(v)) for row in metric for v in row))
        tol = 1e-12 * scale
        for i in range(4):
            for j in range(i + 1, 4):
                if abs(float(metric[i][j]) - float(metric[j][i])) > tol:
                    errors.append("metric_tensor must be symmetric")
                    matrix_ok = False
                    break
        if matrix_ok and signature in VALID_SIGNATURES:
            eigenvalues = _eigenvalues_symmetric(metric)
            zero_tol = 1e-12 * max(1.0, max(abs(v) for v in eigenvalues))
            negative = sum(v < -zero_tol for v in eigenvalues)
            positive = sum(v > zero_tol for v in eigenvalues)
            expected_negative, expected_positive = VALID_SIGNATURES[signature]
            if negative != expected_negative or positive != expected_positive:
                errors.append(f"metric_tensor inertia does not match signature {signature}")

    boundary = data["boundary"]
    if not isinstance(boundary, dict) or boundary.get("metric_variation") not in ("dirichlet", "neumann"):
        errors.append("boundary.metric_variation must be exactly 'dirichlet' or 'neumann'")

    policy = data["exchange_policy"]
    if not isinstance(policy, dict):
        errors.append("exchange_policy must be an object")
    else:
        for channel in ("matter", "energy", "information"):
            if type(policy.get(channel)) is not bool:
                errors.append(f"exchange_policy.{channel} must be boolean")
            elif policy[channel] is not False:
                errors.append(f"isolated CDM-1 profile requires exchange_policy.{channel}=false")

    ledger = data.get("energy_ledger")
    if ledger is not None:
        if not isinstance(ledger, dict) or not all(_number(ledger.get(k)) for k in ("initial_j", "final_j", "tolerance_j")):
            errors.append("energy_ledger requires finite initial_j, final_j, and tolerance_j")
        elif ledger["initial_j"] < 0 or ledger["final_j"] < 0 or ledger["tolerance_j"] < 0:
            errors.append("energy_ledger values must be non-negative")
        elif abs(float(ledger["final_j"]) - float(ledger["initial_j"])) > float(ledger["tolerance_j"]):
            errors.append("energy_ledger does not close within tolerance_j")

    mass = data.get("mass_model")
    if mass is not None:
        if not isinstance(mass, dict) or not _number(mass.get("rest_energy_j")) or not _number(mass.get("effective_rest_mass_kg")):
            errors.append("mass_model requires finite rest_energy_j and effective_rest_mass_kg")
        elif mass["rest_energy_j"] < 0 or mass["effective_rest_mass_kg"] < 0:
            errors.append("mass_model energy and mass must be non-negative")
        else:
            rel_tol = mass.get("relative_tolerance", 1e-9)
            if not _number(rel_tol) or rel_tol < 0 or rel_tol > 0.01:
                errors.append("mass_model.relative_tolerance must be between 0 and 0.01")
            else:
                expected = float(mass["rest_energy_j"]) / (C * C)
                actual = float(mass["effective_rest_mass_kg"])
                if not math.isclose(actual, expected, rel_tol=float(rel_tol), abs_tol=1e-30):
                    errors.append("effective_rest_mass_kg must equal rest_energy_j / c^2; this is not a geometry-derived mass law")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--self-test":
        valid = json.loads(Path("data/physics/closed_domain_metric.example.json").read_text(encoding="utf-8"))
        if validate(valid):
            print("FAIL: canonical example did not validate")
            return 1
        invalid = json.loads(json.dumps(valid))
        invalid["exchange_policy"]["energy"] = True
        if not validate(invalid):
            print("FAIL: invalid exchange policy was accepted")
            return 1
        invalid = json.loads(json.dumps(valid))
        invalid["metric_tensor"][0][0] = 1
        if not validate(invalid):
            print("FAIL: invalid metric signature was accepted")
            return 1
        print("PASS: CDM-1 self-tests")
        return 0
    if len(argv) != 2:
        print("usage: python tools/validate_closed_domain.py <json-file> | --self-test")
        return 2
    path = Path(argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS: {path} satisfies CDM-1 input invariants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
