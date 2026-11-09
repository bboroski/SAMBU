"""Deterministic, inspectable ecosystem-inspired systems planners for SAMBU."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Callable

from .values import Quantity, Record, number_value

_MAX_ITEMS = 100_000
_MAX_WORKERS = 4_096
_MAX_FEATURES = 64
_MAX_CONTEXT_NODES = 20_000
_MAX_CONTEXT_DEPTH = 64


class _FrozenList(list):
    """List-compatible immutable snapshot."""
    @staticmethod
    def _deny(*_args: object, **_kwargs: object) -> None:
        raise TypeError("imprinted closure context is immutable")

    __setitem__ = _deny
    __delitem__ = _deny
    append = _deny
    clear = _deny
    extend = _deny
    insert = _deny
    pop = _deny
    remove = _deny
    reverse = _deny
    sort = _deny
    __iadd__ = _deny
    __imul__ = _deny


def _freeze(value: object, active: set[int] | None = None,
            depth: int = 0, budget: list[int] | None = None) -> object:
    """Detach and recursively freeze a bounded SAMBU-compatible value graph."""
    if depth > _MAX_CONTEXT_DEPTH:
        raise ValueError("imprinted context exceeds maximum nesting depth")
    active = active if active is not None else set()
    budget = budget if budget is not None else [0]
    budget[0] += 1
    if budget[0] > _MAX_CONTEXT_NODES:
        raise ValueError("imprinted context exceeds maximum value count")
    if value is None or isinstance(value, (bool, int, str, bytes, Quantity)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("imprinted context cannot contain non-finite numbers")
        return value

    if isinstance(value, (Record, Mapping, list, tuple)):
        identity = id(value)
        if identity in active:
            raise ValueError("imprinted context cannot contain reference cycles")
        active.add(identity)
        try:
            if isinstance(value, Record):
                fields = {
                    key: _freeze(item, active, depth + 1, budget)
                    for key, item in value.fields.items()
                }
                return Record(MappingProxyType(fields))
            if isinstance(value, Mapping):
                fields: dict[str, object] = {}
                for key, item in value.items():
                    if not isinstance(key, str):
                        raise TypeError("imprinted context mapping keys must be strings")
                    fields[key] = _freeze(item, active, depth + 1, budget)
                return MappingProxyType(fields)
            items = [_freeze(item, active, depth + 1, budget) for item in value]
            return _FrozenList(items) if isinstance(value, list) else tuple(items)
        finally:
            active.remove(identity)

    raise TypeError("imprinted context supports only scalars, quantities, arrays and records")


@dataclass(frozen=True, slots=True)
class ImprintedClosure:
    """Callable that permanently captures one detached immutable context."""
    _callback: Callable[[list[object]], object]
    _context: object

    def __init__(self, callback: Callable[[list[object]], object], context: object):
        if not callable(callback):
            raise TypeError("imprint_closure expects a callable SAMBU function")
        object.__setattr__(self, "_callback", callback)
        object.__setattr__(self, "_context", _freeze(context))

    @property
    def context(self) -> object:
        return self._context

    def __call__(self, args: list[object]) -> object:
        if not isinstance(args, list):
            raise TypeError("imprinted closure arguments must be an array")
        return self._callback([self._context, *args])

    def __str__(self) -> str:
        return "<imprinted-closure: immutable first context>"


def _arity(args: list[object], allowed: set[int], signature: str) -> None:
    if len(args) not in allowed:
        expected = " or ".join(str(n) for n in sorted(allowed))
        raise TypeError(f"{signature} expects {expected} arguments")


def _array(value: object, what: str, maximum: int = _MAX_ITEMS) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{what} must be an array")
    if len(value) > maximum:
        raise ValueError(f"{what} cannot contain more than {maximum} items")
    return value


def _finite(value: object, what: str, minimum: float | None = None) -> float:
    result = number_value(value, what)
    if not math.isfinite(result):
        raise ValueError(f"{what} must be finite")
    if minimum is not None and result < minimum:
        raise ValueError(f"{what} must be at least {minimum}")
    return result


def _integer(value: object, what: str, minimum: int = 0,
             maximum: int = 1_000_000) -> int:
    # Preserve exact Python integers, including 64-bit trait masks.
    if isinstance(value, int) and not isinstance(value, bool):
        result = value
    else:
        number = _finite(value, what)
        result = int(number)
        if result != number:
            raise ValueError(f"{what} must be an integer")
    if result < minimum or result > maximum:
        raise ValueError(f"{what} must be an integer from {minimum} to {maximum}")
    return result


def imprint_closure(args: list[object]) -> ImprintedClosure:
    """Capture (function, context) once; all calls receive the same snapshot."""
    _arity(args, {2}, "imprint_closure(function, context)")
    callback, context = args
    if not callable(callback):
        raise TypeError("imprint_closure first argument must be a function")
    return ImprintedClosure(callback, context)  # type: ignore[arg-type]


def v_vector_stream(args: list[object]) -> Record:
    """Build a deterministic leader/follower index plan; does not schedule workers."""
    _arity(args, {2, 3, 4}, "v_vector_stream(item_count, workers, leader_share=0.6, phase=0)")
    total = _integer(args[0], "item_count", 0, 2**31 - 1)
    workers = _integer(args[1], "workers", 1, _MAX_WORKERS)
    share = _finite(args[2], "leader_share") if len(args) >= 3 else 0.6
    phase_input = _integer(args[3], "phase", 0, 2**31 - 1) if len(args) == 4 else 0
    if not 0.0 <= share <= 1.0:
        raise ValueError("leader_share must be between 0 and 1")

    followers = workers - 1
    leader_count = total if not followers else math.ceil(total * share)
    remaining = total - leader_count
    assignments = [Record({
        "worker": 0, "role": "leader", "start": 0,
        "stop": leader_count, "count": leader_count,
    })]
    if followers:
        base, extra = divmod(remaining, followers)
        cursor = leader_count
        phase = phase_input % followers
        for offset in range(followers):
            count = base + (1 if offset < extra else 0)
            worker = 1 + ((offset + phase) % followers)
            assignments.append(Record({
                "worker": worker, "role": "follower",
                "start": cursor, "stop": cursor + count,
                "count": count, "phase": phase,
            }))
            cursor += count

    return Record({
        "strategy": "leader_follower_partition",
        "item_count": total,
        "worker_count": workers,
        "leader_share": share,
        "phase": phase_input % followers if followers else 0,
        "assignments": assignments,
        "covered_items": sum(item.get("count") for item in assignments),
        "plan_only": True,
        "workers_started": False,
    })


def countercurrent_sync(args: list[object]) -> Record:
    """Plan bounded promotion/demotion between application-defined hot/cold tiers."""
    _arity(args, {5}, "countercurrent_sync(hot, cold, hot_capacity, promote_budget, demote_budget)")
    hot = list(_array(args[0], "hot tier"))
    cold = list(_array(args[1], "cold tier"))
    capacity = _integer(args[2], "hot_capacity", 0, _MAX_ITEMS)
    promote_budget = _integer(args[3], "promote_budget", 0, _MAX_ITEMS)
    demote_budget = _integer(args[4], "demote_budget", 0, _MAX_ITEMS)

    # Hot: most-recent to least-recent. Cold: highest to lowest promotion priority.
    overflow = max(0, len(hot) - capacity)
    demote_count = min(overflow, demote_budget)
    demoted = hot[len(hot) - demote_count:] if demote_count else []
    retained_hot = hot[:len(hot) - demote_count] if demote_count else hot[:]
    free_slots = max(0, capacity - len(retained_hot))
    promote_count = min(free_slots, promote_budget, len(cold))
    promoted = cold[:promote_count]
    hot_after = retained_hot + promoted
    cold_after = cold[promote_count:] + demoted

    if promoted and demoted:
        direction = "bidirectional"
    elif promoted:
        direction = "promote"
    elif demoted:
        direction = "demote"
    else:
        direction = "idle"
    return Record({
        "direction": direction,
        "hot_after": hot_after,
        "cold_after": cold_after,
        "promoted": promoted,
        "demoted": demoted,
        "promoted_count": len(promoted),
        "demoted_count": len(demoted),
        "hot_capacity": capacity,
        "capacity_satisfied": len(hot_after) <= capacity,
        "pending_evictions": max(0, len(hot_after) - capacity),
        "plan_only": True,
        "storage_transfer_executed": False,
    })


def biometric_taxonomy_sort(args: list[object]) -> Record:
    """Build a deterministic binary trait classifier from named integer bitmasks."""
    _arity(args, {2}, "biometric_taxonomy_sort(entities, features)")
    raw_entities = _array(args[0], "entities")
    raw_features = _array(args[1], "features", _MAX_FEATURES)
    if not raw_features:
        raise ValueError("features must contain at least one binary trait")
    if any(not isinstance(name, str) or not name for name in raw_features):
        raise ValueError("feature names must be non-empty strings")
    features = [str(name) for name in raw_features]
    if len(set(features)) != len(features):
        raise ValueError("feature names must be unique")
    if len(raw_entities) > 10_000:
        raise ValueError("taxonomy accepts at most 10,000 entities")

    maximum_mask = (1 << len(features)) - 1
    entries: list[tuple[str, int]] = []
    names: set[str] = set()
    for row in raw_entities:
        pair = _array(row, "each entity", 2)
        if len(pair) != 2 or not isinstance(pair[0], str) or not pair[0]:
            raise ValueError("each entity must be [non_empty_name, integer_mask]")
        name = str(pair[0])
        if name in names:
            raise ValueError(f"duplicate entity name {name!r}")
        names.add(name)
        entries.append((name, _integer(pair[1], f"trait mask for {name}", 0, maximum_mask)))
    entries.sort(key=lambda item: item[0])

    def leaf(items: list[tuple[str, int]]) -> Record:
        return Record({
            "kind": "leaf",
            "taxa": [name for name, _ in items],
            "trait_masks": sorted({mask for _, mask in items}),
            "count": len(items),
        })

    def build(items: list[tuple[str, int]], available: tuple[int, ...]) -> Record:
        if len(items) <= 1 or not available:
            return leaf(items)
        best: int | None = None
        best_balance = -1
        for feature_index in available:
            bit = 1 << feature_index
            present_count = sum(1 for _, mask in items if mask & bit)
            absent_count = len(items) - present_count
            if present_count and absent_count and min(present_count, absent_count) > best_balance:
                best = feature_index
                best_balance = min(present_count, absent_count)
        if best is None:
            return leaf(items)
        bit = 1 << best
        present = [item for item in items if item[1] & bit]
        absent = [item for item in items if not item[1] & bit]
        remaining = tuple(index for index in available if index != best)
        return Record({
            "kind": "split",
            "feature": features[best],
            "present": build(present, remaining),
            "absent": build(absent, remaining),
            "present_count": len(present),
            "absent_count": len(absent),
            "count": len(items),
        })

    return Record({
        "classification": "binary_trait_tree",
        "features": features,
        "taxa_order": [name for name, _ in entries],
        "taxa_count": len(entries),
        "root": build(entries, tuple(range(len(features)))),
        "phylogeny_inferred": False,
        "plan_only": True,
    })


def wetland_ecosystem_loop(args: list[object]) -> Record:
    """Calculate one bounded worker recommendation; never runs a controller."""
    _arity(args, {5, 6}, "wetland_ecosystem_loop(load, capacity_per_worker, current_workers, min_workers, max_workers, target_utilization=0.75)")
    load = _finite(args[0], "load", 0.0)
    capacity = _finite(args[1], "capacity_per_worker", 0.0)
    if capacity <= 0:
        raise ValueError("capacity_per_worker must be greater than zero")
    current = _integer(args[2], "current_workers", 0, _MAX_WORKERS)
    minimum = _integer(args[3], "min_workers", 0, _MAX_WORKERS)
    maximum = _integer(args[4], "max_workers", 0, _MAX_WORKERS)
    target = _finite(args[5], "target_utilization") if len(args) == 6 else 0.75
    if not 0.0 < target <= 1.0:
        raise ValueError("target_utilization must be in (0, 1]")
    if minimum > maximum:
        raise ValueError("min_workers cannot exceed max_workers")
    if not minimum <= current <= maximum:
        raise ValueError("current_workers must be within min_workers and max_workers")

    required = math.ceil(load / (capacity * target)) if load else 0
    desired = min(maximum, max(minimum, required))
    delta = desired - current
    action = "scale_up" if delta > 0 else "scale_down" if delta < 0 else "steady"
    current_utilization = load / (current * capacity) if current else None
    projected = load / (desired * capacity) if desired else None
    if projected is None and load > 0:
        pressure = "no_capacity"
    elif projected is not None and projected > 1.0:
        pressure = "over_capacity"
    elif projected is not None and projected > target:
        pressure = "above_target"
    else:
        pressure = "balanced"

    return Record({
        "current_workers": current,
        "desired_workers": desired,
        "worker_delta": delta,
        "action": action,
        "required_workers_before_clamp": required,
        "current_utilization": current_utilization,
        "projected_utilization": projected,
        "target_utilization": target,
        "capacity_limited": required > maximum,
        "resource_pressure": pressure,
        "controller_required": True,
        "plan_only": True,
        "workers_started_or_stopped": False,
        "gc_modified": False,
    })


ECOSYSTEM_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "imprint_closure": imprint_closure,
    "v_vector_stream": v_vector_stream,
    "countercurrent_sync": countercurrent_sync,
    "biometric_taxonomy_sort": biometric_taxonomy_sort,
    "wetland_ecosystem_loop": wetland_ecosystem_loop,
    "ImprintClosure": imprint_closure,
    "V_VectorStream": v_vector_stream,
    "CountercurrentSync": countercurrent_sync,
    "BiometricTaxonomySort": biometric_taxonomy_sort,
    "WetlandEcosystemLoop": wetland_ecosystem_loop,
}
