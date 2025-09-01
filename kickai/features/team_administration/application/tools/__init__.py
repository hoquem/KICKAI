"""Team Administration Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for team administration features.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import all application layer tools
from .team_member_tools import (
    create_member,
    list_members_all,
    activate_member
)
from .player_management_tools import create_player
from .team_management_tools import list_team_members_and_players
from .team_administration_tools import (
    create_member_role,
    remove_member_role,
    promote_member_admin,
    create_team,
    update_member_field,
    update_member_multiple,
    get_member_update_help,
    update_member_info
)

# Import approve tools
from .approve_tools import approve_player, approve_member, list_pending_approvals

# Import member management tools (clean naming convention)
from .member_management_tools import (
    get_member_info,
    get_member_current,
    list_members_and_players,
    update_member_other
)

# Export all tools for agent registration  
__all__ = [
    # Team member management
    "create_member",
    "list_members_all", 
    "activate_member",
    # Player management
    "create_player",
    # Team management
    "list_team_members_and_players",
    # Team administration
    "create_member_role",
    "remove_member_role", 
    "promote_member_admin",
    "create_team",
    "update_member_field",
    "update_member_multiple",
    "get_member_update_help",
    "update_member_info",
    # Approve tools
    "approve_player",
    "approve_member",
    "list_pending_approvals",
    # Member management tools (clean naming convention)
    "get_member_info",
    "get_member_current", 
    "list_members_and_players",
    "update_member_other"
]