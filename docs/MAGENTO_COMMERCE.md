# Magento / Adobe Commerce architecture with SAMBU

## Purpose and boundary

This document defines a reference architecture that SAMBU can describe and validate. It is not executable Magento integration code. SAMBU 0.5.0 has no network, database, payment, or RabbitMQ transport; it cannot replace Magento's checkout service or guarantee that a remote side effect has completed.

Magento / Adobe Commerce should remain the system of record for carts, quotes, orders, inventory reservations, customers, tax, and payment state. SAMBU models orchestration policies and invariants around those systems. A future adapter must be a separate, version-pinned package with integration tests against the exact Commerce release and enabled modules.

## Recommended architecture

```text
Storefront
   |
Magento Checkout / Quote validation
   |
Durable order-intent transaction (outbox)
   |
Outbox publisher -----> RabbitMQ exchange
                           |
                    heavy_orders_queue
                           |
                    Consumer worker pool
                           |
              Idempotency / state transition
                           |
          Inventory reservation + payment workflow
                           |
                Magento Order Management
                           |
                Notification outbox
                           |
                 Email / SMS workers

Failed or exhausted messages -----> Dead-letter queue
```

### Important checkout rule

Do not acknowledge a successful order merely because a message was placed on a broker. The user-facing response must distinguish **request accepted** from **order confirmed**. If the business requires a confirmed order response, the synchronous boundary must wait until the authoritative order transaction has committed. If the business accepts asynchronous confirmation, persist a durable order-intent record first and return a truthful pending reference.

Avoid replacing Magento's standard checkout with a controller that serializes arbitrary cart data and publishes it directly. Use supported service contracts and extension points, preserve quote validation, totals, customer context, stock checks, payment semantics, and the platform's order lifecycle.

## Message contract

Prefer a small, versioned message envelope over a serialized in-memory object or an unbounded cart dump:

| Field | Purpose |
|---|---|
| `message_id` | Unique message identifier |
| `schema_version` | Contract version for safe evolution |
| `idempotency_key` | Stable business-operation key |
| `quote_id` | Reference to the authoritative quote |
| `store_id` | Store / website context |
| `correlation_id` | Trace across checkout, broker, worker, and payment |
| `occurred_at` | UTC event timestamp |
| `trace_context` | Optional distributed-tracing context |

Do not put card data, secrets, access tokens, or unnecessary personal data in queue payloads. The worker should reload authoritative state through supported service contracts and revalidate assumptions before committing side effects.

## Delivery semantics and idempotency

Assume at-least-once delivery. A worker can crash after committing a database transaction but before acknowledging the message; the broker may deliver it again. Therefore:

1. Persist an idempotency record under a unique database constraint before performing non-repeatable work.
2. Associate the key with the operation type and stable quote / order reference.
3. Make state transitions conditional and reject invalid repeats.
4. Use provider-supported idempotency keys for payment operations where available.
5. Record outcomes so a retry can return the prior result instead of creating a duplicate order or charge.

SAMBU's `idempotency_key(scope, identifier)` only constructs a deterministic namespaced string. Uniqueness, persistence, race handling, retention, and replay policy belong to the adapter and database.

## Inventory and payment ordering

Inventory reservation and payment authorization are not ordinary interchangeable steps. Define an explicit state machine and compensation policy for each payment provider and inventory implementation. A typical high-level sequence is:

1. Validate the quote and calculate authoritative totals.
2. Reserve inventory using the supported inventory service.
3. Authorize payment using a provider idempotency key.
4. Place / persist the order using supported Commerce services.
5. Capture payment according to the merchant's payment policy.
6. Commit the workflow outcome and publish notifications through a durable outbox.
7. Release reservations or void authorizations when a later step fails, following provider-specific rules.

Do not assume every payment method supports separate authorization and capture. Do not perform irreversible payment capture before the order and inventory invariants are safely established.

## RabbitMQ topology and worker operations

Use a dedicated exchange and routing key for order-intent messages, with queue durability and message persistence configured consistently. Separate critical order processing from email, catalog indexing, and marketing workloads. Configure prefetch to bound in-flight work; size consumer concurrency against database connections, PHP-FPM / worker memory, payment-provider limits, and inventory contention.

The exact Magento XML declarations and CLI consumer name must be taken from the target Commerce version's official documentation and module conventions. In Magento Message Queue Framework, topic declarations, publisher configuration, topology bindings, consumer declarations, and queue connections have distinct roles. Do not assume a queue name is interchangeable with a consumer name. Validate the generated topology in the target environment.

SAMBU planning primitives:

```sambu
let queue = queue_profile("heavy_orders", 4, 8, 3, true)
let delays = retry_schedule(4, 2, 2, 30)
print(queue.max_in_flight)
print(queue.dead_letter_queue)
print(delays)
```

Here, four workers with prefetch eight allow at most 32 messages in flight by this simple model. Four total processing attempts mean three retries after the initial attempt. The schedule is capped exponential backoff in seconds. Actual broker policies, consumer declarations, and retry transport must be configured independently.

The `order_pipeline` function packages the key checklist into one inspectable result:

```sambu
let queue = queue_profile("heavy_orders_queue", 4, 8, 3, true)
let flow = order_pipeline(queue, true, true, true, true, true, true)
print(flow.invariants_satisfied)
print(flow.blockers)
print(flow.steps)
```

The six flags assert that the adapter has a durable outbox, persisted idempotency, inventory reservation, payment authorization, acknowledgement only after order-state commit, and supervised workers. The queue profile must also enable dead-letter routing. A passing checklist is not evidence of deployed configuration or transaction success. The customer response remains a pending reference until the authoritative order state commits; broker acceptance alone is not order confirmation.

## Failure handling

- Retry transient network, provider, and lock-contention failures with bounded exponential backoff and jitter.
- Do not retry permanent validation failures indefinitely.
- Route exhausted messages to a dead-letter queue with the original message, failure category, attempt count, and correlation ID.
- Provide a controlled replay procedure that preserves idempotency and requires an operator-visible audit trail.
- Alert on queue age, ready / unacked counts, consumer health, retry rate, DLQ growth, order-intent age, payment failures, and reservation compensation failures.

A dead-letter queue is not a substitute for error classification or an operational replay process.

## Magento module integration plan

A production adapter should be implemented as a conventional Magento module with:

- `registration.php`, `etc/module.xml`, and Composer package metadata.
- Service-contract interfaces for publishing and handling order-intent messages.
- Version-correct `communication.xml`, `queue_publisher.xml`, `queue_topology.xml`, and `queue_consumer.xml` declarations as required by the target Commerce release.
- Dependency injection through `etc/di.xml`; no direct ObjectManager calls.
- Plugins / observers only where supported extension points are appropriate; prefer service contracts.
- Database schema for idempotency and outbox / inbox records, with transactional uniqueness constraints.
- Integration tests for duplicate delivery, worker crash windows, payment timeouts, inventory contention, and replay.
- Supervisor or the platform's supported process manager for long-running consumers, with bounded process lifetime and restart policy.

## Deployment and compatibility

Pin supported Adobe Commerce / Magento Open Source versions, PHP versions, RabbitMQ versions, and enabled modules. Treat Adobe Commerce Cloud deployment constraints separately from self-managed infrastructure. Verify queue transport settings, secrets management, TLS, least-privilege broker accounts, database capacity, and rollback behavior in each environment.

## Non-goals in SAMBU 0.5

- No Magento runtime, module generator, checkout replacement, or production connector.
- No direct RabbitMQ publish / consume implementation.
- No payment processing, inventory reservation, order persistence, or customer notification.
- No claim that asynchronous acknowledgement equals a confirmed order.
