# ERCF-20 — Engineering Readiness & Coordination Framework

**Repository:** bboroski/SAMBU  
**Version:** 1.0.0  
**Status:** Adopted as a validation contract; capability maturity remains evidence-driven.

## Purpose

ERCF-20 turns the twenty supplied three-part concepts into a practical, reviewable engineering control model for this repository. It is a software-readiness framework, not a military capability model. Terms such as вооружение, боеготовность and мобилизация are interpreted strictly as provisioning, authorization, release readiness and controlled activation of software resources. They do not authorize weapons, physical actuation, privileged hardware writes, destructive operations or autonomous deployment.

## Repository scope

Scientific modeling, language tooling, reproducible workflows and typed scientific data.

The framework must fit the existing architecture. It does not replace APIs, ABIs, build systems, ownership rules, hardware boundaries or established project conventions. A capability is marked implemented only when repository-local code, tests or reproducible evidence demonstrate it.

## The twenty control groups

| # | Supplied three-part concept | Engineering interpretation |
|---:|---|---|
| 01 | Вооружённость · Волеизъявление · Согласование | Capability inventory, explicit intent and interface agreement |
| 02 | Оснащённость · Волевое решение · Синхронизация | Available resources, approved decisions and deterministic synchronization |
| 03 | Укомплектованность · Вооружение · Сопряжение | Component completeness, controlled provisioning and interface coupling |
| 04 | Экипированность · Перевооружение · Согласованность | Deployment profile, safe upgrade path and compatibility consistency |
| 05 | Снаряжённость · Переоснащение · Взаимодействие | Operational readiness, staged re-equipment and component interaction |
| 06 | Оборудованность · Оснащение · Управление | Equipment inventory, explicit configuration and lifecycle control |
| 07 | Подготовленность · Укомплектование · Регулирование | Qualification evidence, dependency completeness and bounded regulation |
| 08 | Снабжённость · Экипирование · Организация | Supply-chain provenance, reproducible setup and ownership organization |
| 09 | Усиленность · Снаряжение · Упорядочивание | Resilience margin, provisioned resources and deterministic ordering |
| 10 | Защищённость · Вооружённость · Унификация | Security posture, capability authorization and common policy alignment |
| 11 | Боеготовность · Боеспособность · Интеграция | Release readiness, functional qualification and tested integration |
| 12 | Мобилизованность · Боеготовность · Централизация | Change activation, readiness confirmation and centralized visibility |
| 13 | Техническая оснащённость · Мобилизация · Систематизация | Toolchain availability, controlled activation and structured inventories |
| 14 | Инструментальность · Укрепление · Комбинирование | Tool availability, hardening controls and composable capabilities |
| 15 | Функциональность · Усиление · Сочетание | Feature completeness, measured improvement and compatible composition |
| 16 | Самостоятельность · Обеспечение · Стыковка | Local operability, declared dependencies and explicit interface adapters |
| 17 | Независимость · Снабжение · Соединение | Portability, verified inputs and deterministic component connection |
| 18 | Ресурсность · Комплектование · Распределение | Resource budgets, bounded allocation and fair distribution |
| 19 | Потенциал · Техническое оснащение · Диспетчеризация | Measured headroom, platform provisioning and workload dispatch |
| 20 | Мощность · Самообеспечение · Оркестрация | Performance envelope, offline-safe operation and lifecycle orchestration |

## Required operating rules

1. **Declare before use.** Every dependency, capability, resource limit and external interface has an explicit owner and source.
2. **Fail closed.** Missing, malformed, stale or contradictory evidence cannot increase readiness.
3. **Bound resources.** Memory, input size, execution time, concurrency and retries have explicit limits where applicable.
4. **Preserve boundaries.** No hidden global mutation, implicit I/O, unreviewed privilege escalation, or cross-repository code execution.
5. **Synchronize deterministically.** Shared state changes have defined ordering, conflict behavior and observable outcomes.
6. **Integrate through contracts.** Adapters validate versions, sizes, ownership and error semantics; no guessed compatibility.
7. **Measure before optimizing.** Performance claims require reproducible baselines and target-specific evidence.
8. **Keep recovery explicit.** Rollback, cleanup and degraded states are documented and tested where applicable.
9. **Separate host and target evidence.** Host tests never imply firmware, kernel, driver, emulator or physical-device qualification.
10. **Review every change.** Each implementation change is isolated in a branch and PR with its own diff and checks.

## Readiness states

- declared — scope and owner are documented; no implementation claim.
- implemented — code or configuration exists and is linked to its evidence.
- verified — relevant automated tests/checks pass on the exact revision.
- qualified — required target, integration or operational evidence is attached.
- blocked — evidence is missing, failed, stale or incompatible.

Readiness is the lowest state of the required controls, never an average. Unknown is not equivalent to pass.

## Pull-request acceptance

- The machine-readable contract at .github/ercf-20.json contains exactly 20 uniquely identified groups and all 60 supplied terms.
- The ERCF-20 workflow validates the manifest with Python's standard library.
- Repository-specific checks remain authoritative for code quality and runtime behavior.
- The PR must be reviewed and all required checks must pass on its current head before merge.
- No check is fabricated, skipped, or bypassed. Protected-branch rules remain in force.

## Non-goals

ERCF-20 does not claim production readiness, complete security certification, hardware qualification, automatic repair, self-modifying code, unrestricted resource allocation or cross-repository deployment. It adds a common vocabulary and a machine-checkable contract; further capabilities require separate evidence-backed PRs.

## Change control

Changes to this framework are versioned. Breaking manifest changes require a schema-version increment and migration notes. Repository-specific deviations must be documented with rationale and tests, not silently ignored.
