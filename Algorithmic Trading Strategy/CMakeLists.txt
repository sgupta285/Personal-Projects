cmake_minimum_required(VERSION 3.18)
project(TradingBacktest VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Optimization flags
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -fsanitize=address")

# OpenMP
find_package(OpenMP REQUIRED)

# PostgreSQL (optional)
find_package(PostgreSQL QUIET)

# Source files
set(ENGINE_SOURCES
    src/engine/backtest_engine.cpp
    src/engine/portfolio.cpp
    src/engine/execution.cpp
    src/engine/risk_manager.cpp
    src/strategies/momentum.cpp
    src/strategies/mean_reversion.cpp
    src/data/market_data.cpp
    src/data/data_generator.cpp
    src/utils/metrics.cpp
    src/utils/walk_forward.cpp
    src/utils/csv_writer.cpp
)

# Main library
add_library(backtest_lib STATIC ${ENGINE_SOURCES})
target_include_directories(backtest_lib PUBLIC ${CMAKE_SOURCE_DIR}/src)
target_link_libraries(backtest_lib PUBLIC OpenMP::OpenMP_CXX)

if(PostgreSQL_FOUND)
    target_link_libraries(backtest_lib PRIVATE PostgreSQL::PostgreSQL)
    target_compile_definitions(backtest_lib PRIVATE HAS_POSTGRES=1)
endif()

# SIMD support detection
include(CheckCXXCompilerFlag)
check_cxx_compiler_flag("-mavx2" COMPILER_SUPPORTS_AVX2)
check_cxx_compiler_flag("-msse4.2" COMPILER_SUPPORTS_SSE42)

if(COMPILER_SUPPORTS_AVX2)
    target_compile_options(backtest_lib PRIVATE -mavx2 -mfma)
    target_compile_definitions(backtest_lib PRIVATE USE_AVX2=1)
    message(STATUS "AVX2 support enabled")
elseif(COMPILER_SUPPORTS_SSE42)
    target_compile_options(backtest_lib PRIVATE -msse4.2)
    target_compile_definitions(backtest_lib PRIVATE USE_SSE42=1)
    message(STATUS "SSE4.2 support enabled")
endif()

# Main executable
add_executable(backtest src/main.cpp)
target_link_libraries(backtest PRIVATE backtest_lib)

# Walk-forward runner
add_executable(walk_forward_runner src/walk_forward_runner.cpp)
target_link_libraries(walk_forward_runner PRIVATE backtest_lib)

# Benchmark executable
add_executable(benchmark src/benchmark.cpp)
target_link_libraries(benchmark PRIVATE backtest_lib)

# Tests
enable_testing()
add_executable(tests
    tests/test_portfolio.cpp
    tests/test_metrics.cpp
    tests/test_momentum.cpp
    tests/test_execution.cpp
    tests/test_walk_forward.cpp
    tests/test_main.cpp
)
target_link_libraries(tests PRIVATE backtest_lib)
add_test(NAME AllTests COMMAND tests)

# Install
install(TARGETS backtest walk_forward_runner DESTINATION bin)
