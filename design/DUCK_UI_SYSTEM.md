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

## Material system: glass, metal and paper

The shared stylesheet exposes three optional, semantic surface treatments: `.duck-glass`, `.duck-metal` and `.duck-paper`. Use them by content role, not as decoration on every card.

- **Glass** is a translucent, layered surface with backdrop blur and a fully opaque fallback. CSS blur is visual depth, not physically accurate refraction. True optical refraction is an optional renderer-specific enhancement and must have a measured GPU budget.
- **Metal** uses a restrained directional highlight and layered graphite gradients. A static highlight is the default; any window- or pointer-reactive reflection must be subtle, non-blocking and disabled under reduced motion.
- **Paper** is reserved for notes, annotations and document previews. It may use a quieter night tint through an explicit `data-cycle="night"` preference; never infer a user's schedule or silently change work content.

Material effects never replace hierarchy, text labels, focus indicators or semantic status. Every surface needs a readable no-backdrop-filter fallback. Preserve contrast, keyboard operation, browser/OS scaling and reduced-motion preferences. Do not place critical diagnostics on low-contrast or animated surfaces.

## Release evidence for visual changes

A material effect is considered integrated only when the running application uses the shared stylesheet, the opaque fallback is checked, keyboard focus and high-contrast states are verified, reduced-motion behavior is tested, and screenshots are captured from the running application. SVG boards and static previews are design references, not implementation evidence.


## Duck System 3.0 — extended visual and motion contract

This section extends schema `3.0.0`. Existing component geometry, semantic roles, platform-specific constraints and runtime behavior remain authoritative. Apply tokens before local overrides; do not rename repository identifiers or public APIs.

### Six base colors

| Base color | HEX | RGB | HSL | Functional role |
|---|---|---|---|---|
| yellow | `#FFD600` | `rgb(255, 214, 0)` | `hsl(50.4 100% 50%)` | Primary action, focus and selection |
| black | `#0D0D0D` | `rgb(13, 13, 13)` | `hsl(0 0% 5.1%)` | Canvas and structural foundation |
| red | `#FF6262` | `rgb(255, 98, 98)` | `hsl(0 100% 69.2%)` | Error and destructive state |
| cyan | `#42C7E8` | `rgb(66, 199, 232)` | `hsl(191.9 78.3% 58.4%)` | Information and active data |
| gray | `#808080` | `rgb(128, 128, 128)` | `hsl(0 0% 50.2%)` | Neutral hierarchy and supporting graphics |
| white | `#F2F2F2` | `rgb(242, 242, 242)` | `hsl(0 0% 94.9%)` | Primary text and high-contrast surfaces |

### Fourteen functional shades

| Shade token | HEX | RGB | HSL | Functional role |
|---|---|---|---|---|
| yellow-hover | `#FFE34D` | `rgb(255, 227, 77)` | `hsl(50.6 100% 65.1%)` | Hover feedback |
| yellow-pressed | `#BFA100` | `rgb(191, 161, 0)` | `hsl(50.6 100% 37.5%)` | Pressed state |
| yellow-selected | `#332B00` | `rgb(51, 43, 0)` | `hsl(50.6 100% 10%)` | Selected surface |
| black-elevated | `#101010` | `rgb(16, 16, 16)` | `hsl(0 0% 6.3%)` | Elevated canvas |
| graphite | `#171717` | `rgb(23, 23, 23)` | `hsl(0 0% 9%)` | Default surface |
| graphite-raised | `#1D1D1D` | `rgb(29, 29, 29)` | `hsl(0 0% 11.4%)` | Raised panel |
| graphite-hover | `#242424` | `rgb(36, 36, 36)` | `hsl(0 0% 14.1%)` | Hovered surface |
| graphite-pressed | `#2B2B2B` | `rgb(43, 43, 43)` | `hsl(0 0% 16.9%)` | Pressed surface |
| gray-border | `#303030` | `rgb(48, 48, 48)` | `hsl(0 0% 18.8%)` | Standard divider |
| gray-strong | `#484848` | `rgb(72, 72, 72)` | `hsl(0 0% 28.2%)` | Strong divider |
| gray-muted | `#A3A3A3` | `rgb(163, 163, 163)` | `hsl(0 0% 63.9%)` | Muted text |
| white-secondary | `#C4C4C4` | `rgb(196, 196, 196)` | `hsl(0 0% 76.9%)` | Secondary text |
| red-surface | `#351717` | `rgb(53, 23, 23)` | `hsl(0 39.5% 14.9%)` | Error surface |
| cyan-surface | `#10232B` | `rgb(16, 35, 43)` | `hsl(197.8 45.8% 11.6%)` | Information surface |

Use the six base colors as the system palette and the fourteen shades as functional UI tokens. Semantic status remains explicit: success uses the existing success token, warning uses yellow, error uses red and information uses cyan. Never infer status from hue alone; pair it with label, icon, shape or accessible live text. Do not use muted shades for body text unless the contrast requirement is verified for the actual background.

### Ten element animations

The stylesheet `assets/duck-ui/duck-ui.css` provides the listed utility classes and keyframes. Apply animation to the entering or changing element, not to the whole workspace. Persistent, looping motion is reserved for a live indicator, spinner, skeleton or indeterminate progress. Do not animate critical telemetry, rapidly changing counters, or large data tables.

| Animation | CSS utility | Duration | Easing | Purpose |
|---|---|---:|---|---|
| Fade-in | `.duck-animate-fade-in` | 160 ms | `ease-out` | Reveal content without spatial movement |
| Rise-in | `.duck-animate-rise-in` | 200 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Enter a card, panel or contextual surface |
| Scale-in | `.duck-animate-scale-in` | 180 ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Open compact popovers and dialogs |
| Slide-inline | `.duck-animate-slide-inline` | 200 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Reveal a drawer from its origin |
| Status pulse | `.duck-animate-pulse` | 1100 ms | `ease-in-out` | Subtle live indicator, never the sole status cue |
| Spinner | `.duck-animate-spin` | 800 ms | `linear` | Indeterminate loading glyph |
| Skeleton shimmer | `.duck-animate-shimmer` | 1400 ms | `linear` | Loading placeholder |
| Validation shake | `.duck-animate-shake` | 320 ms | `cubic-bezier(0.36, 0.07, 0.19, 0.97)` | Brief invalid-input cue paired with text |
| Update highlight | `.duck-animate-highlight` | 700 ms | `ease-out` | Acknowledge refreshed data without stealing focus |
| Indeterminate progress | `.duck-animate-progress` | 1500 ms | `cubic-bezier(0.65, 0.05, 0.36, 1)` | Moving progress segment paired with accessible status text |

### Ten transition profiles

Use transitions for a state change between two existing layouts; use keyframe animations for a one-time entrance, feedback cue or loading loop. Prefer animating `opacity` and `transform`. Avoid animating expensive layout properties except for small, bounded panels and only after profiling.

| Transition | CSS utility | Properties | Duration | Easing | Use |
|---|---|---|---:|---|---|
| Page enter | `.duck-transition-page` | opacity, transform | 200 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Route/page entry |
| Page exit | `.duck-transition-page-exit` | opacity, transform | 140 ms | `ease-in` | Outgoing page |
| Modal | `.duck-transition-modal` | opacity, transform | 200 ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Dialog and modal |
| Tab indicator | `.duck-transition-tabs` | transform, background-color | 180 ms | `ease-out` | Active tab marker |
| Tab content | `.duck-transition-tab-content` | opacity, transform | 160 ms | `ease-out` | Tab panel replacement |
| Toast | `.duck-transition-toast` | opacity, transform | 180 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Alerts and notifications |
| Accordion | `.duck-transition-accordion` | grid-template-rows, opacity | 220 ms | `ease-in-out` | Disclosure sections |
| Interactive | `.duck-transition-interactive` | background, border, color, shadow, transform | 140 ms | `ease-out` | Buttons, links, fields and focus feedback |
| Layout | `.duck-transition-layout` | width, height, gap, grid-template-columns | 220 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Workspace and responsive layout |
| Overlay | `.duck-transition-overlay` | opacity | 160 ms | `ease-out` | Backdrop and scrim |

### Motion quality and accessibility

- Follow the operating-system `prefers-reduced-motion` setting. The shared stylesheet disables the animation and transition utilities under reduced motion.
- Preserve the final state when animation is disabled. No information, control or navigation may depend on motion.
- Never use flashing, strobing, parallax or an infinite decorative loop. Infinite loops are permitted only for meaningful loading or live-state indicators and must stop when the state ends.
- Motion should communicate origin, destination or cause. Do not delay an action until a decorative sequence completes.
- Avoid hover-only information and preserve keyboard focus throughout page, modal, tab and toast transitions.
- Validate animation performance on supported low-power devices and native UI stacks; CSS timing values are a reference contract, not a requirement to introduce a web renderer.

### Integration and validation

For web surfaces, load the shared stylesheet and use the utility classes or map local components to the same tokens. For desktop/native applications, implement equivalent native transitions only where the platform supports them without compromising accessibility. For CLI/specification-only projects, keep the same token contract for documentation and diagnostic output; do not claim graphical animations are implemented. A visual feature is marked **implemented** only after integration, tests and evidence from the running application.
