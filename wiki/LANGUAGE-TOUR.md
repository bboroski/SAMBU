# Language tour

## Execution model

SAMBU source is interpreted. At a high level, source text passes through a lexer and parser, is represented as syntax-tree data, and is evaluated by the runtime.

```text
.sambu source
    |
    v
Lexer / tokens
    |
    v
Parser
    |
    +--> legacy tuple AST (parse)
    |
    +--> immutable typed AST (parse_ast)
    |
    v
Interpreter / runtime
    |
    v
Formatted values and diagnostics
```

The current package exports source-aware parser structures and keeps a legacy AST conversion path for compatibility. This is an interpreter pipeline, not a claim of native machine-code compilation.

## What the language is for

The language began as a compact scientific DSL for statistical mechanics and introductory kinetic theory. It has since expanded into a broader set of built-in models and executable examples, including percentages, object-oriented programming, game-state helpers, Anatidae teaching models and sparse voxel operations.

SAMBU is particularly useful when a small readable program can express a calculation or bounded model more clearly than a larger host application.

## A small example

```sambu
let temperature = 300 * K
let particle_mass = 6.6e-26 * kg
let speeds = maxwell(temperature, particle_mass)

print(speeds.most_probable)
print(speeds.mean)
print(speeds.rms)
```

The result is a record whose fields expose different characteristic speeds for the classical Maxwell distribution.

## Core language elements

The documented language surface includes:

- immutable `let` bindings;
- numbers, strings, booleans, `null`, arrays and records;
- arithmetic, comparisons and boolean operators;
- function calls, indexing and record-field access;
- user-defined functions and `return`;
- `if` / `else`;
- bounded `for` iteration;
- lexical scopes;
- classes and object methods;
- interfaces and traits in the extended OOP slice;
- built-in physical units and constants.

Exact feature availability should be checked against the current source and tests, because some historical reference pages were written for earlier alpha versions.

## Language versus toolkit

A crucial distinction:

| Surface | Example | How it is used |
|---|---|---|
| SAMBU source language | `maxwell(T, mass)` | Written in a `.sambu` program |
| Python package API | `from sambu.judo import Judo` | Imported by a Python host program |
| CLI tool | `sambu-studio inspect ...` | Invoked in a terminal |
| Engine adapter source | Unity / Unreal / Godot bridge | Added and compiled in the host engine project |

Not every module in the repository is available as a built-in function in a SAMBU source program.

## Runtime safety profile

The original DSL intentionally avoids exposing arbitrary Python evaluation, general imports, filesystem access or network access to SAMBU programs. Bounded constructs such as `range` and `for` limit resource growth. Host-side Python modules may perform operations unavailable to the interpreted language, but their behavior is governed by their own APIs and trust boundaries.

## Further reading

- [Syntax and control flow](SYNTAX-AND-CONTROL-FLOW.md)
- [Types, units and numerics](TYPES-UNITS-AND-NUMERICS.md)
- [Scientific computing](SCIENTIFIC-COMPUTING.md)
- [Domain libraries](DOMAIN-LIBRARIES.md)
