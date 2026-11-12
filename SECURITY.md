# Security Policy — SAMBU

## Supported scope

This policy covers the compiler, parser, language runtime, engine adapters, and generated artifacts. Report the exact affected path, commit SHA, and version or platform where the issue can be reproduced. If the issue crosses repository boundaries, identify every affected repository and the contract between them.

This policy does not authorize testing third-party systems, production devices, accounts, or infrastructure without explicit permission.

## Reporting a vulnerability

**Do not publish exploit details, credentials, private data, proof-of-concept payloads, or unpatched vulnerability information in public Issues, Discussions, or Pull Requests.**

1. Use GitHub's **Private vulnerability reporting** or **Security Advisories** for this repository when that feature is enabled.
2. If no private channel is available, contact the maintainer through the [bboroski GitHub profile](https://github.com/bboroski) and request a private reporting route. Keep the initial public request free of exploit details.
3. Once a private channel is established, provide the affected commit, component, environment, impact, safe reproduction steps, and any proposed mitigation.
4. Redact tokens, passwords, private keys, personal data, device identifiers, and sensitive logs before sharing evidence.

## Response and disclosure

The maintainer will assess reports in good faith. No response-time, remediation, or disclosure SLA is promised by this policy. Coordinate public disclosure with the maintainer; do not publish a working exploit while affected users remain exposed.

## Dependency and supply-chain reports

Include the package/action name, exact version or commit SHA, lockfile or workflow path, and evidence of the affected dependency chain. Do not attach secret-bearing environment files or private build logs.

## Repository ownership

Report an issue to the repository that owns the affected implementation. A central or federated repository may track coordination, but it does not replace the security responsibility of the implementation owner.
