"""Policy-gated feature completion; proposal only, never execution or deployment."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json


class PipelineDecision(str, Enum):
    REJECTED = "rejected"
    NEEDS_TESTS = "needs_tests"
    NEEDS_SECURITY_REVIEW = "needs_security_review"
    NEEDS_HUMAN_APPROVAL = "needs_human_approval"
    READY_FOR_PULL_REQUEST = "ready_for_pull_request"


@dataclass(frozen=True, slots=True)
class ChangeProposal:
    title: str
    summary: str
    changed_paths: tuple[str, ...]
    required_tests: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    risk: str = "medium"


@dataclass(frozen=True, slots=True)
class PipelineResult:
    decision: PipelineDecision
    digest: str
    reasons: tuple[str, ...]


class ChangePipeline:
    """Evaluate evidence and policy gates; never runs code or merges a branch."""

    _RISK = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    def __init__(self, *, max_auto_pr_risk: str = "low",
                 protected_roots: tuple[str, ...] = (".github/workflows/", "infra/prod/")) -> None:
        if max_auto_pr_risk not in self._RISK:
            raise ValueError("unknown risk tier")
        self.max_auto_pr_risk = max_auto_pr_risk
        self.protected_roots = protected_roots

    def evaluate(self, proposal: ChangeProposal, *, tests_passed: bool,
                 security_passed: bool, human_approved: bool = False) -> PipelineResult:
        body = {
            "title": proposal.title, "summary": proposal.summary,
            "changed_paths": list(proposal.changed_paths),
            "required_tests": list(proposal.required_tests),
            "evidence_refs": list(proposal.evidence_refs), "risk": proposal.risk,
        }
        digest = hashlib.sha256(json.dumps(
            body, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")).hexdigest()
        reasons: list[str] = []
        if not proposal.title.strip() or not proposal.summary.strip():
            reasons.append("missing_change_description")
        if not proposal.changed_paths:
            reasons.append("no_changed_paths")
        if not proposal.required_tests:
            reasons.append("no_required_tests")
        if not proposal.evidence_refs:
            reasons.append("no_evidence_references")
        if proposal.risk not in self._RISK:
            reasons.append("invalid_risk_tier")
        if any(path.startswith("../") or path.startswith("/") for path in proposal.changed_paths):
            reasons.append("path_traversal_or_absolute_path")
        if reasons:
            return PipelineResult(PipelineDecision.REJECTED, digest, tuple(reasons))
        if not tests_passed:
            return PipelineResult(PipelineDecision.NEEDS_TESTS, digest, ("tests_not_passed",))
        if not security_passed:
            return PipelineResult(PipelineDecision.NEEDS_SECURITY_REVIEW, digest, ("security_gate_not_passed",))
        protected = any(path.startswith(root) for path in proposal.changed_paths
                        for root in self.protected_roots)
        above_ceiling = self._RISK[proposal.risk] > self._RISK[self.max_auto_pr_risk]
        if protected or above_ceiling:
            if not human_approved:
                reason = "protected_path_requires_human_approval" if protected else "risk_exceeds_auto_pr_ceiling"
                return PipelineResult(PipelineDecision.NEEDS_HUMAN_APPROVAL, digest, (reason,))
        return PipelineResult(PipelineDecision.READY_FOR_PULL_REQUEST, digest, ())
