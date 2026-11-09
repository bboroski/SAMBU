# SAMBU Studio — IDE architecture

## Product direction

SAMBU Studio is the planned developer environment for the Neo-Modern Diplomat workflow. The interpreter and CLI remain the language's stable core; editor services should be separate processes or libraries so a missing IDE dependency never affects deterministic command-line execution.

## Semantic language services

### Typed AST and source ranges

The parser exposes immutable typed statement and expression nodes through `parse_ast()`. Each node carries an end-exclusive source span, while `parse()` continues to return the legacy tuple AST. This is the stable substrate for semantic analysis and editor services. AST offsets count Python Unicode code points; protocol adapters must translate them to the negotiated LSP encoding.

### Dimensional semantic highlighting

Tokenize identifiers, literals, units, constants, function names, record fields, and control-flow keywords into distinct semantic classes. Unit symbols such as `eV`, `K`, `kg`, and `m/s` should be highlighted only when the parser resolves them as known unit bindings, not by matching arbitrary text.

### Dimensional diagnostics

The analyzer should infer dimensions through the expression tree and report incompatible operations before execution:

- Addition / subtraction of incompatible dimensions.
- Comparison of quantities with incompatible dimensions.
- Invalid function arguments, such as a mass passed where a temperature is required.
- Non-positive temperature and particle mass constraints where statically provable.
- Unknown names, duplicate immutable bindings, and invalid field access.

Diagnostics should carry file range, severity, stable code, and a short explanation. Runtime checks remain authoritative for values that cannot be known statically.

### Context-aware completion

Completion items should be derived from the parser, lexical scope, built-in signatures, record schemas, and imported adapter manifests. Examples include `maxwell(temperature, particle_mass)`, `boltzmann(energy, temperature)`, and Commerce planning functions. Completion must not invent Magento service methods that are absent from the selected version's adapter metadata.

## Interactive scientific REPL

The REPL should support incremental evaluation, retained session bindings, dimensional inspection, and opt-in plotting for arrays and distribution samples. Plotting belongs in an optional UI package; the base language remains dependency-free. Each cell should display source, result, elapsed time, and diagnostics.

## Execution tracing and debugger

A debugger should expose statement boundaries, lexical scopes, function call frames, evaluated values, and runtime errors. Scientific quantities should display both magnitude and dimensions. Stepping must not change program semantics; external side effects remain unavailable in the core runtime.

## Diplomat Night theme

A dark theme with restrained contrast, clear semantic differentiation, and accessible focus / selection states. The theme must be tested against WCAG contrast targets and should avoid relying on color alone to communicate errors or dimensional mismatches.

## Delivery sequence

1. Publish a stable parser / AST interface and source-span model.
2. Implement diagnostics and semantic tokens.
3. Add completion from lexical scopes and built-in signatures.
4. Add an LSP server and editor extension.
5. Implement REPL sessions and optional plots.
6. Add deterministic execution tracing and debugger controls.
7. Package the theme and accessibility tests.

## Current implementation status (0.5.1)

The core exposes immutable `SourcePosition` and `SourceSpan` values, end-exclusive token spans, stable lexical/parser diagnostic codes, and an immutable typed AST through `parse_ast()`. Every statement and expression node carries a source span. `parse()` remains backward-compatible and returns the established tuple AST; `Program.to_legacy()` is the explicit conversion path.

The parser reports incomplete expressions at the actual EOF token. Token and AST offsets count Python Unicode code points; an LSP adapter must convert them to the negotiated protocol encoding (commonly UTF-16).

The repository still does not ship a semantic dimension analyzer, LSP server, graphical IDE, semantic token provider, context completion provider, live plot panel, debugger UI, or Diplomat Night theme. This document is a target architecture, not a feature checklist claiming those components already exist.
