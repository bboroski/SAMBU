cmake_minimum_required(VERSION 3.16)
project(sambu_native_ir VERSION 0.1.0 LANGUAGES C)

include(CTest)

add_library(sambu_ir STATIC src/ir.c)
target_include_directories(sambu_ir PUBLIC
    $<BUILD_INTERFACE:\${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_compile_features(sambu_ir PUBLIC c_std_11)
set_target_properties(sambu_ir PROPERTIES
    C_STANDARD 11
    C_STANDARD_REQUIRED YES
    C_EXTENSIONS NO
)

if(MSVC)
    target_compile_options(sambu_ir PRIVATE /W4 /WX)
else()
    target_compile_options(sambu_ir PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()

if(BUILD_TESTING)
    add_executable(sambu_ir_tests tests/test_ir.c)
    target_link_libraries(sambu_ir_tests PRIVATE sambu_ir)
    if(MSVC)
        target_compile_options(sambu_ir_tests PRIVATE /W4 /WX)
    else()
        target_compile_options(sambu_ir_tests PRIVATE -Wall -Wextra -Wpedantic -Werror)
    endif()
    add_test(NAME sambu_ir_tests COMMAND sambu_ir_tests)
endif()
