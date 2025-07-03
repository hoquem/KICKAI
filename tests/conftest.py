"""
Test configuration and fixtures for KICKAI tests.
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up test environment variables
os.environ.update({
    'ENVIRONMENT': 'testing',
    'CI': 'true',
    'GITHUB_ACTIONS': 'true',
    'FIREBASE_CREDENTIALS_JSON': '{"type":"service_account","project_id":"test-project","private_key":"test-key","client_email":"test@test.com"}',
    'GOOGLE_API_KEY': 'test-google-api-key',
    'TELEGRAM_BOT_TOKEN': 'test-bot-token',
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
        "parse_mode": "MarkdownV2",
        "message_timeout": 30
    }

@pytest.fixture(scope="function")
def mock_config_manager(test_environment, mock_firebase_credentials, mock_ai_config, mock_telegram_config):
    """Mock configuration manager for testing."""
    with patch('src.core.config.ConfigurationManager') as mock_config:
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
        
        mock_config.return_value = config_instance
        yield config_instance

@pytest.fixture(scope="function")
def mock_firebase_client():
    """Mock Firebase client for testing."""
    with patch('src.database.firebase_client.FirebaseClient') as mock_client:
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
    with patch('src.agents.handlers.create_llm') as mock_llm_create:
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