"""Team Administration Application Tools - Clean Architecture Compliant

This module contains all CrewAI tools for team administration features.
These tools serve as the application boundary and delegate to pure domain services.
"""

# Import all application layer tools
# Import approve tools
from .approve_tools import approve_member, approve_player, list_pending_approvals

# Import member info tools (CrewAI semantic naming)
from .member_info_tools import get_member_by_identifier, get_member_update_help, list_members_all
from .player_management_tools import create_player
from .team_administration_tools import (
    assign_member_role,
    create_team,
    promote_member_admin,
    revoke_member_role,
    update_member_field,
    update_member_info,
    update_member_multiple_fields,
)
from .team_management_tools import list_team_members_and_players
from .team_member_tools import activate_member, create_member

# Export all tools for agent registration
__all__ = [
    # Team member management
    "create_member",
    "activate_member",
    # Player management
    "create_player",
    # Team management
    "list_team_members_and_players",
    # Team administration
    "assign_member_role",
    "revoke_member_role",
    "promote_member_admin",
    "create_team",
    "update_member_field",
    "update_member_multiple_fields",
    "get_member_update_help",
    "update_member_info",
    # Approve tools
    "approve_player",
    "approve_member",
    "list_pending_approvals",
    # Member info tools (CrewAI semantic naming)
    "get_member_by_identifier",
    "list_members_all",
]
