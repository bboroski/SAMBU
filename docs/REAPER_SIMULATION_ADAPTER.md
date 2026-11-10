# SAMBU — Reaper cycle simulation adapter

## Role

SAMBU may use the Reaper-themed cycle as a reproducible scientific-computing workload: seeded state evolution, bounded iterations, phase accounting, and deterministic reports. The workflow belongs in SAMBU's modeling and verification layers; it is not a new instruction set or a biological processing feature.

## Contract

- Use unsigned 64-bit arithmetic semantics when matching the C reference model in ReaperCripple.
- Treat 6666 as a workload ceiling, not as a number of source lines or a hardware register width.
- Require an explicit non-zero seed and an explicit iteration count from 1 through 6666.
- Separate synthetic source values, transformed values, aggregate state, and event digest.
- Record model version, seed, iteration count, and implementation version with each reproducible experiment.
- Mark all outputs as simulated; never label them as physical measurements.

## Phase mapping

DISCOVERY -> VALIDATION -> HARVEST -> LIQUEFACTION -> SYNTHESIS -> VERIFICATION -> COMMIT is a domain-level sequence. SAMBU can model it as typed records or workflow nodes. Runtime dependency resolution, source parsing, and scientific unit validation remain SAMBU responsibilities.

## Interoperability

The C reference implementation is maintained in ReaperCripple. Its contract is documented in docs/REAPER_SYNTHESIS_CORE.md. A future SAMBU adapter must compare deterministic outputs against a pinned reference vector before claiming cross-language compatibility.

## Non-goals

No claim of quantum execution, 666-bit arithmetic, real Element Zero physics, physical harvesting, weapon control, or autonomous source mutation is made by this adapter.
