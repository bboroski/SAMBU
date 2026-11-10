# SAMBU Articulatory Syntax — 200-word edition

**Specification:** AS-1  
**Baseline:** SAMBU 0.11 alpha  
**Status:** implemented, experimental  
**Word count:** 200 unique lexical forms — 25 grammar forms, 123 built-in forms, 52 reserved forms.

## 1. Design intent

SAMBU now has a second native source surface: **articulatory syntax**. It is not a replacement grammar and does not translate whole programs through a natural-language model. It is a deterministic phonological layer over the existing parser and runtime.

Every word follows one regular two-syllable shape:

`ONSET + GRADE + CODA`

- The onset consonant selects a semantic family.
- The vowel selects an articulation mode.
- The ending selects the grammatical role.
- The first syllable carries the stress: `ka-va`, `ka-ven`, `ka-vir`, `ka-vum`.

The wordbook is generated as a closed matrix:

`10 families × 5 grades × 4 codas = 200 words`.

This gives SAMBU a regular sound-to-meaning system rather than 200 unrelated coinages.

## 2. Articulatory construction

### 2.1 Onset families

| Sound | Family | Semantic field |
|---|---|---|
| `k` | structure | declarations, types and architecture |
| `t` | flow | sequence, branching and control |
| `r` | value | data, payloads and numbers |
| `m` | memory | state, identity and continuity |
| `s` | safeguard | logic, truth and constraints |
| `v` | measure | quantities, physics and calculation |
| `d` | evidence | diagnostics, signals and proof |
| `n` | coordination | messages, concurrency and supervision |
| `p` | transform | geometry, space and composition |
| `l` | language | sound, symbols, text and expression |

### 2.2 Vowel grades

| Vowel | Articulation | Semantic operation |
|---|---|---|
| `a` | opening | initiate, declare, create |
| `e` | inspection | observe, check, validate |
| `i` | transformation | calculate, convert, transform |
| `o` | composition | combine, group, contain |
| `u` | completion | finish, release, close |

### 2.3 Grammatical codas

| Ending | Role | Meaning |
|---|---|---|
| `-va` | action | operation or directive |
| `-ven` | entity | named object, type or resource |
| `-vir` | relation | link, rule or connection |
| `-vum` | state | value, condition or result |

**Example derivation:** `kava` = structure + opening + action = “declare/construct”. `kaven` = structure + opening + entity = “declared structural entity”. `kavir` = structure + opening + relation = “structural link”. `kavum` = structure + opening + state = “structural state”.

The four endings preserve their roles across all ten families. New words can therefore be understood from their sound shape before consulting the full entry.

## 3. Executable grammar words

The 25 implemented grammar forms are normalized by the lexer to existing grammar terminals. The original spelling remains available as `Token.lexeme`, and source offsets are unchanged.

| Articulatory word | Canonical grammar |
|---|---|
| `kava` | `let` |
| `kaven` | `class` |
| `kavir` | `extends` |
| `kavum` | `static` |
| `keva` | `interface` |
| `keven` | `trait` |
| `kevir` | `implements` |
| `kevum` | `abstract` |
| `kiva` | `final` |
| `kiven` | `public` |
| `kivir` | `private` |
| `kivum` | `protected` |
| `kova` | `uses` |
| `tava` | `fn` |
| `taven` | `for` |
| `tavir` | `in` |
| `tavum` | `return` |
| `teva` | `if` |
| `teven` | `else` |
| `rava` | `and` |
| `raven` | `or` |
| `ravir` | `not` |
| `ravum` | `true` |
| `reva` | `false` |
| `reven` | `null` |

Legacy forms such as `let`, `fn`, `if`, `class`, `return`, and `true` remain valid. A source file may use either surface, or combine both during migration.

## 4. Executable built-in words

The 123 implemented built-in forms call existing SAMBU library functions. They do not create duplicate implementations or change function argument contracts. Families are grouped by sound and functional relationship in the full wordbook below.

Two additional lexicon services are available inside SAMBU:
- `word_info(word)` returns the complete articulatory record.
- `wordbook()` returns all 200 forms; `wordbook("active")`, `wordbook("reserved")`, `wordbook("keyword")`, `wordbook("builtin")`, or `wordbook("V")` filters the lexicon.

Their articulated spellings are `leven` (`word_info`) and `levir` (`wordbook`).

## 5. Reserved vocabulary

52 forms are fully defined lexemes, but are **reserved**, not executable keywords or built-ins yet. They name future semantic slots for advanced type construction, protocols, state transitions, diagnostics, parallel execution and source tooling. They are available through `word_info` and `wordbook("reserved")`.

A reserved word never silently performs an operation. When a future feature is implemented, its status can change only alongside parser/runtime code and regression tests.

## 6. Complete 200-word lexicon

The table marks every word's phonetic form, compositional meaning and implementation status. `keyword` means parser grammar alias; `builtin` means runtime alias; `reserved` means documented future vocabulary.

### K — structure

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `kava` | ka-va | shape, declaration and architecture; initiate, declare or create; an operation or directive | ключевое слово → `let` |
| `kaven` | ka-ven | shape, declaration and architecture; initiate, declare or create; a named object, type or resource | ключевое слово → `class` |
| `kavir` | ka-vir | shape, declaration and architecture; initiate, declare or create; a link, rule or connection | ключевое слово → `extends` |
| `kavum` | ka-vum | shape, declaration and architecture; initiate, declare or create; a value, condition or result | ключевое слово → `static` |
| `keva` | ke-va | shape, declaration and architecture; observe, check or validate; an operation or directive | ключевое слово → `interface` |
| `keven` | ke-ven | shape, declaration and architecture; observe, check or validate; a named object, type or resource | ключевое слово → `trait` |
| `kevir` | ke-vir | shape, declaration and architecture; observe, check or validate; a link, rule or connection | ключевое слово → `implements` |
| `kevum` | ke-vum | shape, declaration and architecture; observe, check or validate; a value, condition or result | ключевое слово → `abstract` |
| `kiva` | ki-va | shape, declaration and architecture; calculate, convert or transform; an operation or directive | ключевое слово → `final` |
| `kiven` | ki-ven | shape, declaration and architecture; calculate, convert or transform; a named object, type or resource | ключевое слово → `public` |
| `kivir` | ki-vir | shape, declaration and architecture; calculate, convert or transform; a link, rule or connection | ключевое слово → `private` |
| `kivum` | ki-vum | shape, declaration and architecture; calculate, convert or transform; a value, condition or result | ключевое слово → `protected` |
| `kova` | ko-va | shape, declaration and architecture; combine, group or contain; an operation or directive | ключевое слово → `uses` |
| `koven` | ko-ven | shape, declaration and architecture; combine, group or contain; a named object, type or resource | встроенная форма → `rps_round` |
| `kovir` | ko-vir | shape, declaration and architecture; combine, group or contain; a link, rule or connection | встроенная форма → `tic_tac_toe_state` |
| `kovum` | ko-vum | shape, declaration and architecture; combine, group or contain; a value, condition or result | встроенная форма → `tic_tac_toe_move` |
| `kuva` | ku-va | shape, declaration and architecture; finish, release or close; an operation or directive | встроенная форма → `tic_tac_toe_best_move` |
| `kuven` | ku-ven | shape, declaration and architecture; finish, release or close; a named object, type or resource | зарезервировано |
| `kuvir` | ku-vir | shape, declaration and architecture; finish, release or close; a link, rule or connection | зарезервировано |
| `kuvum` | ku-vum | shape, declaration and architecture; finish, release or close; a value, condition or result | зарезервировано |

### T — flow

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `tava` | ta-va | sequence, branching and control; initiate, declare or create; an operation or directive | ключевое слово → `fn` |
| `taven` | ta-ven | sequence, branching and control; initiate, declare or create; a named object, type or resource | ключевое слово → `for` |
| `tavir` | ta-vir | sequence, branching and control; initiate, declare or create; a link, rule or connection | ключевое слово → `in` |
| `tavum` | ta-vum | sequence, branching and control; initiate, declare or create; a value, condition or result | ключевое слово → `return` |
| `teva` | te-va | sequence, branching and control; observe, check or validate; an operation or directive | ключевое слово → `if` |
| `teven` | te-ven | sequence, branching and control; observe, check or validate; a named object, type or resource | ключевое слово → `else` |
| `tevir` | te-vir | sequence, branching and control; observe, check or validate; a link, rule or connection | встроенная форма → `network` |
| `tevum` | te-vum | sequence, branching and control; observe, check or validate; a value, condition or result | встроенная форма → `network_metrics` |
| `tiva` | ti-va | sequence, branching and control; calculate, convert or transform; an operation or directive | встроенная форма → `influence` |
| `tiven` | ti-ven | sequence, branching and control; calculate, convert or transform; a named object, type or resource | встроенная форма → `funnel` |
| `tivir` | ti-vir | sequence, branching and control; calculate, convert or transform; a link, rule or connection | встроенная форма → `ab_test` |
| `tivum` | ti-vum | sequence, branching and control; calculate, convert or transform; a value, condition or result | встроенная форма → `weekly_schedule` |
| `tova` | to-va | sequence, branching and control; combine, group or contain; an operation or directive | встроенная форма → `attendance` |
| `toven` | to-ven | sequence, branching and control; combine, group or contain; a named object, type or resource | встроенная форма → `capture_tower` |
| `tovir` | to-vir | sequence, branching and control; combine, group or contain; a link, rule or connection | встроенная форма → `allocate` |
| `tovum` | to-vum | sequence, branching and control; combine, group or contain; a value, condition or result | встроенная форма → `negotiate` |
| `tuva` | tu-va | sequence, branching and control; finish, release or close; an operation or directive | встроенная форма → `channel_metrics` |
| `tuven` | tu-ven | sequence, branching and control; finish, release or close; a named object, type or resource | встроенная форма → `queue_profile` |
| `tuvir` | tu-vir | sequence, branching and control; finish, release or close; a link, rule or connection | встроенная форма → `retry_schedule` |
| `tuvum` | tu-vum | sequence, branching and control; finish, release or close; a value, condition or result | встроенная форма → `idempotency_key` |

### R — value

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `rava` | ra-va | payload, number and stored data; initiate, declare or create; an operation or directive | ключевое слово → `and` |
| `raven` | ra-ven | payload, number and stored data; initiate, declare or create; a named object, type or resource | ключевое слово → `or` |
| `ravir` | ra-vir | payload, number and stored data; initiate, declare or create; a link, rule or connection | ключевое слово → `not` |
| `ravum` | ra-vum | payload, number and stored data; initiate, declare or create; a value, condition or result | ключевое слово → `true` |
| `reva` | re-va | payload, number and stored data; observe, check or validate; an operation or directive | ключевое слово → `false` |
| `reven` | re-ven | payload, number and stored data; observe, check or validate; a named object, type or resource | ключевое слово → `null` |
| `revir` | re-vir | payload, number and stored data; observe, check or validate; a link, rule or connection | встроенная форма → `percent_of` |
| `revum` | re-vum | payload, number and stored data; observe, check or validate; a value, condition or result | встроенная форма → `apply_percent` |
| `riva` | ri-va | payload, number and stored data; calculate, convert or transform; an operation or directive | встроенная форма → `reduce_by_percent` |
| `riven` | ri-ven | payload, number and stored data; calculate, convert or transform; a named object, type or resource | встроенная форма → `percentage` |
| `rivir` | ri-vir | payload, number and stored data; calculate, convert or transform; a link, rule or connection | встроенная форма → `percent_change` |
| `rivum` | ri-vum | payload, number and stored data; calculate, convert or transform; a value, condition or result | встроенная форма → `percent_to_ratio` |
| `rova` | ro-va | payload, number and stored data; combine, group or contain; an operation or directive | встроенная форма → `ratio_to_percent` |
| `roven` | ro-ven | payload, number and stored data; combine, group or contain; a named object, type or resource | встроенная форма → `percentage_points` |
| `rovir` | ro-vir | payload, number and stored data; combine, group or contain; a link, rule or connection | встроенная форма → `clamp_percent` |
| `rovum` | ro-vum | payload, number and stored data; combine, group or contain; a value, condition or result | зарезервировано |
| `ruva` | ru-va | payload, number and stored data; finish, release or close; an operation or directive | зарезервировано |
| `ruven` | ru-ven | payload, number and stored data; finish, release or close; a named object, type or resource | зарезервировано |
| `ruvir` | ru-vir | payload, number and stored data; finish, release or close; a link, rule or connection | зарезервировано |
| `ruvum` | ru-vum | payload, number and stored data; finish, release or close; a value, condition or result | зарезервировано |

### M — memory

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `mava` | ma-va | state, identity and continuity; initiate, declare or create; an operation or directive | встроенная форма → `gift_transfer` |
| `maven` | ma-ven | state, identity and continuity; initiate, declare or create; a named object, type or resource | встроенная форма → `gift_batch` |
| `mavir` | ma-vir | state, identity and continuity; initiate, declare or create; a link, rule or connection | встроенная форма → `accreditation_record` |
| `mavum` | ma-vum | state, identity and continuity; initiate, declare or create; a value, condition or result | встроенная форма → `accreditation_status` |
| `meva` | me-va | state, identity and continuity; observe, check or validate; an operation or directive | встроенная форма → `associate` |
| `meven` | me-ven | state, identity and continuity; observe, check or validate; a named object, type or resource | встроенная форма → `signal_report` |
| `mevir` | me-vir | state, identity and continuity; observe, check or validate; a link, rule or connection | встроенная форма → `blast_plan` |
| `mevum` | me-vum | state, identity and continuity; observe, check or validate; a value, condition or result | встроенная форма → `mimic_profile` |
| `miva` | mi-va | state, identity and continuity; calculate, convert or transform; an operation or directive | встроенная форма → `mimic_distance` |
| `miven` | mi-ven | state, identity and continuity; calculate, convert or transform; a named object, type or resource | встроенная форма → `imprint_closure` |
| `mivir` | mi-vir | state, identity and continuity; calculate, convert or transform; a link, rule or connection | встроенная форма → `v_vector_stream` |
| `mivum` | mi-vum | state, identity and continuity; calculate, convert or transform; a value, condition or result | встроенная форма → `countercurrent_sync` |
| `mova` | mo-va | state, identity and continuity; combine, group or contain; an operation or directive | встроенная форма → `biometric_taxonomy_sort` |
| `moven` | mo-ven | state, identity and continuity; combine, group or contain; a named object, type or resource | встроенная форма → `wetland_ecosystem_loop` |
| `movir` | mo-vir | state, identity and continuity; combine, group or contain; a link, rule or connection | зарезервировано |
| `movum` | mo-vum | state, identity and continuity; combine, group or contain; a value, condition or result | зарезервировано |
| `muva` | mu-va | state, identity and continuity; finish, release or close; an operation or directive | зарезервировано |
| `muven` | mu-ven | state, identity and continuity; finish, release or close; a named object, type or resource | зарезервировано |
| `muvir` | mu-vir | state, identity and continuity; finish, release or close; a link, rule or connection | зарезервировано |
| `muvum` | mu-vum | state, identity and continuity; finish, release or close; a value, condition or result | зарезервировано |

### S — safeguard

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `sava` | sa-va | logic, truth and constraint; initiate, declare or create; an operation or directive | встроенная форма → `countercurrent_exchange` |
| `saven` | sa-ven | logic, truth and constraint; initiate, declare or create; a named object, type or resource | встроенная форма → `plumage_insulation` |
| `savir` | sa-vir | logic, truth and constraint; initiate, declare or create; a link, rule or connection | встроенная форма → `feather_barrier_profile` |
| `savum` | sa-vum | logic, truth and constraint; initiate, declare or create; a value, condition or result | встроенная форма → `flight_energy_budget` |
| `seva` | se-va | logic, truth and constraint; observe, check or validate; an operation or directive | встроенная форма → `flight_muscle_profile` |
| `seven` | se-ven | logic, truth and constraint; observe, check or validate; a named object, type or resource | встроенная форма → `migration_speed` |
| `sevir` | se-vir | logic, truth and constraint; observe, check or validate; a link, rule or connection | встроенная форма → `oxygen_pressure_ratio` |
| `sevum` | se-vum | logic, truth and constraint; observe, check or validate; a value, condition or result | встроенная форма → `avian_gas_exchange` |
| `siva` | si-va | logic, truth and constraint; calculate, convert or transform; an operation or directive | встроенная форма → `avian_air_sac_cycle` |
| `siven` | si-ven | logic, truth and constraint; calculate, convert or transform; a named object, type or resource | встроенная форма → `bill_lamella_filter` |
| `sivir` | si-vir | logic, truth and constraint; calculate, convert or transform; a link, rule or connection | встроенная форма → `salt_balance` |
| `sivum` | si-vum | logic, truth and constraint; calculate, convert or transform; a value, condition or result | встроенная форма → `flock_flight_budget` |
| `sova` | so-va | logic, truth and constraint; combine, group or contain; an operation or directive | встроенная форма → `visual_system_profile` |
| `soven` | so-ven | logic, truth and constraint; combine, group or contain; a named object, type or resource | встроенная форма → `imprinting_window` |
| `sovir` | so-vir | logic, truth and constraint; combine, group or contain; a link, rule or connection | встроенная форма → `hemispheric_sleep_budget` |
| `sovum` | so-vum | logic, truth and constraint; combine, group or contain; a value, condition or result | встроенная форма → `magnetic_heading` |
| `suva` | su-va | logic, truth and constraint; finish, release or close; an operation or directive | встроенная форма → `digestive_grinding` |
| `suven` | su-ven | logic, truth and constraint; finish, release or close; a named object, type or resource | зарезервировано |
| `suvir` | su-vir | logic, truth and constraint; finish, release or close; a link, rule or connection | зарезервировано |
| `suvum` | su-vum | logic, truth and constraint; finish, release or close; a value, condition or result | зарезервировано |

### V — measure

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `vava` | va-va | quantity, physics and calculation; initiate, declare or create; an operation or directive | встроенная форма → `maxwell` |
| `vaven` | va-ven | quantity, physics and calculation; initiate, declare or create; a named object, type or resource | встроенная форма → `boltzmann` |
| `vavir` | va-vir | quantity, physics and calculation; initiate, declare or create; a link, rule or connection | встроенная форма → `thermal_energy` |
| `vavum` | va-vum | quantity, physics and calculation; initiate, declare or create; a value, condition or result | встроенная форма → `partition` |
| `veva` | ve-va | quantity, physics and calculation; observe, check or validate; an operation or directive | встроенная форма → `entropy` |
| `veven` | ve-ven | quantity, physics and calculation; observe, check or validate; a named object, type or resource | встроенная форма → `sample_maxwell` |
| `vevir` | ve-vir | quantity, physics and calculation; observe, check or validate; a link, rule or connection | встроенная форма → `mean` |
| `vevum` | ve-vum | quantity, physics and calculation; observe, check or validate; a value, condition or result | встроенная форма → `variance` |
| `viva` | vi-va | quantity, physics and calculation; calculate, convert or transform; an operation or directive | встроенная форма → `sqrt` |
| `viven` | vi-ven | quantity, physics and calculation; calculate, convert or transform; a named object, type or resource | встроенная форма → `exp` |
| `vivir` | vi-vir | quantity, physics and calculation; calculate, convert or transform; a link, rule or connection | встроенная форма → `log` |
| `vivum` | vi-vum | quantity, physics and calculation; calculate, convert or transform; a value, condition or result | встроенная форма → `abs` |
| `vova` | vo-va | quantity, physics and calculation; combine, group or contain; an operation or directive | встроенная форма → `count` |
| `voven` | vo-ven | quantity, physics and calculation; combine, group or contain; a named object, type or resource | встроенная форма → `len` |
| `vovir` | vo-vir | quantity, physics and calculation; combine, group or contain; a link, rule or connection | встроенная форма → `range` |
| `vovum` | vo-vum | quantity, physics and calculation; combine, group or contain; a value, condition or result | встроенная форма → `sum` |
| `vuva` | vu-va | quantity, physics and calculation; finish, release or close; an operation or directive | встроенная форма → `min` |
| `vuven` | vu-ven | quantity, physics and calculation; finish, release or close; a named object, type or resource | встроенная форма → `max` |
| `vuvir` | vu-vir | quantity, physics and calculation; finish, release or close; a link, rule or connection | зарезервировано |
| `vuvum` | vu-vum | quantity, physics and calculation; finish, release or close; a value, condition or result | зарезервировано |

### D — evidence

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `dava` | da-va | diagnosis, signal and proof; initiate, declare or create; an operation or directive | встроенная форма → `coq_rule` |
| `daven` | da-ven | diagnosis, signal and proof; initiate, declare or create; a named object, type or resource | встроенная форма → `coq_match` |
| `davir` | da-vir | diagnosis, signal and proof; initiate, declare or create; a link, rule or connection | встроенная форма → `coq_explain` |
| `davum` | da-vum | diagnosis, signal and proof; initiate, declare or create; a value, condition or result | встроенная форма → `coq_filter` |
| `deva` | de-va | diagnosis, signal and proof; observe, check or validate; an operation or directive | встроенная форма → `coq_pipeline` |
| `deven` | de-ven | diagnosis, signal and proof; observe, check or validate; a named object, type or resource | встроенная форма → `parse_report` |
| `devir` | de-vir | diagnosis, signal and proof; observe, check or validate; a link, rule or connection | встроенная форма → `mine_patterns` |
| `devum` | de-vum | diagnosis, signal and proof; observe, check or validate; a value, condition or result | встроенная форма → `cluster_glue` |
| `diva` | di-va | diagnosis, signal and proof; calculate, convert or transform; an operation or directive | встроенная форма → `pitch_score` |
| `diven` | di-ven | diagnosis, signal and proof; calculate, convert or transform; a named object, type or resource | зарезервировано |
| `divir` | di-vir | diagnosis, signal and proof; calculate, convert or transform; a link, rule or connection | зарезервировано |
| `divum` | di-vum | diagnosis, signal and proof; calculate, convert or transform; a value, condition or result | зарезервировано |
| `dova` | do-va | diagnosis, signal and proof; combine, group or contain; an operation or directive | зарезервировано |
| `doven` | do-ven | diagnosis, signal and proof; combine, group or contain; a named object, type or resource | зарезервировано |
| `dovir` | do-vir | diagnosis, signal and proof; combine, group or contain; a link, rule or connection | зарезервировано |
| `dovum` | do-vum | diagnosis, signal and proof; combine, group or contain; a value, condition or result | зарезервировано |
| `duva` | du-va | diagnosis, signal and proof; finish, release or close; an operation or directive | зарезервировано |
| `duven` | du-ven | diagnosis, signal and proof; finish, release or close; a named object, type or resource | зарезервировано |
| `duvir` | du-vir | diagnosis, signal and proof; finish, release or close; a link, rule or connection | зарезервировано |
| `duvum` | du-vum | diagnosis, signal and proof; finish, release or close; a value, condition or result | зарезервировано |

### N — coordination

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `nava` | na-va | messages, concurrency and supervision; initiate, declare or create; an operation or directive | встроенная форма → `actor` |
| `naven` | na-ven | messages, concurrency and supervision; initiate, declare or create; a named object, type or resource | встроенная форма → `actor_send` |
| `navir` | na-vir | messages, concurrency and supervision; initiate, declare or create; a link, rule or connection | встроенная форма → `actor_drain` |
| `navum` | na-vum | messages, concurrency and supervision; initiate, declare or create; a value, condition or result | встроенная форма → `actor_state` |
| `neva` | ne-va | messages, concurrency and supervision; observe, check or validate; an operation or directive | встроенная форма → `supervisor` |
| `neven` | ne-ven | messages, concurrency and supervision; observe, check or validate; a named object, type or resource | встроенная форма → `supervise` |
| `nevir` | ne-vir | messages, concurrency and supervision; observe, check or validate; a link, rule or connection | встроенная форма → `supervisor_status` |
| `nevum` | ne-vum | messages, concurrency and supervision; observe, check or validate; a value, condition or result | встроенная форма → `channel` |
| `niva` | ni-va | messages, concurrency and supervision; calculate, convert or transform; an operation or directive | встроенная форма → `channel_send` |
| `niven` | ni-ven | messages, concurrency and supervision; calculate, convert or transform; a named object, type or resource | встроенная форма → `channel_receive` |
| `nivir` | ni-vir | messages, concurrency and supervision; calculate, convert or transform; a link, rule or connection | зарезервировано |
| `nivum` | ni-vum | messages, concurrency and supervision; calculate, convert or transform; a value, condition or result | зарезервировано |
| `nova` | no-va | messages, concurrency and supervision; combine, group or contain; an operation or directive | зарезервировано |
| `noven` | no-ven | messages, concurrency and supervision; combine, group or contain; a named object, type or resource | зарезервировано |
| `novir` | no-vir | messages, concurrency and supervision; combine, group or contain; a link, rule or connection | зарезервировано |
| `novum` | no-vum | messages, concurrency and supervision; combine, group or contain; a value, condition or result | зарезервировано |
| `nuva` | nu-va | messages, concurrency and supervision; finish, release or close; an operation or directive | зарезервировано |
| `nuven` | nu-ven | messages, concurrency and supervision; finish, release or close; a named object, type or resource | зарезервировано |
| `nuvir` | nu-vir | messages, concurrency and supervision; finish, release or close; a link, rule or connection | зарезервировано |
| `nuvum` | nu-vum | messages, concurrency and supervision; finish, release or close; a value, condition or result | зарезервировано |

### P — transform

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `pava` | pa-va | space, geometry and composition; initiate, declare or create; an operation or directive | встроенная форма → `voxel_grid` |
| `paven` | pa-ven | space, geometry and composition; initiate, declare or create; a named object, type or resource | встроенная форма → `voxel_set` |
| `pavir` | pa-vir | space, geometry and composition; initiate, declare or create; a link, rule or connection | встроенная форма → `voxel_remove` |
| `pavum` | pa-vum | space, geometry and composition; initiate, declare or create; a value, condition or result | встроенная форма → `voxel_get` |
| `peva` | pe-va | space, geometry and composition; observe, check or validate; an operation or directive | встроенная форма → `voxel_count` |
| `peven` | pe-ven | space, geometry and composition; observe, check or validate; a named object, type or resource | встроенная форма → `voxel_mesh` |
| `pevir` | pe-vir | space, geometry and composition; observe, check or validate; a link, rule or connection | встроенная форма → `voxel_chunks` |
| `pevum` | pe-vum | space, geometry and composition; observe, check or validate; a value, condition or result | встроенная форма → `voxel_frame_plan` |
| `piva` | pi-va | space, geometry and composition; calculate, convert or transform; an operation or directive | встроенная форма → `voxel_raycast` |
| `piven` | pi-ven | space, geometry and composition; calculate, convert or transform; a named object, type or resource | встроенная форма → `voxel_octree` |
| `pivir` | pi-vir | space, geometry and composition; calculate, convert or transform; a link, rule or connection | встроенная форма → `voxel_octree_get` |
| `pivum` | pi-vum | space, geometry and composition; calculate, convert or transform; a value, condition or result | встроенная форма → `voxel_export` |
| `pova` | po-va | space, geometry and composition; combine, group or contain; an operation or directive | встроенная форма → `voxel_spectral_profile` |
| `poven` | po-ven | space, geometry and composition; combine, group or contain; a named object, type or resource | встроенная форма → `voxel_solve_field` |
| `povir` | po-vir | space, geometry and composition; combine, group or contain; a link, rule or connection | встроенная форма → `voxel_sparsify` |
| `povum` | po-vum | space, geometry and composition; combine, group or contain; a value, condition or result | зарезервировано |
| `puva` | pu-va | space, geometry and composition; finish, release or close; an operation or directive | зарезервировано |
| `puven` | pu-ven | space, geometry and composition; finish, release or close; a named object, type or resource | зарезервировано |
| `puvir` | pu-vir | space, geometry and composition; finish, release or close; a link, rule or connection | зарезервировано |
| `puvum` | pu-vum | space, geometry and composition; finish, release or close; a value, condition or result | зарезервировано |

### L — language

| Слово | Произношение | Составной смысл | Состояние |
|---|---|---|---|
| `lava` | la-va | sound, symbol, text and expression; initiate, declare or create; an operation or directive | встроенная форма → `print` |
| `laven` | la-ven | sound, symbol, text and expression; initiate, declare or create; a named object, type or resource | встроенная форма → `syllables` |
| `lavir` | la-vir | sound, symbol, text and expression; initiate, declare or create; a link, rule or connection | встроенная форма → `rhyme_key` |
| `lavum` | la-vum | sound, symbol, text and expression; initiate, declare or create; a value, condition or result | встроенная форма → `text_profile` |
| `leva` | le-va | sound, symbol, text and expression; observe, check or validate; an operation or directive | встроенная форма → `prosody_profile` |
| `leven` | le-ven | sound, symbol, text and expression; observe, check or validate; a named object, type or resource | встроенная форма → `word_info` |
| `levir` | le-vir | sound, symbol, text and expression; observe, check or validate; a link, rule or connection | встроенная форма → `wordbook` |
| `levum` | le-vum | sound, symbol, text and expression; observe, check or validate; a value, condition or result | встроенная форма → `audio_profile` |
| `liva` | li-va | sound, symbol, text and expression; calculate, convert or transform; an operation or directive | встроенная форма → `studio_offer` |
| `liven` | li-ven | sound, symbol, text and expression; calculate, convert or transform; a named object, type or resource | встроенная форма → `capture_node` |
| `livir` | li-vir | sound, symbol, text and expression; calculate, convert or transform; a link, rule or connection | встроенная форма → `order_pipeline` |
| `livum` | li-vum | sound, symbol, text and expression; calculate, convert or transform; a value, condition or result | встроенная форма → `package_pricing` |
| `lova` | lo-va | sound, symbol, text and expression; combine, group or contain; an operation or directive | встроенная форма → `unit_economics` |
| `loven` | lo-ven | sound, symbol, text and expression; combine, group or contain; a named object, type or resource | зарезервировано |
| `lovir` | lo-vir | sound, symbol, text and expression; combine, group or contain; a link, rule or connection | зарезервировано |
| `lovum` | lo-vum | sound, symbol, text and expression; combine, group or contain; a value, condition or result | зарезервировано |
| `luva` | lu-va | sound, symbol, text and expression; finish, release or close; an operation or directive | зарезервировано |
| `luven` | lu-ven | sound, symbol, text and expression; finish, release or close; a named object, type or resource | зарезервировано |
| `luvir` | lu-vir | sound, symbol, text and expression; finish, release or close; a link, rule or connection | зарезервировано |
| `luvum` | lu-vum | sound, symbol, text and expression; finish, release or close; a value, condition or result | зарезервировано |

## 7. Writing a program in articulatory syntax

```sambu
kava temperature = 300 * K
kava particle_mass = 6.6e-26 * kg
kava profile = vava(temperature, particle_mass)

tava square(value) {
  tavum value * value
}

teva square(5) > 0 {
  lava(profile.rms)
  lava(square(5))
} teven {
  lava(0)
}
```

The sample uses:
- `kava` for immutable declaration;
- `vava` for the existing `maxwell` scientific function;
- `tava` / `tavum` for function / return;
- `teva` / `teven` for conditional / alternative branch;
- `lava` for the interpreter's normal output function.

The program produces the same runtime values as its canonical-keyword equivalent.

## 8. Tooling

List the full dictionary:

```bash
sambu lexicon
sambu lexicon --status active
sambu lexicon --status reserved
sambu lexicon --family V
sambu lexicon --json
```

The headless IDE completion list includes all executable articulatory words. Reserved words remain discoverable through `wordbook` and the CLI but are not offered as executable completions.

## 9. Compatibility and guarantees

- Articulatory words are exact, lowercase, case-sensitive identifiers.
- The lexer normalizes reserved grammar forms before parsing but retains original spellings and source spans.
- Existing English-like keywords and built-ins remain supported.
- Built-in aliases point to the same callable objects as their canonical targets.
- No runtime guesswork, fuzzy spelling correction or semantic inference is used.
- The 52 reserved forms have meanings but no execution semantics.
- The wordbook is finite, deterministic and checked for exactly 200 unique forms.

**Articulatory law:** sound selects a domain, vowel selects an operation mode, ending selects the grammatical role; the compiler does not guess.
