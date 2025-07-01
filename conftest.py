"""
Pytest configuration and fixtures for KICKAI tests.

This module provides global test configuration, fixtures, and mocks
to ensure consistent test behavior across the entire test suite.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Mock Firebase before any imports
@pytest.fixture(scope="session", autouse=True)
def mock_firebase_session():
    """Mock Firebase client at session level before any imports."""
    with patch('firebase_admin.initialize_app') as mock_init:
        with patch('firebase_admin.firestore.client') as mock_client:
            mock_db = Mock()
            mock_client.return_value = mock_db
            yield mock_db


@pytest.fixture(autouse=True)
def mock_get_firebase_client():
    """Mock the get_firebase_client function to prevent Firebase initialization."""
    with patch('src.database.firebase_client.get_firebase_client') as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock the client instance
        mock_client._initialize_client = Mock()
        mock_client._client = Mock()
        mock_client.config = Mock()
        mock_client.config.project_id = "test_project"
        
        # Mock database operations
        mock_client.get_team.return_value = {
            'id': 'test-team-1',
            'name': 'Test Team',
            'status': 'ACTIVE',
            'bot_token': 'test_bot_token',
            'admin_chat_id': 'test_admin_chat_id'
        }
        
        mock_client.get_player.return_value = {
            'id': 'test-player-1',
            'name': 'John Smith',
            'phone': '07123456789',
            'team_id': 'test-team-1',
            'position': 'FORWARD',
            'role': 'PLAYER',
            'onboarding_status': 'COMPLETED'
        }
        
        mock_client.create_player.return_value = 'test-player-1'
        mock_client.update_player.return_value = True
        mock_client.delete_player.return_value = True
        
        mock_client.create_team.return_value = 'test-team-1'
        mock_client.update_team.return_value = True
        mock_client.delete_team.return_value = True
        
        yield mock_client


@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Mock environment variables for testing."""
    env_vars = {
        'GOOGLE_API_KEY': 'test_google_api_key',
        'OPENAI_API_KEY': 'test_openai_api_key',
        'TELEGRAM_BOT_TOKEN': 'test_telegram_bot_token',
        'FIREBASE_PROJECT_ID': 'test_project_id',
        'FIREBASE_PRIVATE_KEY_ID': 'test_private_key_id',
        'FIREBASE_PRIVATE_KEY': 'test_private_key',
        'FIREBASE_CLIENT_EMAIL': 'test_client_email',
        'FIREBASE_CLIENT_ID': 'test_client_id',
        'FIREBASE_AUTH_URI': 'https://accounts.google.com/o/oauth2/auth',
        'FIREBASE_TOKEN_URI': 'https://oauth2.googleapis.com/token',
        'FIREBASE_AUTH_PROVIDER_X509_CERT_URL': 'https://www.googleapis.com/oauth2/v1/certs',
        'FIREBASE_CLIENT_X509_CERT_URL': 'test_cert_url',
        'ENVIRONMENT': 'test'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture(autouse=True)
def mock_config():
    """Mock configuration loading."""
    with patch('src.core.config.ConfigurationManager') as mock_config_class:
        mock_config_instance = Mock()
        mock_config_class.return_value = mock_config_instance
        
        # Mock config properties
        mock_config_instance.google_api_key = 'test_google_api_key'
        mock_config_instance.openai_api_key = 'test_openai_api_key'
        mock_config_instance.telegram_bot_token = 'test_telegram_bot_token'
        mock_config_instance.environment = 'test'
        mock_config_instance.is_production = False
        mock_config_instance.is_development = True
        
        yield mock_config_instance


# Test session configuration
def pytest_configure(config):
    """Configure pytest session."""
    # Add custom markers
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "security: mark test as security test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add default markers based on test file location
        if 'integration' in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif 'unit' in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif 'performance' in item.nodeid:
            item.add_marker(pytest.mark.performance)
        elif 'security' in item.nodeid:
            item.add_marker(pytest.mark.security) 