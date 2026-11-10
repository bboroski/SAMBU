# Duck UI system — SAMBU

**Status:** integrated in the two existing Tkinter desktop tools. This document is the visual contract for future SAMBU UI surfaces.

## Identity

Use the duck mark as a small product signature, not as a repeating decoration. The interface is a quiet engineering workspace: graphite surfaces, legible data, restrained yellow actions and clear source/diagnostic hierarchy.

## Color tokens

The machine-readable source of truth is [`design/duck-ui.tokens.json`](../design/duck-ui.tokens.json).

| Role | Token |
|---|---|
| Canvas | `#0D0D0D` |
| Panels/cards | `#1A1A1A` |
| Alternate surface | `#141414` |
| Main accent | `#FFD600` |
| Muted accent / hover | `#BFA100` |
| Selected state | `#332B00` |
| Main text | `#E6E6E6` |
| Secondary text | `#999999` |
| Disabled text | `#4D4D4D` |
| Borders | `#262626` |
| Success / warning / error | `#4CAF50` / `#FFD600` / `#FF4444` |

Yellow is reserved for primary actions, active navigation, keyboard focus, progress and high-priority warnings. It is not a general panel background.

## Interaction rules

- Primary controls use yellow with near-black text; secondary controls use graphite with a yellow outline; ghost controls stay neutral until hover.
- Keyboard focus is always visible (2 px yellow ring). Every state must remain understandable without color alone.
- Tables use fixed, readable headings, alternating `#1A1A1A` / `#141414` rows and horizontal scrolling when columns cannot fit.
- Keep diagnostics, command output and report previews inside the application. File export remains an explicit action.
- Motion is 120–250 ms, ease-out, and must respect reduced-motion settings.

## Scaling and layout

The desktop tools should follow OS DPI scaling and provide an independent UI zoom range of 80–160%. In the IDE, use the visible **+ / −** toolbar controls; in Duck Studio, use the visible **+ / −** controls in the top bar. Both also support **Ctrl +** / **Ctrl −** and **Ctrl 0**. The preference is stored under `~/.sambu/`. Keep the main workspace usable at 1366×768 and 1920×1080; reduce secondary panels before clipping the editor or report content.

## Current implementation

- `sambu_ide/app.py`: graphite/yellow editor, contrast-corrected status/output surfaces and persisted UI zoom.
- `sambu_studio/duck_gui.py`: graphite/yellow navigation, cards, report/diagnostic panes, tables, toast notifications and persisted UI zoom.
- `docs/DUCK_STUDIO.md`: previous light-theme captures are retained as historical evidence. Vector layout previews in `assets/duck-ui/` use a 1920 × 1080 canvas and are design references, not runtime screenshots.

The Tkinter core remains dependency-light. Do not add a web runtime or heavyweight UI framework solely to apply this theme.

## Screenshot policy

Capture the running application at 1920×1080 (and 1366×768 for compact layout) after setting a deterministic DEMO WORKSPACE. Screenshots must come from the running app, include no private paths or personal data, and state clearly when data is synthetic. SVG design previews must be labelled **preview**, never **screenshot**.
