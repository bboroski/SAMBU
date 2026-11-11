"""Versioned, bounded runtime interoperability primitives.

This module validates metadata and provides a local in-process reference queue.
It does not grant capabilities, authenticate principals, encrypt traffic, access
hardware, or provide a distributed message broker.
"""
from __future__ import annotations

from collections import deque
from datetime import datetime
import json
import re
import threading
import uuid
from typing import Any, Mapping

SCHEMA_VERSION = "1.0.0"
MAX_ENVELOPE_BYTES = 256 * 1024
MAX_METADATA_BYTES = 64 * 1024
MAX_QUEUE_CAPACITY = 65_536
_EVENT_TYPE = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_ALLOWED_RIGHTS = {"observe", "read", "write", "execute", "configure"}
_LIFETIMES = {"call", "session", "process", "persistent", "device"}
_RESOURCE_STATES = {"declared", "ready", "busy", "degraded", "released", "faulted"}


class ContractError(ValueError):
    """Raised when a contract document is malformed or exceeds its budget."""


def _nonempty(value: Any, field: str, max_length: int = 256) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ContractError(f"{field} must be a non-empty string of at most {max_length} characters")


def _uuid(value: Any, field: str) -> None:
    if not isinstance(value, str):
        raise ContractError(f"{field} must be a canonical UUID")
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError) as exc:
        raise ContractError(f"{field} must be a canonical UUID") from exc
    if str(parsed) != value:
        raise ContractError(f"{field} must use canonical UUID formatting")


def _timestamp(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{field} must be an RFC 3339 timestamp with an offset")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"{field} must be an RFC 3339 timestamp with an offset") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ContractError(f"{field} must include a UTC offset")


def _encoded_size(value: Any, field: str, limit: int) -> int:
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise ContractError(f"{field} must contain finite JSON-compatible values") from exc
    if len(encoded) > limit:
        raise ContractError(f"{field} exceeds the {limit}-byte limit")
    return len(encoded)


def validate_envelope(envelope: Any) -> dict[str, Any]:
    """Validate an event envelope and return the original mapping as a dict."""
    if not isinstance(envelope, Mapping):
        raise ContractError("envelope must be an object")
    data = dict(envelope)
    required = {
        "schema_version", "message_id", "producer", "event_type",
        "sequence", "occurred_at", "payload",
    }
    missing = required.difference(data)
    if missing:
        raise ContractError("missing required fields: " + ", ".join(sorted(missing)))
    allowed = required | {"trace", "idempotency_key"}
    unknown = set(data).difference(allowed)
    if unknown:
        raise ContractError("unknown envelope fields: " + ", ".join(sorted(unknown)))
    if data["schema_version"] != SCHEMA_VERSION:
        raise ContractError(f"schema_version must be {SCHEMA_VERSION!r}")
    _uuid(data["message_id"], "message_id")

    producer = data["producer"]
    if not isinstance(producer, Mapping):
        raise ContractError("producer must be an object")
    if set(producer) != {"module_id", "version"}:
        raise ContractError("producer must contain exactly module_id and version")
    _nonempty(producer["module_id"], "producer.module_id", 128)
    _nonempty(producer["version"], "producer.version", 64)

    event_type = data["event_type"]
    if not isinstance(event_type, str) or len(event_type) > 128 or not _EVENT_TYPE.fullmatch(event_type):
        raise ContractError("event_type must be a lowercase dotted event identifier")
    if type(data["sequence"]) is not int or data["sequence"] < 0:
        raise ContractError("sequence must be a non-negative integer")
    _timestamp(data["occurred_at"], "occurred_at")

    payload = data["payload"]
    if not isinstance(payload, Mapping):
        raise ContractError("payload must be an object")
    _encoded_size(payload, "payload", MAX_METADATA_BYTES)

    trace = data.get("trace")
    if trace is not None:
        if not isinstance(trace, Mapping) or set(trace).difference({"correlation_id", "causation_id"}):
            raise ContractError("trace must contain only correlation_id and causation_id")
        for key, value in trace.items():
            _uuid(value, f"trace.{key}")

    if "idempotency_key" in data:
        _nonempty(data["idempotency_key"], "idempotency_key", 128)

    _encoded_size(data, "envelope", MAX_ENVELOPE_BYTES)
    return data


def validate_resource_descriptor(descriptor: Any) -> dict[str, Any]:
    """Validate a portable resource descriptor without interpreting host handles."""
    if not isinstance(descriptor, Mapping):
        raise ContractError("resource descriptor must be an object")
    data = dict(descriptor)
    required = {
        "schema_version", "resource_id", "resource_type", "owner_module_id",
        "lifetime", "state", "rights", "capabilities",
    }
    missing = required.difference(data)
    if missing:
        raise ContractError("missing required fields: " + ", ".join(sorted(missing)))
    allowed = required | {"size_bytes", "alignment_bytes", "metadata", "expires_at"}
    unknown = set(data).difference(allowed)
    if unknown:
        raise ContractError("unknown resource fields: " + ", ".join(sorted(unknown)))
    if data["schema_version"] != SCHEMA_VERSION:
        raise ContractError(f"schema_version must be {SCHEMA_VERSION!r}")
    _uuid(data["resource_id"], "resource_id")
    _nonempty(data["resource_type"], "resource_type", 128)
    _nonempty(data["owner_module_id"], "owner_module_id", 128)
    if not isinstance(data["lifetime"], str) or data["lifetime"] not in _LIFETIMES:
        raise ContractError("unsupported resource lifetime")
    if not isinstance(data["state"], str) or data["state"] not in _RESOURCE_STATES:
        raise ContractError("unsupported resource state")

    rights = data["rights"]
    if not isinstance(rights, list) or any(not isinstance(right, str) for right in rights):
        raise ContractError("rights must be a list of string permissions")
    if len(rights) != len(set(rights)):
        raise ContractError("rights must contain unique permissions")
    if any(right not in _ALLOWED_RIGHTS for right in rights):
        raise ContractError("rights contains an unsupported permission")

    capabilities = data["capabilities"]
    if not isinstance(capabilities, list) or any(not isinstance(item, str) for item in capabilities):
        raise ContractError("capabilities must be a list of string identifiers")
    if len(capabilities) != len(set(capabilities)):
        raise ContractError("capabilities must contain unique identifiers")
    for capability in capabilities:
        _nonempty(capability, "capability", 128)

    if "size_bytes" in data and (type(data["size_bytes"]) is not int or data["size_bytes"] < 0):
        raise ContractError("size_bytes must be a non-negative integer")
    if "alignment_bytes" in data:
        alignment = data["alignment_bytes"]
        if type(alignment) is not int or alignment < 1 or alignment & (alignment - 1):
            raise ContractError("alignment_bytes must be a positive power of two")
    if "metadata" in data:
        if not isinstance(data["metadata"], Mapping):
            raise ContractError("metadata must be an object")
        _encoded_size(data["metadata"], "metadata", MAX_METADATA_BYTES)
    if "expires_at" in data:
        _timestamp(data["expires_at"], "expires_at")
    _encoded_size(data, "resource descriptor", MAX_METADATA_BYTES)
    return data


def encode_envelope(envelope: Any) -> bytes:
    """Validate and serialize one envelope using canonical UTF-8 JSON."""
    validated = validate_envelope(envelope)
    try:
        result = json.dumps(
            validated, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError) as exc:
        raise ContractError("envelope cannot be serialized as finite JSON") from exc
    if len(result) > MAX_ENVELOPE_BYTES:
        raise ContractError("encoded envelope exceeds the byte limit")
    return result


def decode_envelope(packet: bytes | bytearray | memoryview) -> dict[str, Any]:
    """Decode one bounded UTF-8 JSON packet and validate its envelope."""
    if not isinstance(packet, (bytes, bytearray, memoryview)):
        raise ContractError("packet must be bytes-like")
    raw = bytes(packet)
    if len(raw) > MAX_ENVELOPE_BYTES:
        raise ContractError("packet exceeds the byte limit")
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("packet must be valid UTF-8 JSON") from exc
    return validate_envelope(decoded)


class BoundedEventBus:
    """FIFO local event queue with atomic publish and explicit backpressure.

    This is an in-process primitive only. It does not provide cross-process or
    network delivery, authentication, encryption, persistence, or exactly-once
    semantics. A full queue rejects the new event without overwriting old data.
    """

    def __init__(self, capacity: int = 128) -> None:
        if type(capacity) is not int or not 1 <= capacity <= MAX_QUEUE_CAPACITY:
            raise ValueError(f"capacity must be an integer between 1 and {MAX_QUEUE_CAPACITY}")
        self._capacity = capacity
        self._queue: deque[bytes] = deque()
        self._lock = threading.Lock()
        self._closed = False

    def publish(self, envelope: Any) -> bool:
        packet = encode_envelope(envelope)
        with self._lock:
            if self._closed:
                raise RuntimeError("event bus is closed")
            if len(self._queue) >= self._capacity:
                return False
            self._queue.append(packet)
            return True

    def receive(self) -> dict[str, Any] | None:
        with self._lock:
            if not self._queue:
                return None
            packet = self._queue.popleft()
        return decode_envelope(packet)

    def close(self) -> None:
        with self._lock:
            self._closed = True

    @property
    def depth(self) -> int:
        with self._lock:
            return len(self._queue)

    @property
    def capacity(self) -> int:
        return self._capacity
