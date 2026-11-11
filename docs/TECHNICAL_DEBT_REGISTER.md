# Technical Debt Register

**Snapshot date:** 2026-11-11  
**Assessment state:** structural inventory only; source-level correctness, runtime security, performance and target-platform behavior have not been fully audited.

An empty table is not a declaration that technical debt is absent. Add an entry only when a finding has reproducible evidence. Do not invent debt to fill the register.

## Risk scale

- **Critical:** exploitable vulnerability, data loss or system-wide outage.
- **High:** major failure of a core workflow, unsafe state or serious compatibility break.
- **Moderate:** recurring defect, maintainability barrier or material operational limitation.
- **Low:** contained cleanup or minor inconsistency.

## Open findings

| ID | Area | Evidence | Impact / risk | Next action | Status |
|---|---|---|---|---|---|
| — | No source-level finding recorded by this structural inventory | Full code and runtime audit remains pending | Not assessed | Record reproducible findings during the next focused audit | Not assessed |

## Required fields for new entries

Record a stable ID, subsystem, exact evidence or reproduction, impact, likelihood, severity, affected versions/platforms, owner or responsible role, mitigation, remediation action, target milestone, status and verification evidence.

Allowed statuses: `identified`, `triaged`, `planned`, `in_progress`, `mitigated`, `resolved`, `accepted`.

Accepted debt requires a written reason, compensating control and review date. Security-critical or data-loss risks cannot be accepted solely to meet a release date. Close an entry only after the fix is merged and its verification evidence is recorded.
