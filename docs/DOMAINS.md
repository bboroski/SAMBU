# SAMBU domain models — 0.5

SAMBU combines its original physics core with transparent systems, commerce, production-brief, community and territory models. The additions are deterministic calculators and scenario tools. They are not autonomous agents, CRM integrations, forecasting services, or validated game-balance engines.

## Entity graph and bounded coordination model

The model represents a set of entities, weighted links, bounded signal propagation and the overlap between two numeric operating ranges. It does not encode political positions, infer intent or replace authorization, domain review or operator decisions.

The model exposes four measurable operations:
- directed graph construction and topology metrics;
- bounded strongest-path propagation from declared source nodes;
- interval intersection with explicit bounds and midpoint;
- proportional allocation under a declared non-negative weight vector.

## Model clusters and computational counterparts

| Technical domain | SAMBU model | Computed result |
|---|---|---|
| Entity and dependency graphs | `network`, `network_metrics`, `influence` | Directed ties, degree counts, density, and strongest-path propagation |
| Range negotiation and resource allocation | `negotiate`, `allocate` | Overlap between two bargaining ranges and proportional resource splits |
| Graph connectivity and signal propagation | Explicit entity labels plus network paths | A transparent topology for discussing who connects whom; no semantic interpretation is inferred |
| Scheduling and conversion metrics | `weekly_schedule`, `attendance`, `funnel`, `ab_test` | Repeating events, capacity use, stage losses, and a simple experiment comparison |
| Stateful resource allocation | `capture_tower`, `capture_node`, `allocate`, `network` | Resistance depletion, ownership transfer and resource distribution |
| Audio signal specification | `audio_profile` | Validated tempo, groove, timing, entry and mix-intent metadata; no audio rendering |
| Grammar pipeline specification | `craft_source`, `craft_cut`, `craft_token`, `craft_rule`, `craft_assemble`, `craft_master` | Provenance-led grammar blueprint assembly and deterministic audit; no dynamic parser generation |

## Network model

**Syntax:** `network(nodes, edges)`

Nodes are unique strings. Each directed edge is `[source, target]` or `[source, target, weight]`, with a weight in `(0, 1]`. Self-links are not useful for the current degree model and are rejected. Duplicate directed edges and references to unknown nodes are errors.

`network_metrics(graph)` reports node and edge counts, directed graph density, in-degree, out-degree, and normalized degree centrality. `influence(graph, seeds, steps=3, decay=0.8)` performs a bounded strongest-path diffusion. A seed is either a node name (strength 1) or `[node_name, strength]`; strengths and decay must lie in `[0, 1]`. At each round a node keeps the maximum signal received along any path. It does not sum signals or model persuasion, trust, strategic deception, or causal behavior.

## Negotiation model

`negotiate(a_min, a_max, b_min, b_max)` computes the intersection of two acceptable intervals. Endpoints must be comparable and dimensionally compatible when expressed as physical quantities. The record returns `possible`, `lower`, `upper`, `midpoint`, and `overlap_width`. A non-empty overlap is only a mathematical bargaining zone; it does not guarantee an agreement.

## Conversion and scheduling metrics

`funnel([stage_1, stage_2, ...])` accepts non-increasing integer stage counts and reports adjacent conversion rates, drop-offs, overall conversion, and total losses. Stage labels are intentionally external in 0.2; array positions preserve the exact stage order chosen by the model author.

`ab_test(control_visitors, control_conversions, variant_visitors, variant_conversions)` computes conversion rates, absolute and relative lift, a pooled two-proportion z statistic, and a two-sided normal-approximation p-value. This is a screening calculation: it does not correct for multiple comparisons, sequential peeking, clustering, seasonality, or small-sample effects. Do not treat the `significant_at_05` flag as a substitute for experimental design or domain expertise.

`weekly_schedule([[weekday, "HH:MM", title, capacity?], ...])` validates a weekly recurring schedule and sorts it by weekday and time. Days use full English names and times use 24-hour format. `attendance(capacity, bookings)` returns remaining seats and a fill rate. `channel_metrics(spend, impressions, leads, customers)` calculates lead rate, close rate, cost per lead, and cost per customer; it validates `customers <= leads <= impressions`. `package_pricing(single_price, package_price, sessions)` compares a prepaid package with the same number of single sessions. `unit_economics(revenue, variable_cost, acquisition_cost)` estimates contribution per customer before and after acquisition cost. Monetary inputs are plain numbers in one consistent currency unit; SAMBU does not perform FX conversion or tax calculations. These functions do not create calendar events, accept payments, or contact customers.

## Resource and territory mechanics

`allocate(resource, weights)` distributes a non-negative amount in proportion to non-negative weights. If the resource is a physical quantity, dimensional units are preserved in the outputs.

`capture_tower(defense, incoming_pressure)` resolves one abstract attack: incoming pressure is subtracted from resistance. It returns whether the target is captured, remaining defense, and overflow. It is a one-step mechanic, not yet a full real-time game simulation with factions, regeneration, pathfinding, enemy turns, or special towers.

## Language control flow

0.2 adds lexical scopes, user functions, `return`, `if` / `else`, and bounded `for ... in` loops. A `let` binding remains immutable within its scope. Blocks create child scopes; a function can read its enclosing scope but cannot reassign outer names. To accumulate or transform collections, use functions such as `sum`, `mean`, `map`-like explicit loops, or return values from user-defined functions. There is no `while`, `break`, `continue`, mutation, import, or file/network access in this release.

## Safety and numeric boundaries

- `range` may create at most 100,000 values.
- A `for` loop may process at most 100,000 items.
- `sample_maxwell` remains capped at 1,000,000 samples.
- A/B inference is approximate and assumes independent Bernoulli observations.
- Network influence scores are illustrative and are not evidence of actual measured system influence.
- No CRM, VOIP, payment-terminal, ticketing, calendar, smart-lighting, social-platform or audio-rendering API is connected.


## Commerce queue planning (0.3)

SAMBU 0.3 adds deterministic planning primitives for asynchronous commerce workflows. They describe configuration and calculate bounded retry / concurrency values; they do not connect to Magento, RabbitMQ, a database, or a payment provider.

- `queue_profile(name, workers, prefetch, retry_limit, dead_letter_enabled)` validates a queue identifier and worker settings. It returns `max_in_flight = workers * prefetch`, `max_attempts = retry_limit + 1`, and an optional `name + ".dlq"` destination. This is a capacity estimate, not measured throughput.
- `retry_schedule(max_attempts, initial_delay, multiplier, max_delay)` returns capped exponential retry delays in seconds. The first attempt is not included; for four attempts, the array contains three retry delays. Jitter is intentionally left to the transport adapter.
- `idempotency_key(scope, identifier)` returns a stable namespaced string. It does not persist a uniqueness constraint or prevent duplicate side effects by itself.

For the recommended Magento / Adobe Commerce boundaries, message envelope, outbox pattern, inventory and payment ordering, retry classification, dead-letter operations, and deployment considerations, see [Magento / Adobe Commerce architecture](MAGENTO_COMMERCE.md).


## Neo-Modern blueprint models (0.5)

SAMBU 0.5 adds four deterministic models that make the strategic blueprint executable as a planning specification. They are domain calculators, not production integrations.

### Sound-production brief

`audio_profile(name, bpm, swing_percent, snare_lag_ms, ceiling_dbfs, immediate_entry, cinematic_samples, metallic_snare, pitch_bent_hats, stereo_mastering)` validates a named production brief. Tempo is constrained to 40–240 BPM, swing to 0–100%, snare lag to 0–100 ms, and the ceiling to -24–0 dBFS. The final five inputs must be booleans. The result records arrangement and mix intentions such as immediate entry, cinematic sample layers, metallic snare, pitch-bent hats and stereo mastering. It does not open a DAW, manipulate audio, enforce loudness standards, or create a master. Values such as 150 BPM, 60% swing, +15 ms and -0.3 dBFS in the example are illustrative project settings, not universal recommendations.

### Checkout orchestration checklist

`order_pipeline(queue, durable_outbox, persisted_idempotency, reserve_inventory, authorize_payment, ack_after_commit, supervised_workers)` accepts a `queue_profile` record and six boolean invariant flags. It returns a proposed sequence, at-least-once delivery semantics, the acknowledgement boundary, concurrency estimate, and a list of blockers. Missing durable outbox, persisted idempotency, inventory reservation, payment authorization, post-commit acknowledgement, supervised workers or queue DLQ marks the plan as not satisfying its checklist. A passing result means only that the declared assumptions satisfy this model; it does not prove the external system implements them or that an order is confirmed. The adapter remains responsible for database constraints, retries/jitter, MSI service contracts, payment-provider semantics, state transitions, compensation, telemetry and version compatibility.

### Service-offer conversion model

`studio_offer(intro_visitors, intro_conversions, target_conversion, single_price, package_price, package_sessions)` reports introductory-class conversion and whether it meets the configured target, then reuses `package_pricing` for effective session price, savings and discount rate. Target is a fraction in [0, 1]; conversions cannot exceed visitors. A zero-visitor sample is reported as unknown and never marked as meeting the target. The target (for example, 0.30) is a business assumption to test, not a forecast or guarantee. Combine with `weekly_schedule`, `attendance`, `channel_metrics`, `funnel` and `unit_economics` for operating analysis. The four-week monthly session count in the example is a rough planning estimate, not a true calendar-month expansion.

### Ownership-aware territory round

`capture_node(current_owner, attacking_faction, resistance, incoming_pressure)` extends `capture_tower` with factions and ownership output. Pressure reduces resistance; ownership changes only when resistance reaches zero. Excess pressure is returned as overflow for a possible next target. It is a single deterministic round: it does not model regeneration, simultaneous attacks, pathfinding, enemy turns, dynamic events, bosses or multiplayer concurrency.

See [Neo-Modern Diplomat Blueprint](NEO_MODERN_BLUEPRINT.md) for the full four-pillar mapping and [Magento / Adobe Commerce architecture](MAGENTO_COMMERCE.md) for enterprise integration boundaries.
