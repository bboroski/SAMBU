"""Evidence and integrity checks for digital portfolios.

Verification checks supplied hashes, issuer allow-lists, evidence references, and
dates. It does not prove identity, signatures, or issuer authenticity.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import date
import hashlib
import math
import re
from typing import Iterable

@dataclass(frozen=True, slots=True)
class PortfolioArtifact:
    identifier: str
    title: str
    content: str
    expected_sha256: str
    issuer: str
    evidence_ref: str
    issued_on: str
    expires_on: str | None = None
    weight: float = 1.0

@dataclass(frozen=True, slots=True)
class ArtifactVerification:
    identifier: str
    verified: bool
    actual_sha256: str
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

@dataclass(frozen=True, slots=True)
class PortfolioVerification:
    portfolio_id: str
    status: str
    is_verified: bool
    trust_percent: float
    verified_weight: float
    total_weight: float
    artifacts: tuple[ArtifactVerification, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "portfolio_id": self.portfolio_id, "status": self.status,
            "is_verified": self.is_verified, "trust_percent": self.trust_percent,
            "verified_weight": self.verified_weight, "total_weight": self.total_weight,
            "artifacts": [item.to_dict() for item in self.artifacts],
        }

def _iso_date(value: str, field: str) -> date:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date string")
    if not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", value):
        raise ValueError(f"{field} must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must use a valid YYYY-MM-DD date") from exc

class PortfolioVerifier:
    """Verify artifact integrity and provenance against an explicit trust policy."""

    def __init__(self, trusted_issuers: Iterable[str], *, as_of: str | date):
        self.trusted_issuers = frozenset(
            issuer.strip().casefold() for issuer in trusted_issuers
            if isinstance(issuer, str) and issuer.strip()
        )
        self.as_of = as_of if isinstance(as_of, date) else _iso_date(as_of, "as_of")

    def verify(self, portfolio_id: str, artifacts: Iterable[PortfolioArtifact]) -> PortfolioVerification:
        if not isinstance(portfolio_id, str) or not portfolio_id.strip():
            raise ValueError("portfolio_id cannot be empty")
        entries = tuple(artifacts)
        if len(entries) > 10_000:
            raise ValueError("portfolio cannot contain more than 10,000 artifacts")
        seen: set[str] = set()
        results: list[ArtifactVerification] = []
        total_weight = verified_weight = 0.0

        for item in entries:
            if not isinstance(item, PortfolioArtifact):
                raise TypeError("artifacts must contain PortfolioArtifact values")
            reasons: list[str] = []
            identifier = item.identifier if isinstance(item.identifier, str) else ""
            if not identifier.strip():
                reasons.append("missing_identifier")
            elif identifier in seen:
                reasons.append("duplicate_identifier")
            seen.add(identifier)
            content = item.content if isinstance(item.content, str) else ""
            if not isinstance(item.content, str):
                reasons.append("invalid_content")
            actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
            expected = item.expected_sha256.casefold() if isinstance(item.expected_sha256, str) else ""
            if not re.fullmatch(r"[0-9a-f]{64}", expected) or actual != expected:
                reasons.append("content_hash_mismatch")
            issuer = item.issuer.casefold().strip() if isinstance(item.issuer, str) else ""
            if not issuer or issuer not in self.trusted_issuers:
                reasons.append("untrusted_issuer")
            if not isinstance(item.evidence_ref, str) or not item.evidence_ref.strip():
                reasons.append("missing_evidence_reference")
            try:
                issued = _iso_date(item.issued_on, "issued_on")
                if issued > self.as_of:
                    reasons.append("evidence_not_yet_valid")
            except ValueError:
                issued = None
                reasons.append("invalid_issued_on")
            if item.expires_on is not None:
                try:
                    expires = _iso_date(item.expires_on, "expires_on")
                    if issued is not None and expires < issued:
                        reasons.append("expiry_precedes_issue")
                    if expires < self.as_of:
                        reasons.append("evidence_expired")
                except ValueError:
                    reasons.append("invalid_expires_on")
            weight = item.weight
            try:
                numeric_weight = float(weight) if not isinstance(weight, bool) and isinstance(weight, (int, float)) else math.nan
            except (OverflowError, ValueError):
                numeric_weight = math.nan
            if not math.isfinite(numeric_weight) or numeric_weight <= 0:
                reasons.append("invalid_weight")
                effective_weight = 1.0
            else:
                effective_weight = numeric_weight
            next_total_weight = total_weight + effective_weight
            if not math.isfinite(next_total_weight):
                raise ValueError("combined artifact weight exceeds the finite numeric range")
            total_weight = next_total_weight
            verified = not reasons
            if verified:
                verified_weight += effective_weight
            results.append(ArtifactVerification(identifier, verified, actual, tuple(dict.fromkeys(reasons))))
        score = 100.0 * verified_weight / total_weight if total_weight else 0.0
        all_verified = bool(results) and all(item.verified for item in results)
        status = "verified" if all_verified else ("partial" if verified_weight else "unverified")
        return PortfolioVerification(portfolio_id, status, all_verified, score, verified_weight, total_weight, tuple(results))

def trust_dig(portfolio_id: str, artifacts: Iterable[PortfolioArtifact], trusted_issuers: Iterable[str], *, as_of: str | date) -> PortfolioVerification:
    """Convenience entry point for a reproducible due-diligence pass."""
    return PortfolioVerifier(trusted_issuers, as_of=as_of).verify(portfolio_id, artifacts)

__all__ = [
    "PortfolioArtifact", "ArtifactVerification", "PortfolioVerification",
    "PortfolioVerifier", "trust_dig",
]
