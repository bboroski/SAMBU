# Semantic Autonomy: Naming and Migration Contract

**Status:** proposal for review  
**Revision:** 1  
**Applies to:** SAMBU  
**Branch:** feat/semantic-autonomy-2026-11-11

## Purpose

This document establishes a controlled policy for choosing clear, internally coherent native-language names for concepts exposed by this project. The goal is semantic independence in user-facing language without sacrificing interoperability, discoverability, or compatibility with existing software ecosystems.

This is a naming and migration contract, not a claim that the codebase has already been translated or mechanically renamed. No production identifier is changed by this document alone.

## 1. Core principles

1. **Meaning before purity.** Prefer a precise native-language term when it is clear to the intended audience. Do not replace a well-defined technical term with an ambiguous or misleading invention merely to avoid borrowing.
2. **Endogenous naming.** New product concepts and user-facing labels should be coined from native roots or concise descriptive phrases. Record the definition, scope, part of speech, and examples of use.
3. **One concept, one canonical name.** The project glossary is the authority. Synonyms may be listed as search terms, but only one preferred label is used in each interface context.
4. **Context-aware names.** Names must reflect the role of the element: an action for an operation, a thing for a resource, and a state for a status.
5. **Interoperability is mandatory.** Do not rename standards-defined fields, wire-protocol tokens, file formats, command-line flags, environment variables, third-party symbols, or externally consumed API fields unless the relevant specification and all consumers are intentionally migrated.
6. **No false promises.** A glossary entry or migration plan is not an implemented feature. Mark planned, experimental, deprecated, and supported states distinctly.

## 2. Naming layers

| Layer | Policy | Examples |
|---|---|---|
| User interface | Prefer native-language labels; retain a familiar technical term in help text when needed | «Сбой», «Свойства», «Запуск» |
| Documentation | Introduce the preferred term with a concise definition; include the conventional term once for searchability | «сопряжение (interface)» |
| Internal code identifiers | Keep existing identifiers stable; new identifiers follow the repository's established language and style | No bulk rename |
| Public APIs and data formats | Preserve published names and schemas; add versioned aliases only through an explicit compatibility plan | Existing JSON keys remain unchanged |
| External standards and dependencies | Preserve canonical spelling and capitalization | Protocol names, compiler flags, library symbols |

## 3. Initial glossary

The following are candidate preferred labels, not unconditional replacements:

| Conventional term | Preferred native-language label | Definition / boundary |
|---|---|---|
| interface | сопряжение; поверхность взаимодействия | Boundary through which components exchange actions or data |
| bug | ошибка; сбой | Use «ошибка» for a defect and «сбой» for an observed failure |
| feature | возможность; функция | User-visible capability or callable behavior, according to context |
| deploy | ввод в действие; развёртывание | Moving a verified build into a target environment |
| commit | фиксация изменения | A version-control record; do not rename the Git command |
| repository | хранилище исходных материалов | Project history and files managed by version control |
| token | ключ; маркер | Use «ключ» only for credentials; «маркер» for a parser or protocol unit |
| cloud | удалённая среда; распределённая среда | Choose according to actual topology; do not imply a cloud provider |
| stream | поток | Ordered sequence of data or events |
| link | связь; ссылка | «Связь» for a relation, «ссылка» for a navigable reference |
| client | потребитель; запрашивающая сторона | Use only when it accurately describes the component's role |
| endpoint | конечная точка; адрес операции | Distinguish a network address from an operation |
| runtime | среда исполнения | Execution environment, not the running process itself |
| build | сборка | Produced artifact or the process that produces it |
| test | проверка; испытание | Automated assertion or broader validation, respectively |

Glossary terms are context-sensitive. For example, «ключ» must not replace «маркер» when the value is not an authentication credential.

## 4. Term proposal record

Every proposed term must be reviewed with this record:

- **Concept ID:** stable, language-neutral internal reference.
- **Current term:** exact spelling and source location.
- **Preferred label:** proposed native-language form.
- **Definition:** one-sentence meaning and explicit non-meanings.
- **Context:** UI, documentation, code, API, data, or several layers.
- **Alternatives:** rejected synonyms and reasons.
- **Compatibility impact:** none, documentation-only, source-compatible, or breaking.
- **Evidence:** affected files, tests, schemas, and consumers.
- **Decision:** proposed, accepted, rejected, or deprecated.
- **Owner and review date:** accountable maintainer and date.

Do not infer a term's meaning from spelling alone. Inspect its call sites, schema, tests, and consumers first.

## 5. Migration sequence

### Phase A — Inventory
Collect occurrences from source, documentation, UI resources, examples, schemas, generated files, and public API descriptions. Classify each occurrence by meaning and layer. Exclude vendored code and generated artifacts from direct editing.

### Phase B — Semantic review
Group occurrences by concept, not by matching text. Resolve homonyms and false positives. Produce a reviewed mapping table and identify all externally visible names.

### Phase C — Parallel naming
Introduce accepted labels in documentation and user-facing surfaces. Where useful, show the conventional term parenthetically during the transition. Keep search terms and migration notes.

### Phase D — Compatible adoption
For internal symbols, use language-aware refactoring and update every reference atomically. For public interfaces, prefer versioned aliases, adapters, or deprecation notices. Never silently change serialized field names or command syntax.

### Phase E — Removal review
Remove an old alias only after usage evidence, a published migration window, passing compatibility tests, and an explicit maintainer decision. Keep historical release notes searchable.

## 6. Safety and correctness gates

A rename or label change is eligible only when all applicable checks pass:

- Meaning is unchanged and the new label is unambiguous.
- Case, Unicode normalization, locale, and transliteration behavior are defined.
- Imports, reflection, serialization, plugin discovery, configuration, scripts, and generated references are checked.
- Public API and data compatibility are tested against supported versions.
- Documentation links, examples, CLI help, and UI accessibility labels are updated.
- A rollback path exists.
- No secret, credential, protocol keyword, third-party license text, or vendor-owned identifier is rewritten.
- Automated changes are reviewed as a diff; no repository-wide blind substitution is allowed.

A failed gate blocks the migration. Record the reason rather than forcing a replacement.

## 7. Validation plan

The first implementation stage is documentation-only. Before any executable rename is proposed, add tests appropriate to the project:

1. Glossary schema/format validation, if the glossary becomes machine-readable.
2. Search-based inventory checks with explicit allowlists for standards and external symbols.
3. Tests for every renamed internal symbol and its import/call sites.
4. Compatibility tests for old and new public names during the transition.
5. UI snapshot, localization, and accessibility checks where applicable.
6. Build, lint, and full existing test suite on supported environments.

Do not report tests as passing unless they were actually run. A repository without a relevant test harness must say so and define a manual review step.

## 8. Governance

- The glossary is reviewed like source code: changes are proposed, discussed, and approved.
- A term may be rejected if it is awkward, misleading, hard to pronounce, or conflicts with established usage.
- Native-language naming is a product choice, not a reason to conceal conventional terms from contributors or interoperability partners.
- The canonical language for code identifiers remains the repository's existing convention until a separate, tested language policy is approved.
- Each repository owns its local vocabulary; shared concepts should use the same definition across the ecosystem.
- This proposal does not alter licenses, authorship, provenance, or ownership. Naming policy is not a substitute for copyright or trademark review.

## 9. Acceptance criteria for this proposal

- [ ] Maintainers approve the glossary and naming layers.
- [ ] Repository-specific terms are inventoried and mapped to real code locations.
- [ ] Affected public interfaces and external dependencies are identified.
- [ ] A test and rollback plan exists for each executable migration.
- [ ] No compatibility-breaking rename is merged without an explicit versioned decision.

**Current implementation state:** specification only. No source-code, API, schema, command, or UI names have been changed by adding this document.
