# SAMBU Rails — convention-driven web ecosystem architecture

**Status:** architecture proposal plus an implemented project/scaffold generator. This is not yet a running web framework.

SAMBU Rails borrows the productive parts of Rails—convention over configuration, resource routing, MVC separation, model-driven schema evolution, generators and a coherent CLI—while retaining SAMBU's explicit type, effect, capability and safety goals.

The current 0.11 runtime is still a Python-hosted language interpreter. The repository now implements two starter commands:

- \`sambu new blog_app\` creates a convention-based project tree.
- \`sambu generate scaffold Post title:string body:text\` creates model/controller/view/migration/test starter files.

These generated files deliberately label unfinished framework contracts. The source entry point runs in the current interpreter; route, controller, template, ORM and migration specifications do not. There is no active native HTTP server, database adapter, router, view renderer, application console or migration runner yet. The generator itself uses only the Python standard library and is an interim host-side tool, not self-hosted SAMBU code.

## 1. Convention map

| Concern | Convention | Generated location | Intended responsibility |
|---|---|---|---|
| Model | Singular PascalCase type; singular snake_case filename | \`app/models/post.sambu\` | Fields, validation, relationships and persistence contract |
| Table | Plural snake_case | \`posts\` | Relational storage identity |
| Controller | Plural resource name plus \`Controller\` | \`app/controllers/posts_controller.sambu\` | Request actions and response decisions |
| View | Resource/action path | \`app/views/posts/index.html\` | Escaped presentation |
| Routes | Explicit resource declaration | \`config/routes.sambu\` | HTTP method/path/action mapping |
| Migration | Monotonic prefix and descriptive name | \`db/migrate/0001_create_posts.sambu\` | Reversible schema transition |
| Tests | Resource-named suite | \`test/posts.sambu\` | Model, request, route and system behavior |

Conventions are defaults, not hidden authority. An explicit project manifest override may change paths, table names or route prefixes. Ambiguous collisions must fail with a diagnostic instead of guessing.

## 2. Intended source design

The following is **illustrative syntax**, not accepted SAMBU 0.11 grammar. It must not be copied into a production source file until parser, AST, semantic checker, interpreter, formatter and docs support it together.

### Routes

~~~sambu
application Blog {
  routes {
    root "welcome#index"
    resources posts {
      resources comments
    }
  }
}
~~~

A route declaration expands into a deterministic route table. For a resource, the initial REST set is index, show, new, create, edit, update and destroy. Nested resources have an explicit parent parameter and bounded nesting depth. Static routes outrank parameter routes; ambiguous routes are compile-time errors. Method, path, name and action uniqueness are checked when the route table is built.

### Models and relationships

~~~sambu
model Post {
  field title: String required
  field body: Option<Text>
  field published: Bool default false
  has_many comments: Comment
}
~~~

A model has one stable schema identity. Field types map through an adapter's capability matrix; a database cannot silently coerce unsupported precision or nullability. Relationships declare foreign-key ownership, deletion behavior, cardinality and loading strategy. Lazy loading must be explicit to prevent hidden N+1 queries.

### Controllers

~~~sambu
controller Posts {
  before_action load_post only [show, edit, update, destroy]

  action index {
    let posts = Post.all().order(created_at, Desc)
    render posts
  }

  action create {
    let input = params.require("post").permit("title", "body")
    match Post.create(input) {
      Ok(post) => redirect(post.path)
      Err(errors) => render("new", status: 422, errors: errors)
    }
  }
}
~~~

Each request receives an isolated request context. Filters execute in declared order and have explicit skip/abort behavior. Parameter schemas are allowlists, not mass-assignment guesses. A controller can return a typed response, redirect or render result; it cannot write directly to a global response object.

### Migrations

~~~sambu
migration CreatePosts {
  up {
    create_table posts {
      id: Int primary_key
      title: String not_null
      body: Text nullable
      created_at: Timestamp not_null
      updated_at: Timestamp not_null
    }
  }

  down {
    drop_table posts
  }
}
~~~

Migrations are append-only historical records with stable IDs and content hashes. The runner obtains an exclusive migration lock, records the applied version only after commit, and refuses checksum drift. Transactions are used where supported. Non-transactional DDL is explicit and requires recovery instructions. A migration is reversible only when its down operation is valid; destructive transformations require a backup or an explicit irreversible marker.

## 3. Runtime request lifecycle

The target request path is:

1. Parse and normalize the HTTP request; enforce header, body, path and timeout limits.
2. Resolve a route from an immutable compiled route table.
3. Build an isolated request context with explicit clock, storage, session and identity capabilities.
4. Run middleware and controller filters in a specified order.
5. Validate authentication, authorization, CSRF and parameter schemas before mutation.
6. Execute a controller action and typed model/query operations.
7. Render an escaped template or serialize a typed response.
8. Apply response headers, cookies and security policy; emit the response.
9. Close request-scoped resources and record bounded telemetry, even on failure.

A failure in one request must not corrupt another request's state. Expected validation, routing, authorization and database failures map to explicit response categories. Internal failures are logged with a correlation ID, but secrets, session tokens and request bodies are not logged by default. Error handling must not convert unknown failures into false success responses.

## 4. ActiveRecord-style persistence contract

The initial ORM should implement a small trustworthy subset before adding convenience APIs:

- Parameterized insert, select, update and delete.
- Explicit connection and transaction scopes.
- Typed field conversion with nullability and range checks.
- Unique and foreign-key constraints represented in schema metadata.
- Optimistic locking for concurrent updates.
- Explicit eager loading and bounded query counts.
- Typed validation errors distinct from adapter or connectivity failures.
- Prepared statements and adapter-specific capability reporting.

Raw SQL remains available only through an explicit unsafe/escape hatch with parameter binding. Common CRUD should not require manually assembled SQL. A query builder must produce inspectable query plans and must not execute during string formatting or logging.

The first database adapter should be selected by a separate design decision. The ORM core must depend on a narrow adapter protocol, not on one vendor's connection object. No live adapter or migration execution is claimed by this change.

## 5. Templates and output safety

Templates use explicit interpolation and automatic HTML escaping by default. Trusted raw HTML requires a distinct type or explicit unsafe call. Contextual escaping differs for HTML text, attributes, URLs, CSS and JavaScript. Layouts and partials have deterministic lookup rules. Rendering must enforce recursion, output-size and nesting budgets. Streaming is a separate response mode with explicit cancellation and resource closure.

## 6. Generator and CLI

The implemented generator supports:

~~~bash
sambu new blog_app
sambu generate scaffold Post title:string body:text
sambu generate scaffold BodyAcceptance status:string reflection:text --path ./sovereign_app
~~~

The project generator validates identifiers and field declarations, refuses to overwrite existing files, assigns deterministic migration sequence numbers and creates a runnable \`src/main.sambu\` entry point.

The following commands are **planned**, not implemented:

- \`sambu db:migrate\` — requires a real database adapter, migration lock and transaction/recovery protocol.
- \`sambu console\` — requires a persistent REPL and application boot lifecycle.
- \`sambu server\` — requires an HTTP runtime, request isolation and security middleware.
- \`sambu routes\` — requires an executable route parser and route-table diagnostics.

## 7. Security and reliability requirements

Before production use, the framework must implement request/body limits, strict header parsing, path traversal protection, HTML contextual escaping, CSRF protection, secure cookie defaults, session rotation, authorization hooks, parameter allowlists, safe file uploads, rate limits and configurable timeouts. Database access uses parameter binding. Migrations have lock/rollback/recovery behavior. Background jobs require bounded queues, idempotency keys, retry ceilings and dead-letter policies.

The framework core must not expose ambient filesystem, network, process or secret-store access. These arrive as granted capabilities. The host process is the fault-containment boundary until a stronger isolation runtime exists.

## 8. Performance policy

No claim that SAMBU is ten times faster than Rails or Node.js is made. Such a claim is meaningless without identical workloads, feature parity, hardware, database, concurrency, latency percentile, memory and error-rate measurements.

Benchmarks must publish source, runtime build, target hardware, operating system, configuration, warm-up, sample count, p50/p95/p99 latency, throughput, RSS, CPU use and correctness checks. Compare interpreter mode first; compare native compilation only after a native backend exists. Performance optimizations may not weaken request isolation, validation or security.

## 9. Roadmap and exit gates

| Stage | Deliverable | Exit gate |
|---|---|---|
| 0 — Generator | \`sambu new\`, scaffold files, naming and collision checks | CI tests generated project and every generated SAMBU file parses |
| 1 — Language modules | Modules, imports, visibility, declarations and project manifest | Independent file parsing, symbol resolution and deterministic dependency DAG |
| 2 — Routing | Route grammar, route table, parameter constraints and route diagnostics | Method/path precedence, duplicate rejection and route tests |
| 3 — HTTP runtime | Request/response types, middleware, safe server adapter and isolation | Security suite, request fuzzing, concurrency and cancellation tests |
| 4 — Models and ORM | Typed schema, query builder and one supported adapter | Transaction, injection, consistency and adapter capability tests |
| 5 — Migrations | Checksums, locks, ledger, rollback and recovery | Crash-injection tests and data-preservation verification |
| 6 — Views and controllers | Controller lifecycle, validation, templates and contextual escaping | End-to-end MVC tests and output-security corpus |
| 7 — Native serving | Typed IR, native backend and optimized HTTP runtime | Differential semantics plus reproducible target benchmarks |
| 8 — Self-hosted tooling | SAMBU-written framework/compiler tools | Reproducible bootstrap from a trusted seed without Python runtime dependency |

Stages may overlap only when their interface contracts are already stable. A generator is not proof of a framework; a route file is not proof of a router; a migration specification is not proof of a database engine.

## 10. Engineering culture

SAMBU should be confident without being defensive. External criticism is evaluated as evidence, not absorbed as identity and not dismissed as noise. The project's quality is determined by reproducible behavior, documentation, security and tests—not by marketing comparisons or pressure to imitate another framework. The community should reward clear reasoning, respectful review, maintainable changes and honest feature status.

See [the 100-rule Autonomy Constitution](AUTONOMY_CONSTITUTION.md) and [the systems-language evolution architecture](LANGUAGE_EVOLUTION.md).
