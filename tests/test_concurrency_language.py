from __future__ import annotations

import unittest

from sambu.interpreter import execute


class SambuConcurrencyBuiltinsTests(unittest.TestCase):
    def test_actor_serializes_messages_in_fifo_order(self):
        output: list[str] = []
        execute("""
fn accumulate(state, message) {
  return state + message
}
let worker = actor(accumulate, 0, 4)
actor_send(worker, 3)
actor_send(worker, 7)
let report = actor_drain(worker, 8)
print(report.processed)
print(actor_state(worker))
""", output=output.append)
        self.assertEqual(output, ["2", "10"])

    def test_supervisor_restarts_failed_actor_and_keeps_failure_visible(self):
        output: list[str] = []
        execute("""
fn guarded(state, message) {
  if (message == 0) {
    return 1 / 0
  }
  return state + message
}
let worker = actor(guarded, 5)
let root = supervisor("one_for_one", 2, 60)
supervise(root, worker)
actor_send(worker, 0)
let failure = actor_drain(worker)
print(failure.status)
print(actor_state(worker))
let status = supervisor_status(root)
print(status.strategy)
print(actor_send(worker, 4).accepted)
actor_drain(worker, 1)
print(actor_state(worker))
""", output=output.append)
        self.assertEqual(output, ["active", "5", "one_for_one", "true", "9"])

    def test_typed_channel_rejects_type_mismatch(self):
        output: list[str] = []
        execute("""
let radio = channel("text", 2)
channel_send(radio, "status")
print(channel_receive(radio))
""", output=output.append)
        self.assertEqual(output, ["status"])

        with self.assertRaises(TypeError):
            execute("""
let power = channel("integer", 1)
channel_send(power, "wrong wire")
""")

    def test_actor_requires_two_parameter_handler(self):
        with self.assertRaises(TypeError):
            execute("""
fn one_argument(value) { return value }
let worker = actor(one_argument, 0)
""")


if __name__ == "__main__":
    unittest.main()
