"""Reproducible observation ledger for scientific and historical inquiry.

This module records what was observed separately from when an event may have
occurred. It never turns co-occurrence into causation or confidence into truth.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import isfinite
from statistics import median
from typing import Iterable, Sequence


@dataclass(frozen=True)
class SambuSource:
    source_id: str
    kind: str
    locator: str = ""
    retrieved_at: str | None = None


@dataclass(frozen=True)
class SambuObservation:
    event_id: str
    observed_at: str
    summary: str
    category: str
    occurred_at: str | None = None
    confidence: float = 0.0
    sources: tuple[SambuSource, ...] = field(default_factory=tuple)
    related_ids: tuple[str, ...] = field(default_factory=tuple)
    causal_hypotheses: tuple[str, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)
    measurement: float | None = None
    unit: str | None = None


def _instant(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be a non-empty ISO-8601 string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include an explicit UTC offset")
    return parsed


def validate_observations(items: Sequence[SambuObservation]) -> list[str]:
    errors: list[str] = []
    by_id: dict[str, SambuObservation] = {}
    for index, item in enumerate(items):
        if not isinstance(item, SambuObservation):
            errors.append(f"items[{index}] is not a SambuObservation")
            continue
        if not item.event_id.strip():
            errors.append(f"items[{index}].event_id is required")
        elif item.event_id in by_id:
            errors.append(f"duplicate event_id: {item.event_id}")
        else:
            by_id[item.event_id] = item
        if not item.summary.strip() or not item.category.strip():
            errors.append(f"{item.event_id}: summary and category are required")
        try:
            observed = _instant(item.observed_at)
            if item.occurred_at is not None:
                _instant(item.occurred_at)
        except (TypeError, ValueError) as exc:
            errors.append(f"{item.event_id}: {exc}")
            observed = None
        if not isfinite(item.confidence) or not 0.0 <= item.confidence <= 1.0:
            errors.append(f"{item.event_id}: confidence must be finite and within 0..1")
        seen_sources: set[str] = set()
        for source in item.sources:
            if not source.source_id.strip() or not source.kind.strip():
                errors.append(f"{item.event_id}: every source needs source_id and kind")
            if source.source_id in seen_sources:
                errors.append(f"{item.event_id}: duplicate source_id {source.source_id}")
            seen_sources.add(source.source_id)
            if source.retrieved_at:
                try:
                    _instant(source.retrieved_at)
                except ValueError as exc:
                    errors.append(f"{item.event_id}: invalid source retrieval time: {exc}")
        if item.measurement is not None and (
            not isfinite(item.measurement) or not item.unit or not item.unit.strip()
        ):
            errors.append(f"{item.event_id}: measurements need a finite value and a unit")
    for item in by_id.values():
        for ref in (*item.related_ids, *item.causal_hypotheses):
            if ref == item.event_id:
                errors.append(f"{item.event_id}: self-reference is not allowed")
            elif ref not in by_id:
                errors.append(f"{item.event_id}: unresolved event reference {ref}")
    errors.extend(_hypothesis_cycle_errors(by_id))
    return errors


def _hypothesis_cycle_errors(by_id: dict[str, SambuObservation]) -> list[str]:
    state: dict[str, int] = {}
    errors: list[str] = []

    def visit(event_id: str, trail: list[str]) -> None:
        marker = state.get(event_id, 0)
        if marker == 2:
            return
        if marker == 1:
            errors.append("causal-hypothesis cycle: " + " -> ".join(trail + [event_id]))
            return
        state[event_id] = 1
        for parent in by_id[event_id].causal_hypotheses:
            if parent in by_id:
                visit(parent, trail + [event_id])
        state[event_id] = 2

    for event_id in by_id:
        if state.get(event_id, 0) == 0:
            visit(event_id, [])
    return errors


def observation_timeline(items: Sequence[SambuObservation]) -> list[SambuObservation]:
    errors = validate_observations(items)
    if errors:
        raise ValueError("; ".join(errors))
    return sorted(
        items,
        key=lambda item: (_instant(item.occurred_at or item.observed_at), item.event_id),
    )


def evidence_completeness(item: SambuObservation) -> dict[str, int | str]:
    """Return coverage metadata, not a probability that the event is true."""
    source_count = len({source.source_id for source in item.sources})
    source_kinds = len({source.kind for source in item.sources})
    has_time = int(bool(item.observed_at) and (
        item.occurred_at is None or _safe_time(item.occurred_at)
    ))
    score = min(source_count, 3) * 15 + min(source_kinds, 3) * 10
    score += 20 if has_time else 0
    score += round(item.confidence * 15)
    score = min(score, 100)
    label = "well-documented" if score >= 70 else "partial" if score >= 35 else "thin"
    return {"coverage_score": score, "source_count": source_count,
            "source_kinds": source_kinds, "label": label}


def _safe_time(value: str) -> bool:
    try:
        _instant(value)
        return True
    except (TypeError, ValueError):
        return False


def robust_outlier_indices(values: Sequence[float | int], threshold: float = 3.5) -> list[int]:
    """Find exploratory outliers using median/MAD; requires at least five values."""
    if not isfinite(threshold) or threshold <= 0:
        raise ValueError("threshold must be a positive finite number")
    numeric = [float(value) for value in values]
    if any(not isfinite(value) for value in numeric):
        raise ValueError("all values must be finite")
    if len(numeric) < 5:
        return []
    center = median(numeric)
    deviations = [abs(value - center) for value in numeric]
    mad = median(deviations)
    if mad == 0:
        nonzero_deviations = [deviation for deviation in deviations if deviation > 0]
        if not nonzero_deviations:
            return []
        mad = median(nonzero_deviations)
    scale = 1.4826 * mad
    return [index for index, value in enumerate(numeric)
            if abs(value - center) / scale >= threshold]


def co_occurring_pairs(
    items: Sequence[SambuObservation], window_seconds: float
) -> list[tuple[str, str, tuple[str, ...]]]:
    """Return temporal co-occurrences only; this is not a causal inference."""
    if not isfinite(window_seconds) or window_seconds < 0:
        raise ValueError("window_seconds must be finite and non-negative")
    ordered = observation_timeline(items)
    pairs: list[tuple[str, str, tuple[str, ...]]] = []
    for index, left in enumerate(ordered):
        if left.occurred_at is None:
            continue
        left_time = _instant(left.occurred_at)
        for right in ordered[index + 1:]:
            if right.occurred_at is None:
                continue
            delta = (_instant(right.occurred_at) - left_time).total_seconds()
            if delta > window_seconds:
                break
            shared = tuple(sorted(set(left.tags).intersection(right.tags)))
            if shared:
                pairs.append((left.event_id, right.event_id, shared))
    return pairs
