# Inter-substrate runtime profile — SAMBU

**Role:** canonical contract owner and Python-hosted reference implementation.  
**Runtime:** Python >=3.10; optional native/embedded adapters remain independently qualified.

## Existing foundations

SAMBU already publishes the ecosystem module manifest and registry, architecture and execution contracts, typed concurrency primitives, workflow/policy descriptions, and a Python-hosted language interpreter. Those are distinct capabilities; the language interpreter is not a kernel, native sandbox, or firmware runtime.

## Added in this branch

- Event envelope v1 and resource descriptor v1 JSON Schemas.
- Strict host validation for message identity, producer metadata, event type, sequence, offset-aware timestamp, trace IDs, ownership, lifetime, rights, bounds and alignment.
- Canonical UTF-8 JSON encode/decode with finite-number checks and a 256 KiB envelope ceiling.
- A FIFO, thread-safe, bounded in-process event queue with explicit overflow rejection.
- Registry declarations and unit tests for these primitives.

## Remaining ecosystem work

Distributed transports, durable delivery, E2E encryption, token verification, remote authorization, durable audit storage, distributed tracing, cluster scheduling, service scaling, database replication/sharding, and hardware/BCI adapters remain separate work items. They require a real transport or target, threat model, test suite, and independent evidence.

## SEGA / Internet-Dust research boundary

Use SEGA-era multi-processor architectures as design studies for ownership, shared-memory coordination, bus arbitration and high-level APIs. Treat Internet Dust as a fictional/simulated multiparticle field model. It may become a deterministic simulation domain with bounded snapshots and provenance; it is not a real-world network carrier, brain interface, quantum communication channel, or hardware feature.

## Verification

Run:

```sh
python -m unittest discover -s tests -p test_ecosystem_runtime.py -v
python -m unittest discover -s tests -v
python one.py check
```

CI results must be read from this branch's actual workflow runs. A successful host test does not qualify a distributed deployment or physical target.
