# NEON SYNDICATE — interface and visual specification

**Repository:** SAMBU  
**Project focus:** Scientific Modeling & Automation Environment  
**Theme:** Cyberpunk / Industrial / Dystopian Noir

## Identity
A precision-first engineering workspace that pairs dense scientific tooling with a cinematic cyber-noir surface. This is an original visual direction; do not copy proprietary Cyberpunk 2077 artwork, logos, characters or interface assets.

## Color system
- Void Black `#050505`: canvas and deep contrast.
- Warning Yellow `#FCEE0A`: primary actions, selected states and critical attention.
- System Red `#FF003C`: errors and blocked states.
- Data Blue `#00F0FF`: links, technical highlights and informational telemetry.
- Interface White `#FFFFFF`: primary text.
- Carbon surfaces `#0D1115` and `#11171C`; muted text `#A6B2BC`.

Never encode state by color alone. Pair red, cyan and yellow with labels, icons or shape changes.

## Typography
Use Orbitron or Rajdhani for uppercase display headings, Rajdhani or a system sans serif for body copy, and Roboto Mono / Share Tech Mono for code, IDs and numeric readouts. Provide local/system fallbacks; the interface must not depend on remote font delivery.

## Layout and components
Use a stable desktop navigation rail, a high-contrast work canvas and contextual panes. Group editor, project structure, output and diagnostics into explicit surfaces. Use chamfered panel corners, thin separators, subtle hexagonal texture and tabular numerals. Primary controls are yellow with near-black text; secondary actions stay graphite with cyan or yellow outlines.

## Effects and motion
Apply edge glows sparingly; keep them away from dense text. Use 120–260 ms transitions, subtle hover elevation and short state feedback. Glitch effects must never obscure code, diagnostics, selection or keyboard focus. Respect `prefers-reduced-motion`.

## Accessibility
Maintain visible keyboard focus, high contrast, at least 40 px control heights and 44 px touch targets where applicable. Do not make hover the only feedback. On compact screens, collapse secondary panes before clipping the editor or diagnostics.

## SAMBU application focus
- Language editor, lexer/parser feedback and source navigation.
- Scientific model and dimensional-check surfaces.
- Sparse voxel and graph inspection.
- Local workflow and diagnostic views.

The accompanying SVG is a 1920×1200 vector design concept, not a screenshot of a running Tkinter process. The current Tkinter palette is defined in `sambu_ide/app.py` and `sambu_studio/duck_gui.py`.

## Screenshot policy
Real runtime captures must be recorded from the launched app at a stated viewport (prefer 1920×1080; include 1366×768 for compact layouts). Keep synthetic data labelled, remove personal paths and secrets, and never present an SVG mockup as a runtime screenshot. Existing 1280×818 raster captures are historical references to a previous visual revision.

## Files
- `assets/neon-syndicate/overview.svg`: vector UI and workflow concept.
- `assets/neon-syndicate/theme.css`: reusable web theme layer.
- `design/neon-syndicate.tokens.json`: machine-readable brand tokens.
