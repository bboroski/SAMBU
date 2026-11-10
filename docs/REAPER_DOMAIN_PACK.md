# Reaper-Inspired Scientific Domain Pack

**Status:** curated reference data and engineering patterns  
**Catalogue:** [50 selected terms](../data/reaper/engineering_patterns_50.tsv)  
**Validator:** `python tools/validate_reaper_domain.py`  
**Related pack:** [500-term academic biology glossary](../data/biology/academic_terms_500.tsv)

## Purpose

This pack translates selected Mass Effect Reaper concepts into neutral engineering questions for scientific modeling, software architecture, and resilience exercises. It does not import game mechanics as real science. The 50 rows are a curated subset of the supplied terminology, not a claim that the entire 500-item source has been reproduced.

## Domain mapping

| Source domain | Engineering interpretation in SAMBU |
|---|---|
| Biosynthesis and cybernetics | Data lineage, staged transformations, model reconstruction, bounded state changes |
| Element Zero and mass-effect physics | Explicit simulation parameters, dimensional analysis, coordinate transforms, uncertainty |
| Weapons and infrastructure | Fault containment, resource budgets, dependency paths, integrity monitoring |
| Cycles and philosophy | Repeatable lifecycle models, migration risk, dependency lock-in, disaster recovery |
| Synthetic intelligence | Auditable model boundaries, distributed consensus, input validation, code provenance |

## Implementation rules

- Keep the catalogue as passive UTF-8 reference data. Terms are never parsed as executable instructions.
- Use existing SAMBU units and validation contracts for physical quantities; never invent units or treat fictional Eezo/dark-energy values as measured science.
- Add domain examples as isolated fixtures or sample programs. Do not add Mass Effect-specific keywords to the language grammar.
- A model's assumptions, parameter ranges, seed, input provenance, and limitations must be recorded so results can be reproduced.
- Keep the existing 500-entry biology dataset independent and byte-for-byte stable; add synonyms through separate metadata rather than renumbering its IDs.

## Verification and acceptance

Run `python tools/validate_biology_terms.py` and `python tools/validate_reaper_domain.py`. The Reaper catalogue must contain 50 unique terms, five declared categories, ten records per category, and contiguous IDs 1–50. CI runs both validators. This validates data structure only; scientific validity still requires domain review.

## Scope boundary

This is a modeling and vocabulary pack. It does not provide biological experimentation, medical interpretation, autonomous system control, weapons design, or real-world faster-than-light/field technology.
