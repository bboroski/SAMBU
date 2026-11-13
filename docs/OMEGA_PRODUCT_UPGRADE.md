# OMEGA product upgrade — SAMBU

**Track:** 7.7.7-OMEGA product and visual modernization  
**Status:** Engineering plan / acceptance contract; implementation status must be proven separately.  
**Branch:** `feat/omega-product-design-upgrade`

## Product responsibility

Core tooling and shared engineering services.

## Architecture upgrade

Keep host-side tooling, data processing, diagnostics and platform adapters independently testable. Expose stable, versioned interfaces; keep optional GPU and E2K paths behind explicit capability detection.

### Required engineering rules

1. Preserve the repository's language, ABI, license, build system and ownership boundaries unless a separately reviewed migration proves a better path.
2. Make capabilities explicit and versioned. Prefer narrow adapters and schemas over cross-repository source copying or implicit shared state.
3. Keep platform-specific code behind capability detection or target profiles. Unsupported capabilities must fail clearly.
4. Use deterministic configuration, stable serialization, bounded resource use and explicit error types at public boundaries.
5. Separate implemented, partial, planned, simulated and unavailable features in both API and UI.
6. Avoid claiming zero overhead, real-time performance, production readiness or hardware support without reproducible measurements on the named target.

## Product and graphical-design upgrade

Use the existing Duck Black / Yellow visual contract. Build dense workspaces with a clear primary canvas, navigation rail, diagnostics drawer and persistent run status. Reuse existing `assets/duck-ui` assets and tokens rather than creating a competing theme.

### Shared visual quality gates

- Respect the repository's established brand and canonical tokens; do not overwrite a product identity merely to make every application look identical.
- Provide responsive layouts, visible keyboard focus, keyboard-only operation, browser/OS scaling and reduced-motion behavior where the platform supports them.
- Target WCAG 2.2 AA contrast: 4.5:1 for normal text and 3:1 for large text and meaningful UI graphics.
- Every state has a textual or shape/icon cue; color is never the sole carrier of meaning.
- Use consistent spacing, typography, component states, empty/loading/error states and clear hierarchy.
- Use SVG for scalable diagrams and iconography. Label static mockups as concepts and sample data as sample data.
- Capture screenshots only from a running application and record build/revision metadata. A static mockup is not runtime evidence.

## Verification gates

| Gate | Required evidence |
|---|---|
| Repository integrity | Existing tests and build instructions remain valid |
| Contract integrity | Schema/API compatibility tests and versioned fixtures |
| Platform support | Build/test result for each claimed target |
| Performance | Reproducible benchmark, workload, hardware and compiler metadata |
| Accessibility | Contrast, focus, keyboard, scaling and reduced-motion checks |
| Visual regression | Reviewed screenshots or deterministic SVG/component snapshots |
| Release readiness | Changelog, migration notes, license and artifact provenance |

## Delivery sequence

1. Inventory current application surfaces, entry points, dependencies and test coverage.
2. Add characterization tests before changing behavior.
3. Establish or map design tokens and reusable components.
4. Implement the highest-value user workflow without changing unrelated interfaces.
5. Add automated contract, accessibility and visual checks.
6. Publish measured results and mark unsupported items as planned.

## Non-goals

This document does not claim that a GUI, compiler backend, JIT, solver, GPU renderer, native package or hardware integration exists. Each capability becomes **implemented** only when source code, tests and reproducible evidence are present.
