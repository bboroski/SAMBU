"""Runtime target identification for native Linux and cross-build diagnostics.

This module reports the host ABI/architecture. It does not claim that a
particular CPU instruction set or optional hardware feature is available.
"""
from __future__ import annotations

import platform
import struct
import sys
from typing import Any


_E2K_NAMES = {"e2k", "elbrus", "mcst-elbrus"}


def normalize_architecture(machine: str) -> str:
    value = machine.strip().lower().replace("_", "-")
    if value in _E2K_NAMES:
        return "e2k"
    if value in {"x86-64", "amd64"}:
        return "x86_64"
    if value in {"i386", "i486", "i586", "i686", "x86"}:
        return "x86"
    if value in {"aarch64", "arm64"}:
        return "aarch64"
    if value.startswith("arm"):
        return "arm"
    if value in {"riscv64", "riscv32"}:
        return value
    return value or "unknown"


def detect_target(
    *,
    machine: str | None = None,
    pointer_bits: int | None = None,
    byteorder: str | None = None,
    system: str | None = None,
) -> dict[str, Any]:
    """Return a stable, JSON-compatible description of the current host."""
    raw_machine = machine if machine is not None else platform.machine()
    architecture = normalize_architecture(raw_machine)
    bits = pointer_bits if pointer_bits is not None else struct.calcsize("P") * 8
    endian = byteorder if byteorder is not None else sys.byteorder
    os_name = (system if system is not None else platform.system()).lower()

    if bits not in (32, 64):
        raise ValueError("pointer_bits must be 32 or 64")
    if endian not in ("little", "big"):
        raise ValueError("byteorder must be 'little' or 'big'")

    is_e2k = architecture == "e2k"
    return {
        "architecture": architecture,
        "machine": raw_machine,
        "word_bits": bits,
        "endianness": endian,
        "operating_system": os_name,
        "elf_machine": 175 if is_e2k else None,
        "execution_abi": "MCST E2K Linux userspace ABI" if is_e2k and os_name == "linux" else None,
        "native_e2k_userspace": bool(is_e2k and bits == 64 and endian == "little" and os_name == "linux"),
        "bare_metal_support": False,
    }


def is_native_e2k_linux() -> bool:
    """True only for a 64-bit little-endian E2K Linux host."""
    target = detect_target()
    return bool(target["native_e2k_userspace"])
