# Biology Domain Capabilities

SAMBU now treats the 500-term bilingual glossary as structured, searchable data
with a tested API. The implementation is an educational reference and metadata
tool, not a wet-lab, clinical or diagnostic system.

## Public API

- `BiologyCatalogue.load(path)`: load the UTF-8 TSV into a validated stable-ID index.
- `BiologyCatalogue.get(term_id)`: retrieve one bilingual record.
- `BiologyCatalogue.search(query, language, categories, limit)`: bounded substring search.
- `BiologyCatalogue.category_counts()`: summarize the five 100-term domains.
- `BiologyCatalogue.annotate(...)`: attach a human-authored note and evidence reference.
- `annotation_digest(annotations)`: deterministic SHA-256 digest for metadata comparison.
- `validate_catalogue(path)`: verify 500 records, contiguous IDs and category coverage.

## CLI

```sh
python -m sambu.biology_domain validate
python -m sambu.biology_domain summary
python -m sambu.biology_domain search transcription --language en
python -m sambu.biology_domain search транскрипция --language ru
```

## Boundaries

The catalogue is terminology data. Annotation records are descriptive references,
not experimental results or evidence of a mechanism. The module does not generate
organism modification instructions, wet-lab procedures, diagnoses or treatment
recommendations. Scientific interpretation must be supported by domain experts
and primary literature.
