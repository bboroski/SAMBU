"""Explicit, local preference memory for creative-work refinement.

This is a bounded preference ledger, not a trained model. It stores only
aggregate choices from an explicit user action; it never stores source text,
prompts, examples, or private drafts.
"""
from __future__ import annotations

import json
from typing import Mapping


CREATIVE_PREFERENCE_FEATURES = (
    "rhythm",
    "naturalness",
    "internal_rhyme",
    "multisyllabic_rhyme",
    "semantic_clarity",
    "refrain_development",
    "imagery",
    "language_mixing",
    "register_control",
    "clean_language",
)
_SCHEMA_VERSION = 1
_MAX_EVENTS = 10_000
_MAX_JSON_BYTES = 64_000
_CHOICES = frozenset({"prefer", "avoid"})


class CreativeLearningError(ValueError):
    """Raised for disabled, unknown, malformed, or over-budget feedback."""


class CreativeLearningProfile:
    """Aggregate explicitly approved preferences without retaining creative text.

    Collection is disabled by default. Instantiate with enabled=True only after
    the caller has obtained an explicit user opt-in. The profile remains in
    memory until the caller explicitly exports it with to_json().
    """

    def __init__(self, *, enabled: bool = False, max_events: int = _MAX_EVENTS):
        if type(enabled) is not bool:
            raise CreativeLearningError("enabled must be a boolean")
        if type(max_events) is not int or not 1 <= max_events <= _MAX_EVENTS:
            raise CreativeLearningError(f"max_events must be an integer from 1 to {_MAX_EVENTS}")
        self._enabled = enabled
        self._max_events = max_events
        self._event_count = 0
        self._counts = {
            feature: {"prefer": 0, "avoid": 0}
            for feature in CREATIVE_PREFERENCE_FEATURES
        }

    @property
    def enabled(self) -> bool:
        """Whether this instance accepts new explicit feedback."""
        return self._enabled

    @property
    def event_count(self) -> int:
        return self._event_count

    @property
    def remaining_events(self) -> int:
        return self._max_events - self._event_count

    def _validate_feature(self, feature: object) -> str:
        if not isinstance(feature, str) or feature not in self._counts:
            raise CreativeLearningError(
                "feature must be one of the registered creative preference dimensions"
            )
        return feature

    def preference(self, feature: str) -> dict[str, object]:
        """Return aggregate counts and a normalized preference signal in [-1, 1]."""
        name = self._validate_feature(feature)
        counts = self._counts[name]
        preferred = counts["prefer"]
        avoided = counts["avoid"]
        total = preferred + avoided
        score = (preferred - avoided) / total if total else 0.0
        return {
            "feature": name,
            "prefer": preferred,
            "avoid": avoided,
            "decisions": total,
            "preference_score": score,
        }

    def record_feedback(self, feature: str, choice: str) -> dict[str, object]:
        """Record one explicit preference choice; no text or sample is accepted."""
        if not self._enabled:
            raise CreativeLearningError("creative learning is disabled; explicit opt-in is required")
        name = self._validate_feature(feature)
        if not isinstance(choice, str) or choice not in _CHOICES:
            raise CreativeLearningError("choice must be 'prefer' or 'avoid'")
        if self._event_count >= self._max_events:
            raise CreativeLearningError("creative feedback budget is exhausted")
        self._counts[name][choice] += 1
        self._event_count += 1
        return self.preference(name)

    def ranked_preferences(self) -> list[dict[str, object]]:
        """Return explicit preference signals from strongest to weakest.

        Ties use the stable feature registry order. A score is a preference
        summary, not a confidence estimate or a prediction of writing quality.
        """
        rows = [self.preference(feature) for feature in CREATIVE_PREFERENCE_FEATURES]
        return sorted(
            rows,
            key=lambda row: (
                -abs(float(row["preference_score"])),
                CREATIVE_PREFERENCE_FEATURES.index(str(row["feature"])),
            ),
        )

    def to_dict(self) -> dict[str, object]:
        """Create an exportable versioned snapshot containing counts only."""
        return {
            "schema_version": _SCHEMA_VERSION,
            "max_events": self._max_events,
            "event_count": self._event_count,
            "preferences": {
                feature: dict(self._counts[feature])
                for feature in CREATIVE_PREFERENCE_FEATURES
            },
        }

    def to_json(self) -> str:
        """Serialize counts for an explicit caller-controlled export."""
        raw = json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        if len(raw.encode("utf-8")) > _MAX_JSON_BYTES:
            raise CreativeLearningError("creative preference export exceeds the size limit")
        return raw

    @classmethod
    def from_json(cls, raw: str, *, enabled: bool = False) -> "CreativeLearningProfile":
        """Load a bounded snapshot; loading never re-enables feedback collection."""
        if not isinstance(raw, str) or len(raw.encode("utf-8")) > _MAX_JSON_BYTES:
            raise CreativeLearningError("creative preference data must be text within the size limit")
        try:
            payload = json.loads(raw)
        except (TypeError, ValueError) as exc:
            raise CreativeLearningError("creative preference data is not valid JSON") from exc
        required = {"schema_version", "max_events", "event_count", "preferences"}
        if not isinstance(payload, dict) or set(payload) != required:
            raise CreativeLearningError("creative preference document has an unsupported shape")
        if type(payload["schema_version"]) is not int or payload["schema_version"] != _SCHEMA_VERSION:
            raise CreativeLearningError("unsupported creative preference schema version")
        max_events = payload["max_events"]
        event_count = payload["event_count"]
        if type(max_events) is not int or not 1 <= max_events <= _MAX_EVENTS:
            raise CreativeLearningError("max_events is outside the supported range")
        if type(event_count) is not int or not 0 <= event_count <= max_events:
            raise CreativeLearningError("event_count is outside the declared budget")
        preferences = payload["preferences"]
        if not isinstance(preferences, Mapping) or set(preferences) != set(CREATIVE_PREFERENCE_FEATURES):
            raise CreativeLearningError("preference dimensions do not match the registered schema")

        profile = cls(enabled=enabled, max_events=max_events)
        actual_events = 0
        for feature in CREATIVE_PREFERENCE_FEATURES:
            counts = preferences[feature]
            if not isinstance(counts, Mapping) or set(counts) != _CHOICES:
                raise CreativeLearningError(f"malformed preference counts for {feature}")
            preferred = counts["prefer"]
            avoided = counts["avoid"]
            if (
                type(preferred) is not int or preferred < 0
                or type(avoided) is not int or avoided < 0
            ):
                raise CreativeLearningError(f"preference counts for {feature} must be non-negative integers")
            profile._counts[feature] = {"prefer": preferred, "avoid": avoided}
            actual_events += preferred + avoided
        if actual_events != event_count:
            raise CreativeLearningError("event_count does not match the aggregate preference counts")
        profile._event_count = event_count
        return profile
