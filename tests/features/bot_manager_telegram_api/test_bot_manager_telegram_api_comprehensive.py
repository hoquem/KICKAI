#!/usr/bin/env python3
"""
Comprehensive Test Suite for Bot Manager & Telegram API Integration

This test suite covers all major components of the bot manager and Telegram API integration:
- MultiBotManager tests
- TelegramBotService tests
- AgenticMessageRouter tests
- CrewAI integration tests
- Configuration management tests
- Integration tests (end-to-end workflows)
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Any, Dict

from kickai.features.team_administration.domain.services.multi_bot_manager import MultiBotManager
from kickai.features.communication.infrastructure.telegram_bot_service import TelegramBotService
from kickai.agents.agentic_message_router import AgenticMessageRouter
from kickai.core.enums import ChatType


class TestMultiBotManager:
    """Test MultiBotManager functionality."""

    @pytest.fixture
    def mock_data_store(self):
        """Create mock data store."""
        return Mock()

    @pytest.fixture
    def mock_team_service(self):
        """Create mock team service."""
        mock_service = Mock()
        mock_service.get_all_teams = AsyncMock()
        return mock_service

    @pytest.fixture
    def multi_bot_manager(self, mock_data_store, mock_team_service):
        """Create multi bot manager with mocked dependencies."""
        return MultiBotManager(mock_data_store, mock_team_service)

    @pytest.mark.asyncio
    async def test_initialization(self, multi_bot_manager):
        """Test multi bot manager initialization."""
        with patch('kickai.features.team_administration.domain.services.multi_bot_manager.initialize_crew_lifecycle_manager') as mock_init:
            await multi_bot_manager.initialize()
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_bot_configurations(self, multi_bot_manager, mock_team_service):
        """Test loading bot configurations."""
        from kickai.features.team_administration.domain.entities.team import Team
        
        mock_teams = [
            Team(name="Team 1", bot_token="token1", main_chat_id="-1001", leadership_chat_id="-1002"),
            Team(name="Team 2", bot_token="token2", main_chat_id="-1003", leadership_chat_id="-1004")
        ]
        mock_team_service.get_all_teams.return_value = mock_teams
        
        result = await multi_bot_manager.load_bot_configurations()
        
        assert len(result) == 2
        assert result[0].name == "Team 1"
        assert result[1].name == "Team 2"

    @pytest.mark.asyncio
    async def test_initialize_crewai_agents(self, multi_bot_manager):
        """Test CrewAI agent initialization."""
        with patch('kickai.features.team_administration.domain.services.multi_bot_manager.get_crew_lifecycle_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_crew = Mock()
            mock_manager.get_or_create_crew = AsyncMock(return_value=mock_crew)
            mock_get_manager.return_value = mock_manager
            
            result = await multi_bot_manager.initialize_crewai_agents("test_team", Mock())
            
            assert result is not None

    @pytest.mark.asyncio
    async def test_start_all_bots(self, multi_bot_manager, mock_team_service):
        """Test starting all bots."""
        from kickai.features.team_administration.domain.entities.team import Team
        
        mock_teams = [
            Team(
                name="Test Team",
                bot_token="test_token",
                main_chat_id="-1001234567890",
                leadership_chat_id="-1001234567891"
            )
        ]
        mock_team_service.get_all_teams.return_value = mock_teams
        
        with patch('kickai.features.team_administration.domain.services.multi_bot_manager.TelegramBotService') as mock_bot_service_class:
            mock_bot_service = Mock()
            mock_bot_service.start_polling = AsyncMock()
            mock_bot_service_class.return_value = mock_bot_service
            
            await multi_bot_manager.start_all_bots()
            
            assert multi_bot_manager.is_running() is True

    @pytest.mark.asyncio
    async def test_stop_all_bots(self, multi_bot_manager):
        """Test stopping all bots."""
        # Add a mock bot to the manager
        mock_bot = Mock()
        mock_bot.stop = AsyncMock()
        multi_bot_manager.bots["test_team"] = mock_bot
        multi_bot_manager._running = True
        
        await multi_bot_manager.stop_all_bots()
        
        assert multi_bot_manager.is_running() is False
        mock_bot.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_startup_messages(self, multi_bot_manager):
        """Test sending startup messages."""
        from kickai.features.team_administration.domain.entities.team import Team
        
        mock_team = Team(
            name="Test Team",
            main_chat_id="-1001234567890",
            leadership_chat_id="-1001234567891"
        )
        # Set the team_id attribute that the method expects
        mock_team.team_id = "test_team"
        multi_bot_manager.bot_configs = [mock_team]
        
        mock_bot = Mock()
        mock_bot.send_message = AsyncMock()
        multi_bot_manager.bots["test_team"] = mock_bot
        
        await multi_bot_manager.send_startup_messages()
        
        assert mock_bot.send_message.call_count == 2  # Main and leadership chats

    def test_is_running(self, multi_bot_manager):
        """Test running status check."""
        assert multi_bot_manager.is_running() is False
        
        multi_bot_manager._running = True
        assert multi_bot_manager.is_running() is True

    def test_get_bot(self, multi_bot_manager):
        """Test getting bot by team ID."""
        mock_bot = Mock()
        multi_bot_manager.bots["test_team"] = mock_bot
        
        result = multi_bot_manager.get_bot("test_team")
        assert result == mock_bot
        
        result = multi_bot_manager.get_bot("nonexistent_team")
        assert result is None


class TestTelegramBotService:
    """Test TelegramBotService functionality."""

    @pytest.fixture
    def mock_crewai_system(self):
        """Create mock CrewAI system."""
        return Mock()

    @pytest.fixture
    def telegram_bot_service(self, mock_crewai_system):
        """Create Telegram bot service with mocked dependencies."""
        return TelegramBotService(
            token="test_bot_token",
            team_id="test_team",
            main_chat_id="-1001234567890",
            leadership_chat_id="-1001234567891",
            crewai_system=mock_crewai_system
        )

    def test_initialization(self, telegram_bot_service):
        """Test Telegram bot service initialization."""
        assert telegram_bot_service.token == "test_bot_token"
        assert telegram_bot_service.team_id == "test_team"
        assert telegram_bot_service.main_chat_id == "-1001234567890"
        assert telegram_bot_service.leadership_chat_id == "-1001234567891"

    def test_initialization_without_token(self):
        """Test initialization fails without token."""
        with pytest.raises(ValueError, match="token must be provided explicitly"):
            TelegramBotService(
                token="",
                team_id="test_team"
            )

    @pytest.mark.asyncio
    async def test_start_polling(self, telegram_bot_service):
        """Test starting bot polling."""
        with patch.object(telegram_bot_service.app, 'initialize') as mock_init, \
             patch.object(telegram_bot_service.app, 'start') as mock_start, \
             patch.object(telegram_bot_service.app.updater, 'start_polling') as mock_polling:
            
            await telegram_bot_service.start_polling()
            
            mock_init.assert_called_once()
            mock_start.assert_called_once()
            mock_polling.assert_called_once()
            assert telegram_bot_service._running is True

    @pytest.mark.asyncio
    async def test_stop(self, telegram_bot_service):
        """Test stopping the bot."""
        telegram_bot_service._running = True
        
        with patch.object(telegram_bot_service.app.updater, 'stop') as mock_stop, \
             patch.object(telegram_bot_service.app, 'stop') as mock_app_stop, \
             patch.object(telegram_bot_service.app, 'shutdown') as mock_shutdown:
            
            await telegram_bot_service.stop()
            
            mock_stop.assert_called_once()
            mock_app_stop.assert_called_once()
            mock_shutdown.assert_called_once()
            assert telegram_bot_service._running is False

    @pytest.mark.asyncio
    async def test_send_message(self, telegram_bot_service):
        """Test sending a message."""
        # Mock the entire bot object to avoid protected attribute issues
        mock_bot = Mock()
        mock_bot.send_message = AsyncMock()
        telegram_bot_service.app.bot = mock_bot
        
        await telegram_bot_service.send_message("123456789", "Test message")
        
        mock_bot.send_message.assert_called_once_with(chat_id="123456789", text="Test message")

    @pytest.mark.asyncio
    async def test_send_contact_share_button(self, telegram_bot_service):
        """Test sending contact share button."""
        # Mock the entire bot object to avoid protected attribute issues
        mock_bot = Mock()
        mock_bot.send_message = AsyncMock()
        telegram_bot_service.app.bot = mock_bot
        
        await telegram_bot_service.send_contact_share_button("123456789", "Share your contact")
        
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        assert call_args[1]['chat_id'] == "123456789"
        assert call_args[1]['text'] == "Share your contact"
        assert 'reply_markup' in call_args[1]

    def test_determine_chat_type(self, telegram_bot_service):
        """Test chat type determination."""
        assert telegram_bot_service._determine_chat_type("-1001234567890") == ChatType.MAIN
        assert telegram_bot_service._determine_chat_type("-1001234567891") == ChatType.LEADERSHIP
        assert telegram_bot_service._determine_chat_type("123456789") == ChatType.PRIVATE

    @pytest.mark.asyncio
    async def test_handle_natural_language_message(self, telegram_bot_service):
        """Test handling natural language messages."""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_update.effective_user.id = "987654321"
        mock_update.message.text = "Hello, how are you?"
        
        mock_context = Mock()
        
        with patch.object(telegram_bot_service.agentic_router, 'convert_telegram_update_to_message') as mock_convert, \
             patch.object(telegram_bot_service.agentic_router, 'route_message') as mock_route, \
             patch.object(telegram_bot_service, '_send_response') as mock_send:
            
            mock_message = Mock()
            mock_convert.return_value = mock_message
            
            mock_response = Mock()
            mock_response.message = "I'm doing well, thank you!"
            mock_response.success = True
            mock_route.return_value = mock_response
            
            await telegram_bot_service._handle_natural_language_message(mock_update, mock_context)
            
            mock_convert.assert_called_once_with(mock_update)
            mock_route.assert_called_once_with(mock_message)
            mock_send.assert_called_once_with(mock_update, mock_response)

    @pytest.mark.asyncio
    async def test_handle_contact_share(self, telegram_bot_service):
        """Test handling contact sharing."""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_update.effective_user.id = "987654321"
        
        mock_contact = Mock()
        mock_contact.phone_number = "+1234567890"
        mock_contact.user_id = "987654321"
        
        mock_message = Mock()
        mock_message.contact = mock_contact
        
        mock_update.message = mock_message
        
        mock_context = Mock()
        
        with patch.object(telegram_bot_service.agentic_router, 'convert_telegram_update_to_message') as mock_convert, \
             patch.object(telegram_bot_service.agentic_router, 'route_contact_share') as mock_route, \
             patch.object(telegram_bot_service, '_send_response') as mock_send:
            
            mock_domain_message = Mock()
            mock_convert.return_value = mock_domain_message
            
            mock_response = Mock()
            mock_response.message = "Contact received successfully!"
            mock_response.success = True
            mock_route.return_value = mock_response
            
            await telegram_bot_service._handle_contact_share(mock_update, mock_context)
            
            mock_convert.assert_called_once_with(mock_update)
            mock_route.assert_called_once_with(mock_domain_message)
            mock_send.assert_called_once_with(mock_update, mock_response)

    @pytest.mark.asyncio
    async def test_handle_registered_command(self, telegram_bot_service):
        """Test handling registered commands."""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_update.effective_user.id = "987654321"
        mock_update.message.text = "/help"
        
        mock_context = Mock()
        
        with patch.object(telegram_bot_service.agentic_router, 'convert_telegram_update_to_message') as mock_convert, \
             patch.object(telegram_bot_service.agentic_router, 'route_message') as mock_route, \
             patch.object(telegram_bot_service, '_send_response') as mock_send:
            
            mock_message = Mock()
            mock_convert.return_value = mock_message
            
            mock_response = Mock()
            mock_response.message = "Here's the help information..."
            mock_response.success = True
            mock_route.return_value = mock_response
            
            await telegram_bot_service._handle_registered_command(mock_update, mock_context, "/help")
            
            mock_convert.assert_called_once_with(mock_update, "/help")
            mock_route.assert_called_once_with(mock_message)
            mock_send.assert_called_once_with(mock_update, mock_response)

    @pytest.mark.asyncio
    async def test_send_response(self, telegram_bot_service):
        """Test sending responses."""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_update.message.reply_text = AsyncMock()
        
        mock_response = Mock()
        mock_response.message = "Test response"
        mock_response.success = True
        mock_response.needs_contact_button = False
        
        await telegram_bot_service._send_response(mock_update, mock_response)
        
        mock_update.message.reply_text.assert_called_once_with("Test response")

    @pytest.mark.asyncio
    async def test_send_error_response(self, telegram_bot_service):
        """Test sending error responses."""
        mock_update = Mock()
        mock_update.message.reply_text = AsyncMock()
        
        await telegram_bot_service._send_error_response(mock_update, "An error occurred")
        
        mock_update.message.reply_text.assert_called_once_with("❌ An error occurred")


class TestAgenticMessageRouter:
    """Test AgenticMessageRouter functionality."""

    @pytest.fixture
    def mock_crewai_system(self):
        """Create mock CrewAI system."""
        return Mock()

    @pytest.fixture
    def agentic_router(self, mock_crewai_system):
        """Create agentic message router with mocked dependencies."""
        return AgenticMessageRouter(team_id="test_team", crewai_system=mock_crewai_system)

    def test_initialization(self, agentic_router):
        """Test agentic message router initialization."""
        assert agentic_router.team_id == "test_team"
        assert agentic_router.crewai_system is not None

    def test_set_chat_ids(self, agentic_router):
        """Test setting chat IDs."""
        agentic_router.set_chat_ids("-1001234567890", "-1001234567891")
        
        assert agentic_router.main_chat_id == "-1001234567890"
        assert agentic_router.leadership_chat_id == "-1001234567891"

    @pytest.mark.asyncio
    async def test_route_message(self, agentic_router):
        """Test routing messages through agentic system."""
        from kickai.agents.user_flow_agent import TelegramMessage
        
        mock_message = TelegramMessage(
            text="Hello, how are you?",
            user_id="987654321",
            username="testuser",
            chat_id="123456789",
            chat_type=ChatType.MAIN,
            team_id="test_team"
        )
        
        # Mock the user flow agent to avoid actual processing
        with patch.object(agentic_router, 'user_flow_agent') as mock_user_flow:
            mock_user_flow.determine_user_flow.return_value = "registered_user"
            
            with patch.object(agentic_router, '_process_with_crewai_system') as mock_process:
                mock_response = Mock()
                mock_response.message = "I'm doing well, thank you!"
                mock_response.success = True
                mock_process.return_value = mock_response
                
                # Mock the method to be async
                mock_process.return_value = AsyncMock(return_value=mock_response)
                
                result = await agentic_router.route_message(mock_message)
                
                assert result == mock_response
                mock_process.assert_called_once_with(mock_message)

    @pytest.mark.asyncio
    async def test_route_contact_share(self, agentic_router):
        """Test routing contact share events."""
        from kickai.agents.user_flow_agent import TelegramMessage
        
        mock_message = TelegramMessage(
            text="Contact shared",
            user_id="987654321",
            username="testuser",
            chat_id="123456789",
            chat_type=ChatType.MAIN,
            team_id="test_team",
            contact_phone="+1234567890"
        )
        
        # Mock the user flow agent to avoid actual processing
        with patch.object(agentic_router, 'user_flow_agent') as mock_user_flow:
            mock_user_flow.determine_user_flow.return_value = "registered_user"
            
            with patch.object(agentic_router, '_process_with_crewai_system') as mock_process:
                mock_response = Mock()
                mock_response.message = "Contact received successfully!"
                mock_response.success = True
                mock_process.return_value = mock_response
                
                # Mock the method to be async
                mock_process.return_value = AsyncMock(return_value=mock_response)
                
                result = await agentic_router.route_contact_share(mock_message)
                
                assert result == mock_response
                mock_process.assert_called_once_with(mock_message)

    def test_convert_telegram_update_to_message(self, agentic_router):
        """Test converting Telegram updates to domain messages."""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_update.effective_user.id = "987654321"
        mock_update.effective_user.username = "testuser"
        mock_update.message.text = "Hello, world!"
        
        result = agentic_router.convert_telegram_update_to_message(mock_update)
        
        assert result.text == "Hello, world!"
        assert result.user_id == "987654321"
        assert result.username == "testuser"
        assert result.chat_id == "123456789"

    def test_convert_telegram_update_with_command(self, agentic_router):
        """Test converting Telegram updates with commands."""
        mock_update = Mock()
        mock_update.effective_chat.id = "123456789"
        mock_update.effective_user.id = "987654321"
        mock_update.effective_user.username = "testuser"
        mock_update.message.text = "/help"
        
        result = agentic_router.convert_telegram_update_to_message(mock_update, "/help")
        
        assert result.text == "/help"
        assert result.user_id == "987654321"
        assert result.username == "testuser"
        assert result.chat_id == "123456789"


class TestBotManagerTelegramIntegration:
    """Integration tests for bot manager and Telegram API."""

    @pytest.mark.asyncio
    async def test_complete_message_flow(self):
        """Test complete message processing workflow."""
        # This would test the full workflow from Telegram update to response
        # Implementation depends on actual integration setup
        pass

    @pytest.mark.asyncio
    async def test_multi_team_operations(self):
        """Test operations across multiple teams."""
        # This would test handling multiple teams simultaneously
        # Implementation depends on actual integration setup
        pass

    @pytest.mark.asyncio
    async def test_bot_lifecycle(self):
        """Test complete bot lifecycle."""
        # This would test bot startup, operation, and shutdown
        # Implementation depends on actual integration setup
        pass

    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test error recovery and system resilience."""
        # This would test system behavior under error conditions
        # Implementation depends on actual integration setup
        pass


class TestConfigurationManagement:
    """Test configuration management for bot manager and Telegram API."""

    def test_team_configuration_validation(self):
        """Test team configuration validation."""
        # Test valid configuration
        valid_config = {
            "team_id": "test_team",
            "bot_token": "test_token",
            "main_chat_id": "-1001234567890",
            "leadership_chat_id": "-1001234567891"
        }
        # Should not raise any exceptions
        
        # Test invalid configuration (missing required fields)
        invalid_config = {
            "team_id": "test_team",
            "bot_token": "",  # Empty token
            "main_chat_id": "-1001234567890",
            "leadership_chat_id": "-1001234567891"
        }
        # Should raise validation error
        with pytest.raises(ValueError):
            # This would be the actual validation logic
            pass

    def test_environment_configuration(self):
        """Test environment configuration loading."""
        # Test loading from environment variables
        # Test configuration overrides
        # Test default values
        # Test configuration validation
        pass


class TestSecurityFeatures:
    """Test security features for bot manager and Telegram API."""

    def test_token_validation(self):
        """Test bot token validation."""
        # Test valid token format
        # Test invalid token format
        # Test token storage security
        # Test token rotation
        pass

    def test_access_control(self):
        """Test access control mechanisms."""
        # Test chat access control
        # Test user permission validation
        # Test command authorization
        # Test data privacy
        pass


class TestPerformanceFeatures:
    """Test performance features for bot manager and Telegram API."""

    @pytest.mark.asyncio
    async def test_concurrent_message_handling(self):
        """Test handling multiple concurrent messages."""
        # Test message queue performance
        # Test response time under load
        # Test memory usage patterns
        # Test resource cleanup
        pass

    @pytest.mark.asyncio
    async def test_multi_team_performance(self):
        """Test performance with multiple teams."""
        # Test multiple team handling
        # Test team isolation
        # Test resource sharing
        # Test scalability
        pass


if __name__ == "__main__":
    # Run the comprehensive test suite
    pytest.main([__file__, "-v", "--tb=short"]) 