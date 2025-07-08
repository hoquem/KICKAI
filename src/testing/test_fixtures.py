"""
Test fixtures and data factories for KICKAI tests.
"""

from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
from database.models_improved import Player, PlayerPosition, PlayerRole
from utils.player_id_service import generate_player_id_from_name


@dataclass
class SampleData:
    """Sample data for testing."""
    team_id: str = "test-team-123"
    player_id: str = generate_player_id_from_name("John Smith")  # Use centralized player ID generation
    match_id: str = "test-match-789"
    user_id: str = "123456789"
    chat_id: str = "-987654321"
    
    # Sample players data
    PLAYERS = {
        "john_smith": {
            "name": "John Smith",
            "phone": "+447123456789",
            "email": "john.smith@example.com",
            "position": "midfielder",
            "role": "player",
            "fa_registered": True,
            "match_eligible": True,
            "player_id": generate_player_id_from_name("John Smith")  # Use centralized player ID generation
        },
        "jane_doe": {
            "name": "Jane Doe", 
            "phone": "+447987654321",
            "email": "jane.doe@example.com",
            "position": "forward",
            "role": "player",
            "fa_registered": False,
            "match_eligible": False,
            "player_id": generate_player_id_from_name("Jane Doe")  # Use centralized player ID generation
        }
    }


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_team_data(team_id: str = None) -> Dict[str, Any]:
        """Create sample team data."""
        return {
            "id": team_id or f"team-{uuid.uuid4().hex[:8]}",
            "name": "Test Team",
            "description": "A test team for unit testing",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "settings": {
                "max_players": 20,
                "training_days": ["Monday", "Wednesday"],
                "home_ground": "Test Stadium"
            }
        }
    
    @staticmethod
    def create_player_data(name: str = "John Doe", phone: str = "07123456789", 
                      position: PlayerPosition = None, 
                      role: PlayerRole = PlayerRole.PLAYER,
                      player_id: str = None, team_id: str = None) -> Player:
        """Create sample player data."""
        from database.models_improved import PlayerPosition as InfraPlayerPosition
        if position is None:
            position = InfraPlayerPosition.ANY
        if player_id is None:
            player_id = generate_player_id_from_name(name)
        return Player(
            name=name,
            phone=phone,
            position=position,
            role=role,
            team_id=team_id or "test-team-123",
            player_id=player_id
        )
    
    @staticmethod
    def create_match_data(match_id: str = None, team_id: str = None) -> Dict[str, Any]:
        """Create sample match data."""
        return {
            "id": match_id or f"match-{uuid.uuid4().hex[:8]}",
            "team_id": team_id or "test-team-123",
            "opponent": "Opponent Team",
            "date": (datetime.now() + timedelta(days=7)).isoformat(),
            "location": "Test Stadium",
            "status": "scheduled",
            "home_away": "home",
            "competition": "League Match",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_payment_data(payment_id: str = None, team_id: str = None, player_id: str = None) -> Dict[str, Any]:
        """Create sample payment data."""
        # Use centralized player ID generation if not provided
        if player_id is None:
            player_id = generate_player_id_from_name("John Smith")
        
        return {
            "id": payment_id or f"payment-{uuid.uuid4().hex[:8]}",
            "team_id": team_id or "test-team-123",
            "player_id": player_id,
            "amount": 25.00,
            "currency": "GBP",
            "type": "match_fee",
            "status": "pending",
            "description": "Match fee for upcoming game",
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_team_member_data(user_id: str = None, team_id: str = None) -> Dict[str, Any]:
        """Create sample team member data."""
        return {
            "id": f"member-{uuid.uuid4().hex[:8]}",
            "user_id": user_id or "123456789",
            "team_id": team_id or "test-team-123",
            "roles": ["player"],
            "joined_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        } 