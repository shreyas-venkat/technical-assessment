.PHONY: lint format check test help

help:
	@echo "Available commands:"
	@echo "  make lint    - Run linter (ruff check)"
	@echo "  make format  - Format code (ruff format)"
	@echo "  make check   - Run both lint and format check"
	@echo "  make fix     - Auto-fix linting issues"

lint:
	ruff check api/

format:
	ruff format api/

check: lint format
	@echo "✓ All checks passed!"

fix:
	ruff check --fix api/
	ruff format api/

