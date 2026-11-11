# NUN integration — compiler, language runtime and SDK boundary

## Assigned responsibility

SAMBU is the ecosystem's experimental language and developer-tooling project. Its NUN-facing direction is a future compiler target, standard-library port and SDK; it is not the kernel or bootloader.

## Current verified state

- The repository contains a Python-hosted language/runtime, CLI and IDE tooling.
- A limited C11 native-compiler slice exists, but it is not a complete source-to-machine-code compiler.
- There is no verified NUN target backend, kernel sysroot, libc port or production cross-compiler.

## Integration contract

1. Keep host execution and freestanding target code generation as distinct build profiles.
2. Do not link Python, Tkinter or host-only runtime components into a freestanding kernel image.
3. A future target backend must define an explicit target triple, data layout, calling convention, relocation model and linker contract before emitting objects.
4. Kernel headers and user-space SDK headers must be separate. Kernel code must not silently import hosted libc.
5. Pin compiler, linker and SDK versions in reproducible toolchain manifests; record the exact compiler revision in build artifacts.
6. Add ABI conformance tests and compile-only fixtures before claiming SAMBU can build NUN applications.

## Dependency order

The kernel's QEMU boot, memory and interrupt gates in [NUN](https://github.com/bboroski/NUN) precede the user-space SDK. A SAMBU target backend can be developed against a documented experimental ABI, but cannot be declared stable while the syscall and userspace contracts are absent.

## ABI status

No NUN target triple, object format or syscall ABI is frozen in this change. Existing SAMBU language/runtime APIs remain independent. Record future NUN-facing changes in `CHANGELOG.NUN`.
