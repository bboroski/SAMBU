# Natural Autonomous Engineering — SAMBU

Status: engineering contract and staged adoption plan. This document defines requirements; it does not claim that unimplemented capabilities already exist.

## Intent
Apply the 20 requested directions as practical, testable engineering properties—not as new programming languages or magic runtime behavior. Prefer native, understandable components; keep the system simple, observable, reversible, and safe.

## The 20 directions, translated into engineering requirements
1. Automatic natural code: automate repetitive, deterministic maintenance only.
2. Independent built-in usability: provide usable defaults and self-explanatory errors.
3. Automated native consistency: follow each repository's language, formatter, and conventions.
4. Autonomous natural programming: isolate components and minimize unnecessary dependencies.
5. Self-acting organic network functions: explicit network boundaries, timeouts, retry budgets, and cancellation.
6. Operator-free initial confidence: fail closed on uncertain or invalid inputs; never imply certainty without evidence.
7. Unattended first-run simplicity: reproducible setup, safe defaults, and clear prerequisites.
8. Programmable source confidence: contracts, type checks, tests, and reproducible validation.
9. Mechanized authentic modularity: preserve a coherent core; split modules only at real boundaries.
10. Robotic original systemization: deterministic, auditable maintenance workflows.
11. Algorithmic native graphics: render real data with units, labels, provenance, and bounded resource use.
12. Cyclic local graphical environment: local-first UI refresh with explicit lifecycle and cancellation.
13. Continuous internal content: keep docs, examples, schemas, and configuration synchronized with shipped behavior.
14. Self-regulating file typing: validate file formats, size limits, paths, and content before processing.
15. Self-managed cryocapsule modulation: treat this metaphor as isolated experimental modules with feature flags, resource limits, and rollback—not as an undefined runtime feature.
16. Self-tuning organic averaging: use documented normalization/adaptation with explicit bounds and deterministic tests.
17. Auto-start standard layering: staged initialization, dependency ordering, readiness checks, and clean shutdown.
18. Adaptive graphic design: accessible, consistent UI tokens and responsive layouts.
19. Intelligent shell animation: respect reduced-motion settings, frame/resource budgets, and lifecycle cleanup.
20. Self-executing shell creation: generate UI shells only from validated schemas/templates; never execute untrusted generated code.

## Repository-specific application
Scientific language and modeling: parser/evaluator boundaries, dimensional and semantic validation, deterministic numerical work, typed IR, bounded visualization inputs. Do not claim hardware DSP, hard real-time behavior, or native ownership guarantees without a matching target and evidence.

## Required implementation sequence
- Inventory existing code, public APIs, workflows, and open PRs before changing behavior.
- Map each applicable direction to an existing module or a narrowly scoped new module. Mark irrelevant items N/A with a reason.
- Implement in small, reviewable changes; preserve public behavior unless a versioned migration is approved.
- Add tests for normal, boundary, invalid-input, cancellation, and failure paths where applicable.
- Update documentation and examples in the same change as behavior.
- Keep platform/hardware qualification distinct from host-only tests.
- Use feature flags for experimental behavior; default off until validated.
- Never delete data, rewrite history, force-push, weaken branch protection, or bypass required checks.

## Definition of Done
A change is complete only when the relevant formatter, lint, type checker, tests, and build pass; the PR records exact commands and results; limitations and untested targets are explicit; no secrets or unrelated files are included; and reviewers can trace each behavior to code and tests.

## Adoption status
This contract is the planning and review baseline. Individual capabilities remain **planned** until implemented and verified in this repository. A documentation change alone does not constitute runtime implementation.
