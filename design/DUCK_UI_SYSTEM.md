# Duck Black / Yellow — UI standard

This repository follows the shared Duck Black / Yellow visual contract. Repository names, technical module names, public interfaces and runtime boundaries remain unchanged.

## Foundation

- Canvas: `#0D0D0D`; graphite surfaces: `#141414`, `#171717`, `#1D1D1D`.
- Primary accent: `#FFD600`; hover: `#FFE34D`; pressed: `#BFA100`; selected: `#332B00`.
- Primary text: `#F2F2F2`; secondary text: `#C4C4C4`; muted text: `#A3A3A3`.
- Semantic states stay distinct: success green, warning yellow, error red. Every state must also carry text or an icon.
- Yellow is reserved for primary actions, focus, selected navigation, progress and high-priority warnings. It is not a large decorative fill.

## Layout and components

Use a persistent top control region, a stable navigation rail where useful, a primary work canvas and contextual side/bottom panels. Keep panel roles explicit. Prefer graphite value steps over excessive borders; use a yellow outline only for the active target or focus.

Buttons and form controls are at least 40 px high; touch targets are at least 44 px. Small drag handles and knobs may stay visually compact only when their pointer/touch capture region is expanded. Cards use 12 px radius, controls 8 px and pills full radius. Use tabular numerals for counters, timecodes and measurements.

The shared stylesheet is `assets/duck-ui/duck-ui.css`; machine-readable values are in `design/duck-ui.tokens.json`; the vector component board is `assets/duck-ui/duck-ui-preview.svg`. The primary vector mark is `assets/duck-ui/duck-mark.svg`.

## Motion and feedback

Use short press depth, subtle hover elevation, 110–240 ms transitions and clear pending/success/error states. Never make hover the only feedback. Respect `prefers-reduced-motion`; keyboard focus must remain visible and high contrast.

## Dense technical workspaces

For timelines, graphs, editors and diagnostic grids, keep primary data brighter than decoration. Use yellow for the active trace or selection, muted gold for secondary traces and neutral graphite grid lines. Keep a stable relationship between object lists and their corresponding rows. Double-code mute, warning, selected and failure states with labels/icons as well as color.

## Accessibility and validation

Target at least 4.5:1 contrast for normal text and 3:1 for large text. Preserve browser zoom and user UI scaling. Test keyboard-only navigation, 200% zoom, reduced motion, narrow layouts and color-deficiency simulations. Do not claim a UI or runtime capability merely because a design asset depicts it.

## Repository adaptation

- Web surfaces: load the shared stylesheet and use the `duck-*` component classes or map local classes to these tokens.
- Desktop surfaces: mirror the token values in native theme configuration; preserve native focus, keyboard and scaling behavior.
- CLI and specification-only repositories: keep terminal output and documentation legible using the same semantic colors and typography; do not fabricate a GUI where no application UI exists.
