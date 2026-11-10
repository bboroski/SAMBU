# Federated reliability model

SAMBU remains the language, modeling and workflow environment. This document maps system-wide reliability principles to the mechanisms that already belong in this runtime.

## Ownership and coordination

- Language execution, scientific models, spatial data and editor workflows remain separate domains with explicit interfaces.
- Cross-domain relationships are represented as typed data and evidence references, not inferred from naming conventions.
- Capability admission and risk limits stay in `TaskManifest` and `AutonomyPolicy`; a task cannot expand its own authority.
- `ExperimentLedger` provides bounded append-only observations with deterministic hash chaining. It is an integrity record, not an identity or signature service.

## Evidence and recovery

- `PortfolioVerifier` validates content hashes, issuer allow-lists, evidence references and validity dates. It does not authenticate an issuer.
- Deterministic seeds, bounded resource budgets and reproducible workflow plans make experiments repeatable.
- Failed or incomplete evidence remains explicitly unverified; percentage scores must not be presented as proof of correctness.
- High-impact ecosystem decisions are evaluated by Klipot; SAMBU does not merge, deploy or grant external permissions.

## Verification gate

Run `python -m pytest` and `python one.py check`. A passing host test proves only the covered software behavior; native compiler and platform integrations retain their own qualification gates.
