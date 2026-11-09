# Design philosophy and roadmap

## Current design identity

SAMBU's repository-level design principles are:

- make assumptions visible;
- make components composable;
- make changes inspectable;
- bound resource use by default;
- distinguish integrity from identity;
- evolve APIs with compatibility in mind.

The project's research-oriented character is expressed through reproducible experiments, inspectable runtime behavior and clear limits—not through intentionally mysterious syntax or unpredictable compiler decisions.

## Proposed evolution principles

The project owner has also developed a broader set of aspirational design laws for SAMBU. They include:
- exploratory compilation and alternative-path analysis;
- richer type inference and contracts;
- isolated execution worlds;
- advanced tracing and debugger history;
- more comprehensive object and concurrency models;
- local syntax extensions and macro systems;
- architecture decision memory;
- feature incubation;
- property-based and differential testing;
- semantic-preserving optimization;
- automated audit and controlled self-improvement.

These ideas are a design backlog, not a statement that the features are currently implemented.

## 100-law development philosophy

The proposed 100 laws can be grouped into six directions:

1. **Research** — keep hypotheses, experiments and unexpected discoveries.
2. **Strategy** — evaluate long-term consequences and alternatives.
3. **Learning** — teach through executable examples and practical challenges.
4. **Community** — preserve knowledge, authorship and project identity.
5. **Verification** — test semantics, boundaries, security and performance.
6. **Evolution** — automate discovery and proposal while retaining review for risky changes.

Aspirational concepts such as an autonomous evolution engine should be implemented as controlled pipelines: scan, hypothesize, prototype, test, compare, report and request review. They should not rewrite semantic guarantees or merge unreviewed changes automatically.

## Current status versus future work

| Area | Current status in repository | Important boundary |
|---|---|---|
| Interpreted language core | Implemented, experimental | Not a native compiler |
| Typed AST and source spans | Implemented | Not a complete semantic analyzer or LSP |
| OOP slice | Implemented in alpha form | Not a native object ABI or static ownership system |
| Scientific calculations | Implemented | Not a general PDE solver or empirical authority |
| Judo / Aikido / Jiu-Jitsu | Python host APIs | No automatic deployment, provider access or renderer |
| Voxel core | Implemented with bounded CPU references and starter bridges | Not a production GPU engine for all platforms |
| Studio inspector | Implemented read-only project inspection | Not official XSD validation or operational automation |
| Web adapters | Optional integrations | Host owns identity, persistence and security |
| Full graphical IDE / LSP | Roadmap | Not shipped as a complete IDE |
| Fully autonomous self-modifying compiler | Proposal only | Requires strict review and safety boundaries |

## Release discipline

The repository currently labels the package as 0.11.0-alpha and classifies it as Development Status: Alpha. Older documents may mention earlier release targets such as 0.5, 0.6 or 0.7.

When documents disagree:
1. inspect current package metadata;
2. inspect current source;
3. run the relevant examples and tests;
4. update the wiki to match the verified implementation;
5. record the change and any remaining limitation.

Do not infer implementation from roadmap language or a design sketch.

## Recommended order of evolution

1. Keep the language reference synchronized with the parser and runtime.
2. Strengthen regression, property-based and differential tests.
3. Consolidate stable contracts across modules.
4. Improve diagnostics and source-aware tooling.
5. Expand performance benchmarks with reproducible inputs.
6. Improve host integration security and version pinning.
7. Add IDE/LSP capabilities in small independently testable slices.
8. Prototype automated improvement workflows that create reviewable proposals rather than self-merging changes.

## Architectural rule

A new capability belongs in the stable project only when it has a defined use case, bounded behavior, tests, documented limits, compatibility considerations and a clear owner.
