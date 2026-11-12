# SAMBU — Server-Side Swift

This repository includes a separately deployable Swift 6 backend boundary. It complements the existing native/runtime implementation; it does not replace kernel, boot, compiler, CLI, or existing application components.

## Build and run

```sh
cd swift-backend
swift package resolve
swift test
swift run sambu-server
```

Configuration is loaded from `HOST`, `PORT`, `SERVICE_NAME`, and `SERVICE_VERSION`. Defaults are non-secret operational values. Database credentials, JWT signing keys, and external API tokens must be supplied by a deployment secret provider; they are not accepted as source constants.

## HTTP endpoints

- `GET /health` — process liveness.
- `GET /ready` — process readiness only; dependency probes are not claimed until concrete providers are configured.
- `GET /v1/health` — versioned liveness.
- Responses include `X-Trace-ID`; supplied trace IDs are bounded and propagated.

## Architecture

- `SAMBUBackendCore`: immutable configuration, Sendable request context, API error DTO, trace middleware and async repository contract.
- `SAMBUBackendServer`: Vapor transport adapter and health routes.
- Repository implementations must own bounded pools, parameterize SQL, and define transaction boundaries at the service layer.
- Do not run blocking CPU, filesystem or database work on SwiftNIO event-loop threads.
- Use actors only for genuinely shared mutable state; prefer stateless services and immutable Sendable values.

## Production qualification gates

This foundation does not claim that PostgreSQL, Redis, JWT/RBAC, TLS termination, OpenTelemetry export, Prometheus scraping, migrations, rate limiting, OpenAPI generation, load testing, or Kubernetes deployment are already configured. Add and verify each integration against the repository's actual requirements before production promotion.

For NUN, this package is strictly a management/control-plane service. It must never be linked into the freestanding kernel, bootloader, interrupt handlers, or other bare-metal targets.
