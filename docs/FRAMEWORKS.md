# SAMBU framework APIs — architecture, inference and UI control

Release target: SAMBU 0.7.0 (experimental alpha).

The three frameworks are independent Python host APIs shipped in the sambu package. They are designed to compose, but they do not silently perform network, deployment, browser or database actions.

## 1. Architecture validation API (legacy namespace: `Judo`)

Module: sambu.judo

The architecture model represents large systems as an explicit component graph. It is intended for service architectures, data platforms, modular monoliths, event-driven systems, enterprise integration maps and infrastructure blueprints.

Core building blocks:

- Component describes a service, database, queue, gateway, worker, library or other architectural unit, including layer, criticality, ownership, replicas, fault domains, provided contracts and required contracts.
- Connection records a directed dependency, call, event-publishing link, observation link or ownership relation.
- JudoPolicy defines layer direction, contract enforcement, owner requirements, critical redundancy and graph-depth limits.
- JudoArchitecture.validate() checks graph references, dependency cycles, contracts, layer direction, ownership, isolated components and critical component redundancy.
- deployment_order() returns a deterministic dependencies-first order or None when the dependency graph is cyclic.

Example:

~~~python
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
~~~

Judo is an architecture model and static validator. It does not deploy infrastructure, probe live services, prove real redundancy, execute migrations or verify cloud-provider configuration. A model can be valid while a real deployment is unhealthy.

## 2. Inference orchestration API (legacy namespace: `Aikido`)

Module: sambu.aikido

The inference API provides a provider-neutral integration boundary. A host application injects adapters for cloud models, local inference servers, private endpoints or other inference runtimes.

Capabilities:

- Registry of model profiles and provider adapters.
- Routing by capability, context window, output-token limit, priority, estimated cost and latency preference.
- Explicit primary-model and fallback-model chains.
- Bounded retries with a per-request retry count.
- Estimated-budget filtering before provider invocation and usage-based cost validation after a response.
- Structured telemetry for success, missing adapters, latency, token usage, model and estimated spend.

Implement ModelAdapter.infer(model, request) for a chosen provider. The adapter is responsible for transport-level timeout enforcement, TLS, credential handling, provider error normalization and cancellation.

Example:

~~~python
from sambu.aikido import (
    Aikido, InferenceRequest, InferenceResult, ModelProfile
)

class LocalAdapter:
    def infer(self, model, request):
        # Replace this body with a real, secured local/provider transport.
        return InferenceResult(
            content={"answer": "inference result"},
            model_id=model.identifier,
            provider=model.provider,
            input_tokens=120,
            output_tokens=80,
        )

hub = Aikido.hub()
hub.register_adapter("local", LocalAdapter())
hub.register_model(ModelProfile(
    "reasoner-small", "local",
    capabilities=frozenset({"chat", "json"}),
    context_window=32_000,
    max_output_tokens=4_000,
    priority=10,
))
result = hub.complete(InferenceRequest(
    prompt="Explain this architecture",
    required_capabilities=frozenset({"chat"}),
    max_output_tokens=1_000,
    max_cost=0.05,
    route_strategy="balanced",
))
print(result.content)
print(hub.telemetry[-1])
~~~

This API ships no provider credentials and does not make network calls by itself. The adapter controls the actual connection. Token and cost values returned by a provider are treated as usage reports, not independently audited invoices. Aikido is an orchestration boundary, not a claim that every AI vendor is already integrated.

## 3. UI workflow and access-control API (legacy namespace: `JiuJitsu`)

Module: sambu.jiu_jitsu

The UI workflow model separates view descriptions, controller actions and authorization policy.

- ViewNode is a renderer-neutral, serializable visual tree. Nodes have stable IDs, semantic component types, JSON-like props and child nodes.
- ViewDefinition associates a route with its title, root view and optional permission.
- ViewController maps named actions to explicit handlers. Unknown actions are rejected.
- JiuJitsuApp composes routes, controllers, application state, authorization and modal stack.
- ModalManager manages nested modal dialogs, payloads, return routes, permission checks and non-dismissible dialogs.
- RoleManager provides role-based access control (RBAC), inherited roles, wildcard grants and explicit-deny precedence.

Example:

~~~python
from sambu.jiu_jitsu import (
    JiuJitsu, Role, RoleManager, ViewNode, ViewDefinition,
    ViewController, ModalDefinition,
)

roles = RoleManager()
roles.add_role(Role("viewer", grants=frozenset({"dashboard:read"})))
roles.add_role(Role(
    "editor",
    grants=frozenset({"dashboard:write", "modal:confirm"}),
    inherits=("viewer",),
))
roles.assign("user-42", "editor")

app = JiuJitsu.app("user-42", roles)
app.register_view(ViewDefinition(
    "/dashboard", "Dashboard",
    ViewNode("dashboard", "page", {"title": "Orders"}, (
        ViewNode("save", "button", {"label": "Save"}),
    )),
    permission="dashboard:read",
))

controller = ViewController("dashboard").action(
    "save",
    lambda context, payload: context.state.update(
        {"saved": payload.get("value", True)}
    ) or "saved",
    permission="dashboard:write",
)
app.register_controller("/dashboard", controller)
app.modals.register(ModalDefinition(
    "confirm", ViewNode("confirm", "dialog", {"title": "Confirm"}),
    permission="modal:confirm",
))
app.navigate("/dashboard")
app.dispatch("save", {"value": True})
app.open_modal("confirm")
print(app.snapshot().to_dict())
~~~

Permission matching supports exact grants, area:* patterns and *. An explicit deny from any inherited or assigned role takes precedence over grants. Assignments are application data; the UI workflow API does not authenticate users or fetch identity claims. The host application must establish the principal and load role assignments from its trusted identity system.

This API does not ship a browser renderer or generate arbitrary JavaScript. A React, Vue, Svelte, Qt or native renderer can consume the serialized view model. The host must still validate user input on the server and enforce authorization at every protected data boundary.

## 4. How the frameworks compose

A practical division of responsibility:

1. The architecture API declares system components, dependencies, ownership, reliability assumptions and service contracts.
2. The inference API provides controlled model access through explicit provider adapters.
3. The UI API exposes workflows through views, controllers, modals and role-gated actions.

The three API models can share IDs and contract names, but no implicit coupling is created. For example, an architecture component can be named ai-gateway, an inference adapter can be injected into its host service, and the UI layer can present an authorized assistant view.

## 5. OOP and games in SAMBU 0.7.0

The interpreter's OOP slice includes classes, constructors (init), instance fields, methods, single inheritance, overriding, super parent dispatch, interfaces, traits, abstract and final classes/methods, method visibility and static fields/methods. Interfaces are structural contracts for method names and arities. Traits provide reusable concrete instance methods; conflicting trait methods require an explicit class implementation. Access modifiers currently govern methods; dynamically created instance fields are public.

~~~sambu
interface Renderable {
  fn render(self)
}

trait Identified {
  fn identity(self) { return self.name }
}

abstract class Widget implements Renderable {
  static let instances = 0
  fn init(self, name) {
    self.name = name
    Widget.instances = Widget.instances + 1
  }
  abstract fn render(self)
}

class Button extends Widget uses Identified {
  fn render(self) { return "[" + self.identity() + "]" }
}
let save = Button("Save")
print(save.render())
print(Widget.instances)
~~~

Game built-ins are deterministic and validate legal state transitions:

- rps_round(player_move, opponent_move) resolves rock-paper-scissors.
- tic_tac_toe_state(board) validates a reachable board and reports status.
- tic_tac_toe_move(board, player, position) returns a new legal board state.
- tic_tac_toe_best_move(board, player) computes a minimax-optimal tic-tac-toe move.

Tic-tac-toe boards are flat, row-major arrays of nine cells, with "X", "O" and "." (or null / empty string) for empty cells. Positions are zero-based. X starts. The evaluator rejects unreachable boards, illegal turns, occupied cells and moves after a terminal state.

## 6. Verification and release discipline

Run:

~~~bash
python -m pip install -e .
python -m unittest discover -s tests -v
sambu examples/oop_and_games.sambu
python examples/neo_modern_frameworks.py
~~~

The CI pipeline runs the test suite across the supported Python version matrix. The hourly repository audit is intentionally read-only: it runs tests and static repository checks, then publishes a report artifact. It does not allow a scheduled task to push unreviewed code or merge changes to the default branch.

All three frameworks are experimental alpha APIs. Their data structures and boundaries are explicit, but production adapters, authentication, cloud deployment, concrete renderers, static type checking and a full IDE remain separate integration work.
