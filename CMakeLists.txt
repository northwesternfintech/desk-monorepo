cmake_minimum_required(VERSION 3.14)

include(cmake/prelude.cmake)

project(
    desk_monorepo
    VERSION 0.1.0
    DESCRIPTION "Short description"
    HOMEPAGE_URL "https://example.com/"
    LANGUAGES CXX
)

include(cmake/project-is-top-level.cmake)
include(cmake/variables.cmake)

# ---- Declare library ----

add_library(
    desk_monorepo_lib OBJECT
    src/cppsrc/src/lib.cpp
)

target_include_directories(
    desk_monorepo_lib ${warning_guard}
    PUBLIC
    "\$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src/cppsrc/src>"
)

target_compile_features(desk_monorepo_lib PUBLIC cxx_std_20)

find_package(fmt REQUIRED)
target_link_libraries(desk_monorepo_lib PRIVATE fmt::fmt)

# ---- Declare executable ----

add_executable(desk_monorepo_exe src/cppsrc/src/main.cpp)
add_executable(desk_monorepo::exe ALIAS desk_monorepo_exe)

set_property(TARGET desk_monorepo_exe PROPERTY OUTPUT_NAME desk_monorepo)

target_compile_features(desk_monorepo_exe PRIVATE cxx_std_20)

target_link_libraries(desk_monorepo_exe PRIVATE desk_monorepo_lib)

# ---- Install rules ----

if(NOT CMAKE_SKIP_INSTALL_RULES)
  include(cmake/install-rules.cmake)
endif()

# ---- Developer mode ----

if(NOT desk_monorepo_DEVELOPER_MODE)
  return()
elseif(NOT PROJECT_IS_TOP_LEVEL)
  message(
      AUTHOR_WARNING
      "Developer mode is intended for developers of desk_monorepo"
  )
endif()

include(cmake/dev-mode.cmake)
