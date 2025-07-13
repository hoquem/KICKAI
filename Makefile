# KICKAI Makefile
# Provides easy commands for development tasks

.PHONY: help install lint format test clean

# Default target
help:
	@echo "KICKAI Development Commands"
	@echo "=========================="
	@echo ""
	@echo "Setup:"
	@echo "  install     Install dependencies"
	@echo "  setup       Setup pre-commit hooks"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        Run all linters"
	@echo "  format      Format code with Black and isort"
	@echo "  check-imports Run custom import linter"
	@echo ""
	@echo "Testing:"
	@echo "  test        Run all tests"
	@echo "  test-unit   Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-e2e    Run end-to-end tests only"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean       Clean up cache and temporary files"
	@echo ""

# Setup commands
install:
	@echo "Installing dependencies..."
	pip install -e .
	pip install -e ".[dev]"

setup:
	@echo "Setting up pre-commit hooks..."
	pre-commit install

# Code quality commands
lint:
	@echo "Running comprehensive linting..."
	./scripts/lint.sh

format:
	@echo "Formatting code..."
	black src tests scripts
	isort src tests scripts

check-imports:
	@echo "Checking import architecture..."
	python scripts/check_imports.py

# Testing commands
test:
	@echo "Running all tests..."
	PYTHONPATH=src pytest tests/ -v

test-unit:
	@echo "Running unit tests..."
	PYTHONPATH=src pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	PYTHONPATH=src pytest tests/integration/ -v

test-e2e:
	@echo "Running end-to-end tests..."
	PYTHONPATH=src pytest tests/e2e/ -v

# Cleanup commands
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	@echo "Cleanup complete!"

# Development workflow
dev-setup: install setup
	@echo "Development environment setup complete!"

quick-check: check-imports format
	@echo "Quick code quality check complete!"

full-check: lint test
	@echo "Full code quality check complete!" 