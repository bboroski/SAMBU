"""Safe, testable engineering abstractions inspired by Reaper/Mass Effect terms.

This module models resource envelopes, lifecycle cycles, consensus and
evolution gates. It does not implement fictional physics or biological
experiments; catalogue terms are not executable instructions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
from collections import Counter
from collections.abc import Iterable, Mapping


class DomainStatus(str, Enum):
    INCOMPLETE = "incomplete"
    NOMINAL = "nominal"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class MetricLimit:
    unit: str
    minimum: float
    maximum: float
    warning_margin: float = 0.0

    def validate(self) -> None:
        values = (self.minimum, self.maximum, self.warning_margin)
        if not self.unit.strip() or not all(math.isfinite(v) for v in values):
            raise ValueError("unit and finite numeric limits are required")
        if self.minimum > self.maximum or self.warning_margin < 0:
            raise ValueError("invalid metric interval or warning margin")


@dataclass(frozen=True)
class MetricObservation:
    name: str
    value: float
    unit: str
    source: str
    sample_count: int = 1
    calibrated: bool = True


@dataclass(frozen=True)
class MetricAssessment:
    name: str
    status: DomainStatus
    value: float | None
    unit: str
    reason: str


def assess_metric(
    observation: MetricObservation,
    limits: MetricLimit,
    *,
    minimum_samples: int = 1,
) -> MetricAssessment:
    """Classify a measured value without changing hardware or source data."""
    limits.validate()
    if minimum_samples < 1:
        raise ValueError("minimum_samples must be positive")
    if observation.unit != limits.unit:
        raise ValueError("observation and limit units must match")
    if not isinstance(observation.name, str) or not observation.name.strip() or not isinstance(observation.source, str) or not observation.source.strip():
        raise ValueError("observation name and source are required")
    if not math.isfinite(observation.value):
        raise ValueError("observation value must be finite")
    if observation.sample_count < minimum_samples or not observation.calibrated:
        return MetricAssessment(
            observation.name, DomainStatus.INCOMPLETE, None, limits.unit,
            "insufficient samples or calibration not confirmed",
        )
    value = observation.value
    if value < limits.minimum or value > limits.maximum:
        return MetricAssessment(
            observation.name, DomainStatus.CRITICAL, value, limits.unit,
            "value is outside the configured operating envelope",
        )
    if (
        value - limits.minimum <= limits.warning_margin
        or limits.maximum - value <= limits.warning_margin
    ):
        return MetricAssessment(
            observation.name, DomainStatus.WARNING, value, limits.unit,
            "value is inside the warning margin",
        )
    return MetricAssessment(
        observation.name, DomainStatus.NOMINAL, value, limits.unit,
        "value is inside the configured operating envelope",
    )


class CycleState(str, Enum):
    DORMANT = "dormant"
    STAGED = "staged"
    VERIFIED = "verified"
    ACTIVE = "active"
    DEGRADED = "degraded"
    ROLLING_BACK = "rolling_back"
    RETIRED = "retired"


_CYCLE_TRANSITIONS: Mapping[CycleState, frozenset[CycleState]] = {
    CycleState.DORMANT: frozenset({CycleState.STAGED}),
    CycleState.STAGED: frozenset({CycleState.VERIFIED, CycleState.DORMANT}),
    CycleState.VERIFIED: frozenset({CycleState.ACTIVE, CycleState.ROLLING_BACK}),
    CycleState.ACTIVE: frozenset(
        {CycleState.DEGRADED, CycleState.ROLLING_BACK, CycleState.RETIRED}
    ),
    CycleState.DEGRADED: frozenset(
        {CycleState.ACTIVE, CycleState.ROLLING_BACK, CycleState.RETIRED}
    ),
    CycleState.ROLLING_BACK: frozenset({CycleState.DORMANT, CycleState.VERIFIED}),
    CycleState.RETIRED: frozenset(),
}


def advance_cycle(current: CycleState, target: CycleState) -> CycleState:
    """Apply one explicitly allowed lifecycle transition."""
    if target not in _CYCLE_TRANSITIONS[current]:
        raise ValueError(f"transition {current.value} -> {target.value} is not allowed")
    return target


@dataclass(frozen=True)
class ConsensusResult:
    accepted: bool
    proposal_id: str | None
    agreeing_nodes: int
    eligible_nodes: int
    reason: str


def decide_consensus(
    votes: Iterable[tuple[str, str]],
    *,
    quorum: int,
) -> ConsensusResult:
    """Count one vote per node; return no decision when quorum is not reached."""
    materialized = list(votes)
    if quorum < 1 or quorum > len(materialized):
        raise ValueError("quorum must be between one and the vote count")
    node_ids = [node for node, _ in materialized]
    proposal_ids = [proposal for _, proposal in materialized]
    if any(not isinstance(value, str) or not value.strip() for value in node_ids + proposal_ids):
        raise ValueError("node and proposal identifiers must be non-empty")
    if len(set(node_ids)) != len(node_ids):
        raise ValueError("duplicate node votes are not permitted")
    counts = Counter(proposal_ids)
    proposal, count = counts.most_common(1)[0]
    if count < quorum:
        return ConsensusResult(
            False, None, count, len(materialized),
            "no proposal reached the configured quorum",
        )
    return ConsensusResult(
        True, proposal, count, len(materialized),
        "proposal reached the configured quorum",
    )


@dataclass(frozen=True)
class EvolutionGate:
    accepted: bool
    missing_evidence: tuple[str, ...]
    rollback_ready: bool
    reason: str


def evaluate_evolution_gate(
    required_evidence: Iterable[str],
    available_evidence: Iterable[str],
    *,
    rollback_ready: bool,
) -> EvolutionGate:
    """Require complete evidence and a rollback path before promoting a change."""
    required = set(required_evidence)
    available = set(available_evidence)
    if any(not isinstance(item, str) or not item.strip() for item in required | available):
        raise ValueError("evidence identifiers must be non-empty")
    missing = tuple(sorted(required - available))
    accepted = not missing and rollback_ready
    if missing:
        reason = "required evidence is missing"
    elif not rollback_ready:
        reason = "rollback path is not ready"
    else:
        reason = "evolution proposal passed the promotion gate"
    return EvolutionGate(accepted, missing, rollback_ready, reason)
