# Cross-Substrate Semantic API (CSSA)

**Status:** proposed, reviewable contract; not a claim of BCI, neural decoding, memory transfer, or hardware qualification.

## Purpose

Provide a versioned, platform-neutral contract for exchanging typed digital events, semantic entities, declared intents, and capability metadata across independently implemented modules. The API is an interoperability layer, not a mechanism for connecting to or controlling a biological nervous system.

## Core envelope

Every message uses this logical shape:

```json
{
  "contract": "cssa.event",
  "version": "1.0.0",
  "message_id": "opaque-unique-id",
  "correlation_id": "optional-opaque-id",
  "occurred_at": "RFC3339 timestamp",
  "producer": { "id": "module-id", "version": "semver" },
  "subject": { "type": "domain-qualified-type", "id": "opaque-id" },
  "kind": "event | intent | observation | capability",
  "schema": "urn:cssa:schema:example:1",
  "payload": {},
  "provenance": { "source": "declared-source", "integrity": "unverified" }
}
```

The envelope is transport-neutral. Adapters may map it to JSON/HTTP, message queues, gRPC/Protobuf, local IPC, or embedded C ABI without changing its semantic meaning.

## Required operations

Implementations expose equivalent operations in their native language; names may follow local conventions:

- `cssa_validate(envelope, schema_registry)` — reject malformed envelopes, unsupported major versions, invalid timestamps, unknown required fields, and payload/schema mismatches.
- `cssa_negotiate(local_capabilities, remote_capabilities)` — return the explicit intersection of supported contract versions, encodings, message kinds, size limits, and optional features.
- `cssa_normalize(input, mapping_profile)` — map an input into a declared canonical vocabulary while preserving the original value and mapping provenance; never infer hidden mental states.
- `cssa_authorize(principal, action, resource, policy)` — deny by default and require explicit permission for every operation.
- `cssa_publish(envelope, delivery_policy)` — publish only validated messages; report accepted/rejected/queued state and preserve correlation IDs.
- `cssa_migrate(envelope, source_version, target_version)` — perform explicit, deterministic migrations; never silently reinterpret or discard unknown required data.

## Semantic graph

Represent concepts as stable identifiers with typed, directed relationships. Each node and edge carries vocabulary/version, provenance, confidence (when evidence-derived), and optional validity interval. Confidence is metadata, not proof. Unknown concepts remain opaque extensions; consumers must preserve them when forwarding.

## Security and privacy

- No raw neural, biometric, health, or memory data is required or assumed.
- Do not use neural or behavioral patterns as sole authentication factors.
- Authenticate software principals using established cryptographic credentials; authorize each action separately.
- Minimize payloads, encrypt transport/storage where applicable, redact secrets from logs, and define retention limits.
- Treat all external payloads as untrusted; enforce size, depth, rate, and replay limits.
- Never execute an intent directly: map it to an allowlisted action, validate parameters, require authorization, and retain an audit record.
- Use explicit consent and revocation for any future sensitive-signal adapter; keep such adapters disabled unless independently reviewed and legally/ethically approved.

## Latency and delivery semantics

Do not promise microsecond end-to-end latency without target measurements. Define per-adapter budgets, monotonic timing for local durations, bounded queues, backpressure, cancellation, and observable timeout behavior. State delivery guarantees explicitly (best-effort, at-most-once, or at-least-once); consumers must be idempotent for retryable delivery.

## Compatibility

Use semantic versioning for the contract: additive optional fields may be minor changes; breaking semantic changes require a new major version. Unknown optional fields must be preserved where practical. Maintain golden fixtures for each supported version and test old-producer/new-consumer plus new-producer/old-consumer combinations.

## Conformance checklist

1. Validate positive and negative envelope fixtures.
2. Test unsupported versions and unknown required fields.
3. Test capability intersection and no-common-version failure.
4. Test deterministic normalization and preservation of source/provenance.
5. Test default-deny authorization, replay rejection, size limits, and redaction.
6. Test ordering, duplicate delivery, retries, cancellation, and backpressure.
7. Run compatibility fixtures across every supported adapter.
8. Report measured latency percentiles and test environment; do not substitute estimates.

## Implementation boundary

This document defines the interoperable contract and acceptance criteria. A repository may claim an operation is implemented only when executable code, tests, and a reproducible CI result exist. Hardware, BCI, neural decoding, memory encoding/transfer, and cross-biological-substrate claims remain out of scope until separately qualified.
