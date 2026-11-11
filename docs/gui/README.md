# SAMBU GUI concept

This folder contains a standalone, responsive interface prototype for the SAMBU scientific workspace.

- `index.html` — interactive browser UI with module filtering, navigation states and local preview actions.
- `preview.svg` — 1600×900 vector composition of the intended workspace.
- Theme: Duck Black / Yellow with restrained cyan and green status accents.
- Motion: short hover and state transitions; respects `prefers-reduced-motion`.
- Accessibility: semantic landmarks, labelled search, keyboard-operable buttons and live status feedback.

**Data boundary:** all displayed counts and activity entries are illustrative sample data. The prototype does not execute SAMBU code, run scientific models or access project files. It is a design implementation, not a production integration.

Open `index.html` directly in a modern browser. No build step or external runtime dependency is required.
