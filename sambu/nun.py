"""Nun: reproducible initial-state and boundary-condition manifests.

The mythological image of a primordial medium is used only as a design metaphor.
This module validates declared JSON-shaped inputs and creates a deterministic
manifest; it does not run a physical simulation, infer scientific laws, schedule
work, or mutate a host system.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
import re
from collections.abc import Iterable, Mapping


MAX_STATE_BYTES = 262_144
MAX_MANIFEST_BYTES = 1_048_576
MAX_JSON_DEPTH = 32
MAX_JSON_ITEMS = 10_000
MAX_SEED = 2**64 - 1

_IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")
_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?$")
_BOUNDARY_MODES = frozenset({"isolated", "exchange", "periodic"})


class NunError(ValueError):
    """Base error for initial-state and genesis-manifest validation."""


def _identifier(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER_RE.fullmatch(value.strip()):
        raise NunError(
            f"{field_name} must be a non-empty identifier of at most 128 characters"
        )
    return value.strip()


def _bounded_text(value: str, field_name: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise NunError(f"{field_name} must be non-empty text of at most {maximum} characters")
    return value.strip()


def _bounded_seed(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_SEED:
        raise NunError(f"seed must be an unsigned 64-bit integer (0..{MAX_SEED})")
    return value


def _labels(values: Iterable[str], field_name: str, *, sort: bool = True) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise NunError(f"{field_name} must be a collection of identifiers")
    try:
        result = tuple(_identifier(value, field_name) for value in values)
    except TypeError as exc:
        raise NunError(f"{field_name} must be iterable") from exc
    if len(set(result)) != len(result):
        raise NunError(f"{field_name} entries must be unique")
    return tuple(sorted(result)) if sort else result


def _normalize_json(
    value: object,
    *,
    depth: int = 0,
    counter: list[int] | None = None,
) -> object:
    if counter is None:
        counter = [0]
    if depth > MAX_JSON_DEPTH:
        raise NunError(f"payload nesting exceeds the maximum depth of {MAX_JSON_DEPTH}")
    counter[0] += 1
    if counter[0] > MAX_JSON_ITEMS:
        raise NunError(f"payload exceeds the maximum of {MAX_JSON_ITEMS} values")

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise NunError("payload numbers must be finite")
        return value
    if isinstance(value, Mapping):
        normalized: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise NunError("payload object keys must be strings")
            normalized[key] = _normalize_json(item, depth=depth + 1, counter=counter)
        return normalized
    if isinstance(value, (list, tuple)):
        return [
            _normalize_json(item, depth=depth + 1, counter=counter)
            for item in value
        ]
    raise NunError(f"unsupported payload value: {type(value).__name__}")


def _canonical_json(value: object, *, max_bytes: int) -> str:
    normalized = _normalize_json(value)
    try:
        encoded = json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError, RecursionError) as exc:
        raise NunError("payload must be bounded, finite JSON-shaped data") from exc
    if len(encoded.encode("utf-8")) > max_bytes:
        raise NunError(f"payload exceeds the maximum of {max_bytes} bytes")
    return encoded


def _digest(encoded: str) -> str:
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True, init=False)
class PrimordialState:
    """Immutable, reproducible snapshot of declared starting values.

    Values are stored as canonical JSON and returned as a defensive copy.
    The seed is explicit so consumers can reproduce their own stochastic work.
    """

    _values_json: str
    seed: int
    provenance: str
    digest: str

    def __init__(
        self,
        values: Mapping[str, object],
        *,
        seed: int = 0,
        provenance: str = "declared",
    ) -> None:
        if not isinstance(values, Mapping):
            raise NunError("initial values must be a mapping")
        normalized = _normalize_json(values)
        if not isinstance(normalized, dict):
            raise NunError("initial values must be a JSON object")
        for key in normalized:
            _identifier(key, "initial-state field")
        selected_seed = _bounded_seed(seed)
        selected_provenance = _bounded_text(provenance, "provenance", 256)
        values_json = json.dumps(
            normalized, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
        if len(values_json.encode("utf-8")) > MAX_STATE_BYTES:
            raise NunError(f"initial state exceeds the maximum of {MAX_STATE_BYTES} bytes")
        identity_json = _canonical_json(
            {
                "values": normalized,
                "seed": selected_seed,
                "provenance": selected_provenance,
            },
            max_bytes=MAX_STATE_BYTES + 512,
        )
        object.__setattr__(self, "_values_json", values_json)
        object.__setattr__(self, "seed", selected_seed)
        object.__setattr__(self, "provenance", selected_provenance)
        object.__setattr__(self, "digest", _digest(identity_json))

    @property
    def values(self) -> dict[str, object]:
        """Return a fresh copy so callers cannot mutate the stored snapshot."""
        return json.loads(self._values_json)

    def to_dict(self) -> dict[str, object]:
        return {
            "values": self.values,
            "seed": self.seed,
            "provenance": self.provenance,
            "digest": self.digest,
        }


@dataclass(frozen=True, slots=True, init=False)
class BoundaryProfile:
    """Declarative boundary metadata for an initial-state model.

    This validates the shape of a contract. It does not enforce conservation
    laws or apply boundary conditions to a numerical solver.
    """

    mode: str
    invariants: tuple[str, ...]
    external_inputs: tuple[str, ...]

    def __init__(
        self,
        *,
        mode: str = "isolated",
        invariants: Iterable[str] = (),
        external_inputs: Iterable[str] = (),
    ) -> None:
        if not isinstance(mode, str) or mode not in _BOUNDARY_MODES:
            raise NunError(
                "boundary mode must be isolated, exchange, or periodic"
            )
        selected_invariants = _labels(invariants, "invariants")
        selected_inputs = _labels(external_inputs, "external_inputs")
        overlap = set(selected_invariants) & set(selected_inputs)
        if overlap:
            raise NunError(
                "a boundary label cannot be both invariant and external input: "
                + ", ".join(sorted(overlap))
            )
        if mode in {"isolated", "periodic"} and selected_inputs:
            raise NunError(
                f"{mode} boundaries cannot declare external inputs; use mode='exchange'"
            )
        if mode == "exchange" and not selected_inputs:
            raise NunError("exchange boundaries require at least one explicit external input")
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "invariants", selected_invariants)
        object.__setattr__(self, "external_inputs", selected_inputs)

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "invariants": list(self.invariants),
            "external_inputs": list(self.external_inputs),
        }


@dataclass(frozen=True, slots=True)
class GenesisSpec:
    """Versioned declaration of an initial state and its environment."""

    identifier: str
    origin: PrimordialState
    boundary: BoundaryProfile = field(default_factory=BoundaryProfile)
    version: str = "1.0.0"
    required_fields: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "identifier", _identifier(self.identifier, "identifier"))
        if not isinstance(self.origin, PrimordialState):
            raise NunError("origin must be a PrimordialState")
        if not isinstance(self.boundary, BoundaryProfile):
            raise NunError("boundary must be a BoundaryProfile")
        if not isinstance(self.version, str) or not _VERSION_RE.fullmatch(self.version):
            raise NunError("version must use MAJOR.MINOR.PATCH with an optional suffix")
        object.__setattr__(
            self, "required_fields", _labels(self.required_fields, "required_fields")
        )
        if isinstance(self.assumptions, (str, bytes)):
            raise NunError("assumptions must be a collection of text entries")
        try:
            assumptions = tuple(
                _bounded_text(item, "assumption", 512) for item in self.assumptions
            )
        except TypeError as exc:
            raise NunError("assumptions must be iterable") from exc
        if len(set(assumptions)) != len(assumptions):
            raise NunError("assumptions entries must be unique")
        if len(assumptions) > 128:
            raise NunError("assumptions cannot contain more than 128 entries")
        object.__setattr__(self, "assumptions", assumptions)


@dataclass(frozen=True, slots=True)
class GenesisFinding:
    code: str
    severity: str
    subject: str
    message: str


@dataclass(frozen=True, slots=True)
class GenesisManifest:
    """Content-addressed description of a validated genesis specification."""

    _payload_json: str
    digest: str

    @property
    def payload(self) -> dict[str, object]:
        return json.loads(self._payload_json)

    def to_dict(self) -> dict[str, object]:
        result = self.payload
        result["manifest_digest"] = self.digest
        return result


@dataclass(frozen=True, slots=True)
class GenesisReport:
    identifier: str
    findings: tuple[GenesisFinding, ...]
    manifest: GenesisManifest | None

    @property
    def is_valid(self) -> bool:
        return self.manifest is not None and not any(
            item.severity == "error" for item in self.findings
        )

    @property
    def errors(self) -> tuple[GenesisFinding, ...]:
        return tuple(item for item in self.findings if item.severity == "error")

    def to_dict(self) -> dict[str, object]:
        return {
            "identifier": self.identifier,
            "is_valid": self.is_valid,
            "findings": [asdict(item) for item in self.findings],
            "manifest": self.manifest.to_dict() if self.manifest is not None else None,
        }


class NunEngine:
    """Build deterministic manifests from explicit, bounded initial conditions.

    The engine is pure with respect to host state: it does not execute callbacks,
    read files, access the network, or start simulations.
    """

    def __init__(self, *, max_manifest_bytes: int = MAX_MANIFEST_BYTES) -> None:
        if (
            isinstance(max_manifest_bytes, bool)
            or not isinstance(max_manifest_bytes, int)
            or not 1 <= max_manifest_bytes <= 16_000_000
        ):
            raise NunError("max_manifest_bytes must be an integer from 1 to 16000000")
        self.max_manifest_bytes = max_manifest_bytes

    def prepare(self, spec: GenesisSpec) -> GenesisReport:
        if not isinstance(spec, GenesisSpec):
            raise NunError("spec must be a GenesisSpec")

        values = spec.origin.values
        missing = tuple(
            name for name in spec.required_fields if name not in values
        )
        if missing:
            finding = GenesisFinding(
                "NUN-STATE-001",
                "error",
                spec.identifier,
                "required initial-state fields are missing: " + ", ".join(missing),
            )
            return GenesisReport(spec.identifier, (finding,), None)

        payload: dict[str, object] = {
            "schema": "sambu.nun.genesis/v1",
            "identifier": spec.identifier,
            "version": spec.version,
            "origin": {
                "values": values,
                "seed": spec.origin.seed,
                "provenance": spec.origin.provenance,
                "digest": spec.origin.digest,
            },
            "boundary": spec.boundary.to_dict(),
            "required_fields": list(spec.required_fields),
            "assumptions": list(spec.assumptions),
        }
        try:
            payload_json = _canonical_json(
                payload, max_bytes=self.max_manifest_bytes
            )
        except NunError as exc:
            finding = GenesisFinding(
                "NUN-MANIFEST-001", "error", spec.identifier, str(exc)
            )
            return GenesisReport(spec.identifier, (finding,), None)

        manifest = GenesisManifest(payload_json, _digest(payload_json))
        return GenesisReport(spec.identifier, (), manifest)


__all__ = [
    "MAX_STATE_BYTES",
    "MAX_MANIFEST_BYTES",
    "MAX_JSON_DEPTH",
    "MAX_JSON_ITEMS",
    "MAX_SEED",
    "NunError",
    "PrimordialState",
    "BoundaryProfile",
    "GenesisSpec",
    "GenesisFinding",
    "GenesisManifest",
    "GenesisReport",
    "NunEngine",
]
