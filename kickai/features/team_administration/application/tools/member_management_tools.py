"""Team Member Management Tools - Clean Architecture Compliant

This module contains CrewAI tools for team member management operations.
These tools follow the clean naming convention and Clean Architecture principles.
All framework dependencies are confined to this application layer.
"""

from crewai.tools import tool
from loguru import logger

from kickai.core.dependency_container import get_container


@tool("create_player")
async def create_player(
    telegram_id: str,
    team_id: str,
    telegram_username: str,
    chat_type: str,
    player_name: str,
    phone_number: str,
) -> str:
    """
    Register new player in team roster.

    Establishes player profile with contact information and position
    assignment, initiating the verification and approval workflow.

    Use when: New team member joins as player
    Required: Leadership or administrative privileges
    Context: Player onboarding process

    Returns: Player registration confirmation
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"
        if not player_name.strip():
            return "❌ player_name is required"
        if not phone_number.strip():
            return "❌ phone_number is required"

        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        # Permission check - only leadership can create players
        if chat_type not in ["leadership", "private"]:
            return "❌ Insufficient permissions. Leadership access required."

        container = get_container()

        # Get team member service
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
                ITeamMemberService,
            )

            team_service = container.get_service(ITeamMemberService)
            if not team_service:
                return "❌ Team service is not available"
        except Exception:
            return "❌ Team service is not available"

        # Create the player
        result = await team_service.create_player_registration(
            team_id=team_id,
            name=player_name,
            phone=phone_number,
            created_by_telegram_id=telegram_id_int,
        )

        if result:
            invite_link = result.get("invite_link", "N/A")
            player_id = result.get("player_id", "N/A")
            status_text = result.get("status", "pending")

            response_text = f"✅ Player '{player_name}' created successfully\n\n"
            response_text += f"🆔 Player ID: {player_id}\n"
            response_text += f"📞 Phone: {phone_number}\n"
            response_text += f"📊 Status: {status_text}\n"
            if invite_link != "N/A":
                response_text += f"🔗 Invite Link: {invite_link}"

            return response_text
        else:
            return f"❌ Failed to create player '{player_name}'. Please try again."

    except Exception as e:
        logger.error(f"❌ Error creating player: {e}")
        return f"❌ Failed to create player '{player_name}': {e!s}"


@tool("update_member_role")
async def update_member_role(
    telegram_id: str,
    team_id: str,
    telegram_username: str,
    chat_type: str,
    member_identifier: str,
    new_role: str,
) -> str:
    """
    Modify team member's organizational role assignment.

    Updates member's responsibilities and permissions within the team
    hierarchy, affecting their access rights and operational duties.

    Use when: Role changes or promotions are required
    Required: Leadership or administrative privileges
    Context: Team governance workflow

    Returns: Role modification confirmation
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"
        if not member_identifier.strip():
            return "❌ member_identifier is required"
        if not new_role.strip():
            return "❌ new_role is required"

        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        # Permission check - only leadership can update roles
        if chat_type not in ["leadership", "private"]:
            return "❌ Insufficient permissions. Leadership access required."

        # Valid roles
        valid_roles = ["player", "captain", "coach", "admin", "leadership"]
        if new_role.lower() not in valid_roles:
            return f"❌ Invalid role. Valid roles: {', '.join(valid_roles)}"

        container = get_container()

        # Get team member service
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
                ITeamMemberService,
            )

            team_service = container.get_service(ITeamMemberService)
            if not team_service:
                return "❌ Team service is not available"
        except Exception:
            return "❌ Team service is not available"

        # Update the member role
        result = await team_service.update_member_role(
            team_id=team_id,
            member_identifier=member_identifier,
            new_role=new_role.lower(),
            updated_by_telegram_id=telegram_id_int,
        )

        if result:
            return f"✅ Member '{member_identifier}' role updated to '{new_role}' successfully"
        else:
            return (
                f"❌ Failed to update role for member '{member_identifier}'. Member may not exist."
            )

    except Exception as e:
        logger.error(f"❌ Error updating member role: {e}")
        return f"❌ Failed to update member role: {e!s}"


@tool("remove_team_member")
async def remove_team_member(
    telegram_id: str,
    team_id: str,
    telegram_username: str,
    chat_type: str,
    member_identifier: str,
    reason: str = "Administrative removal",
) -> str:
    """
    Terminate team member's organizational participation.

    Removes member from active roster and revokes all associated
    permissions, access rights, and participation privileges.

    Use when: Member departure or disciplinary action is required
    Required: Leadership or administrative privileges
    Context: Team governance workflow

    Returns: Member removal confirmation
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"
        if not member_identifier.strip():
            return "❌ member_identifier is required"

        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        # Permission check - only leadership can remove members
        if chat_type not in ["leadership", "private"]:
            return "❌ Insufficient permissions. Leadership access required."

        container = get_container()

        # Get team member service
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
                ITeamMemberService,
            )

            team_service = container.get_service(ITeamMemberService)
            if not team_service:
                return "❌ Team service is not available"
        except Exception:
            return "❌ Team service is not available"

        # Remove the member
        result = await team_service.remove_team_member(
            team_id=team_id,
            member_identifier=member_identifier,
            removed_by_telegram_id=telegram_id_int,
            reason=reason,
        )

        if result:
            return f"✅ Team member '{member_identifier}' removed successfully\n📝 Reason: {reason}"
        else:
            return f"❌ Failed to remove team member '{member_identifier}'. Member may not exist."

    except Exception as e:
        logger.error(f"❌ Error removing team member: {e}")
        return f"❌ Failed to remove team member: {e!s}"


@tool("list_members_and_players")
async def list_members_and_players(
    telegram_id: str,
    team_id: str,
    telegram_username: str,
    chat_type: str,
    include_players: bool = True,
    status_filter: str = "all",
) -> str:
    """
    Retrieve comprehensive team roster with members and players.

    Provides complete organizational overview including administrative
    members and game participants with their roles and status information.

    Use when: Complete team roster review is needed
    Required: Team access or administrative privileges
    Context: Team overview workflow

    Returns: Complete team roster summary
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"

        # Convert telegram_id to int for logging
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        container = get_container()

        # Get services
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
                ITeamMemberService,
            )

            team_service = container.get_service(ITeamMemberService)

            if include_players:
                from kickai.features.player_registration.domain.interfaces.player_service_interface import (
                    IPlayerService,
                )

                player_service = container.get_service(IPlayerService)
        except Exception:
            return "❌ Required services are not available"

        all_members = []

        # Get team members
        try:
            team_members = await team_service.get_team_members_by_team(team_id)
            for member in team_members:
                if status_filter == "all" or getattr(member, "status", "active") == status_filter:
                    all_members.append(
                        {
                            "type": "team_member",
                            "name": member.name or "Unknown Member",
                            "role": getattr(member, "role", "member"),
                            "status": getattr(member, "status", "active"),
                            "phone": getattr(member, "phone", ""),
                            "telegram_id": getattr(member, "telegram_id", "N/A"),
                        }
                    )
        except Exception:
            pass

        # Get players if requested
        if include_players:
            try:
                players = await player_service.get_all_players(team_id)
                for player in players:
                    if (
                        status_filter == "all"
                        or getattr(player, "status", "active") == status_filter
                    ):
                        all_members.append(
                            {
                                "type": "player",
                                "name": player.name or "Unknown Player",
                                "role": "Player",
                                "status": getattr(player, "status", "active"),
                                "phone": getattr(player, "phone_number", ""),
                                "telegram_id": getattr(player, "telegram_id", "N/A"),
                            }
                        )
            except Exception:
                pass

        if not all_members:
            return f"📋 No {'team members or players' if include_players else 'team members'} found (filter: {status_filter})"

        # Sort by name (handle None names)
        all_members.sort(key=lambda x: (x["name"] or "").lower())

        # Format as clean text
        member_type = "Team Members & Players" if include_players else "Team Members"
        list_text = f"👥 {member_type} ({len(all_members)} total)\n"
        list_text += f"Filter: {status_filter}\n\n"

        for i, member in enumerate(all_members, 1):
            emoji = "👤" if member["type"] == "team_member" else "⚽"
            list_text += f"{i}. {emoji} {member['name']}\n"
            list_text += f"   📋 Role: {member['role']}\n"
            list_text += f"   📊 Status: {member['status']}\n"
            if member["phone"]:
                list_text += f"   📞 Phone: {member['phone']}\n"
            if member["telegram_id"] != "N/A":
                list_text += f"   📱 Telegram: {member['telegram_id']}\n"
            list_text += "\n"

        return list_text.strip()

    except Exception as e:
        logger.error(f"❌ Error listing team members: {e}")
        return f"❌ Failed to list team members: {e!s}"


@tool("get_member_status")
async def get_member_status(
    telegram_id: str,
    team_id: str,
    member_identifier: str,
    telegram_username: str = "user",
    chat_type: str = "main",
) -> str:
    """
    Retrieve specific member's status and administrative details.

    Provides detailed information about designated team member including
    roles, permissions, contact details, and current participation status.

    Use when: Individual member information lookup is required
    Required: Team access or administrative privileges
    Context: Member information workflow

    Returns: Member status and administrative details
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"
        if not member_identifier.strip():
            return "❌ member_identifier is required"

        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        logger.info(
            f"🔍 Member info request for '{member_identifier}' from {telegram_username} ({telegram_id_int}) in team {team_id}"
        )

        container = get_container()

        # Get services
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
                ITeamMemberService,
            )

            team_service = container.get_service(ITeamMemberService)
            if not team_service:
                return "❌ Team service is not available"
        except Exception:
            return "❌ Team service is not available"

        # Try to find member by different identifiers
        member = None

        # First, try to find by member_id (if it looks like an ID)
        if member_identifier.isalnum() and len(member_identifier) <= 20:
            try:
                member = await team_service.get_team_member_by_id(member_identifier, team_id)
            except Exception:
                pass

        # If not found by ID, try by phone number
        if (
            not member
            and member_identifier.replace("+", "").replace("-", "").replace(" ", "").isdigit()
        ):
            try:
                member = await team_service.get_team_member_by_phone(member_identifier, team_id)
            except Exception:
                pass

        # If still not found, search through all team members by name or username
        if not member:
            try:
                all_members = await team_service.get_team_members_by_team(team_id)
                for m in all_members:
                    if (
                        member_identifier.lower() in (m.name or "").lower()
                        or member_identifier.lower() in (getattr(m, "username", "") or "").lower()
                    ):
                        member = m
                        break
            except Exception:
                pass

        if not member:
            return f"❌ Team member '{member_identifier}' not found"

        # Format member details as clean text
        details_text = f"👤 {member.name or 'Unknown'} - Team Member Details\n\n"
        details_text += f"🆔 ID: {getattr(member, 'member_id', 'N/A')}\n"
        details_text += f"📞 Phone: {getattr(member, 'phone', 'N/A')}\n"
        details_text += f"📋 Role: {getattr(member, 'role', 'member')}\n"
        details_text += f"📊 Status: {getattr(member, 'status', 'active')}\n"
        details_text += f"📱 Telegram: {getattr(member, 'telegram_id', 'N/A')}\n"
        details_text += f"📅 Joined: {getattr(member, 'created_at', 'N/A')}\n"
        if hasattr(member, "updated_at") and member.updated_at:
            details_text += f"🔄 Last Updated: {member.updated_at}\n"

        logger.info(f"✅ Retrieved member info for {member.name or 'Unknown'}")
        return details_text

    except Exception as e:
        logger.error(f"❌ Failed to get member details: {e}")
        return f"❌ Failed to get member details: {e!s}"


@tool("update_member_by_identifier")
async def update_member_by_identifier(
    telegram_id: str,
    team_id: str,
    telegram_username: str,
    chat_type: str,
    member_identifier: str,
    field_name: str,
    field_value: str,
) -> str:
    """
    Modify designated member's profile information.

    Updates specified member's contact details, role assignments, or
    administrative information using leadership authority.

    Use when: Administrative member profile updates are required
    Required: Leadership or administrative privileges
    Context: Administrative member management workflow

    Returns: Member profile update confirmation
    """
    try:
        # Only validate required parameters for this tool
        if not telegram_id.strip():
            return "❌ telegram_id is required"
        if not team_id.strip():
            return "❌ team_id is required"
        if not member_identifier.strip():
            return "❌ member_identifier is required"
        if not field_name.strip():
            return "❌ field_name is required"
        if not field_value.strip():
            return "❌ field_value is required"

        # Convert telegram_id to int for service calls
        try:
            telegram_id_int = int(telegram_id)
        except (ValueError, TypeError):
            return "❌ Invalid telegram_id format"

        # Permission check - only leadership can update other members
        if chat_type not in ["leadership", "private"]:
            return "❌ Insufficient permissions. Leadership access required."

        # Valid fields
        valid_fields = ["name", "phone", "role", "status", "position"]
        if field_name.lower() not in valid_fields:
            return f"❌ Invalid field. Valid fields: {', '.join(valid_fields)}"

        container = get_container()

        # Get team member service
        try:
            from kickai.features.team_administration.domain.interfaces.team_member_service_interface import (
                ITeamMemberService,
            )

            team_service = container.get_service(ITeamMemberService)
            if not team_service:
                return "❌ Team service is not available"
        except Exception:
            return "❌ Team service is not available"

        # Update the member field
        try:
            result = await team_service.update_member_field(
                team_id=team_id,
                member_identifier=member_identifier,
                field_name=field_name.lower(),
                field_value=field_value,
                updated_by_telegram_id=telegram_id_int,
            )

            if result:
                return f"✅ Member '{member_identifier}' {field_name} updated to '{field_value}' successfully"
            else:
                return f"❌ Failed to update {field_name} for member '{member_identifier}'. Member may not exist."

        except Exception as e:
            logger.error(f"❌ Error updating member field: {e}")
            return f"❌ Failed to update member field: {e!s}"

    except Exception as e:
        logger.error(f"❌ Error updating member: {e}")
        return f"❌ Failed to update member: {e!s}"
