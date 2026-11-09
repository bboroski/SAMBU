# Integrations and security boundaries

SAMBU separates the interpreter core from host-controlled integrations. This keeps optional dependencies optional and prevents a model or preview from silently acquiring external authority.

## Optional web adapters

The repository provides optional adapters for:
- Flask;
- Django;
- FastAPI.

Install only the adapter required by the host project:

```bash
python -m pip install -e ".[flask]"
python -m pip install -e ".[django]"
python -m pip install -e ".[fastapi]"
```

The adapters expose Jiu-Jitsu view snapshots and actions through HTTP routes. They do not replace the host framework's authentication, session storage, database or deployment configuration.

## Identity and authorization

The host application supplies a trusted principal resolver and per-principal application state. Clients must not be allowed to nominate arbitrary user identities in request JSON.

The host is responsible for:
- authenticating the user;
- validating session and token state;
- storing role assignments;
- enforcing permission checks at protected data boundaries;
- applying CSRF defenses when cookie authentication is used;
- rate limiting where appropriate;
- using HTTPS in deployed environments.

Jiu-Jitsu checks permissions in its UI model, but UI authorization is not a substitute for server-side authorization on the underlying data API.

## AI provider adapters

Aikido is provider-neutral. A host injects a model adapter and handles transport, TLS, provider credentials, timeouts, cancellation and error normalization.

The core does not ship vendor credentials or automatically connect to AI providers.

## Magento and message queues

SAMBU offers planning models and static XML inspection. It does not connect to Magento, RabbitMQ, payment providers or inventory services.

A future adapter must be version-pinned, use supported service contracts, enforce idempotency and define transaction, retry and compensation behavior. See [Magento architecture guide](../docs/MAGENTO_COMMERCE.md).

## Filesystem and process authority

The SAMBU source interpreter's language-level sandbox does not expose arbitrary Python evaluation, general imports, filesystem access or network access. Host-side Python tools have their own permissions and must be treated separately.

Planning utilities do not create workers, deploy infrastructure or execute arbitrary terminal commands. Reversible patch APIs are local text transformations, not automatic filesystem writers.

## Voxel engine bridges

The bridge files are source examples for host engine projects. The host engine owns SDK installation, GPU allocation, renderer integration, resource lifetimes and platform validation.

## Security review checklist

Before production use, verify:
1. What code runs inside SAMBU versus in the Python host?
2. Which external permissions does the host provide?
3. Where is the authenticated principal established?
4. Where are authorization checks enforced on data access?
5. Are inputs bounded and validated?
6. Are artifacts and dependencies trusted?
7. Are external side effects idempotent and auditable?
8. Are error reports free of secrets?
9. Are platform-specific adapters pinned to tested versions?
10. Can a failed operation be safely retried or rolled back?

## Further reading

- [Judo, Aikido and Jiu-Jitsu](FRAMEWORKS.md)
- [Studio and inspection](STUDIO-AND-INSPECTION.md)
- [Trust and evidence](TRUST-AND-EVIDENCE.md)
