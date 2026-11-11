# Repository Renovation Standard

> Shared engineering and presentation contract. Repository names, product scope, architecture, and capability claims remain repository-specific.

## 1. Purpose and principles

This standard aligns documentation, visual identity, GUI patterns, pull-request review, and technical-debt governance across the ecosystem. It does not authorize changing a repository's canonical name, scope, public API, or runtime behavior merely to make projects look alike.

**Truthfulness rule:** limitations must be described plainly. A weakness is not a feature until a user-visible capability, measurable service level, or verified mitigation exists. Use wording such as "designed for", "supports", or "planned" only when accurate; never relabel latency, missing GUI, incomplete coverage, or unsupported behavior as a delivered benefit.

## 2. Visual identity

Use a high-contrast black/yellow foundation. Red and cyan/blue are semantic accents, not competing primary themes.

| Token | HEX | RGB | HSL | Use |
|---|---|---|---|---|
| Yellow 500 | #FFCC00 | 255, 204, 0 | 48°, 100%, 50% | Primary accent, selected controls |
| Yellow 400 | #FFE600 | 255, 230, 0 | 55°, 100%, 50% | Highlight, active canvas |
| Black 950 | #000000 | 0, 0, 0 | 0°, 0%, 0% | Main dark surface, outlines |
| Black 900 | #1A1A1A | 26, 26, 26 | 0°, 0%, 10% | Elevated dark surface |
| Red 600 | #E53935 | 229, 57, 53 | 1°, 77%, 55% | Error, destructive, critical |
| Cyan 400 | #29B6F6 | 41, 182, 246 | 199°, 92%, 56% | Active process, data flow |
| Gray 100 | #F5F5F5 | 245, 245, 245 | 0°, 0%, 96% | Light surface |
| Gray 300 | #D6D6D6 | 214, 214, 214 | 0°, 0%, 84% | Borders |
| Gray 500 | #808080 | 128, 128, 128 | 0°, 0%, 50% | Secondary text |
| Gray 700 | #4A4A4A | 74, 74, 74 | 0°, 0%, 29% | Muted dark surface |
| White 000 | #FFFFFF | 255, 255, 255 | 0°, 0%, 100% | Text on dark surfaces |
| Yellow 100 | #FFF7CC | 255, 247, 204 | 52°, 100%, 90% | Soft highlight |
| Red 100 | #FFEBEE | 255, 235, 238 | 351°, 100%, 96% | Error background |
| Cyan 100 | #E1F5FE | 225, 245, 254 | 198°, 100%, 94% | Info background |
| Gray 900 | #262626 | 38, 38, 38 | 0°, 0%, 15% | Strong dark text/surface |
| Gray 050 | #FAFAFA | 250, 250, 250 | 0°, 0%, 98% | Page background |
| Yellow 700 | #B38F00 | 179, 143, 0 | 48°, 100%, 35% | Dark-mode yellow text/accent |
| Red 800 | #B71C1C | 183, 28, 28 | 0°, 74%, 41% | Dark error state |
| Cyan 700 | #0277BD | 2, 119, 189 | 202°, 98%, 37% | Dark info state |
| Gray 200 | #EEEEEE | 238, 238, 238 | 0°, 0%, 93% | Dividers |
| Gray 600 | #666666 | 102, 102, 102 | 0°, 0%, 40% | Secondary dark text |

Maintain accessible contrast (WCAG 2.2 AA target for text and controls), visible keyboard focus, non-color status cues, and reduced-motion support. Do not place yellow body text on white or gray text on yellow without checking contrast.

## 3. Motion and transitions

Motion must explain state changes, not decorate every element. Use transform/opacity where possible; avoid animating layout dimensions unless needed. Respect `prefers-reduced-motion`.

### Element animation catalogue

| Pattern | Keyframe intent | Duration | Easing | Use |
|---|---|---:|---|---|
| Fade in | opacity 0 → 1 | 160ms | ease-out | Content arrival |
| Rise in | opacity + translateY(8px → 0) | 220ms | cubic-bezier(.2,.8,.2,1) | Cards/panels |
| Press | scale(1 → .98 → 1) | 120ms | ease-out | Button feedback |
| Pulse | subtle opacity/scale cycle | 1.4s | ease-in-out | Live status only |
| Shimmer | background-position sweep | 1.2s | linear | Loading skeleton |
| Spin | rotate(0 → 360deg) | 900ms | linear | Indeterminate progress |
| Draw | stroke-dashoffset full → 0 | 600ms | ease-in-out | Vector paths |
| Shake | small horizontal offsets | 260ms | ease-in-out | Invalid input |
| Expand | opacity + scale(.98 → 1) | 180ms | ease-out | Disclosure |
| Progress | scaleX(0 → measured value) | data-driven | linear | Measured progress |

### Transition catalogue

| Transition | Duration | Easing | Use |
|---|---:|---|---|
| Color/background | 140ms | ease-out | Hover/active |
| Border/focus | 120ms | ease-out | Focus state |
| Button press | 100ms | ease-in | Press feedback |
| Tooltip | 120ms | ease-out | Tooltip |
| Popover | 160ms | ease-out | Menus |
| Modal | 200ms | cubic-bezier(.2,.8,.2,1) | Dialog |
| Drawer | 240ms | cubic-bezier(.2,.8,.2,1) | Side panel |
| Tab indicator | 180ms | ease-in-out | Navigation |
| Page content | 220ms | ease-out | Route/content swap |
| Alert | 180ms | ease-out | Notice entry/exit |

Example keyframes (adapt names/tokens to the host UI):
```css
@keyframes duck-fade-in { from { opacity: 0 } to { opacity: 1 } }
@keyframes duck-rise-in { from { opacity: 0; transform: translateY(8px) } to { opacity: 1; transform: translateY(0) } }
@keyframes duck-draw { to { stroke-dashoffset: 0 } }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
```

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
