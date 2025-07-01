"""
Test Player Registration System - Updated for new architecture
Tests the core player management functionality using the new service layer
"""

import pytest
from src.testing.test_base import BaseTestCase
from src.testing.test_fixtures import TestDataFactory, SampleData
from src.database.models import Player, PlayerPosition, PlayerRole, OnboardingStatus


class TestPlayer(BaseTestCase):
    """Test Player data structure using new model and testing infrastructure"""
    
    def setup_test_data(self):
        """Set up test data using the new infrastructure"""
        self.test_player_data = TestDataFactory.create_player_data(
            name="John Smith",
            phone="07123456789",
            position=PlayerPosition.FORWARD,
            role=PlayerRole.PLAYER,
            team_id="test-team-123"
        )
    
    def test_player_creation(self):
        """Test creating a player with basic information"""
        player = Player(
            name="John Smith",
            phone="07123456789",
            position=PlayerPosition.FORWARD,
            role=PlayerRole.PLAYER,
            fa_registered=False,
            fa_eligible=False,
            team_id="test-team-123"
        )
        
        self.assertEqual(player.name, "John Smith")
        self.assertEqual(player.phone, "07123456789")
        self.assertEqual(player.position, PlayerPosition.FORWARD)
        self.assertEqual(player.role, PlayerRole.PLAYER)
        self.assertFalse(player.fa_registered)
        self.assertFalse(player.fa_eligible)
        self.assertEqual(player.team_id, "test-team-123")
        self.assertIsNotNone(player.created_at)
    
    def test_player_to_dict(self):
        """Test converting player to dictionary"""
        player = Player(
            name="John Smith",
            phone="07123456789",
            position=PlayerPosition.MIDFIELDER,
            role=PlayerRole.PLAYER,
            team_id="test-team-123"
        )
        
        player_dict = player.to_dict()
        
        self.assertEqual(player_dict['name'], "John Smith")
        self.assertEqual(player_dict['phone'], "07123456789")
        self.assertEqual(player_dict['position'], "midfielder")
        self.assertEqual(player_dict['role'], "player")
        self.assertIn('created_at', player_dict)
        self.assertIn('updated_at', player_dict)
    
    def test_player_from_dict(self):
        """Test creating player from dictionary"""
        player_data = {
            'id': 'test-id-123',
            'name': 'John Smith',
            'phone': '07123456789',
            'position': 'midfielder',
            'role': 'player',
            'fa_registered': False,
            'fa_eligible': True,
            'player_id': 'JS1',
            'team_id': 'test-team-123',
            'onboarding_status': 'pending',
            'created_at': '2024-01-01T10:00:00',
            'updated_at': '2024-01-01T10:00:00'
        }
        
        player = Player.from_dict(player_data)
        
        self.assertEqual(player.name, "John Smith")
        self.assertEqual(player.phone, "07123456789")
        self.assertEqual(player.position, PlayerPosition.MIDFIELDER)
        self.assertEqual(player.role, PlayerRole.PLAYER)
        self.assertFalse(player.fa_registered)
        self.assertTrue(player.fa_eligible)
        self.assertEqual(player.player_id, "JS1")
        self.assertEqual(player.team_id, "test-team-123")
    
    def test_player_validation(self):
        """Test player validation"""
        # Test valid player
        player = Player(
            name="Jane Doe",
            phone="07987654321",
            position=PlayerPosition.DEFENDER,
            role=PlayerRole.CAPTAIN,
            team_id="test-team-123"
        )
        self.assertEqual(player.name, "Jane Doe")
        self.assertEqual(player.phone, "07987654321")
    
    def test_player_update(self):
        """Test player update functionality"""
        player = Player(
            name="John Smith",
            phone="07123456789",
            position=PlayerPosition.FORWARD,
            role=PlayerRole.PLAYER,
            team_id="test-team-123"
        )
        
        # Update player
        player.update(name="John Updated", position=PlayerPosition.MIDFIELDER)
        
        self.assertEqual(player.name, "John Updated")
        self.assertEqual(player.position, PlayerPosition.MIDFIELDER)
        self.assertIsNotNone(player.updated_at)
    
    def test_sample_data_integration(self):
        """Test using sample data from the new infrastructure"""
        john_smith = SampleData.PLAYERS["john_smith"]
        self.assertEqual(john_smith.name, "John Smith")
        self.assertEqual(john_smith.role, PlayerRole.CAPTAIN)
        self.assertEqual(john_smith.onboarding_status, OnboardingStatus.COMPLETED)
    
    def test_test_data_factory(self):
        """Test using TestDataFactory for creating test data"""
        player_data = TestDataFactory.create_player_data(
            name="Factory Test",
            phone="07555123456",
            position=PlayerPosition.GOALKEEPER,
            role=PlayerRole.PLAYER
        )
        
        self.assertEqual(player_data.name, "Factory Test")
        self.assertEqual(player_data.position, PlayerPosition.GOALKEEPER)
        self.assertIsNotNone(player_data.id)
        self.assertIsNotNone(player_data.created_at) 