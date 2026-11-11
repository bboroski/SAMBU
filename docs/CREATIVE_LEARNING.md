# Text Signal Analysis and Preference Tuning

This guide connects measurable text diagnostics, explicit parameter choices and repeatable revision workflows. It does not assume that one score can represent overall quality.

## 1. Preference profile

The existing `CreativeLearningProfile` name remains a compatibility API. Enable collection only after explicit opt-in:

```python
from sambu import CreativeLearningProfile

profile = CreativeLearningProfile(enabled=True)
profile.record_feedback("rhythm", "prefer")
profile.record_feedback("multisyllabic_rhyme", "prefer")
profile.record_feedback("clean_language", "prefer")
print(profile.ranked_preferences())
```

The profile stores aggregate counters for a fixed dimension registry. It does not accept raw source text, prompts, comments or example passages. State is in-memory by default; export is explicit:

```python
snapshot = profile.to_json()
restored = CreativeLearningProfile.from_json(snapshot)
assert restored.enabled is False
```

Obtain consent before enabling collection. Protect exported profiles under the caller's storage policy. Aggregate preference patterns may still be sensitive in context and must not be published without permission.

## 2. Revision cycle

Apply one measurable change per cycle:

1. **Declare constraints:** target format, language, register and invariants.
2. **Measure baseline:** run `text_profile`, `prosody_profile`, `text_structure_profile` and, where relevant, `hook_profile`.
3. **Select a hypothesis:** reduce local density, improve phonetic alignment, clarify repeated segments or normalize register transitions.
4. **Generate a candidate:** preserve source order and declared constraints; keep the source snapshot immutable.
5. **Compare metrics:** line count, syllable distribution, phonetic overlap, repetition and segment structure. Do not optimize every metric simultaneously.
6. **Review output:** the operator accepts, adjusts or rejects the candidate. Heuristic metrics do not prove semantic correctness.
7. **Record an optional preference:** store one explicit `prefer` or `avoid` value for a registered dimension.

Keep source and candidate snapshots separate until approval. Rejected candidates may be retained as test evidence only when the caller's data policy permits it.

## 3. Engineering change loop

For code and system revisions, use the same bounded process:

- define baseline workload and measurements;
- propose a small, reviewable change;
- run unit, integration, compatibility and safety tests;
- compare performance and resource use under equivalent conditions;
- reject unapproved regressions;
- preserve a reversible patch or rollback path;
- record results and measurement limits.

The `EffortAmplification` model can summarize declared metric change per engineering hour. Compare only equivalent workloads, hardware, metric definitions and test protocols; do not convert unlike tasks into a universal score.

## 4. Signal-quality constraints

Prioritize intelligibility, controlled repetition, segment continuity and explicit register selection. Do not force a pattern merely to increase density, and do not optimize a proxy metric at the expense of the declared output constraints.

## 5. Safety and limits

- The preference profile is not model training, embedding generation, automatic classification or online adaptation.
- It learns only from explicit aggregate choices supplied by a caller.
- A preference score summarizes recorded choices; it is not a probability or confidence estimate.
- Text diagnostics use spelling and structure heuristics. They do not prove semantic quality or replace domain review.
- The content owner remains responsible for meaning, source context, licensing and suitability.

The goal is not maximal output volume. It is a revision process that is inspectable, reproducible and reversible.
