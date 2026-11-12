#!/usr/bin/env python3
"""Read-only storage audit and bounded engineering reference models.

Findings are review candidates, never proof of a leak or dead allocation.
This tool does not delete source, release memory, access devices, or perform I/O
other than reading the selected source tree and printing a report.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import tempfile
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, MutableSequence, Sequence

VERSION = "1.0.0"
SOURCE_SUFFIXES = {
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx",
    ".rs", ".swift", ".cs", ".py", ".js", ".jsx", ".ts", ".tsx",
}
SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "vendor", "third_party",
    "build", "dist", "target", "out", "coverage", "__pycache__",
}
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_MATRIX_ELEMENTS = 1_000_000

C_ARRAY = re.compile(
    r"^\s*(?:(?:static|extern|const|volatile|register|unsigned|signed)\s+)*"
    r"(?:[A-Za-z_]\w*(?:::\w+)?\s+)+"
    r"(?P<name>[A-Za-z_]\w*)\s*(?P<dims>(?:\[[^\]]*\]\s*)+)"
)
PATTERNS = (
    ("heap-allocation", re.compile(
        r"\b(?:malloc|calloc|realloc|aligned_alloc|reallocarray)\s*\("
    )),
    ("cpp-or-csharp-array", re.compile(
        r"\bnew\s+[A-Za-z_][\w:<>]*\s*\[[^\]]*\]"
    )),
    ("container-allocation", re.compile(
        r"\b(?:std::vector|std::array|Vec\s*<|Array\s*<|List\s*<|vector\s*<\s*vector\s*<)"
    )),
    ("numeric-buffer", re.compile(
        r"\b(?:bytearray|memoryview|np\.(?:array|zeros|ones|empty|full|ndarray)|"
        r"numpy\.(?:array|zeros|ones|empty|full|ndarray))\s*\("
    )),
    ("typed-array", re.compile(
        r"\bnew\s+(?:Array|(?:Int|Uint|Float|BigInt)(?:8|16|32|64)(?:Clamped)?Array)\s*\("
    )),
    ("swift-buffer", re.compile(
        r"\b(?:Array\s*\(\s*repeating:|reserveCapacity\s*\()"
    )),
    ("matrix-shaped-buffer", re.compile(
        r"\b(?:zeros|ones|empty|full|ndarray)\s*\(\s*\(|"
        r"\bArray2D\s*<|\bVec\s*<\s*Vec\s*<|\bvector\s*<\s*vector\s*<"
    )),
    ("pointer-arithmetic", re.compile(
        r"\b[A-Za-z_]\w*\s*\+\s*(?:sizeof\s*\(|[A-Za-z_]\w*\s*(?:\*|\+)|\d+)"
    )),
)


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    category: str
    excerpt: str
    guidance: str = (
        "Review all references, ownership, capacity and lifetime before changing this code."
    )


def _patterns_for(suffix: str) -> tuple[tuple[str, re.Pattern[str]], ...]:
    if suffix in {".c", ".h", ".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx"}:
        return (("fixed-array-candidate", C_ARRAY),) + PATTERNS
    if suffix == ".rs":
        allowed = {"container-allocation", "matrix-shaped-buffer", "pointer-arithmetic"}
        return tuple(item for item in PATTERNS if item[0] in allowed)
    if suffix == ".swift":
        allowed = {"container-allocation", "swift-buffer", "matrix-shaped-buffer"}
        return tuple(item for item in PATTERNS if item[0] in allowed)
    if suffix == ".cs":
        allowed = {"cpp-or-csharp-array", "container-allocation", "matrix-shaped-buffer"}
        return tuple(item for item in PATTERNS if item[0] in allowed)
    if suffix in {".py", ".js", ".jsx", ".ts", ".tsx"}:
        excluded = {"heap-allocation", "cpp-or-csharp-array", "pointer-arithmetic"}
        return tuple(item for item in PATTERNS if item[0] not in excluded)
    return ()


def _source_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        if root.suffix.lower() in SOURCE_SUFFIXES and not root.is_symlink():
            try:
                if root.stat().st_size <= MAX_FILE_BYTES:
                    yield root
            except OSError:
                pass
        return
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if relative.as_posix() in {
            "tools/engineering_integrity.py",
            "tests/test_engineering_integrity.py",
        }:
            continue
        try:
            if path.stat().st_size <= MAX_FILE_BYTES:
                yield path
        except OSError:
            continue


def scan(root: Path) -> list[Finding]:
    root = root.resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    findings: list[Finding] = []
    for path in _source_files(root):
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_number, line in enumerate(source.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith(
                ("//", "#", "/*", "*", "<!--", "'''", '"""')
            ):
                continue
            for category, pattern in _patterns_for(path.suffix.lower()):
                match = pattern.search(line)
                if not match:
                    continue
                if category == "fixed-array-candidate":
                    dimensions = match.group("dims")
                    category = (
                        "fixed-matrix-candidate"
                        if dimensions.count("[") > 1
                        else "fixed-array-candidate"
                    )
                findings.append(Finding(
                    path=path.relative_to(root).as_posix() if path != root else path.name,
                    line=line_number,
                    category=category,
                    excerpt=" ".join(stripped.split())[:220],
                ))
    return findings


@dataclass(frozen=True)
class ParticleEvent:
    event_id: str
    source: str
    kind: str
    tick: int
    correlation_id: str = ""
    hop: int = 0


class WaveBus:
    """Bounded corpuscular-event queue with duplicate and stale-event control."""
    ACCEPTED = "accepted"
    DUPLICATE = "duplicate"
    CONFLICT = "conflict"
    STALE = "stale"
    INVALID = "invalid"
    BACKPRESSURE = "backpressure"
    HOP_LIMIT = "hop_limit"

    def __init__(self, capacity: int = 128, max_hops: int = 16, seen_limit: int = 512):
        if capacity < 1 or max_hops < 0 or seen_limit < capacity:
            raise ValueError("invalid WaveBus bounds")
        self.capacity = capacity
        self.max_hops = max_hops
        self.seen_limit = seen_limit
        self._queue: deque[ParticleEvent] = deque()
        self._seen: deque[str] = deque()
        self._seen_set: set[str] = set()
        self._fingerprints: dict[str, tuple[str, str, int, str, int]] = {}

    def publish(self, event: ParticleEvent, *, now_tick: int, max_age: int) -> str:
        if (
            not event.event_id or not event.source or not event.kind
            or event.tick < 0 or event.hop < 0 or now_tick < 0 or max_age < 0
        ):
            return self.INVALID
        fingerprint = (event.source, event.kind, event.tick, event.correlation_id, event.hop)
        if event.event_id in self._seen_set:
            return self.DUPLICATE if self._fingerprints[event.event_id] == fingerprint else self.CONFLICT
        if event.tick > now_tick or now_tick - event.tick > max_age:
            return self.STALE
        if event.hop > self.max_hops:
            return self.HOP_LIMIT
        if len(self._queue) >= self.capacity:
            return self.BACKPRESSURE
        self._queue.append(event)
        self._seen.append(event.event_id)
        self._seen_set.add(event.event_id)
        self._fingerprints[event.event_id] = fingerprint
        while len(self._seen) > self.seen_limit:
            expired = self._seen.popleft()
            self._seen_set.discard(expired)
            self._fingerprints.pop(expired, None)
        return self.ACCEPTED

    def drain(self, limit: int) -> list[ParticleEvent]:
        if limit < 0:
            raise ValueError("limit must be non-negative")
        return [self._queue.popleft() for _ in range(min(limit, len(self._queue)))]

    def __len__(self) -> int:
        return len(self._queue)


class ResourceBudget:
    """Explicit capacity ledger for memory, work units or queue slots."""
    def __init__(self, capacity: int):
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        self.capacity = capacity
        self.used = 0

    @property
    def available(self) -> int:
        return self.capacity - self.used

    def reserve(self, amount: int) -> bool:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        if amount > self.available:
            return False
        self.used += amount
        return True

    def release(self, amount: int) -> None:
        if amount < 0 or amount > self.used:
            raise ValueError("release exceeds reserved amount")
        self.used -= amount


def dependency_cycle_candidates(graph: dict[str, Sequence[str]]) -> list[str]:
    """Return nodes left by topological reduction (cycles and their dependents)."""
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)
    indegree = {node: 0 for node in nodes}
    dependents: dict[str, list[str]] = {node: [] for node in nodes}
    for node, dependencies in graph.items():
        for dependency in set(dependencies):
            indegree[node] += 1
            dependents[dependency].append(node)
    ready = deque(sorted(node for node, degree in indegree.items() if degree == 0))
    removed = set()
    while ready:
        node = ready.popleft()
        removed.add(node)
        for dependent in dependents[node]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
    return sorted(nodes - removed)


@dataclass(frozen=True)
class MechanicsSnapshot:
    memory_utilization: float
    queue_pressure: float
    latency_us: float
    contention_events: int
    status: str


def technical_mechanics(
    *, memory_used_bytes: int, memory_capacity_bytes: int,
    queue_depth: int, queue_capacity: int, latency_us: float,
    contention_events: int, latency_limit_us: float = 1000.0,
    high_watermark: float = 0.9,
) -> MechanicsSnapshot:
    """Compare measured resource values with explicit capacities and units."""
    if (
        memory_used_bytes < 0 or memory_capacity_bytes < 1
        or queue_depth < 0 or queue_capacity < 1
        or contention_events < 0 or not math.isfinite(latency_us)
        or latency_us < 0 or not math.isfinite(latency_limit_us)
        or latency_limit_us <= 0 or not math.isfinite(high_watermark)
        or not 0.0 < high_watermark <= 1.0
    ):
        raise ValueError("invalid resource metrics or thresholds")
    memory_ratio = memory_used_bytes / memory_capacity_bytes
    queue_ratio = queue_depth / queue_capacity
    overloaded = (
        memory_ratio >= high_watermark or queue_ratio >= high_watermark
        or latency_us >= latency_limit_us
    )
    status = "overloaded" if overloaded else ("contended" if contention_events else "within-budget")
    return MechanicsSnapshot(memory_ratio, queue_ratio, latency_us, contention_events, status)


@dataclass(frozen=True)
class HealthThermalState:
    status: str
    heartbeat_age: int | None
    temperature_c: float | None
    temperature_state: str


def cardio_thermodynamics(
    *, now_tick: int, last_heartbeat_tick: int | None,
    temperature_c: float | None, heartbeat_timeout: int,
    temperature_limit_c: float,
) -> HealthThermalState:
    """Software health abstraction; missing telemetry remains unknown, not zero."""
    if now_tick < 0 or heartbeat_timeout < 0 or not math.isfinite(temperature_limit_c):
        raise ValueError("invalid telemetry bounds")
    if last_heartbeat_tick is None:
        age, live = None, "unknown"
    elif last_heartbeat_tick < 0 or last_heartbeat_tick > now_tick:
        raise ValueError("heartbeat tick is outside the monotonic timeline")
    else:
        age = now_tick - last_heartbeat_tick
        live = "healthy" if age <= heartbeat_timeout else "stale"
    if temperature_c is None:
        thermal = "unknown"
    elif not math.isfinite(temperature_c):
        raise ValueError("temperature must be finite or unavailable")
    else:
        thermal = "hot" if temperature_c >= temperature_limit_c else "within-limit"
    if live == "stale" or thermal == "hot":
        status = "degraded"
    elif live == "unknown" or thermal == "unknown":
        status = "unknown"
    else:
        status = "healthy"
    return HealthThermalState(status, age, temperature_c, thermal)


@dataclass(frozen=True)
class FlightTask:
    task_id: str
    priority: int
    submitted_tick: int


class LeafFlightScheduler:
    """Seeded, bounded background-task scheduler with age-based fairness."""
    def __init__(self, *, capacity: int = 64, seed: int = 0, age_weight: int = 1):
        if capacity < 1 or age_weight < 0:
            raise ValueError("invalid scheduler bounds")
        self.capacity = capacity
        self.age_weight = age_weight
        self._rng = random.Random(seed)
        self._tasks: list[FlightTask] = []

    def submit(self, task: FlightTask) -> bool:
        if not task.task_id or task.priority < 0 or task.submitted_tick < 0:
            raise ValueError("invalid task")
        if any(item.task_id == task.task_id for item in self._tasks):
            return False
        if len(self._tasks) >= self.capacity:
            return False
        self._tasks.append(task)
        return True

    def next(self, *, now_tick: int) -> FlightTask | None:
        if now_tick < 0:
            raise ValueError("now_tick must be non-negative")
        if not self._tasks:
            return None
        ranked = []
        for task in self._tasks:
            age = max(0, now_tick - task.submitted_tick)
            ranked.append((task.priority + age * self.age_weight + self._rng.random(),
                           task.task_id, task))
        chosen = max(ranked, key=lambda item: (item[0], item[1]))[2]
        self._tasks.remove(chosen)
        return chosen


@dataclass(frozen=True)
class MatrixView:
    rows: int
    cols: int
    stride: int
    data: Sequence[float]

    def validate(self) -> None:
        if self.rows < 1 or self.cols < 1 or self.stride < self.cols:
            raise ValueError("invalid matrix dimensions or stride")
        if self.rows * self.cols > MAX_MATRIX_ELEMENTS:
            raise ValueError("matrix view exceeds the configured element limit")
        required = (self.rows - 1) * self.stride + self.cols
        if required > MAX_MATRIX_ELEMENTS:
            raise ValueError("matrix view exceeds the configured storage-span limit")
        if required > len(self.data):
            raise ValueError("matrix view exceeds backing storage")
        for row in range(self.rows):
            for col in range(self.cols):
                if not math.isfinite(float(self.data[row * self.stride + col])):
                    raise ValueError("matrix contains a non-finite value")


def matrix_multiply(left: MatrixView, right: MatrixView) -> list[list[float]]:
    left.validate()
    right.validate()
    if left.cols != right.rows:
        raise ValueError("matrix dimensions do not conform")
    if left.rows * right.cols > MAX_MATRIX_ELEMENTS:
        raise ValueError("matrix result exceeds the configured element limit")
    def cell(row: int, col: int) -> float:
        def products():
            for k in range(left.cols):
                product = (
                    float(left.data[row * left.stride + k])
                    * float(right.data[k * right.stride + col])
                )
                if not math.isfinite(product):
                    raise ArithmeticError("matrix product overflow")
                yield product
        try:
            result = math.fsum(products())
        except OverflowError as error:
            raise ArithmeticError("matrix accumulation overflow") from error
        if not math.isfinite(result):
            raise ArithmeticError("matrix result is not finite")
        return result

    return [
        [cell(row, col) for col in range(right.cols)]
        for row in range(left.rows)
    ]


def zeroize_owned_buffer(storage: bytearray) -> None:
    """Overwrite caller-owned bytes; does not release memory or erase copies."""
    if not isinstance(storage, bytearray):
        raise TypeError("storage must be a caller-owned bytearray")
    storage[:] = b"\x00" * len(storage)


def zeroize_owned_matrix(
    storage: MutableSequence[float], *, rows: int, cols: int, stride: int
) -> None:
    """Overwrite a caller-owned matrix region; never deallocates its storage."""
    if rows < 1 or cols < 1 or stride < cols:
        raise ValueError("invalid matrix dimensions or stride")
    if rows * cols > MAX_MATRIX_ELEMENTS:
        raise ValueError("matrix region exceeds the configured element limit")
    required = (rows - 1) * stride + cols
    if required > MAX_MATRIX_ELEMENTS:
        raise ValueError("matrix region exceeds the configured storage-span limit")
    if required > len(storage):
        raise ValueError("matrix view exceeds backing storage")
    for row in range(rows):
        for col in range(cols):
            storage[row * stride + col] = 0


def self_test() -> None:
    bus = WaveBus(capacity=2, max_hops=2)
    event = ParticleEvent("e1", "self-test", "telemetry", 4)
    assert bus.publish(event, now_tick=5, max_age=2) == WaveBus.ACCEPTED
    assert bus.publish(event, now_tick=5, max_age=2) == WaveBus.DUPLICATE
    assert bus.publish(ParticleEvent("old", "test", "sample", 1), now_tick=5,
                       max_age=2) == WaveBus.STALE
    assert bus.publish(ParticleEvent("e2", "test", "sample", 5), now_tick=5,
                       max_age=2) == WaveBus.ACCEPTED
    assert bus.publish(ParticleEvent("e3", "test", "sample", 5), now_tick=5,
                       max_age=2) == WaveBus.BACKPRESSURE
    assert bus.publish(ParticleEvent("hop", "test", "sample", 5, hop=3),
                       now_tick=5, max_age=2) == WaveBus.HOP_LIMIT
    assert len(bus.drain(1)) == 1 and len(bus) == 1

    budget = ResourceBudget(10)
    assert budget.reserve(7) and not budget.reserve(4) and budget.available == 3
    budget.release(7)
    assert budget.available == 10

    assert dependency_cycle_candidates({"a": ["b"], "b": ["a"], "c": ["a"]}) == ["a", "b", "c"]
    metrics = technical_mechanics(
        memory_used_bytes=850, memory_capacity_bytes=1000,
        queue_depth=2, queue_capacity=10, latency_us=125.0,
        latency_limit_us=500.0, contention_events=0,
    )
    assert metrics.status == "within-budget" and metrics.memory_utilization == 0.85
    metrics = technical_mechanics(
        memory_used_bytes=950, memory_capacity_bytes=1000,
        queue_depth=2, queue_capacity=10, latency_us=125.0,
        latency_limit_us=500.0, contention_events=0,
    )
    assert metrics.status == "overloaded"

    conflict_bus = WaveBus(capacity=2)
    assert conflict_bus.publish(ParticleEvent("same", "one", "event", 3), now_tick=3, max_age=0) == WaveBus.ACCEPTED
    assert conflict_bus.publish(ParticleEvent("same", "two", "event", 3), now_tick=3, max_age=0) == WaveBus.CONFLICT

    state = cardio_thermodynamics(
        now_tick=10, last_heartbeat_tick=9, temperature_c=None,
        heartbeat_timeout=3, temperature_limit_c=80.0,
    )
    assert state.status == "unknown" and state.temperature_state == "unknown"
    state = cardio_thermodynamics(
        now_tick=10, last_heartbeat_tick=2, temperature_c=81.0,
        heartbeat_timeout=3, temperature_limit_c=80.0,
    )
    assert state.status == "degraded" and state.temperature_state == "hot"

    tasks = [FlightTask("a", 1, 0), FlightTask("b", 1, 0), FlightTask("c", 2, 0)]
    first = LeafFlightScheduler(capacity=3, seed=42)
    second = LeafFlightScheduler(capacity=3, seed=42)
    for task in tasks:
        assert first.submit(task) and second.submit(task)
    order_a = [first.next(now_tick=3).task_id for _ in tasks]  # type: ignore[union-attr]
    order_b = [second.next(now_tick=3).task_id for _ in tasks]  # type: ignore[union-attr]
    assert order_a == order_b and sorted(order_a) == ["a", "b", "c"]

    left = MatrixView(2, 2, 2, [1.0, 2.0, 3.0, 4.0])
    right = MatrixView(2, 1, 1, [2.0, 1.0])
    assert matrix_multiply(left, right) == [[4.0], [10.0]]
    try:
        MatrixView(MAX_MATRIX_ELEMENTS + 1, 1, 1, ()).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("oversized matrix view must be rejected")
    try:
        matrix_multiply(
            MatrixView(1001, 1, 1, [1.0] * 1001),
            MatrixView(1, 1000, 1000, [1.0] * 1000),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("oversized matrix result must be rejected")

    buffer = bytearray(b"private")
    zeroize_owned_buffer(buffer)
    assert buffer == bytearray(len(buffer))
    matrix = [1.0, 2.0, 99.0, 3.0, 4.0]
    zeroize_owned_matrix(matrix, rows=2, cols=2, stride=3)
    assert matrix == [0, 0, 99.0, 0, 0]

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "fixture.c").write_text(
            "static double grid[4][4];\nvoid *p = malloc(n);\n",
            encoding="utf-8",
        )
        categories = {finding.category for finding in scan(root)}
        assert "fixed-matrix-candidate" in categories
        assert "heap-allocation" in categories


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only storage audit and bounded engineering reference models"
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        print(f"engineering-integrity {VERSION}: self-test passed")
        return 0
    if not args.root.exists():
        parser.error(f"scan root does not exist: {args.root}")

    findings = scan(args.root)
    if args.format == "json":
        print(json.dumps({
            "version": VERSION,
            "root": str(args.root.resolve()),
            "mode": "read-only",
            "finding_count": len(findings),
            "findings": [asdict(item) for item in findings],
        }, indent=2))
    else:
        print(f"Engineering integrity audit {VERSION} — read-only")
        print(f"Root: {args.root.resolve()}")
        print(f"Review candidates: {len(findings)}")
        for item in findings:
            print(f"{item.path}:{item.line}: {item.category}: {item.excerpt}")
        print("No source files or runtime memory were modified.")
        print("A finding is not proof of dead storage; verify references and ownership.")
    return 1 if args.fail_on_findings and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
