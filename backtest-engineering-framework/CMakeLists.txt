cmake_minimum_required(VERSION 3.16)
project(backtest_engineering_framework LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(bef_core
    cpp/src/cost_model.cpp
    cpp/src/fill_simulator.cpp
)

target_include_directories(bef_core PUBLIC cpp/include)

target_compile_options(bef_core PRIVATE -O3 -Wall -Wextra -Wpedantic)

add_executable(cost_model_bench cpp/src/cost_model_bench.cpp)
target_link_libraries(cost_model_bench PRIVATE bef_core)

add_executable(bef_cpp_tests cpp/tests/test_cost_model.cpp)
target_link_libraries(bef_cpp_tests PRIVATE bef_core)

include(CTest)
enable_testing()
add_test(NAME bef_cpp_tests COMMAND bef_cpp_tests)
