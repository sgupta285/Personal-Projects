cmake_minimum_required(VERSION 3.18)
project(OptionsPricingEngine VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -fsanitize=address")

# OpenMP
find_package(OpenMP REQUIRED)

# SIMD detection
include(CheckCXXCompilerFlag)
check_cxx_compiler_flag("-mavx2" COMPILER_SUPPORTS_AVX2)
check_cxx_compiler_flag("-msse4.2" COMPILER_SUPPORTS_SSE42)

# Source files
set(ENGINE_SOURCES
    src/pricing/black_scholes.cpp
    src/pricing/binomial_tree.cpp
    src/monte_carlo/mc_engine.cpp
    src/monte_carlo/variance_reduction.cpp
    src/greeks/finite_difference.cpp
    src/greeks/analytical_greeks.cpp
    src/calibration/implied_vol.cpp
    src/calibration/vol_surface.cpp
    src/utils/normal_dist.cpp
    src/utils/random_gen.cpp
    src/utils/timer.cpp
)

add_library(options_lib STATIC ${ENGINE_SOURCES})
target_include_directories(options_lib PUBLIC ${CMAKE_SOURCE_DIR}/src)
target_link_libraries(options_lib PUBLIC OpenMP::OpenMP_CXX)

if(COMPILER_SUPPORTS_AVX2)
    target_compile_options(options_lib PRIVATE -mavx2 -mfma)
    target_compile_definitions(options_lib PRIVATE USE_AVX2=1)
    message(STATUS "AVX2 + FMA enabled")
elseif(COMPILER_SUPPORTS_SSE42)
    target_compile_options(options_lib PRIVATE -msse4.2)
    target_compile_definitions(options_lib PRIVATE USE_SSE42=1)
endif()

# Main executable
add_executable(options_pricer src/main.cpp)
target_link_libraries(options_pricer PRIVATE options_lib)

# Benchmark
add_executable(benchmark src/benchmark.cpp)
target_link_libraries(benchmark PRIVATE options_lib)

# Tests
enable_testing()
add_executable(tests
    tests/test_black_scholes.cpp
    tests/test_monte_carlo.cpp
    tests/test_greeks.cpp
    tests/test_implied_vol.cpp
    tests/test_vol_surface.cpp
    tests/test_main.cpp
)
target_link_libraries(tests PRIVATE options_lib)
add_test(NAME AllTests COMMAND tests)

install(TARGETS options_pricer DESTINATION bin)
