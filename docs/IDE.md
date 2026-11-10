# SAMBU Studio — IDE architecture and implementation status

## Product direction

SAMBU Studio is the graphical desktop workbench for the SAMBU language. It is shipped as a standard-library Tkinter application, launched with `sambu-ide`. The editor consumes the existing `SambuIDE` document-inspection and completion API; the interpreter and parser remain independent of the GUI.

The workspace is organized around a multi-document editor, bounded project explorer, document outline, syntax diagnostics, task output and project actions. This is a practical desktop IDE milestone, not a claim that every planned compiler or language-service feature is complete.

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

## Historical typed-AST milestone (0.5.1)

The core introduced immutable `SourcePosition` and `SourceSpan` values, end-exclusive token spans, stable lexical/parser diagnostic codes, and an immutable typed AST through `parse_ast()`. Every statement and expression node carries a source span. `parse()` remains backward-compatible and returns the established tuple AST; `Program.to_legacy()` is the explicit conversion path.

Token and AST offsets count Python Unicode code points; a future LSP adapter must convert them to the negotiated protocol encoding (commonly UTF-16).

## Desktop IDE: shipped capabilities

Launch the graphical application after installing the project:

~~~bash
python -m pip install -e .
sambu-ide
# equivalent module entry point
python -m sambu_ide.app
~~~

The desktop application currently provides:

- Multiple editable documents in tabs, UTF-8 open/save/save-as, unsaved-change prompts and a bounded file size.
- A project explorer that skips common generated/dependency folders, avoids following symlinks and caps the number/depth of displayed nodes.
- SAMBU syntax highlighting, line-number gutter, current-line indication, indentation, line-comment toggling, search/replace and go-to-line navigation.
- Bounded lexical completion from the current SAMBU keyword/builtin catalog through `SambuIDE.complete()`.
- Parsed outline for functions, classes, interfaces, traits and methods, plus source-located parser diagnostics.
- Current-file execution through `python -m sambu`, workspace parse/architecture checks through SAMBU Machine, Python `unittest` discovery, Python package build through `python -m build`, and read-only Git status.
- Asynchronous task execution with captured output, execution time limits and a stop action. Commands are passed as argument arrays with `shell=False`; the IDE does not provide a general-purpose shell or arbitrary command entry.
- Russian and English interface labels and optional Apple-device diagnostics.

Keyboard shortcuts:

| Shortcut | Action |
|---|---|
| Ctrl+N / Ctrl+O | New buffer / open file |
| Ctrl+Shift+O | Open project folder |
| Ctrl+S | Save |
| Ctrl+F / Ctrl+H | Find / replace |
| Ctrl+G | Go to line |
| Ctrl+/ | Toggle line comment |
| Ctrl+Space | Keyword/builtin completion |
| F5 | Run current SAMBU file |
| F6 | Check workspace |
| F7 | Run Python unit tests |
| Shift+F5 | Request task termination |

## Language-service boundary and roadmap

The GUI is implemented, while the language services remain intentionally incremental. `SambuIDE` is the current headless service core:

- `open_document(uri, source, version=1)` and `change_document(uri, source, version=...)` maintain versioned document snapshots, hashes, token counts and typed-AST parse diagnostics.
- `close_document(uri)` releases a document snapshot.
- `complete(prefix, limit=50)` returns bounded keyword and builtin prefix matches. It is lexical completion, not scope-aware semantic completion.
- `inspect_workspace(path)` delegates bounded source parsing and declared architecture checks to SAMBU Machine.
- `sample_code(path, denominator=100, seed=0)` delegates to deterministic AST sampling.

The current outline is parser-derived. It does not yet resolve project-wide imports or references. The editor does not yet provide an LSP server, full type inference, effect/ownership analysis, semantic tokens, signature-aware hover, refactoring/rename, formatter, interactive debugger, live plot panel, native compiler or native source maps. Package build depends on the optional `build` Python package being installed.

## Execution and trust boundary

Running a source file executes it as the current operating-system user. The SAMBU `sealed` profile used by inspection is not an OS sandbox and does not constrain a process launched by the Run action. Only run source code from projects you trust. The workspace explorer and static checks do not upload project files or contact external services.

The workspace checker reports only the checks its implementation performs; a green parse/architecture result is not proof of type safety, security, runtime correctness or production readiness. Git status is read-only: staging, committing, pushing, release signing and deployment remain explicit external operations.
