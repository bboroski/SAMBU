# NUN OS integration contract — SAMBU

## Ownership
SAMBU owns the language and toolchain boundary: compiler frontend/backend integration, the NUN target description, freestanding runtime support, SDK headers/libraries, linker integration and package metadata. NUN remains the sole owner of kernel source, boot code, HAL, memory management and privileged execution.

## Integration direction
1. Define a versioned NUN target descriptor for x86_64 first; add ARM64 only when the kernel has a validated boot target.
2. Expose SaintSI syscall and ABI declarations as generated or checked headers rather than duplicating numeric syscall identifiers.
3. Separate hosted SAMBU programs from freestanding kernel objects. Kernel builds must not inherit Python, desktop, filesystem or host threading dependencies.
4. Package cross-compiler configuration, linker scripts, debug symbols and SDK headers as reproducible toolchain artifacts.
5. Add ABI compatibility and reproducible-build checks to the SAMBU test matrix.

## Acceptance gates
- A minimal freestanding NUN-target object compiles and links against the versioned kernel ABI.
- Compiler output is deterministic for a pinned toolchain and source revision.
- Unsupported target features fail explicitly rather than silently emitting host binaries.
- Host-side SAMBU features remain independently testable.

## Current status
This document establishes the integration boundary. It does not claim a NUN-target backend, libc port, native package manager or bootable SAMBU-produced kernel image is already complete.
