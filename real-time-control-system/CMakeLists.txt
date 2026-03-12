cmake_minimum_required(VERSION 3.16)
project(real_time_control_system VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(BUILD_TESTS "Build test targets" ON)

include_directories(include)

add_library(realtime_core
    src/controller.cpp
    src/filter.cpp
    src/plant.cpp
    src/config.cpp
)

target_include_directories(realtime_core PUBLIC include)

target_compile_options(realtime_core PRIVATE -Wall -Wextra -Wpedantic)

add_executable(realtime_control src/main.cpp)
target_link_libraries(realtime_control PRIVATE realtime_core pthread)

if(BUILD_TESTS)
    enable_testing()
    add_executable(test_realtime_control tests/test_control.cpp)
    target_link_libraries(test_realtime_control PRIVATE realtime_core)
    add_test(NAME realtime_control_tests COMMAND test_realtime_control)
endif()
