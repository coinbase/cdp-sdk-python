.PHONY: format
format:
	poetry run ruff format .

.PHONY: lint
lint:
	poetry run ruff check .

.PHONY: lint-fix
lint-fix:
	poetry run ruff check . --fix

.PHONY: test
test:
	poetry run pytest

.PHONY: e2e
e2e:
	poetry run pytest -m "tests and e2e"

.PHONY: repl
repl:
	poetry run python

.PHONY: install-deps
install-deps:
	poetry install

.PHONY: docs
docs:
	poetry run sphinx-apidoc -f -o docs/ ./cdp/

.PHONY: local-docs
local-docs: docs
	cd docs && make html && open ./_build/html/index.html
