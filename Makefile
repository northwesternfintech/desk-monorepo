.PHONY: py-install py-test py-ci py-lint py-format py-unit py-integration cpp-deps cpp-init cpp-build

py-install:
	poetry lock --no-update
	poetry install
	poetry env use python3.12

py-test: lint unit

py-ci: test integration

py-lint:
	poetry run mypy .
	poetry run ruff check .
	poetry run ruff format --check

py-format:
	poetry run ruff format
	poetry run ruff check --fix

py-unit:
	poetry run pytest src/pysrc/test/unit

py-integration:
	poetry run pytest src/pysrc/test/integration

cpp-deps:
	conan install . -s build_type=Debug -b missing -pr cpp23 -pr:b cpp23

cpp-init:
	cmake --preset=dev

cpp-build:
	cmake --build --preset=dev -j

cpp-test:
	ctest --preset=dev --timeout 1

cpp-fmt:
	cmake -D FIX=YES -P cmake/lint.cmake
