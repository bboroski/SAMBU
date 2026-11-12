# Release Policy

This policy governs releases from this repository. A release is a verified product artifact, not merely a Git tag.

## Versioning

Use SemVer tags in the exact form `vMAJOR.MINOR.PATCH`. Pre-release candidates use `vMAJOR.MINOR.PATCH-rc.N` (for example, `v1.2.0-rc.1`). Do not reuse or move a published tag.

- **MAJOR**: incompatible public API, ABI, file-format, boot-image, manifest, or behavior change.
- **MINOR**: backward-compatible capability or feature addition.
- **PATCH**: backward-compatible defect or security correction.
- **Pre-1.0**: while MAJOR is 0, compatibility is not assumed; document every breaking change explicitly.

Conventional Commit categories guide the proposed increment: `feat` normally maps to MINOR, `fix` and `perf` to PATCH, and a breaking-change marker/footer to MAJOR. The final version remains a maintainer decision.

## Mandatory release gates

A release may not proceed until all applicable checks pass:

1. Pull request merged through the protected default branch with required reviews and successful required status checks.
2. Full project-specific build, unit, integration, cross-platform, and applicable hardware/emulation tests pass.
3. Security checks complete with no unresolved release-blocking findings: secret scan, CodeQL where supported, dependency review, and vulnerability triage.
4. An SPDX or CycloneDX SBOM is generated from the exact release tree/artifact.
5. `CHANGELOG.md` contains the release date, version, user-visible changes, breaking changes, and security fixes.
6. The repository's licensing status is explicit and compatible with distribution. Do not infer or select a license automatically.
7. The exact candidate commit is reviewed; no uncommitted or untracked release input is included.

## Release candidate and freeze

Create `vX.Y.Z-rc.1` from the reviewed release commit. Freeze feature work for the candidate; only release-blocking fixes may enter. Each fix restarts the candidate sequence (`rc.2`, `rc.3`, ...). Validate the candidate in staging or the closest reproducible test environment. Promote only the exact tested commit.

## Signing and provenance

Create an annotated signed tag with a maintainer-controlled signing key:

```bash
git tag -s vX.Y.Z -m "Release vX.Y.Z"
git verify-tag vX.Y.Z
```

Push the tag only after local signature verification. Never store a private signing key in the repository or ordinary Actions secrets. If signed tags cannot be verified, the release is blocked.

## Release artifacts

Build only the targets supported by this repository's maintained toolchain. Attach binaries/packages, SPDX/CycloneDX SBOM, release notes, and SHA-256 checksums. Record the source commit and toolchain versions. Container images, when applicable, must use immutable version and commit-SHA tags; `latest` is a convenience pointer, not provenance.

## Deployment, rollback, and closeout

Deploy the exact RC/promoted artifact to staging, perform smoke and integration checks, then promote to production only where this repository has a defined production deployment target. Retain the previous stable artifact and document a one-step rollback to its immutable version/tag. Verify service/boot health after rollback.

After release, merge release-only fixes back to the default branch, close the matching milestone, and carry unresolved issues into the next milestone. Reconcile source commit, tag, SBOM, checksums, release page, and deployed artifact.

## No-go conditions

Do not publish a release when required CI is pending/failed, the security scan is incomplete, the SBOM or checksum is missing, license status is unknown, the signed tag is unverifiable, or a rollback target is unavailable.
