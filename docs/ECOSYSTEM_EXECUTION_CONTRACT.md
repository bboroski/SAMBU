# SAMBU — Ecosystem Execution Contract

## Purpose and ownership

Language, IDE, scientific modeling, Pascal/Delphi/Fortran compatibility experiments, typed workflow automation, and reproducible domain tooling. Keep interpreter, IDE, native compiler slice, and compatibility adapters independently versioned; never describe the native slice as a complete compiler until code generation and ABI tests exist.

The repository name `SAMBU` is its canonical identity. Keep it unchanged in package metadata, APIs, documentation, links, build artifacts, and integration manifests. Do not replace it with an alias or a new acronym. Other repository names remain exact identifiers too.

## Cross-repository engineering rules

1. **Contract-first integration.** Connect components through versioned schemas, stable capability IDs, explicit ABI versions, declared dependencies, bounded resource profiles, and deterministic failure codes. A shared topic or file format does not prove compatibility.
2. **No imaginary functionality.** A feature is `planned`, `implemented`, `host-tested`, `cross-compiled`, `emulator-tested`, or `hardware-qualified`. Use the strongest status supported by committed source and reproducible evidence. Documentation, mocks, screenshots, manifests, and simulations do not prove runtime or physical support.
3. **Ambiguity becomes a typed outcome.** Missing, unknown, unsupported, stale, conflicting, or incomplete inputs produce explicit result codes, diagnostics, and recovery instructions. Do not silently guess, coerce, or discard.
4. **Bounded by default.** Every queue, buffer, retry loop, parser, dependency graph, and resource budget has a stated limit and overflow behavior. Prefer reject/backpressure over silent data loss. Any lossy telemetry policy must be explicit.
5. **Safe integration.** Untrusted extensions remain data until validated. Use least privilege, scoped capabilities, pinned inputs, provenance, digest/signature policy, resource limits, and rollback. A native in-process module is not a sandbox.
6. **Freshness and provenance.** Time-sensitive metadata records its source, observed-at time, version, and validation state. Never present estimates, cached values, or generated examples as current verified facts.
7. **No culturally loaded internal labels.** Use precise technical names for modules, states, interfaces, and tests. Preserve this repository's exact name and the exact names of connected repositories.

## Platform and execution matrix

| Target | Engineering treatment | Claim gate |
|---|---|---|
| Intel x86 / x86-64 | Baseline ISA family; vendor-specific paths are separately gated | Compiler, ABI, build and host/emulator tests |
| AMD x86 / x86-64 | Same ISA-family baseline where applicable; separately test vendor extensions and dispatch | Exact CPU feature detection and tests on AMD hardware |
| Apple Intel | x86-64 platform profile with Apple OS/toolchain constraints | Build and tests on the named macOS version/device |
| Apple Silicon | AArch64 platform profile; do not assume x86 binary compatibility | Native arm64 build and tests; translation is a separate runtime |
| Elbrus / E2K | Experimental research target; never infer ABI or instruction behavior from another ISA | E2K compiler, binutils/linker, startup, ABI tests, emulator or board evidence |
| Other targets | Explicit adapter and capability profile; unsupported by default | Target-specific toolchain and conformance evidence |

An architecture label in a manifest is a selection hint, not proof of support. Vendor optimization must use verified runtime feature detection and a conservative fallback.

## NUN and executable compatibility boundary

NUN and NUNLauncher are not to be described as bootable operating systems or loaders until their boot path, image format, linker configuration, reproducible build, and emulator/target tests exist. A Windows `.exe` is not executable merely because a kernel can read a file. Running Windows applications or games requires, at minimum, a PE/COFF loader, process and memory model, compatible system-call and Win32 API surface, x86/x64 execution or translation, filesystem and handle semantics, graphics/audio/input paths, and per-application isolation. Game compatibility additionally depends on graphics API mapping, drivers, timing, DRM and anti-cheat constraints. Implement these as separately testable compatibility layers; never bypass isolation or claim universal compatibility.

Fortran, Pascal, and Delphi belong in explicit language front ends, dialect adapters, compiler bridges, or SDK tooling. Listing a language as an inspiration or syntax profile does not mean its compiler/runtime is implemented.

## Interface and product experience

Use the shared Duck Black / Yellow design contract in `design/DUCK_UI_SYSTEM.md` and `design/duck-ui.tokens.json`: `#0D0D0D` graphite/black foundations, `#FFD600` primary action/focus, readable neutral surfaces, strong contrast, keyboard-visible focus, text/icon state labels, responsive density, and reduced-motion support. Treat material effects (glass, metal, paper, depth, lighting) as progressive enhancement; preserve legibility, performance, reduced-motion behavior, and high-contrast modes. Do not let decorative effects obscure status or controls.

Keep product documentation aligned in Ukrainian (`README.md`), English (`README.en.md`), and Russian (`README.ru.md`). Each version must preserve the same feature set, setup steps, limitations, release status, and security notes. Keep each README under 10,000 characters. Write clear marketing around demonstrated value, not unimplemented claims.

## Release and management gates

- Build from a clean checkout with pinned or bounded toolchain versions.
- Run unit, negative, boundary, compatibility, and regression tests.
- Validate schemas, manifests, localization parity, generated artifacts, and documentation links.
- Publish compiler version, target, flags, commit, artifact digest, and test results.
- Use draft pull requests for cross-repository changes; require review before merging.
- Track every proposed capability as an issue or manifest entry with owner, dependency, risk, acceptance test, and status. A target of 10,000 capabilities means a traceable backlog—not 10,000 empty stubs.

## Repository-specific acceptance focus

Grammar and dialect fixtures; diagnostics with source spans; deterministic interpreter tests; native codegen and ABI tests before any native-compiler support claim; runnable Fortran/Pascal/Delphi compatibility examples for each advertised dialect.

---

*Built with care, engineering discipline, and love for the people who use it.*
