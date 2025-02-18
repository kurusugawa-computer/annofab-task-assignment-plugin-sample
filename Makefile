.PHONY: docs lint test format

format:
	poetry run ruff format app
	poetry run ruff check app --fix-only --exit-zero

lint:
	poetry run ruff format app --check
	poetry run ruff check app
	poetry run mypy app

