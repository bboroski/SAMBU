# Systems Operations — executable planning blueprint

This document maps the four-domain technical model to SAMBU's current deterministic models. The language makes assumptions explicit and testable; it does not claim to run the external products named in the concept.

## 1. Sound production architecture

Use `audio_profile` to turn a creative brief into validated, machine-readable production metadata:

```sambu
let mix = audio_profile("Systems Operations", 150, 60, 15, -0.3, true, true, true, true, true)
print(mix.bpm)
print(mix.immediate_entry)
print(mix.stereo_mastering)
```

The model records tempo, swing, snare timing, peak ceiling and production intentions: immediate entry / no intro build, cinematic sample layers, metallic snare, pitch-bent hats and stereo mastering. The sample values are project settings, not standards. The function does not render stems, edit samples, apply EQ/compression, measure loudness or replace a DAW/mastering engineer.

## 2. Neo-Magento asynchronous order architecture

The customer-facing checkout must remain inside the supported Magento / Adobe Commerce flow. The order intent is persisted transactionally with a durable outbox; a publisher delivers a small versioned message to RabbitMQ; consumers reload authoritative quote/order state through version-pinned service contracts.

```sambu
let queue = queue_profile("heavy_orders_queue", 4, 8, 3, true)
let retries = retry_schedule(4, 2, 2, 30)
let key = idempotency_key("checkout", "quote-2048")
let order = order_pipeline(queue, true, true, true, true, true, true)
print(order.invariants_satisfied)
print(order.delivery_semantics)
print(order.steps)
```

The checklist assumes at-least-once delivery. It requires durable outbox, persisted uniqueness for idempotency, inventory reservation, payment authorization, acknowledgement only after order-state commit, supervised long-running workers and dead-letter routing. Payment capture and compensation remain provider- and merchant-specific; never infer success from broker acknowledgement. A pending customer reference is not a confirmed order.

The model is intentionally not a Magento or RabbitMQ client. A real adapter must pin Commerce/PHP/RabbitMQ versions, use supported service contracts, validate MSI reservations, protect payment side effects with provider idempotency where supported, and test duplicate delivery and crash windows.

## 3. Physical community space and growth loop

Reuse existing operating functions instead of duplicating them:

- `weekly_schedule` sets the recurring weekly rhythm; multiplying by four gives only a rough monthly planning estimate.
- `attendance` measures seat utilization and remaining capacity.
- `studio_offer` evaluates a configured free-intro conversion target and a multi-session package.
- `funnel`, `channel_metrics`, `ab_test` and `unit_economics` help assess acquisition and offer economics.

Example:

```sambu
let offer = studio_offer(200, 60, 0.30, 30, 200, 8)
print(offer.intro_conversion)
print(offer.target_met)
print(offer.effective_session_price)
```

A 30% conversion target is a hypothesis supplied to the model, not a forecast or promise. Bitrix24, Zadarma, Philips Hue, social platforms, booking systems, fragrances, singing bowls and physical-room controls are not connected to SAMBU. Integrations should be optional adapters with consent, least-privilege credentials and explicit data handling; customer records should not be copied into queue messages without a clear need.

## 4. Strategic core loop and node ownership

`allocate` splits a finite resource by weights. `capture_tower` retains the original one-step resistance calculation. `capture_node` additionally models factions and ownership:

```sambu
let pressure = allocate(50, [0.5, 0.3, 0.2])
let result = capture_node("rival", "diplomat", 35, pressure[0])
print(result.captured)
print(result.owner_after)
print(result.resistance_after)
print(result.overflow)
```

Ownership changes only when resistance reaches zero. The current implementation is a single deterministic round; regeneration, simultaneous turns, dynamic information storms, defensive protocols, boss agents, pathfinding and multiplayer synchronization remain future game-simulation work. Numerical control of nodes is an abstract game mechanic, not a model of real-world coercion or harm.

## Implementation status

In SAMBU 0.5 the following are executable language models: audio-brief validation, queue profile/retry/idempotency planning, order-pipeline invariant checks, recurring schedule/capacity/funnel/package metrics, resource allocation, directed influence and one-step territory capture with ownership transfer.

Still not implemented: audio DSP/rendering, Magento/Adobe Commerce modules, live RabbitMQ workers, durable database outbox, payment/inventory integrations, CRM/VOIP/smart-home/social adapters, a full real-time strategy engine and the graphical SAMBU Studio. These require separate packages, real integration environments and their own test/security plans.
