# E2K / Elbrus platform profile

This profile enables **64-bit little-endian E2K Linux user-space builds** with
the MCST LCC toolchain. It records the ELF machine value
`EM_MCST_ELBRUS = 175`, the Linux machine name `e2k`, CPU/ISA variants and
the boundary between native application support and firmware boot support.

## Build path

- Native target: Elbrus Linux running on an E2K processor, with the MCST LCC
  compiler and matching runtime libraries installed.
- Cross target: x86_64 Linux build host with the MCST LCC cross-system
  programming environment and target sysroot.
- CMake toolchain: `cmake/toolchains/e2k-linux-lcc.cmake`.
- Compiler selection: set `E2K_LCC` or `E2K_CC` to the vendor compiler
  executable; set `E2K_SYSROOT` only when the SDK supplies a separate sysroot.

The vendor SDK is versioned by processor target and Elbrus Linux release. Do
not substitute a generic GCC cross compiler unless it can emit and link the
vendor E2K ABI. Toolchain installation and redistribution may have vendor
access/licensing requirements.

## Execution and boot boundary

The supported deployment route for these projects is a native E2K Linux
process. On physical hardware the machine firmware / Program of Initial Start
(PNS) initializes the board and launches the installed Elbrus Linux system;
the project then runs as a native userspace program.

The published `qemu-e2k` is a **user-mode** emulator for Linux application
binaries. It is not a full-system emulator, does not emulate the Elbrus board
firmware and cannot prove a cold boot of a bare-metal kernel.

The generic Limine release used by x86_64 projects does not list E2K among its
supported architectures. Therefore an x86 Limine ISO or an x86 boot protocol
must not be relabelled as an Elbrus boot image. A future bare-metal NUN port
needs a documented PNS/kernel image contract and platform-specific entry,
interrupt, memory-map and device initialization code.

## ISA and evidence

Elbrus Linux distributions identify E2K processor generations (including
v2-v7). The available vendor SDK packages are model/ISA-specific. The published
QEMU user-emulator manual lists v2-v6 profiles and explicitly does not qualify
v7 emulation. Keep the selected compiler target and runtime target aligned.

No project should claim E2K as hardware-verified until its E2K-native CI job or
a recorded hardware test has compiled **and executed** the target binary. A
host-side unit test or successful cross-compile alone is not execution proof.

## References

- [MCST developer downloads: LCC, E2K Linux sources and qemu-e2k](https://dev.mcst.ru/download/)
- [MCST Elbrus programming SDK](https://www.mcst.ru/SDK)
- [MCST Elbrus Linux architecture matrix](https://www.mcst.ru/elbrus_linux)
- [MCST Program of Initial Start (PNS)](https://www.mcst.ru/boot)
- [MCST qemu-e2k announcement and user-mode scope](https://www.mcst.ru/2025-12-25_qemu-e2k)
- [Limine supported architectures](https://github.com/Limine-Bootloader/Limine)
