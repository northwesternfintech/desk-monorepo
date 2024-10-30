#include <gtest/gtest.h>

#include "lib.hpp"

TEST(UnitTests, NameIsDeskMonorepo) {
  auto const lib = library{};
  ASSERT_EQ(lib.name, "desk_monorepo");
}
