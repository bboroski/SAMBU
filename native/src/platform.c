#include "sambu/platform.h"

#include <stdint.h>

SambuPlatformInfo sambu_platform_info(void)
{
    SambuPlatformInfo result = {SAMBU_ARCH_UNKNOWN, (uint32_t)(sizeof(void *) * 8u), 0u, 0u};
    const uint16_t marker = 1u;
    result.little_endian = (*(const uint8_t *)&marker == 1u) ? 1u : 0u;

#if defined(__e2k__)
    result.architecture = SAMBU_ARCH_E2K;
    result.elf_machine = 175u;
#elif defined(__x86_64__) || defined(_M_X64)
    result.architecture = SAMBU_ARCH_X86_64;
#elif defined(__i386__) || defined(_M_IX86)
    result.architecture = SAMBU_ARCH_X86;
#elif defined(__aarch64__) || defined(_M_ARM64)
    result.architecture = SAMBU_ARCH_AARCH64;
#elif defined(__arm__) || defined(_M_ARM)
    result.architecture = SAMBU_ARCH_ARM32;
#elif defined(__riscv) && __riscv_xlen == 64
    result.architecture = SAMBU_ARCH_RISCV64;
#elif defined(__riscv) && __riscv_xlen == 32
    result.architecture = SAMBU_ARCH_RISCV32;
#endif
    return result;
}

const char *sambu_architecture_name(SambuArchitecture architecture)
{
    switch (architecture) {
        case SAMBU_ARCH_X86: return "x86";
        case SAMBU_ARCH_X86_64: return "x86_64";
        case SAMBU_ARCH_ARM32: return "arm";
        case SAMBU_ARCH_AARCH64: return "aarch64";
        case SAMBU_ARCH_RISCV32: return "riscv32";
        case SAMBU_ARCH_RISCV64: return "riscv64";
        case SAMBU_ARCH_E2K: return "e2k";
        case SAMBU_ARCH_UNKNOWN:
        default: return "unknown";
    }
}
