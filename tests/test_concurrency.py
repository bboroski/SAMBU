from __future__ import annotations

import unittest

from sambu.concurrency import (
    Actor, ActorStoppedError, AuthorizationError, ChannelEmptyError,
    ChannelFullError, DualAuthorizationGate, FiberScheduler, MailboxFullError,
    ModuleMetadata, ResourceScope, ResourceScopeError, SchedulerLimitError,
    Supervisor, TypedChannel, sleep_ticks, yield_now,
)


class FiberSchedulerTests(unittest.TestCase):
    def test_round_robin_order_is_deterministic(self):
        scheduler = FiberScheduler(max_tasks=4)
        trace: list[str] = []

        def task(label: str):
            trace.append(label + "1")
            yield yield_now()
            trace.append(label + "2")
            return label

        first = scheduler.spawn(task, "a")
        second = scheduler.spawn(task, "b")
        report = scheduler.run()

        self.assertEqual(trace, ["a1", "b1", "a2", "b2"])
        self.assertEqual(scheduler.result(first), "a")
        self.assertEqual(scheduler.result(second), "b")
        self.assertEqual(report.completed, 2)
        self.assertFalse(report.budget_exhausted)

    def test_sleep_uses_logical_ticks_without_blocking(self):
        scheduler = FiberScheduler()
        trace: list[tuple[str, int]] = []

        def task():
            trace.append(("start", scheduler.logical_tick))
            yield sleep_ticks(3)
            trace.append(("awake", scheduler.logical_tick))

        scheduler.spawn(task)
        report = scheduler.run()
        self.assertEqual([name for name, _ in trace], ["start", "awake"])
        self.assertGreaterEqual(trace[1][1] - trace[0][1], 3)
        self.assertEqual(report.completed, 1)

    def test_task_failure_is_contained_and_reported(self):
        scheduler = FiberScheduler()

        def broken():
            yield yield_now()
            raise RuntimeError("fiber fault")

        handle = scheduler.spawn(broken)
        report = scheduler.run()
        self.assertEqual(report.failed, 1)
        self.assertEqual(scheduler.snapshot(handle)["status"], "failed")
        with self.assertRaisesRegex(RuntimeError, "fiber fault"):
            scheduler.result(handle)

    def test_task_and_scheduler_budgets_are_enforced(self):
        scheduler = FiberScheduler(max_tasks=1, max_total_steps=2)

        def endless():
            while True:
                yield yield_now()

        handle = scheduler.spawn(endless, step_limit=1)
        scheduler.run()
        self.assertEqual(scheduler.snapshot(handle)["status"], "failed")
        self.assertIn("budget", str(scheduler.snapshot(handle)["error"]))

        other = FiberScheduler(max_tasks=1)
        other.spawn(endless)
        with self.assertRaises(SchedulerLimitError):
            other.spawn(endless)


class ActorTests(unittest.TestCase):
    def test_mailbox_is_bounded_fifo_and_state_is_serialized(self):
        actor = Actor(lambda state, message: state + message, 0, mailbox_capacity=2)
        self.assertEqual(actor.send(2), 1)
        self.assertEqual(actor.send(3), 2)
        with self.assertRaises(MailboxFullError):
            actor.send(4)

        report = actor.drain(max_messages=2)
        self.assertEqual(report["processed"], 2)
        self.assertEqual(actor.snapshot().state, 5)
        self.assertEqual(actor.snapshot().processed, 2)

    def test_failed_message_does_not_commit_partial_state(self):
        def mutate_then_fail(state, message):
            state["items"].append(message)
            if message == "bad":
                raise RuntimeError("rejected")
            return state

        actor = Actor(mutate_then_fail, {"items": []})
        actor.send("bad")
        report = actor.drain()
        self.assertEqual(report["status"], "failed")
        self.assertEqual(actor.snapshot().state, {"items": []})
        self.assertEqual(len(actor.dead_letters), 1)
        with self.assertRaises(ActorStoppedError):
            actor.send("later")

    def test_actor_payloads_are_bounded_and_json_shaped(self):
        actor = Actor(lambda state, message: state, 0, max_payload_bytes=12)
        with self.assertRaises(ValueError):
            actor.send("x" * 100)
        with self.assertRaises(TypeError):
            actor.send(object())


    def test_actor_drain_cannot_be_reentered_from_its_handler(self):
        holder: dict[str, Actor] = {}

        def reentrant(state, message):
            holder["actor"].drain()
            return state

        actor = Actor(reentrant, 0)
        holder["actor"] = actor
        actor.send("trigger")
        report = actor.drain()
        self.assertEqual(report["status"], "failed")
        self.assertIn("cannot re-enter", actor.snapshot().last_error or "")


class SupervisorTests(unittest.TestCase):
    def test_one_for_one_restarts_only_failed_actor(self):
        def handler(state, message):
            if message == "panic":
                raise RuntimeError("actor crash")
            return state + message

        first = Actor(handler, 10, name="first")
        second = Actor(lambda state, message: state + message, 20, name="second")
        supervisor = Supervisor(strategy="one_for_one", max_restarts=2)
        supervisor.supervise(first)
        supervisor.supervise(second)

        first.send("panic")
        first.drain()

        self.assertEqual(first.status, "active")
        self.assertEqual(first.snapshot().state, 10)
        self.assertEqual(first.generation, 1)
        self.assertEqual(second.generation, 0)
        self.assertEqual(supervisor.snapshot()["restarts_in_window"], 1)

    def test_rest_for_one_restarts_failed_and_following_children(self):
        def crash(state, message):
            raise RuntimeError("stop")

        def fail(state, message):
            raise RuntimeError("stop")

        actors = [
            Actor(lambda state, message: state, 0, name="worker-0"),
            Actor(fail, 1, name="worker-1"),
            Actor(lambda state, message: state, 2, name="worker-2"),
        ]
        supervisor = Supervisor(strategy="rest_for_one", max_restarts=3)
        for actor in actors:
            supervisor.supervise(actor)
        actors[1].send("fault")
        actors[1].drain()

        self.assertEqual([actor.generation for actor in actors], [0, 1, 1])

    def test_restart_budget_escalates_to_parent_supervisor(self):
        actor = Actor(lambda state, message: (_ for _ in ()).throw(RuntimeError("x")), 0)
        child = Supervisor(name="child", max_restarts=0)
        child.supervise(actor)
        parent = Supervisor(name="root", max_restarts=1)
        parent.supervise(child)

        actor.send("fail")
        actor.drain()

        self.assertEqual(parent.status, "active")
        self.assertEqual(child.status, "active")
        self.assertEqual(actor.status, "active")
        self.assertEqual(actor.generation, 1)

    def test_supervision_tree_rejects_cycles_and_multiple_parents(self):
        root = Supervisor(name="root")
        branch = Supervisor(name="branch")
        root.supervise(branch)
        with self.assertRaises(ValueError):
            branch.supervise(root)
        with self.assertRaises(ValueError):
            Supervisor(name="other").supervise(branch)


class TypedChannelTests(unittest.TestCase):
    def test_channel_checks_type_capacity_and_fifo(self):
        channel = TypedChannel("integer", capacity=2)
        channel.send(10)
        channel.send(20)
        with self.assertRaises(ChannelFullError):
            channel.send(30)
        self.assertEqual(channel.receive(), 10)
        self.assertEqual(channel.receive(), 20)
        with self.assertRaises(ChannelEmptyError):
            channel.receive()
        with self.assertRaises(TypeError):
            channel.send(True)


class ResourceAndTrustTests(unittest.TestCase):
    def test_resource_scope_closes_in_reverse_order_and_once(self):
        events: list[str] = []

        class Resource:
            def __init__(self, name: str):
                self.name = name

            def close(self):
                events.append(self.name)

        scope = ResourceScope()
        first, second = Resource("first"), Resource("second")
        with scope:
            scope.own(first)
            scope.own(second)
        scope.close()
        self.assertEqual(events, ["second", "first"])

    def test_resource_scope_attempts_all_closures_after_failure(self):
        events: list[str] = []
        scope = ResourceScope()
        scope.own(object(), lambda: (_ for _ in ()).throw(RuntimeError("bad")))
        scope.own(object(), lambda: events.append("closed"))
        with self.assertRaises(ResourceScopeError):
            scope.close()
        self.assertEqual(events, ["closed"])

    def test_module_metadata_requires_every_safety_field(self):
        metadata = ModuleMetadata("core", "0.12", "", "ops@example.invalid", "audit")
        self.assertEqual(metadata.validate(), ("owner must be a non-empty string",))
        with self.assertRaises(ValueError):
            metadata.require_valid()
        valid = ModuleMetadata("core", "0.12", "platform", "ops@example.invalid", "audit")
        self.assertIs(valid.require_valid(), valid)

    def test_dual_authorization_requires_independent_verifiers(self):
        gate = DualAuthorizationGate(
            lambda token: token == "local-ok",
            lambda token: token == "hardware-ok",
        )
        self.assertTrue(gate.authorize("local-ok", "hardware-ok"))
        with self.assertRaises(AuthorizationError):
            gate.authorize("local-ok", "wrong")
        self.assertEqual(gate.authorized_count, 1)
        self.assertEqual(gate.denied_count, 1)


if __name__ == "__main__":
    unittest.main()
