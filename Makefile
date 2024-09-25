.PHONY: format
format:
	ruff format .

.PHONY: lint
lint:
	ruff check .

.PHONY: lint-fix
lint-fix:
	ruff check . --fix

.PHONY: test
test:
	pytest

.PHONY: e2e
e2e:
	python -m tests.e2e

.PHONY: repl
repl:
	python

.PHONY: install-deps
install-deps:
	pip install .[dev]

.PHONY: docs
docs:
	sphinx-apidoc -f -o docs/ ./cdp/
