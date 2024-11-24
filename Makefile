.PHONY: install cppinstall build test ci lint pylint cpplint fomrat unit cpptest integration test-backtester

RELEASE_TYPE = Release
PY_SRC = src/pysrc

install:
	poetry lock --no-update
	poetry install
	poetry env use python3.12

cppinstall:
	conan install . --build=missing

build: cppinstall
	cd build && cmake .. -DCMAKE_TOOLCHAIN_FILE=$(RELEASE_TYPE)/generators/conan_toolchain.cmake -DCMAKE_BUILD_TYPE=$(RELEASE_TYPE) -G Ninja
	cd build && cmake --build .

test: lint unit

ci: test integration

lint: pylint cpplint

pylint:
	poetry run mypy src
	poetry run ruff check src
	poetry run ruff format --check src

cpplint:
	find src -name '*.cpp' -o -name '*.hpp' | xargs clang-format --style=file --dry-run -Werror
	run-clang-tidy -j $(shell nproc) -p build

format:
	poetry run ruff format src
	poetry run ruff check --fix src
	find src -name '*.cpp' -o -name '*.hpp' | xargs clang-format --style=file -i
	run-clang-tidy -fix -j $(shell nproc) -p build

unit:
	poetry run pytest src/pysrc/test/unit

integration:
	poetry run pytest src/pysrc/test/integration

cpptest: build test-backtester

test-backtester:
	cd build && ./backtester_tests
