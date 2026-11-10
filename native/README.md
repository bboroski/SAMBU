# SAMBU Native Kernel

This directory starts a backend-independent native compiler path in portable C11.
It is intentionally separate from the existing Python-hosted interpreter.

## Implemented in this first slice

- Typed scalar HIR for boolean, signed 64-bit integer and 64-bit floating values.
- A single-basic-block MIR in SSA form with explicit type metadata on each result.
- A verifier for dense SSA definitions, use-before-definition, operand types and final returns.
- Explicit operand-free terminators for unit-returning MIR/LIR functions, with strict verifier checks.
- A first LIR with virtual-register identifiers and a second verifier.
- A chunked arena allocator for compiler-lifetime objects.
- A compiler-lifetime string interner with stable returned pointers.
- Recursive HIR-expression → MIR lowering and MIR → LIR lowering.
- CMake/CTest tests for alignment, interning, type rejection, lowering and invalid SSA.

## Build and test

From this directory:

\`\`\`sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build --output-on-failure
\`\`\`

The library has no third-party dependency and does not link to Python or libc++.
It does use the C standard library allocator and string routines.

## Deliberate limits

This is a compiler kernel, not yet a complete compiler. The current MIR verifier
accepts one basic block only; there is no source parser bridge, CFG/phi-node
support, optimization pipeline, IR serialization, object writer, LLVM/Cranelift
adapter, native runtime, borrow checker or machine-code emission. The LIR uses
virtual registers and is not an ISA instruction set.

The Python interpreter remains the compatibility implementation while the
native front end and back ends are developed incrementally.
