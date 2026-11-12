# SAMBU tooling for NUN OS profiles

**Status:** read-only host-side tooling. This is not a compiler backend, kernel loader, or remote management agent.

NUN owns the operating system and low-level contracts. SAMBU consumes the versioned profile at `bboroski/NUN/spec/os-capability-profile.json`; the normative JSON Schema is at `bboroski/NUN/spec/os-capability-profile.schema.json`.

The `sambu.nun_os` module performs bounded semantic validation and computes a deterministic SHA-256 digest. It rejects duplicate JSON keys, unknown fields, repeated IDs, unsupported states, and `implemented`/`partial` claims without evidence.

## CLI

```sh
sambu os profile check path/to/os-capability-profile.json
sambu os profile check path/to/os-capability-profile.json --json
sambu os profile check path/to/os-capability-profile.json --require services.dependency-graph
```

`--require` accepts only `implemented` by default. `--allow-partial` explicitly permits a partial implementation. Planned, unsupported, and undeclared features fail the gate. The command reads metadata only and executes no profile content.

Evidence paths are provenance pointers, not proof that a test ran on the current commit. CI and target-specific hardware qualification remain separate gates.

SAMBU is Python-hosted developer tooling and must not be linked into, or required to boot, the freestanding NUN kernel. A future native SAMBU target needs a separately specified versioned C ABI and cross-target conformance tests.
