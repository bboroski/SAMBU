# Amber–Obsidian UI system — SAMBU

**Status:** integrated in the two existing Tkinter desktop tools. This document is the visual contract for future SAMBU UI surfaces.

## Identity

Use the duck mark as a small product signature, not as a repeating decoration. The interface is a quiet engineering workspace: graphite surfaces, legible data, restrained amber actions and clear source/diagnostic hierarchy.

## Color tokens

The machine-readable source of truth is [`design/duck-ui.tokens.json`](../design/duck-ui.tokens.json).

| Role | Token |
|---|---|
| Canvas | `#0B0B0D` |
| Panels/cards | `#1C1C1E` |
| Alternate surface | `#141416` |
| Main accent | `#FF9F0A` |
| Muted accent / hover | `#D97706` |
| Selected state | `#3A2408` |
| Main text | `#F5F3EE` |
| Secondary text | `#A6A3AB` |
| Disabled text | `#77747C` |
| Borders | `#34343A` |
| Success / warning / error | `#64C787` / `#FF9F0A` / `#F16D65` |

amber is reserved for primary actions, active navigation, keyboard focus, progress and high-priority warnings. It is not a general panel background.

## Interaction rules

- Primary controls use amber with near-black text; secondary controls use graphite with a amber outline; ghost controls stay neutral until hover.
- Keyboard focus is always visible (2 px amber ring). Every state must remain understandable without color alone.
- Tables use fixed, readable headings, alternating `#1C1C1E` / `#141416` rows and horizontal scrolling when columns cannot fit.
- Keep diagnostics, command output and report previews inside the application. File export remains an explicit action.
- Motion is 120–250 ms, ease-out, and must respect reduced-motion settings.

## Scaling and layout

The desktop tools should follow OS DPI scaling and provide an independent UI zoom range of 80–160%. In the IDE, use the visible **+ / −** toolbar controls; in Duck Studio, use the visible **+ / −** controls in the top bar. Both also support **Ctrl +** / **Ctrl −** and **Ctrl 0**. The preference is stored under `~/.sambu/`. Keep the main workspace usable at 1366×768 and 1920×1080; reduce secondary panels before clipping the editor or report content.

## Current implementation

- `sambu_ide/app.py`: graphite/amber editor, contrast-corrected status/output surfaces and persisted UI zoom.
- `sambu_studio/duck_gui.py`: graphite/amber navigation, cards, report/diagnostic panes, tables, toast notifications and persisted UI zoom.
- `docs/DUCK_STUDIO.md`: previous light-theme captures are retained as historical evidence. Vector layout previews in `assets/duck-ui/` use a 1920 × 1080 canvas and are design references, not runtime screenshots.

The Tkinter core remains dependency-light. Do not add a web runtime or heavyweight UI framework solely to apply this theme.

## Screenshot policy

Capture the running application at 1920×1080 (and 1366×768 for compact layout) after setting a deterministic DEMO WORKSPACE. Screenshots must come from the running app, include no private paths or personal data, and state clearly when data is synthetic. SVG design previews must be labelled **preview**, never **screenshot**.


## Amber–Obsidian v2 alignment

This legacy design contract is aligned with the repository-specific palette and visual system v2. See [the current interface specification](INTERFACE_DESIGN.md) and the machine-readable [design tokens](../design/duck-ui.tokens.json). The project accent is #FF9F0A; secondary data signal is #A78BFA. The embedded target/library core must remain presentation-free where the product boundary requires it.
