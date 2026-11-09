"""Stable source-location primitives shared by SAMBU tooling.

Offsets are zero-based Python string offsets (Unicode code points). Line and
column values are one-based, and span end positions are exclusive.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True, slots=True)
class SourcePosition:
    """A position in a source string."""

    offset: int
    line: int
    column: int

    def __post_init__(self) -> None:
        if self.offset < 0:
            raise ValueError("source offset cannot be negative")
        if self.line < 1 or self.column < 1:
            raise ValueError("source line and column numbers are one-based")


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """An end-exclusive range in a source string."""

    start: SourcePosition
    end: SourcePosition

    def __post_init__(self) -> None:
        if self.end.offset < self.start.offset:
            raise ValueError("source span end cannot precede its start")

    @classmethod
    def point(cls, position: SourcePosition) -> "SourceSpan":
        """Create an empty span at the supplied position."""
        return cls(position, position)

    @property
    def is_empty(self) -> bool:
        return self.start.offset == self.end.offset
