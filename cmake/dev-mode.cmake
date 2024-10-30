include(cmake/folders.cmake)

include(CTest)
if(BUILD_TESTING)
  add_subdirectory(src/cppsrc/test)
endif()

add_custom_target(
    run-exe
    COMMAND desk_monorepo_exe
    VERBATIM
)
add_dependencies(run-exe desk_monorepo_exe)

include(cmake/lint-targets.cmake)
include(cmake/spell-targets.cmake)

add_folders(Project)
