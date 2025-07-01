#!/usr/bin/env python3
"""
Integration tests for player registration and onboarding workflows.
Tests the complete flow from player registration to onboarding completion.
"""

import pytest
import asyncio
from unittest.mock import Mock
from datetime import datetime, date

from src.testing.test_base import BaseTestCase, AsyncBaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.testing.test_utils import MockLLM, MockAgent, MockTool
from src.telegram.player_registration_handler import PlayerRegistrationHandler
from src.telegram_command_handler import PlayerCommandHandler
from src.database.models import Player, PlayerPosition, PlayerRole, OnboardingStatus
from src.services.player_service import PlayerService
from src.services.team_service import TeamService


@pytest.mark.asyncio
class TestPlayerRegistrationIntegration(AsyncBaseTestCase):
    """Test the complete player registration integration workflow."""
    
    def setup_method(self, method=None):
        """Set up test environment."""
        super().setup_method(method)
        self.team_id = "test-team-123"
        self.player_id = "JS1"
        self.telegram_user_id = "123456789"
        self.telegram_username = "testuser"
        
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
    
    def test_player_registration_handler_initialization(self):
        """Test PlayerRegistrationHandler initialization."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize handler
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Verify initialization
        self.assertEqual(handler.team_id, self.team_id)
        self.assertIsNotNone(handler.player_service)
        self.assertIsNotNone(handler.team_service)
    
    async def test_add_player(self):
        """Test adding a player via the registration handler."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_player_service.create_player.return_value = Player(
            id="test-id",
            player_id="JS1",
            name="John Smith",
            phone="07123456789",
            team_id=self.team_id,
            position=PlayerPosition.MIDFIELDER,
            role=PlayerRole.PLAYER,
            fa_registered=False
        )
        
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize handler with dependency injection
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Add player
        success, message = await handler.add_player(
            name="John Smith",
            phone="07123456789",
            position="midfielder",
            added_by="123456789"
        )
        
        # Verify success
        self.assertTrue(success)
        self.assertIn("added successfully", message)
    
    async def test_get_onboarding_message(self):
        """Test getting onboarding message for a player."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_player_service.get_team_players.return_value = [
            Player(
                id="test-id",
                player_id="JS1",
                name="John Smith",
                phone="07123456789",
                team_id=self.team_id,
                position=PlayerPosition.MIDFIELDER,
                role=PlayerRole.PLAYER,
                fa_registered=False
            )
        ]
        
        mock_team_service = self.create_mock_service('team_service')
        mock_team_service.get_team.return_value = Mock(name="Test Team")
        
        # Initialize handler with dependency injection
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Get onboarding message
        success, message = await handler.get_onboarding_message(self.player_id)
        
        # Verify success
        self.assertTrue(success)
        self.assertIn("Welcome", message)
    
    async def test_process_onboarding_response(self):
        """Test processing onboarding response."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_player_service.get_player.return_value = Player(
            id="test-id",
            player_id="JS1",
            name="John Smith",
            phone="07123456789",
            team_id=self.team_id,
            position=PlayerPosition.MIDFIELDER,
            role=PlayerRole.PLAYER,
            fa_registered=False,
            onboarding_status=OnboardingStatus.PENDING
        )
        mock_player_service.update_player.return_value = Player(
            id="test-id",
            player_id="JS1",
            name="John Smith",
            phone="07123456789",
            team_id=self.team_id,
            position=PlayerPosition.MIDFIELDER,
            role=PlayerRole.PLAYER,
            fa_registered=False
        )
        
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize handler with dependency injection
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Process onboarding response
        success, message = await handler.process_onboarding_response(
            self.player_id,
            "Yes, I confirm"
        )
        
        # Verify success
        self.assertTrue(success)
        self.assertIn("confirmed", message)
    
    async def test_player_command_handler(self):
        """Test player command handler functionality."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize registration handler first
        registration_handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Initialize command handler with registration handler
        command_handler = PlayerCommandHandler(registration_handler)
        
        # Test help command
        response = await command_handler.handle_command("help", self.telegram_user_id)
        self.assertIsInstance(response, str)
        self.assertIn("Available commands", response)
    
    async def test_complete_onboarding_workflow(self):
        """Test the complete onboarding workflow from start to finish."""
        # Mock services with stateful behavior
        mock_player_service = self.create_mock_service('player_service')
        mock_team_service = self.create_mock_service('team_service')
        
        # Mock player data that changes during onboarding
        player_data = {
            'id': 'test-id',
            'player_id': 'JS1',
            'name': 'John Smith',
            'phone': '07123456789',
            'team_id': self.team_id,
            'position': PlayerPosition.MIDFIELDER,
            'role': PlayerRole.PLAYER,
            'fa_registered': False,
            'onboarding_status': OnboardingStatus.PENDING,
            'onboarding_step': None
        }
        
        def get_player_mock(*args, **kwargs):
            return Player(**player_data)
        
        def update_player_side_effect(*args, **kwargs):
            # Simulate onboarding status transitions
            if 'onboarding_status' in kwargs:
                player_data['onboarding_status'] = kwargs['onboarding_status']
            if 'onboarding_step' in kwargs:
                player_data['onboarding_step'] = kwargs['onboarding_step']
            return Player(**player_data)
        
        def get_team_players_mock(*args, **kwargs):
            return [Player(**player_data)]
        
        mock_player_service.get_player.side_effect = get_player_mock
        mock_player_service.update_player.side_effect = update_player_side_effect
        mock_player_service.get_team_players.side_effect = get_team_players_mock
        mock_player_service.create_player.return_value = Player(**player_data)
        
        mock_team_service.get_team.return_value = Mock(name="Test Team")
        
        # Initialize handler
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Step 1: Add player
        success, message = await handler.add_player(
            name="John Smith",
            phone="07123456789",
            position="midfielder",
            added_by=self.telegram_user_id
        )
        self.assertTrue(success)
        
        # Step 2: Get onboarding message
        success, message = await handler.get_onboarding_message(self.player_id)
        self.assertTrue(success)
        self.assertIn("Welcome", message)
        
        # Step 3: Process onboarding response
        success, message = await handler.process_onboarding_response(
            self.player_id,
            "Yes, I confirm"
        )
        self.assertTrue(success)
        
        # Verify final state
        final_player = await mock_player_service.get_player(self.player_id)
        self.assertEqual(final_player.onboarding_status, OnboardingStatus.COMPLETED)
    
    async def test_edge_case_duplicate_phone(self):
        """Test handling of duplicate phone numbers."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_player_service.create_player.side_effect = Exception("Phone number already exists")
        
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize handler
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Try to add player with duplicate phone
        success, message = await handler.add_player(
            name="John Smith",
            phone="07123456789",
            position="midfielder",
            added_by=self.telegram_user_id
        )
        
        # Should handle error gracefully
        self.assertFalse(success)
        self.assertIn("already exists", message)
    
    async def test_edge_case_invalid_position(self):
        """Test handling of invalid position."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize handler
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Try to add player with invalid position
        success, message = await handler.add_player(
            name="John Smith",
            phone="07123456789",
            position="invalid_position",
            added_by=self.telegram_user_id
        )
        
        # Should handle error gracefully
        self.assertFalse(success)
        self.assertIn("invalid", message.lower())
    
    async def test_edge_case_invalid_phone(self):
        """Test handling of invalid phone number."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize handler
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Try to add player with invalid phone
        success, message = await handler.add_player(
            name="John Smith",
            phone="invalid_phone",
            position="midfielder",
            added_by=self.telegram_user_id
        )
        
        # Should handle error gracefully
        self.assertFalse(success)
        self.assertIn("phone", message.lower())
    
    async def test_partial_onboarding_handling(self):
        """Test handling of partial onboarding completion."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_player_service.get_player.return_value = Player(
            id="test-id",
            player_id="JS1",
            name="John Smith",
            phone="07123456789",
            team_id=self.team_id,
            position=PlayerPosition.MIDFIELDER,
            role=PlayerRole.PLAYER,
            fa_registered=False,
            onboarding_status=OnboardingStatus.IN_PROGRESS,
            onboarding_step="emergency_contact"
        )
        
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize handler
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Process partial onboarding response
        success, message = await handler.process_onboarding_response(
            self.player_id,
            "John Doe, 07987654321"
        )
        
        # Should handle partial completion
        self.assertTrue(success)
        self.assertIn("emergency contact", message)
    
    async def test_admin_approval_workflow(self):
        """Test admin approval workflow."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_player_service.get_player.return_value = Player(
            id="test-id",
            player_id="JS1",
            name="John Smith",
            phone="07123456789",
            team_id=self.team_id,
            position=PlayerPosition.MIDFIELDER,
            role=PlayerRole.PLAYER,
            fa_registered=False,
            onboarding_status=OnboardingStatus.PENDING_APPROVAL
        )
        
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize registration handler first
        registration_handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Initialize command handler with registration handler
        command_handler = PlayerCommandHandler(registration_handler)
        
        # Test admin approval command
        response = await command_handler.handle_command(
            f"approve {self.player_id}",
            "admin_user_id"
        )
        
        self.assertIsInstance(response, str)
        self.assertIn("approved", response)
    
    async def test_security_validation(self):
        """Test security validation in player registration."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_team_service = self.create_mock_service('team_service')
        
        # Initialize handler
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Test with invalid user ID
        success, message = await handler.add_player(
            name="John Smith",
            phone="07123456789",
            position="midfielder",
            added_by="invalid_user"
        )
        
        # Should validate user permissions
        self.assertFalse(success)
        self.assertIn("unauthorized", message.lower())
    
    async def test_invite_link_security(self):
        """Test invite link security and validation."""
        # Mock services
        mock_player_service = self.create_mock_service('player_service')
        mock_team_service = self.create_mock_service('team_service')
        
        def get_player_by_phone_mock(*args, **kwargs):
            return None  # Player doesn't exist yet
        
        def update_player_mock(*args, **kwargs):
            # Simulate player joining via invite
            return Player(
                id="test-id",
                player_id="JS1",
                name="John Smith",
                phone="07123456789",
                team_id=self.team_id,
                position=PlayerPosition.MIDFIELDER,
                role=PlayerRole.PLAYER,
                fa_registered=False
            )
        
        def generate_invite_link_mock(*args, **kwargs):
            # Simulate invite link generation
            return "https://t.me/joinchat/test_invite_link"
        
        def get_team_players_mock(*args, **kwargs):
            return []
        
        mock_player_service.get_player_by_phone.side_effect = get_player_by_phone_mock
        mock_player_service.update_player.side_effect = update_player_mock
        mock_player_service.get_team_players.side_effect = get_team_players_mock
        mock_team_service.generate_invite_link.side_effect = generate_invite_link_mock
        
        # Initialize handler
        handler = PlayerRegistrationHandler(
            self.team_id,
            player_service=mock_player_service,
            team_service=mock_team_service
        )
        
        # Test invite link generation
        success, message = await handler.generate_invite_link(
            self.telegram_user_id,
            "https://t.me/joinchat/"
        )
        
        # Should generate secure invite link
        self.assertTrue(success)
        self.assertIn("https://t.me/joinchat/", message)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 