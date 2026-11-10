# Creative Data Governance and Semantic Metadata

**Current ontology version:** `2026.12`  
**Backward compatibility:** existing `2026.11` records remain readable; `T-009` is available only in `2026.12`.  
**Status:** the metadata model, cluster registry and validator are implemented in Python. Automated text classification, embedding generation, model training and online adaptation are not implemented by this module.

This document defines a versioned, reviewable metadata contract for SAMBU. The bundled examples are synthetic, neutral demonstrations of annotation structure; they are not derived from user-authored poems, lyrics, private drafts or an imported personal corpus.

## 1. Purpose and boundary

SAMBU may convert creative material into structured annotations for search, analysis, translation support and carefully reviewed generation workflows. The metadata layer is descriptive: it does not rewrite source text, infer intent from keywords, decide whether a real-world claim is true, or automatically declare content safe.

The processing boundary is:

`source (user-controlled) → human/approved annotation → schema validation → versioned metadata → downstream consumer`

Raw source text is not part of the metadata schema. A caller may attach a source reference and SHA-256 digest, but must manage the source separately under its own consent, access, retention and licensing rules. A digest identifies bytes; it does not prove provenance, permission or truth.

## 2. Thematic ontology

| ID | Cluster | Stable theme key | Description | Candidate applications |
|---|---|---|---|---|
| T-001 | Celebration and ritual | `cultural_celebration` | Public events, shared activities, recurring calendars and community contexts | Event description, context tagging, schedule annotation |
| T-002 | Identity and transformation | `identity_transformation` | Profile changes, role transitions, representation and lifecycle changes | Profile analysis, entity tracking, state annotation |
| T-003 | Geopolitical awareness | `geopolitical_awareness` | Regions, jurisdictions, institutional structures and geographic context | Entity recognition, regional comparison, context grounding |
| T-004 | Emotional duality | `emotional_duality` | Contrasting states, competing conditions, uncertainty and change over time | State comparison, dialogue analysis, change annotation |
| T-005 | Spiritual syncretism | `spiritual_syncretism` | Symbol systems, inherited conventions, heritage references and cultural classifications | Catalog annotation, symbolic indexing, reference analysis |
| T-006 | Technological metaphor | `technological_metaphor` | Technical systems, software/hardware mappings and digital/physical analogies | Technical writing, system documentation, interface analysis |
| T-007 | Conflict and resilience | `conflict_resilience` | Incidents, constraints, fault handling, continuity and recovery sequences | Incident reporting, operational documentation, recovery analysis |
| T-008 | Linguistic hybridity | `linguistic_hybridity` | Multiple languages, locale switching, terminology variants and mixed registers | Translation assessment, interface localization, terminology analysis |
| T-009 | Surreal juxtaposition and wordplay | `surreal_juxtaposition` | Unexpected associations, ambiguous labels, category mismatches and controlled wordplay | Label review, ambiguity analysis, controlled wordplay annotation |

The cluster is a navigation and analysis label, not a verdict about the source. T-009 was added in ontology `2026.12`; records tagged with it must declare that version. Existing `2026.11` records remain valid and are not silently rewritten. One work may carry more than one cluster in a future multi-label schema; the current record format deliberately assigns one primary cluster so its first implementation remains deterministic.

## 3. Safety and review labels

The validator accepts these explicit labels:

| Label | Meaning | Generation treatment |
|---|---|---|
| `CLEAN` | Reviewed metadata with no unresolved safety concern | Eligible only with `review_ref` and `reviewed_at` evidence |
| `CLEAN_SATIRE` | Satirical material reviewed in context | Eligible only with `review_ref` and `reviewed_at` evidence |
| `SANITIZED_ARGOT_ONLY` | Only neutralized argot descriptors are retained | Not eligible by this label alone |
| `SANITIZED_INTIMACY` | Only neutralized intimacy descriptors are retained | Not eligible by this label alone |
| `NEEDS_REVIEW` | Review has not been completed | Not eligible |
| `EXCLUDED_FROM_GENERATION` | Explicitly withheld from generation workflows | Not eligible |

Eligibility is deliberately conservative and does not replace downstream policy checks. A `CLEAN` or `CLEAN_SATIRE` label alone is not enough: the record must also contain a pseudonymous `review_ref` and a timezone-aware ISO-8601 `reviewed_at` timestamp. These fields provide an auditable review reference, not proof that the source is licensed, truthful or universally safe. The system never infers them automatically. Negative or harmful examples may be used in a separate, access-controlled evaluation set when lawful and appropriate; they must not be silently promoted into generative examples.

Profanity, dialect, political references, religion, sexuality or conflict are not automatically equivalent to harmful content. Review should evaluate meaning, target, context, intent and likely use. Neutral academic discussion and creative expression must not be suppressed merely because they mention a sensitive subject.

## 4. Metadata contract

The Python API is `sambu.creative_metadata.CreativeMetadata`. The record contains:

- `cluster_id`, `theme`, `tone`;
- bounded `key_symbols`, `language` and `stylistic_devices` arrays;
- optional `linguistic_register`, `source_ref`, `content_sha256`, `review_ref` and `reviewed_at`;
- an explicit `safety_flag` and immutable `ontology_version`.

The validator rejects unknown fields, unknown cluster identifiers, unbounded arrays, malformed hashes, invalid review timestamps and unsupported ontology versions. Both review fields must be provided together. Missing safety labels default to `NEEDS_REVIEW`, never to a permissive state. A `2026.11` record cannot use `T-009`. The machine-readable Draft 2020-12 contract is [schemas/creative-metadata.schema.json](../schemas/creative-metadata.schema.json).

Example JSON record (metadata only):

```json
{
  "cluster_id": "T-006",
  "theme": "technological_metaphor",
  "tone": "neutral_explanatory",
  "key_symbols": ["service_request", "queue_state", "cache_entry"],
  "language": ["en"],
  "linguistic_register": "technical_documentation",
  "stylistic_devices": ["process_description", "precise_labeling"],
  "safety_flag": "NEEDS_REVIEW",
  "source_ref": "synthetic-demo-006",
  "ontology_version": "2026.12"
}
```


JSON-LD export uses Schema.org's `CreativeWork` type and adds the SAMBU cluster, tone, safety fields and (when available) review reference/date. It contains metadata, not the original lyric or prose.

## 5. CLI and Python usage

List the registered clusters:

```bash
sambu creative clusters
sambu creative clusters --json
```

Validate a local JSON object or array:

```bash
sambu creative validate examples/creative_metadata.sample.json
sambu creative validate examples/creative_metadata.sample.json --json
```

Use the library API:

```python
from sambu.creative_metadata import CreativeMetadata

record = CreativeMetadata.from_mapping({
    "cluster_id": "T-006",
    "theme": "technological_metaphor",
    "tone": "neutral_explanatory",
    "key_symbols": ["service_request", "queue_state"],
    "language": ["en"],
    "linguistic_register": "technical_documentation",
    "stylistic_devices": ["process_description"],
    "safety_flag": "NEEDS_REVIEW",
})

print(record.to_dict())
print(record.to_jsonld())
```

The tool validates supplied labels. It does not classify unannotated text, generate embeddings, fine-tune Sentence-BERT, or learn from user corrections. Text Craft diagnostics (`text_profile`, `prosody_profile`, `text_structure_profile` and `language_mix_profile`) surface measurable writing patterns but do not assign thematic clusters or safety labels. Keep the layers separate: diagnostics produce evidence; a human curator assigns metadata.

## 6. Synthetic examples and Text Craft crosswalk

The [synthetic metadata fixture](../examples/creative_metadata_examples.sample.json) contains nine compact, source-free records, one per registered cluster. Each record uses neutral examples from ordinary documentation and information systems: event calendars, profile transitions, regional routing, state comparisons, catalog records, service queues, incident recovery, bilingual interface labels and category matching. Every record is marked `NEEDS_REVIEW`; the fixture demonstrates schema shape, not a completed content or safety review.

| Neutral demonstration scenario | SAMBU representation |
|---|---|
| Public event calendar and schedule entry | `T-001` — cultural celebration |
| Account profile and role transition | `T-002` — identity transformation |
| Regional service routing and jurisdiction metadata | `T-003` — geopolitical awareness |
| Before/after status comparison | `T-004` — emotional duality |
| Museum catalog and historical symbol index | `T-005` — spiritual syncretism |
| Service request, queue state and cache entry | `T-006` — technological metaphor |
| Incident ticket and recovery checklist | `T-007` — conflict and resilience |
| Bilingual interface labels and locale fallback | `T-008` — linguistic hybridity |
| Unexpected pairing of unrelated catalog categories | `T-009` — surreal juxtaposition |

Text Craft supplies deterministic, non-semantic signals alongside human annotation: section and repeated-block structure, writing-system counts, approximate syllable and spelling-rhyme patterns, internal echoes, marked casing and explicit written notation. The `performance_cues_profile` function detects stage directions, parenthetical notes, quoted phrases and elongated spellings with source line/column spans. It does not infer emotion, speaker identity or actual vocal delivery.

Validate the synthetic metadata-only fixture:

```bash
sambu creative validate examples/creative_metadata_examples.sample.json --json
sambu examples/performance_cues.sambu
```

The fixture contains no original poems, lyrics, quoted source passages, personal identifiers or generated training vectors. Its `source_ref` values are synthetic fixture identifiers, not references to user material. It is not a training set and does not imply that a human review has occurred. Its `2026.12` records use the current schema; existing `2026.11` records remain readable under the compatibility rules above.


## 7. Opt-in creative preference learning

`CreativeLearningProfile` is a small local preference ledger for iterative writing work. It accepts only explicit choices against a fixed set of dimensions: rhythm, naturalness, internal and multisyllabic rhyme, semantic clarity, refrain development, imagery, language mixing, register control and clean language.

The design deliberately avoids hidden training:

- collection is disabled by default and must be enabled by the caller after explicit opt-in;
- each feedback action is a single `prefer` or `avoid` choice on a registered dimension;
- only bounded aggregate counters are stored; drafts, prompts, excerpts, identifiers and raw feedback text are not accepted;
- the in-memory profile is not persisted automatically; JSON export is an explicit caller action;
- loading an export does not re-enable collection;
- the profile is capped at 10,000 decisions and uses a versioned, validated JSON shape.

Example:

```python
from sambu import CreativeLearningProfile

# Create only after the user explicitly opts in.
profile = CreativeLearningProfile(enabled=True)
profile.record_feedback("rhythm", "prefer")
profile.record_feedback("clean_language", "prefer")

# Inspect aggregate preference signals.
print(profile.preference("rhythm"))
snapshot = profile.to_json()  # export only when the caller requests it
```

The normalized preference score is a descriptive balance of approved choices, not a confidence estimate, model prediction or measure of literary quality. This profile does not train a language model, rewrite a draft or infer preferences from usage. For each revision, the author still chooses whether to accept a proposed change.

See [Creative Learning and the improvement loop](CREATIVE_LEARNING.md) for the end-to-end workflow and API boundaries.

## 8. Future model and feedback work

Any later semantic encoder must be a separate, optional subsystem with:

1. explicit training-data provenance, consent and licensing records;
2. distinct semantic, rhythmic/metrical and safety evaluation tasks;
3. language- and dialect-stratified validation sets;
4. a documented baseline, reproducible seeds and versioned artifacts;
5. human review for low-confidence or high-impact decisions;
6. drift monitoring and a tested rollback path;
7. an opt-in feedback path that excludes secrets and unapproved source material.

Vector dimensions, inference latency, accuracy, training-set size and GPU requirements must be published only after measurements can be reproduced. The earlier design brief's example values are not current SAMBU benchmarks.

## 9. Acceptance checklist

- [x] Stable T-001 through T-009 registry with a versioned addition in `2026.12`.
- [x] Backward read compatibility for `2026.11` metadata.
- [x] Machine-readable JSON Schema for objects and bounded arrays.
- [x] Audited review reference/time pair gates generation eligibility.
- [x] Versioned metadata dataclass and JSON-LD export.
- [x] Strict bounds and unknown-field rejection.
- [x] Conservative safety defaults and generation eligibility flag.
- [x] Unit tests for cluster identity, legacy compatibility, validation, bounds, review evidence and safety labels.
- [ ] Reviewed source-corpus ingestion and provenance tooling.
- [ ] Human-in-the-loop annotation interface.
- [ ] Optional embedding/classifier adapter with reproducible evaluation.
- [ ] Drift dashboard and versioned ontology migration tooling.

**Rule:** preserve the creative signal, but never confuse an annotation with evidence, a checksum with provenance, or a planned model with an implemented one.
