# Creative Data Governance and Semantic Metadata

**Ontology version:** `2026.11`  
**Status:** the metadata model, cluster registry and validator are implemented in Python. Automated text classification, embedding generation, model training and online adaptation are not implemented by this module.

This document turns the March–April 2025 creative corpus interpretation brief into a versioned, reviewable data contract for SAMBU. It preserves the source vocabulary and eight thematic clusters while avoiding unsupported claims about trained models or classifier performance.

## 1. Purpose and boundary

SAMBU may convert creative material into structured annotations for search, analysis, translation support and carefully reviewed generation workflows. The metadata layer is descriptive: it does not rewrite source text, infer intent from keywords, decide whether a real-world claim is true, or automatically declare content safe.

The processing boundary is:

`source (user-controlled) → human/approved annotation → schema validation → versioned metadata → downstream consumer`

Raw source text is not part of the metadata schema. A caller may attach a source reference and SHA-256 digest, but must manage the source separately under its own consent, access, retention and licensing rules. A digest identifies bytes; it does not prove provenance, permission or truth.

## 2. Thematic ontology

| ID | Cluster | Stable theme key | Description | Candidate applications |
|---|---|---|---|---|
| T-001 | Celebration and ritual | `cultural_celebration` | Festive gatherings, communal joy, market aesthetics and seasonal cycles | Event generation, cultural context tagging, mood analysis |
| T-002 | Identity and transformation | `identity_transformation` | Masks and faces, self-reinvention and artistic persona construction | Character development, style analysis, persona metadata |
| T-003 | Geopolitical awareness | `geopolitical_awareness` | Regional dynamics, institutions, borders and technological sovereignty | Entity recognition, neutral context grounding, summarization |
| T-004 | Emotional duality | `emotional_duality` | Warmth and distance, intimacy and alienation, memory and present reality | Sentiment analysis, dialogue analysis, emotional arc annotation |
| T-005 | Spiritual syncretism | `spiritual_syncretism` | Religious imagery, folk motifs, ritual language and sacred/profane tension | Cultural literacy, symbolic annotation, metaphor analysis |
| T-006 | Technological metaphor | `technological_metaphor` | Hardware-as-body imagery, code-as-ritual and digital/analogue fusion | Technical writing, creative coding prompts, UX language analysis |
| T-007 | Conflict and resilience | `conflict_resilience` | Institutional critique, disruption, endurance and recovery narratives | Crisis communication, educational content, resilience narratives |
| T-008 | Linguistic hybridity | `linguistic_hybridity` | Code-switching, multilingual rhyme, dialectal texture and mixed registers | Translation assessment, multilingual annotation, register analysis |

The cluster is a navigation and analysis label, not a verdict about the source. One work may carry more than one cluster in a future multi-label schema; the current record format deliberately assigns one primary cluster so its first implementation remains deterministic.

## 3. Safety and review labels

The validator accepts these explicit labels:

| Label | Meaning | Generation treatment |
|---|---|---|
| `CLEAN` | Reviewed metadata with no unresolved safety concern | Eligible at the metadata-policy layer |
| `CLEAN_SATIRE` | Satirical material reviewed in context | Eligible at the metadata-policy layer |
| `SANITIZED_ARGOT_ONLY` | Only neutralized argot descriptors are retained | Not eligible by this label alone |
| `SANITIZED_INTIMACY` | Only neutralized intimacy descriptors are retained | Not eligible by this label alone |
| `NEEDS_REVIEW` | Review has not been completed | Not eligible |
| `EXCLUDED_FROM_GENERATION` | Explicitly withheld from generation workflows | Not eligible |

Eligibility is deliberately conservative and does not replace downstream policy checks. A `CLEAN` flag is an annotation from an authorized review process, not a classifier result. Negative or harmful examples may be used in a separate, access-controlled evaluation set when lawful and appropriate; they must not be silently promoted into generative examples.

Profanity, dialect, political references, religion, sexuality or conflict are not automatically equivalent to harmful content. Review should evaluate meaning, target, context, intent and likely use. Neutral academic discussion and creative expression must not be suppressed merely because they mention a sensitive subject.

## 4. Metadata contract

The Python API is `sambu.creative_metadata.CreativeMetadata`. The record contains:

- `cluster_id`, `theme`, `tone`;
- bounded `key_symbols`, `language` and `stylistic_devices` arrays;
- optional `linguistic_register`, `source_ref` and `content_sha256`;
- an explicit `safety_flag` and immutable `ontology_version`.

The validator rejects unknown fields, unknown cluster identifiers, unbounded arrays, malformed hashes and unsupported ontology versions. Missing safety labels default to `NEEDS_REVIEW`, never to a permissive state.

Example JSON record (metadata only):

```json
{
  "cluster_id": "T-001",
  "theme": "cultural_celebration",
  "tone": "nostalgic_reverence",
  "key_symbols": ["fairground", "style_marker", "communal_gathering"],
  "language": ["ru"],
  "linguistic_register": "poetic_colloquial",
  "stylistic_devices": ["visual_imagery", "nostalgic_address"],
  "safety_flag": "NEEDS_REVIEW",
  "source_ref": "corpus-item-001",
  "ontology_version": "2026.11"
}
```

JSON-LD export uses Schema.org's `CreativeWork` type and adds the SAMBU cluster, tone and safety fields. It contains metadata, not the original lyric or prose.

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
    "cluster_id": "T-004",
    "theme": "emotional_duality",
    "tone": "resigned_clarity",
    "key_symbols": ["distance", "memory"],
    "language": ["uk"],
    "safety_flag": "NEEDS_REVIEW",
})

print(record.to_dict())
print(record.to_jsonld())
```

The tool validates supplied labels. It does not classify unannotated text, generate embeddings, fine-tune Sentence-BERT, or learn from user corrections.

## 6. Future model and feedback work

Any later semantic encoder must be a separate, optional subsystem with:

1. explicit training-data provenance, consent and licensing records;
2. distinct semantic, rhythmic/metrical and safety evaluation tasks;
3. language- and dialect-stratified validation sets;
4. a documented baseline, reproducible seeds and versioned artifacts;
5. human review for low-confidence or high-impact decisions;
6. drift monitoring and a tested rollback path;
7. an opt-in feedback path that excludes secrets and unapproved source material.

Vector dimensions, inference latency, accuracy, training-set size and GPU requirements must be published only after measurements can be reproduced. The earlier design brief's example values are not current SAMBU benchmarks.

## 7. Acceptance checklist

- [x] Stable T-001 through T-008 registry.
- [x] Versioned metadata dataclass and JSON-LD export.
- [x] Strict bounds and unknown-field rejection.
- [x] Conservative safety defaults and generation eligibility flag.
- [x] Unit tests for cluster identity, validation, bounds and safety labels.
- [ ] Reviewed source-corpus ingestion and provenance tooling.
- [ ] Human-in-the-loop annotation interface.
- [ ] Optional embedding/classifier adapter with reproducible evaluation.
- [ ] Drift dashboard and versioned ontology migration tooling.

**Rule:** preserve the creative signal, but never confuse an annotation with evidence, a checksum with provenance, or a planned model with an implemented one.
