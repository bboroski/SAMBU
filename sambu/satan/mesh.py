"""Authenticated, bounded QEGM-style gossip envelopes.

This is conventional cryptographic message authentication, not quantum
entanglement. Deployments should use authenticated TLS for transport and
independently provision per-node secrets; this module never creates secrets.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
import time
from typing import Mapping

ALLOWED_KINDS = frozenset({
    "repository.registered", "security.finding", "dependency.changed",
    "contract.changed", "artifact.attested", "change.proposed",
})
MAX_PAYLOAD_BYTES = 256 * 1024
MAX_TTL_SECONDS = 7 * 24 * 60 * 60
MAX_HOPS = 32


class MeshError(ValueError):
    """Invalid, unauthenticated, expired, or over-budget mesh message."""


def _canonical(value: object) -> bytes:
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as exc:
        raise MeshError("payload must be finite JSON data") from exc
    if len(raw) > MAX_PAYLOAD_BYTES:
        raise MeshError("message exceeds payload limit")
    return raw


def _mac(secret: bytes, value: object) -> str:
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise MeshError("node secret must contain at least 32 bytes")
    return hmac.new(secret, _canonical(value), hashlib.sha256).hexdigest()


@dataclass(frozen=True, slots=True)
class MeshEnvelope:
    event_id: str
    kind: str
    origin: str
    issued_at: int
    expires_at: int
    payload: dict
    origin_signature: str
    signer: str
    hop_count: int
    previous_digest: str | None
    relay_signature: str

    def to_dict(self) -> dict:
        return asdict(self)

    def digest(self) -> str:
        return hashlib.sha256(_canonical(self.to_dict())).hexdigest()


def _origin_body(event_id: str, kind: str, origin: str, issued_at: int,
                 expires_at: int, payload: dict) -> dict:
    return {
        "event_id": event_id, "kind": kind, "origin": origin,
        "issued_at": issued_at, "expires_at": expires_at, "payload": payload,
    }


def _relay_body(envelope: MeshEnvelope) -> dict:
    value = envelope.to_dict()
    value.pop("relay_signature")
    return value


def create_envelope(*, event_id: str, kind: str, origin: str, payload: dict,
                    secret: bytes, now: int | None = None,
                    ttl_seconds: int = 3600) -> MeshEnvelope:
    if not isinstance(event_id, str) or not event_id or len(event_id) > 128:
        raise MeshError("event_id must be 1..128 characters")
    if kind not in ALLOWED_KINDS:
        raise MeshError("event kind is not allow-listed")
    if not isinstance(origin, str) or not origin or len(origin) > 256:
        raise MeshError("origin must be 1..256 characters")
    if not isinstance(payload, dict):
        raise MeshError("payload must be an object")
    if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
        raise MeshError("ttl_seconds is outside the allowed range")
    issued = int(time.time()) if now is None else now
    if isinstance(issued, bool) or not isinstance(issued, int) or issued < 0:
        raise MeshError("now must be a non-negative integer")
    body = _origin_body(event_id, kind, origin, issued, issued + ttl_seconds, payload)
    origin_sig = _mac(secret, body)
    partial = MeshEnvelope(event_id, kind, origin, issued, issued + ttl_seconds,
                           payload, origin_sig, origin, 0, None, "")
    return MeshEnvelope(event_id, kind, origin, issued, issued + ttl_seconds,
                        payload, origin_sig, origin, 0, None,
                        _mac(secret, _relay_body(partial)))


def forward_envelope(envelope: MeshEnvelope, *, relay: str, secret: bytes,
                     max_hops: int = MAX_HOPS) -> MeshEnvelope:
    if isinstance(max_hops, bool) or not isinstance(max_hops, int) or not 1 <= max_hops <= MAX_HOPS:
        raise MeshError("max_hops must be between 1 and MAX_HOPS")
    if envelope.hop_count >= max_hops:
        raise MeshError("hop limit reached")
    if not isinstance(relay, str) or not relay or len(relay) > 256:
        raise MeshError("relay must be 1..256 characters")
    partial = MeshEnvelope(
        envelope.event_id, envelope.kind, envelope.origin, envelope.issued_at,
        envelope.expires_at, envelope.payload, envelope.origin_signature,
        relay, envelope.hop_count + 1, envelope.digest(), "",
    )
    return MeshEnvelope(
        partial.event_id, partial.kind, partial.origin, partial.issued_at,
        partial.expires_at, partial.payload, partial.origin_signature,
        partial.signer, partial.hop_count, partial.previous_digest,
        _mac(secret, _relay_body(partial)),
    )


def verify_envelope(envelope: MeshEnvelope, *, node_secrets: Mapping[str, bytes],
                    now: int | None = None, max_hops: int = MAX_HOPS) -> bool:
    if not isinstance(envelope, MeshEnvelope):
        raise MeshError("expected MeshEnvelope")
    current = int(time.time()) if now is None else now
    if isinstance(current, bool) or not isinstance(current, int):
        raise MeshError("now must be an integer timestamp")
    if envelope.kind not in ALLOWED_KINDS:
        raise MeshError("event kind is not allow-listed")
    if envelope.expires_at <= current or envelope.issued_at > current + 60:
        raise MeshError("message is expired or issued in the future")
    if envelope.expires_at <= envelope.issued_at or envelope.expires_at - envelope.issued_at > MAX_TTL_SECONDS:
        raise MeshError("invalid message lifetime")
    if isinstance(envelope.hop_count, bool) or not isinstance(envelope.hop_count, int) or not 0 <= envelope.hop_count <= min(max_hops, MAX_HOPS):
        raise MeshError("invalid hop count")
    if envelope.hop_count == 0 and envelope.previous_digest is not None:
        raise MeshError("origin envelope cannot contain a previous digest")
    if envelope.hop_count > 0 and (
        not isinstance(envelope.previous_digest, str)
        or len(envelope.previous_digest) != 64
        or any(c not in "0123456789abcdef" for c in envelope.previous_digest)
    ):
        raise MeshError("relayed envelope must contain a previous SHA-256 digest")
    if envelope.origin not in node_secrets or envelope.signer not in node_secrets:
        raise MeshError("unknown origin or relay")
    origin_body = _origin_body(envelope.event_id, envelope.kind, envelope.origin,
                               envelope.issued_at, envelope.expires_at, envelope.payload)
    if not hmac.compare_digest(_mac(node_secrets[envelope.origin], origin_body),
                               envelope.origin_signature):
        raise MeshError("origin signature mismatch")
    if not hmac.compare_digest(_mac(node_secrets[envelope.signer], _relay_body(envelope)),
                               envelope.relay_signature):
        raise MeshError("relay signature mismatch")
    _canonical(envelope.payload)
    return True
