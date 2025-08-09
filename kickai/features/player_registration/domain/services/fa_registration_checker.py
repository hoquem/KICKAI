#!/usr/bin/env python3
"""
FA Registration Checker

This module provides functionality to check FA registration status.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..repositories.player_repository_interface import PlayerRepositoryInterface

logger = logging.getLogger(__name__)


class FixtureData:
    """Placeholder for fixture data structure."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def get_registration_status(self) -> str:
        """Get registration status from fixture data."""
        return self.data.get("status", "unknown")


class FARegistrationChecker:
    """Service for checking FA registration status."""

    def __init__(self, player_repository: PlayerRepositoryInterface):
        self.player_repository = player_repository

    async def check_registration_status(self, player_id: str) -> Dict[str, Any]:
        """Check FA registration status for a player."""
        try:
            player = await self.player_repository.get_by_id(player_id)
            if not player:
                return {
                    "registered": False,
                    "message": "Player not found",
                    "last_checked": datetime.now().isoformat(),
                }

            # In a real implementation, this would call an external FA API
            # For now, return mock data based on player status
            if player.status == "active":
                return {
                    "registered": True,
                    "message": "Player is registered with FA",
                    "last_checked": datetime.now().isoformat(),
                    "registration_date": player.created_at.isoformat()
                    if player.created_at
                    else None,
                }
            else:
                return {
                    "registered": False,
                    "message": "Player is not registered with FA",
                    "last_checked": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error checking FA registration for player {player_id}: {e}")
            return {
                "registered": False,
                "message": f"Error checking registration: {e!s}",
                "last_checked": datetime.now().isoformat(),
            }

    async def get_fixture_data(self, player_id: str) -> Optional[FixtureData]:
        """Get fixture data for a player."""
        try:
            # In a real implementation, this would fetch data from FA fixtures
            # For now, return mock data
            mock_data = {
                "player_id": player_id,
                "status": "active",
                "last_match": "2024-01-15",
                "next_match": "2024-01-22",
            }
            return FixtureData(mock_data)
        except Exception as e:
            logger.error(f"Error getting fixture data for player {player_id}: {e}")
            return None
