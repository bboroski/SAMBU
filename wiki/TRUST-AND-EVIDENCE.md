# Trust, evidence and portfolio checks

SAMBU's trust-related tools emphasize explicit evidence references, content integrity, issuer policies and date-aware status. Their outputs must not be treated as broader proof than the model actually provides.

## Content integrity

The portfolio verification layer can compare supplied artifact content against a supplied SHA-256 digest. This can establish whether the bytes currently supplied match the expected digest.

A matching digest does **not** establish:
- who created the artifact;
- who currently owns it;
- whether an issuer is legally recognized;
- whether a credential is genuine in the real world;
- whether a wallet contains funds;
- whether an external URL is trustworthy.

Integrity is not identity.

## Trusted issuer lists

Issuer names are checked against an allow-list configured by the host. This means the host's trust policy is part of the result. An allow-listed label is not independently authenticated by SAMBU.

For stronger provenance, a host application can add a cryptographic signature-verification provider and explicitly governed trust roots.

## Evidence dates and expiry

Evidence-linked records can include issue and expiry dates. Evaluation should use an explicit `as_of` date so the same input produces a deterministic status.

An evidence reference is a pointer to supporting material, not proof that the referenced material is accurate or authoritative.

## Coverage and status

The portfolio report can return:
- per-artifact validation reasons;
- weighted verification coverage;
- an overall verified, partial or unverified status.

The weight is part of the supplied model. It is not a universal truth score, legal conclusion or financial recommendation.

## Workflow records

Related models can store:
- accreditation-like records;
- associations with relation, evidence and confidence fields;
- signal reports requiring human review;
- proposal-priority scores;
- previewed transfer calculations.

These are data and triage models. They do not issue recognized qualifications, publish accusations, send funds or automatically act on allegations.

## Safe use

1. Preserve source evidence and its provenance outside the model.
2. Record who configured trusted issuers and why.
3. Keep evaluation dates explicit.
4. Treat unverified records as unverified.
5. Require human and domain review before high-impact decisions.
6. Never translate a percentage coverage score directly into a legal or financial conclusion.

## Further reading

- [Trust and portfolio reference](../docs/TRUST_AND_PORTFOLIOS.md)
- [Workflow, trust and batch primitives](../docs/workflows.md)
- [Integration and security boundaries](INTEGRATIONS-AND-SECURITY.md)
