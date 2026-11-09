"""Bounded, reusable chunking primitives for finite and streaming inputs."""
from __future__ import annotations
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass
from itertools import islice
import math
from typing import TypeVar

T = TypeVar("T")
_MAX_ITEMS = 1_000_000
_MAX_CHUNK_SIZE = 100_000

def _integer(value: object, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value

@dataclass(frozen=True, slots=True)
class ChunkManifest:
    total_items: int
    chunk_size: int
    chunk_count: int
    max_in_flight: int
    processing_waves: int
    final_chunk_size: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)

def plan_chunks(total_items: int, chunk_size: int, max_in_flight: int = 1) -> ChunkManifest:
    """Describe a bounded chunk plan without executing work."""
    total = _integer(total_items, "total_items", 0, _MAX_ITEMS)
    size = _integer(chunk_size, "chunk_size", 1, _MAX_CHUNK_SIZE)
    concurrency = _integer(max_in_flight, "max_in_flight", 1, 10_000)
    count = math.ceil(total / size) if total else 0
    final_size = total % size or (size if total else 0)
    waves = math.ceil(count / concurrency) if count else 0
    return ChunkManifest(total, size, count, concurrency, waves, final_size)

def chunked(items: Iterable[T], chunk_size: int, *, max_items: int = _MAX_ITEMS) -> Iterator[tuple[T, ...]]:
    """Yield immutable chunks lazily and reject streams over the configured ceiling."""
    size = _integer(chunk_size, "chunk_size", 1, _MAX_CHUNK_SIZE)
    limit = _integer(max_items, "max_items", 1, _MAX_ITEMS)
    iterator = iter(items)
    consumed = 0
    while True:
        batch = list(islice(iterator, min(size, limit - consumed)))
        if not batch:
            return
        consumed += len(batch)
        yield tuple(batch)
        if consumed == limit:
            try:
                next(iterator)
            except StopIteration:
                return
            raise ValueError(f"input exceeds the configured limit of {limit} items")

__all__ = ["ChunkManifest", "chunked", "plan_chunks"]
