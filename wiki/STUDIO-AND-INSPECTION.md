# SAMBU Studio and project inspection

## Product direction

SAMBU Studio is a separate tooling package around the interpreter and developer workflow. It is delivered through Python packages and CLI tools first. A language server or graphical Electron/Tauri + Monaco application is a roadmap direction, not a feature that should be assumed to exist in the current release.

## Current command-line inspection

Install the package, then run:

```bash
sambu-studio inspect /path/to/project
sambu-studio inspect /path/to/project --format json
```

The repository README highlights static inspection of selected Magento / Adobe Commerce XML configuration.

The inspector inventories selected configuration in files such as:
- `etc/di.xml`;
- `etc/communication.xml`;
- `etc/queue_consumer.xml`;
- `etc/queue_topology.xml`;
- `etc/queue_publisher.xml`.

It checks UTF-8 input, file-size limits, XML well-formedness, selected attributes and simple cross-file references. It skips common generated/dependency folders and does not follow symlinked configuration files.

## What inspection does not prove

The inspector is not:
- the official Magento XSD validator;
- a complete merged configuration resolver;
- proof that PHP classes or methods exist;
- proof that DI compilation succeeds;
- a live connection to Magento, RabbitMQ, Redis, a database or OpenSearch;
- an operational command runner;
- a queue purge or dead-letter replay tool.

References that are absent from the inspected folder may exist in another module, so some cross-file findings are warnings rather than definitive failures.

## Typed AST as a tooling foundation

The parser exposes immutable typed AST nodes with end-exclusive source spans through `parse_ast()`. The established `parse()` API continues to return the legacy tuple AST; `Program.to_legacy()` converts the typed tree back to that shape.

This source-aware representation is a foundation for editor diagnostics, symbol navigation, completion and refactoring. It does not by itself implement those services.

Offsets count Python Unicode code points. An LSP adapter must convert offsets to the negotiated protocol encoding, commonly UTF-16.

## Roadmap directions

The Studio design document describes possible future work:
- semantic analysis and dimensional diagnostics;
- semantic highlighting;
- completion based on scope and API metadata;
- Language Server Protocol services;
- AST-aware rename and refactoring previews;
- debugger and execution trace;
- live plots and richer graphical tooling;
- version-pinned Magento-aware analysis.

A design document is not a claim of implementation. Always check current source, examples and tests.

## Further reading

- [Studio architecture source document](../docs/IDE.md)
- [Language tour](LANGUAGE-TOUR.md)
- [Testing and diagnostics](TESTING-AND-DIAGNOSTICS.md)
