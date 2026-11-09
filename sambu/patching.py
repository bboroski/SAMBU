"""Conflict-aware, reversible text patching for editor and refactoring tools."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib

class PatchConflict(ValueError):
    """Raised when a patch is stale, overlapping, or cannot be reversed safely."""

def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

@dataclass(frozen=True, slots=True)
class TextPatch:
    start: int
    end: int
    expected: str
    replacement: str

    def __post_init__(self) -> None:
        if isinstance(self.start, bool) or not isinstance(self.start, int):
            raise TypeError("patch start must be an integer")
        if isinstance(self.end, bool) or not isinstance(self.end, int):
            raise TypeError("patch end must be an integer")
        if self.start < 0 or self.end < self.start:
            raise ValueError("patch range must satisfy 0 <= start <= end")
        if not isinstance(self.expected, str) or not isinstance(self.replacement, str):
            raise TypeError("patch expected and replacement values must be strings")

@dataclass(frozen=True, slots=True)
class PatchReceipt:
    original: str
    updated: str
    patches: tuple[TextPatch, ...]
    original_sha256: str
    updated_sha256: str

    def rollback(self, current: str | None = None) -> str:
        if current is not None and current != self.updated:
            raise PatchConflict("current text differs from the patched snapshot")
        if _digest(self.original) != self.original_sha256:
            raise PatchConflict("original snapshot failed its integrity check")
        return self.original

    def reapply(self, current: str | None = None) -> str:
        if current is not None and current != self.original:
            raise PatchConflict("current text differs from the original snapshot")
        if _digest(self.updated) != self.updated_sha256:
            raise PatchConflict("updated snapshot failed its integrity check")
        return self.updated

@dataclass(frozen=True, slots=True)
class PatchSet:
    identifier: str
    patches: tuple[TextPatch, ...]

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("patch set identifier cannot be empty")
        if not self.patches:
            raise ValueError("patch set must contain at least one patch")
        if not all(isinstance(item, TextPatch) for item in self.patches):
            raise TypeError("patches must contain only TextPatch values")

    def apply(self, source: str) -> PatchReceipt:
        if not isinstance(source, str):
            raise TypeError("patch source must be text")
        ordered = sorted(self.patches, key=lambda item: (item.start, item.end))
        previous_start, previous_end = -1, 0
        for patch in ordered:
            if patch.start < previous_end or patch.start == previous_start:
                raise PatchConflict("patch ranges overlap or share an ambiguous insertion point")
            if patch.end > len(source):
                raise PatchConflict("patch range extends beyond the source text")
            if source[patch.start:patch.end] != patch.expected:
                raise PatchConflict(f"stale patch at offsets {patch.start}:{patch.end}; expected text does not match")
            previous_start, previous_end = patch.start, patch.end
        updated = source
        for patch in reversed(ordered):
            updated = updated[:patch.start] + patch.replacement + updated[patch.end:]
        return PatchReceipt(source, updated, tuple(ordered), _digest(source), _digest(updated))

__all__ = ["PatchConflict", "TextPatch", "PatchReceipt", "PatchSet"]
