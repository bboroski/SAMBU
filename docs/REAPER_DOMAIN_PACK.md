# Engineering Reference Domain Pack

**Status:** curated technical reference data and bounded design patterns  
**Catalogue:** [50 engineering patterns](../data/reaper/engineering_patterns_50.tsv)  
**Validator:** `python tools/validate_reaper_domain.py`  
**Related dataset:** [500-term biology reference](../data/biology/academic_terms_500.tsv)

## Purpose

This pack organizes reusable patterns for data pipelines, physical modeling, infrastructure resilience, lifecycle governance and distributed intelligence. The catalogue is passive UTF-8 reference data; its labels are not executable instructions, physical claims or authority to operate external systems.

## Domain mapping

| Technical domain | Engineering interpretation |
|---|---|
| Data pipelines | Provenance, staged transformations, bounded state changes and integrity checks |
| Physical modeling | Explicit parameters, dimensional analysis, coordinate transforms and uncertainty |
| Infrastructure resilience | Fault containment, resource budgets, dependency paths and integrity monitoring |
| Lifecycle governance | Repeatable state machines, migration risk, dependency analysis and disaster recovery |
| Distributed intelligence | Auditable inference boundaries, consensus, input validation and code provenance |

## Implementation constraints

- Keep the catalogue passive; terms are never parsed as executable instructions.
- Use SAMBU unit and validation contracts for physical quantities. Simulation parameters must remain separate from measured values.
- Add examples as isolated fixtures or sample programs; do not add catalogue-specific keywords to the language grammar.
- Record assumptions, parameter ranges, seeds, input provenance and limitations for reproducibility.
- Keep the 500-entry biology dataset independent and stable; add synonyms through separate metadata rather than renumbering IDs.

## Verification

Run `python tools/validate_biology_terms.py` and `python tools/validate_reaper_domain.py`. The pattern catalogue must contain 50 unique terms, five declared categories, ten records per category and contiguous IDs 1–50. Validation proves data structure only; scientific validity requires domain review.

## Scope boundary

This pack provides modeling vocabulary and design patterns. It does not provide biological experimentation, medical interpretation, autonomous system control, weapon specifications or unverified physical technology.
