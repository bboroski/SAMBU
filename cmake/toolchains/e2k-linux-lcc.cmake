# MCST LCC toolchain for E2K Linux userspace targets.
# Supply E2K_LCC (CMake) or E2K_CC (environment) from the vendor SDK.
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR e2k)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

if(NOT DEFINED E2K_LCC OR E2K_LCC STREQUAL "")
    if(DEFINED ENV{E2K_CC} AND NOT "$ENV{E2K_CC}" STREQUAL "")
        set(E2K_LCC "$ENV{E2K_CC}")
    elseif(DEFINED ENV{E2K_LCC} AND NOT "$ENV{E2K_LCC}" STREQUAL "")
        set(E2K_LCC "$ENV{E2K_LCC}")
    else()
        find_program(E2K_LCC NAMES lcc)
    endif()
endif()

if(NOT E2K_LCC)
    message(FATAL_ERROR
        "E2K LCC compiler not found. Set -DE2K_LCC=/path/to/lcc or E2K_CC.")
endif()

set(CMAKE_C_COMPILER "${E2K_LCC}" CACHE FILEPATH "MCST E2K LCC compiler")
if(DEFINED ENV{E2K_SYSROOT} AND NOT "$ENV{E2K_SYSROOT}" STREQUAL "")
    set(CMAKE_SYSROOT "$ENV{E2K_SYSROOT}")
endif()

message(STATUS "E2K target selected: ${CMAKE_SYSTEM_PROCESSOR}")
message(STATUS "E2K compiler: ${CMAKE_C_COMPILER}")
if(CMAKE_SYSROOT)
    message(STATUS "E2K sysroot: ${CMAKE_SYSROOT}")
endif()
