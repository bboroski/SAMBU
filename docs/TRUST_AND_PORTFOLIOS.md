# Trust evidence and portfolio verification

SAMBU's portfolio verifier is a local due-diligence utility for artifact collections.

~~~python
import hashlib
from sambu.trust import PortfolioArtifact, PortfolioVerifier

content = "A project case study"
artifact = PortfolioArtifact(
    identifier="case-study-01",
    title="Case study",
    content=content,
    expected_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
    issuer="approved-review-board",
    evidence_ref="evidence://review/2026-04",
    issued_on="2026-04-01",
    expires_on="2027-04-01",
    weight=1.0,
)
report = PortfolioVerifier(
    {"approved-review-board"},
    as_of="2026-11-09",
).verify("creative-portfolio", [artifact])
print(report.to_dict())
~~~

Each artifact is checked for SHA-256 content integrity, a non-empty evidence reference, a configured trusted-issuer allow-list, valid issue and expiry dates at an explicit evaluation date, unique identifiers, and positive finite weights.

The report returns per-artifact reasons, weighted verification coverage, and an overall verified, partial, or unverified status.

## Security boundary

A matching hash proves only that supplied content matches the supplied digest. An allow-listed issuer is trusted because the host configured that allow-list. This module does not verify legal identity, digital signatures, ownership, financial holdings, wallet balances, or external evidence URLs. Do not treat its percentage as a universal truth score or financial recommendation.

For stronger provenance, add a host-controlled signature-verification provider and an auditable trust-root policy.
