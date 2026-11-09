# SAMBU frameworks: Judo, Aikido and Jiu-Jitsu

SAMBU ships three independent Python host APIs under the `sambu` package. They are designed to compose, but they do not silently perform network, deployment, browser or database actions.

## Judo — architecture modeling

**Module:** `sambu.judo`

Judo models a system as an explicit directed component graph. It is useful for describing service architectures, modular monoliths, data platforms, event-driven systems and infrastructure blueprints.

Core elements:

- `Component` describes a service, database, queue, gateway, worker, library or other unit. It can declare a layer, criticality, owner, replicas, fault domains, provided contracts and required contracts.
- `Connection` records a dependency, call, event-publishing link, observation link or ownership relation.
- `JudoPolicy` declares constraints such as layer direction, owner requirements, critical redundancy and graph-depth limits.
- `JudoArchitecture.validate()` checks graph references, dependency cycles, contracts, layer direction, ownership, isolated components and critical-component redundancy.
- `deployment_order()` returns a deterministic dependencies-first order, or `None` when the graph is cyclic.

Example:

```python
from sambu.judo import Component, Judo, JudoPolicy

architecture = Judo.architecture(
    "commerce",
    version="1.0",
    policy=JudoPolicy(
        layer_order=("edge", "application", "data"),
        require_component_owner=True,
        critical_min_replicas=2,
        critical_distinct_fault_domains=2,
    ),
)

architecture.add_component(Component(
    "orders-db", "database", "data",
    criticality="critical", owner="platform",
    replicas=2, fault_domains=("zone-a", "zone-b"),
    provides=("orders.read", "orders.write"),
))

architecture.add_component(Component(
    "order-service", "service", "application",
    owner="commerce", requires=("orders.read", "orders.write"),
))

architecture.connect(
    "order-service", "orders-db",
    contracts=("orders.read", "orders.write"),
)

report = architecture.validate()
print(report.to_dict())
```

**Boundary:** Judo is a model and static validator. It does not deploy infrastructure, probe live services, prove real redundancy, execute migrations or verify cloud configuration. A valid model does not prove a live deployment is healthy.

## Aikido — provider-neutral AI orchestration

**Module:** `sambu.aikido`

Aikido defines a provider-neutral boundary for routing inference requests. A host injects adapters for local inference servers, cloud models, private endpoints or other runtimes.

Capabilities include:
- model and adapter registries;
- capability matching;
- context-window and output-token constraints;
- priority and routing strategies;
- primary and fallback chains;
- bounded retries;
- estimated-budget preflight;
- usage-based cost checks;
- structured telemetry.

A host implements `ModelAdapter.infer(model, request)` for the provider it chooses.

**Boundary:** Aikido ships no provider credentials and makes no network call by itself. The adapter owns transport timeouts, TLS, credential handling, cancellation and provider-error normalization. Reported token and cost values are usage reports, not independently audited invoices.

## Jiu-Jitsu — renderer-neutral UI and MVC model

**Module:** `sambu.jiu_jitsu`

Jiu-Jitsu separates a serializable view description from controller actions and authorization policy.

Core elements:

- `ViewNode` represents a renderer-neutral visual tree with stable IDs, component types, JSON-like properties and child nodes.
- `ViewDefinition` associates a route with a title, root view and optional permission.
- `ViewController` maps named actions to explicit handlers.
- `JiuJitsuApp` composes routes, controllers, application state, authorization and modal stack.
- `ModalManager` manages nested dialogs, payloads, return routes and permission checks.
- `RoleManager` provides role-based access control with inherited roles, wildcard grants and explicit-deny precedence.

The model can be consumed by a React, Vue, Svelte, Qt or native renderer, but SAMBU does not ship a browser renderer or generate arbitrary JavaScript.

**Security boundary:** Jiu-Jitsu does not authenticate users. The host must establish the principal, load trusted role assignments, validate input and enforce authorization at every protected data boundary.

## How the frameworks compose

A practical division of responsibility:

1. **Judo** describes components, dependencies, ownership, contracts and reliability assumptions.
2. **Aikido** supplies a controlled inference capability through injected provider adapters.
3. **Jiu-Jitsu** exposes workflows through views, controllers, modals and role-gated actions.

They can share identifiers and contract names, but there is no hidden coupling between them.

## Status

All three are experimental alpha APIs. Treat data models as explicit planning and integration boundaries, not proof that an external service has been deployed or that a remote side effect has completed.

## Further reading

- [Framework implementation guide](../docs/FRAMEWORKS.md)
- [Web integrations](INTEGRATIONS-AND-SECURITY.md)
- [Architecture principles](DESIGN-PHILOSOPHY-AND-ROADMAP.md)
