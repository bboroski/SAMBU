# Structured Annotation Metadata Governance

**Ontology version:** `2026.12`  
**Compatibility:** records from `2026.11` remain readable; cluster `T-009` requires `2026.12`.  
**Status:** metadata model, cluster registry and validator implemented in Python. Automated classification, embedding generation, model training and online adaptation are not implemented.

## 1. Scope and data boundary

SAMBU stores bounded annotations for search, comparison, localization and reviewed generation workflows. The metadata layer does not rewrite source data, infer intent, validate external claims or assign safety status automatically.

`source reference → reviewed annotation → schema validation → versioned metadata → consumer`

Raw source content is excluded. Callers may attach a source reference and SHA-256 digest, but source storage, consent, access, retention and licensing remain external responsibilities. A digest identifies bytes; it does not prove provenance, permission or truth.

## 2. Technical annotation taxonomy

| ID | Technical cluster | Scope | Applications |
|---|---|---|---|
| T-001 | Event and schedule context | Event records, recurring time windows, shared activity metadata and service contexts | Event description, context tagging, schedule annotation |
| T-002 | Entity state transitions | Profile updates, role transitions, representation metadata and lifecycle changes | Profile analysis, entity tracking, state annotation |
| T-003 | Geospatial and boundary context | Regions, jurisdictional boundaries, coordinate references and administrative zones | Entity recognition, regional comparison, context grounding |
| T-004 | State contrast | Competing conditions, uncertainty, value differences and temporal variation | State comparison, dialogue-structure analysis, change annotation |
| T-005 | Symbolic reference mapping | Symbol sets, convention mappings, source references and category relationships | Catalog annotation, symbolic indexing, reference analysis |
| T-006 | System analogy mapping | Cross-domain mappings between technical systems, software, hardware and physical representations | Technical writing, system documentation, interface analysis |
| T-007 | Fault and recovery sequences | Incidents, constraints, failure handling, continuity and restoration sequences | Incident reporting, operational documentation, recovery analysis |
| T-008 | Locale and terminology variance | Language tags, locale switching, terminology variants and register selection | Translation assessment, interface localization, terminology analysis |
| T-009 | Ambiguity and association analysis | Unexpected links, ambiguous labels, category mismatches and controlled association mapping | Label review, ambiguity analysis, association annotation |

Cluster IDs remain stable. The legacy `theme` field is a storage-compatibility identifier; display labels and descriptions use the neutral technical taxonomy above. Do not renumber IDs or infer implementation from a cluster label.

## 3. Review and eligibility flags

| Stable flag | Technical meaning | Generation treatment |
|---|---|---|
| `CLEAN` | Reviewed metadata with no unresolved policy issue | Eligible only with `review_ref` and `reviewed_at` evidence |
| `CLEAN_SATIRE` | Reviewed nonliteral data in declared context | Eligible only with review evidence |
| `SANITIZED_ARGOT_ONLY` | Only normalized lexical markers are retained | Not eligible by this flag alone |
| `SANITIZED_INTIMACY` | Only normalized proximity markers are retained | Not eligible by this flag alone |
| `NEEDS_REVIEW` | Review is incomplete | Not eligible |
| `EXCLUDED_FROM_GENERATION` | Explicitly excluded from generation workflows | Not eligible |

Eligibility is conservative. A `CLEAN` or `CLEAN_SATIRE` flag is insufficient without a pseudonymous `review_ref` and timezone-aware ISO-8601 `reviewed_at`. The record is an audit reference, not proof that source data is licensed, accurate or universally safe. The system never infers review evidence automatically.

Lexical variation, locale markers, jurisdictional references, interpersonal terms and incident language are not automatically equivalent to harmful content. Review must assess the data in its declared context and intended processing path. Do not classify a record solely by keyword presence.

## 4. Record contract

The compatibility API is `sambu.creative_metadata.CreativeMetadata`. A record contains:

- `cluster_id`, `theme`, `tone`;
- bounded `key_symbols`, `language` and `stylistic_devices` arrays;
- optional `linguistic_register`, `source_ref`, `content_sha256`, `review_ref` and `reviewed_at`;
- explicit `safety_flag` and immutable `ontology_version`.

The validator rejects unknown fields and clusters, unbounded arrays, malformed hashes, invalid timestamps and unsupported ontology versions. Review fields must be supplied together. Missing safety values default to `NEEDS_REVIEW`. The machine-readable Draft 2020-12 contract is [schemas/creative-metadata.schema.json](../schemas/creative-metadata.schema.json).

## 5. CLI and API

```bash
sambu creative clusters
sambu creative clusters --json
sambu creative validate examples/creative_metadata.sample.json
sambu creative validate examples/creative_metadata.sample.json --json
```

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

The stable theme value in the example is retained for stored-record compatibility. JSON-LD exposes the neutral cluster display name.

## 6. Limits

The module validates supplied metadata only. It does not classify unannotated source data, generate embeddings, fine-tune models or learn from user content. Review remains explicit, external and auditable; raw source data is never copied into the metadata record.
