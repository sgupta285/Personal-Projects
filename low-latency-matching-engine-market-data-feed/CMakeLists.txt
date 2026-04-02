cmake_minimum_required(VERSION 3.20)
project(low_latency_matching_engine VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(LLMDE_ENABLE_ASAN "Enable address sanitizer" OFF)
option(LLMDE_ENABLE_BENCHMARK_HINTS "Enable extra benchmark compiler flags" ON)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -Wshadow -Wconversion)
  if(LLMDE_ENABLE_BENCHMARK_HINTS)
    add_compile_options(-O3 -march=native)
  endif()
  if(LLMDE_ENABLE_ASAN)
    add_compile_options(-fsanitize=address -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address)
  endif()
endif()

include_directories(include)

add_library(llmde_core
  src/core/order_book.cpp
  src/engine/matching_engine.cpp
  src/feed/itch_parser.cpp
  src/io/udp_publisher.cpp
)

target_include_directories(llmde_core PUBLIC include)

target_link_libraries(llmde_core PUBLIC pthread)

add_executable(matching_engine_app apps/matching_engine_app.cpp)
target_link_libraries(matching_engine_app PRIVATE llmde_core)

add_executable(feed_replayer_app apps/feed_replayer_app.cpp)
target_link_libraries(feed_replayer_app PRIVATE llmde_core)

add_executable(order_book_tests tests/order_book_tests.cpp)
target_link_libraries(order_book_tests PRIVATE llmde_core)

add_executable(parser_tests tests/parser_tests.cpp)
target_link_libraries(parser_tests PRIVATE llmde_core)

enable_testing()
add_test(NAME order_book_tests COMMAND order_book_tests)
add_test(NAME parser_tests COMMAND parser_tests)
