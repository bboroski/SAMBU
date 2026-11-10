"""Versioned, evidence-aware metadata for creative text analysis.

This module stores descriptive metadata only. It deliberately does not retain
source text, infer safety labels, train embeddings, or promise that a record is
suitable for generation. Callers must classify and review source material
before constructing a CreativeMetadata record.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re
from typing import Mapping, Sequence


ONTOLOGY_VERSION = "2026.12"
SUPPORTED_ONTOLOGY_VERSIONS = frozenset({"2026.11", "2026.12"})
JSONLD_CONTEXT = "https://schema.org/"

SAFETY_FLAGS = frozenset(
    {
        "CLEAN",
        "CLEAN_SATIRE",
        "SANITIZED_ARGOT_ONLY",
        "SANITIZED_INTIMACY",
        "NEEDS_REVIEW",
        "EXCLUDED_FROM_GENERATION",
    }
)
_GENERATION_ELIGIBLE_FLAGS = frozenset({"CLEAN", "CLEAN_SATIRE"})
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_REVIEW_TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


class CreativeMetadataError(ValueError):
    """Raised when creative metadata is malformed or outside policy bounds."""


@dataclass(frozen=True, slots=True)
class CreativeCluster:
    """A stable, descriptive node in the creative-data ontology."""

    cluster_id: str
    name: str
    theme: str
    description: str
    applications: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.cluster_id,
            "name": self.name,
            "theme": self.theme,
            "description": self.description,
            "applications": list(self.applications),
        }


CREATIVE_CLUSTERS: tuple[CreativeCluster, ...] = (
    CreativeCluster(
        "T-001",
        "Celebration and ritual",
        "cultural_celebration",
        "Public events, shared activities, recurring calendars and community contexts.",
        ("event description", "context tagging", "schedule annotation"),
    ),
    CreativeCluster(
        "T-002",
        "Identity and transformation",
        "identity_transformation",
        "Profile changes, role transitions, representation and lifecycle changes.",
        ("profile analysis", "entity tracking", "state annotation"),
    ),
    CreativeCluster(
        "T-003",
        "Geopolitical awareness",
        "geopolitical_awareness",
        "Regions, jurisdictions, institutional structures and geographic context.",
        ("entity recognition", "regional comparison", "context grounding"),
    ),
    CreativeCluster(
        "T-004",
        "Emotional duality",
        "emotional_duality",
        "Contrasting states, competing conditions, uncertainty and change over time.",
        ("state comparison", "dialogue analysis", "change annotation"),
    ),
    CreativeCluster(
        "T-005",
        "Spiritual syncretism",
        "spiritual_syncretism",
        "Symbol systems, inherited conventions, heritage references and cultural classifications.",
        ("catalog annotation", "symbolic indexing", "reference analysis"),
    ),
    CreativeCluster(
        "T-006",
        "Technological metaphor",
        "technological_metaphor",
        "Technical systems, software/hardware mappings and digital/physical analogies.",
        ("technical writing", "system documentation", "interface analysis"),
    ),
    CreativeCluster(
        "T-007",
        "Conflict and resilience",
        "conflict_resilience",
        "Incidents, constraints, fault handling, continuity and recovery sequences.",
        ("incident reporting", "operational documentation", "recovery analysis"),
    ),
    CreativeCluster(
        "T-008",
        "Linguistic hybridity",
        "linguistic_hybridity",
        "Multiple languages, locale switching, terminology variants and mixed registers.",
        ("translation assessment", "interface localization", "terminology analysis"),
    ),
    CreativeCluster(
        "T-009",
        "Surreal juxtaposition and wordplay",
        "surreal_juxtaposition",
        "Unexpected associations, ambiguous labels, category mismatches and controlled wordplay.",
        ("label review", "ambiguity analysis", "controlled wordplay annotation"),
    ),
)
CLUSTER_BY_ID = {cluster.cluster_id: cluster for cluster in CREATIVE_CLUSTERS}


def _required_text(value: object, field_name: str, *, limit: int = 160) -> str:
    if not isinstance(value, str):
        raise CreativeMetadataError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise CreativeMetadataError(f"{field_name} must not be empty")
    if len(normalized) > limit:
        raise CreativeMetadataError(f"{field_name} exceeds {limit} characters")
    return normalized


def _string_tuple(
    value: object,
    field_name: str,
    *,
    maximum: int,
    item_limit: int = 80,
) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise CreativeMetadataError(f"{field_name} must be a list of strings")
    if len(value) > maximum:
        raise CreativeMetadataError(f"{field_name} accepts at most {maximum} items")
    items: list[str] = []
    seen: set[str] = set()
    for item in value:
        normalized = _required_text(item, field_name, limit=item_limit)
        key = normalized.casefold()
        if key not in seen:
            items.append(normalized)
            seen.add(key)
    return tuple(items)


def _review_timestamp(value: object) -> str:
    """Validate an ISO-8601 timestamp with an explicit timezone offset."""
    if not isinstance(value, str) or not _REVIEW_TIME_RE.fullmatch(value):
        raise CreativeMetadataError(
            "reviewed_at must be an ISO-8601 timestamp with a timezone offset"
        )
    try:
        parsed = datetime.fromisoformat(
            value[:-1] + "+00:00" if value.endswith("Z") else value
        )
    except ValueError as exc:
        raise CreativeMetadataError("reviewed_at is not a valid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CreativeMetadataError("reviewed_at must include a timezone offset")
    return value


@dataclass(frozen=True, slots=True)
class CreativeMetadata:
    """A reviewed metadata record; raw creative source is intentionally absent."""

    cluster_id: str
    theme: str
    tone: str
    key_symbols: tuple[str, ...] = ()
    language: tuple[str, ...] = ()
    linguistic_register: str | None = None
    stylistic_devices: tuple[str, ...] = ()
    safety_flag: str = "NEEDS_REVIEW"
    source_ref: str | None = None
    content_sha256: str | None = None
    ontology_version: str = ONTOLOGY_VERSION
    review_ref: str | None = None
    reviewed_at: str | None = None

    def __post_init__(self) -> None:
        cluster_id = _required_text(self.cluster_id, "cluster_id", limit=16)
        if cluster_id not in CLUSTER_BY_ID:
            raise CreativeMetadataError(f"unknown cluster_id: {cluster_id!r}")
        object.__setattr__(self, "cluster_id", cluster_id)
        object.__setattr__(self, "theme", _required_text(self.theme, "theme", limit=96))
        object.__setattr__(self, "tone", _required_text(self.tone, "tone", limit=96))
        if not isinstance(self.safety_flag, str) or self.safety_flag not in SAFETY_FLAGS:
            raise CreativeMetadataError(
                f"safety_flag must be one of: {', '.join(sorted(SAFETY_FLAGS))}"
            )
        if self.linguistic_register is not None:
            object.__setattr__(
                self, "linguistic_register",
                _required_text(self.linguistic_register, "linguistic_register", limit=96),
            )
        if self.source_ref is not None:
            object.__setattr__(
                self, "source_ref", _required_text(self.source_ref, "source_ref", limit=128)
            )
        if self.content_sha256 is not None:
            if not isinstance(self.content_sha256, str) or not _SHA256_RE.fullmatch(self.content_sha256):
                raise CreativeMetadataError(
                    "content_sha256 must be a 64-character SHA-256 hex digest"
                )
            object.__setattr__(self, "content_sha256", self.content_sha256.lower())
        if self.ontology_version not in SUPPORTED_ONTOLOGY_VERSIONS:
            supported = ", ".join(sorted(SUPPORTED_ONTOLOGY_VERSIONS))
            raise CreativeMetadataError(
                f"unsupported ontology_version {self.ontology_version!r}; "
                f"supported versions: {supported!r}"
            )
        if cluster_id == "T-009" and self.ontology_version != ONTOLOGY_VERSION:
            raise CreativeMetadataError("cluster T-009 requires ontology_version 2026.12")
        if self.review_ref is not None:
            object.__setattr__(
                self, "review_ref", _required_text(self.review_ref, "review_ref", limit=128)
            )
        if self.reviewed_at is not None:
            object.__setattr__(self, "reviewed_at", _review_timestamp(self.reviewed_at))
        if (self.review_ref is None) != (self.reviewed_at is None):
            raise CreativeMetadataError("review_ref and reviewed_at must be provided together")
        object.__setattr__(
            self, "key_symbols",
            _string_tuple(self.key_symbols, "key_symbols", maximum=16),
        )
        object.__setattr__(
            self, "language",
            tuple(item.lower() for item in _string_tuple(
                self.language, "language", maximum=8, item_limit=16
            )),
        )
        object.__setattr__(
            self, "stylistic_devices",
            _string_tuple(self.stylistic_devices, "stylistic_devices", maximum=16),
        )

    @property
    def generation_eligible(self) -> bool:
        """True only for explicitly reviewed, non-sanitization-only labels."""
        return (
            self.safety_flag in _GENERATION_ELIGIBLE_FLAGS
            and self.review_ref is not None
            and self.reviewed_at is not None
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "cluster_id": self.cluster_id,
            "theme": self.theme,
            "tone": self.tone,
            "key_symbols": list(self.key_symbols),
            "language": list(self.language),
            "linguistic_register": self.linguistic_register,
            "stylistic_devices": list(self.stylistic_devices),
            "safety_flag": self.safety_flag,
            "source_ref": self.source_ref,
            "content_sha256": self.content_sha256,
            "ontology_version": self.ontology_version,
            "review_ref": self.review_ref,
            "reviewed_at": self.reviewed_at,
        }

    def to_jsonld(self) -> dict[str, object]:
        """Return a JSON-LD description containing metadata, never source text."""
        cluster = CLUSTER_BY_ID[self.cluster_id]
        result: dict[str, object] = {
            "@context": JSONLD_CONTEXT,
            "@type": "CreativeWork",
            "name": f"Creative cluster {self.cluster_id}",
            "description": cluster.description,
            "keywords": list(self.key_symbols) + [self.theme, self.tone],
            "inLanguage": list(self.language),
            "genre": cluster.name,
            "version": self.ontology_version,
            "creativeCluster": self.cluster_id,
            "tone": self.tone,
            "safetyFlag": self.safety_flag,
            "generationEligible": self.generation_eligible,
        }
        if self.linguistic_register is not None:
            result["linguisticRegister"] = self.linguistic_register
        if self.stylistic_devices:
            result["stylisticDevices"] = list(self.stylistic_devices)
        if self.source_ref is not None:
            result["sourceReference"] = self.source_ref
        if self.content_sha256 is not None:
            result["contentHash"] = self.content_sha256
        if self.review_ref is not None and self.reviewed_at is not None:
            result["reviewReference"] = self.review_ref
            result["dateReviewed"] = self.reviewed_at
        return result

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "CreativeMetadata":
        if not isinstance(payload, Mapping):
            raise CreativeMetadataError("metadata record must be a JSON object")
        allowed = {
            "cluster_id", "theme", "tone", "key_symbols", "language",
            "linguistic_register", "stylistic_devices", "safety_flag",
            "source_ref", "content_sha256", "ontology_version",
            "review_ref", "reviewed_at",
        }
        unknown = set(payload) - allowed
        if unknown:
            raise CreativeMetadataError(
                "unknown metadata field(s): " + ", ".join(sorted(str(x) for x in unknown))
            )

        cluster_id = _required_text(payload.get("cluster_id"), "cluster_id", limit=16)
        theme = _required_text(payload.get("theme"), "theme", limit=96)
        tone = _required_text(payload.get("tone"), "tone", limit=96)
        safety_flag = payload.get("safety_flag", "NEEDS_REVIEW")
        if not isinstance(safety_flag, str):
            raise CreativeMetadataError("safety_flag must be a string")

        linguistic_register = payload.get("linguistic_register")
        if linguistic_register is not None and not isinstance(linguistic_register, str):
            raise CreativeMetadataError("linguistic_register must be a string or null")
        source_ref = payload.get("source_ref")
        if source_ref is not None and not isinstance(source_ref, str):
            raise CreativeMetadataError("source_ref must be a string or null")
        content_sha256 = payload.get("content_sha256")
        if content_sha256 is not None and not isinstance(content_sha256, str):
            raise CreativeMetadataError("content_sha256 must be a string or null")
        ontology_version = payload.get("ontology_version", ONTOLOGY_VERSION)
        if not isinstance(ontology_version, str):
            raise CreativeMetadataError("ontology_version must be a string")
        review_ref = payload.get("review_ref")
        if review_ref is not None and not isinstance(review_ref, str):
            raise CreativeMetadataError("review_ref must be a string or null")
        reviewed_at = payload.get("reviewed_at")
        if reviewed_at is not None and not isinstance(reviewed_at, str):
            raise CreativeMetadataError("reviewed_at must be a string or null")

        return cls(
            cluster_id=cluster_id,
            theme=theme,
            tone=tone,
            key_symbols=_string_tuple(payload.get("key_symbols"), "key_symbols", maximum=16),
            language=_string_tuple(
                payload.get("language"), "language", maximum=8, item_limit=16
            ),
            linguistic_register=linguistic_register,
            stylistic_devices=_string_tuple(
                payload.get("stylistic_devices"), "stylistic_devices", maximum=16
            ),
            safety_flag=safety_flag,
            source_ref=source_ref,
            content_sha256=content_sha256,
            ontology_version=ontology_version,
            review_ref=review_ref,
            reviewed_at=reviewed_at,
        )


def validate_metadata_document(payload: object) -> tuple[CreativeMetadata, ...]:
    """Validate one record or a bounded list of records."""
    if isinstance(payload, Mapping):
        return (CreativeMetadata.from_mapping(payload),)
    if isinstance(payload, list):
        if not payload:
            raise CreativeMetadataError("metadata document must contain at least one record")
        if len(payload) > 1000:
            raise CreativeMetadataError("metadata document accepts at most 1000 records")
        return tuple(CreativeMetadata.from_mapping(item) for item in payload)
    raise CreativeMetadataError("metadata document must be a JSON object or array")
