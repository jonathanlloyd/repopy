all: lint typecheck test

.PHONY: lint
lint:
	@poetry run pylint repopy

.PHONY: typecheck
typecheck:
	@poetry run mypy .

.PHONY: test
test:
	@poetry run pytest
