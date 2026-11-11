"""Consent-first, local-only journey measurement for SAMBU workflows."""
from __future__ import annotations
from collections import Counter, deque
from dataclasses import dataclass
from statistics import median
import re
from typing import Literal

Outcome = Literal["completed", "failed", "abandoned"]
_CODE = re.compile(r"^[a-z][a-z0-9_.-]{0,47}$")
_MAX_DURATION_MS = 86_400_000

@dataclass(frozen=True)
class JourneyEvent:
    stage: str
    outcome: Outcome
    duration_ms: int
    friction_code: str | None = None

@dataclass(frozen=True)
class JourneySummary:
    sample_count: int
    completed: int
    failed: int
    abandoned: int
    completion_rate: float
    failure_rate: float
    median_duration_ms: float
    top_friction: tuple[tuple[str, int], ...]
    sample_is_actionable: bool

class ExperienceJournal:
    """Bounded in-memory journal; recording is off until explicit opt-in."""
    def __init__(self, *, opt_in: bool = False, capacity: int = 256, minimum_sample: int = 5) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or not 1 <= capacity <= 10_000:
            raise ValueError("capacity must be an integer in 1..10000")
        if isinstance(minimum_sample, bool) or not isinstance(minimum_sample, int) or minimum_sample < 1:
            raise ValueError("minimum_sample must be a positive integer")
        self.capacity, self.minimum_sample = capacity, minimum_sample
        self._events: deque[JourneyEvent] = deque(maxlen=capacity)
        self._opt_in = bool(opt_in)

    @property
    def enabled(self) -> bool:
        return self._opt_in

    def set_consent(self, enabled: bool) -> None:
        self._opt_in = bool(enabled)
        if not self._opt_in:
            self._events.clear()

    def record(self, stage: str, outcome: Outcome, *, duration_ms: int = 0, friction_code: str | None = None) -> bool:
        if not self._opt_in:
            return False
        if not isinstance(stage, str) or not _CODE.fullmatch(stage):
            raise ValueError("stage must be a short lowercase machine code")
        if outcome not in ("completed", "failed", "abandoned"):
            raise ValueError("unsupported journey outcome")
        if isinstance(duration_ms, bool) or not isinstance(duration_ms, int) or not 0 <= duration_ms <= _MAX_DURATION_MS:
            raise ValueError("duration_ms must be an integer in 0..86400000")
        if friction_code is not None and (not isinstance(friction_code, str) or not _CODE.fullmatch(friction_code)):
            raise ValueError("friction_code must be a short lowercase machine code")
        self._events.append(JourneyEvent(stage, outcome, duration_ms, friction_code))
        return True

    def clear(self) -> None:
        self._events.clear()

    def summary(self, *, friction_limit: int = 3) -> JourneySummary:
        if isinstance(friction_limit, bool) or not isinstance(friction_limit, int) or friction_limit < 0:
            raise ValueError("friction_limit must be a non-negative integer")
        events = tuple(self._events)
        total = len(events)
        counts = Counter(event.outcome for event in events)
        friction = Counter(event.friction_code for event in events if event.friction_code is not None and event.outcome != "completed")
        top = tuple(sorted(friction.items(), key=lambda item: (-item[1], item[0]))[:friction_limit])
        return JourneySummary(
            sample_count=total, completed=counts["completed"], failed=counts["failed"], abandoned=counts["abandoned"],
            completion_rate=(counts["completed"] / total * 100.0) if total else 0.0,
            failure_rate=(counts["failed"] / total * 100.0) if total else 0.0,
            median_duration_ms=float(median(event.duration_ms for event in events)) if events else 0.0,
            top_friction=top, sample_is_actionable=total >= self.minimum_sample)

    def next_actions(self, *, limit: int = 3) -> tuple[str, ...]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 0 <= limit <= 10:
            raise ValueError("limit must be an integer in 0..10")
        report = self.summary(friction_limit=limit)
        if not report.sample_is_actionable:
            return ()
        return tuple(code for code, _count in report.top_friction)
