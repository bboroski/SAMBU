"""Bounded continuity cycles and provenance-checked signal admission.

These host-side primitives model lifecycle governance and trust boundaries.
They do not schedule work, execute signal payloads, or grant host capabilities.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
import math
import re
import threading
from typing import Callable, Iterable


class ContinuityError(ValueError):
    """Base error for continuity and signal-governance failures."""


class TransitionDenied(ContinuityError):
    """A lifecycle transition is not permitted by the phase graph."""


class CycleCapacityError(ContinuityError):
    """The configured cycle or event ceiling has been reached."""


class SignalCapacityError(ContinuityError):
    """The bounded signal-decision history has reached capacity."""


_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")
_ZERO_DIGEST = "0" * 64


def _name(value: str, field: str) -> str:
    if not isinstance(value, str) or not _NAME_RE.fullmatch(value.strip()):
        raise ValueError(f"{field} must be a non-empty identifier of at most 128 characters")
    return value.strip()


def _positive_int(value: int, field: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise ValueError(f"{field} must be an integer between 1 and {maximum}")
    return value


def _validate_json(
    value: object, *, depth: int = 0, count: list[int] | None = None,
    max_depth: int = 32, max_items: int = 10_000,
) -> None:
    if count is None:
        count = [0]
    if depth > max_depth:
        raise ValueError(f"payload nesting exceeds the maximum depth of {max_depth}")
    count[0] += 1
    if count[0] > max_items:
        raise ValueError(f"payload exceeds the maximum of {max_items} values")
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("payload numbers must be finite")
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            _validate_json(
                item, depth=depth + 1, count=count,
                max_depth=max_depth, max_items=max_items,
            )
        return
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("payload object keys must be strings")
        for item in value.values():
            _validate_json(
                item, depth=depth + 1, count=count,
                max_depth=max_depth, max_items=max_items,
            )
        return
    raise ValueError(f"unsupported payload value: {type(value).__name__}")


def _canonical_json(
    value: object, *, max_bytes: int, max_depth: int = 32, max_items: int = 10_000,
) -> str:
    _validate_json(value, max_depth=max_depth, max_items=max_items)
    try:
        encoded = json.dumps(
            value, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("payload must be bounded, finite JSON-shaped data") from exc
    if len(encoded.encode("utf-8")) > max_bytes:
        raise ValueError(f"payload exceeds the maximum of {max_bytes} bytes")
    return encoded


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class CyclePhase(str, Enum):
    DORMANT = "dormant"
    OBSERVING = "observing"
    PREPARING = "preparing"
    ACTIVE = "active"
    RECOVERING = "recovering"
    ARCHIVED = "archived"
    HALTED = "halted"


_TRANSITIONS = {
    CyclePhase.DORMANT: {CyclePhase.OBSERVING, CyclePhase.HALTED},
    CyclePhase.OBSERVING: {CyclePhase.PREPARING, CyclePhase.HALTED},
    CyclePhase.PREPARING: {CyclePhase.ACTIVE, CyclePhase.HALTED},
    CyclePhase.ACTIVE: {CyclePhase.RECOVERING, CyclePhase.HALTED},
    CyclePhase.RECOVERING: {
        CyclePhase.ACTIVE, CyclePhase.ARCHIVED, CyclePhase.HALTED,
    },
    CyclePhase.ARCHIVED: {CyclePhase.OBSERVING, CyclePhase.HALTED},
    CyclePhase.HALTED: set(),
}


@dataclass(frozen=True, slots=True)
class CycleEvent:
    sequence: int
    cycle_number: int
    previous_phase: CyclePhase
    next_phase: CyclePhase
    reason: str
    evidence_digest: str | None
    previous_digest: str
    digest: str


class CycleController:
    """A bounded, auditable finite-state lifecycle controller.

    A cycle advances only through explicit transitions. Entering an operational
    or archival phase requires evidence; archiving stores only its digest. The
    controller never invokes handlers or performs the work described by a cycle.
    """

    def __init__(self, *, max_cycles: int = 100, max_events: int = 10_000):
        self.max_cycles = _positive_int(max_cycles, "max_cycles", 1_000_000)
        self.max_events = _positive_int(max_events, "max_events", 1_000_000)
        self._phase = CyclePhase.DORMANT
        self._cycle_number = 1
        self._events: list[CycleEvent] = []

    @property
    def phase(self) -> CyclePhase:
        return self._phase

    @property
    def cycle_number(self) -> int:
        return self._cycle_number

    @property
    def events(self) -> tuple[CycleEvent, ...]:
        return tuple(self._events)

    @property
    def head_digest(self) -> str:
        return self._events[-1].digest if self._events else _ZERO_DIGEST

    @property
    def archive_digest(self) -> str | None:
        if self._phase is not CyclePhase.ARCHIVED or not self._events:
            return None
        event = self._events[-1]
        return event.evidence_digest if event.next_phase is CyclePhase.ARCHIVED else None

    def transition(
        self,
        next_phase: CyclePhase | str,
        reason: str,
        *,
        evidence: object | None = None,
    ) -> CycleEvent:
        try:
            target = next_phase if isinstance(next_phase, CyclePhase) else CyclePhase(next_phase)
        except (TypeError, ValueError) as exc:
            raise TransitionDenied("unknown lifecycle phase") from exc
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 512:
            raise ValueError("reason must be a non-empty string of at most 512 characters")
        if target not in _TRANSITIONS[self._phase]:
            raise TransitionDenied(
                f"transition {self._phase.value!r} -> {target.value!r} is not permitted"
            )
        if len(self._events) >= self.max_events:
            raise CycleCapacityError("cycle event capacity reached")

        evidence_digest = None
        if evidence is not None:
            evidence_json = _canonical_json(evidence, max_bytes=262_144)
            evidence_digest = _digest(evidence_json)
        evidence_required = target in {
            CyclePhase.OBSERVING, CyclePhase.PREPARING,
            CyclePhase.ACTIVE, CyclePhase.ARCHIVED,
        }
        if evidence_required and evidence_digest is None:
            raise TransitionDenied(
                f"evidence is required before entering {target.value!r}"
            )

        next_cycle = self._cycle_number
        if self._phase is CyclePhase.ARCHIVED and target is CyclePhase.OBSERVING:
            if self._cycle_number >= self.max_cycles:
                raise CycleCapacityError("maximum lifecycle cycle count reached")
            next_cycle += 1

        previous_digest = self.head_digest
        payload = {
            "sequence": len(self._events) + 1,
            "cycle_number": next_cycle,
            "previous_phase": self._phase.value,
            "next_phase": target.value,
            "reason": reason.strip(),
            "evidence_digest": evidence_digest,
            "previous_digest": previous_digest,
        }
        event_digest = _digest(json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ))
        event = CycleEvent(
            sequence=payload["sequence"],
            cycle_number=next_cycle,
            previous_phase=self._phase,
            next_phase=target,
            reason=payload["reason"],
            evidence_digest=evidence_digest,
            previous_digest=previous_digest,
            digest=event_digest,
        )
        self._events.append(event)
        self._phase = target
        self._cycle_number = next_cycle
        return event

    def verify(self) -> bool:
        """Validate event order, legal transitions and the complete hash chain."""
        previous = _ZERO_DIGEST
        phase = CyclePhase.DORMANT
        cycle_number = 1
        if len(self._events) > self.max_events:
            return False
        for expected_sequence, event in enumerate(self._events, start=1):
            if event.sequence != expected_sequence or event.previous_digest != previous:
                return False
            if event.previous_phase is not phase or event.next_phase not in _TRANSITIONS[phase]:
                return False
            if phase is CyclePhase.ARCHIVED and event.next_phase is CyclePhase.OBSERVING:
                cycle_number += 1
            if event.cycle_number != cycle_number or cycle_number > self.max_cycles:
                return False
            evidence_required = event.next_phase in {
                CyclePhase.OBSERVING, CyclePhase.PREPARING,
                CyclePhase.ACTIVE, CyclePhase.ARCHIVED,
            }
            if evidence_required and event.evidence_digest is None:
                return False
            if event.evidence_digest is not None and not re.fullmatch(
                r"[0-9a-f]{64}", event.evidence_digest
            ):
                return False
            payload = {
                "sequence": event.sequence,
                "cycle_number": event.cycle_number,
                "previous_phase": event.previous_phase.value,
                "next_phase": event.next_phase.value,
                "reason": event.reason,
                "evidence_digest": event.evidence_digest,
                "previous_digest": previous,
            }
            expected = _digest(json.dumps(
                payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            ))
            if not hmac.compare_digest(expected, event.digest):
                return False
            phase = event.next_phase
            previous = event.digest
        return phase is self._phase and cycle_number == self._cycle_number


@dataclass(frozen=True, slots=True)
class SignalEnvelope:
    """Immutable, canonical signal metadata; payload access returns a fresh copy."""

    issuer: str
    sequence: int
    payload_json: str
    payload_digest: str
    signature: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "issuer", _name(self.issuer, "issuer"))
        _positive_int(self.sequence, "sequence", 2**63 - 1)
        if not isinstance(self.payload_json, str):
            raise TypeError("payload_json must be a string")
        if len(self.payload_json.encode("utf-8")) > 1_048_576:
            raise ValueError("payload exceeds the absolute 1 MiB envelope limit")
        try:
            decoded = json.loads(self.payload_json)
        except (TypeError, ValueError) as exc:
            raise ValueError("payload_json must contain valid JSON") from exc
        canonical = _canonical_json(decoded, max_bytes=1_048_576)
        if canonical != self.payload_json:
            raise ValueError("payload_json must use canonical JSON encoding")
        if not isinstance(self.payload_digest, str) or not re.fullmatch(
            r"[0-9a-f]{64}", self.payload_digest
        ):
            raise ValueError("payload_digest must be a lowercase SHA-256 digest")
        if not hmac.compare_digest(_digest(canonical), self.payload_digest):
            raise ValueError("payload digest does not match canonical payload")
        if self.signature is not None and (
            not isinstance(self.signature, str) or not self.signature.strip()
            or len(self.signature) > 8_192
        ):
            raise ValueError("signature must be absent or a non-empty string of at most 8192 characters")

    @classmethod
    def create(
        cls,
        issuer: str,
        sequence: int,
        payload: object,
        *,
        signature: str | None = None,
        max_payload_bytes: int = 65_536,
    ) -> "SignalEnvelope":
        _positive_int(max_payload_bytes, "max_payload_bytes", 1_048_576)
        encoded = _canonical_json(payload, max_bytes=max_payload_bytes)
        return cls(
            issuer=issuer,
            sequence=sequence,
            payload_json=encoded,
            payload_digest=_digest(encoded),
            signature=signature,
        )

    @property
    def payload(self) -> object:
        return json.loads(self.payload_json)


class SignalDisposition(str, Enum):
    ACCEPTED = "accepted"
    QUARANTINED = "quarantined"


@dataclass(frozen=True, slots=True)
class SignalDecision:
    issuer: str
    sequence: int
    disposition: SignalDisposition
    reason: str
    payload_digest: str
    authenticated: bool

    @property
    def accepted(self) -> bool:
        return self.disposition is SignalDisposition.ACCEPTED


SignatureVerifier = Callable[[str, int, str, str], bool]


class SignalGuard:
    """Fail-closed signal admission with issuer, signature and replay checks.

    Signatures are verified only by an injected, externally reviewed provider.
    Accepted payloads are data: this class never executes them or grants access.
    Decisions and per-issuer sequence cursors are held in memory only.
    """

    def __init__(
        self,
        allowed_issuers: Iterable[str],
        *,
        signature_verifier: SignatureVerifier | None = None,
        require_authentication: bool = True,
        max_payload_bytes: int = 65_536,
        max_decisions: int = 10_000,
    ):
        if isinstance(allowed_issuers, (str, bytes)):
            raise TypeError("allowed_issuers must be an iterable of issuer identifiers")
        issuers = frozenset(_name(item, "issuer") for item in allowed_issuers)
        if not issuers:
            raise ValueError("allowed_issuers must not be empty")
        if signature_verifier is not None and not callable(signature_verifier):
            raise TypeError("signature_verifier must be callable")
        if not isinstance(require_authentication, bool):
            raise TypeError("require_authentication must be a boolean")
        self.allowed_issuers = issuers
        self.signature_verifier = signature_verifier
        self.require_authentication = require_authentication
        self.max_payload_bytes = _positive_int(
            max_payload_bytes, "max_payload_bytes", 1_048_576
        )
        self.max_decisions = _positive_int(max_decisions, "max_decisions", 1_000_000)
        self._last_sequence: dict[str, int] = {}
        self._decisions: list[SignalDecision] = []
        self._lock = threading.RLock()

    @property
    def decisions(self) -> tuple[SignalDecision, ...]:
        with self._lock:
            return tuple(self._decisions)

    @property
    def sequence_cursors(self) -> dict[str, int]:
        with self._lock:
            return dict(self._last_sequence)

    def accept(self, envelope: SignalEnvelope) -> SignalDecision:
        if not isinstance(envelope, SignalEnvelope):
            raise TypeError("accept() requires a SignalEnvelope")
        with self._lock:
            if len(self._decisions) >= self.max_decisions:
                raise SignalCapacityError("signal decision history capacity reached")

            reason = "accepted"
            authenticated = False
            encoded = envelope.payload_json
            try:
                decoded = json.loads(encoded)
                canonical = _canonical_json(decoded, max_bytes=self.max_payload_bytes)
                if canonical != encoded:
                    reason = "payload_not_canonical"
                elif not hmac.compare_digest(_digest(canonical), envelope.payload_digest):
                    reason = "payload_digest_mismatch"
            except (TypeError, ValueError, RecursionError):
                reason = "payload_invalid_or_too_large"

            if reason == "accepted" and envelope.issuer not in self.allowed_issuers:
                reason = "issuer_not_allowed"
            if reason == "accepted":
                last = self._last_sequence.get(envelope.issuer, 0)
                if envelope.sequence <= last:
                    reason = "replay_or_out_of_order"
            if reason == "accepted":
                if envelope.signature is None:
                    if self.require_authentication:
                        reason = "signature_required"
                elif self.signature_verifier is None:
                    reason = "signature_verifier_unavailable"
                else:
                    try:
                        verification_result = self.signature_verifier(
                            envelope.issuer, envelope.sequence,
                            envelope.payload_digest, envelope.signature,
                        )
                        authenticated = verification_result is True
                        if not authenticated:
                            reason = "signature_invalid"
                    except Exception:
                        reason = "signature_verifier_error"
            if reason == "accepted":
                self._last_sequence[envelope.issuer] = envelope.sequence
                disposition = SignalDisposition.ACCEPTED
            else:
                disposition = SignalDisposition.QUARANTINED
                authenticated = False

            decision = SignalDecision(
                issuer=envelope.issuer,
                sequence=envelope.sequence,
                disposition=disposition,
                reason=reason,
                payload_digest=envelope.payload_digest,
                authenticated=authenticated,
            )
            self._decisions.append(decision)
            return decision
