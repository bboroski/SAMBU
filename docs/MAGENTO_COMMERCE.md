# Magento / Adobe Commerce architecture with SAMBU

## Purpose and boundary

SAMBU 0.6.0 provides planning models and a static XML inspector. It has no database, payment, network or RabbitMQ transport; it cannot replace Magento checkout or prove that a remote side effect completed.

Magento / Adobe Commerce remains the system of record for carts, quotes, orders, inventory reservations, customers, tax and payment state. A future adapter must be separate, version-pinned and tested against the exact Commerce release and enabled modules.

## Recommended asynchronous order architecture

~~~text
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

Failed or exhausted messages -----> Dead-letter queue
~~~

### Checkout contract

Do not acknowledge a successful order merely because a message was placed on a broker. The customer response must distinguish request accepted from order confirmed. For asynchronous confirmation, persist a durable order-intent record first and return a pending reference. The order is confirmed only after authoritative Commerce state commits.

Do not replace standard checkout with a controller that serializes arbitrary cart data and publishes it directly. Preserve quote validation, totals, customer context, stock checks, payment semantics and order lifecycle through supported service contracts. Queueing can move work off the synchronous path; it does not by itself remove database contention or guarantee higher throughput.

## Delivery semantics and idempotency

Assume at-least-once delivery. Persist idempotency under a unique database constraint; make state transitions conditional; use provider-supported payment idempotency keys where available; record outcomes so duplicate deliveries return prior results. SAMBU's idempotency_key only constructs a string and does not enforce uniqueness or prevent duplicate side effects.

Inventory reservation, payment authorization/capture and order persistence require an explicit state machine and compensation strategy for the selected inventory implementation and provider.

## Message Queue Framework XML

Adobe Commerce uses distinct configuration files:

- communication.xml defines topic contracts and handlers.
- queue_consumer.xml defines the relationship between a queue and its consumer.
- queue_topology.xml declares exchanges, bindings and destinations.
- queue_publisher.xml maps topics to publisher connections and exchanges.

A topic must define exactly one of request or schema. Use schema for a service-interface contract; use request for a data type. For synchronous request topics, also specify response. Do not use xsi:type="object" on topic elements. Magento documents topic as the supported exchange type in queue_topology.xml; do not assume arbitrary RabbitMQ exchange types are supported by Magento configuration.

Example communication file:

~~~xml
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Communication/etc/communication.xsd">
    <topic name="heavy.order.place" request="string">
        <handler name="heavyOrderProcessor"
                 type="Vendor\HeavyOrderQueue\Model\Queue\Consumer"
                 method="process"/>
    </topic>
</config>
~~~

Example topology:

~~~xml
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework-message-queue:etc/topology.xsd">
    <exchange name="magento-heavy-orders" type="topic" connection="amqp">
        <binding id="HeavyOrderBinding" topic="heavy.order.place"
                 destinationType="queue" destination="heavy_orders_queue"/>
    </exchange>
</config>
~~~

Also define queue_publisher.xml and queue_consumer.xml for the intended module architecture. A consumer's configured name is the identifier passed to the consumer-start CLI command; it is not automatically the queue name. Use the schema and configuration of the target release.

## SAMBU Studio inspection

~~~bash
sambu-studio inspect /path/to/magento/module
sambu-studio inspect /path/to/magento/project --format json
~~~

The inspector inventories preferences/plugins, communication topics/handlers, consumers, exchanges/bindings and publishers. It checks XML well-formedness, selected attributes and simple cross-file links. It is not an official XSD validator and does not resolve Magento's merged runtime config. A clean report does not prove referenced classes exist, DI compilation succeeds, RabbitMQ is reachable or an order is processed.

## Failure handling and operations

- Retry only transient errors with bounded backoff and jitter.
- Do not retry permanent validation failures indefinitely.
- Route exhausted messages to a DLQ with failure category, attempt count and correlation ID.
- Replay only through an audited operator workflow that preserves idempotency.
- Monitor queue age, ready/unacked messages, consumer health, retry rate, DLQ growth, payment failures and inventory compensation failures.
- Use a supervised process manager with bounded process lifetime, restart policy, resource limits and logs.

## Version-aware Studio roadmap

1. Official XSD validation for the target module and Commerce version.
2. DI config merging and plugin/preference inspection by area and module load order.
3. PHP AST navigation and Service Contract symbol indexing.
4. GraphQL schema explorer and query validation against the target schema.
5. SQL profiling through explicitly enabled local development instrumentation.
6. Read-only RabbitMQ telemetry using least-privilege credentials.
7. Audited DLQ replay only after idempotency, permission and confirmation design.

Do not embed credentials or issue destructive commands from editor preview. SSH/SFTP, cache clearing, deployment, queue purge and message replay are not implemented by the current inspector.
