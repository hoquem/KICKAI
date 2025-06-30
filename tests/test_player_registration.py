"""
Test Player Registration System - Phase 1
Tests the core player management functionality
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from player_registration import Player, PlayerRegistrationManager, PlayerCommandHandler

class TestPlayer(unittest.TestCase):
    """Test Player data structure"""
    
    def test_player_creation(self):
        """Test creating a player with basic information"""
        player = Player(
            player_id="JS1",
            name="John Smith",
            phone="07123456789",
            position="striker",
            fa_eligible=False
        )
        
        self.assertEqual(player.player_id, "JS1")
        self.assertEqual(player.name, "John Smith")
        self.assertEqual(player.phone, "07123456789")
        self.assertEqual(player.position, "striker")
        self.assertEqual(player.status, "active")
        self.assertIsNotNone(player.date_added)
        self.assertFalse(player.fa_registered)
        self.assertFalse(player.fa_eligible)
    
    def test_player_to_dict(self):
        """Test converting player to dictionary"""
        player = Player(
            player_id="JS1",
            name="John Smith",
            phone="07123456789",
            position="striker",
            added_by="123456"
        )
        
        player_dict = player.to_dict()
        
        self.assertEqual(player_dict['name'], "John Smith")
        self.assertEqual(player_dict['phone'], "07123456789")
        self.assertEqual(player_dict['position'], "striker")
        self.assertEqual(player_dict['added_by'], "123456")
        self.assertIn('date_added', player_dict)
        self.assertIn('fa_registered', player_dict)
    
    def test_player_from_dict(self):
        """Test creating player from dictionary"""
        player_data = {
            'player_id': 'JS1',
            'name': 'John Smith',
            'phone': '07123456789',
            'position': 'striker',
            'status': 'active',
            'date_added': '2024-01-01T10:00:00',
            'added_by': '123456',
            'fa_registered': False
        }
        
        player = Player.from_dict(player_data)
        
        self.assertEqual(player.name, "John Smith")
        self.assertEqual(player.phone, "07123456789")
        self.assertEqual(player.position, "striker")
        self.assertEqual(player.status, "active")
        self.assertEqual(player.date_added, "2024-01-01T10:00:00")
        self.assertEqual(player.added_by, "123456")
        self.assertFalse(player.fa_registered)

class TestPlayerRegistrationManager(unittest.TestCase):
    """Test PlayerRegistrationManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock Firebase client
        self.mock_firebase_client = Mock()
        self.mock_collection = Mock()
        self.mock_document = Mock()
        self.mock_players_ref = Mock()
        
        # Set up the mock chain
        self.mock_firebase_client.collection.return_value = self.mock_collection
        self.mock_collection.document.return_value = self.mock_document
        self.mock_document.collection.return_value = self.mock_players_ref
        
        self.team_id = "test-team-123"
        self.player_manager = PlayerRegistrationManager(self.mock_firebase_client, self.team_id)
    
    def test_validate_phone_valid(self):
        """Test phone number validation with valid numbers"""
        valid_phones = [
            "07123456789",
            "07987654321",
            "07890123456"
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                self.assertTrue(self.player_manager._validate_phone(phone))
    
    def test_validate_phone_invalid(self):
        """Test phone number validation with invalid numbers"""
        invalid_phones = [
            "123456789",  # Too short
            "071234567890",  # Too long
            "08123456789",  # Wrong prefix
            "0712345678",  # Too short
            "0712345678901",  # Too long
            "abc123def45",  # Contains letters
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                self.assertFalse(self.player_manager._validate_phone(phone))
    
    def test_add_player_success(self):
        """Test successfully adding a player"""
        # Mock that player doesn't exist
        self.mock_players_ref.document.return_value.get.return_value.exists = False
        
        success, message = self.player_manager.add_player(
            name="John Smith",
            phone="07123456789",
            position="striker",
            added_by="123456"
        )
        
        self.assertTrue(success)
        self.assertIn("successfully", message)
        self.assertIn("John Smith", message)
        
        # Verify Firebase was called
        self.mock_players_ref.document.assert_called_with("07123456789")
        self.mock_players_ref.document.return_value.set.assert_called_once()
    
    def test_add_player_invalid_phone(self):
        """Test adding player with invalid phone number"""
        success, message = self.player_manager.add_player(
            name="John Smith",
            phone="123456789",  # Invalid
            position="striker",
            added_by="123456"
        )
        
        self.assertFalse(success)
        self.assertIn("Invalid phone number", message)
    
    def test_add_player_already_exists(self):
        """Test adding player that already exists"""
        # Mock that player exists
        existing_player_data = {
            'player_id': 'JS1',
            'name': 'John Smith',
            'phone': '07123456789',
            'position': 'striker'
        }
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = existing_player_data
        self.mock_players_ref.document.return_value.get.return_value = mock_doc
        
        success, message = self.player_manager.add_player(
            name="John Smith",
            phone="07123456789",
            position="striker",
            added_by="123456"
        )
        
        self.assertFalse(success)
        self.assertIn("already exists", message)
    
    def test_remove_player_success(self):
        """Test successfully removing a player"""
        # Mock that player exists
        existing_player_data = {
            'player_id': 'JS1',
            'name': 'John Smith',
            'phone': '07123456789',
            'position': 'striker'
        }
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = existing_player_data
        self.mock_players_ref.document.return_value.get.return_value = mock_doc
        
        success, message = self.player_manager.remove_player(
            phone="07123456789",
            removed_by="123456"
        )
        
        self.assertTrue(success)
        self.assertIn("removed successfully", message)
        
        # Verify Firebase was called
        self.mock_players_ref.document.assert_called_with("07123456789")
        self.mock_players_ref.document.return_value.delete.assert_called_once()
    
    def test_remove_player_not_found(self):
        """Test removing player that doesn't exist"""
        # Mock that player doesn't exist
        self.mock_players_ref.document.return_value.get.return_value.exists = False
        
        success, message = self.player_manager.remove_player(
            phone="07123456789",
            removed_by="123456"
        )
        
        self.assertFalse(success)
        self.assertIn("not found", message)
    
    def test_get_player_by_phone(self):
        """Test getting player by phone number"""
        player_data = {
            'player_id': 'JS1',
            'name': 'John Smith',
            'phone': '07123456789',
            'position': 'striker',
            'status': 'active',
            'date_added': '2024-01-01T10:00:00',
            'added_by': '123456',
            'fa_registered': False
        }
        
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = player_data
        self.mock_players_ref.document.return_value.get.return_value = mock_doc
        
        player = self.player_manager.get_player_by_phone("07123456789")
        
        self.assertIsNotNone(player)
        if player:  # Add null check
            self.assertEqual(player.name, "John Smith")
            self.assertEqual(player.phone, "07123456789")
    
    def test_get_all_players(self):
        """Test getting all players"""
        players_data = [
            {
                'player_id': 'JS1',
                'name': 'John Smith',
                'phone': '07123456789',
                'position': 'striker',
                'status': 'active'
            },
            {
                'player_id': 'JD1',
                'name': 'Jane Doe',
                'phone': '07987654321',
                'position': 'defender',
                'status': 'active'
            }
        ]
        
        # Mock stream method
        mock_docs = []
        for data in players_data:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = data
            mock_docs.append(mock_doc)
        
        self.mock_players_ref.stream.return_value = mock_docs
        
        players = self.player_manager.get_all_players()
        
        self.assertEqual(len(players), 2)
        self.assertEqual(players[0].name, "John Smith")
        self.assertEqual(players[1].name, "Jane Doe")
    
    def test_get_player_stats(self):
        """Test getting player statistics"""
        players_data = [
            {'player_id': 'J1', 'name': 'John', 'phone': '07123456789', 'position': 'striker', 'status': 'active', 'fa_registered': True},
            {'player_id': 'J2', 'name': 'Jane', 'phone': '07987654321', 'position': 'defender', 'status': 'active', 'fa_registered': False},
            {'player_id': 'B1', 'name': 'Bob', 'phone': '07890123456', 'position': 'midfielder', 'status': 'pending', 'fa_registered': False},
            {'player_id': 'A1', 'name': 'Alice', 'phone': '07765432109', 'position': 'goalkeeper', 'status': 'inactive', 'fa_registered': True}
        ]
        
        # Mock stream method
        mock_docs = []
        for data in players_data:
            mock_doc = Mock()
            mock_doc.to_dict.return_value = data
            mock_docs.append(mock_doc)
        
        self.mock_players_ref.stream.return_value = mock_docs
        
        stats = self.player_manager.get_player_stats()
        
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['active'], 2)
        self.assertEqual(stats['pending'], 1)
        self.assertEqual(stats['inactive'], 1)
        self.assertEqual(stats['fa_registered'], 2)

    def test_generate_player_id(self):
        # Mock get_all_players to simulate existing IDs
        self.player_manager.get_all_players = lambda: [
            Player(player_id="JS1", name="John Smith", phone="07123456789", position="striker"),
            Player(player_id="JS2", name="John Smith", phone="07987654321", position="defender")
        ]
        new_id = self.player_manager._generate_player_id("John Smith")
        self.assertEqual(new_id, "JS3")

    def test_add_player_fa_eligible(self):
        # Test adding a player who is FA eligible
        self.mock_players_ref.document.return_value.get.return_value.exists = False
        success, message = self.player_manager.add_player(
            name="John Smith",
            phone="07123456789",
            position="striker",
            added_by="123456",
            fa_eligible=True
        )
        self.assertTrue(success)
        # ... existing code ...

class TestPlayerCommandHandler(unittest.TestCase):
    """Test PlayerCommandHandler functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_player_manager = Mock()
        self.command_handler = PlayerCommandHandler(self.mock_player_manager)
    
    def test_handle_add_player_success(self):
        """Test handling add player command successfully"""
        self.mock_player_manager.add_player.return_value = (True, "✅ Player John Smith added successfully!")
        
        response = self.command_handler.handle_command(
            "add player John Smith 07123456789 striker",
            user_id="123456"
        )
        
        self.assertIn("successfully", response)
        # Note: The command handler converts to lowercase, so we check for the lowercase version
        self.mock_player_manager.add_player.assert_called_once_with(
            "john smith", "07123456789", "striker", "123456"
        )
    
    def test_handle_add_player_invalid_format(self):
        """Test handling add player command with invalid format"""
        response = self.command_handler.handle_command(
            "add player John Smith",
            user_id="123456"
        )
        
        self.assertIn("Usage:", response)
        self.assertIn("Example:", response)
    
    def test_handle_remove_player_success(self):
        """Test handling remove player command successfully"""
        self.mock_player_manager.remove_player.return_value = (True, "✅ Player John Smith removed successfully")
        
        response = self.command_handler.handle_command(
            "remove player 07123456789",
            user_id="123456"
        )
        
        self.assertIn("removed successfully", response)
        self.mock_player_manager.remove_player.assert_called_once_with("07123456789", "123456")
    
    def test_handle_remove_player_invalid_format(self):
        """Test handling remove player command with invalid format"""
        response = self.command_handler.handle_command(
            "remove player",
            user_id="123456"
        )
        
        self.assertIn("Usage:", response)
        self.assertIn("Example:", response)
    
    def test_handle_list_players(self):
        """Test handling list players command"""
        players = [
            Player("John Smith", "07123456789", "striker", "active"),
            Player("Jane Doe", "07987654321", "defender", "pending")
        ]
        self.mock_player_manager.get_all_players.return_value = players
        
        response = self.command_handler.handle_command("list players", user_id="123456")
        
        self.assertIn("Team Players", response)
        self.assertIn("John Smith", response)
        self.assertIn("Jane Doe", response)
    
    def test_handle_player_status(self):
        """Test handling player status command"""
        player = Player("John Smith", "07123456789", "striker", "active")
        self.mock_player_manager.get_player_by_phone.return_value = player
        
        response = self.command_handler.handle_command(
            "player status 07123456789",
            user_id="123456"
        )
        
        self.assertIn("Player Status", response)
        self.assertIn("John Smith", response)
        self.assertIn("striker", response)
    
    def test_handle_player_stats(self):
        """Test handling player stats command"""
        stats = {
            'total': 10,
            'active': 8,
            'pending': 1,
            'inactive': 1,
            'fa_registered': 7
        }
        self.mock_player_manager.get_player_stats.return_value = stats
        
        response = self.command_handler.handle_command("player stats", user_id="123456")
        
        self.assertIn("Team Statistics", response)
        self.assertIn("10", response)  # Total players
        self.assertIn("8", response)   # Active players
        self.assertIn("70.0%", response)  # FA compliance percentage
    
    def test_handle_unknown_command(self):
        """Test handling unknown command"""
        response = self.command_handler.handle_command("unknown command", user_id="123456")
        
        self.assertIn("Player Management Commands", response)
        self.assertIn("Help:", response)

class TestPlayerRegistrationIntegration(unittest.TestCase):
    """Integration tests for player registration system"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        # Mock Firebase client for integration tests
        self.mock_firebase_client = Mock()
        self.mock_collection = Mock()
        self.mock_document = Mock()
        self.mock_players_ref = Mock()
        
        # Set up the mock chain
        self.mock_firebase_client.collection.return_value = self.mock_collection
        self.mock_collection.document.return_value = self.mock_document
        self.mock_document.collection.return_value = self.mock_players_ref
        
        self.team_id = "test-team-123"
        self.player_manager = PlayerRegistrationManager(self.mock_firebase_client, self.team_id)
        self.command_handler = PlayerCommandHandler(self.player_manager)
    
    def test_full_player_lifecycle(self):
        """Test complete player lifecycle: add, list, status, remove"""
        # Step 1: Add player
        self.mock_players_ref.document.return_value.get.return_value.exists = False
        
        success, message = self.player_manager.add_player(
            name="John Smith",
            phone="07123456789",
            position="striker",
            added_by="123456"
        )
        
        self.assertTrue(success)
        
        # Step 2: List players
        player = Player("John Smith", "07123456789", "striker", "pending")
        self.mock_players_ref.stream.return_value = [Mock(to_dict=lambda: player.to_dict())]
        
        list_response = self.command_handler.handle_command("list players", user_id="123456")
        self.assertIn("John Smith", list_response)
        
        # Step 3: Check player status
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = player.to_dict()
        self.mock_players_ref.document.return_value.get.return_value = mock_doc
        
        status_response = self.command_handler.handle_command("player status 07123456789", user_id="123456")
        self.assertIn("John Smith", status_response)
        self.assertIn("striker", status_response)
        
        # Step 4: Remove player
        success, message = self.player_manager.remove_player("07123456789", "123456")
        self.assertTrue(success)
    
    def test_command_handler_with_real_manager(self):
        """Test command handler with real player manager"""
        # Mock that no players exist initially
        self.mock_players_ref.document.return_value.get.return_value.exists = False
        self.mock_players_ref.stream.return_value = []
        
        # Test adding player via command
        response = self.command_handler.handle_command(
            "add player John Smith 07123456789 striker",
            user_id="123456"
        )
        
        self.assertIn("successfully", response)
        
        # Verify the manager was called correctly
        # Note: The command handler converts to lowercase, so we check for the lowercase version
        # self.player_manager.add_player.assert_called_once_with(
        #     "john smith", "07123456789", "striker", "123456"
        # )

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2) 