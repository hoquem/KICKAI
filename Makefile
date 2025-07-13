# KICKAI Makefile
# Provides convenient commands for development, testing, and deployment

.PHONY: help setup-dev test test-unit test-integration test-e2e lint clean deploy-testing deploy-production

# Default target
help:
	@echo "KICKAI Development Commands"
	@echo "=========================="
	@echo ""
	@echo "Development:"
	@echo "  setup-dev     - Set up development environment"
	@echo "  dev           - Start development server"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e      - Run E2E tests only"
	@echo "  lint          - Run code quality checks"
	@echo "  clean         - Clean up temporary files"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy-testing    - Deploy to testing environment"
	@echo "  deploy-production - Deploy to production environment"
	@echo "  validate-testing  - Validate testing environment"
	@echo "  validate-production - Validate production environment"
	@echo ""
	@echo "Environment:"
	@echo "  env-dev       - Load development environment"
	@echo "  env-testing   - Load testing environment"
	@echo "  env-production - Load production environment"

# Development setup
setup-dev:
	@echo "Setting up development environment..."
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pip install -r requirements-local.txt
	pre-commit install
	@echo "Development environment setup complete!"

# Development server
dev:
	@echo "Starting development server..."
	export PYTHONPATH=src && python run_telegram_bot.py

# Testing commands
test: test-unit test-integration test-e2e

test-unit:
	@echo "Running unit tests..."
	export PYTHONPATH=src && python -m pytest tests/unit/ -v

test-integration:
	@echo "Running integration tests..."
	export PYTHONPATH=src && python -m pytest tests/integration/ -v

test-e2e:
	@echo "Running E2E tests..."
	export PYTHONPATH=src && python run_e2e_tests.py --suite=smoke

# Code quality
lint:
	@echo "Running code quality checks..."
	python -m flake8 src/
	python -m black --check src/
	python -m isort --check-only src/
	python -m mypy src/

# Clean up
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.log" -delete
	find . -type f -name "e2e_report_*.txt" -delete
	find . -type f -name "e2e_report_*.html" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "Cleanup complete!"

# Environment loading
env-dev:
	@echo "Loading development environment..."
	export $(cat .env.development | xargs)

env-testing:
	@echo "Loading testing environment..."
	export $(cat .env.testing | xargs)

env-production:
	@echo "Loading production environment..."
	export $(cat .env.production | xargs)

# Deployment commands
deploy-testing:
	@echo "Deploying to testing environment..."
	railway up --service kickai-testing

deploy-production:
	@echo "Deploying to production environment..."
	railway up --service kickai-production

# Validation commands
validate-testing:
	@echo "Validating testing environment..."
	export PYTHONPATH=src && python scripts/validate_feature_deployment.py --feature=all --environment=testing

validate-production:
	@echo "Validating production environment..."
	export PYTHONPATH=src && python scripts/validate_feature_deployment.py --feature=all --environment=production

# Health checks
health-check:
	@echo "Running health checks..."
	export PYTHONPATH=src && python scripts/run_health_checks.py

# Bootstrap commands
bootstrap-testing:
	@echo "Bootstrapping testing environment..."
	export PYTHONPATH=src && python scripts/bootstrap_team.py --environment=testing

bootstrap-production:
	@echo "Bootstrapping production environment..."
	export PYTHONPATH=src && python scripts/bootstrap_team.py --environment=production

# Database cleanup
cleanup-testing:
	@echo "Cleaning up testing database..."
	export PYTHONPATH=src && python scripts-oneoff/cleanup/clean_firestore_collections.py --environment=testing

cleanup-production:
	@echo "Cleaning up production database..."
	export PYTHONPATH=src && python scripts-oneoff/cleanup/clean_firestore_collections.py --environment=production

# Full deployment pipeline
deploy-pipeline: test lint deploy-testing validate-testing deploy-production validate-production
	@echo "Full deployment pipeline completed!"

# Quick development workflow
dev-workflow: clean test lint
	@echo "Development workflow completed!"

# Emergency rollback
rollback-testing:
	@echo "Rolling back testing environment..."
	railway rollback --service kickai-testing

rollback-production:
	@echo "Rolling back production environment..."
	railway rollback --service kickai-production 