from __future__ import annotations

import unittest
import uuid

from sambu.ecosystem_runtime import (
    BoundedEventBus,
    ContractError,
    decode_envelope,
    encode_envelope,
    validate_resource_descriptor,
)


def envelope(sequence: int = 1) -> dict:
    return {
        "schema_version": "1.0.0",
        "message_id": str(uuid.UUID(int=sequence)),
        "producer": {"module_id": "sambu-core", "version": "0.11.0"},
        "event_type": "runtime.resource.changed",
        "sequence": sequence,
        "occurred_at": "2026-11-11T20:00:00Z",
        "trace": {"correlation_id": str(uuid.UUID(int=42))},
        "payload": {"resource_id": "test-resource", "state": "ready"},
    }


def resource_descriptor() -> dict:
    return {
        "schema_version": "1.0.0",
        "resource_id": str(uuid.UUID(int=17)),
        "resource_type": "memory.arena",
        "owner_module_id": "kloz-platform",
        "lifetime": "session",
        "state": "ready",
        "rights": ["observe", "read"],
        "size_bytes": 4096,
        "alignment_bytes": 16,
        "capabilities": ["memory.fixed-capacity"],
        "metadata": {"region": "caller-owned"},
    }


class RuntimeContractTests(unittest.TestCase):
    def test_canonical_round_trip_preserves_envelope(self):
        source = envelope()
        self.assertEqual(decode_envelope(encode_envelope(source)), source)

    def test_unknown_schema_version_is_rejected(self):
        item = envelope()
        item["schema_version"] = "2.0.0"
        with self.assertRaises(ContractError):
            encode_envelope(item)

    def test_boolean_is_not_accepted_as_sequence_integer(self):
        item = envelope()
        item["sequence"] = True
        with self.assertRaises(ContractError):
            encode_envelope(item)

    def test_timezone_is_required(self):
        item = envelope()
        item["occurred_at"] = "2026-11-11T20:00:00"
        with self.assertRaises(ContractError):
            encode_envelope(item)

    def test_invalid_utf8_and_invalid_json_are_rejected(self):
        for packet in (b"\xff", b"{"):
            with self.assertRaises(ContractError):
                decode_envelope(packet)

    def test_resource_descriptor_validates_and_rejects_bad_alignment(self):
        self.assertEqual(validate_resource_descriptor(resource_descriptor())["size_bytes"], 4096)
        item = resource_descriptor()
        item["alignment_bytes"] = 12
        with self.assertRaises(ContractError):
            validate_resource_descriptor(item)

    def test_resource_descriptor_rejects_unsupported_right(self):
        item = resource_descriptor()
        item["rights"].append("root")
        with self.assertRaises(ContractError):
            validate_resource_descriptor(item)

    def test_bounded_bus_is_fifo_and_rejects_overflow(self):
        bus = BoundedEventBus(capacity=1)
        self.assertTrue(bus.publish(envelope(1)))
        self.assertFalse(bus.publish(envelope(2)))
        self.assertEqual(bus.depth, 1)
        self.assertEqual(bus.receive()["sequence"], 1)
        self.assertIsNone(bus.receive())

    def test_closed_bus_rejects_publication(self):
        bus = BoundedEventBus(capacity=2)
        bus.close()
        with self.assertRaises(RuntimeError):
            bus.publish(envelope())


if __name__ == "__main__":
    unittest.main()
