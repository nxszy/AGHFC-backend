.PHONY: format black isort lint fix type-check test all

black:
	poetry run black .

isort:
	poetry run isort app

format:
	make black isort

lint:
	poetry run ruff check app

fix:
	poetry run ruff check app --fix

type-check:
	poetry run mypy app

test:
	PYTHONPATH=. poetry run pytest --cov=app --cov-report=term-missing

all: format lint type-check test