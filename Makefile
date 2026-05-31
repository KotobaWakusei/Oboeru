.PHONY: format lint type-check test test-cov clean install-dev pre-commit-install

format:
	black .

lint:
	ruff check .

type-check:
	mypy --ignore-missing-imports modules ui

type-check-strict:
	mypy --ignore-missing-imports --strict modules ui

test:
	pytest -v tests/

test-cov:
	pytest --cov=modules --cov=ui --cov-report=html --cov-report=term-missing tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

install-dev:
	pip install -r dev-requirements.txt
	pip install -r requirements.txt

pre-commit-install:
	pre-commit install
	pre-commit run --all-files

check: format lint type-check test

help:
	@echo "Available targets:"
	@echo "  format              - Format code with black"
	@echo "  lint                - Lint code with ruff"
	@echo "  type-check          - Type check with mypy"
	@echo "  type-check-strict   - Strict type checking"
	@echo "  test                - Run tests with pytest"
	@echo "  test-cov            - Run tests with coverage report"
	@echo "  clean               - Clean build artifacts"
	@echo "  install-dev         - Install dev and runtime dependencies"
	@echo "  pre-commit-install  - Set up pre-commit hooks"
	@echo "  check               - Run all checks (format, lint, type-check, test)"

