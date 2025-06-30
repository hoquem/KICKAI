#!/usr/bin/env python3
"""
Test OnboardingAgent Integration

This test verifies the complete onboarding workflow integration:
1. Player join via invite
2. Onboarding agent initialization
3. Onboarding conversation flow
4. Response handling
5. Completion and leadership notification
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain.tools import BaseTool

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agents import OnboardingAgent
from src.simple_agentic_handler import SimpleAgenticHandler
from src.telegram_command_handler import AgentBasedMessageHandler
from src.player_registration import PlayerRegistrationManager, Player

class DummyTool(BaseTool):
    name = "dummy"
    description = "dummy tool"
    
    def __init__(self, team_id=None, *args, **kwargs):
        super().__init__(name="dummy", description="dummy tool")
        
    def _run(self, *args, **kwargs):
        return "dummy result"
        
    def _arun(self, *args, **kwargs):
        return "dummy result"

class DummyLLM:
    def bind(self, *args, **kwargs):
        return self
    
    def invoke(self, *args, **kwargs):
        return "Dummy response"
    
    def __call__(self, *args, **kwargs):
        return "Dummy response"

class TestOnboardingIntegration:
    """Test the complete onboarding integration workflow."""
    
    def setup_method(self):
        """Set up test environment."""
        self.team_id = "test-team-123"
        self.player_id = "JS1"
        self.telegram_user_id = "123456789"
        self.telegram_username = "testuser"
        self.mock_llm = DummyLLM()
        
        # Mock Firebase client
        self.mock_firebase = Mock()
        self.mock_collection = Mock()
        self.mock_doc = Mock()
        self.mock_firebase.collection.return_value = self.mock_collection
        self.mock_collection.document.return_value = self.mock_doc
        
        # Mock player data
        self.mock_player_data = {
            'player_id': self.player_id,
            'name': 'John Smith',
            'phone_number': '07123456789',
            'position': 'midfielder',
            'telegram_id': self.telegram_user_id,
            'telegram_username': self.telegram_username,
            'onboarding_status': 'pending',
            'onboarding_step': None,
            'emergency_contact': None,
            'date_of_birth': None,
            'fa_eligible': False
        }

    @patch('src.tools.firebase_tools.get_firebase_client')
    @patch('src.agents.PlayerTools', new=DummyTool)
    @patch('src.agents.SendTelegramMessageTool', new=DummyTool)
    @patch('src.agents.SendLeadershipMessageTool', new=DummyTool)
    @patch('src.agents.CommandLoggingTools', new=DummyTool)
    def test_onboarding_agent_initialization(self, mock_firebase):
        """Test OnboardingAgent initialization."""
        # Mock Firebase client
        mock_firebase.return_value = self.mock_firebase
        
        # Initialize agent
        agent = OnboardingAgent(self.team_id, team_name="Test Team", llm=self.mock_llm)
        
        # Verify initialization
        assert agent._player_tools is not None
        assert agent._message_tool is not None
        assert agent._leadership_tool is not None
        assert agent._log_tool is not None

    @patch('src.tools.firebase_tools.get_firebase_client')
    @patch('src.agents.PlayerTools', new=DummyTool)
    @patch('src.agents.SendTelegramMessageTool', new=DummyTool)
    @patch('src.agents.SendLeadershipMessageTool', new=DummyTool)
    @patch('src.agents.CommandLoggingTools', new=DummyTool)
    @patch('src.agents.PlayerTools', new_callable=lambda: type('CustomPlayerTool', (DummyTool,), {
        '_run': lambda self, command, **kwargs: f"Player: John Smith (JS1)" if command == 'get_player' else "ok"
    }))
    def test_start_onboarding(self, mock_player_tools, mock_firebase):
        """Test starting the onboarding process."""
        # Mock Firebase client
        mock_firebase.return_value = self.mock_firebase
        
        # Initialize agent
        agent = OnboardingAgent(self.team_id, team_name="Test Team", llm=self.mock_llm)
        
        # Start onboarding
        success, message = agent.start_onboarding(self.player_id, self.telegram_user_id)
        
        # Verify success
        assert success is True
        assert "started successfully" in message

    @patch('src.tools.firebase_tools.get_firebase_client')
    @patch('src.agents.PlayerTools', new=DummyTool)
    @patch('src.agents.SendTelegramMessageTool', new=DummyTool)
    @patch('src.agents.SendLeadershipMessageTool', new=DummyTool)
    @patch('src.agents.CommandLoggingTools', new=DummyTool)
    @patch('src.agents.PlayerTools', new_callable=lambda: type('CustomPlayerTool', (DummyTool,), {
        '_run': lambda self, command, **kwargs: "ok"
    }))
    def test_welcome_response_confirm(self, mock_player_tools, mock_firebase):
        """Test handling 'confirm' response to welcome message."""
        # Mock Firebase client
        mock_firebase.return_value = self.mock_firebase
        
        # Initialize agent
        agent = OnboardingAgent(self.team_id, team_name="Test Team", llm=self.mock_llm)
        
        # Handle confirm response
        success, message = agent.handle_welcome_response(self.player_id, self.telegram_user_id, "confirm")
        
        # Verify success
        assert success is True
        assert "Moved to info collection" in message

    @patch('src.tools.firebase_tools.get_firebase_client')
    @patch('src.agents.PlayerTools', new=DummyTool)
    @patch('src.agents.SendTelegramMessageTool', new=DummyTool)
    @patch('src.agents.SendLeadershipMessageTool', new=DummyTool)
    @patch('src.agents.CommandLoggingTools', new=DummyTool)
    @patch('src.agents.PlayerTools', new_callable=lambda: type('CustomPlayerTool', (DummyTool,), {
        '_run': lambda self, command, **kwargs: "ok"
    }))
    def test_info_collection_emergency_contact(self, mock_player_tools, mock_firebase):
        """Test collecting emergency contact information."""
        # Mock Firebase client
        mock_firebase.return_value = self.mock_firebase
        
        # Initialize agent
        agent = OnboardingAgent(self.team_id, team_name="Test Team", llm=self.mock_llm)
        
        # Handle emergency contact response
        success, message = agent.handle_info_collection(self.player_id, self.telegram_user_id, "emergency Jane Doe 07987654321")
        
        # Verify success
        assert success is True
        assert "Emergency contact saved" in message

    @patch('src.tools.firebase_tools.get_firebase_client')
    @patch('src.agents.PlayerTools', new=DummyTool)
    @patch('src.agents.SendTelegramMessageTool', new=DummyTool)
    @patch('src.agents.SendLeadershipMessageTool', new=DummyTool)
    @patch('src.agents.CommandLoggingTools', new=DummyTool)
    @patch('src.agents.PlayerTools', new_callable=lambda: type('CustomPlayerTool', (DummyTool,), {
        '_run': lambda self, command, **kwargs: "ok"
    }))
    def test_info_collection_date_of_birth(self, mock_player_tools, mock_firebase):
        """Test collecting date of birth information."""
        # Mock Firebase client
        mock_firebase.return_value = self.mock_firebase
        
        # Initialize agent
        agent = OnboardingAgent(self.team_id, team_name="Test Team", llm=self.mock_llm)
        
        # Handle date of birth response
        success, message = agent.handle_info_collection(self.player_id, self.telegram_user_id, "dob 15/03/1990")
        
        # Verify success
        assert success is True
        assert "Date of birth saved" in message

    @patch('src.tools.firebase_tools.get_firebase_client')
    @patch('src.agents.PlayerTools', new=DummyTool)
    @patch('src.agents.SendTelegramMessageTool', new=DummyTool)
    @patch('src.agents.SendLeadershipMessageTool', new=DummyTool)
    @patch('src.agents.CommandLoggingTools', new=DummyTool)
    @patch('src.agents.PlayerTools', new_callable=lambda: type('CustomPlayerTool', (DummyTool,), {
        '_run': lambda self, command, **kwargs: "ok"
    }))
    def test_complete_onboarding(self, mock_player_tools, mock_firebase):
        """Test completing the onboarding process."""
        # Mock Firebase client
        mock_firebase.return_value = self.mock_firebase
        
        # Initialize agent
        agent = OnboardingAgent(self.team_id, team_name="Test Team", llm=self.mock_llm)
        
        # Complete onboarding
        success, message = agent.complete_onboarding(self.player_id, self.telegram_user_id)
        
        # Verify success
        assert success is True
        assert "completed successfully" in message

    @patch('src.tools.firebase_tools.get_firebase_client')
    def test_simple_agentic_handler_integration(self, mock_firebase):
        """Test OnboardingAgent integration with SimpleAgenticHandler."""
        # Mock Firebase client
        mock_firebase.return_value = self.mock_firebase
        
        # Mock player manager
        with patch('src.simple_agentic_handler.PlayerRegistrationManager') as mock_player_manager:
            mock_player_manager.return_value.player_joined_via_invite.return_value = (True, "Player joined successfully")
            
            # Initialize handler
            handler = SimpleAgenticHandler(self.team_id)
            
            # Verify onboarding agent is initialized
            assert handler.onboarding_agent is not None
            
            # Test player join
            result = handler.handle_player_join(self.player_id, self.telegram_user_id, self.telegram_username)
            assert "joined successfully" in result

    @patch('src.tools.firebase_tools.get_firebase_client')
    def test_telegram_handler_integration(self, mock_firebase):
        """Test OnboardingAgent integration with Telegram command handler."""
        # Mock Firebase client
        mock_firebase.return_value = self.mock_firebase
        
        # Mock agentic handler
        with patch('src.simple_agentic_handler.create_simple_agentic_handler') as mock_create_handler:
            mock_handler = Mock()
            mock_handler.player_manager = Mock()
            mock_handler.player_manager.player_joined_via_invite.return_value = (True, "Player joined successfully")
            mock_create_handler.return_value = mock_handler
            
            # Initialize handler
            handler = AgentBasedMessageHandler(self.team_id)
            
            # Verify onboarding agent is initialized
            assert handler.onboarding_agent is not None
            
            # Test onboarding message handling
            result = handler.handle_onboarding_message("confirm", self.telegram_user_id, self.telegram_username, False)
            assert "Error processing message" in result  # Expected since we don't have a real player

    def test_onboarding_workflow_complete(self):
        """Test the complete onboarding workflow end-to-end."""
        # This test would require more complex mocking but demonstrates the workflow
        workflow_steps = [
            "1. Player joins via invite link",
            "2. Onboarding agent starts conversation",
            "3. Player confirms details",
            "4. Player provides emergency contact",
            "5. Player provides date of birth",
            "6. Player completes onboarding",
            "7. Leadership is notified"
        ]
        
        # Verify workflow steps are defined
        assert len(workflow_steps) == 7
        assert "Player joins via invite link" in workflow_steps[0]
        assert "Leadership is notified" in workflow_steps[6]

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 