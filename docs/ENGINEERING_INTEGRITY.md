# Engineering Integrity Engine

A small, dependency-free, read-only audit and reference-model package for the NUN Mesh engineering ecosystem.

## What it does
- Finds source-level candidates for fixed arrays, dynamic buffers, pointer arithmetic and matrix-shaped storage.
- Reports file, line, category and a review reminder. A match is not proof that storage is unused, hidden, leaked or safe to remove.
- Provides a bounded corpuscular-event queue with duplicate identity and conflicting-ID detection, stale-event, hop-limit and backpressure checks, plus dependency-cycle candidate detection.
- Compares memory utilization, queue pressure, latency and contention against declared resource capacities and thresholds.
- Separates heartbeat/liveness from thermal telemetry; adds seeded bounded leaf-flight scheduling and checked matrix views.
- Caps source-file reads at 2 MiB and matrix views, zeroization regions and multiplication outputs at 1,000,000 elements to prevent unbounded work or allocation.
- Provides explicit overwrite helpers only for caller-owned bytearrays or mutable matrix buffers.

## Run
```sh
python tools/engineering_integrity.py --self-test
python tools/engineering_integrity.py --root . --format text
```

## Safety contract
The auditor never edits or deletes source. No automatic memory free, garbage-collector manipulation, pointer invalidation, remote execution, device access or kernel writes are performed. Overwrite helpers do not deallocate storage and cannot guarantee erasure of copies, snapshots, swap pages or compiler-created temporaries. Use them only when the caller owns the complete buffer and controls its lifecycle.

## Model boundaries
“Anti-corpuscular”, “corpuscular-wave”, “technical mechanics”, “cardio-thermodynamics” and “leaf-flight mechanics” are names for software checks and scheduling models, not claims of new physical laws or hardware telemetry. Unknown measurements remain unknown; event queues and work budgets are bounded; the scheduler is deterministic for a fixed seed.
