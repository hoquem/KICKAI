"""
Test fixtures and data factories for KICKAI tests.
"""

from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid


@dataclass
class SampleData:
    """Sample data for testing."""
    team_id: str = "test-team-123"
    player_id: str = "test-player-456"
    match_id: str = "test-match-789"
    user_id: str = "123456789"
    chat_id: str = "-987654321"


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
    def create_player_data(player_id: str = None, team_id: str = None) -> Dict[str, Any]:
        """Create sample player data."""
        return {
            "id": player_id or f"player-{uuid.uuid4().hex[:8]}",
            "player_id": f"P{uuid.uuid4().hex[:6].upper()}",
            "name": "John Doe",
            "phone": "+1234567890",
            "email": "john.doe@test.com",
            "team_id": team_id or "test-team-123",
            "position": "midfielder",
            "role": "player",
            "fa_registered": True,
            "onboarding_status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
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
    def create_payment_data(payment_id: str = None, team_id: str = None) -> Dict[str, Any]:
        """Create sample payment data."""
        return {
            "id": payment_id or f"payment-{uuid.uuid4().hex[:8]}",
            "team_id": team_id or "test-team-123",
            "player_id": "test-player-456",
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