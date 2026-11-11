# Repository Renovation Standard

> Shared engineering and presentation contract. Repository names, product scope, architecture, and capability claims remain repository-specific.

## 1. Purpose and principles

This standard aligns documentation, visual identity, GUI patterns, pull-request review, and technical-debt governance across the ecosystem. It does not authorize changing a repository's canonical name, scope, public API, or runtime behavior merely to make projects look alike.

**Truthfulness rule:** limitations must be described plainly. A weakness is not a feature until a user-visible capability, measurable service level, or verified mitigation exists. Use wording such as "designed for", "supports", or "planned" only when accurate; never relabel latency, missing GUI, incomplete coverage, or unsupported behavior as a delivered benefit.

## 2. Visual identity

The canonical visual source of truth is `design/duck-ui.tokens.json` (schema 3.0.0), with the complete color specification in `design/DUCK_UI_SYSTEM.md`. It defines exactly six base colors and fourteen functional shades, each with HEX, RGB, HSL and a semantic purpose. Use those tokens; do not introduce a competing palette or copy older, incompatible values into new UI or documentation.

Black and graphite form the structural foundation. Yellow is reserved for primary actions, focus and selection. Red indicates errors/destructive actions, cyan information, gray neutral hierarchy and white readable content. Status must also use text, icon or shape; color alone is never sufficient. Check contrast in the actual foreground/background pairing.

## 3. Motion and transitions

The authoritative catalogue of ten element animations and ten transition profiles—including keyframes, durations, easing, intended use and shared CSS utilities—is maintained in `design/DUCK_UI_SYSTEM.md` and `assets/duck-ui/duck-ui.css`. Do not duplicate or redefine timing values in this document.

Use motion to explain state changes, not as decoration. Prefer opacity and transform; respect `prefers-reduced-motion`; preserve the final state when motion is disabled. Persistent animation is limited to meaningful loading or live-state indicators. Native, CLI and specification-only projects must document the shared contract without claiming that graphical motion is implemented where no GUI exists.

## 4. GUI layout contract

Where the product has a GUI, prefer a clear shell with:
- Header: product mark, truthful system status, measured progress/operation count, optional activity trace, local clock only when useful.
- Main work surface: task-specific content; yellow canvas only when it improves the task, never as an obligatory full-screen background.
- Input area: structured controls plus optional freehand/vector/gesture input only when supported by the product.
- Action/control region: grouped primary and secondary actions, clear disabled/loading/error states.
- Footer/navigation: tabs or pager only when multiple workspaces exist.

Text wireframe:
```text
+------------------------------------------------------------------+
| [MARK] Status: <measured state> | <metric> | <activity> | HH:MM  |
+------------------------------------------------------------------+
| Work area: task-specific content, grid/canvas, forms or results   |
|                                                                  |
| [Primary actions]                         [Context controls]     |
+------------------------------------------------------------------+
| [Current workspace]  o  o  o  (only if multiple pages exist)     |
+------------------------------------------------------------------+
```

Do not display fabricated metrics (for example, hard-coded FPS or "55 ops"). Every metric needs a source, unit, refresh policy, and unavailable state.

## 5. Weakness-to-feature governance

Document the real limitation first, then its verified mitigation and user impact. Example mapping:

| Observed limitation | Honest product framing | Required implementation/evidence |
|---|---|---|
| High latency | Asynchronous/batched processing, if implemented | Queue/progress states, cancellation, timing metrics, documented latency distribution |
| Unstructured handwriting | Freeform annotation input, if implemented | Input model, vector/stroke capture, export and accessibility behavior |
| No built-in GUI | Headless-first/CLI integration, if intentional | Stable CLI/API contract, examples, external GUI integration docs |
| Partial platform support | Explicitly scoped portability | Platform matrix, tested versions, unsupported-state messaging |
| Technical debt | Transparent engineering roadmap | Tracked debt items, owners, risk, remediation status and release notes |

Never hide defects or rename missing functionality as a delivered feature. Keep planned, experimental, supported, and deprecated states distinct.

## 6. README contract

Every repository root must have a current README that preserves its exact canonical repository name and explains its actual purpose. Recommended order:
1. Product mark and canonical repository title.
2. One-sentence accurate summary and truthful status badges.
3. Language links where maintained (Ukrainian, English, Russian).
4. Actual capabilities and architecture overview.
5. Quick start using real commands and dependencies.
6. Tests/build/lint commands that exist in the repository.
7. GUI screenshots/wireframes under `docs/gui/` only when relevant.
8. Architecture boundaries, limitations, platform support, security/privacy notes.
9. Contribution, PR, release and support guidance.
10. Links to maintained documentation.

Do not invent `make install-yellow-env`, `npm run start:gui`, coverage percentages, build-success badges, or screenshots. Verify every command, badge endpoint, path, and claim against the repository. Archive obsolete docs only after checking inbound links and preserving historical value.

## 7. Pull request and Git governance

- Work on short-lived feature/fix/docs branches; never push directly to protected `main`, `master`, or `release`.
- Require at least two independent approvals where repository plan/team size supports it and branch protection can enforce it. Do not claim this is active until GitHub branch protection is configured and verified.
- Require all applicable CI checks; no merge with failing, skipped-required, or pending checks.
- Prefer small, reviewable PRs; link issues, document migration and rollback risks.
- Use squash/merge strategy consistently with repository policy.
- Never bypass review or required checks to meet a deadline.
- Set coverage targets per language and repository baseline. 80% is a target only where measurable and meaningful; do not falsify coverage or block safety-critical tests behind a vanity percentage.

## 8. RACI and documentation KPIs

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Code and tests | Contributor | Maintainer | Reviewer | Team |
| README/API docs | Contributor/technical writer | Maintainer | API owner | Users |
| Design tokens/GUI | UI owner | Maintainer | Accessibility reviewer | Team |
| CI/security | CI owner | Maintainer | Security reviewer | Team |
| Release notes | Release owner | Maintainer | Contributors | Users |

Track: README command validity, API-doc freshness, broken-link count, required-check pass rate, review latency, unresolved high-risk debt, accessibility findings, and documented platform coverage. Publish measured values with date and method; never fabricate targets as results.

## 9. Brand voice and marketing

Be precise, direct, user-centered, and evidence-led. Explain who the product serves, which task it solves, what is supported today, and what remains experimental. Marketing claims must be traceable to tests, benchmarks, screenshots, or release evidence. Position engineering investment as reliability, maintainability, transparency, and reduced operational risk—not as a claim that defects are features.

## 10. Completion checklist

- [ ] README reflects current code and canonical repository name.
- [ ] Commands, badges, links, screenshots, and status claims verified.
- [ ] UI uses shared tokens and accessible contrast where applicable.
- [ ] Motion catalog implemented only where it improves interaction; reduced motion respected.
- [ ] Limitations and mitigations accurately documented.
- [ ] PR template and contribution guidance present.
- [ ] CI, tests, lint, docs checks pass or failures are explicitly tracked.
- [ ] Branch protections/review rules verified rather than merely described.
- [ ] Obsolete docs archived only after link and history review.
- [ ] Ukrainian, English, and Russian docs agree in meaning and status where all three are maintained.
