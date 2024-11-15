.PHONY: install test ci lint format unit integration cppinstall build

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

lint:
	poetry run mypy .
	poetry run ruff check .
	poetry run ruff format --check

format:
	poetry run ruff format
	poetry run ruff check --fix

unit:
	poetry run pytest src/pysrc/test/unit

integration:
	poetry run pytest src/pysrc/test/integration

