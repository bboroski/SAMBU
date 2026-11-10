# Reaper Domain Transfer Profile — SAMBU

**Status:** domain-pack design and typed glossary seed  
**Role:** bilingual terminology, ontology, scientific-model metadata and deterministic validation

## Objective

Turn the 500-entry English–Russian reference into a maintainable domain pack rather than a loose list. The subject is the Reapers and related *Mass Effect* lore: biology and harvesting, eezo/mass-effect physics, weapons and infrastructure, cycle history/philosophy, and synthetic intelligence.

SAMBU owns the language-neutral record model. A term is data, not executable authority. The initial machine-readable contract is `schemas/domain-term.schema.json`; `domains/mass-effect/reapers/terms.seed.json` contains representative records for all five source groups.

## Classification is mandatory

The source list mixes established franchise names/mechanics with descriptive labels and extrapolations. Every record must carry one of these labels:

- `canon-name`: named character, species, ship, place, faction or artifact used in the games.
- `canon-mechanic`: an established in-universe mechanism such as indoctrination, mass relays or kinetic barriers.
- `descriptive-extension`: useful wording that describes a process but is not asserted to be an official proper term.
- `speculative-fiction`: an extrapolation or fictional mechanism whose status is uncertain.
- `engineering-analogy`: a neutral mapping to a real software or systems concept.

Do not silently upgrade descriptive or speculative entries to canon. Keep the source wording, normalized identifier, English label, Russian label, category, classification, short note and typed relations separate. Translations are display values; identifiers remain stable and language-independent.

## Five ontology domains

| Source group | SAMBU domain | Useful data model |
|---|---|---|
| Reaper biology, harvesting and cybernetics | `reaper.bio` | organism, transformation, batch, neural/cognitive effect |
| Eezo and mass-effect physics | `reaper.physics` | fictional field, drive, relay, anomaly, unit disclaimer |
| Weapons, defense and infrastructure | `reaper.systems` | platform, weapon, barrier, sensor, network node |
| Lore, history and cycles | `reaper.history` | species, cycle, event, artifact, chronology |
| Synthetic biology and AI | `reaper.ai` | agent, consensus, memory, process, trust boundary |

## Modeling rules

1. Preserve provenance and the original English–Russian pair; never infer a missing translation.
2. Use explicit relations such as `part-of`, `derived-from`, `opposes`, `controls`, and `appears-in`. Reject dangling identifiers.
3. Do not assign SI units to eezo, mass relays, biotic fields or other fictional mechanisms unless a source explicitly defines them.
4. Keep lore facts separate from scientific facts. “Dark energy” in the setting is not a measurement of cosmological dark energy.
5. Treat indoctrination and synthetic consciousness as narrative concepts, not medical or psychological diagnoses.
6. Keep corpus import, normalization and export deterministic. Never execute a term, a relationship or an imported example as code.

## Acceptance criteria

- Schema validation rejects missing IDs, duplicate IDs, invalid categories and unknown classifications.
- A normalized export is stable across repeated runs.
- English and Russian labels can be searched independently without changing identity.
- Tests distinguish canon labels from descriptive and speculative language.
- The CLI and IDE can display domain metadata without claiming the full 500-entry corpus has already been imported.

**Scope note:** this profile defines the data contract and transfer path. It does not claim a complete import of all 500 entries or a finished ontology engine.
