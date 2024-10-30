# Parent project does not export its library target, so this CML implicitly
# depends on being added from it, i.e. the testing is done only from the build
# tree and is not feasible from an install location

project(desk_monorepoTests LANGUAGES CXX)

# ---- Dependencies ----

find_package(GTest REQUIRED)
include(GoogleTest)

# ---- Tests ----

add_executable(desk_monorepo_test src/desk_monorepo_test.cpp)
target_link_libraries(
    desk_monorepo_test PRIVATE
    desk_monorepo_lib
	GTest::gtest_main

)
target_compile_features(desk_monorepo_test PRIVATE cxx_std_20)

gtest_discover_tests(desk_monorepo_test)

# ---- End-of-file commands ----

add_folders(Test)
