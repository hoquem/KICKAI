"""Team Administration Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for team administration features.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import all application layer tools
from .team_member_tools import (
    add_team_member_simplified,
    get_my_team_member_status,
    get_team_members,
    activate_team_member
)
from .player_management_tools import add_player
from .team_management_tools import list_team_members_and_players
from .team_administration_tools import (
    add_team_member_role,
    remove_team_member_role,
    promote_team_member_to_admin,
    create_team,
    update_team_member_field,
    update_team_member_multiple_fields,
    get_team_member_update_help,
    get_team_member_current_info,
    update_other_team_member
)

# Export all tools for agent registration
__all__ = [
    # Team member management
    "add_team_member_simplified",
    "get_my_team_member_status",
    "get_team_members",
    "activate_team_member",
    # Player management
    "add_player",
    # Team management
    "list_team_members_and_players",
    # Team administration
    "add_team_member_role",
    "remove_team_member_role",
    "promote_team_member_to_admin",
    "create_team",
    "update_team_member_field",
    "update_team_member_multiple_fields",
    "get_team_member_update_help",
    "get_team_member_current_info",
    "update_other_team_member"
]