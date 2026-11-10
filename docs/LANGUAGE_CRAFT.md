# SAMBU Language Craft

**Status:** implemented design tooling, experimental.  
**Scope:** source provenance, lexical extraction, token design, grammar assembly and deterministic audit.  
**Non-goal:** this module does not rewrite SAMBU's lexer/parser, execute a user-defined grammar or certify third-party licensing.

## 1. The production analogy, translated into language engineering

Music production is a useful model for language design because it separates discovery, transformation, arrangement and quality control. The analogy becomes practical when every stage produces an inspectable artifact.

| Production stage | Language-design equivalent | SAMBU artifact |
|---|---|---|
| Archive digging | Discover concepts, conventions and source material | `craft_source` |
| Sample selection and chopping | Select small semantic fragments without losing origin | `craft_cut` |
| Pitch / time transformation | Give a fragment a new lexical spelling, terminal identity and semantic role | `craft_token` |
| Arrangement | Combine terminals into explicit grammar productions | `craft_rule` |
| Full arrangement | Assemble sources, terminals, productions and a start symbol | `craft_assemble` |
| Mix / mastering audit | Detect collisions, missing references, unreachable rules and unused material | `craft_master` |

The key principle is **transform meaning, preserve provenance**. A source phrase is not copied into a parser blindly. It is selected, assigned a role, given a spelling and connected to a grammar rule. The source record remains available so a later maintainer can understand why a token exists.

## 2. A complete design pass

### 2.1 Register source material

```sambu
let archive = craft_source(
  "core-vocabulary",
  "declarations and expressions",
  "original design notes",
  "Author-created examples; references are conceptual, not copied implementations.",
  ["binding", "identifier", "assignment", "numeric literal"]
)
```

A source records its name, domain, provenance note, reuse note and a bounded fragment list. SAMBU stores the declarations supplied by the author; it does not browse archives, verify ownership or make a legal determination about reuse rights.

### 2.2 Select fragments

```sambu
let cuts = craft_cut(archive, ["binding", "identifier", "assignment"])
```

Selection order is retained. Each cut records the source name, source index and cut index. Repeated or unknown fragments are rejected. This resembles micro-slicing: small parts can be rearranged later, but their origin is not discarded.

### 2.3 Design terminals

```sambu
let binding = craft_token(cuts, "binding", "LET", "kava", "immutable binding", "keyword")
let name = craft_token(cuts, "identifier", "IDENT", "name", "user-defined name", "identifier")
let assignment = craft_token(cuts, "assignment", "ASSIGN", ":=", "binding assignment", "operator")
```

The terminal symbol is an uppercase grammar identity. The lexeme is the spelling users may type. The meaning and role describe the token's intent. A token can only be created from a fragment already selected by `craft_cut`.

Supported roles are `keyword`, `identifier`, `operator`, `delimiter` and `literal`. Lexical collisions are checked later across the complete design, because no isolated token can know the rest of the language.

### 2.4 Arrange grammar productions

```sambu
let program = craft_rule("Program", ["Statement"])
let statement = craft_rule("Statement", ["$LET", "$IDENT", "$ASSIGN", "$NUMBER"])
let empty_tail = craft_rule("Tail", [])
```

A production has one nonterminal on the left and an ordered sequence on the right. A reference beginning with `$` names a terminal; all other references name nonterminals. An empty right-hand side represents epsilon. Alternative productions are represented as multiple rules with the same left-hand nonterminal.

This layer deliberately begins with explicit productions rather than guessing precedence or silently translating a prose description into executable grammar.

### 2.5 Assemble and audit

```sambu
let design = craft_assemble(
  "Pondlet",
  [archive],
  [binding, name, assignment],
  [program, statement],
  "Program"
)
let audit = craft_master(design)

print(audit.status)
print(audit.errors)
print(audit.warnings)
print(audit.token_coverage)
print(audit.grammar_reachability)
print(audit.source_coverage)
```

The audit detects:

- duplicate source names, terminal symbols, token spellings and productions;
- tokens whose source or source fragment is absent;
- references to undefined terminals or nonterminals;
- an undefined start symbol;
- unreachable nonterminals;
- terminals and source fragments that are never used.

Errors block readiness. Warnings preserve useful but incomplete drafts. Coverage values are ratios, not aesthetic scores: a higher number does not prove that a language is easier to learn, safer or more expressive.

## 3. Stable diagnostic codes

| Code | Meaning | Severity |
|---|---|---|
| `LC001` | Duplicate source name | Error |
| `LC002` | Token references unknown source | Error |
| `LC003` | Token references absent source fragment | Error |
| `LC004` | Duplicate terminal symbol | Error |
| `LC005` | Duplicate token spelling | Error |
| `LC006` | Duplicate production | Error |
| `LC007` | Undefined terminal reference | Error |
| `LC008` | Undefined nonterminal reference | Error |
| `LC010` | Undefined start nonterminal | Error |
| `LW001` | Unreachable nonterminals | Warning |
| `LW002` | Unused terminals | Warning |
| `LW003` | Source fragments not mapped to terminals | Warning |

Diagnostics are deterministic and returned as arrays on the audit record. They do not mutate the original source or silently repair a grammar.

## 4. Design doctrine

The music blueprint suggests several durable programming-language principles:

1. **Source quality before vocabulary volume.** A small set of meaningful primitives is more valuable than a large list of decorative keywords.
2. **Semantic fragments before surface spelling.** Decide what a construct does before deciding what it sounds or looks like.
3. **Transform, do not merely imitate.** References may inspire a concept, but SAMBU's token, grammar and runtime contracts must be independently specified.
4. **Arrangement before optimization.** Define production rules and their boundaries before attempting parser or compiler optimization.
5. **Low-level pressure must not obscure meaning.** Runtime representation and future IR design must preserve the semantics expressed by the grammar.
6. **Mastering means verification, not a vanity score.** Report collisions, missing edges, reachability and coverage; never collapse language quality into one arbitrary number.
7. **Preserve compatibility deliberately.** A new grammar surface must pass a conformance corpus before it can replace or alias an existing one.

## 5. Implementation boundary and next compiler stages

The current feature creates and audits a **language-design blueprint**. It does not yet emit a lexer table, parser, typed AST, HIR, MIR, LIR, bytecode or native executable. The existing SAMBU grammar remains unchanged.

A responsible next sequence is:

1. Version the blueprint schema and publish a grammar conformance corpus.
2. Add a deterministic exporter from validated terminals and productions to a lexer/parser adapter.
3. Parse into source-spanned AST nodes and compare parser behavior against the corpus.
4. Add semantic/type checks only after the syntax contract is stable.
5. Lower the checked AST into backend-independent HIR, then SSA MIR and target LIR.
6. Differentially test interpreter and compiler behavior before enabling a native backend.

This keeps the musical metaphor useful without mistaking a design document for an implemented compiler.
