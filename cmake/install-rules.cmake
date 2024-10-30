install(
    TARGETS desk_monorepo_exe
    RUNTIME COMPONENT desk_monorepo_Runtime
)

if(PROJECT_IS_TOP_LEVEL)
  include(CPack)
endif()
