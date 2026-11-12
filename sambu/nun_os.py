"""Strict, read-only validation of NUN OS capability profiles."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any

MAX_PROFILE_BYTES = 1_048_576
STATUSES = frozenset({"implemented", "partial", "planned", "not_supported"})


class NUNOSProfileError(ValueError):
    """A NUN OS profile is malformed or makes an unsupported claim."""


class NUNOSFeatureUnavailable(NUNOSProfileError):
    """A requested feature is not implemented in the selected profile."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise NUNOSProfileError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _object(value: object, required: set[str], optional: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise NUNOSProfileError(f"{name} must be an object")
    missing, extra = required - value.keys(), value.keys() - required - optional
    if missing or extra:
        raise NUNOSProfileError(
            f"{name}: missing={sorted(missing)}, unknown={sorted(extra)}"
        )
    return value


def _text(value: object, name: str, limit: int = 512) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise NUNOSProfileError(f"{name} must be non-empty text (max {limit})")
    return value.strip()


def _strings(value: object, name: str, required: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise NUNOSProfileError(f"{name} must be an array")
    result = tuple(_text(item, name) for item in value)
    if len(set(result)) != len(result):
        raise NUNOSProfileError(f"{name} contains duplicates")
    if required and not result:
        raise NUNOSProfileError(f"{name} must include evidence for implemented/partial claims")
    return result


@dataclass(frozen=True, slots=True)
class NUNOSFeature:
    identifier: str
    domain: str
    status: str
    evidence: tuple[str, ...]
    notes: str = ""

    def to_dict(self) -> dict[str, object]:
        return {"id": self.identifier, "domain": self.domain, "status": self.status,
                "evidence": list(self.evidence), "notes": self.notes}


@dataclass(frozen=True, slots=True)
class NUNOSProfile:
    profile_id: str
    profile_version: str
    maturity: str
    targets: tuple[dict[str, object], ...]
    contracts: tuple[dict[str, object], ...]
    features: tuple[NUNOSFeature, ...]
    digest: str

    def feature(self, identifier: str) -> NUNOSFeature | None:
        return next((item for item in self.features if item.identifier == identifier), None)

    def require_feature(self, identifier: str, *, allow_partial: bool = False) -> NUNOSFeature:
        feature = self.feature(identifier)
        allowed = {"implemented", "partial"} if allow_partial else {"implemented"}
        if feature is None or feature.status not in allowed:
            status = "missing" if feature is None else feature.status
            raise NUNOSFeatureUnavailable(f"{identifier!r} is {status}; accepted: {sorted(allowed)}")
        return feature

    def summary(self) -> dict[str, object]:
        counts = {key: sum(item.status == key for item in self.features)
                  for key in sorted(STATUSES)}
        return {"os": "NUN", "profile_id": self.profile_id,
                "profile_version": self.profile_version, "maturity": self.maturity,
                "target_count": len(self.targets), "contract_count": len(self.contracts),
                "feature_count": len(self.features), "status_counts": counts,
                "sha256": self.digest}


def validate_nun_os_profile(payload: object) -> NUNOSProfile:
    fields = {"schema_version", "os", "profile_id", "profile_version", "maturity",
              "targets", "contracts", "features"}
    root = _object(payload, fields, set(), "profile")
    if type(root["schema_version"]) is not int or root["schema_version"] != 1:
        raise NUNOSProfileError("schema_version must be integer 1")
    if root["os"] != "NUN":
        raise NUNOSProfileError("os must be 'NUN'")
    profile_id = _text(root["profile_id"], "profile_id", 128)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", profile_id):
        raise NUNOSProfileError("profile_id must be lowercase kebab-case")
    version = _text(root["profile_version"], "profile_version", 64)
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise NUNOSProfileError("profile_version must use MAJOR.MINOR.PATCH")
    maturity = _text(root["maturity"], "maturity")
    if maturity not in {"research", "bring-up", "experimental", "beta", "stable"}:
        raise NUNOSProfileError("invalid profile maturity")

    if not isinstance(root["targets"], list) or not root["targets"]:
        raise NUNOSProfileError("targets must be a non-empty array")
    targets: list[dict[str, object]] = []
    for i, raw in enumerate(root["targets"]):
        item = _object(raw, {"architecture", "boot_protocol", "status"}, {"firmware"}, f"targets[{i}]")
        arch = _text(item["architecture"], f"targets[{i}].architecture")
        if arch not in {"x86_64", "aarch64", "riscv64", "e2k"}:
            raise NUNOSProfileError(f"targets[{i}] has unsupported architecture")
        protocol = _text(item["boot_protocol"], f"targets[{i}].boot_protocol")
        status = _text(item["status"], f"targets[{i}].status")
        if status not in STATUSES:
            raise NUNOSProfileError(f"targets[{i}] has invalid status")
        firmware = _strings(item.get("firmware", []), f"targets[{i}].firmware")
        if any(v not in {"bios", "uefi", "unknown"} for v in firmware):
            raise NUNOSProfileError(f"targets[{i}] has invalid firmware")
        targets.append({"architecture": arch, "boot_protocol": protocol,
                        "status": status, "firmware": list(firmware)})

    contracts: list[dict[str, object]] = []
    contract_ids: set[str] = set()
    if not isinstance(root["contracts"], list):
        raise NUNOSProfileError("contracts must be an array")
    for i, raw in enumerate(root["contracts"]):
        item = _object(raw, {"id", "version", "status", "evidence"}, {"notes"}, f"contracts[{i}]")
        identifier = _text(item["id"], f"contracts[{i}].id", 128)
        if identifier in contract_ids:
            raise NUNOSProfileError(f"duplicate contract id: {identifier}")
        contract_ids.add(identifier)
        status = _text(item["status"], f"contracts[{i}].status")
        if status not in {"implemented", "partial", "planned"}:
            raise NUNOSProfileError(f"contracts[{i}] has invalid status")
        evidence = _strings(item["evidence"], f"contracts[{i}].evidence",
                            required=status in {"implemented", "partial"})
        contracts.append({"id": identifier, "version": _text(item["version"], "contract version"),
                          "status": status, "evidence": list(evidence),
                          "notes": _text(item["notes"], "contract notes") if item.get("notes") else ""})

    if not isinstance(root["features"], list):
        raise NUNOSProfileError("features must be an array")
    features: list[NUNOSFeature] = []
    feature_ids: set[str] = set()
    for i, raw in enumerate(root["features"]):
        item = _object(raw, {"id", "domain", "status", "evidence"}, {"notes"}, f"features[{i}]")
        identifier = _text(item["id"], f"features[{i}].id", 128)
        if not re.fullmatch(r"[a-z0-9]+(?:[._-][a-z0-9]+)*", identifier):
            raise NUNOSProfileError(f"features[{i}] has invalid ID")
        if identifier in feature_ids:
            raise NUNOSProfileError(f"duplicate feature id: {identifier}")
        feature_ids.add(identifier)
        status = _text(item["status"], f"features[{i}].status")
        if status not in STATUSES:
            raise NUNOSProfileError(f"features[{i}] has invalid status")
        evidence = _strings(item["evidence"], f"features[{i}].evidence",
                            required=status in {"implemented", "partial"})
        notes = _text(item["notes"], f"features[{i}].notes") if item.get("notes") else ""
        features.append(NUNOSFeature(identifier, _text(item["domain"], "feature domain"),
                                     status, evidence, notes))

    canonical = json.dumps(root, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":"), allow_nan=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return NUNOSProfile(profile_id, version, maturity, tuple(targets), tuple(contracts),
                        tuple(features), digest)


def load_nun_os_profile(path: str | Path) -> NUNOSProfile:
    raw = Path(path).read_bytes()
    if len(raw) > MAX_PROFILE_BYTES:
        raise NUNOSProfileError(f"profile exceeds {MAX_PROFILE_BYTES} bytes")
    try:
        payload = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NUNOSProfileError(f"invalid UTF-8 JSON profile: {exc}") from exc
    return validate_nun_os_profile(payload)
