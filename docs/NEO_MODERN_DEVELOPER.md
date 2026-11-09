# Neo-Modern Developer — language and IDE strategy

## Engineering objective

SAMBU should become a typed, safe, async-capable modeling and integration language that improves Magento engineering ergonomics. It must not claim to outperform PHP until reproducible benchmarks demonstrate that for a defined workload. PHP remains the host runtime and ecosystem for Magento; compatibility is a first-class design constraint.

## Language evolution

### Typed core

The current runtime is an interpreted Python implementation with SI-aware quantities and runtime checks. It is not a compiled or memory-safe native language.

Proposed sequence:
1. Introduce a typed AST and type annotations while preserving the existing tuple AST API during migration.
2. Add type inference for literals, bindings, functions, arrays, records and builtin signatures.
3. Add effect annotations for IO, async, filesystem, broker, database and payment adapters.
4. Make dimensional quantities part of the type checker, so invalid physical arithmetic and known business units can be diagnosed before execution.
5. Add bounded collection sizes and explicit resource budgets at untrusted or external boundaries.
6. Benchmark interpreter, code generation and native-backend candidates on the same realistic workloads before selecting an optimization path.

Memory safety should come from immutable values, explicit ownership/lifetime rules for native resources and strict adapter boundaries. A Python interpreter cannot promise Rust-like compile-time memory safety merely by adding a new syntax layer.

### Async model

Future async functions should have explicit effect contracts and structured cancellation. Actors or worker pools may be useful for independent tasks, but order creation, inventory reservation and payment must use durable state transitions, idempotency and compensation.

The language must not silently turn synchronous Magento checkout into fire-and-forget behavior. Async completion should return a pending operation reference; confirmed order state must come from Magento's authoritative transaction.

### PHP 8.3+ interoperability

Treat PHP as the host ecosystem, not an obstacle to erase.

Preferred incremental path:
1. Generate PHP classes/adapters from a typed SAMBU subset.
2. Preserve Magento service-contract interfaces and dependency-injection conventions.
3. Add versioned adapter manifests for PHP, Magento/Adobe Commerce and enabled modules.
4. Use a sidecar process or explicit RPC boundary when a long-lived SAMBU runtime must call PHP services.
5. Consider native extension/FFI only for a well-defined C ABI with a measured need.

PHP FFI is an interface to native C libraries; it is not a direct general-purpose bridge to arbitrary PHP userland objects. Do not expose PHP object internals through unsafe memory assumptions.

## IDE Studio: semantic engineering

The core IDE service roadmap:
- PHP AST and SAMBU AST indices.
- Cross-file symbols and references for classes, methods, service contracts, DI preferences/plugins, events.xml, layout XML, GraphQL schemas and resolvers.
- Rename/refactor as a previewable file-range transaction, not blind string replacement.
- Type/nullability checks for repository results and service-contract calls.
- EAV attribute metadata checks only when the project's attribute schema is available and versioned.
- DI dependency graph with cycles, preference conflicts, area scope and module sequence.
- Generated-code cache fingerprint based on composer.lock, PHP version, Commerce version and relevant module configuration; generated/code remains a derived artifact, not source of truth.
- Optional GraphQL, SQL and test tooling against an explicitly selected local development environment.

## Magento operations and security

Queue status, cache/indexer status and SQL profiling should begin read-only. Credentials must be least-privilege, scoped to one explicit environment and kept outside project files. Queue purge, DLQ replay, cache invalidation, deployment, SSH and arbitrary terminal execution require permission checks, audit trails, operator confirmation, idempotency and rollback design.

## Performance claims

Compare SAMBU against PHP only with published benchmark scripts, identical input/output and environment, warm/cold cache definitions, memory measurements and repeated runs. Optimize the bottleneck actually measured. A transpiled PHP backend may improve expressiveness but cannot inherently execute faster than carefully written PHP without evidence.

## Catalogue of 100 specialist roles

Core/backend: DI Architect; Module Engineer; Plugin Specialist; ORM Optimizer; CLI Commander; Layout Compiler; Observer Patternist; Service Contract Builder; Registry Purifier; PHP Core Developer; Event Dispatcher; Plugin Interceptor; Data Patch Crafter; Plugin Constructor; Preference Overrider; Repository Manager; Factory Injector; Extension Attributes Engineer; Plugin Chain Master; Backend Integrator.

Frontend/PWA: PWA Studio Architect; GraphQL Integrator; Headless Developer; React Storefront Developer; KnockoutJS Refactorer; RequireJS Resolver; LESS/CSS Stylist; UI Component Builder; Hyvä Theme Coder; Tailwind Optimizer; GraphQL Resolver; REST API Mapper; Frontend Bundler Engineer; Luma Theme Maintainer; Template Renderer; AJAX Integrator; Checkout UI Builder; Web Worker Developer; DOM Performance Engineer; UI Component Configurator.

Infrastructure: Cloud Deployer; Varnish Purger; Redis Cache Engineer; Elasticsearch/OpenSearch Optimizer; Docker Orchestrator; CI/CD Pipeline Builder; RabbitMQ Handler; Full Page Cache Engineer; Database Indexer; Cron Operations Engineer; Zero-Downtime Deployer; Log Rotator; SSL/TLS Warden; Composer Dependency Resolver; Nginx Engineer; PHP-FPM Pool Tuner; Cache Warm-Up Engineer; Load Balancer Engineer; Serverless Integrator; Infrastructure Architect.

Business/integrations: ERP Connector; Payment Gateway Integrator; Shipping API Mapper; CRM Sync Engineer; Multi-Store Manager; B2B Module Builder; Tax Calculation Engineer; Currency Conversion Engineer; MSI Inventory Handler; Checkout Flow Optimizer; Promotion Rule Builder; Catalog Price Rule Engineer; Customer Segment Analyst; Order Management Specialist; Webhook Listener; Marketplace Bridge Engineer; Import/Export Architect; Attribute Set Designer; Customer Data Platform Engineer; Omnichannel Architect.

QA/security: PHPUnit Tester; MFTF Automator; Code Quality Auditor; Security Vulnerability Scanner; Integration Tester; Performance Profiler; Static Code Analyzer; Quality Patches Applicator; Load Testing Engineer; Mutation Tester; CI Test Runner; Database Migration Validator; Dependency Checker; Error Log Monitor; API Contract Tester; Memory Leak Analyst; Refactoring Specialist; Legacy Strangler Architect; PCI-DSS Compliance Auditor; Neo-Magento Architect.

## Studio delivery principles

Small vertical slices; read-only first; separate packages; version-pinned Magento metadata; measurable performance; reversible refactoring; no fake UI; explicit status for every implemented or planned capability.
