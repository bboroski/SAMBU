# Repository IP and Naming Compliance

## Purpose and limits

This policy defines repeatable engineering checks for copyright and license metadata, configured trademark references, and likely credential leaks. It is not legal advice or a guarantee against claims. A clean scan does not prove ownership, license compatibility, or trademark clearance.

## Keep four questions separate

1. **Copyright and provenance:** retain author and third-party notices. Do not erase attribution or rewrite Git history as routine cleanup.
2. **License grant and obligations:** the owner must choose and approve the license after confirming distribution rights. Public visibility alone does not grant reuse rights. Add \`NOTICE\` only when applicable obligations require it; do not invent ownership or contributor records.
3. **Trademarks and naming:** a detected name is a review signal, not proof of infringement. Compatibility statements, factual references, nominative use, and brand use need contextual review. The scanner never renames packages, URLs, APIs, identifiers, or documents automatically.
4. **Secrets and confidential information:** revoke or rotate exposed credentials. Deleting a value in a later commit does not remove it from Git history. History rewriting is a separately authorized incident-response action.

## Repository policy configuration

Edit \`compliance/repository-policy.json\` only after an owner or authorized maintainer has made the relevant decision:

- Set \`license.spdx_id\` only to the approved SPDX identifier; do not infer a license from repository visibility or a neighboring project.
- Populate \`trademark_watchlist\` with names requiring review in this project's context. An empty list means no project-specific watchlist has been approved; it does not mean trademark clearance.
- Add \`trademark_allow_paths\` only for reviewed references, keeping exceptions narrow and documented.
- Use \`exclude_paths\` sparingly because excluded paths are not scanned.
- Enable SPDX header enforcement only after the license and source-file scope have been approved; preserve third-party notices.

## Automated checks

\`tools/repository_compliance.py\` scans Git-tracked UTF-8 text files up to the configured size limit. It detects a limited set of credential patterns, tracked \`.env\` files, configured name references, optional SPDX-header omissions, and whether a root license file exists. It does not inspect the complete Git history, binary artifacts, every dependency license, package registries, or legal rights. Use dedicated dependency-license and historical-secret scanners where required.

The CI workflow is advisory by default: findings appear as GitHub warnings and do not fail a build for a possible trademark reference or an unconfirmed license choice. \`--strict\` is available after the owner has reviewed the patterns. A human must investigate results before changing code or metadata.

## Safe naming and identifier policy

Prefer neutral functional abstractions for newly designed integration boundaries, while retaining truthful compatibility information where necessary. Keep provider-specific behavior in adapters. Do not bulk-replace brand strings or hash public identifiers: this can break APIs, persisted data, debugging, attribution, and compatibility, and does not itself create trademark clearance or protect copyright. Use secret managers and access controls for confidential values; use keyed pseudonymous identifiers only where a documented data-protection requirement and key-management plan exist.

## Publication gate

- The owner has approved the license and confirmed rights to distribute project contents.
- Applicable third-party licenses, notices, and attribution are retained.
- Contributor terms, if needed, are selected deliberately and disclosed before contribution; this template does not assume a CLA.
- Credential findings are investigated and exposed credentials revoked or rotated.
- Trademark findings receive contextual review; compatibility and affiliation are not misrepresented.
- Package, organization, domain, and product names are reviewed by an authorized owner.
- CI results, exceptions, and unresolved legal questions are recorded for human review.
