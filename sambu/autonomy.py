"""Bounded, evidence-led autonomy primitives for SAMBU.

This module plans work and evaluates proposed changes. It deliberately does not
execute arbitrary Python, modify files, grant host privileges, or merge code.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import math
import re
from typing import Iterable
from pathlib import PurePosixPath


class AutonomyError(ValueError):
    """Base error for autonomy policy and evidence failures."""


class CapabilityDenied(AutonomyError):
    """A task requested a capability outside the active policy."""


class LedgerFull(AutonomyError):
    """The append-only experiment ledger reached its configured capacity."""


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


_RISK_ORDER = {
    RiskTier.LOW: 0,
    RiskTier.MEDIUM: 1,
    RiskTier.HIGH: 2,
    RiskTier.CRITICAL: 3,
}
_ZERO_DIGEST = "0" * 64
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_NAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.-]{0,63}$")


def _positive_int(value: int, name: str, *, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > maximum:
        raise ValueError(f"{name} must be an integer between 1 and {maximum}")
    return value


def _seed(value: int) -> int:
    if (isinstance(value, bool) or not isinstance(value, int)
            or value < -(2 ** 63) or value > (2 ** 64 - 1)):
        raise ValueError("seed must be a signed/unsigned 64-bit integer")
    return value


def _non_empty(value: str, name: str, *, limit: int = 512) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{name} must be a non-empty string of at most {limit} characters")
    return value.strip()


def _names(values: Iterable[str], name: str) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be an iterable of names, not a string")
    result = tuple(sorted({_non_empty(value, name, limit=128) for value in values}))
    if not result:
        raise ValueError(f"{name} must contain at least one entry")
    return result


def _risk(value: RiskTier | str) -> RiskTier:
    try:
        return value if isinstance(value, RiskTier) else RiskTier(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("risk tier must be low, medium, high, or critical") from exc


def _validate_json_shape(value: object, *, depth: int = 0, count: list[int] | None = None) -> None:
    """Reject ambiguous, excessively deep or excessively broad JSON-shaped values."""
    if count is None:
        count = [0]
    if depth > 64:
        raise TypeError("evidence nesting exceeds the maximum depth of 64")
    count[0] += 1
    if count[0] > 100_000:
        raise TypeError("evidence exceeds the maximum of 100,000 values")
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise TypeError("evidence numbers must be finite")
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_json_shape(item, depth=depth + 1, count=count)
        return
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("evidence object keys must be strings")
        for item in value.values():
            _validate_json_shape(item, depth=depth + 1, count=count)
        return
    raise TypeError(f"unsupported evidence value: {type(value).__name__}")


def _canonical_json(value: object, *, max_bytes: int = 1_048_576) -> str:
    """Serialize bounded JSON-shaped evidence with stable key ordering."""
    _positive_int(max_bytes, "max_bytes", maximum=268_435_456)
    _validate_json_shape(value)
    try:
        encoded = json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
    except (TypeError, ValueError, RecursionError) as exc:
        raise TypeError("evidence must contain bounded finite JSON-shaped values") from exc
    if len(encoded.encode("utf-8")) > max_bytes:
        raise ValueError(f"canonical JSON payload exceeds {max_bytes} bytes")
    return encoded


def fingerprint(value: object) -> str:
    """Return a stable SHA-256 digest of a JSON-shaped value."""
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ResourceBudget:
    """Hard upper bounds for one planned task.

    These are admission-control limits, not a claim that this module can measure
    Python heap use or preempt a running host function.
    """

    max_steps: int = 10_000
    max_messages: int = 1_000
    max_payload_bytes: int = 262_144
    max_retries: int = 0

    def __post_init__(self) -> None:
        _positive_int(self.max_steps, "max_steps", maximum=100_000_000)
        _positive_int(self.max_messages, "max_messages", maximum=1_000_000)
        _positive_int(self.max_payload_bytes, "max_payload_bytes", maximum=16_777_216)
        if (isinstance(self.max_retries, bool) or not isinstance(self.max_retries, int)
                or self.max_retries < 0 or self.max_retries > 100):
            raise ValueError("max_retries must be an integer between 0 and 100")

    def cap_to(self, maximum: "ResourceBudget") -> tuple["ResourceBudget", tuple[str, ...]]:
        """Return the component-wise minimum and the names of clipped limits."""
        if not isinstance(maximum, ResourceBudget):
            raise TypeError("maximum must be a ResourceBudget")
        clipped = []
        values = {}
        for name in ("max_steps", "max_messages", "max_payload_bytes", "max_retries"):
            requested = getattr(self, name)
            allowed = getattr(maximum, name)
            values[name] = min(requested, allowed)
            if requested > allowed:
                clipped.append(name)
        return ResourceBudget(**values), tuple(clipped)


@dataclass(frozen=True, slots=True)
class TaskManifest:
    """Declarative request for bounded work; it contains no executable code."""

    name: str
    purpose: str
    capabilities: tuple[str, ...]
    budget: ResourceBudget = ResourceBudget()
    risk: RiskTier = RiskTier.LOW
    seed: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _non_empty(self.name, "task name", limit=64))
        if not _NAME_RE.fullmatch(self.name):
            raise ValueError("task name may contain letters, digits, dot, underscore and hyphen")
        object.__setattr__(self, "purpose", _non_empty(self.purpose, "task purpose"))
        object.__setattr__(self, "capabilities", _names(self.capabilities, "capability"))
        object.__setattr__(self, "risk", _risk(self.risk))
        if not isinstance(self.budget, ResourceBudget):
            raise TypeError("budget must be a ResourceBudget")
        object.__setattr__(self, "seed", _seed(self.seed))


@dataclass(frozen=True, slots=True)
class AutonomyPolicy:
    """Immutable policy that can only reduce task authority and resource budgets."""

    allowed_capabilities: frozenset[str] = frozenset({
        "compute", "ledger.read", "ledger.append",
    })
    maximum_budget: ResourceBudget = ResourceBudget()
    maximum_autonomous_risk: RiskTier = RiskTier.LOW
    allowed_change_roots: tuple[str, ...] = (
        "sambu/", "tests/", "docs/", "examples/", "benchmarks/",
    )
    protected_paths: tuple[str, ...] = (
        ".github/", ".git/", "secrets/", ".secrets/",
        "pyproject.toml", "setup.py", "setup.cfg",
    )

    def __post_init__(self) -> None:
        if isinstance(self.allowed_capabilities, (str, bytes)):
            raise TypeError("allowed_capabilities must be an iterable of names")
        if isinstance(self.allowed_change_roots, (str, bytes)):
            raise TypeError("allowed_change_roots must be an iterable of path prefixes")
        caps = frozenset(
            _non_empty(value, "allowed capability", limit=128)
            for value in self.allowed_capabilities
        )
        roots = tuple(sorted({
            _non_empty(value, "allowed change root", limit=256)
            for value in self.allowed_change_roots
        }))
        protected = tuple(_non_empty(p, "protected path", limit=256) for p in self.protected_paths)
        if not isinstance(self.maximum_budget, ResourceBudget):
            raise TypeError("maximum_budget must be a ResourceBudget")
        if isinstance(self.protected_paths, (str, bytes)):
            raise TypeError("protected_paths must be an iterable of repository paths")
        object.__setattr__(self, "allowed_capabilities", caps)
        object.__setattr__(self, "maximum_autonomous_risk", _risk(self.maximum_autonomous_risk))
        object.__setattr__(self, "allowed_change_roots", roots)
        object.__setattr__(self, "protected_paths", protected)


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """Auditable admission decision. It is not an executor or sandbox."""

    task_name: str
    status: str
    granted_capabilities: tuple[str, ...]
    effective_budget: ResourceBudget
    clipped_limits: tuple[str, ...]
    reasons: tuple[str, ...]
    digest: str

    @property
    def admitted(self) -> bool:
        return self.status == "ready"


@dataclass(frozen=True, slots=True)
class ChangeProposal:
    """A reviewable change description without patch contents or write authority."""

    title: str
    summary: str
    changed_paths: tuple[str, ...]
    risk: RiskTier = RiskTier.LOW
    required_tests: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    reversible: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "title", _non_empty(self.title, "proposal title", limit=160))
        object.__setattr__(self, "summary", _non_empty(self.summary, "proposal summary"))
        if isinstance(self.changed_paths, (str, bytes)):
            raise TypeError("changed_paths must be an iterable of repository paths")
        paths = tuple(_non_empty(p, "changed path", limit=512) for p in self.changed_paths)
        if not paths:
            raise ValueError("a proposal must name at least one changed path")
        object.__setattr__(self, "changed_paths", paths)
        object.__setattr__(self, "risk", _risk(self.risk))
        if isinstance(self.required_tests, (str, bytes)):
            raise TypeError("required_tests must be an iterable of test identifiers")
        if isinstance(self.evidence_refs, (str, bytes)):
            raise TypeError("evidence_refs must be an iterable of evidence identifiers")
        object.__setattr__(self, "required_tests", tuple(
            _non_empty(x, "required test", limit=256) for x in self.required_tests
        ))
        object.__setattr__(self, "evidence_refs", tuple(
            _non_empty(x, "evidence reference", limit=512) for x in self.evidence_refs
        ))
        if not isinstance(self.reversible, bool):
            raise TypeError("reversible must be a boolean")


@dataclass(frozen=True, slots=True)
class ChangeEvaluation:
    """Preflight verdict; no verdict authorizes a merge or deployment."""

    verdict: str
    proposal_digest: str
    reasons: tuple[str, ...]

    @property
    def may_enter_review(self) -> bool:
        return self.verdict in {"ready_for_tests", "human_review_required"}


@dataclass(frozen=True, slots=True)
class ExperimentRecord:
    """One append-only, hash-chained experiment observation."""

    sequence: int
    hypothesis: str
    method: str
    input_digest: str
    outcome_json: str
    evidence_refs: tuple[str, ...]
    seed: int
    previous_digest: str
    digest: str

    @property
    def outcome(self) -> object:
        """Return a fresh decoded copy so callers cannot mutate the ledger."""
        return json.loads(self.outcome_json)


class ExperimentLedger:
    """Bounded append-only evidence ledger with deterministic hash chaining."""

    def __init__(
        self, *, max_records: int = 10_000, max_total_bytes: int = 16_777_216,
    ):
        self.max_records = _positive_int(max_records, "max_records", maximum=1_000_000)
        self.max_total_bytes = _positive_int(
            max_total_bytes, "max_total_bytes", maximum=1_073_741_824
        )
        self._records: list[ExperimentRecord] = []
        self._stored_bytes = 0

    @property
    def records(self) -> tuple[ExperimentRecord, ...]:
        return tuple(self._records)

    @property
    def stored_bytes(self) -> int:
        return self._stored_bytes

    def find_by_input(self, input_digest: str) -> tuple[ExperimentRecord, ...]:
        """Return all observations made with one canonical input fingerprint."""
        if not isinstance(input_digest, str) or not _SHA256_RE.fullmatch(input_digest):
            raise ValueError("input_digest must be a lowercase SHA-256 hex digest")
        return tuple(record for record in self._records if record.input_digest == input_digest)

    def export_json(self) -> str:
        """Return a deterministic portable snapshot; persistence remains host-owned."""
        rows = [{
            "sequence": record.sequence,
            "hypothesis": record.hypothesis,
            "method": record.method,
            "input_digest": record.input_digest,
            "outcome_json": record.outcome_json,
            "evidence_refs": record.evidence_refs,
            "seed": record.seed,
            "previous_digest": record.previous_digest,
            "digest": record.digest,
        } for record in self._records]
        return _canonical_json({
            "format": "sambu.experiment-ledger/v1",
            "records": rows,
        }, max_bytes=min(268_435_456, self.max_total_bytes * 2 + 1_048_576))

    def record(
        self,
        hypothesis: str,
        method: str,
        input_digest: str,
        outcome: object,
        evidence_refs: Iterable[str],
        *,
        seed: int = 0,
    ) -> ExperimentRecord:
        if len(self._records) >= self.max_records:
            raise LedgerFull("experiment ledger capacity reached; export or rotate it explicitly")
        hypothesis = _non_empty(hypothesis, "hypothesis", limit=2_000)
        method = _non_empty(method, "method", limit=512)
        if not isinstance(input_digest, str) or not _SHA256_RE.fullmatch(input_digest):
            raise ValueError("input_digest must be a lowercase SHA-256 hex digest")
        evidence = tuple(_names(evidence_refs, "evidence reference"))
        seed = _seed(seed)
        outcome_json = _canonical_json(outcome, max_bytes=32_768)
        previous = self._records[-1].digest if self._records else _ZERO_DIGEST
        payload = {
            "sequence": len(self._records) + 1,
            "hypothesis": hypothesis,
            "method": method,
            "input_digest": input_digest,
            "outcome_json": outcome_json,
            "evidence_refs": evidence,
            "seed": seed,
            "previous_digest": previous,
        }
        serialized_payload = _canonical_json(payload, max_bytes=65_536)
        record_size = len(serialized_payload.encode("utf-8"))
        if self._stored_bytes + record_size > self.max_total_bytes:
            raise LedgerFull("experiment ledger byte capacity reached")
        digest = hashlib.sha256(serialized_payload.encode("utf-8")).hexdigest()
        record = ExperimentRecord(
            sequence=payload["sequence"],
            hypothesis=hypothesis,
            method=method,
            input_digest=input_digest,
            outcome_json=outcome_json,
            evidence_refs=evidence,
            seed=seed,
            previous_digest=previous,
            digest=digest,
        )
        self._records.append(record)
        self._stored_bytes += record_size
        return record

    def verify(self) -> bool:
        """Recompute every link and record digest; return False on any mutation."""
        previous = _ZERO_DIGEST
        for expected_sequence, record in enumerate(self._records, start=1):
            payload = {
                "sequence": expected_sequence,
                "hypothesis": record.hypothesis,
                "method": record.method,
                "input_digest": record.input_digest,
                "outcome_json": record.outcome_json,
                "evidence_refs": record.evidence_refs,
                "seed": record.seed,
                "previous_digest": previous,
            }
            if record.sequence != expected_sequence or record.previous_digest != previous:
                return False
            if fingerprint(payload) != record.digest:
                return False
            previous = record.digest
        return True


class SambuMachine:
    """Deterministic policy core for planning and evaluating proposed changes.

    SambuMachine never executes tasks, runs untrusted experiments, edits the
    repository, changes its own policy, or merges a pull request. A host tool
    must separately perform any admitted action and supply evidence afterwards.
    """

    def __init__(
        self,
        policy: AutonomyPolicy | None = None,
        *,
        ledger: ExperimentLedger | None = None,
    ):
        if policy is not None and not isinstance(policy, AutonomyPolicy):
            raise TypeError("policy must be an AutonomyPolicy")
        if ledger is not None and not isinstance(ledger, ExperimentLedger):
            raise TypeError("ledger must be an ExperimentLedger")
        self.policy = policy if policy is not None else AutonomyPolicy()
        self.ledger = ledger if ledger is not None else ExperimentLedger()

    def plan(self, manifest: TaskManifest) -> ExecutionPlan:
        if not isinstance(manifest, TaskManifest):
            raise TypeError("plan() requires a TaskManifest")
        denied = sorted(set(manifest.capabilities) - self.policy.allowed_capabilities)
        if denied:
            raise CapabilityDenied("capabilities not granted by policy: " + ", ".join(denied))
        effective, clipped = manifest.budget.cap_to(self.policy.maximum_budget)
        needs_review = _RISK_ORDER[manifest.risk] > _RISK_ORDER[self.policy.maximum_autonomous_risk]
        reasons = []
        if clipped:
            reasons.append("requested limits capped: " + ", ".join(clipped))
        if needs_review:
            reasons.append(f"risk {manifest.risk.value} exceeds autonomous ceiling")
        granted = () if needs_review else tuple(sorted(manifest.capabilities))
        payload = {
            "name": manifest.name,
            "purpose": manifest.purpose,
            "risk": manifest.risk.value,
            "seed": manifest.seed,
            "requested_capabilities": tuple(sorted(manifest.capabilities)),
            "granted_capabilities": granted,
            "requested_budget": {
                "max_steps": manifest.budget.max_steps,
                "max_messages": manifest.budget.max_messages,
                "max_payload_bytes": manifest.budget.max_payload_bytes,
                "max_retries": manifest.budget.max_retries,
            },
            "policy_maximum_budget": {
                "max_steps": self.policy.maximum_budget.max_steps,
                "max_messages": self.policy.maximum_budget.max_messages,
                "max_payload_bytes": self.policy.maximum_budget.max_payload_bytes,
                "max_retries": self.policy.maximum_budget.max_retries,
            },
            "policy_maximum_risk": self.policy.maximum_autonomous_risk.value,
            "budget": {
                "max_steps": effective.max_steps,
                "max_messages": effective.max_messages,
                "max_payload_bytes": effective.max_payload_bytes,
                "max_retries": effective.max_retries,
            },
            "clipped": clipped,
            "policy_capabilities": tuple(sorted(self.policy.allowed_capabilities)),
        }
        return ExecutionPlan(
            task_name=manifest.name,
            status="human_review_required" if needs_review else "ready",
            granted_capabilities=granted,
            effective_budget=effective,
            clipped_limits=clipped,
            reasons=tuple(reasons),
            digest=fingerprint(payload),
        )

    def evaluate_change(self, proposal: ChangeProposal) -> ChangeEvaluation:
        if not isinstance(proposal, ChangeProposal):
            raise TypeError("evaluate_change() requires a ChangeProposal")
        reasons: list[str] = []
        paths = proposal.changed_paths
        for raw_path in paths:
            path = PurePosixPath(raw_path)
            normalized = path.as_posix()
            if path.is_absolute() or ".." in path.parts or "\\" in raw_path:
                reasons.append(f"unsafe repository path: {raw_path}")
                continue
            if any(normalized == p or normalized.startswith(p) for p in self.policy.protected_paths):
                reasons.append(f"protected path requires a separate human-controlled workflow: {raw_path}")
                continue
            if not any(normalized.startswith(root) for root in self.policy.allowed_change_roots):
                reasons.append(f"path is outside the autonomous review scope: {raw_path}")
        if not proposal.reversible:
            reasons.append("irreversible changes are not eligible for the autonomous lane")
        if not proposal.required_tests:
            reasons.append("proposal must name at least one executable or reviewable test")
        if not proposal.evidence_refs:
            reasons.append("proposal must include at least one evidence reference")
        if proposal.risk == RiskTier.CRITICAL:
            reasons.append("critical-risk changes always require a separately governed process")
        digest = fingerprint({
            "title": proposal.title,
            "summary": proposal.summary,
            "changed_paths": paths,
            "risk": proposal.risk.value,
            "required_tests": proposal.required_tests,
            "evidence_refs": proposal.evidence_refs,
            "reversible": proposal.reversible,
        })
        if reasons:
            return ChangeEvaluation("rejected", digest, tuple(reasons))
        if _RISK_ORDER[proposal.risk] > _RISK_ORDER[self.policy.maximum_autonomous_risk]:
            return ChangeEvaluation(
                "human_review_required", digest,
                (f"risk {proposal.risk.value} exceeds autonomous ceiling",),
            )
        return ChangeEvaluation(
            "ready_for_tests", digest,
            ("preflight passed; tests and independent review are still required",),
        )

    def record_experiment(
        self,
        hypothesis: str,
        method: str,
        inputs: object,
        outcome: object,
        evidence_refs: Iterable[str],
        *,
        seed: int = 0,
    ) -> ExperimentRecord:
        """Record an observation; inputs are fingerprinted, not retained."""
        return self.ledger.record(
            hypothesis, method, fingerprint(inputs), outcome, evidence_refs, seed=seed,
        )

    def audit(self) -> dict[str, object]:
        return {
            "ledger_records": len(self.ledger.records),
            "ledger_bytes": self.ledger.stored_bytes,
            "ledger_valid": self.ledger.verify(),
            "policy_capabilities": tuple(sorted(self.policy.allowed_capabilities)),
            "maximum_autonomous_risk": self.policy.maximum_autonomous_risk.value,
            "autonomous_file_roots": self.policy.allowed_change_roots,
            "protected_paths": self.policy.protected_paths,
            "execution_enabled": False,
            "self_modification_enabled": False,
            "merge_enabled": False,
        }
