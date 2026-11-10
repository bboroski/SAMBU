"""Judo: composable engineering architecture models and invariant checks.

The framework is deterministic and offline. It validates a declared system graph;
it does not deploy services, contact infrastructure, or claim production health.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class Component:
    identifier: str
    kind: str
    layer: str
    criticality: str = "normal"
    owner: str | None = None
    replicas: int = 1
    stateful: bool = False
    provides: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()
    fault_domains: tuple[str, ...] = ()
    deployment_unit: str | None = None
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.identifier.strip():
            raise ValueError("component identifier cannot be empty")
        if not self.kind.strip() or not self.layer.strip():
            raise ValueError("component kind and layer cannot be empty")
        if self.criticality not in {"low", "normal", "high", "critical"}:
            raise ValueError("criticality must be low, normal, high, or critical")
        if isinstance(self.replicas, bool) or self.replicas < 1:
            raise ValueError("replicas must be a positive integer")
        if len(set(self.provides)) != len(self.provides):
            raise ValueError("provided contract names must be unique")
        if len(set(self.requires)) != len(self.requires):
            raise ValueError("required contract names must be unique")


@dataclass(frozen=True, slots=True)
class Connection:
    source: str
    target: str
    relation: str = "depends_on"
    contracts: tuple[str, ...] = ()
    optional: bool = False

    def __post_init__(self) -> None:
        if self.relation not in {"depends_on", "calls", "publishes_to", "observes", "owns"}:
            raise ValueError(f"unsupported architecture relation {self.relation!r}")


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    severity: str
    subject: str
    message: str


@dataclass(frozen=True, slots=True)
class ArchitectureMetrics:
    component_count: int
    connection_count: int
    dependency_count: int
    isolated_components: tuple[str, ...]
    maximum_dependency_depth: int
    critical_single_points: tuple[str, ...]
    deployment_order: tuple[str, ...] | None


@dataclass(frozen=True, slots=True)
class ArchitectureReport:
    name: str
    version: str
    findings: tuple[Finding, ...]
    metrics: ArchitectureMetrics

    @property
    def is_valid(self) -> bool:
        return not any(item.severity == "error" for item in self.findings)

    @property
    def errors(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == "error")

    @property
    def warnings(self) -> tuple[Finding, ...]:
        return tuple(item for item in self.findings if item.severity == "warning")

    def to_dict(self) -> dict[str, object]:
        return {
            "framework": "Judo",
            "name": self.name,
            "version": self.version,
            "is_valid": self.is_valid,
            "findings": [asdict(item) for item in self.findings],
            "metrics": asdict(self.metrics),
        }


@dataclass(slots=True)
class JudoPolicy:
    layer_order: tuple[str, ...] = ()
    require_component_owner: bool = False
    enforce_contracts: bool = True
    critical_min_replicas: int = 1
    critical_distinct_fault_domains: int = 1
    max_components: int = 10_000
    max_dependency_depth: int | None = None


class JudoArchitecture:
    """Mutable builder for an explicit, versioned engineering architecture."""

    def __init__(self, name: str, version: str = "1.0.0", policy: JudoPolicy | None = None):
        if not name.strip():
            raise ValueError("architecture name cannot be empty")
        self.name = name
        self.version = version
        self.policy = policy or JudoPolicy()
        self._components: dict[str, Component] = {}
        self._connections: list[Connection] = []

    @property
    def components(self) -> Mapping[str, Component]:
        return dict(self._components)

    @property
    def connections(self) -> tuple[Connection, ...]:
        return tuple(self._connections)

    def add_component(self, component: Component | None = None, **values: object) -> "JudoArchitecture":
        item = component if component is not None else Component(**values)  # type: ignore[arg-type]
        if item.identifier in self._components:
            raise ValueError(f"duplicate component {item.identifier!r}")
        self._components[item.identifier] = item
        return self

    def connect(
        self,
        source: str,
        target: str,
        *,
        relation: str = "depends_on",
        contracts: Iterable[str] = (),
        optional: bool = False,
    ) -> "JudoArchitecture":
        link = Connection(source, target, relation, tuple(contracts), optional)
        if link in self._connections:
            raise ValueError(f"duplicate connection {source!r} -> {target!r}")
        self._connections.append(link)
        return self

    def _dependency_graph(self) -> dict[str, set[str]]:
        graph = {name: set() for name in self._components}
        for link in self._connections:
            if link.relation == "depends_on" and link.source in graph and link.target in graph:
                graph[link.source].add(link.target)
        return graph

    def _cycles(self, graph: Mapping[str, set[str]]) -> list[tuple[str, ...]]:
        colors: dict[str, int] = {name: 0 for name in graph}
        stack: list[str] = []
        found: list[tuple[str, ...]] = []

        def visit(node: str) -> None:
            colors[node] = 1
            stack.append(node)
            for target in sorted(graph[node]):
                if colors[target] == 0:
                    visit(target)
                elif colors[target] == 1:
                    start = stack.index(target)
                    cycle = tuple(stack[start:] + [target])
                    if cycle not in found:
                        found.append(cycle)
            stack.pop()
            colors[node] = 2

        for node in sorted(graph):
            if colors[node] == 0:
                visit(node)
        return found

    def deployment_order(self) -> tuple[str, ...] | None:
        """Return dependencies-first deployment order, or None when cyclic."""
        graph = self._dependency_graph()
        incoming = {name: 0 for name in graph}
        dependents: dict[str, set[str]] = defaultdict(set)
        for source, dependencies in graph.items():
            for dependency in dependencies:
                incoming[source] += 1
                dependents[dependency].add(source)
        ready = deque(sorted(name for name, degree in incoming.items() if degree == 0))
        order: list[str] = []
        while ready:
            node = ready.popleft()
            order.append(node)
            for dependent in sorted(dependents[node]):
                incoming[dependent] -= 1
                if incoming[dependent] == 0:
                    ready.append(dependent)
        return tuple(order) if len(order) == len(graph) else None

    def _maximum_depth(self, graph: Mapping[str, set[str]], order: tuple[str, ...] | None) -> int:
        if order is None:
            return 0
        depth = {name: 1 for name in order}
        for node in order:
            for dependency in graph[node]:
                depth[node] = max(depth[node], depth[dependency] + 1)
        return max(depth.values(), default=0)

    def validate(self) -> ArchitectureReport:
        findings: list[Finding] = []
        if len(self._components) > self.policy.max_components:
            findings.append(Finding(
                "JUDO-ARCH-001", "error", self.name,
                f"component count exceeds configured maximum {self.policy.max_components}",
            ))

        degree = {name: 0 for name in self._components}
        links_by_source: dict[str, list[Connection]] = defaultdict(list)
        for link in self._connections:
            if link.source not in self._components:
                findings.append(Finding(
                    "JUDO-GRAPH-001", "error", link.source,
                    f"connection targets unknown source component {link.source!r}",
                ))
                continue
            if link.target not in self._components:
                severity = "warning" if link.optional else "error"
                findings.append(Finding(
                    "JUDO-GRAPH-002", severity, link.target,
                    f"connection from {link.source!r} targets unknown component {link.target!r}",
                ))
                continue
            degree[link.source] += 1
            degree[link.target] += 1
            links_by_source[link.source].append(link)

        layer_index = {name: index for index, name in enumerate(self.policy.layer_order)}
        for component in self._components.values():
            if self.policy.require_component_owner and not component.owner:
                findings.append(Finding(
                    "JUDO-GOV-001", "error", component.identifier,
                    "component must declare an accountable owner",
                ))
            if degree[component.identifier] == 0:
                findings.append(Finding(
                    "JUDO-GRAPH-003", "warning", component.identifier,
                    "component is isolated from the declared architecture graph",
                ))
            if component.criticality == "critical":
                if component.replicas < self.policy.critical_min_replicas:
                    findings.append(Finding(
                        "JUDO-RES-001", "error", component.identifier,
                        f"critical component needs at least {self.policy.critical_min_replicas} replicas",
                    ))
                if len(set(component.fault_domains)) < self.policy.critical_distinct_fault_domains:
                    findings.append(Finding(
                        "JUDO-RES-002", "error", component.identifier,
                        "critical component does not span enough distinct fault domains",
                    ))

            if self.policy.layer_order and component.layer not in layer_index:
                findings.append(Finding(
                    "JUDO-LAYER-001", "error", component.identifier,
                    f"layer {component.layer!r} is absent from the configured layer order",
                ))

        for link in self._connections:
            source = self._components.get(link.source)
            target = self._components.get(link.target)
            if source is None or target is None:
                continue
            if self.policy.layer_order and source.layer in layer_index and target.layer in layer_index:
                if layer_index[source.layer] > layer_index[target.layer] and link.relation in {"depends_on", "calls"}:
                    findings.append(Finding(
                        "JUDO-LAYER-002", "error", f"{link.source}->{link.target}",
                        f"dependency points upward from {source.layer!r} to {target.layer!r}",
                    ))
            if self.policy.enforce_contracts and link.relation in {"depends_on", "calls"}:
                available = set(target.provides)
                required = set(source.requires)
                required_on_edge = set(link.contracts)
                missing = (required_on_edge or required) - available
                if missing:
                    findings.append(Finding(
                        "JUDO-CONTRACT-001", "error", f"{link.source}->{link.target}",
                        "target does not provide required contracts: " + ", ".join(sorted(missing)),
                    ))

        graph = self._dependency_graph()
        cycles = self._cycles(graph)
        for cycle in cycles:
            findings.append(Finding(
                "JUDO-GRAPH-004", "error", " -> ".join(cycle),
                "dependency cycle detected; split the cycle or introduce an explicit event boundary",
            ))

        order = self.deployment_order()
        maximum_depth = self._maximum_depth(graph, order)
        if (
            self.policy.max_dependency_depth is not None
            and maximum_depth > self.policy.max_dependency_depth
        ):
            findings.append(Finding(
                "JUDO-GRAPH-005", "error", self.name,
                f"dependency depth {maximum_depth} exceeds {self.policy.max_dependency_depth}",
            ))

        isolated = tuple(sorted(name for name, count in degree.items() if count == 0))
        critical_single = tuple(sorted(
            item.identifier for item in self._components.values()
            if item.criticality == "critical" and item.replicas < 2
        ))
        metrics = ArchitectureMetrics(
            component_count=len(self._components),
            connection_count=len(self._connections),
            dependency_count=sum(len(items) for items in graph.values()),
            isolated_components=isolated,
            maximum_dependency_depth=maximum_depth,
            critical_single_points=critical_single,
            deployment_order=order,
        )
        return ArchitectureReport(self.name, self.version, tuple(findings), metrics)


class Judo:
    """Namespace-style factory for Judo architecture models."""

    @staticmethod
    def architecture(name: str, version: str = "1.0.0", policy: JudoPolicy | None = None) -> JudoArchitecture:
        return JudoArchitecture(name, version, policy)


__all__ = [
    "Component", "Connection", "Finding", "ArchitectureMetrics",
    "ArchitectureReport", "JudoPolicy", "JudoArchitecture", "Judo",
]

# Canonical MCL terminology; the historical symbol remains supported.
ArchitectureGraph = JudoArchitecture

# Canonical MCL terminology; the historical symbol remains supported.
ArchitecturePolicy = JudoPolicy
