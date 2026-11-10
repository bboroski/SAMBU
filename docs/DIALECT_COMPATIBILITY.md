# SAMBU dialect compatibility profiles

SAMBU provides three source-compatibility profiles that translate a deliberately bounded Pascal, Delphi/Object Pascal, and Fortran subset into canonical SAMBU source. They are implemented in `sambu.dialects` and use the normal SAMBU parser and runtime after translation.

These profiles are interoperability bridges, not copied compilers or full language implementations. They do not claim full ISO Pascal, Delphi, Free Pascal, or Fortran standard conformance.

## Quick start

After installing SAMBU from the repository:

```bash
# Check syntax and translation without executing the program
sambu dialect pascal examples/dialect_apps/pascal/invoice_calculator.sambu --check
sambu dialect delphi examples/dialect_apps/delphi/actor_message_service.sambu --check
sambu dialect fortran examples/dialect_apps/fortran/thermal_energy_model.sambu --check

# Translate, then execute on the SAMBU runtime
sambu dialect pascal examples/dialect_apps/pascal/invoice_calculator.sambu
sambu dialect delphi examples/dialect_apps/delphi/actor_message_service.sambu
sambu dialect fortran examples/dialect_apps/fortran/thermal_energy_model.sambu

# Inspect or export the canonical SAMBU source
sambu dialect fortran examples/dialect_apps/fortran/maxwell_speed_profile.sambu --show-translated
sambu dialect pascal examples/dialect_apps/pascal/probability_lab.sambu --emit-sambu generated_probability.sambu
```

## Compatibility matrix

| Profile | Implemented syntax subset | Deliberate exclusions |
|---|---|---|
| Pascal-style | `program`, simple `var`/`const` declarations, typed function/procedure headers, `begin/end`, `if/then/else`, inclusive `for ... to/downto ... do`, `write/writeln`, `:=`, `<>`, `div`, `mod`, common line/block comments | Full standard library, records, pointers, sets, files, units/compilation semantics, `case`, `while`, `repeat/until`, exceptions, class model and mutable variables |
| Delphi/Object Pascal-style | The shared procedural subset, semicolon-separated parameter declarations, common parameter modifiers (`const`, `var`, `out`, `in`, `constref`), program/unit headers, `uses` and visibility section markers as non-runtime metadata | Delphi class/object semantics, properties and backing fields, generics, attributes, RTTI, exceptions, VCL, FMX, Windows API, packages and native ABI. `property` declarations are skipped as metadata and do not create executable SAMBU properties |
| Fortran free-form-style | `program/module` headers, `implicit none`, simple `integer`, `int`, `real`, `double precision`, `logical`, `character` declarations, `function/subroutine`, `result`, `call`, `do` loops, block `if/then/else/end if`, `end do`, `print *`, basic `write(*,*)`, dotted boolean/comparison operators and `**` | Complete Fortran 77/90/95/2003/2008/2018 semantics, array shape/section semantics, allocatables, pointers, derived types, coarrays, modules as compiled interfaces, I/O units/formats, OpenMP/OpenACC directives, bindings and compiler intrinsics |

## Semantic boundary

- Type annotations are parsed only to identify declaration names. They are erased during translation; they do not create a SAMBU static type, layout, or ABI guarantee.
- Because source types are erased, Pascal `div` currently lowers to SAMBU `/`, not integer truncation; Fortran integer declarations likewise do not change SAMBU's numeric representation or division rules. Code that depends on integer overflow, truncation, kind selection, or exact compiler rounding must be rewritten and verified explicitly.
- SAMBU `let` bindings are immutable. A source variable may be initialized only once in a translated program. Reassignment is rejected rather than silently translated into different semantics.
- Pascal and Fortran counted loop bounds are inclusive and are lowered to SAMBU's bounded `range` implementation. The runtime's range limit still applies.
- Identifier names are case-normalized to match the case-insensitive source conventions of these profiles. Recognized SI unit symbols retain SAMBU's canonical casing (`K`, `J`, `kJ`, `eV`, `Pa`, `Hz`, `N`, `L`).
- Function/procedure declarations are lowered to SAMBU functions. A Pascal/Fortran function result variable assignment is recognized as a return only for the active function's result name.
- The translator rejects known unsupported control, memory, exception, and compiler constructs rather than pretending to implement them.
- The generated program executes in the Python-hosted SAMBU interpreter. It is not native Pascal, Delphi, or Fortran machine code and does not link to their runtimes.

## Thirty executable application examples

The examples are small console applications that exercise actual SAMBU built-ins after translation. They are source examples and regression fixtures, not GUI products or production deployment bundles.

### Pascal-style applications

| Example | SAMBU capability demonstrated |
|---|---|
| `invoice_calculator.sambu` | Percentage reduction and savings calculation |
| `gradebook_report.sambu` | Mean, sample variance and branching |
| `network_influence_map.sambu` | Directed graph metrics and influence propagation |
| `probability_lab.sambu` | Boltzmann factor, partition sum and entropy |
| `text_quality_inspector.sambu` | Lexical profile, syllable rhythm and rhyme analysis |
| `sparse_voxel_scene.sambu` | Sparse grid, mesh summary and portable export |
| `gift_batch_preview.sambu` | Validated all-or-nothing transaction preview |
| `accreditation_register.sambu` | Evidence-linked accreditation record and date status |
| `queue_capacity_planner.sambu` | Bounded worker/prefetch plan and retry schedule |
| `weekly_session_planner.sambu` | Validated recurring event schedule |

### Delphi/Object Pascal-style applications

| Example | SAMBU capability demonstrated |
|---|---|
| `actor_message_service.sambu` | Stateful actor, bounded mailbox and message drain |
| `typed_channel_mailbox.sambu` | Typed bounded channel and FIFO receive |
| `supervisor_dashboard.sambu` | Actor supervision strategy and runtime snapshot |
| `unit_economics_console.sambu` | Contribution and margin after acquisition cost |
| `experiment_analyser.sambu` | Two-proportion A/B screening estimate |
| `commerce_queue_profile.sambu` | Worker, prefetch, retry and dead-letter configuration |
| `audio_session_brief.sambu` | Validated BPM, swing, snare timing and output ceiling brief |
| `declarative_quality_filter.sambu` | Explainable 04coq filtering rules |
| `conversion_funnel_console.sambu` | Stage conversion and drop-off report |
| `package_pricing_assistant.sambu` | Package price, effective rate and savings |

### Fortran-style applications

| Example | SAMBU capability demonstrated |
|---|---|
| `thermal_energy_model.sambu` | SI temperature and thermal energy |
| `maxwell_speed_profile.sambu` | Maxwell most-probable, mean and RMS speed |
| `boltzmann_occupancy.sambu` | Boltzmann population factor |
| `partition_function.sambu` | Discrete statistical-mechanics partition sum |
| `entropy_estimator.sambu` | Shannon entropy of a probability distribution |
| `seeded_molecular_sampler.sambu` | Reproducible Maxwell-distributed sampling |
| `migration_speed_calculator.sambu` | Dimensional distance/time conversion |
| `avian_gas_exchange.sambu` | Parameterized gas-exchange proxy model |
| `plumage_insulation_model.sambu` | Comparative insulation index |
| `sparse_voxel_spectrum.sambu` | Voxel adjacency graph and sparse spectral profile |

## Verification

The project test suite includes:
- syntax/translation unit tests for all three profiles;
- source-map length checks;
- rejection tests for reassignment and unsupported constructs;
- execution tests for the thirty example applications;
- TextMate grammar tests for dialect keywords, operators and comment forms.

Run the complete suite with:

```bash
python -m unittest discover -s tests -v
```

The canonical SAMBU language reference remains authoritative for runtime semantics. A successful dialect translation means only that a source file uses this documented subset and that its generated SAMBU program can be parsed/executed.
