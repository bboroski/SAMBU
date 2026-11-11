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


<!-- DUCK_STANDARD_ADDENDUM_2026 -->
## Extended palette — six base colors and fourteen functional shades

The brand palette has exactly six base colors: signal yellow, structural black, alert red, information blue, neutral gray and clean white. Fourteen functional shades extend those bases. HEX is canonical; RGB and HSL are derived equivalents. Existing semantic compatibility tokens (such as success green) remain status-only and do not count as additional brand base colors.

| Type / role | HEX | RGB | HSL |
|---|---|---|---|
| Base · Signal yellow | `#FFD600` | `rgb(255, 214, 0)` | `hsl(50.4, 100%, 50%)` |
| Base · Structural black | `#0D0D0D` | `rgb(13, 13, 13)` | `hsl(0, 0%, 5.1%)` |
| Base · Alert red | `#FF4D4F` | `rgb(255, 77, 79)` | `hsl(359.3, 100%, 65.1%)` |
| Base · Information blue | `#38BDF8` | `rgb(56, 189, 248)` | `hsl(198.4, 93.2%, 59.6%)` |
| Base · Neutral gray | `#808080` | `rgb(128, 128, 128)` | `hsl(0, 0%, 50.2%)` |
| Base · Clean white | `#F5F5F5` | `rgb(245, 245, 245)` | `hsl(0, 0%, 96.1%)` |
| Shade · Yellow hover | `#FFE34D` | `rgb(255, 227, 77)` | `hsl(50.6, 100%, 65.1%)` |
| Shade · Yellow pressed | `#BFA100` | `rgb(191, 161, 0)` | `hsl(50.6, 100%, 37.5%)` |
| Shade · Yellow selected | `#332B00` | `rgb(51, 43, 0)` | `hsl(50.6, 100%, 10%)` |
| Shade · Black surface | `#141414` | `rgb(20, 20, 20)` | `hsl(0, 0%, 7.8%)` |
| Shade · Black raised surface | `#1D1D1D` | `rgb(29, 29, 29)` | `hsl(0, 0%, 11.4%)` |
| Shade · Black border | `#303030` | `rgb(48, 48, 48)` | `hsl(0, 0%, 18.8%)` |
| Shade · Red hover | `#FF7072` | `rgb(255, 112, 114)` | `hsl(359.2, 100%, 72%)` |
| Shade · Red muted surface | `#351717` | `rgb(53, 23, 23)` | `hsl(0, 39.5%, 14.9%)` |
| Shade · Blue hover | `#60C9F5` | `rgb(96, 201, 245)` | `hsl(197.7, 88.2%, 66.9%)` |
| Shade · Blue muted surface | `#102A38` | `rgb(16, 42, 56)` | `hsl(201, 55.6%, 14.1%)` |
| Shade · Secondary gray | `#A3A3A3` | `rgb(163, 163, 163)` | `hsl(0, 0%, 63.9%)` |
| Shade · Muted gray | `#6B7280` | `rgb(107, 114, 128)` | `hsl(220, 8.9%, 46.1%)` |
| Shade · Secondary white | `#C4C4C4` | `rgb(196, 196, 196)` | `hsl(0, 0%, 76.9%)` |
| Shade · Pure white | `#FFFFFF` | `rgb(255, 255, 255)` | `hsl(0, 0%, 100%)` |

Use yellow for primary actions, selected navigation, progress and keyboard focus; black/graphite for structural surfaces; red for destructive/error states; blue for information; gray for secondary hierarchy; white for primary readable text. Never use color as the only status signal. Preserve semantic green success as a status-only compatibility token where an established UI relies on it.

## Motion system — ten element animations

The shared CSS implementation is `assets/duck-ui/duck-ui.css`. Apply one-shot motion to state changes, not to every element on every render. Never animate large amounts of diagnostic data or critical text.

| Animation | CSS keyframes | Timing | Easing | Intended use |
|---|---|---|---|---|
| fade-in | `duck-fade-in` | 180 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | New content, tooltips and non-blocking status updates |
| rise-in | `duck-rise-in` | 220 ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Cards and contextual panels entering the workspace |
| scale-in | `duck-scale-in` | 180 ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Small popovers and compact controls |
| slide-in-inline | `duck-slide-in-inline` | 220 ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Side panels and navigation drawers |
| pulse-soft | `duck-pulse-soft` | 900 ms; one cycle | `ease-in-out` | One-shot attention cue for a newly selected item |
| shimmer | `duck-shimmer` | 1200 ms; while loading | `linear` | Skeleton placeholders only; never real data |
| spin | `duck-spin` | 900 ms; while loading | `linear` | Small indeterminate progress indicator |
| progress-fill | `duck-progress-fill` | 260 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Progress value changes |
| shake | `duck-shake` | 260 ms; one cycle | `cubic-bezier(0.36, 0.07, 0.19, 0.97)` | Invalid form field after attempted submission |
| breathe | `duck-breathe` | 1800 ms; optional loop | `ease-in-out` | Subtle idle emphasis on a single active surface; avoid on dense data |

Canonical keyframe implementation:

```css
@keyframes duck-fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes duck-rise-in { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes duck-scale-in { from { opacity: 0; transform: scale(.96); } to { opacity: 1; transform: scale(1); } }
@keyframes duck-slide-in-inline { from { opacity: 0; transform: translateX(16px); } to { opacity: 1; transform: translateX(0); } }
@keyframes duck-pulse-soft { 0%, 100% { box-shadow: 0 0 0 0 #FFD60000; } 50% { box-shadow: 0 0 0 4px #FFD60025; } }
@keyframes duck-shimmer { from { background-position: 180% 0; } to { background-position: -180% 0; } }
@keyframes duck-spin { to { transform: rotate(360deg); } }
@keyframes duck-progress-fill { from { width: 0; } to { width: var(--duck-progress-to, 100%); } }
@keyframes duck-shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-4px); } 75% { transform: translateX(4px); } }
@keyframes duck-breathe { 0%, 100% { box-shadow: 0 0 0 0 #FFD60000; } 50% { box-shadow: 0 0 0 3px #FFD60018; } }
```

The utility classes use the durations/easing in the table. Shimmer is restricted to skeletons; spin to compact loading indicators; shake to a single invalid field; breathe is opt-in and must not become ambient motion.

## Transition system — ten interaction transitions

| Transition | Properties | Timing | Easing | Intended use |
|---|---|---|---|---|
| color | `color, background-color, border-color` | 160 ms | `ease` | Text, icons and semantic color changes |
| surface | `background-color, border-color, box-shadow` | 180 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Cards, controls and hover surfaces |
| transform | `transform` | 180 ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Press depth, lift and drag affordances |
| opacity | `opacity` | 140 ms | `linear` | Visibility and disabled-state changes |
| panel | `transform, opacity` | 220 ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Navigation rail and side panel open/close |
| modal | `transform, opacity` | 200 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Dialog and modal entry/exit |
| tab | `color, background-color, transform` | 180 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Tab bar and segmented-control selection |
| toast | `transform, opacity` | 200 ms | `cubic-bezier(0.16, 1, 0.3, 1)` | Alerts and toast notifications |
| layout | `grid-template-columns, gap, width, max-width` | 240 ms | `cubic-bezier(0.2, 0.8, 0.2, 1)` | Workspace density and responsive panel layout |
| progress | `width` | 260 ms | `linear` | Determinate progress bars |

Use the corresponding `.duck-transition-*` utility classes in the shared stylesheet. Transitions must not delay destructive-action feedback, error messages or keyboard focus. Use transform/opacity for overlays instead of animating expensive layout properties unless the panel layout genuinely needs to reflow.

## Reduced motion and performance

Respect `prefers-reduced-motion: reduce` globally. In reduced-motion mode, remove spatial travel, looping shimmer/spin/pulse/breathe and non-essential scale; use an immediate state change or a brief opacity fade. Avoid layout thrashing, forced synchronous reflow and animating box-shadow on large surfaces. Keep animation durations under 260 ms for ordinary interactions; loading indicators may loop only while work is actually pending. Motion must never imply that an operation succeeded before the application confirms it.

## Visual system acceptance checks

- All six base colors and fourteen shades are sourced from `design/duck-ui.tokens.json`; do not maintain a second divergent palette.
- `assets/duck-ui/duck-ui.css` contains the ten keyframes and ten transition utility classes.
- Keyboard focus, contrast, status text/icon, reduced motion and small viewport behavior are checked.
- Static preview assets are not described as runtime screenshots.
- Repository names, public APIs, paths, runtime boundaries and license terms remain unchanged.

See also: [Engineering Governance](../docs/ENGINEERING_GOVERNANCE.md) for branding, marketing, RACI, documentation KPIs, GitFlow, PR and technical-debt controls.
