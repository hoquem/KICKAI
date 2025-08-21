# SDLC - Testing Strategy, CI/CD, and Deployment

## Essential Commands

```bash
# Development (Python 3.11+ Required)
make dev                           # Start development server  
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py  # Mock UI (localhost:8001)
./start_bot_safe.sh               # Safe startup (kills existing processes)

# Testing & Validation
make test                          # All tests (unit + integration + e2e)
make test-unit                     # Unit tests only
make lint                          # Code quality (ruff + mypy)
PYTHONPATH=. python scripts/run_health_checks.py  # System health validation

# Specific Testing
PYTHONPATH=. python -m pytest tests/unit/test_file.py::test_function -v -s
PYTHONPATH=. python -m pytest tests/integration/ -v --tb=short
PYTHONPATH=. python run_comprehensive_e2e_tests.py

# Emergency/Debug
PYTHONPATH=. KICKAI_INVITE_SECRET_KEY=test-key python -c "..."  # System validation
```

## Testing Strategy

### Test Types & Commands
```bash
# Unit Tests - Component isolation
PYTHONPATH=. python -m pytest tests/unit/ -v

# Integration Tests - Service interactions  
PYTHONPATH=. python -m pytest tests/integration/ -v

# E2E Tests - Complete user workflows
PYTHONPATH=. python run_comprehensive_e2e_tests.py

# Mock Telegram UI - Interactive testing
PYTHONPATH=. python tests/mock_telegram/start_mock_tester.py
# Access at: http://localhost:8001 (Liverpool FC themed)
```

### Test Pattern
```python
from unittest.mock import AsyncMock, patch

async def test_tool_with_mock():
    with patch('kickai.core.dependency_container.get_container') as mock_container:
        mock_service = AsyncMock()
        mock_container.return_value.get_service.return_value = mock_service
        
        result = await tool_name(123456789, "KTI", "testuser", "main")
        
        mock_service.method_name.assert_called_once()
        assert "success" in result
```

## System Health Validation

```bash
# Complete system health check
PYTHONPATH=. python scripts/run_health_checks.py

# Quick validation commands
PYTHONPATH=. KICKAI_INVITE_SECRET_KEY=test-key python -c "
from kickai.core.dependency_container import ensure_container_initialized
from kickai.agents.tool_registry import initialize_tool_registry
ensure_container_initialized()
registry = initialize_tool_registry()
print(f'✅ {len(registry.get_all_tools())} tools registered')
"

# Agent system validation
PYTHONPATH=. KICKAI_INVITE_SECRET_KEY=test-key python -c "
from kickai.agents.crew_agents import TeamManagementSystem
system = TeamManagementSystem('KTI') 
print(f'✅ {len(system.agents)} agents initialized')
"
```

## MCP Server Integration

```bash
# Documentation access (always up-to-date)
claude mcp add --transport http context7 https://mcp.context7.com/mcp

# UI testing and automation
claude mcp add puppeteer -s user -- npx -y @modelcontextprotocol/server-puppeteer
```

**Usage:** Add `use context7` to prompts needing current documentation (CrewAI, Firebase, Python libraries).

## CI/CD Pipeline
- **Railway Deployment**: Automated deployment with health checks
- **Multi-Environment**: Testing, staging, and production environments
- **Monitoring**: System health via agents and comprehensive logging
- **Scaling**: Agent-based architecture supports horizontal scaling

## Deployment Environments
1. **Local Development**: `make dev` with mock services
2. **Testing**: Mock Telegram UI integration
3. **Staging**: Pre-production validation
4. **Production**: Railway deployment with monitoring