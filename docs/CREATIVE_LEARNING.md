# Creative Learning and the Improvement Loop

This guide connects measurable text diagnostics, explicit author choices and repeatable engineering practice. It does not treat writing as an optimization problem with one universal score.

## 1. Creative preference memory

Use `CreativeLearningProfile` only after the author explicitly opts in:

```python
from sambu import CreativeLearningProfile

profile = CreativeLearningProfile(enabled=True)
profile.record_feedback("rhythm", "prefer")
profile.record_feedback("multisyllabic_rhyme", "prefer")
profile.record_feedback("clean_language", "prefer")

print(profile.ranked_preferences())
```

The profile records only aggregate counters for a fixed registry of dimensions. It does not accept text, prompts, raw comments or example passages. It is in-memory by default. Export is explicit:

```python
snapshot = profile.to_json()
restored = CreativeLearningProfile.from_json(snapshot)
assert restored.enabled is False  # loading never resumes collection implicitly
```

Callers must obtain consent before enabling collection and must protect any exported file according to their own storage policy. The profile contains no user identity, but preference patterns can still be personal data in context; do not publish them without permission.

## 2. The creative refinement cycle

Use one meaningful edit per cycle:

1. **Declare intent.** Record the target format, speaker, point of view, register, language mix and constraints that must remain unchanged.
2. **Measure the baseline.** Run `text_profile`, `prosody_profile`, `text_structure_profile` and, for a compact refrain, `hook_profile`.
3. **Choose one hypothesis.** Examples: smooth a crowded line, strengthen an internal rhyme, make a returning phrase develop its meaning, or reduce an unintended register shift.
4. **Produce a candidate.** Preserve source order, signature vocabulary and deliberate deviations. Apply clean-language constraints only when explicitly selected.
5. **Compare evidence.** Re-run the same diagnostics. Compare line count, syllable spread, sound echoes, repetition and section structure; do not assume that increasing every metric improves the work.
6. **Read aloud and decide.** The author accepts, edits or rejects the candidate. A heuristic cannot replace performance or semantic review.
7. **Record an optional preference.** Only after an explicit choice, store a `prefer` or `avoid` vote against one registered dimension.

Keep the original and candidate separate until approval. Every accepted change should have a reason; rejected experiments can still teach the author what not to do without being added to the preference profile.

## 3. Engineering the improvement of improvements

For code and system changes, use a parallel acceptance loop:

- define the baseline workload and measurements;
- propose a small, reviewable change;
- run unit, integration, compatibility and safety tests;
- compare performance and resource use under the same conditions;
- reject a candidate that introduces an unapproved regression;
- keep a reversible patch or rollback path;
- document the measured result and the limits of the measurement.

The existing `EffortAmplification` model in the engineering doctrine can summarize declared metric changes per engineering hour. It is only useful when the workload, hardware, metric definitions and test protocol are comparable. It must not be used to turn unlike tasks into a misleading universal score.

## 4. Hook-building rules in clean language

The default revision order is:

1. natural spoken rhythm and breath length;
2. a clear central image, phrase or proposition;
3. purposeful internal and multisyllabic sound links;
4. a returning anchor that changes meaning or raises the stakes;
5. concise wording and deliberate register control.

Do not force a rhyme on every line. Do not repeat a phrase solely to fill a bar. Do not sacrifice intelligibility for density. Examples and default suggestions in this guide use clean language. A supplied source remains untouched unless the author explicitly asks for a clean-language rewrite.

## 5. Safety and limits

- The preference profile is not model training, embeddings, automatic classification or online adaptation.
- It learns only from explicit aggregate choices supplied by a caller.
- A preference score describes the balance of recorded choices; it is not a probability or confidence estimate.
- Text diagnostics use spelling and structure heuristics. They do not hear a performance, infer lexical stress or prove semantic quality.
- The author remains the final reviewer for meaning, cultural context, legality, licensing and suitability.

A useful system does not merely create more output. It makes each next decision easier to inspect, reproduce and reverse.
