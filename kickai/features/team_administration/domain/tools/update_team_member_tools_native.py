#!/usr/bin/env python3
"""
Team Member Update Tools - Native CrewAI Implementation

This module provides tools for updating team member information using ONLY CrewAI native patterns.
"""

import re
from datetime import datetime

from crewai.tools import tool
from loguru import logger

from kickai.core.constants import get_team_members_collection
from kickai.core.dependency_container import get_container
from kickai.database.firebase_client import FirebaseClient


@tool("update_team_member_information")
def update_team_member_information(
    telegram_id: int,
    team_id: str,
    field: str,
    value: str,
    username: str
) -> str:
    """
    Update specific team member information field.

    :param telegram_id: Telegram user ID of the team member
    :type telegram_id: str
    :param team_id: Team ID for context
    :type team_id: str
    :param field: Field name to update (phone, email, emergency_contact, role)
    :type field: str
    :param value: New value for the field
    :type value: str
    :param username: Username of the person making the update
    :type username: str
    :return: Update status message
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not telegram_id:
        return "❌ Telegram ID is required to update team member information."

    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to update team member information."

    if not field or field.strip() == "":
        return "❌ Field name is required to update team member information."

    if not value or value.strip() == "":
        return "❌ Field value is required to update team member information."

    try:
        # Get service using simple container access
        container = get_container()
        firebase_service = container.get_service(FirebaseClient)

        if not firebase_service:
            return "❌ Firebase service is temporarily unavailable. Please try again later."

        collection_name = get_team_members_collection(team_id)

        # Check if team member exists
        members = firebase_service.query_documents(collection_name, [("telegram_id", "==", str(telegram_id))])

        if not members:
            return "❌ You are not registered as a team member. Use /register to register first."

        member = members[0]
        member_id = member.get("id", "unknown")
        member_name = member.get("name", "Unknown Member")

        # Valid updatable fields
        valid_fields = ["phone", "email", "emergency_contact", "role"]
        if field.lower() not in valid_fields:
            return f"❌ Invalid field '{field}'. Valid fields: {', '.join(valid_fields)}"

        # Fields that require admin approval
        admin_approval_fields = ["role"]
        requires_approval = field.lower() in admin_approval_fields

        # Simple validation based on field type
        validated_value = value.strip()

        if field.lower() == "phone":
            # Basic phone validation
            if not re.match(r'^[\+]?[\d\s\-\(\)]{10,15}$', validated_value):
                return "❌ Invalid phone number format. Please use a valid format like +447123456789 or 07123456789."

            # Check for duplicates
            existing_members = firebase_service.query_documents(
                collection_name, [("phone", "==", validated_value)]
            )
            duplicate_members = [m for m in existing_members if m.get("telegram_id") != telegram_id]

            if duplicate_members:
                duplicate_name = duplicate_members[0].get("name", "Unknown")
                return f"❌ Phone number {validated_value} is already registered to another team member ({duplicate_name})."

        elif field.lower() == "email":
            # Basic email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', validated_value):
                return "❌ Invalid email format. Please provide a valid email address."
            validated_value = validated_value.lower()

        elif field.lower() == "emergency_contact":
            if len(validated_value) < 5 or len(validated_value) > 200:
                return "❌ Emergency contact must be between 5 and 200 characters long."

        elif field.lower() == "role":
            # Valid roles
            valid_roles = [
                "team manager", "coach", "assistant coach", "head coach", "club administrator",
                "treasurer", "secretary", "volunteer coordinator", "volunteer", "parent helper",
                "first aid coordinator", "equipment manager", "transport coordinator"
            ]
            if validated_value.lower() not in valid_roles:
                return f"❌ Invalid role '{validated_value}'. Valid roles include: {', '.join(valid_roles[:5])}..."

        current_time = datetime.now().isoformat()
        old_value = member.get(field, "Not set")

        if requires_approval:
            # Create approval request instead of direct update
            approval_data = {
                "request_type": "field_update",
                "telegram_id": telegram_id,
                "member_id": member_id,
                "member_name": member_name,
                "team_id": team_id,
                "field": field,
                "old_value": old_value,
                "new_value": validated_value,
                "requested_by": username if username else "Unknown",
                "requested_at": current_time,
                "status": "pending",
                "approved_by": None,
                "approved_at": None,
            }

            # Store approval request
            firebase_service.create_document(f"kickai_{team_id}_approval_requests", approval_data)

            result = "⏳ Role Change Request Submitted\\n\\n"
            result += f"📋 Requested Change: {field} → {validated_value}\\n"
            result += f"👤 Requested By: {username if username else 'Unknown'}\\n"
            result += f"📅 Requested: {datetime.fromisoformat(current_time).strftime('%d %b %Y at %H:%M')}\\n\\n"
            result += "🔒 This change requires admin approval.\\n"
            result += "📧 You'll be notified when the request is processed.\\n\\n"
            result += "💡 Contact a team admin to expedite the approval."

            return result
        else:
            # Direct update for non-approval fields
            update_data = {
                field: validated_value,
                "updated_at": current_time,
                "updated_by": username if username else "Unknown",
                f"{field}_updated_at": current_time,
                f"{field}_previous_value": old_value,
            }

            # Update team member record
            firebase_service.update_document(collection_name, member_id, update_data)

            result = "✅ Information Updated Successfully!\\n\\n"
            result += f"📋 Team Member: {member_name}\\n"
            result += f"🔄 Updated Field: {field}\\n"
            result += f"🆕 New Value: {validated_value}\\n"
            result += f"🕐 Updated: {datetime.fromisoformat(current_time).strftime('%d %b %Y at %H:%M')}\\n"
            result += f"👤 Updated By: {username if username else 'Unknown'}\\n\\n"
            result += "💡 Use /myinfo to view your complete updated information."

            return result

    except Exception as e:
        logger.error(f"Failed to update team member information: {e}")
        return f"❌ Failed to update team member information: {e!s}"


@tool("get_team_member_updatable_fields")
def get_team_member_updatable_fields(telegram_id: int, team_id: str) -> str:
    """
    Get list of fields that a team member can update.

    :param telegram_id: Telegram user ID of the team member
    :type telegram_id: str
    :param team_id: Team ID for context
    :type team_id: str
    :return: List of updatable fields with descriptions and examples
    :rtype: str
    """
        # Native CrewAI pattern - simple parameter validation
    if not telegram_id:
        return "❌ Telegram ID is required to get updatable fields."
    
    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get updatable fields."

    try:
        # Check if team member exists
        container = get_container()
        firebase_service = container.get_service(FirebaseClient)

        if not firebase_service:
            return "❌ Firebase service is temporarily unavailable. Please try again later."

        collection_name = get_team_members_collection(team_id)
        members = firebase_service.query_documents(collection_name, [("telegram_id", "==", str(telegram_id))])

        if not members:
            return "❌ You are not registered as a team member. Use /register to register first."

        member = members[0]
        member_name = member.get("name", "Unknown Member")
        current_role = member.get("role", "Not set")

        # Format as simple string response
        result = "✅ Team Member Information Update\\n\\n"
        result += f"👤 {member_name} (Current Role: {current_role})\\n\\n"
        result += "📋 Available Fields to Update:\\n\\n"

        result += "📱 phone - Your contact phone number\\n"
        result += "   Example: /update phone 07123456789\\n"
        result += "   Format: UK numbers (+44 or 07xxx format)\\n\\n"

        result += "📧 email - Your email address\\n"
        result += "   Example: /update email admin@example.com\\n"
        result += "   Format: Valid email address\\n\\n"

        result += "🚨 emergency_contact - Emergency contact info\\n"
        result += "   Example: /update emergency_contact +44787654321\\n"
        result += "   Format: Phone number or contact details\\n\\n"

        result += "👔 role - Your administrative role ⚠️ ADMIN APPROVAL REQUIRED\\n"
        result += "   Example: /update role Assistant Coach\\n"
        result += "   Valid: team manager, coach, assistant coach, head coach...\\n\\n"

        result += "📝 Usage: /update [field] [new value]\\n\\n"
        result += "🔒 Security:\\n"
        result += "• You can update your own contact information immediately\\n"
        result += "• Role changes require admin approval and will be pending\\n"
        result += "• All changes are logged for audit purposes\\n"
        result += "• Phone numbers must be unique within the team\\n\\n"
        result += "💡 Use /myinfo to view your current information before updating."

        return result

    except Exception as e:
        logger.error(f"Failed to get updatable fields: {e}")
        return f"❌ Failed to get updatable fields: {e!s}"


@tool("get_pending_team_member_approval_requests")
def get_pending_team_member_approval_requests(team_id: str, telegram_id: str = "") -> str:
    """
    Get pending approval requests for team member updates.

    :param team_id: Team ID for context
    :type team_id: str
    :param telegram_id: Optional Telegram user ID to filter requests for specific user
    :type telegram_id: str
    :return: List of pending approval requests
    :rtype: str
    """
    # Native CrewAI pattern - simple parameter validation
    if not team_id or team_id.strip() == "":
        return "❌ Team ID is required to get approval requests."

    try:
        container = get_container()
        firebase_service = container.get_service(FirebaseClient)

        if not firebase_service:
            return "❌ Firebase service is temporarily unavailable. Please try again later."

        # Build query filters
        filters = [("status", "==", "pending"), ("request_type", "==", "field_update")]
        if telegram_id and telegram_id.strip() != "":
            filters.append(("telegram_id", "==", telegram_id.strip()))

        # Get pending requests
        requests = firebase_service.query_documents(f"kickai_{team_id}_approval_requests", filters)

        if not requests:
            if telegram_id and telegram_id.strip() != "":
                return "✅ No pending approval requests for your account."
            else:
                return "✅ No pending approval requests."

        # Format response
        result = "⏳ Pending Approval Requests\\n\\n"

        for req in requests:
            request_time = datetime.fromisoformat(req["requested_at"]).strftime("%d %b %Y at %H:%M")

            if telegram_id and telegram_id.strip() != "":
                # Single user view
                result += f"• {req['field']}: {req['old_value']} → {req['new_value']}\\n"
                result += f"  Requested: {request_time}\\n\\n"
            else:
                # Admin view - all pending requests
                result += f"• {req['member_name']}: {req['field']} → {req['new_value']}\\n"
                result += f"  Requested: {request_time}\\n\\n"

        if telegram_id and telegram_id.strip() != "":
            result += "🔒 These requests require admin approval.\\n"
            result += "📧 You'll be notified when processed.\\n"
            result += "💡 Contact a team admin for status updates."
        else:
            result += "🔧 Admin Action Required:\\n"
            result += "Use team admin tools to approve or reject these requests.\\n\\n"
            result += f"📊 Total Requests: {len(requests)}"

        return result

    except Exception as e:
        logger.error(f"Failed to get approval requests: {e}")
        return f"❌ Failed to get approval requests: {e!s}"
