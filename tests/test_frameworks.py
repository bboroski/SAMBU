from __future__ import annotations

import unittest

from sambu import execute
from sambu.runtime import SambuRuntimeError
from sambu.judo import Component, Judo, JudoPolicy
from sambu.aikido import (
    Aikido, BudgetExceeded, InferenceExhausted, InferenceRequest,
    InferenceResult, ModelProfile, NoModelAvailable,
)
from sambu.jiu_jitsu import (
    AccessDenied, JiuJitsu, JiuJitsuError, ModalDefinition, Role,
    RoleManager, ViewController, ViewDefinition, ViewNode,
)


class OOPExpansionTests(unittest.TestCase):
    def test_interface_polymorphism_and_type_operator(self):
        output: list[str] = []
        execute("""
interface Speakable {
  fn speak(self)
}
class Animal implements Speakable {
  fn speak(self) { return "sound" }
}
class Dog extends Animal {
  fn speak(self) { return "bark" }
}
let dog = Dog()
print(dog.speak())
print(dog is Animal)
print(dog is Speakable)
""", output=output.append)
        self.assertEqual(output, ["bark", "true", "true"])

    def test_missing_interface_method_is_rejected(self):
        with self.assertRaises(SambuRuntimeError):
            execute("""
interface Renderable { fn render(self) }
class Broken implements Renderable { }
""")

    def test_abstract_class_requires_concrete_implementation(self):
        output: list[str] = []
        execute("""
abstract class Shape {
  abstract fn area(self)
}
class Square extends Shape {
  fn init(self, edge) { self.edge = edge }
  fn area(self) { return self.edge * self.edge }
}
let shape = Square(4)
print(shape.area())
""", output=output.append)
        self.assertEqual(output, ["16"])
        with self.assertRaises(SambuRuntimeError):
            execute("""
abstract class Shape { abstract fn area(self) }
let shape = Shape()
""")

    def test_traits_static_fields_and_static_methods(self):
        output: list[str] = []
        execute("""
trait Named {
  fn label(self) { return self.name }
}
class Counter uses Named {
  static let created = 0
  static fn kind() { return "counter" }
  fn init(self, name) { self.name = name }
}
let item = Counter("SAMBU")
print(item.label())
print(Counter.kind())
print(Counter.created)
Counter.created = Counter.created + 1
print(Counter.created)
""", output=output.append)
        self.assertEqual(output, ["SAMBU", "counter", "0", "1"])

    def test_final_class_and_final_method(self):
        with self.assertRaises(SambuRuntimeError):
            execute("""
final class Locked { }
class Child extends Locked { }
""")
        with self.assertRaises(SambuRuntimeError):
            execute("""
class Parent { final fn run(self) { return 1 } }
class Child extends Parent { fn run(self) { return 2 } }
""")

    def test_visibility_and_super_dispatch(self):
        output: list[str] = []
        execute("""
class Parent {
  protected fn value(self) { return 4 }
  private fn secret(self) { return 9 }
}
class Child extends Parent {
  fn value(self) { return super.value() + 1 }
  fn read(self) { return self.value() }
}
let item = Child()
print(item.read())
""", output=output.append)
        self.assertEqual(output, ["5"])
        with self.assertRaises(SambuRuntimeError):
            execute("""
class Parent { private fn secret(self) { return 9 } }
let item = Parent()
item.secret()
""")

    def test_multiple_trait_method_collision_requires_explicit_resolution(self):
        with self.assertRaises(SambuRuntimeError):
            execute("""
trait First { fn label(self) { return "first" } }
trait Second { fn label(self) { return "second" } }
class Combined uses First, Second { }
""")


class JudoTests(unittest.TestCase):
    def test_architecture_validates_contracts_and_deployment_order(self):
        model = Judo.architecture(
            "checkout",
            policy=JudoPolicy(layer_order=("api", "service", "storage")),
        )
        model.add_component(Component(
            "db", "database", "storage", provides=("orders.read", "orders.write"),
        ))
        model.add_component(Component(
            "orders", "service", "service", requires=("orders.read",),
        ))
        model.add_component(Component("api", "http", "api"))
        model.connect("orders", "db", contracts=("orders.read",))
        model.connect("api", "orders")
        report = model.validate()
        self.assertTrue(report.is_valid)
        self.assertEqual(report.metrics.deployment_order, ("db", "orders", "api"))

    def test_architecture_detects_cycles_unknown_edges_and_bad_contracts(self):
        model = Judo.architecture("broken")
        model.add_component(Component("a", "service", "app", requires=("a.read",)))
        model.add_component(Component("b", "database", "data"))
        model.connect("a", "b", contracts=("a.read",))
        model.connect("b", "a")
        model.connect("a", "missing")
        report = model.validate()
        self.assertFalse(report.is_valid)
        codes = {item.code for item in report.errors}
        self.assertIn("JUDO-CONTRACT-001", codes)
        self.assertIn("JUDO-GRAPH-004", codes)
        self.assertIn("JUDO-GRAPH-002", codes)


class _FakeAdapter:
    def __init__(self, content: str = "ok", fail: bool = False):
        self.content = content
        self.fail = fail
        self.calls = 0

    def infer(self, model, request):
        self.calls += 1
        if self.fail:
            raise RuntimeError("simulated provider outage")
        return InferenceResult(
            content=self.content,
            model_id=model.identifier,
            provider=model.provider,
            input_tokens=100,
            output_tokens=50,
        )


class AikidoTests(unittest.TestCase):
    def test_provider_routing_cost_and_telemetry(self):
        hub = Aikido.hub()
        adapter = _FakeAdapter("answer")
        hub.register_adapter("local", adapter)
        hub.register_model(ModelProfile(
            "small", "local", priority=2,
            input_cost_per_1k=0.01, output_cost_per_1k=0.02,
        ))
        result = hub.complete(InferenceRequest(
            prompt="hello", max_cost=0.04, route_strategy="lowest_cost",
        ))
        self.assertEqual(result.content, "answer")
        self.assertEqual(result.model_id, "small")
        self.assertEqual(result.estimated_cost, 0.002)
        self.assertEqual(hub.telemetry[-1].status, "success")

    def test_fallback_after_provider_failure(self):
        hub = Aikido.hub()
        first, second = _FakeAdapter(fail=True), _FakeAdapter("fallback")
        hub.register_adapter("down", first).register_adapter("up", second)
        hub.register_model(ModelProfile(
            "primary", "down", priority=10, fallback_models=("secondary",),
        ))
        hub.register_model(ModelProfile("secondary", "up", priority=1))
        result = hub.complete(InferenceRequest(
            prompt="hello", preferred_model="primary", max_retries=0,
        ))
        self.assertEqual(result.model_id, "secondary")
        self.assertEqual(first.calls, 1)
        self.assertEqual(second.calls, 1)

    def test_capability_and_budget_preflight(self):
        hub = Aikido.hub()
        hub.register_adapter("local", _FakeAdapter())
        hub.register_model(ModelProfile(
            "text-only", "local", capabilities=frozenset({"chat"}),
            input_cost_per_1k=1.0,
        ))
        with self.assertRaises(NoModelAvailable):
            hub.complete(InferenceRequest(
                prompt="draw", required_capabilities=frozenset({"image"}),
            ))
        with self.assertRaises(NoModelAvailable):
            hub.complete(InferenceRequest(prompt="too expensive", max_cost=0.0001))


class JiuJitsuTests(unittest.TestCase):
    def setUp(self):
        self.roles = RoleManager()
        self.roles.add_role(Role("reader", grants=frozenset({"page:read", "modal:help"})))
        self.roles.add_role(Role(
            "admin",
            grants=frozenset({"*"}),
            denies=frozenset({"order:delete"}),
            inherits=("reader",),
        ))
        self.roles.assign("alice", "admin")

    def test_view_serialization_controller_and_modal_stack(self):
        app = JiuJitsu.app("alice", self.roles)
        root = ViewNode("root", "page", {"heading": "Dashboard"}, (
            ViewNode("save", "button", {"label": "Save"}),
        ))
        app.register_view(ViewDefinition("/dashboard", "Dashboard", root, "page:read"))
        controller = ViewController("dashboard").action(
            "save",
            lambda context, payload: context.state.update({"saved": payload.get("value", True)}) or "saved",
            permission="page:read",
        )
        app.register_controller("/dashboard", controller)
        app.modals.register(ModalDefinition(
            "help", ViewNode("help-root", "dialog", {"title": "Help"}), "modal:help",
        ))
        snapshot = app.navigate("/dashboard")
        self.assertEqual(snapshot.view["type"], "page")
        self.assertEqual(app.dispatch("save", {"value": "yes"}), "saved")
        app.open_modal("help")
        self.assertEqual(len(app.snapshot().modals), 1)
        app.modals.close()
        self.assertEqual(app.snapshot().modals, ())

    def test_explicit_deny_overrides_inherited_admin_grant(self):
        with self.assertRaises(AccessDenied):
            self.roles.require("alice", "order:delete")
        self.roles.require("alice", "page:read")

    def test_role_cycles_unknown_actions_and_non_dismissible_modals(self):
        roles = RoleManager()
        roles.add_role(Role("a"))
        with self.assertRaises(ValueError):
            roles.add_role(Role("b", inherits=("missing",)))
        with self.assertRaises(JiuJitsuError):
            self.roles.require("unknown", "page:read")

        app = JiuJitsu.app("alice", self.roles)
        with self.assertRaises(JiuJitsuError):
            app.modals.close()
        app.modals.register(ModalDefinition(
            "busy", ViewNode("busy", "dialog"), dismissible=False,
        ))
        app.open_modal("busy")
        with self.assertRaises(JiuJitsuError):
            app.modals.close()
        app.modals.close(force=True)


if __name__ == "__main__":
    unittest.main()
