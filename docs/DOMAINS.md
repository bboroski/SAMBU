# SAMBU domain models — 0.2

SAMBU now combines its original physics core with a small library for transparent systems models. The additions are deterministic calculators and scenario tools. They are not autonomous agents, CRM integrations, forecasting services, or validated game-balance engines.

## Neo-Modern Diplomat as a systems concept

The phrase **Neo-Modern Diplomat** is treated in SAMBU as a design archetype: an adaptive intermediary that maps stakeholders, communicates across institutional and cultural contexts, identifies bargaining intervals, and evaluates the consequences of proposals. The language does not encode a political ideology or presume that a mathematical score can replace judgment, consent, law, or institutional legitimacy.

The three-word construction can be read conceptually as:

- **Neo** — a new or renewed method; from Greek *néos* (new, young).
- **Modern** — responsive to the present; from Late Latin *modernus*, associated with *modo* (just now, recently).
- **Diplomat** — a representative or intermediary; historically connected to Greek *diplōma* (a folded document), the source of the later diplomatic vocabulary.

A number of labels in the supplied synonym lists (for example, *Quantum Envoy*, *Matrix Diplomat*, and *Singularity Broker*) are coined metaphors or stylistic variants, not strict dictionary synonyms or established professional titles. Some etymological glosses in informal lists are speculative; SAMBU documentation does not treat them as verified derivations.

## Model clusters and computational counterparts

| Conceptual cluster | SAMBU model | What it computes |
|---|---|---|
| Cybernetic and network agents | `network`, `network_metrics`, `influence` | Directed ties, degree counts, density, and strongest-path propagation |
| Geoeconomic and multilateral strategy | `negotiate`, `allocate` | Overlap between two bargaining ranges and proportional resource splits |
| Semiotic and cognitive mediation | Explicit stakeholder labels plus network paths | A transparent topology for discussing who connects whom; no semantic interpretation is inferred |
| Institutional and operational coordination | `weekly_schedule`, `attendance`, `funnel`, `ab_test` | Repeating events, capacity use, stage losses, and a simple experiment comparison |
| Game-like territorial systems | `capture_tower`, `allocate`, `network` | One-step resistance depletion and resource distribution |

## Network model

**Syntax:** `network(nodes, edges)`

Nodes are unique strings. Each directed edge is `[source, target]` or `[source, target, weight]`, with a weight in `(0, 1]`. Self-links are not useful for the current degree model and are rejected. Duplicate directed edges and references to unknown nodes are errors.

`network_metrics(graph)` reports node and edge counts, directed graph density, in-degree, out-degree, and normalized degree centrality. `influence(graph, seeds, steps=3, decay=0.8)` performs a bounded strongest-path diffusion. A seed is either a node name (strength 1) or `[node_name, strength]`; strengths and decay must lie in `[0, 1]`. At each round a node keeps the maximum signal received along any path. It does not sum signals or model persuasion, trust, strategic deception, or causal behavior.

## Negotiation model

`negotiate(a_min, a_max, b_min, b_max)` computes the intersection of two acceptable intervals. Endpoints must be comparable and dimensionally compatible when expressed as physical quantities. The record returns `possible`, `lower`, `upper`, `midpoint`, and `overlap_width`. A non-empty overlap is only a mathematical bargaining zone; it does not guarantee an agreement.

## Marketing and community operations

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
- Network influence scores are illustrative and are not evidence of actual political, social, or commercial influence.
- No CRM, VOIP, payment-terminal, ticketing, calendar, or social-platform API is connected.


## Commerce queue planning (0.3)

SAMBU 0.3 adds deterministic planning primitives for asynchronous commerce workflows. They describe configuration and calculate bounded retry / concurrency values; they do not connect to Magento, RabbitMQ, a database, or a payment provider.

- `queue_profile(name, workers, prefetch, retry_limit, dead_letter_enabled)` validates a queue identifier and worker settings. It returns `max_in_flight = workers * prefetch`, `max_attempts = retry_limit + 1`, and an optional `name + ".dlq"` destination. This is a capacity estimate, not measured throughput.
- `retry_schedule(max_attempts, initial_delay, multiplier, max_delay)` returns capped exponential retry delays in seconds. The first attempt is not included; for four attempts, the array contains three retry delays. Jitter is intentionally left to the transport adapter.
- `idempotency_key(scope, identifier)` returns a stable namespaced string. It does not persist a uniqueness constraint or prevent duplicate side effects by itself.

For the recommended Magento / Adobe Commerce boundaries, message envelope, outbox pattern, inventory and payment ordering, retry classification, dead-letter operations, and deployment considerations, see [Magento / Adobe Commerce architecture](MAGENTO_COMMERCE.md).
