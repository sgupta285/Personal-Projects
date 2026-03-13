cmake_minimum_required(VERSION 3.20)
project(distributed_data_acquisition_system LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(daq_core
    src/core/metrics.cpp
    src/core/scenario.cpp
)
target_include_directories(daq_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(daq_core PRIVATE -O2 -Wall -Wextra -Wpedantic)

add_executable(daq_acquire src/acquisition/main.cpp)
target_link_libraries(daq_acquire PRIVATE daq_core pthread)

add_executable(daq_replay src/replay/main.cpp)
target_link_libraries(daq_replay PRIVATE daq_core)

enable_testing()

add_executable(test_queue tests/test_queue.cpp)
target_link_libraries(test_queue PRIVATE daq_core pthread)
add_test(NAME queue_test COMMAND test_queue)

add_executable(test_metrics tests/test_metrics.cpp)
target_link_libraries(test_metrics PRIVATE daq_core)
add_test(NAME metrics_test COMMAND test_metrics)
