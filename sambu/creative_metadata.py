"""Versioned, evidence-aware metadata for creative text analysis.

This module stores descriptive metadata only. It deliberately does not retain
source text, infer safety labels, train embeddings, or promise that a record is
suitable for generation. Callers must classify and review source material
before constructing a CreativeMetadata record.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Sequence


ONTOLOGY_VERSION = "2026.11"
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
        "Festive gatherings, communal joy, market aesthetics and seasonal cycles.",
        ("event generation", "cultural context tagging", "mood analysis"),
    ),
    CreativeCluster(
        "T-002",
        "Identity and transformation",
        "identity_transformation",
        "Masks and faces, self-reinvention and artistic persona construction.",
        ("character development", "style analysis", "persona metadata"),
    ),
    CreativeCluster(
        "T-003",
        "Geopolitical awareness",
        "geopolitical_awareness",
        "Regional dynamics, institutions, borders and technological sovereignty.",
        ("entity recognition", "neutral context grounding", "summarization"),
    ),
    CreativeCluster(
        "T-004",
        "Emotional duality",
        "emotional_duality",
        "Warmth and distance, intimacy and alienation, memory and present reality.",
        ("sentiment analysis", "dialogue analysis", "emotional arc annotation"),
    ),
    CreativeCluster(
        "T-005",
        "Spiritual syncretism",
        "spiritual_syncretism",
        "Religious imagery, folk motifs, ritual language and sacred/profane tension.",
        ("cultural literacy", "symbolic annotation", "metaphor analysis"),
    ),
    CreativeCluster(
        "T-006",
        "Technological metaphor",
        "technological_metaphor",
        "Hardware-as-body imagery, code-as-ritual and digital/analogue fusion.",
        ("technical writing", "creative coding prompts", "UX language analysis"),
    ),
    CreativeCluster(
        "T-007",
        "Conflict and resilience",
        "conflict_resilience",
        "Institutional critique, disruption, endurance and recovery narratives.",
        ("crisis communication", "educational content", "resilience narratives"),
    ),
    CreativeCluster(
        "T-008",
        "Linguistic hybridity",
        "linguistic_hybridity",
        "Code-switching, multilingual rhyme, dialectal texture and mixed registers.",
        ("translation assessment", "multilingual annotation", "register analysis"),
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
        if self.ontology_version != ONTOLOGY_VERSION:
            raise CreativeMetadataError(
                f"unsupported ontology_version {self.ontology_version!r}; "
                f"expected {ONTOLOGY_VERSION!r}"
            )
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
        return self.safety_flag in _GENERATION_ELIGIBLE_FLAGS

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
        return result

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> "CreativeMetadata":
        if not isinstance(payload, Mapping):
            raise CreativeMetadataError("metadata record must be a JSON object")
        allowed = {
            "cluster_id", "theme", "tone", "key_symbols", "language",
            "linguistic_register", "stylistic_devices", "safety_flag",
            "source_ref", "content_sha256", "ontology_version",
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
