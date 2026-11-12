# Repository IP Governance

This directory implements a lightweight, portable baseline for provenance and rights metadata.

## Components

- `manifest.json`: repository-scoped object identifier, rights declaration, and optional artifact digests.
- `verify.py`: standard-library validator for manifest structure, safe relative paths, and SHA-256 digests.
- `../.github/workflows/ip-governance.yml`: CI validation on pushes and pull requests.

## Operating rules

1. Keep the repository locator stable. The current UOI profile is `urn:uoi:github:<owner>/<repository>`; it identifies this repository, not every file and not a legal title claim.
2. Use SPDX license expressions where verified. Keep `NOASSERTION` until the applicable license has been checked. Never infer an author or rights holder from commit metadata alone.
3. Add an artifact entry only after independently reviewing the file and computing its SHA-256 digest. Paths must be repository-relative.
4. Preserve Git history and use verified commit/tag signatures where available. A digest proves byte-level integrity, not authorship, ownership, originality, or the legal validity of a timestamp.
5. Treat licenses as authoritative policy documents. This manifest is machine-readable metadata, not an executable replacement for MIT, GPL, Creative Commons, contracts, or applicable law.
6. Do not write per-viewer access events or personal identifiers to a public ledger by default. Use consent, data minimization, retention limits, and access controls for any telemetry or personalized watermarking.
7. Never rewrite source names or text to conceal trademark references. Use explicit aliases only in presentation layers, preserve nominative/fair-use references, and label unofficial resources clearly.
8. Do not calculate ownership shares from line counts. Contribution analytics can inform review but cannot determine legal authorship or entitlement.
9. Blockchain, DAG anchoring, NFTs, payment automation, and post-quantum signatures are optional integrations, not prerequisites. Add them only with a threat model, key-management plan, privacy review, and legal review.

## Add a protected artifact

After reviewing the file, compute its digest:

```sh
python -c "import hashlib,pathlib; p=pathlib.Path('path/to/file'); print(hashlib.sha256(p.read_bytes()).hexdigest())"
```

Add `{"path":"path/to/file","sha256":"<64 lowercase hex characters>"}` to `artifacts`, then run:

```sh
python ip-governance/verify.py
```

The check is deterministic and uses only Python's standard library.
