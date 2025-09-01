"""Team Member Management Tools - Clean Architecture Compliant

This module contains CrewAI tools for team member management operations.
These tools follow the clean naming convention: [action]_[entity]_[modifier].
"""

from crewai.tools import tool
from kickai.core.dependency_container import get_container
from typing import Any


@tool("create_player")
async def create_player(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    player_name: str,
    phone_number: str
) -> str:
    """Create a new player registration (leadership/admin function).
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        player_name: Full name of the player to add
        phone_number: Player's phone number
    
    Returns:
        Formatted player creation result with invite information
    """
    try:
        container = get_container()
        
        # Get team member service
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
            team_service = container.get_service(ITeamMemberService)
        except Exception:
            return "❌ Team service is not available"
        
        # Permission check - only leadership can create players
        if chat_type not in ["leadership", "private"]:
            return "❌ Insufficient permissions. Leadership access required."
        
        # Validate inputs
        if not player_name or not player_name.strip():
            return "❌ Player name is required"
            
        if not phone_number or not phone_number.strip():
            return "❌ Phone number is required"
        
        # Create the player
        result = await team_service.create_player_registration(
            team_id=team_id,
            name=player_name,
            phone=phone_number,
            created_by_telegram_id=telegram_id
        )
        
        if result:
            invite_link = result.get('invite_link', 'N/A')
            player_id = result.get('player_id', 'N/A')
            status_text = result.get('status', 'pending')
            
            response_text = f"✅ **Player '{player_name}' created successfully**\n\n"
            response_text += f"🆔 Player ID: {player_id}\n"
            response_text += f"📞 Phone: {phone_number}\n"
            response_text += f"📊 Status: {status_text}\n"
            if invite_link != 'N/A':
                response_text += f"🔗 Invite Link: {invite_link}"
            
            return response_text
        else:
            return f"❌ Failed to create player '{player_name}'. Please try again."
        
    except Exception as e:
        return f"❌ Failed to create player '{player_name}': {str(e)}"


@tool("update_member_role")
async def update_member_role(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    member_identifier: str,
    new_role: str
) -> str:
    """Update a team member's role (leadership/admin function).
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        member_identifier: Member ID, name, or phone to identify member
        new_role: New role to assign (player, captain, coach, admin)
    
    Returns:
        Formatted role update result
    """
    try:
        container = get_container()
        
        # Get team member service
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
            team_service = container.get_service(ITeamMemberService)
        except Exception:
            return "❌ Team service is not available"
        
        # Permission check - only leadership can update roles
        if chat_type not in ["leadership", "private"]:
            return "❌ Insufficient permissions. Leadership access required."
        
        # Validate inputs
        if not member_identifier or not member_identifier.strip():
            return "❌ Member identifier is required"
            
        if not new_role or not new_role.strip():
            return "❌ New role is required"
        
        # Valid roles
        valid_roles = ["player", "captain", "coach", "admin", "leadership"]
        if new_role.lower() not in valid_roles:
            return f"❌ Invalid role. Valid roles: {', '.join(valid_roles)}"
        
        # Update the member role
        result = await team_service.update_member_role(
            team_id=team_id,
            member_identifier=member_identifier,
            new_role=new_role.lower(),
            updated_by_telegram_id=telegram_id
        )
        
        if result:
            return f"✅ Member '{member_identifier}' role updated to '{new_role}' successfully"
        else:
            return f"❌ Failed to update role for member '{member_identifier}'. Member may not exist."
        
    except Exception as e:
        return f"❌ Failed to update member role: {str(e)}"


@tool("remove_team_member")
async def remove_team_member(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    member_identifier: str,
    reason: str = "Administrative removal"
) -> str:
    """Remove a team member (leadership/admin function).
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        member_identifier: Member ID, name, or phone to identify member
        reason: Reason for removal (optional)
    
    Returns:
        Formatted member removal result
    """
    try:
        container = get_container()
        
        # Get team member service
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
            team_service = container.get_service(ITeamMemberService)
        except Exception:
            return "❌ Team service is not available"
        
        # Permission check - only leadership can remove members
        if chat_type not in ["leadership", "private"]:
            return "❌ Insufficient permissions. Leadership access required."
        
        # Validate inputs
        if not member_identifier or not member_identifier.strip():
            return "❌ Member identifier is required"
        
        # Remove the member
        result = await team_service.remove_team_member(
            team_id=team_id,
            member_identifier=member_identifier,
            removed_by_telegram_id=telegram_id,
            reason=reason
        )
        
        if result:
            return f"✅ Team member '{member_identifier}' removed successfully\n📝 Reason: {reason}"
        else:
            return f"❌ Failed to remove team member '{member_identifier}'. Member may not exist."
        
    except Exception as e:
        return f"❌ Failed to remove team member: {str(e)}"


@tool("list_members_and_players")
async def list_members_and_players(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    include_players: bool = True,
    status_filter: str = "all"
) -> str:
    """List all team members and optionally players.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        include_players: Whether to include players in the list
        status_filter: Filter by status ('all', 'active', 'pending', 'inactive')
    
    Returns:
        Formatted list of all team members and players
    """
    try:
        container = get_container()
        
        # Get services
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
            team_service = container.get_service(ITeamMemberService)
            
            if include_players:
                from kickai.features.player_registration.domain.interfaces.player_service_interface import IPlayerService
                player_service = container.get_service(IPlayerService)
        except Exception:
            return "❌ Required services are not available"
        
        all_members = []
        
        # Get team members
        try:
            team_members = await team_service.get_team_members_by_team(team_id)
            for member in team_members:
                if status_filter == "all" or getattr(member, 'status', 'active') == status_filter:
                    all_members.append({
                        "type": "team_member",
                        "name": member.name or "Unknown Member",
                        "role": getattr(member, 'role', 'member'),
                        "status": getattr(member, 'status', 'active'),
                        "phone": getattr(member, 'phone', ''),
                        "telegram_id": getattr(member, 'telegram_id', 'N/A')
                    })
        except Exception:
            pass
        
        # Get players if requested
        if include_players:
            try:
                players = await player_service.get_all_players(team_id)
                for player in players:
                    if status_filter == "all" or getattr(player, 'status', 'active') == status_filter:
                        all_members.append({
                            "type": "player",
                            "name": player.name or "Unknown Player",
                            "role": "Player",
                            "status": getattr(player, 'status', 'active'),
                            "phone": getattr(player, 'phone_number', ''),
                            "telegram_id": getattr(player, 'telegram_id', 'N/A')
                        })
            except Exception:
                pass
        
        if not all_members:
            return f"📋 No {'team members or players' if include_players else 'team members'} found (filter: {status_filter})"
        
        # Sort by name (handle None names)
        all_members.sort(key=lambda x: (x["name"] or "").lower())
        
        # Format as clean text
        member_type = "Team Members & Players" if include_players else "Team Members"
        list_text = f"👥 **{member_type}** ({len(all_members)} total)\n"
        list_text += f"Filter: {status_filter}\n\n"
        
        for i, member in enumerate(all_members, 1):
            emoji = "👤" if member["type"] == "team_member" else "⚽"
            list_text += f"{i}. {emoji} {member['name']}\n"
            list_text += f"   📋 Role: {member['role']}\n"
            list_text += f"   📊 Status: {member['status']}\n"
            if member['phone']:
                list_text += f"   📞 Phone: {member['phone']}\n"
            if member['telegram_id'] != 'N/A':
                list_text += f"   📱 Telegram: {member['telegram_id']}\n"
            list_text += "\n"
        
        return list_text.strip()
        
    except Exception as e:
        return f"❌ Failed to list team members: {str(e)}"


@tool("get_member_info")
async def get_member_info(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    member_identifier: str
) -> str:
    """Get detailed information about a specific team member.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        member_identifier: Member ID, name, or phone to identify member
    
    Returns:
        Formatted member details
    """
    try:
        container = get_container()
        
        # Get services
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
            team_service = container.get_service(ITeamMemberService)
        except Exception:
            return "❌ Team service is not available"
        
        # Validate inputs
        if not member_identifier or not member_identifier.strip():
            return "❌ Member identifier is required"
        
        # Get member details
        member = await team_service.get_member_details(team_id, member_identifier)
        
        if not member:
            return f"❌ Team member '{member_identifier}' not found"
        
        # Format member details as clean text
        details_text = f"👤 **{member.name}** - Team Member Details\n\n"
        details_text += f"🆔 ID: {getattr(member, 'member_id', 'N/A')}\n"
        details_text += f"📞 Phone: {getattr(member, 'phone', 'N/A')}\n"
        details_text += f"📋 Role: {getattr(member, 'role', 'member')}\n"
        details_text += f"📊 Status: {getattr(member, 'status', 'active')}\n"
        details_text += f"📱 Telegram: {getattr(member, 'telegram_id', 'N/A')}\n"
        details_text += f"📅 Joined: {getattr(member, 'registration_date', 'N/A')}\n"
        if hasattr(member, 'last_activity'):
            details_text += f"🔄 Last Activity: {member.last_activity}"
        
        return details_text
        
    except Exception as e:
        return f"❌ Failed to get member details: {str(e)}"


@tool("get_member_current")
async def get_member_current(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str
) -> str:
    """Get current member information for the requesting user.
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
    
    Returns:
        Formatted current member information
    """
    try:
        container = get_container()
        
        # Get team member service
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
            team_service = container.get_service(ITeamMemberService)
        except Exception:
            return "❌ Team service is not available"
        
        # Get current member by telegram_id
        try:
            member = await team_service.get_team_member_by_telegram_id(telegram_id, team_id)
            if not member:
                return "❌ You are not registered as a team member"
        except Exception as e:
            return f"❌ Failed to retrieve your member information: {str(e)}"
        
        # Format current member info as clean text
        info_text = f"👤 **{member.name}** - Your Member Information\n\n"
        info_text += f"🆔 ID: {getattr(member, 'member_id', 'N/A')}\n"
        info_text += f"📞 Phone: {getattr(member, 'phone', 'N/A')}\n"
        info_text += f"📋 Role: {getattr(member, 'role', 'member')}\n"
        info_text += f"📊 Status: {getattr(member, 'status', 'active')}\n"
        info_text += f"📱 Telegram: {telegram_id}\n"
        info_text += f"📅 Joined: {getattr(member, 'registration_date', 'N/A')}\n"
        if hasattr(member, 'last_activity'):
            info_text += f"🔄 Last Activity: {member.last_activity}"
        
        return info_text
        
    except Exception as e:
        return f"❌ Failed to get current member info: {str(e)}"


@tool("update_member_other")
async def update_member_other(
    telegram_id: int,
    team_id: str,
    username: str,
    chat_type: str,
    member_identifier: str,
    field_name: str,
    field_value: str
) -> str:
    """Update another member's information (leadership/admin function).
    
    Args:
        telegram_id: User's Telegram ID
        team_id: Team identifier
        username: User's username
        chat_type: Chat context (main/leadership/private)
        member_identifier: Member ID, name, or phone to identify member
        field_name: Field to update (name, phone, role, status)
        field_value: New value for the field
    
    Returns:
        Formatted member update result
    """
    try:
        container = get_container()
        
        # Get team member service
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import ITeamMemberService
            team_service = container.get_service(ITeamMemberService)
        except Exception:
            return "❌ Team service is not available"
        
        # Permission check - only leadership can update other members
        if chat_type not in ["leadership", "private"]:
            return "❌ Insufficient permissions. Leadership access required."
        
        # Validate inputs
        if not member_identifier or not member_identifier.strip():
            return "❌ Member identifier is required"
            
        if not field_name or not field_name.strip():
            return "❌ Field name is required"
            
        if not field_value or not field_value.strip():
            return "❌ Field value is required"
        
        # Valid fields
        valid_fields = ["name", "phone", "role", "status", "position"]
        if field_name.lower() not in valid_fields:
            return f"❌ Invalid field. Valid fields: {', '.join(valid_fields)}"
        
        # Update the member field
        try:
            result = await team_service.update_member_field(
                team_id=team_id,
                member_identifier=member_identifier,
                field_name=field_name.lower(),
                field_value=field_value,
                updated_by_telegram_id=telegram_id
            )
            
            if result:
                return f"✅ Member '{member_identifier}' {field_name} updated to '{field_value}' successfully"
            else:
                return f"❌ Failed to update {field_name} for member '{member_identifier}'. Member may not exist."
                
        except Exception as e:
            return f"❌ Failed to update member field: {str(e)}"
        
    except Exception as e:
        return f"❌ Failed to update member: {str(e)}"