# SAMBU Studio — IDE architecture and implementation status

## Product direction

SAMBU Studio is a separate tooling package around the SAMBU language and Neo-Modern Developer workflow. The interpreter stays small and dependency-free. Studio services are delivered as Python packages and CLI tools first, then can be exposed through LSP or a graphical Electron/Tauri + Monaco shell.

“No intro build” means project inspection should return useful information without launching external services or heavyweight workspace bootstrapping. “Sharp transitions”, “layered slices” and “stereo mastering” translate into fast context navigation, code folding, structural views and consistent workspace organization—not literal audio effects.

### Typed AST and source ranges

The parser exposes immutable typed statement and expression nodes through `parse_ast()`. Each node carries an end-exclusive source span, while `parse()` continues to return the legacy tuple AST. This is the stable substrate for semantic analysis and editor services. AST offsets count Python Unicode code points; protocol adapters must translate them to the negotiated LSP encoding.

### Dimensional semantic highlighting

Run:

~~~bash
python -m pip install -e .
sambu-studio inspect /path/to/magento/module
sambu-studio inspect /path/to/magento/project --format json
~~~

The read-only inspector scans:

- etc/di.xml: preferences, observed types, plugin names/types, sortOrder and disabled state.
- etc/communication.xml: topics, request/schema contracts and handlers.
- etc/queue_consumer.xml: consumer names, queues, connection names and selected runtime settings.
- etc/queue_topology.xml: exchange declarations and enabled bindings.
- etc/queue_publisher.xml: publisher topics, enabled connections and exchanges.

It checks UTF-8, file-size limits, DTD/entity declarations, XML well-formedness, selected attributes and simple cross-file references. It emits stable diagnostic codes and JSON with schema_version 1. It skips common generated/dependency directories such as vendor, generated, var, pub and node_modules and does not follow symlinked configuration files.

Limitations:
- Not official Magento XSD validation.
- Does not resolve merged DI configuration across modules, areas, scopes or module load order.
- Does not confirm that referenced PHP classes/methods exist or that DI compilation succeeds.
- Does not connect to Magento, database, Redis, OpenSearch, Varnish or RabbitMQ.
- Does not run CLI commands, SSH/SFTP, purge queues, replay DLQ messages or mutate files.
- Cross-file references absent from the inspected folder are warnings because dependencies can declare them elsewhere.

## AST refactoring engine

Target design:
1. Introduce immutable typed AST nodes with source spans while preserving the legacy tuple AST during migration.
2. Build a workspace symbol index for SAMBU and supported Magento PHP/XML constructs.
3. Model references from PHP declarations, di.xml preferences/plugins, events.xml observers, layout XML, GraphQL schema/resolvers and selected service-contract metadata.
4. Offer rename as a previewable change set with exact file ranges, collision checks, stale-file detection and explicit apply/revert.
5. Never rewrite arbitrary matching text or mutate production projects from editor preview.

The initial Magento inspector is a foundation for this index, not a semantic refactoring engine yet.

## Static analysis and dependency graph

The future analyzer should report type compatibility, nullable repository results, service-contract mismatches, invalid field access and dimensional inconsistencies before execution. Magento-aware checks must be pinned to the target Commerce version and installed module set.

Dependency graph stages:
- Local DI preferences and plugin declarations.
- Module sequence and area-specific config.
- Cross-module references and cycles.
- Plugin sort order and disabled state.
- Generated-code cache fingerprints, invalidated when composer.lock, module config, PHP version or target Commerce version changes.

Do not treat generated/code as source of truth; it is a derived build artifact.

## Magento operational tools

Planned modules include GraphQL schema explorer, layout XML visualizer, service-contract completion, PHPUnit/MFTF test runner, local SQL profiling, read-only RabbitMQ queue telemetry and cache/indexer status.

Queue actions are read-only initially. DLQ replay, purge, cache mutation, deployment, SSH/SFTP and arbitrary terminal commands require explicit authorization, audit logs, target environment identity, idempotency-aware safeguards and an operator confirmation step. No operational mutation tool is implemented in 0.6.0.

## Language services

- Typed AST and type inference: gradual annotations first; preserve runtime validation at dynamic boundaries.
- Dimensional semantic analysis: infer SI dimensions and report incompatible operations before execution.
- Semantic tokens: classify resolved units, constants, functions, fields, keywords and diagnostics.
- Context completion: derive suggestions from lexical scope, builtin signatures, record schemas and versioned adapter metadata.
- LSP: document lifecycle, diagnostics, hover, completion, symbols and versioned text edits.
- REPL/debugger: incremental sessions, execution trace and optional plots, isolated from the core runtime.

## Diplomat Night theme

## Current implementation status (0.5.1)

The core exposes immutable `SourcePosition` and `SourceSpan` values, end-exclusive token spans, stable lexical/parser diagnostic codes, and an immutable typed AST through `parse_ast()`. Every statement and expression node carries a source span. `parse()` remains backward-compatible and returns the established tuple AST; `Program.to_legacy()` is the explicit conversion path.

The parser reports incomplete expressions at the actual EOF token. Token and AST offsets count Python Unicode code points; an LSP adapter must convert them to the negotiated protocol encoding (commonly UTF-16).

The repository still does not ship a semantic dimension analyzer, LSP server, graphical IDE, semantic token provider, context completion provider, live plot panel, debugger UI, or Diplomat Night theme. This document is a target architecture, not a feature checklist claiming those components already exist.
