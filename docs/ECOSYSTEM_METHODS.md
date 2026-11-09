# SAMBU ecosystem-inspired systems primitives

**Status:** implemented deterministic planners in the Python-hosted 0.11 interpreter. These operations produce inspectable values; they do not start workers, move hardware data, mutate cloud infrastructure, infer biological ancestry or control garbage collection.

The five names are inspired by ethology, flight, thermoregulation, trait classification and wetland ecology. The metaphors guide API design but are not claims that biological systems map literally onto CPU behavior.

## 1. ImprintClosure

Canonical call: \`imprint_closure(function, context)\`

The returned callable binds the first context supplied at construction. It takes a detached recursive snapshot, freezes arrays and records, and passes that same context as the first parameter on each invocation. The callback's remaining parameters are supplied by the caller.

~~~sambu
fn greet(context, event) {
  return context.prefix + event
}
let bound = imprint_closure(greet, some_context)
let answer = bound(" arrived")
~~~

Captured values are limited to immutable scalars, finite numbers, quantities, arrays and records, with cycle, nesting and node-count limits. Arbitrary host objects, mutable SAMBU instances and pointer capture are rejected. There are no hidden stimulus triggers: the callback executes only when called explicitly. Alias: \`ImprintClosure\`.

## 2. V_VectorStream

Canonical call: \`v_vector_stream(item_count, workers, leader_share=0.6, phase=0)\`

Returns a deterministic partition of the integer index range \`[0, item_count)\`. Worker zero is the leader and receives the configured leading share; remaining indices are divided as evenly as possible among followers. The phase rotates which follower receives remainder items. Every index appears exactly once, and ranges are contiguous and non-overlapping.

The result is a plan with worker IDs, roles, start/stop offsets, counts and a normalized phase. It does not create OS threads, measure cache trails or schedule CPU cores. Actual execution belongs to a future runtime scheduler. Alias: \`V_VectorStream\`.

## 3. CountercurrentSync

Canonical call: \`countercurrent_sync(hot, cold, hot_capacity, promote_budget, demote_budget)\`

Plans bounded transfer between application-defined hot and cold tiers. The hot array is ordered most-recent to least-recent; the cold array is ordered highest-promotion-priority to lowest. Promotion takes from the front of cold data; demotion evicts from the end of hot data. Budgets independently cap each direction.

The result includes post-plan arrays, promoted/demoted elements, capacity status and pending evictions. If the demotion budget is insufficient to meet capacity, the plan reports remaining pressure rather than violating its budget. This is not L1/L2 cache control, disk I/O or a thermal model. Alias: \`CountercurrentSync\`.

## 4. BiometricTaxonomySort

Canonical call: \`biometric_taxonomy_sort(entities, features)\`

Each entity is \`[name, integer_mask]\`; each feature name corresponds to one bit, up to 53 features (the largest exact integer mask supported by the current numeric-literal representation). The function builds a deterministic binary trait-classification tree, choosing the most balanced available split and breaking ties by feature input order. Names, masks, features and traversal order are stable.

This is a trait partition, not phylogenetic inference, DNA analysis or a dynamic type/inheritance system. The output explicitly sets \`phylogeny_inferred=false\`. Alias: \`BiometricTaxonomySort\`.

## 5. WetlandEcosystemLoop

Canonical call: \`wetland_ecosystem_loop(load, capacity_per_worker, current_workers, min_workers, max_workers, target_utilization=0.75)\`

Calculates one bounded worker-count recommendation from current load and per-worker capacity. The output reports target workers, delta, current/projected utilization, capacity ceiling and pressure class. Worker bounds and a target utilization in \`(0, 1]\` are validated.

Despite the name, this is a single pure planning step, not a running background loop. It does not start/stop workers, scale Kubernetes, tune the Python garbage collector or guarantee leak-free execution. A host controller must apply recommendations, enforce cooldowns and observe actual health/latency. Alias: \`WetlandEcosystemLoop\`.

## Safety and implementation boundaries

All five primitives are deterministic for the same inputs and return SAMBU records. Workload arrays and captured contexts are bounded. No network, filesystem, scheduler, cache, kernel or cloud side effects are performed. Results are recommendations and data transformations, not proofs of end-to-end behavior.

Run the example:

~~~bash
sambu examples/ecosystem_primitives.sambu
python -m unittest discover -s tests -v
~~~
