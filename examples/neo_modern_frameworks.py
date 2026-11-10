"""Executable examples for the SAMBU 0.7.0 framework APIs.

Run with: python examples/neo_modern_frameworks.py
"""
from sambu.judo import Component, Judo, JudoPolicy
from sambu.aikido import Aikido, InferenceRequest, InferenceResult, ModelProfile
from sambu.jiu_jitsu import (
    JiuJitsu, ModalDefinition, Role, RoleManager,
    ViewController, ViewDefinition, ViewNode,
)


def run_judo() -> None:
    architecture = Judo.architecture(
        "neo-modern-commerce",
        policy=JudoPolicy(
            layer_order=("edge", "application", "data"),
            require_component_owner=True,
            critical_min_replicas=2,
            critical_distinct_fault_domains=2,
        ),
    )
    architecture.add_component(Component(
        "orders-db", "database", "data", criticality="critical",
        owner="platform", replicas=2, fault_domains=("zone-a", "zone-b"),
        provides=("orders.read", "orders.write"),
    ))
    architecture.add_component(Component(
        "orders-api", "service", "application",
        owner="commerce", requires=("orders.read", "orders.write"),
    ))
    architecture.connect(
        "orders-api", "orders-db",
        contracts=("orders.read", "orders.write"),
    )
    report = architecture.validate()
    assert report.is_valid, report.to_dict()
    print("Judo deployment order:", report.metrics.deployment_order)


class DemoAdapter:
    def infer(self, model, request):
        # This is a deterministic local stub, not a live neural provider.
        return InferenceResult(
            content={"summary": "SAMBU framework integration ready"},
            model_id=model.identifier,
            provider=model.provider,
            input_tokens=64,
            output_tokens=24,
        )


def run_aikido() -> None:
    hub = Aikido.hub()
    hub.register_adapter("demo-local", DemoAdapter())
    hub.register_model(ModelProfile(
        "demo-reasoner", "demo-local",
        capabilities=frozenset({"chat", "json"}),
        priority=10,
    ))
    result = hub.complete(InferenceRequest(
        prompt="Summarize the architecture",
        required_capabilities=frozenset({"chat"}),
        max_cost=1.0,
    ))
    print("Aikido response:", result.content)


def run_jiu_jitsu() -> None:
    roles = RoleManager()
    roles.add_role(Role("reader", grants=frozenset({"dashboard:read"})))
    roles.add_role(Role(
        "operator",
        grants=frozenset({"dashboard:refresh", "modal:help"}),
        inherits=("reader",),
    ))
    roles.assign("demo-user", "operator")

    app = JiuJitsu.app("demo-user", roles)
    app.register_view(ViewDefinition(
        "/dashboard", "Dashboard",
        ViewNode("dashboard", "page", {"title": "SAMBU"}, (
            ViewNode("refresh", "button", {"label": "Refresh"}),
        )),
        permission="dashboard:read",
    ))
    controller = ViewController("dashboard").action(
        "refresh",
        lambda context, payload: context.state.update({"refreshed": True}) or "refreshed",
        permission="dashboard:refresh",
    )
    app.register_controller("/dashboard", controller)
    app.modals.register(ModalDefinition(
        "help", ViewNode("help-dialog", "dialog", {"title": "Help"}),
        permission="modal:help",
    ))
    app.navigate("/dashboard")
    app.dispatch("refresh")
    app.open_modal("help")
    print("UI workflow model:", app.snapshot().to_dict())


if __name__ == "__main__":
    run_judo()
    run_aikido()
    run_jiu_jitsu()
