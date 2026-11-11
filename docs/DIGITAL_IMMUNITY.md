# Digital Immunity & Intellectual Property Provenance

> **Guiding principle:** Code is a claim; provenance is its evidence; a repository is a maintained record, not merely a storage location.
>
> This document operationalizes integrity, provenance, and intellectual-property practices. It does not create legal rights, replace a license, or guarantee that infringement is impossible.

## 1. Purpose and scope

Source code, documentation, assets, build outputs, and dependency metadata are materials whose origin and permitted use must remain understandable over time. The repository should preserve an auditable chain from contribution to reviewed change and published release.

Iterations 1–666,665 were supplied as intentionally redacted for bandwidth optimization. No missing iteration data is inferred or fabricated. Iteration 666,666 is retained as the guiding principle: reduce ambiguity, preserve provenance, and make protection operational.

## 2. Digital identity and provenance

For each important contribution and release, maintain the following evidence where practical:

- **Project identity:** canonical repository URL, project name, release tag, and commit identifier.
- **Contributor identity:** attributable commits; use verified author identities and signed commits or signed release tags where supported.
- **Content identity:** SHA-256 digests for release archives and important generated artifacts.
- **Change history:** preserve review context, commit history, changelog entries, and release notes.
- **Origin records:** identify third-party code, copied snippets, datasets, fonts, images, and other imported materials with their source and license.
- **Build provenance:** record source revision, build workflow, toolchain/dependency versions, and artifact digest for published releases.

A hash establishes that bytes match a recorded digest; it does **not**, by itself, establish who created those bytes, when they were created, or who owns copyright.

## 3. Integrity controls

Recommended controls, to be enabled according to the project's tooling and threat model:

1. Generate SHA-256 checksums for release artifacts and publish the checksum file alongside each release.
2. Verify checksums before consuming or mirroring release artifacts.
3. Protect the default branch with pull-request review and required CI checks where repository settings permit.
4. Prefer signed commits and signed release tags; verify signatures against trusted contributor keys.
5. Keep dependency lockfiles and generate an SBOM for distributable releases where feasible.
6. Pin critical third-party actions and dependencies to reviewed immutable versions or digests.
7. Run automated secret scanning, dependency vulnerability checks, and license-policy checks in CI.
8. Preserve immutable release records and avoid rewriting published history except under a documented incident procedure.

## 4. Licensing and rights

- Treat the repository's `LICENSE` file and explicit notices as the authoritative statement of the project's declared license.
- Do not assume that public availability means permission to relicense, remove attribution, or reuse every asset.
- Preserve copyright notices, SPDX identifiers, attribution, and required license texts when redistributing covered material.
- Record the origin, version, license, and required notices for third-party components.
- Review license compatibility before adding or distributing dependencies and assets.
- If ownership, permission, or licensing is unclear, pause redistribution of the affected material and obtain appropriate legal review.

This document is a technical policy, not legal advice. It does not amend the repository's license or determine ownership of contributions.

## 5. Copy and change traceability

When code or assets are moved between repositories:

- retain the original source URL and commit or release reference;
- preserve upstream notices and license texts;
- record local modifications and their dates in the relevant change history;
- avoid stripping attribution or disguising copied material through renaming;
- use a provenance record or SBOM component entry when the material is shipped.

Names and identifiers may be standardized for clarity, but renaming must never be used to conceal origin or evade attribution obligations.

## 6. Suggested release evidence

| Evidence | Minimum useful content |
|---|---|
| Source revision | Full commit SHA and release tag |
| Checksums | SHA-256 digest for each published artifact |
| Signature | Verified signed tag or release provenance |
| SBOM | Component name, version, supplier/origin, license |
| Notices | Project and third-party copyright/license notices |
| Build record | Workflow, toolchain, dependencies, artifact digest |

Example checksum generation:

```sh
sha256sum ./dist/* > SHA256SUMS
sha256sum --check SHA256SUMS
```

Use platform-appropriate equivalents where `sha256sum` is unavailable.

## 7. Operational ownership

Maintainers should periodically review whether the declared license matches distributed material; imported assets and dependencies have traceable origins; branch protections and CI checks remain enabled; release checksums and signatures can be independently verified; and notices and provenance records survive packaging and mirroring.

Handle security or rights incidents through the repository's documented security/contact process. Preserve relevant evidence and avoid publishing sensitive personal data or credentials in provenance records.

## 8. Acceptance criteria

This policy is operational only when maintainers can demonstrate that:

- a release can be tied to a specific source commit;
- published artifacts can be checked against recorded SHA-256 digests;
- contributors and reviewers are attributable to recorded changes;
- third-party materials have documented origins and license information;
- required notices are included in distributions;
- integrity and dependency checks run in CI or an explicitly documented manual release process.

## 9. Guiding principle

**Every bit should have a verifiable history; every copy should retain its provenance; every reuse should respect its license.**

The repository's “immune system” is a combination of cryptographic integrity checks, review controls, provenance records, licensing discipline, and repeatable release procedures—not a claim that technology can make infringement physically impossible.
