# Linting Setup

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

## Installation

Install ruff using uv:

```bash
uv pip install ruff
```

Or install dev dependencies:

```bash
uv pip install -e ".[dev]"
```

## Usage

### Lint (check for issues)
```bash
ruff check api/
```

### Format code
```bash
ruff format api/
```

### Auto-fix issues
```bash
ruff check --fix api/
```

### Using Makefile

```bash
make lint    # Run linter
make format  # Format code
make check   # Run both lint and format check
make fix     # Auto-fix linting issues
```

## Configuration

Linting rules are configured in `pyproject.toml` under `[tool.ruff]`.

## IDE Integration

### VS Code
Install the "Ruff" extension for automatic linting and formatting.

### PyCharm
Ruff is supported natively in PyCharm 2023.3+.

