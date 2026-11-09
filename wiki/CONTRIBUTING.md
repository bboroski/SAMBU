# Contributing to the SAMBU wiki and project

## Scope

Contributions can improve:
- language syntax and reference accuracy;
- source-aware diagnostics;
- scientific and domain model validation;
- test coverage;
- examples;
- security boundaries;
- architecture descriptions;
- integrations;
- this encyclopedia.

## Documentation rules

1. Describe implemented behavior separately from planned behavior.
2. Prefer executable examples from the repository.
3. State limits, preconditions and assumptions.
4. Do not turn an illustrative model into an empirical or scientific claim.
5. Do not imply that a plan executes external side effects.
6. Keep version numbers synchronized with package metadata.
7. Link to source, tests and examples when possible.
8. Avoid duplicating existing reference docs; summarize and link to them.
9. Preserve clear language and stable terminology.
10. Update the wiki when a public interface changes.

## Local verification

Install in editable mode:

```bash
python -m pip install -e .
```

Run the full test suite:

```bash
python -m unittest discover -s tests -v
```

Run relevant examples and CLI checks for the subsystem you changed. If a change affects the interpreter, also test valid and invalid source programs and inspect diagnostics.

## Bug reports

Include a minimal reproducer, exact command, Python/SAMBU versions, expected and actual behavior, and full diagnostics. A vague symptom is harder to reproduce and may lead to an incorrect fix.

## Pull requests

A focused pull request should explain:
- what problem it solves;
- why the change belongs in SAMBU;
- which files and public interfaces change;
- how the change was tested;
- compatibility impact;
- known limitations.

Avoid mixing unrelated refactors, new features and documentation rewrites in one large change.

## Security-sensitive changes

Changes involving process execution, file access, network access, identity, authorization, cryptographic trust or production adapters require explicit threat analysis, permission boundaries, failure handling and tests. Never add secrets to source files or examples.

## Wiki maintenance checklist

Before merging a wiki change:
- verify each link;
- verify code examples against current source;
- label roadmap items as planned;
- remove claims contradicted by tests;
- check that subsystem names and version details are current.
