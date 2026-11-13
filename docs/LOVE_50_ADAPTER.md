# LOVE-50 adapter — SAMBU

**Repository:** `bboroski/SAMBU`  
**Role:** Python-hosted language, scientific modelling, IDE and reproducible workflow environment  
**Status:** SPECIFIED — this mapping is guidance; it does not certify runtime conformance.  
**Canonical doctrine:** [Klipot LOVE-50](https://github.com/bboroski/Klipot/blob/feat/love-50-chinese-proverbs-20261113/docs/LOVE_50_CHINESE_DOCTRINE.md)  
**Related standard:** [Trust and portfolios](TRUST_AND_PORTFOLIOS.md)

## Why this profile exists

SAMBU combines a language toolchain, semantic analysis, scientific and spatial data, creative workflows and local desktop tooling. LOVE-50 should strengthen clarity and reproducibility without turning Chinese literary expressions into language syntax or using user emotion as data.

## Repository-specific application

### Fate / compatibility
Keep language grammar, module manifests, dialect profiles and host adapters versioned. A compatible extension must declare the syntax/API it consumes; discovery must not silently alter semantics.

### Fidelity / trust
Preserve deterministic execution where promised, explicit seeds for sampling, stable serialization, data provenance and honest distinction between hash integrity and issuer authenticity.

### Responsiveness / care
Make compiler and CLI diagnostics actionable: source location, cause, safe correction, and uncertainty. Keep ExperienceJournal opt-in, local-only, bounded and revocable.

### Harmony / integration
Treat IDE, CLI, native compiler slice and ecosystem adapters as separate surfaces with explicit contracts. Integration tests should cover full user workflows, not imply the native slice is a complete compiler.

### Wisdom / restraint
Avoid collecting creative content or inferring emotional traits. Do not add dependencies or syntax sugar solely to mirror the proverb collection.

## Local verification

- `python -m pytest`
- `python one.py check`
- `Add regression cases for parser/semantic errors, deterministic sampling, provenance and opt-in journal revocation when those paths change.`

## Non-goals and safety boundaries

- Do not change the language grammar merely to embed proverbs.
- Do not claim the native compiler slice is a complete source-to-machine-code toolchain.
- Do not treat portfolio hashes as proof of identity, issuer authenticity or ownership.

## Adoption state

This document establishes a repository-specific interpretation only. Promote any item to **IMPLEMENTED** after the relevant code or configuration exists; promote it to **VERIFIED** only after the repository-native checks and target-specific evidence pass. Keep unknown, planned, partial and failed states distinct. Do not weaken existing security, privacy, ABI, platform, licensing or release requirements to satisfy a metaphor.

---
*The Chinese expressions are engineering prompts, not claims that software has human emotions.*
