# Beelzebub repository adapter — SAMBU

**Repository role:** Scientific Modeling & Automation Environment  
**Status:** integration contract / design only  
**Canonical policy:** [Beelzebub SAMBO Defense Engine](https://github.com/bboroski/Klipot/blob/main/docs/security/BEELZEBUB_SAMBO_DEFENSE_ENGINE.md)  
**Policy owner:** `bboroski/Klipot`

## Purpose

This repository participates in the Beelzebub security ecosystem through controls appropriate to its actual engineering role. This adapter does not claim that an endpoint antivirus agent or privileged kernel component is implemented here.

## Local integration requirements

1. Preserve this repository's existing build, test, release, and branch-protection workflows.
2. Run secret detection, dependency/SBOM review, static analysis, and repository-specific tests in CI where supported.
3. Verify provenance and integrity of release artifacts; reject unsigned or untrusted release inputs where the toolchain supports verification.
4. Treat pull requests, commits, workflows, dependencies, generated artifacts, and release credentials as protected assets.
5. Record security findings with evidence, severity, confidence, affected component, and remediation status.
6. Never execute untrusted samples on developer machines or production runners; use disposable, network-restricted analysis environments.
7. Do not add arbitrary kernel hooks, SSDT/IDT patching, fake process identities, destructive resource starvation, or offensive counter-exploitation.
8. Keep telemetry minimal and avoid transmitting source code, secrets, credentials, or raw memory outside approved workflows.

## Role-specific boundary

- This repository's own CI and release pipeline are the primary enforcement points.
- Runtime endpoint controls are applicable only if this repository actually builds a qualified endpoint component.
- For kernel, firmware, boot, or bare-metal artifacts, use signed build provenance, static verification, reproducible tests, and artifact admission. Do not assume desktop OS APIs exist.
- Any new privileged capability requires an ADR, threat-model update, platform qualification, independent review, and rollback test.

## Required acceptance evidence

- CI run links for all existing required checks.
- Secret/dependency/static-analysis results or a documented unsupported-capability reason.
- A negative test proving invalid policy/signature or malformed input is rejected safely.
- A rollback/recovery test for any control that changes files, configuration, or runtime state.
- Documentation of false-positive handling and operator override.

## Rollout

This adapter is a policy anchor. Implementation proceeds in independently reviewable stages under the canonical policy. No protection capability may be advertised as active until code, tests, and platform evidence demonstrate it.
