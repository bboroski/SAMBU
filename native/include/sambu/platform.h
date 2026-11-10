#ifndef SAMBU_PLATFORM_H
#define SAMBU_PLATFORM_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum SambuArchitecture {
    SAMBU_ARCH_UNKNOWN = 0,
    SAMBU_ARCH_X86,
    SAMBU_ARCH_X86_64,
    SAMBU_ARCH_ARM32,
    SAMBU_ARCH_AARCH64,
    SAMBU_ARCH_RISCV32,
    SAMBU_ARCH_RISCV64,
    SAMBU_ARCH_E2K
} SambuArchitecture;

typedef struct SambuPlatformInfo {
    SambuArchitecture architecture;
    uint32_t pointer_bits;
    uint32_t little_endian;
    uint32_t elf_machine;
} SambuPlatformInfo;

/* Compile-time target facts; no speculative CPU feature probing is performed. */
SambuPlatformInfo sambu_platform_info(void);
const char *sambu_architecture_name(SambuArchitecture architecture);

#ifdef __cplusplus
}
#endif
#endif
