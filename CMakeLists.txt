cmake_minimum_required(VERSION 3.20)

project (desk LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(GTest REQUIRED)

# --- File Declarations ---

# Headers
file(GLOB_RECURSE HEADERS src/*.hpp)

# Backtester
file(GLOB BACKTESTER_MAIN src/backtester/main.cpp)
file(GLOB_RECURSE BACKTESTER_TESTS src/backtester/tst/*.cpp)


# --- Executable Declarations ---

# Backtester
add_executable(backtester ${BACKTESTER_MAIN} ${HEADERS})
add_executable(backtester_tests ${BACKTESTER_TESTS} ${HEADERS})

# --- Packages ---
find_package(argparse REQUIRED)

SET(PACKAGES argparse::argparse)
# ---- Linking ---

SET(TARGETS backtester)
SET(TEST_TARGETS backtester_tests)

foreach (target ${TARGETS} ${TEST_TARGETS})
    target_include_directories(${target} PUBLIC src)
    target_link_libraries(${target} PRIVATE ${PACKAGES})
endforeach()

foreach (testtarget ${TEST_TARGETS})
    target_link_libraries(${testtarget} PRIVATE gtest::gtest)
endforeach()
