.PHONY: install test ci lint format unit integration

install:
	poetry lock --no-update
	poetry install
	poetry env use python3.12

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

