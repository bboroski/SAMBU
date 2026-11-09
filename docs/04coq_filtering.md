# 04coq — SAMBU filtering framework

**04coq** is SAMBU's deterministic, declarative filtering layer. It selects values from in-memory collections using explicit predicates, reports why a candidate matched or failed, and composes filters into a bounded pipeline.

Rules are data, not code. The framework does not call `eval`, execute rule strings, invoke object methods, access the network, mutate source collections, or apply hidden transformations.

## Public SAMBU API

- `coq_rule(path, operator, expected?)` — build and validate a reusable rule record.
- `coq_match(item, rules, mode="all")` — return a boolean for one item.
- `coq_explain(item, rules, mode="all")` — return the complete per-rule decision trace.
- `coq_filter(items, rules, mode="all")` — split a collection into accepted and rejected items.
- `coq_pipeline(items, stages)` — apply multiple filters in sequence.

A rule is `[path, operator]` for a unary operator or `[path, operator, expected]` for a value operator. Paths are explicit dot-separated record keys and zero-based array indexes. Use `"$"` to address the item itself. For example, `"account.status"` or `"2"`.

`mode` is `"all"` (logical AND) or `"any"` (logical OR). All rules are evaluated so that the explanation contains a complete trace. A missing path fails a normal comparison; use `exists` or `missing` when absence itself is the condition. A present `null` value is distinct from a missing path.

## Operators

| Family | Operators |
|---|---|
| Equality | `eq`, `ne` |
| Ordered | `gt`, `gte`, `lt`, `lte`, `between` |
| Membership | `in`, `not_in`, `contains`, `not_contains` |
| Text | `starts_with`, `ends_with`, `icontains`, `istarts_with`, `iends_with` |
| Presence | `exists`, `missing`, `is_null`, `not_null` |
| Boolean | `truthy`, `falsy` |
| Length | `length_eq`, `length_gt`, `length_gte`, `length_lt`, `length_lte` |

`between` takes an inclusive two-value array: `[minimum, maximum]`. `in` and `not_in` take an array of candidate values. Text operators are case-sensitive except those prefixed by `i`. Ordered comparisons support finite numbers, strings, and compatible physical quantities. A mismatched data type fails closed and is reported as `type_mismatch`.

## Results and trace

`coq_filter` returns a record containing:

- `items` and `rejected`, preserving input order;
- `input_count`, `matched_count`, `rejected_count`, and `mode`;
- `execution = "in_memory_pure_filter"` and `mutated_input = false`.

`coq_explain` returns `matched`, `mode`, `rules_checked`, and one result per predicate. Each result carries its path, operator, actual and expected values, path-presence flag, boolean result, and a stable reason such as `matched`, `not_matched`, `path_missing`, or `type_mismatch`.

A pipeline is an array of stages in the form `[mode, rules]`. Only survivors from one stage reach the next. Each stage reports input, output, and dropped counts.

## Safety and limits

- At most 100,000 items per collection.
- At most 256 rules per stage and 64 stages per pipeline.
- At most 10,000 membership candidates per rule.
- At most 32 path segments and 1,024 path characters.
- Only explicit record keys, dictionary keys and non-negative array indexes are traversed.
- Dunder path segments are rejected; attributes, methods, expressions and regular expressions are not evaluated.
- Incompatible types fail closed instead of being coerced.
- The engine is deterministic and in-memory. It is not a network firewall, malware scanner, content-moderation authority, database query engine, or security sandbox.

## Example

Run `sambu examples/04coq_filtering.sambu`. The regression suite is `python -m unittest tests.test_filtering -v`.
