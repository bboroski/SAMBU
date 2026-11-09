"""Bounded concurrency and safety primitives for SAMBU.

The scheduler is cooperative and single-threaded. Actors serialize access to
their own state; supervisors restart failed actors within explicit budgets.
These tools do not claim OS-thread parallelism, native stack allocation, or
hardware-backed security.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import heapq
import json
import math
import threading
import time
from types import TracebackType
from typing import Callable, Generator, Iterable


class ConcurrencyError(RuntimeError):
    """Base error for bounded concurrency primitives."""


class SchedulerLimitError(ConcurrencyError):
    """A scheduler capacity or work budget was exceeded."""


class InvalidYieldError(ConcurrencyError):
    """A fiber yielded a value the scheduler does not understand."""


class MailboxFullError(ConcurrencyError):
    """An actor mailbox has reached its configured capacity."""


class ActorStoppedError(ConcurrencyError):
    """A message was sent to an actor that is not running."""


class ChannelEmptyError(ConcurrencyError):
    """A non-blocking typed channel has no queued value."""


class ChannelFullError(ConcurrencyError):
    """A bounded typed channel has no remaining capacity."""


class ResourceScopeError(ConcurrencyError):
    """One or more resources could not be closed safely."""

    def __init__(self, failures: Iterable[str]):
        self.failures = tuple(failures)
        super().__init__("; ".join(self.failures))


class AuthorizationError(ConcurrencyError):
    """A protected operation did not receive both independent approvals."""


@dataclass(frozen=True, slots=True)
class YieldNow:
    """Return control to the scheduler after the current generator step."""


@dataclass(frozen=True, slots=True)
class SleepTicks:
    """Suspend a fiber for a positive number of logical scheduler ticks."""

    ticks: int

    def __post_init__(self) -> None:
        if isinstance(self.ticks, bool) or not isinstance(self.ticks, int) or self.ticks < 1:
            raise ValueError("sleep ticks must be a positive integer")


def yield_now() -> YieldNow:
    """Yield to the next ready fiber."""
    return YieldNow()


def sleep_ticks(ticks: int) -> SleepTicks:
    """Suspend a fiber without blocking the host operating-system thread."""
    return SleepTicks(ticks)


@dataclass(slots=True)
class _Fiber:
    identifier: int
    name: str
    iterator: Generator[object, None, object]
    status: str = "ready"
    steps: int = 0
    result: object = None
    error: str | None = None
    step_limit: int = 100_000


@dataclass(frozen=True, slots=True)
class FiberHandle:
    identifier: int
    name: str


@dataclass(frozen=True, slots=True)
class FiberRunReport:
    logical_tick: int
    steps: int
    ready: int
    sleeping: int
    completed: int
    failed: int
    cancelled: int
    budget_exhausted: bool


class FiberScheduler:
    """A deterministic FIFO cooperative scheduler for Python generator fibers.

    Each resume of a generator is one scheduler step. A fiber runs until it
    yields, completes, or fails. The scheduler never creates an OS thread.
    """

    def __init__(self, *, max_tasks: int = 1024, max_total_steps: int = 1_000_000):
        self.max_tasks = _positive_int(max_tasks, "max_tasks", maximum=100_000)
        self.max_total_steps = _positive_int(
            max_total_steps, "max_total_steps", maximum=100_000_000
        )
        self._fibers: dict[int, _Fiber] = {}
        self._ready: deque[int] = deque()
        self._sleeping: list[tuple[int, int]] = []
        self._next_id = 1
        self.logical_tick = 0
        self.total_steps = 0
        self._lock = threading.RLock()

    def spawn(
        self,
        factory: Callable[..., object],
        *args: object,
        name: str | None = None,
        step_limit: int = 100_000,
        **kwargs: object,
    ) -> FiberHandle:
        if not callable(factory):
            raise TypeError("fiber factory must be callable")
        with self._lock:
            if len(self._fibers) >= self.max_tasks:
                raise SchedulerLimitError("fiber capacity exceeded")
            limit = _positive_int(step_limit, "step_limit", maximum=self.max_total_steps)
            identifier = self._next_id
            self._next_id += 1
            fiber_name = name or f"fiber-{identifier}"
            if not isinstance(fiber_name, str) or not fiber_name.strip():
                raise ValueError("fiber name must be a non-empty string")
            iterator = factory(*args, **kwargs)
            if not hasattr(iterator, "__next__") or not hasattr(iterator, "send"):
                raise TypeError("fiber factory must return a generator")
            self._fibers[identifier] = _Fiber(
                identifier, fiber_name, iterator, step_limit=limit
            )
            self._ready.append(identifier)
            return FiberHandle(identifier, fiber_name)

    def cancel(self, handle: FiberHandle | int) -> bool:
        identifier = handle.identifier if isinstance(handle, FiberHandle) else handle
        with self._lock:
            fiber = self._fibers.get(identifier)
            if fiber is None or fiber.status in {"completed", "failed", "cancelled"}:
                return False
            fiber.status = "cancelled"
            try:
                fiber.iterator.close()
            except Exception as exc:  # cancellation remains final and inspectable
                fiber.error = f"cancel cleanup: {type(exc).__name__}: {exc}"
            return True

    def run(self, *, max_steps: int | None = None) -> FiberRunReport:
        budget = (
            self.max_total_steps - self.total_steps
            if max_steps is None
            else _positive_int(max_steps, "max_steps", maximum=self.max_total_steps)
        )
        budget = min(budget, self.max_total_steps - self.total_steps)
        steps = 0
        while steps < budget:
            with self._lock:
                self._wake_sleepers()
                if not self._ready:
                    if not self._sleeping:
                        break
                    self.logical_tick = max(self.logical_tick, self._sleeping[0][0])
                    self._wake_sleepers()
                    if not self._ready:
                        break
                identifier = self._ready.popleft()
                fiber = self._fibers[identifier]
                if fiber.status != "ready":
                    continue
                fiber.status = "running"
            try:
                yielded = next(fiber.iterator)
            except StopIteration as stop:
                with self._lock:
                    fiber.result = stop.value
                    fiber.status = "completed"
            except Exception as exc:
                with self._lock:
                    fiber.error = f"{type(exc).__name__}: {exc}"
                    fiber.status = "failed"
            else:
                with self._lock:
                    fiber.steps += 1
                    if fiber.steps > fiber.step_limit:
                        fiber.status = "failed"
                        fiber.error = "per-fiber step budget exceeded"
                    elif yielded is None or isinstance(yielded, YieldNow):
                        fiber.status = "ready"
                        self._ready.append(identifier)
                    elif isinstance(yielded, SleepTicks):
                        fiber.status = "sleeping"
                        heapq.heappush(
                            self._sleeping, (self.logical_tick + yielded.ticks, identifier)
                        )
                    else:
                        fiber.status = "failed"
                        fiber.error = (
                            f"unsupported yield value {type(yielded).__name__}; "
                            "use yield_now() or sleep_ticks()"
                        )
            steps += 1
            self.total_steps += 1
            self.logical_tick += 1
        with self._lock:
            active = [fiber for fiber in self._fibers.values()
                      if fiber.status in {"ready", "running", "sleeping"}]
            return FiberRunReport(
                logical_tick=self.logical_tick,
                steps=steps,
                ready=sum(item.status == "ready" for item in active),
                sleeping=sum(item.status == "sleeping" for item in active),
                completed=sum(item.status == "completed" for item in self._fibers.values()),
                failed=sum(item.status == "failed" for item in self._fibers.values()),
                cancelled=sum(item.status == "cancelled" for item in self._fibers.values()),
                budget_exhausted=bool(active and (steps >= budget or self.total_steps >= self.max_total_steps)),
            )

    def result(self, handle: FiberHandle | int) -> object:
        fiber = self._get_fiber(handle)
        if fiber.status == "failed":
            raise ConcurrencyError(f"{fiber.name} failed: {fiber.error}")
        if fiber.status != "completed":
            raise ConcurrencyError(f"{fiber.name} has not completed (status={fiber.status})")
        return fiber.result

    def snapshot(self, handle: FiberHandle | int) -> dict[str, object]:
        fiber = self._get_fiber(handle)
        return {
            "id": fiber.identifier,
            "name": fiber.name,
            "status": fiber.status,
            "steps": fiber.steps,
            "error": fiber.error,
        }

    def _get_fiber(self, handle: FiberHandle | int) -> _Fiber:
        identifier = handle.identifier if isinstance(handle, FiberHandle) else handle
        try:
            return self._fibers[identifier]
        except KeyError as exc:
            raise KeyError(f"unknown fiber id {identifier!r}") from exc

    def _wake_sleepers(self) -> None:
        while self._sleeping and self._sleeping[0][0] <= self.logical_tick:
            _, identifier = heapq.heappop(self._sleeping)
            fiber = self._fibers[identifier]
            if fiber.status == "sleeping":
                fiber.status = "ready"
                self._ready.append(identifier)


def _positive_int(value: int, name: str, *, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValueError(f"{name} must be an integer from 1 to {maximum}")
    return value


def _bounded_payload(value: object, *, max_bytes: int = 65_536) -> object:
    """Copy a JSON-shaped value while bounding nesting, item count and size."""
    item_count = 0

    def visit(item: object, depth: int) -> object:
        nonlocal item_count
        item_count += 1
        if item_count > 10_000:
            raise ValueError("payload contains more than 10,000 values")
        if depth > 32:
            raise ValueError("payload nesting exceeds 32 levels")
        if item is None or type(item) in {bool, int, str}:
            return item
        if type(item) is float:
            if not math.isfinite(item):
                raise ValueError("payload numbers must be finite")
            return item
        if type(item) in {list, tuple}:
            return [visit(child, depth + 1) for child in item]
        if type(item) is dict:
            copied: dict[str, object] = {}
            for key, child in item.items():
                if not isinstance(key, str):
                    raise TypeError("payload object keys must be strings")
                copied[key] = visit(child, depth + 1)
            return copied
        raise TypeError(
            "actor payloads must contain only null, booleans, finite numbers, "
            "strings, arrays and string-keyed objects"
        )

    result = visit(value, 0)
    encoded = json.dumps(
        result, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    if len(encoded) > max_bytes:
        raise ValueError(f"payload exceeds {max_bytes} UTF-8 bytes")
    return result


@dataclass(frozen=True, slots=True)
class ActorSnapshot:
    name: str
    status: str
    state: object
    queued: int
    processed: int
    failures: int
    generation: int
    last_error: str | None


class Actor:
    """An actor with a bounded FIFO mailbox and sequential state transitions.

    Handler signature: handler(current_state, message) -> next_state.
    State is committed only after a successful, bounded return value.
    """

    def __init__(
        self,
        handler: Callable[[object, object], object],
        initial_state: object,
        *,
        name: str = "actor",
        mailbox_capacity: int = 256,
        max_payload_bytes: int = 65_536,
        dead_letter_capacity: int = 64,
    ):
        if not callable(handler):
            raise TypeError("actor handler must be callable")
        self.name = _non_empty(name, "actor name")
        self.mailbox_capacity = _positive_int(
            mailbox_capacity, "mailbox_capacity", maximum=1_000_000
        )
        self.max_payload_bytes = _positive_int(
            max_payload_bytes, "max_payload_bytes", maximum=16_777_216
        )
        self.dead_letter_capacity = _positive_int(
            dead_letter_capacity, "dead_letter_capacity", maximum=100_000
        )
        self.handler = handler
        self._initial_state = _bounded_payload(initial_state, max_bytes=max_payload_bytes)
        self._state = _bounded_payload(initial_state, max_bytes=max_payload_bytes)
        self._mailbox: deque[object] = deque()
        self._dead_letters: deque[dict[str, object]] = deque(maxlen=dead_letter_capacity)
        self._lock = threading.RLock()
        self._supervisor: Supervisor | None = None
        self.status = "active"
        self.processed = 0
        self.failures = 0
        self.generation = 0
        self.last_error: str | None = None

    def send(self, message: object) -> int:
        copied = _bounded_payload(message, max_bytes=self.max_payload_bytes)
        with self._lock:
            if self.status != "active":
                raise ActorStoppedError(f"actor {self.name!r} is {self.status}")
            if len(self._mailbox) >= self.mailbox_capacity:
                raise MailboxFullError(
                    f"actor {self.name!r} mailbox capacity {self.mailbox_capacity} reached"
                )
            self._mailbox.append(copied)
            return len(self._mailbox)

    def drain(self, *, max_messages: int = 1) -> dict[str, object]:
        limit = _positive_int(max_messages, "max_messages", maximum=1_000_000)
        processed_before = self.processed
        failed_now = False
        while self.processed - processed_before < limit:
            with self._lock:
                if self.status != "active" or not self._mailbox:
                    break
                message = self._mailbox.popleft()
                working_state = _bounded_payload(
                    self._state, max_bytes=self.max_payload_bytes
                )
                try:
                    next_state = self.handler(working_state, message)
                    committed = _bounded_payload(
                        next_state, max_bytes=self.max_payload_bytes
                    )
                except Exception as exc:
                    self.failures += 1
                    self.last_error = f"{type(exc).__name__}: {exc}"
                    self._dead_letters.append({
                        "message": message,
                        "error": self.last_error,
                        "generation": self.generation,
                    })
                    self.status = "failed"
                    supervisor = self._supervisor
                    failed_now = True
                else:
                    self._state = committed
                    self.processed += 1
                    supervisor = None
            if failed_now:
                if supervisor is not None:
                    supervisor._child_failed(self, self.last_error or "actor failure")
                break
        return {
            "processed": self.processed - processed_before,
            "failures": self.failures,
            "queued": self.queue_depth,
            "status": self.status,
        }

    @property
    def queue_depth(self) -> int:
        with self._lock:
            return len(self._mailbox)

    @property
    def dead_letters(self) -> tuple[dict[str, object], ...]:
        with self._lock:
            return tuple(_bounded_payload(item) for item in self._dead_letters)

    def snapshot(self) -> ActorSnapshot:
        with self._lock:
            return ActorSnapshot(
                self.name, self.status,
                _bounded_payload(self._state, max_bytes=self.max_payload_bytes),
                len(self._mailbox), self.processed, self.failures,
                self.generation, self.last_error,
            )

    def _restart(self) -> None:
        with self._lock:
            self._state = _bounded_payload(
                self._initial_state, max_bytes=self.max_payload_bytes
            )
            self.status = "active"
            self.generation += 1
            self.last_error = None

    def _stop(self) -> None:
        with self._lock:
            self.status = "stopped"


def _non_empty(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class SupervisorEvent:
    action: str
    child: str
    strategy: str
    reason: str
    restart_number: int


class Supervisor:
    """Hierarchical restart supervisor for actors and nested supervisors."""

    STRATEGIES = {"one_for_one", "one_for_all", "rest_for_one"}

    def __init__(
        self,
        *,
        name: str = "supervisor",
        strategy: str = "one_for_one",
        max_restarts: int = 3,
        window_seconds: float = 60.0,
        event_capacity: int = 256,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.name = _non_empty(name, "supervisor name")
        if strategy not in self.STRATEGIES:
            raise ValueError(
                "strategy must be one_for_one, one_for_all, or rest_for_one"
            )
        if isinstance(max_restarts, bool) or not isinstance(max_restarts, int) or max_restarts < 0:
            raise ValueError("max_restarts must be a non-negative integer")
        if not isinstance(window_seconds, (int, float)) or not math.isfinite(window_seconds) or window_seconds <= 0:
            raise ValueError("window_seconds must be finite and positive")
        self.strategy = strategy
        self.max_restarts = max_restarts
        self.window_seconds = float(window_seconds)
        self.clock = clock
        self._children: list[Actor | Supervisor] = []
        self._restart_times: deque[float] = deque()
        self._events: deque[SupervisorEvent] = deque(
            maxlen=_positive_int(event_capacity, "event_capacity", maximum=100_000)
        )
        self._lock = threading.RLock()
        self._supervisor: Supervisor | None = None
        self.status = "active"

    def supervise(self, child: Actor | Supervisor) -> None:
        if not isinstance(child, (Actor, Supervisor)):
            raise TypeError("supervisors can supervise actors or other supervisors")
        if child is self:
            raise ValueError("a supervisor cannot supervise itself")
        with self._lock:
            if self.status != "active":
                raise ConcurrencyError(f"supervisor {self.name!r} is not active")
            ancestor: Supervisor | None = self
            while ancestor is not None:
                if ancestor is child:
                    raise ValueError("supervision would create a cycle")
                ancestor = ancestor._supervisor
            if child._supervisor is not None:
                raise ValueError(f"child {child.name!r} already has a supervisor")
            self._children.append(child)
            child._supervisor = self

    def _child_failed(self, child: Actor | Supervisor, reason: str) -> None:
        parent_to_notify: Supervisor | None = None
        with self._lock:
            if self.status != "active":
                child._stop() if isinstance(child, Actor) else child._stop_tree()
                return
            now = self.clock()
            cutoff = now - self.window_seconds
            while self._restart_times and self._restart_times[0] < cutoff:
                self._restart_times.popleft()
            if len(self._restart_times) >= self.max_restarts:
                self.status = "failed"
                child._stop() if isinstance(child, Actor) else child._stop_tree()
                self._events.append(SupervisorEvent(
                    "escalate", child.name, self.strategy, reason, len(self._restart_times)
                ))
                parent_to_notify = self._supervisor
            else:
                try:
                    index = self._children.index(child)
                except ValueError:
                    child._stop() if isinstance(child, Actor) else child._stop_tree()
                    return
                if self.strategy == "one_for_one":
                    targets = [child]
                elif self.strategy == "one_for_all":
                    targets = list(self._children)
                else:
                    targets = self._children[index:]
                self._restart_times.append(now)
                restart_number = len(self._restart_times)
                for target in targets:
                    if isinstance(target, Actor):
                        target._restart()
                    else:
                        target._restart_tree()
                    self._events.append(SupervisorEvent(
                        "restart", target.name, self.strategy, reason, restart_number
                    ))
        if parent_to_notify is not None:
            parent_to_notify._child_failed(self, f"child supervisor failed: {reason}")

    def _restart_tree(self) -> None:
        with self._lock:
            self.status = "active"
            self._restart_times.clear()
            for child in self._children:
                if isinstance(child, Actor):
                    child._restart()
                else:
                    child._restart_tree()

    def _stop_tree(self) -> None:
        with self._lock:
            self.status = "stopped"
            for child in self._children:
                if isinstance(child, Actor):
                    child._stop()
                else:
                    child._stop_tree()

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            children = []
            for child in self._children:
                if isinstance(child, Actor):
                    snap = child.snapshot()
                    children.append({
                        "name": snap.name, "kind": "actor", "status": snap.status,
                        "queued": snap.queued, "generation": snap.generation,
                        "processed": snap.processed, "failures": snap.failures,
                    })
                else:
                    children.append({
                        "name": child.name, "kind": "supervisor",
                        "status": child.status,
                    })
            return {
                "name": self.name,
                "status": self.status,
                "strategy": self.strategy,
                "children": children,
                "recent_events": [
                    {
                        "action": event.action,
                        "child": event.child,
                        "reason": event.reason,
                        "restart_number": event.restart_number,
                    }
                    for event in self._events
                ],
                "restarts_in_window": len(self._restart_times),
            }


@dataclass(frozen=True, slots=True)
class ChannelType:
    name: str
    validator: Callable[[object], bool]


_CHANNEL_TYPES: dict[str, ChannelType] = {
    "int": ChannelType("int", lambda value: type(value) is int),
    "integer": ChannelType("integer", lambda value: type(value) is int),
    "float": ChannelType("float", lambda value: type(value) is float and math.isfinite(value)),
    "number": ChannelType(
        "number",
        lambda value: type(value) in {int, float} and (type(value) is int or math.isfinite(value)),
    ),
    "text": ChannelType("text", lambda value: isinstance(value, str)),
    "string": ChannelType("string", lambda value: isinstance(value, str)),
    "bool": ChannelType("bool", lambda value: type(value) is bool),
    "boolean": ChannelType("boolean", lambda value: type(value) is bool),
}


class TypedChannel:
    """A bounded, non-blocking, single-type FIFO channel."""

    def __init__(self, value_type: str, *, capacity: int = 64, name: str = "channel"):
        try:
            self.value_type = _CHANNEL_TYPES[value_type]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"unsupported channel type {value_type!r}") from exc
        self.name = _non_empty(name, "channel name")
        self.capacity = _positive_int(capacity, "capacity", maximum=1_000_000)
        self._values: deque[object] = deque()
        self._lock = threading.RLock()

    def send(self, value: object) -> int:
        if not self.value_type.validator(value):
            raise TypeError(
                f"channel {self.name!r} accepts {self.value_type.name}, "
                f"not {type(value).__name__}"
            )
        with self._lock:
            if len(self._values) >= self.capacity:
                raise ChannelFullError(f"channel {self.name!r} is full")
            self._values.append(value)
            return len(self._values)

    def receive(self) -> object:
        with self._lock:
            if not self._values:
                raise ChannelEmptyError(f"channel {self.name!r} is empty")
            return self._values.popleft()

    @property
    def depth(self) -> int:
        with self._lock:
            return len(self._values)


@dataclass(frozen=True, slots=True)
class ModuleMetadata:
    """Validated descriptive metadata; it is not a security credential."""

    module: str
    version: str
    owner: str
    emergency_contact: str
    telemetry_channel: str

    def validate(self) -> tuple[str, ...]:
        required = {
            "module": self.module,
            "version": self.version,
            "owner": self.owner,
            "emergency_contact": self.emergency_contact,
            "telemetry_channel": self.telemetry_channel,
        }
        return tuple(
            f"{name} must be a non-empty string"
            for name, value in required.items()
            if not isinstance(value, str) or not value.strip()
        )

    def require_valid(self) -> "ModuleMetadata":
        issues = self.validate()
        if issues:
            raise ValueError("invalid module metadata: " + "; ".join(issues))
        return self


class ResourceScope:
    """Own resources and close them in reverse acquisition order."""

    def __init__(self, *, name: str = "scope", max_resources: int = 1024):
        self.name = _non_empty(name, "scope name")
        self.max_resources = _positive_int(
            max_resources, "max_resources", maximum=1_000_000
        )
        self._resources: list[tuple[object, Callable[[], object]]] = []
        self._closed = False

    def __enter__(self) -> "ResourceScope":
        if self._closed:
            raise ConcurrencyError("resource scope is already closed")
        return self

    def own(
        self, resource: object, closer: Callable[[], object] | None = None
    ) -> object:
        if self._closed:
            raise ConcurrencyError("cannot add a resource to a closed scope")
        close_fn = closer or getattr(resource, "close", None)
        if not callable(close_fn):
            raise TypeError("resource must provide close() or an explicit closer")
        if len(self._resources) >= self.max_resources:
            raise SchedulerLimitError("resource scope capacity exceeded")
        if any(existing is resource for existing, _ in self._resources):
            raise ValueError("resource is already owned by this scope")
        self._resources.append((resource, close_fn))
        return resource

    def release(self, resource: object) -> object:
        if self._closed:
            raise ConcurrencyError("cannot release from a closed scope")
        for index, (existing, _) in enumerate(self._resources):
            if existing is resource:
                self._resources.pop(index)
                return existing
        raise ValueError("resource is not owned by this scope")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        failures: list[str] = []
        resources, self._resources = self._resources, []
        for resource, closer in reversed(resources):
            try:
                result = closer()
                if result is False:
                    raise RuntimeError("closer reported that the resource did not reach a safe state")
            except Exception as exc:
                failures.append(f"{type(resource).__name__}: {type(exc).__name__}: {exc}")
        if failures:
            raise ResourceScopeError(failures)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        try:
            self.close()
        except ResourceScopeError as close_error:
            if exc is None:
                raise
            if hasattr(exc, "add_note"):
                exc.add_note(f"resource cleanup also failed: {close_error}")
        return False


class DualAuthorizationGate:
    """Require two independently configured verifiers for a critical action.

    A hardware verifier can delegate to an HSM, TPM or external key service.
    This class itself does not provide cryptography or hardware isolation.
    """

    def __init__(
        self,
        local_verifier: Callable[[object], bool],
        hardware_verifier: Callable[[object], bool],
    ):
        if not callable(local_verifier) or not callable(hardware_verifier):
            raise TypeError("both authorization verifiers must be callable")
        if local_verifier is hardware_verifier:
            raise ValueError("local and hardware verifiers must be independent")
        self._local_verifier = local_verifier
        self._hardware_verifier = hardware_verifier
        self.authorized_count = 0
        self.denied_count = 0
        self._lock = threading.RLock()

    def authorize(self, local_credential: object, hardware_credential: object) -> bool:
        local_ok = bool(self._local_verifier(local_credential))
        hardware_ok = bool(self._hardware_verifier(hardware_credential))
        with self._lock:
            if not (local_ok and hardware_ok):
                self.denied_count += 1
                raise AuthorizationError("both local and hardware approvals are required")
            self.authorized_count += 1
        return True
