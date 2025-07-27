"""
Team management tools for KICKAI system.

This module provides tools for team administration and management.
"""

import logging

from crewai.tools import tool
from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.features.team_administration.domain.services.team_service import TeamService

logger = logging.getLogger(__name__)


class CreateTeamInput(BaseModel):
    """Input model for create_team tool."""

    team_name: str
    team_id: str
    admin_user_id: str | None = None


@tool("create_team")
def create_team(team_name: str, team_id: str, admin_user_id: str | None = None) -> str:
    """
    Create a new team. Requires: team_name, team_id

    Args:
        team_name: The name of the team to create
        team_id: The unique identifier for the team
        admin_user_id: Optional admin user ID for the team

    Returns:
        Confirmation message indicating success or failure
    """
    try:
        container = get_container()
        team_service = container.get_service(TeamService)

        if not team_service:
            logger.error("❌ TeamService not available")
            return "❌ Team service not available"

        # Create the team
        team = team_service.create_team(team_name, team_id, admin_user_id)

        if team:
            logger.info(f"✅ Team created: {team_name} (ID: {team_id})")
            return f"✅ Team created successfully: {team_name} (ID: {team_id})"
        else:
            logger.error(f"❌ Failed to create team: {team_name}")
            return f"❌ Failed to create team: {team_name}"

    except Exception as e:
        logger.error(f"❌ Failed to create team: {e}")
        return f"❌ Failed to create team: {e!s}"
