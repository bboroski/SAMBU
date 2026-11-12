# Linguistic Heritage Engine: Cyrillic Ы

**Status:** research data contract and repository integration baseline  
**Shared record:** `data/linguistic-heritage/cyrillic-letter-y.json`  
**Contract:** `linguistic-heritage.letter.v1`

## Purpose

This repository participates in the 13-repository Linguistic Heritage Engine. The shared subject is the Cyrillic grapheme **Ы / ы**, researched through separate but connected layers: graphic genealogy, historical phonology, modern articulation, comparative Slavic phonetics, orthographic history and cultural interpretation.

## Repository integration role

Canonical research owner: maintain the letter-record schema, evidence taxonomy, deterministic validation and versioned linguistic data. The Python runtime remains optional for consumers.

The integration is intentionally scoped to this repository's existing responsibility. The shared research record is reference data, not a new runtime dependency. No repository's product behavior, device access, boot path, firmware, lifecycle or safety policy is changed by the presence of this record.

## Research rules

1. Keep grapheme history distinct from the history of the sound [ɨ].
2. Treat ЪІ / ЪИ as the conventional ligature explanation; do not invent a single creation date.
3. Mark disputed phonological analyses as disputed.
4. Do not equate Russian ы, Polish y and Ukrainian и as identical phones.
5. Keep symbolism and numerology in an explicitly interpretive layer.
6. Every manuscript-specific statement requires a verifiable shelfmark, folio and specialist source.
7. Distinguish documented evidence, scholarly interpretation and open hypothesis.

## Validation

The JSON record is designed for deterministic, offline validation. The shared conformance test uses only the Python standard library:

```bash
python -m unittest discover -s tests -p 'test_linguistic_heritage_contract.py' -v
```

This test validates the local research record's structural and epistemic guardrails. It does not prove historical truth or replace expert review.

## Cross-repository boundaries

- SAMBU owns the canonical data contract, schema and research validator.
- Luci may inspect the metadata and report policy violations; it does not certify scholarship.
- Klipot may present a read-only research view; it does not execute repository code.
- Hellduck indexes repository participation and versioned relationships.
- All other repositories expose a scoped reference/integration note without acquiring runtime dependencies.

## References

- Cavar et al., *High central vowels in Polish, Ukrainian and Russian*, JIPA (2025), [DOI](https://doi.org/10.1017/S0025100325000040).
- *Russian*, Journal of the International Phonetic Association (2015), [Cambridge Core](https://www.cambridge.org/core/journals/journal-of-the-international-phonetic-association/article/russian/55589EC639ADEF1764B5ECD0B76970FA).
- The conventional ЪІ ligature account is a secondary-reference starting point; see [Cyrillic script](https://www.newworldencyclopedia.org/entry/Cyrillic_script). Manuscript claims remain pending primary palaeographic evidence.


## Canonical implementation

SAMBU owns the shared record contract in `schemas/linguistic-heritage-letter.schema.json`, the 13-repository registration in `ecosystem/registry.json`, and the offline validator `tools/validate_linguistic_heritage.py`.

Run `python tools/validate_linguistic_heritage.py` to validate the canonical record. The check uses only the Python standard library and verifies identity, Unicode code points, claim status vocabulary, evidence/interpretation separation, policy flags and HTTPS references. It does not adjudicate historical truth.
