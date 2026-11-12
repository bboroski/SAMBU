# Nero Spider — flat GUI and visual contract

**Repository:** SAMBU  
**System:** Nero Spider / Mallard  
**Status:** design and integration contract; runtime implementation is tracked separately.

## Repository-specific integration

Compiler, SDK, language tooling and SAMBU Studio/IDE. Apply tokens to editor chrome, diagnostics, package views and build feedback without changing language semantics.

## Visual foundation

- Canvas: Nero Void `#050505`; panels: Anthracite `#121212`; separators: `#1F1F1F`.
- Primary text: `#F4F4F4`; secondary text: `#C8C8C8`; muted text: `#929292`.
- Mallard Green `#006442` is reserved for successful prebuilds, trusted links, protected modules and verified synchronization.
- Critical security state: `#FF1E1E`; warnings: `#F2C94C`; informational data: `#58C7E8`.
- All surfaces are flat and square: no shadows, gradients, silhouettes, 3D effects or skeuomorphic treatments.
- Thin pixel rules and a 2% coordinate grid provide structure without competing with content.

Machine-readable tokens: [nero-spider.tokens.json](nero-spider.tokens.json). Luci is the canonical token source; repositories may map tokens to native controls but must not fork the base palette.

## Motion and interaction

- Use 100–220 ms transitions for ordinary state changes; ripple feedback may last up to 420 ms.
- Duck motion is an abstract geometric line glyph, not a filled silhouette. Keep it small and non-blocking.
- CI progress moves left-to-right; repository synchronization uses a restrained horizontal trace.
- Logs append in source order. Do not fade, reorder or animate away security-critical content.
- Security focus uses a visible outline and labeled severity; keep the native pointer and keyboard behavior.
- Disable nonessential motion under `prefers-reduced-motion: reduce`. Audio is off by default.

## Anime-inspired geometry

Use only abstract circles, triangles, clipped rectangles, line marks and typography. Red perimeter rules indicate critical vulnerability; concentric scan marks indicate dependency analysis; triangular cells indicate verified isolation; rune-like labels are decorative only and must never replace readable security language. Do not reproduce character likenesses or silhouettes.

## GUI surfaces and operational states

1. Repository status strip: branch, commit, build state, security state and last verified timestamp.
2. Build console: ordered logs, explicit pending/pass/fail/unknown labels and accessible live announcements.
3. Dependency and vulnerability map: nodes and edges with text labels, severity and provenance.
4. CI/CD runway: deterministic progress and explicit cancellation state.
5. Quarantine: file identity, reason, hash, source event and restore policy; no destructive animation as a substitute for confirmation.
6. Release timeline: commit → checks → review → artifact → deployment, with each gate independently verifiable.
7. Emergency stop: keyboard-accessible, confirmed, audited and fail-safe; never trigger from a decorative control.

## README, screenshots and status automation

A generated `## Live Security Status` section may be refreshed by CI from verified check-run data. Missing or stale evidence must display `UNKNOWN`; never infer success. Update only content between explicit generated markers. Screenshots belong in `docs/screenshots/`; only captures from a running application may be called runtime screenshots. Static SVG previews must be labeled as concepts. Do not fabricate screenshots for repositories without a GUI runtime.

## Integration gates

- Validate JSON tokens and ensure required keys exist.
- Check that CSS/SVG assets contain no gradients, filters, drop shadows or silhouette artwork.
- Test keyboard focus, contrast, 200% zoom, reduced motion and 44 px touch targets where applicable.
- Verify that security state always includes text or an icon and that missing telemetry is `UNKNOWN`.
- Preserve each repository's language, build system, license, ownership and independent release lifecycle.

## Scope boundary

The supplied manifesto contains ten concrete example concepts and placeholder ranges for the remaining ideas. This contract operationalizes the supplied direction; it does not pretend that 666 individually specified requirements or a working GUI already exist. Further components must be implemented and tested in the repository's native stack before being marked complete.
