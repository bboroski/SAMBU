# AI-Assisted Modeling and Domain Packs

**Scope:** SAMBU language, scientific modeling, structured terminology and developer tooling.  
**Status:** engineering policy; no runtime AI dependency is introduced.

## Operating rule

Gemini and other language models may propose examples, terminology mappings, test cases, documentation edits and architecture alternatives. Their output is an untrusted draft, not executable authority, scientific evidence, a compiler result or an accepted API change.

Every accepted change must be reproducible without a model service. Keep prompts, private data and credentials out of source control. Record only the model/provider, review date, relevant source references and the commit that accepted the result when provenance is useful.

## Domain-pack contract

Domain packs remain passive, versioned data. A consumer must validate UTF-8, schema/header, stable IDs, unique keys, allowed categories and non-empty values before loading them. Unknown entries must remain representable; a failed lookup must not silently become a guessed translation.

The existing [500-term biology pack](../data/biology/academic_terms_500.tsv) is a bilingual study glossary, not a peer-reviewed ontology. The ReaperCripple Mass Effect vocabulary is a separate fictional-lore corpus. Do not merge fictional names or speculative Reaper descriptions into real biology, physics constants, SI units or scientific claims.

For new packs, preserve:
- a stable identifier and explicit version;
- source/provenance and license/usage notes;
- language and category metadata;
- a clear distinction between established scientific terms, editorial descriptions and fictional concepts;
- validation fixtures for duplicates, malformed rows, unknown categories and Unicode.

## Modeling and compiler boundaries

AI-generated SAMBU programs and native IR must pass the ordinary lexer/parser, type and dimensional checks, deterministic test suite and compiler validation. Never use model prose as a parser bypass or silently translate it into privileged host calls. A generated example is not proof that the language feature or native backend exists.

A unit-aware example must state units explicitly. A model-generated numerical result must be independently recomputed or tested against a known reference before it is described as validated.

## Review checklist

1. Identify the exact files, API contracts and target versions affected.
2. Separate facts supplied by source material from assumptions and proposals.
3. Build a minimal regression fixture before accepting a behavior change.
4. Run the project checks and inspect the diff for scope creep, hidden dependencies and unsupported claims.
5. Keep the Python interpreter, native compiler slice, IDE and external integrations as separately bounded components.

## Acceptance criteria

A change is accepted only when its behavior, provenance, tests and limitations are documented. Model availability must never be required for build, test, installation or normal execution.
