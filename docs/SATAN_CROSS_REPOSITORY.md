# Satan — Cross-Repository Autonomous Core

Satan is a governed coordination layer for the repositories in the bboroski
ecosystem. The first implementation lives in the SAMBU package
`sambu.satan`; other repositories connect through versioned manifests and
small, repository-specific adapters.

## Architecture

- **Nexus** — SQLite-backed registry, idempotent event inbox, and threat memory.
- **QEGM** — authenticated gossip envelope format. It uses ordinary HMAC-SHA256
  message authentication and assumes authenticated TLS at the transport layer.
  “Quantum entanglement” is a metaphor, not a networking primitive.
- **Dependency graph** — directed provider-to-consumer edges and Python AST
  contract extraction. AST parsing never imports or executes scanned source.
- **Autonomous change pipeline** — validates proposal metadata and test/security
  evidence before allowing a change to be marked ready for a Pull Request.
- **Repository adapters** — discover local metadata and publish allow-listed
  events. Adapters must not receive production credentials by default.

## Trust and delivery rules

1. Every event kind is allow-listed, bounded, authenticated, and time-limited.
2. Event IDs are unique; duplicate delivery is idempotent and conflicting
   reuse of an ID is rejected.
3. Each node has an independently provisioned secret of at least 32 bytes.
   Rotate secrets out-of-band; never commit them or put them in event payloads.
4. Use TLS with peer authentication for network transport. HMAC is message
   authentication, not encryption or non-repudiation.
5. Relays append a signed hop record. Enforce a finite hop budget and expiry.
6. Treat repository content, tickets, comments, model output, and findings as
   untrusted input. Never execute an event payload.
7. A generated change must have a reproducible digest, required tests, security
   evidence, and a reviewable diff.
8. Protected paths, high-risk changes, production credentials, merge, and
   deployment require explicit human approval.
9. The initial release does not host a network listener, invoke an LLM, run
   generated code, merge Pull Requests, or deploy production artifacts.

## Event envelope

The immutable origin statement contains `event_id`, `kind`, `origin`,
`issued_at`, `expires_at`, and `payload`. The origin signs this statement.
Each relay signs its forwarding envelope, including the previous envelope
digest and hop count. Receivers verify both signatures against a provisioned
node-key map.

Allowed event kinds:

- `repository.registered`
- `security.finding`
- `dependency.changed`
- `contract.changed`
- `artifact.attested`
- `change.proposed`

## Next implementation increments

1. Add authenticated transport adapters and key rotation.
2. Add repository discovery with explicit installation allow-lists.
3. Add language-specific contract adapters and cross-repository impact reports.
4. Connect static analysis, dependency scanners, and CI evidence.
5. Add isolated agent execution only after sandbox and capability boundaries
   are independently reviewed.
6. Add deployment adapters behind environment-specific approvals and rollback.

## Local checks

Run:

```sh
python -m unittest tests.test_satan_mesh -v
```

The implementation is deliberately conservative: it creates a secure
coordination foundation, not a self-authorizing production deployer.
