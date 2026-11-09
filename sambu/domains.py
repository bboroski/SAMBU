"""Domain models for networks, negotiation, growth funnels, events and territory games.

These are transparent deterministic models, not predictions about real people or markets.
All percentages are represented as fractions in [0, 1].
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import re

from .values import Quantity, number_value


@dataclass(frozen=True)
class Graph:
    nodes: tuple[str, ...]
    edges: tuple[tuple[int, int, float], ...]

    def __str__(self) -> str:
        return f"Graph(nodes={len(self.nodes)}, edges={len(self.edges)})"


def _arity(args: list[object], allowed: set[int], signature: str) -> None:
    if len(args) not in allowed:
        expected = " or ".join(str(n) for n in sorted(allowed))
        raise TypeError(f"{signature} expects {expected} arguments")


def _array(value: object, what: str) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{what} must be an array")
    return value


def _nonnegative(value: object, what: str) -> float:
    result = number_value(value, what)
    if result < 0:
        raise ValueError(f"{what} cannot be negative")
    return result


def _integer(value: object, what: str, minimum: int = 0, maximum: int = 10**12) -> int:
    number = number_value(value, what)
    result = int(number)
    if result != number or result < minimum or result > maximum:
        raise ValueError(f"{what} must be an integer from {minimum} to {maximum}")
    return result


def network(args: list[object]) -> Graph:
    """Build a directed weighted network from nodes and [source, target, weight] edges."""
    _arity(args, {2}, "network(nodes, edges)")
    raw_nodes = _array(args[0], "network nodes")
    if not raw_nodes or any(not isinstance(node, str) or not node for node in raw_nodes):
        raise ValueError("network nodes must be a non-empty array of non-empty strings")
    nodes = tuple(raw_nodes)
    if len(set(nodes)) != len(nodes):
        raise ValueError("network node names must be unique")
    index = {name: i for i, name in enumerate(nodes)}
    edges: list[tuple[int, int, float]] = []
    seen: set[tuple[int, int]] = set()
    for row in _array(args[1], "network edges"):
        edge = _array(row, "each network edge")
        if len(edge) not in (2, 3):
            raise ValueError("each edge must be [source, target] or [source, target, weight]")
        source, target = edge[0], edge[1]
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError("edge endpoints must be node-name strings")
        if source not in index or target not in index:
            raise ValueError(f"edge references unknown node: {source!r} -> {target!r}")
        pair = (index[str(source)], index[str(target)])
        if pair[0] == pair[1]:
            raise ValueError("self-links are not supported in SAMBU networks")
        if pair in seen:
            raise ValueError(f"duplicate directed edge: {source!r} -> {target!r}")
        seen.add(pair)
        weight = number_value(edge[2], "edge weight") if len(edge) == 3 else 1.0
        if not 0.0 < weight <= 1.0:
            raise ValueError("edge weight must be in (0, 1]")
        edges.append((pair[0], pair[1], weight))
    return Graph(nodes, tuple(edges))


def network_metrics(args: list[object]):
    """Return directed degree metrics and normalized degree centrality."""
    from .values import Record
    _arity(args, {1}, "network_metrics(graph)")
    graph = args[0]
    if not isinstance(graph, Graph):
        raise TypeError("network_metrics expects a network")
    n = len(graph.nodes)
    incoming = [0] * n
    outgoing = [0] * n
    for source, target, _ in graph.edges:
        outgoing[source] += 1
        incoming[target] += 1
    denominator = 2 * max(1, n - 1)
    centrality = [(incoming[i] + outgoing[i]) / denominator for i in range(n)]
    density = len(graph.edges) / (n * (n - 1)) if n > 1 else 0.0
    return Record({
        "nodes": list(graph.nodes),
        "node_count": n,
        "edge_count": len(graph.edges),
        "density": density,
        "in_degree": incoming,
        "out_degree": outgoing,
        "degree_centrality": centrality,
    })


def influence(args: list[object]):
    """Propagate strongest-path influence over a directed graph for a fixed number of rounds."""
    from .values import Record
    _arity(args, {2, 3, 4}, "influence(graph, seeds, steps=3, decay=0.8)")
    graph = args[0]
    if not isinstance(graph, Graph):
        raise TypeError("influence expects a network as its first argument")
    seeds = _array(args[1], "influence seeds")
    steps = _integer(args[2], "steps", 0, 100) if len(args) >= 3 else 3
    decay = number_value(args[3], "decay") if len(args) >= 4 else 0.8
    if not 0.0 <= decay <= 1.0:
        raise ValueError("decay must be between 0 and 1")
    index = {name: i for i, name in enumerate(graph.nodes)}
    scores = [0.0] * len(graph.nodes)
    for seed in seeds:
        if isinstance(seed, str):
            name, strength = seed, 1.0
        elif isinstance(seed, list) and len(seed) == 2 and isinstance(seed[0], str):
            name, strength = seed[0], number_value(seed[1], "seed strength")
        else:
            raise ValueError("each seed must be a node name or [node_name, strength]")
        if name not in index:
            raise ValueError(f"unknown seed node {name!r}")
        if not 0 <= strength <= 1:
            raise ValueError("seed strength must be between 0 and 1")
        scores[index[name]] = max(scores[index[name]], strength)
    for _ in range(steps):
        next_scores = scores.copy()
        for source, target, weight in graph.edges:
            next_scores[target] = max(next_scores[target], scores[source] * weight * decay)
        scores = next_scores
    return Record({"nodes": list(graph.nodes), "scores": scores, "steps": steps, "decay": decay})


def funnel(args: list[object]):
    """Analyze ordered stage counts in a non-increasing conversion funnel."""
    from .values import Record
    _arity(args, {1}, "funnel(stage_counts)")
    counts = [_integer(value, "stage count") for value in _array(args[0], "stage counts")]
    if len(counts) < 2:
        raise ValueError("a funnel needs at least two stage counts")
    if any(right > left for left, right in zip(counts, counts[1:])):
        raise ValueError("funnel stage counts must not increase")
    rates = [right / left if left else 0.0 for left, right in zip(counts, counts[1:])]
    dropoffs = [left - right for left, right in zip(counts, counts[1:])]
    overall = counts[-1] / counts[0] if counts[0] else 0.0
    return Record({
        "stage_counts": counts,
        "step_conversion": rates,
        "step_dropoff": dropoffs,
        "overall_conversion": overall,
        "total_lost": counts[0] - counts[-1],
    })


def ab_test(args: list[object]):
    """Two-sided pooled two-proportion z-test; use as a screening estimate, not a decision oracle."""
    from .values import Record
    _arity(args, {4}, "ab_test(control_visitors, control_conversions, variant_visitors, variant_conversions)")
    n0 = _integer(args[0], "control visitors", 1)
    x0 = _integer(args[1], "control conversions")
    n1 = _integer(args[2], "variant visitors", 1)
    x1 = _integer(args[3], "variant conversions")
    if x0 > n0 or x1 > n1:
        raise ValueError("conversions cannot exceed visitors")
    p0, p1 = x0 / n0, x1 / n1
    pooled = (x0 + x1) / (n0 + n1)
    standard_error = math.sqrt(pooled * (1 - pooled) * (1 / n0 + 1 / n1))
    z = (p1 - p0) / standard_error if standard_error else 0.0
    p_value = math.erfc(abs(z) / math.sqrt(2.0))
    relative = (p1 / p0 - 1.0) if p0 else None
    return Record({
        "control_rate": p0,
        "variant_rate": p1,
        "absolute_lift": p1 - p0,
        "relative_lift": relative,
        "z_score": z,
        "p_value": p_value,
        "significant_at_05": p_value < 0.05,
    })


_DAYS = {name: i for i, name in enumerate(("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"))}
_TIME = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


def weekly_schedule(args: list[object]):
    """Validate and normalize recurring weekly events [weekday, HH:MM, title, capacity?]."""
    from .values import Record
    _arity(args, {1}, "weekly_schedule(events)")
    rows = _array(args[0], "weekly events")
    if not rows:
        raise ValueError("weekly schedule cannot be empty")
    normalized = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        event = _array(row, "each weekly event")
        if len(event) not in (3, 4):
            raise ValueError("each event must be [weekday, HH:MM, title, capacity?]")
        day, clock, title = event[:3]
        if not isinstance(day, str) or day not in _DAYS:
            raise ValueError("weekday must be a full English weekday name")
        if not isinstance(clock, str) or not _TIME.match(clock):
            raise ValueError("event time must use 24-hour HH:MM format")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("event title must be a non-empty string")
        key = (day, clock)
        if key in seen:
            raise ValueError(f"duplicate event slot: {day} {clock}")
        seen.add(key)
        capacity = _integer(event[3], "event capacity", 1) if len(event) == 4 else None
        normalized.append(((_DAYS[day], clock), Record({"weekday": day, "time": clock, "title": title, "capacity": capacity})))
    normalized.sort(key=lambda pair: pair[0])
    events = [record for _, record in normalized]
    days = list(dict.fromkeys(record.get("weekday") for record in events))
    return Record({"events": events, "session_count": len(events), "active_weekdays": days, "fixed_weekly_rhythm": True})


def attendance(args: list[object]):
    """Calculate capacity utilization for a scheduled session."""
    from .values import Record
    _arity(args, {2}, "attendance(capacity, bookings)")
    capacity = _integer(args[0], "capacity", 1)
    bookings = _integer(args[1], "bookings")
    if bookings > capacity:
        raise ValueError("bookings cannot exceed capacity")
    return Record({"capacity": capacity, "bookings": bookings, "remaining": capacity - bookings, "fill_rate": bookings / capacity})


def capture_tower(args: list[object]):
    """Resolve one abstract tower capture attempt: pressure consumes defense/resistance."""
    from .values import Record
    _arity(args, {2}, "capture_tower(defense, incoming_pressure)")
    defense = _nonnegative(args[0], "defense")
    pressure = _nonnegative(args[1], "incoming pressure")
    captured = pressure >= defense
    return Record({
        "captured": captured,
        "remaining_defense": max(0.0, defense - pressure),
        "overflow": max(0.0, pressure - defense),
    })


def allocate(args: list[object]):
    """Split a non-negative resource in proportion to non-negative weights."""
    _arity(args, {2}, "allocate(resource, weights)")
    resource = args[0]
    if isinstance(resource, Quantity):
        if resource.value < 0:
            raise ValueError("resource cannot be negative")
    else:
        resource = _nonnegative(resource, "resource")
    weights = [_nonnegative(value, "allocation weight") for value in _array(args[1], "allocation weights")]
    total = sum(weights)
    if not weights or total <= 0:
        raise ValueError("allocation weights must contain a positive total")
    return [resource * (weight / total) for weight in weights]  # type: ignore[operator]


def negotiate(args: list[object]):
    """Find the overlap of two bargaining intervals [minimum, maximum]."""
    from .values import Record
    _arity(args, {4}, "negotiate(a_min, a_max, b_min, b_max)")
    a_min, a_max, b_min, b_max = args
    if a_min > a_max:  # type: ignore[operator]
        raise ValueError("first negotiation range minimum exceeds maximum")
    if b_min > b_max:  # type: ignore[operator]
        raise ValueError("second negotiation range minimum exceeds maximum")
    lower = max(a_min, b_min)  # type: ignore[type-var]
    upper = min(a_max, b_max)  # type: ignore[type-var]
    possible = lower <= upper  # type: ignore[operator]
    midpoint = (lower + upper) / 2 if possible else None  # type: ignore[operator]
    width = upper - lower if possible else None  # type: ignore[operator]
    return Record({"possible": possible, "lower": lower if possible else None, "upper": upper if possible else None, "midpoint": midpoint, "overlap_width": width})


def channel_metrics(args: list[object]):
    """Calculate basic cost and conversion metrics for one marketing channel."""
    from .values import Record
    _arity(args, {4}, "channel_metrics(spend, impressions, leads, customers)")
    spend = _nonnegative(args[0], "channel spend")
    impressions = _integer(args[1], "impressions", maximum=10**12)
    leads = _integer(args[2], "leads", maximum=10**12)
    customers = _integer(args[3], "customers", maximum=10**12)
    if leads > impressions or customers > leads:
        raise ValueError("expected customers <= leads <= impressions")
    return Record({
        "spend": spend,
        "impressions": impressions,
        "leads": leads,
        "customers": customers,
        "lead_rate": leads / impressions if impressions else None,
        "close_rate": customers / leads if leads else None,
        "customer_rate": customers / impressions if impressions else None,
        "cost_per_lead": spend / leads if leads else None,
        "cost_per_customer": spend / customers if customers else None,
    })


def package_pricing(args: list[object]):
    """Compare a multi-session package with the equivalent single-session price."""
    from .values import Record
    _arity(args, {3}, "package_pricing(single_price, package_price, sessions)")
    single_price = _nonnegative(args[0], "single-session price")
    package_price = _nonnegative(args[1], "package price")
    sessions = _integer(args[2], "package sessions", 1, 100_000)
    full_price = single_price * sessions
    savings = full_price - package_price
    return Record({
        "single_price": single_price,
        "package_price": package_price,
        "sessions": sessions,
        "effective_session_price": package_price / sessions,
        "savings": savings,
        "discount_rate": savings / full_price if full_price else 0.0,
    })


def unit_economics(args: list[object]):
    """Calculate per-customer contribution before and after acquisition cost."""
    from .values import Record
    _arity(args, {3}, "unit_economics(revenue, variable_cost, acquisition_cost)")
    revenue, variable_cost, acquisition_cost = (_nonnegative(v, name) for v, name in zip(args, ("revenue", "variable cost", "acquisition cost")))
    before = revenue - variable_cost
    after = before - acquisition_cost
    return Record({
        "revenue": revenue,
        "variable_cost": variable_cost,
        "acquisition_cost": acquisition_cost,
        "contribution_before_acquisition": before,
        "contribution_after_acquisition": after,
        "margin_after_acquisition": after / revenue if revenue else None,
    })


# Commerce queue-planning primitives. These model configuration; they do not
# connect to RabbitMQ or execute Magento checkout operations.
_QUEUE_NAME = re.compile(r"^[a-z][a-z0-9_.-]{0,62}$")


def queue_profile(args: list[object]):
    """Describe a bounded worker pool and its dead-letter destination."""
    from .values import Record
    _arity(args, {5}, "queue_profile(name, workers, prefetch, retry_limit, dead_letter_enabled)")
    name, workers, prefetch, retry_limit, dead_letter = args
    if not isinstance(name, str) or not _QUEUE_NAME.fullmatch(name):
        raise ValueError("queue name must be 1-63 lowercase letters, digits, dots, underscores or hyphens")
    workers = _integer(workers, "worker count", 1, 256)
    prefetch = _integer(prefetch, "prefetch", 1, 1000)
    retry_limit = _integer(retry_limit, "retry limit", 0, 100)
    if not isinstance(dead_letter, bool):
        raise TypeError("dead_letter_enabled must be true or false")
    return Record({
        "name": name,
        "workers": workers,
        "prefetch": prefetch,
        "max_in_flight": workers * prefetch,
        "retry_limit": retry_limit,
        "max_attempts": retry_limit + 1,
        "dead_letter_enabled": dead_letter,
        "dead_letter_queue": name + ".dlq" if dead_letter else None,
    })


def retry_schedule(args: list[object]):
    """Return capped exponential retry delays in seconds (excluding the first attempt)."""
    _arity(args, {4}, "retry_schedule(max_attempts, initial_delay, multiplier, max_delay)")
    attempts = _integer(args[0], "maximum attempts", 1, 21)
    initial = _nonnegative(args[1], "initial retry delay")
    multiplier = number_value(args[2], "retry multiplier")
    maximum = _nonnegative(args[3], "maximum retry delay")
    if initial <= 0 or maximum <= 0:
        raise ValueError("initial and maximum retry delays must be positive")
    if multiplier < 1:
        raise ValueError("retry multiplier must be at least 1")
    delays = []
    delay = initial
    for _ in range(attempts - 1):
        delay = min(delay, maximum)
        delays.append(delay)
        delay = min(delay * multiplier, maximum)
    return delays


def idempotency_key(args: list[object]) -> str:
    """Build a stable namespaced key; callers must still persist and enforce uniqueness."""
    _arity(args, {2}, "idempotency_key(scope, identifier)")
    scope, identifier = args
    if not isinstance(scope, str) or not isinstance(identifier, str):
        raise TypeError("idempotency_key arguments must be strings")
    if not scope.strip() or not identifier.strip():
        raise ValueError("idempotency key scope and identifier cannot be empty")
    if len(scope) > 64 or len(identifier) > 128:
        raise ValueError("idempotency key parts exceed their length limits")
    return scope.strip() + ":" + identifier.strip()


DOMAIN_BUILTINS = {
    "network": network,
    "network_metrics": network_metrics,
    "influence": influence,
    "funnel": funnel,
    "ab_test": ab_test,
    "weekly_schedule": weekly_schedule,
    "attendance": attendance,
    "capture_tower": capture_tower,
    "allocate": allocate,
    "negotiate": negotiate,
    "channel_metrics": channel_metrics,
    "package_pricing": package_pricing,
    "unit_economics": unit_economics,
    "queue_profile": queue_profile,
    "retry_schedule": retry_schedule,
    "idempotency_key": idempotency_key,
}
