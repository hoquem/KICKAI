# SDLC - Testing, CI/CD & Deployment

## Testing Strategy
**Test Pyramid:** Unit → Integration → E2E

### Test Commands
```bash
# All tests  
make test

# Specific test types
make test-unit              # Fast, isolated component tests
make test-integration       # Service interaction tests  
make test-e2e              # Complete workflow tests

# Single test execution
PYTHONPATH=. python -m pytest tests/unit/features/[feature]/test_[component].py::test_[function] -v -s
PYTHONPATH=. python -m pytest tests/integration/features/team_administration/ -v
PYTHONPATH=. python -m pytest tests/e2e/features/test_cross_feature_flows.py -k "player_registration" -v
```

### Test Types
- **Unit Tests:** Mock all external dependencies, test business logic in isolation
- **Integration Tests:** Test service interactions with real or test databases
- **E2E Tests:** Complete user workflows through Mock Telegram UI

## Code Quality
```bash
make lint                   # All quality checks
ruff check kickai/          # Linting only  
ruff format kickai/         # Formatting only
mypy kickai/               # Type checking
```

## Health Validation
```bash
# System health checks (run frequently)
PYTHONPATH=. python scripts/run_health_checks.py
make health-check

# Quick validation
PYTHONPATH=. python -c "
from kickai.core.dependency_container import ensure_container_initialized
ensure_container_initialized(); print('✅ System OK')
"
```

## Deployment
```bash
# Railway deployment
make deploy-testing         # Deploy to test environment
make deploy-production      # Deploy to production  
make validate-testing       # Validate test deployment
make validate-production    # Validate prod deployment

# Emergency rollback
make rollback-testing
make rollback-production
```

## Environment Management
**Development:** Python 3.11+, venv311, local Firebase
**Testing:** Railway test environment, test Firebase project
**Production:** Railway production, production Firebase

## CI/CD Pipeline
1. **Code Quality:** Lint, format, type check
2. **Testing:** Unit → Integration → E2E  
3. **Health Checks:** System validation
4. **Deployment:** Automated Railway deployment
5. **Validation:** Post-deployment health checks