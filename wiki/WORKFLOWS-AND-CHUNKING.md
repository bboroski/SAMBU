# Workflows, chunking and reversible patching

SAMBU provides deterministic planning helpers for bounded data work. These tools describe or preview work; they do not automatically launch workers or mutate external systems.

## Bounded chunking

The Python API exposes `chunked()` and `plan_chunks()` from `sambu.chunking`.

```python
from sambu.chunking import chunked, plan_chunks

for batch in chunked(stream_of_records, chunk_size=250, max_items=50_000):
    process(batch)  # execution and side effects belong to the host

plan = plan_chunks(
    total_items=12_000,
    chunk_size=250,
    max_in_flight=4,
)
print(plan.to_dict())
```

`chunked()` is lazy and yields immutable tuples. It reads at most one chunk at a time and stops at a configurable item ceiling. `plan_chunks()` calculates chunk count, final chunk size, concurrency bound and processing waves; it does not start workers or promise an execution time.

## Reversible text patches

The Python API exposes `PatchSet` and `TextPatch` from `sambu.patching`.

```python
from sambu.patching import PatchSet, TextPatch

changes = PatchSet("rename-api-symbol", (
    TextPatch(
        start=10,
        end=13,
        expected="foo",
        replacement="bar",
    ),
))

receipt = changes.apply(source_text)
preview = receipt.updated
restored = receipt.rollback(current=preview)
```

Patches use Python string offsets measured in Unicode code points. Stale expected text, out-of-range spans, overlapping edits and ambiguous insertions are rejected. A receipt stores original and updated snapshots with SHA-256 digests. Rollback is permitted only while the current text still matches the patched snapshot.

This is a local text transformation primitive, not a filesystem writer.

## Batch and retry plans

Other bounded models calculate:
- batch sizes and concurrency limits;
- estimated processing waves;
- capped retry delays;
- queue capacity estimates;
- idempotency-key strings;
- workflow invariant checklists.

A calculated retry schedule does not enforce retries in a transport. An idempotency-key constructor does not create a database uniqueness constraint. A capacity estimate is not measured throughput.

## Evidence-aware workflows

The workflow layer includes preview models for transfers, accreditation records, relationship evidence, signal reports and proposal scoring. It does not settle payments, issue credentials, make allegations, contact external services or execute background jobs.

## External side-effect boundary

A host application must own:
- worker creation and supervision;
- durable queues and databases;
- transaction boundaries;
- idempotency persistence;
- retry classification and jitter;
- cancellation and back-pressure;
- authorization;
- audit logging;
- observability and recovery.

SAMBU's planning objects are building blocks for a responsible integration, not substitutes for these systems.

## Further reading

- [Chunking and patching reference](../docs/CHUNKING_AND_PATCHING.md)
- [Workflow models](../docs/workflows.md)
- [Frameworks](FRAMEWORKS.md)
