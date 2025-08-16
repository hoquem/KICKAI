"""
Team management tools for KICKAI system.

This module provides tools for team administration and management.
"""

import logging

from pydantic import BaseModel

from kickai.core.dependency_container import get_container
from kickai.features.team_administration.domain.services.team_service import TeamService
from kickai.utils.crewai_tool_decorator import tool
from kickai.core.enums import ResponseStatus
from kickai.utils.tool_helpers import create_json_response
from typing import Optional

logger = logging.getLogger(__name__)


class CreateTeamInput(BaseModel):
    """Input model for create_team tool."""

    team_name: str
    team_id: str
    admin_user_id: Optional[str] = None


@tool("create_team", result_as_answer=True)
async def create_team(team_name: str, team_id: str, admin_user_id: Optional[str] = None) -> str:
    """Create a new team.
    
    Creates a new team entity in the system with the specified
    name, identifier, and optional admin user.
    
    :param team_name: The name of the team to create
    :type team_name: str
    :param team_id: The unique identifier for the team
    :type team_id: str
    :param admin_user_id: Optional admin user ID for the team
    :type admin_user_id: Optional[str]
    :returns: JSON string with confirmation message and team details
    :rtype: str
    :raises Exception: When TeamService unavailable or team creation fails
    
    .. example::
       >>> result = create_team("Liverpool FC", "LFC", "admin123")
       >>> print(result)
       '{"status": "success", "data": {"message": "Team created successfully...", ...}}'
    
    .. note::
       Team ID must be unique across the system
    """
    try:
        container = get_container()
        team_service = container.get_service(TeamService)

        if not team_service:
            logger.error("TeamService not available")
            return create_json_response(ResponseStatus.ERROR, message="Team service not available")

        # Create the team (async)
        team = await team_service.create_team(team_name, team_id, admin_user_id)

        if team:
            logger.info(f"Team created: {team_name} (ID: {team_id})")
            return create_json_response(ResponseStatus.SUCCESS, data={
                'message': f'Team created successfully: {team_name} (ID: {team_id})',
                'team_name': team_name,
                'team_id': team_id,
                'admin_user_id': admin_user_id
            })
        else:
            logger.error(f"Failed to create team: {team_name}")
            return create_json_response(ResponseStatus.ERROR, message=f"Failed to create team: {team_name}")

    except Exception as e:
        logger.error(f"Failed to create team: {e}")
        return create_json_response(ResponseStatus.ERROR, message=f"Failed to create team: {e!s}")
