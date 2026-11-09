# Chunking and reversible patching

## Bounded chunking

~~~python
from sambu.chunking import chunked, plan_chunks

for batch in chunked(stream_of_records, chunk_size=250, max_items=50_000):
    process(batch)  # the host owns execution and side effects

plan = plan_chunks(total_items=12_000, chunk_size=250, max_in_flight=4)
print(plan.to_dict())
~~~

chunked() is lazy and yields immutable tuples. It reads at most one chunk at a time and stops at a configurable item ceiling. plan_chunks() calculates chunk count, last chunk size, concurrency bound and processing waves; it does not launch workers or promise an execution time.

## Previewable patches

~~~python
from sambu.patching import PatchSet, TextPatch

changes = PatchSet("rename-api-symbol", (
    TextPatch(start=10, end=13, expected="foo", replacement="bar"),
))
receipt = changes.apply(source_text)
preview = receipt.updated
restored = receipt.rollback(current=preview)
~~~

Patches use exact Python string offsets (Unicode code points). Stale expected text, out-of-range spans, overlaps and ambiguous insertions are rejected. A receipt retains original and updated snapshots with SHA-256 digests; rollback is allowed only while the current text still matches the patched snapshot. This is a local text-edit primitive, not a filesystem writer.
