# Nero Spider — flat GUI and visual contract

**Repository:** SAMBU  
**Status:** design/integration contract; runtime implementation is tracked separately.

## Repository integration
Compiler, SDK, language tooling and IDE; apply tokens to editor chrome, diagnostics and build feedback without changing language semantics.

## Visual foundation
Nero Void `#050505`; Anthracite `#121212`; dividers `#1F1F1F`; text `#F4F4F4`; Mallard Green `#006442` for verified success, trusted links and protected modules. Critical red `#FF1E1E`, warning `#F2C94C`, information `#58C7E8`. Square geometry, 1 px rules and a 2% coordinate grid. No shadows, gradients, silhouettes, 3D or skeuomorphism.

Tokens: [nero-spider.tokens.json](nero-spider.tokens.json). Luci is canonical; native mappings may differ but base tokens do not.

## Motion and motifs
100–220 ms state transitions; click ripple up to 420 ms. Duck motif is an abstract geometric line glyph, not a silhouette. Anime-inspired marks use abstract circles, triangles and typography only. Red perimeter rules denote critical findings; concentric marks denote scans; triangular cells denote verified isolation. Honor `prefers-reduced-motion`; audio and custom cursors are off by default. Preserve ordered logs and never animate away security-critical content.

## Required surfaces
Status strip (branch/SHA/CI/security/timestamp); build console (ordered logs and pending/pass/fail/unknown); dependency map (labeled nodes, severity and provenance); CI runway; quarantine details (file/hash/reason/restore policy); release timeline (commit → checks → review → artifact → deploy); audited, keyboard-accessible emergency stop.

## README and evidence
Generated `Live Security Status` may update only inside explicit markers from verified CI data. Missing/stale data is `UNKNOWN`, never `PASS`. Runtime screenshots go in `docs/screenshots/` and must come from a running application; static previews are labeled concepts.

## Acceptance gates
Validate token JSON, contrast, keyboard focus, 200% zoom, reduced motion and 44 px touch targets where applicable. Check SVG/CSS for gradients, filters, shadows and silhouette artwork. Preserve this repository's native stack, API, security boundary, ownership and license.

The source manifesto contains ten detailed examples and placeholder ranges for the remaining ideas. This contract applies the supplied direction without claiming 666 individually specified features or an implemented GUI runtime.
