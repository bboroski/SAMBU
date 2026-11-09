# SAMBU workflow, trust and batch primitives

This module gives SAMBU deterministic data models for gifting, evidence-linked reports, accreditation records, relationship graphs, proposal scoring, safe batch plans, syntax inspection and pattern mining. It does not send payments or gifts, issue credentials, make factual accusations, run parallel jobs, or access external systems.

## Trait and OOP foundation

Traits, interfaces, abstract/final classes, visibility, static members and explicit conflict checks already exist in the object model. See `docs/GAMES_AND_OOP.md`. A trait is reusable implementation, not a security boundary.

## Gifting

- `gift_transfer(gift_id, giver, recipient, amount, balances)`
- `gift_batch(transfers, balances)`

Balances use `[[owner, amount], ...]`. Transfers use `[gift_id, giver, recipient, amount]`. The entire batch is validated before a preview result is produced. Duplicate IDs within the batch, self-gifts, missing accounts and insufficient balances are rejected. Results include stable idempotency keys and updated preview balances. Persistent storage and external transfer settlement are deliberately not claimed.

## Accreditation

- `accreditation_record(subject, standard, issuer, issued_on, expires_on, evidence, verified)`
- `accreditation_status(record, as_of)`

Dates use ISO `YYYY-MM-DD`. Verification must be explicit; an evidence reference is not itself proof that an accreditor is legitimate. Status evaluation is deterministic for an explicitly supplied `as_of` date. This is a credential-record model, not a recognized accreditation authority or legal certification.

## Associated entities and signal reports

- `associate(source, target, relation, evidence, confidence, verified=false)`
- `signal_report(reporter, subject, category, claim, evidence, severity, confidence=0.5)`

Associations preserve relationship type, evidence and confidence, while explicitly not claiming causation. Signal reports remain `unverified_requires_review`, have no automated finding and trigger no automated action. They are a triage record, not a mechanism for publishing allegations or treating a report as established fact.

## Pitch scoring

`pitch_score(impact, confidence, effort, risk)` returns the transparent formula:

`impact * confidence * (1 - risk) / (1 + effort)`

Every input is a fraction from 0 through 1. The score is a prioritization aid, not an automatic accept/reject decision.

## Blasting, blazing and batch processing

`blast_plan(total_items, chunk_size, max_in_flight, max_attempts=1)` calculates chunk count, bounded concurrency, estimated processing waves and retry safeguards. It is a plan only. Any future executor must add idempotent handlers, back-pressure, cancellation, bounded memory, observability, dead-letter handling and explicit external-effect permissions before doing real work.

## Parsing and hardening

`parse_report(source)` lexes and parses SAMBU source without executing it. A malformed program returns the stable diagnostic code, message and source position; a valid program returns token and top-level statement counts. This is an inspection primitive, not a sandbox or static type checker.

## Mimicry by structure, not copied wording

- `mimic_profile(text)` extracts an abstract signature of line length, approximate syllable movement, rhyme/alliteration density, lexical diversity and punctuation density.
- `mimic_distance(profile, draft)` compares the signature with a new draft using normalized per-feature distance.

The profile deliberately excludes the source wording and does not compare vocabulary. It is a structural aid for rhythm and delivery, not a promise to reproduce an author's identity or a score of artistic quality.

## Mining and cluster glue

- `mine_patterns(text, min_frequency=2)` finds repeated words, adjacent word pairs and approximate spelling-based rhyme families.
- `cluster_glue([[item, [tags...]], ...])` returns deterministic connected components for items whose tag sets overlap transitively.

Both are bounded and deterministic. Text mining uses surface forms, not semantic embeddings; cluster glue uses shared tags, not inferred similarity.

## Limits

- Maximum 100,000 rows for gifting and clustering.
- Maximum 1,000,000 items for a batch plan.
- Maximum 1,000,000 text characters for parsing and mining.
- No network access, money movement, accreditation lookup, public posting, external job execution or hidden background work.
