"""
Test configuration and fixtures for KICKAI tests.
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# Package imports work directly now

# Import service discovery components for fixtures
try:
    from kickai.core.service_discovery import (
        ServiceRegistry,
        ServiceDefinition,
        ServiceType,
        ServiceConfiguration,
        ServiceHealth,
        ServiceStatus,
        reset_service_registry,
    )
except ImportError:
    # Graceful fallback if service discovery is not available
    ServiceRegistry = None
    ServiceDefinition = None
    ServiceType = None
    ServiceConfiguration = None
    ServiceHealth = None
    ServiceStatus = None
    reset_service_registry = lambda: None

# Set up test environment variables
os.environ.update({
    'ENVIRONMENT': 'testing',
    'CI': 'true',
    'GITHUB_ACTIONS': 'true',
    'FIREBASE_CREDENTIALS_JSON': '{"type":"service_account","project_id":"test-project","private_key":"test-key","client_email":"test@test.com"}',
    'GOOGLE_API_KEY': 'test-google-api-key',
    # Bot token should come from Firestore team configuration, not environment variables
    # 'TELEGRAM_BOT_TOKEN': 'test-bot-token',  # Removed - should come from Firestore
    'AI_PROVIDER': 'google_gemini',
    'AI_MODEL_NAME': 'gemini-pro',
    'JWT_SECRET': 'test-jwt-secret',
    'LOG_LEVEL': 'DEBUG'
})

@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables."""
    # Ensure we're in testing mode
    os.environ['ENVIRONMENT'] = 'testing'
    os.environ['CI'] = 'true'
    return {
        'environment': 'testing',
        'ci': True
    }

@pytest.fixture(scope="session")
def mock_firebase_credentials():
    """Mock Firebase credentials for testing."""
    return {
        "type": "service_account",
        "project_id": "test-project",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
        "client_email": "test@test.com",
        "client_id": "test-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/test%40test.com"
    }

@pytest.fixture(scope="session")
def mock_ai_config():
    """Mock AI configuration for testing."""
    return {
        "provider": "google_gemini",
        "api_key": "test-google-api-key",
        "model_name": "gemini-pro",
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout_seconds": 60
    }

@pytest.fixture(scope="session")
def mock_telegram_config():
    """Mock Telegram configuration for testing."""
    return {
        "bot_token": "test-bot-token",
        "webhook_url": None,
        "parse_mode": "",  # Plain text only
        "message_timeout": 30
    }

@pytest.fixture(scope="function")
def mock_config_manager(test_environment, mock_firebase_credentials, mock_ai_config, mock_telegram_config):
    """Mock configuration manager for testing."""
    with patch('kickai.core.config.ImprovedConfigurationManager') as mock_config:
        # Create a mock configuration manager
        config_instance = Mock()
        config_instance.environment.value = 'testing'
        config_instance.is_testing.return_value = True
        config_instance.is_development.return_value = False
        config_instance.is_production.return_value = False
        
        # Mock the configuration properties
        config_instance.database.project_id = mock_firebase_credentials["project_id"]
        config_instance.ai.provider.value = mock_ai_config["provider"]
        config_instance.ai.api_key = mock_ai_config["api_key"]
        config_instance.ai.model_name = mock_ai_config["model_name"]
        config_instance.telegram.bot_token = mock_telegram_config["bot_token"]
        
        # Mock logging configuration with proper string values
        logging_config = Mock()
        logging_config.level = "DEBUG"  # String value, not Mock
        logging_config.format = "json"
        logging_config.output = "console"
        config_instance.logging = logging_config
        
        mock_config.return_value = config_instance
        yield config_instance

@pytest.fixture(scope="function")
def mock_firebase_client():
    """Mock Firebase client for testing."""
    with patch('kickai.database.firebase_client.FirebaseClient') as mock_client:
        client_instance = Mock()
        
        # Mock common Firebase operations
        client_instance.create_team.return_value = "test-team-id"
        client_instance.create_player.return_value = "test-player-id"
        client_instance.create_match.return_value = "test-match-id"
        client_instance.get_team.return_value = {"id": "test-team-id", "name": "Test Team"}
        client_instance.get_player.return_value = {"id": "test-player-id", "name": "Test Player"}
        client_instance.get_match.return_value = {"id": "test-match-id", "team_id": "test-team-id"}
        
        mock_client.return_value = client_instance
        yield client_instance

@pytest.fixture(scope="function")
def mock_telegram_bot():
    """Mock Telegram bot for testing."""
    with patch('telegram.Bot') as mock_bot:
        bot_instance = Mock()
        bot_instance.get_me.return_value = {
            "id": 123456789,
            "first_name": "Test Bot",
            "username": "test_bot"
        }
        bot_instance.send_message.return_value = Mock()
        
        mock_bot.return_value = bot_instance
        yield bot_instance

@pytest.fixture(scope="function")
def mock_llm():
    """Mock LLM for testing."""
    with patch('kickai.agents.handlers.create_llm') as mock_llm_create:
        llm_instance = Mock()
        llm_instance.invoke.return_value = "Mock LLM response"
        llm_instance.ainvoke.return_value = "Mock async LLM response"
        
        mock_llm_create.return_value = llm_instance
        yield llm_instance

@pytest.fixture(scope="function")
def sample_team_data():
    """Sample team data for testing."""
    return {
        "id": "test-team-id",
        "name": "Test Team",
        "description": "A test team for unit testing",
        "status": "active",
        "settings": {
            "max_players": 20,
            "training_days": ["Monday", "Wednesday"],
            "home_ground": "Test Stadium"
        }
    }

@pytest.fixture(scope="function")
def sample_player_data():
    """Sample player data for testing."""
    return {
        "player_id": "test-player-id",
        "name": "John Doe",
        "phone": "+1234567890",
        "email": "john.doe@test.com",
        "team_id": "test-team-id",
        "position": "midfielder",
        "role": "player",
        "fa_registered": True,
        "onboarding_status": "completed"
    }

@pytest.fixture(scope="function")
def sample_match_data():
    """Sample match data for testing."""
    return {
        "id": "test-match-id",
        "team_id": "test-team-id",
        "opponent": "Opponent Team",
        "date": "2024-07-01T14:00:00Z",
        "location": "Test Stadium",
        "status": "scheduled",
        "home_away": "home",
        "competition": "League Match"
    }

@pytest.fixture(scope="function")
def mock_agent_system():
    """Mock agent system for testing."""
    with patch('src.agents.handlers.SimpleAgenticHandler') as mock_handler:
        handler_instance = Mock()
        handler_instance.process_message.return_value = "Mock agent response"
        
        mock_handler.return_value = handler_instance
        yield handler_instance

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Set up logging for tests to avoid configuration issues."""
    # Disable logging during tests to avoid configuration issues
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)
    
    # No need to mock custom logging since we're using standard logging now
    yield

# Test utilities
def create_test_message(text: str = "test message", user_id: str = "123456", chat_id: str = "-987654321") -> Dict[str, Any]:
    """Create a test message object for Telegram testing."""
    return {
        "message_id": 1,
        "date": 1234567890,
        "chat": {
            "id": int(chat_id),
            "type": "group",
            "title": "Test Group"
        },
        "from": {
            "id": int(user_id),
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser"
        },
        "text": text
    }

def create_test_update(message_text: str = "test message", user_id: str = "123456", chat_id: str = "-987654321") -> Dict[str, Any]:
    """Create a test update object for Telegram testing."""
    return {
        "update_id": 123456789,
        "message": create_test_message(message_text, user_id, chat_id)
    }


# Service Discovery Test Fixtures (only if service discovery is available)
if ServiceRegistry is not None:
    
    class TestServiceBase:
        """Base class for test services with common functionality."""
        
        def __init__(self, name: str, should_fail: bool = False, delay: float = 0.0):
            self.name = name
            self.should_fail = should_fail
            self.delay = delay
            self._health_check_calls = 0
            self._operation_calls = 0
        
        async def health_check(self) -> bool:
            """Standard health check method."""
            self._health_check_calls += 1
            
            if self.delay > 0:
                await asyncio.sleep(self.delay)
            
            if self.should_fail:
                raise Exception(f"Health check failed for {self.name}")
            
            return True
        
        def get_health_check_calls(self) -> int:
            return self._health_check_calls
        
        def get_operation_calls(self) -> int:
            return self._operation_calls
        
        def reset_counters(self):
            self._health_check_calls = 0
            self._operation_calls = 0


    class MockPlayerService(TestServiceBase):
        """Mock player service for testing."""
        
        async def get_player(self, player_id: str):
            self._operation_calls += 1
            return {"id": player_id, "name": f"Player {player_id}"}
        
        async def create_player(self, data: dict):
            self._operation_calls += 1
            return {"id": "new_player", **data}
        
        async def update_player(self, player_id: str, data: dict):
            self._operation_calls += 1
            return {"id": player_id, **data}


    class MockDatabaseService(TestServiceBase):
        """Mock database service for testing."""
        
        async def ping(self) -> bool:
            return await self.health_check()
        
        async def test_connection(self) -> bool:
            return await self.health_check()
        
        async def create_document(self, collection: str, data: dict, document_id: str = None):
            self._operation_calls += 1
            return {"id": document_id or "new_doc", **data}
        
        async def get_document(self, collection: str, document_id: str):
            self._operation_calls += 1
            return {"id": document_id, "collection": collection}
        
        async def update_document(self, collection: str, document_id: str, data: dict):
            self._operation_calls += 1
            return {"id": document_id, **data}


    class MockExternalService(TestServiceBase):
        """Mock external service for testing."""
        
        async def test_connection(self) -> bool:
            return await self.health_check()
        
        async def ping(self) -> bool:
            return await self.health_check()
        
        async def send_message(self, message: str):
            self._operation_calls += 1
            return {"message_id": f"msg_{self._operation_calls}", "status": "sent"}


    class MockAgentService(TestServiceBase):
        """Mock agent service for testing."""
        
        def create_agent(self, agent_type: str):
            self._operation_calls += 1
            return Mock(name=f"Agent_{agent_type}_{self._operation_calls}")
        
        async def route_message(self, message: str):
            self._operation_calls += 1
            return {"routed_to": "test_agent", "message": message}


    @pytest.fixture
    def service_discovery_registry():
        """Fixture providing a fresh service registry."""
        if ServiceConfiguration is None:
            pytest.skip("Service discovery not available")
        
        config = ServiceConfiguration(
            health_check_enabled=True,
            circuit_breaker_enabled=True,
            circuit_breaker_threshold=3
        )
        return ServiceRegistry(config)


    @pytest.fixture
    def mock_player_service():
        """Fixture providing a mock player service."""
        return MockPlayerService("PlayerService")


    @pytest.fixture
    def mock_database_service():
        """Fixture providing a mock database service."""
        return MockDatabaseService("DataStoreInterface")


    @pytest.fixture
    def mock_external_service():
        """Fixture providing a mock external service."""
        return MockExternalService("TelegramBot")


    @pytest.fixture
    def mock_agent_service():
        """Fixture providing a mock agent service."""
        return MockAgentService("AgentFactory")


    @pytest.fixture
    def sample_service_definitions():
        """Fixture providing sample service definitions."""
        if ServiceDefinition is None or ServiceType is None:
            pytest.skip("Service discovery not available")
        
        return [
            ServiceDefinition(
                name="DataStoreInterface",
                service_type=ServiceType.CORE,
                interface_name="test.IDataStore",
                implementation_class="test.DataStore",
                dependencies=[],
                timeout=10.0,
                metadata={"priority": "critical"}
            ),
            ServiceDefinition(
                name="PlayerService",
                service_type=ServiceType.FEATURE,
                interface_name="test.IPlayerService",
                implementation_class="test.PlayerService",
                dependencies=["DataStoreInterface"],
                timeout=15.0,
                metadata={"feature": "player_management"}
            ),
            ServiceDefinition(
                name="TelegramBot",
                service_type=ServiceType.EXTERNAL,
                interface_name="test.ITelegramBot",
                implementation_class="test.TelegramBot",
                dependencies=[],
                timeout=20.0,
                metadata={"external_provider": "telegram"}
            ),
            ServiceDefinition(
                name="AgentFactory",
                service_type=ServiceType.CORE,
                interface_name="test.IAgentFactory",
                implementation_class="test.AgentFactory",
                dependencies=["DataStoreInterface"],
                timeout=12.0,
                metadata={"agent_system": True}
            )
        ]


    @pytest.fixture(autouse=True)
    def reset_global_service_registry():
        """Auto-reset global service registry between tests."""
        if reset_service_registry is not None:
            reset_service_registry()
        yield
        if reset_service_registry is not None:
            reset_service_registry()


    @pytest.fixture
    def mock_health_checker():
        """Fixture providing a mock health checker."""
        if ServiceHealth is None or ServiceStatus is None:
            pytest.skip("Service discovery not available")
        
        class MockHealthChecker:
            def __init__(self, supported_services: List[str] = None):
                self.supported_services = supported_services or []
                self.check_called = False
                self.last_service_name = None
                self.last_service_instance = None
            
            async def check_health(self, service_name: str, service_instance: Any) -> ServiceHealth:
                self.check_called = True
                self.last_service_name = service_name
                self.last_service_instance = service_instance
                
                # Simulate health check based on service instance
                if hasattr(service_instance, 'should_fail') and service_instance.should_fail:
                    return ServiceHealth(
                        service_name=service_name,
                        status=ServiceStatus.UNHEALTHY,
                        error_message="Mock service configured to fail"
                    )
                
                return ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.HEALTHY,
                    response_time=0.1,
                    metadata={"mock_checker": True}
                )
            
            def supports_service(self, service_name: str) -> bool:
                if not self.supported_services:
                    return True
                return service_name in self.supported_services
        
        return MockHealthChecker()


# Pytest configuration for service discovery tests
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "service_discovery: mark test as service discovery related"
    )