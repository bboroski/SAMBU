# Academic Biology Domain Pack — 500 Terms

**Repository:** `SAMBU`  
**Dataset:** [`data/biology/academic_terms_500.tsv`](../data/biology/academic_terms_500.tsv)  
**Format:** UTF-8, tab-separated TSV, stable numeric IDs  
**Coverage:** 500 English terms with Russian equivalents across five biology domains

## Data contract

The file contains one header row and exactly 500 records. IDs are stable from 1 through 500 and must not be reassigned when translations or editorial notes are improved.

| Category key | IDs | Scope |
|---|---:|---|
| `molecular_cell` | 1–100 | Molecular and cell biology |
| `genetics_evolution` | 101–200 | Genetics, evolution, biotechnology and development |
| `ecology_environment` | 201–300 | Ecology and environmental biology |
| `physiology_anatomy` | 301–400 | Physiology and anatomy |
| `immunology_microbiology_virology` | 401–500 | Immunology, microbiology and virology |

Each record has four fields: `id`, `category`, `term_en`, and `term_ru`. A tab character is the field separator. Consumers should validate the header, record count, unique contiguous IDs, known category keys, UTF-8 decoding and non-empty terms before use.

## Editorial quality notes

The dataset preserves the 500-entry scope supplied for this project while normalizing clear spelling or translation issues:

- Entry 283, **Demecenter**, is retained to preserve the supplied sequence, but it is not a standard, unambiguous biology term and requires subject-matter review before use as an authoritative term.
- Entry 310 is normalized to **Nephron**; the supplied spelling was “Nefron”.
- Entry 461 is normalized to **Extremophile**; the supplied spelling was “Extremeophile”.
- Entry 487 is translated as **Эндемичное заболевание** to make the disease-context meaning explicit.

This is a bilingual study glossary, not a peer-reviewed ontology. Context-dependent terms can have other translations in specialist literature. Add synonyms or citations in a future version without silently changing stable IDs.

## Project-specific role

Scientific and educational reference data for biology, cell biology, genetics, ecology, physiology, immunology, microbiology and bioinformatics examples. The lexicon can support teaching materials, metadata, search and reproducible scientific examples; it does not change the language grammar or claim that a biology runtime is implemented.

## Safety and integration boundaries

- Treat the glossary as passive text data. Never execute entries as code or commands.
- Do not infer health status, diagnose disease, recommend treatment, or make clinical decisions from a glossary match.
- Do not use terminology as a substitute for biosafety procedures, laboratory protocols, calibrated measurements or professional review.
- Keep this pack optional and offline. Core system, boot, manufacturing, device-diagnostic and lifecycle behavior must remain independent of it.
- Any future parser or UI must handle unknown terms gracefully and retain the original source entry for traceability.

## Local validation

Run `python tools/validate_biology_terms.py` from the repository root. The validator uses only the Python standard library and checks the header, 500-record count, contiguous unique IDs, category coverage and non-empty bilingual fields.

## Change policy

Keep all nine repository copies byte-for-byte aligned when updating the shared pack. Review changes to scientific wording separately from software changes. Validate exactly 500 data rows and IDs 1–500 after every update.

---

*UA: Довідковий двомовний словник для навчання й метаданих; не є медичним або апаратним механізмом прийняття рішень.*  
*RU: Двуязычный справочный словарь для обучения и метаданных; не является медицинским или аппаратным механизмом принятия решений.*  
*EN: A bilingual reference glossary for education and metadata; it is not a medical or hardware decision engine.*
