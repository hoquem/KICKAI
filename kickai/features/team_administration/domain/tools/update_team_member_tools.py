#!/usr/bin/env python3
"""
Team Member Update Tools

This module provides tools for updating team member information with validation
and approval workflows.
"""

import re
from datetime import datetime

from loguru import logger

from kickai.core.constants import get_team_members_collection
from kickai.core.dependency_container import get_container
from kickai.database.firebase_client import FirebaseClient
from kickai.utils.crewai_tool_decorator import tool


class TeamMemberUpdateValidationError(Exception):
    """Exception raised for team member update validation errors."""

    pass


class TeamMemberUpdateValidator:
    """Validator for team member information updates."""

    # Valid roles for team members
    VALID_ROLES = [
        "team manager",
        "coach",
        "assistant coach",
        "head coach",
        "club administrator",
        "treasurer",
        "secretary",
        "volunteer coordinator",
        "volunteer",
        "parent helper",
        "first aid coordinator",
        "equipment manager",
        "transport coordinator",
    ]

    # Fields that team members can update
    UPDATABLE_FIELDS = {
        "phone": "Contact phone number",
        "email": "Email address",
        "emergency_contact": "Emergency contact information",
        "role": "Administrative role (admin approval required)",
    }

    # Fields that cannot be updated by users
    PROTECTED_FIELDS = {
        "user_id",
        "team_id",
        "telegram_id",
        "status",
        "created_at",
        "source",
        "id",
        "name",
        "full_name",
        "approved_at",
        "approved_by",
    }

    # Fields that require admin approval
    ADMIN_APPROVAL_FIELDS = {"role"}

    @classmethod
    def validate_field_name(cls, field: str) -> bool:
        """Validate that the field name is updatable."""
        if field.lower() in cls.PROTECTED_FIELDS:
            raise TeamMemberUpdateValidationError(
                f"Field '{field}' cannot be updated by users. "
                f"Contact team administrator for changes to protected fields."
            )

        if field.lower() not in cls.UPDATABLE_FIELDS:
            available_fields = ", ".join(cls.UPDATABLE_FIELDS.keys())
            raise TeamMemberUpdateValidationError(
                f"Invalid field '{field}'. Available fields: {available_fields}"
            )

        return True

    @classmethod
    def requires_admin_approval(cls, field: str) -> bool:
        """Check if field requires admin approval."""
        return field.lower() in cls.ADMIN_APPROVAL_FIELDS

    @classmethod
    def validate_phone(cls, phone: str) -> str:
        """Validate and normalize UK phone number using phonenumbers library."""
        if not phone or not phone.strip():
            raise TeamMemberUpdateValidationError("Phone number cannot be empty")

        # Use the proper phone validation library
        from kickai.utils.phone_utils import is_valid_phone, normalize_phone

        if not is_valid_phone(phone.strip()):
            raise TeamMemberUpdateValidationError(
                f"Invalid phone number format. Please use UK format: "
                f"+44xxxxxxxxxx or 07xxxxxxxxx. Got: {phone}"
            )

        # Return normalized phone number
        normalized = normalize_phone(phone.strip())
        return normalized if normalized else phone.strip()

    @classmethod
    def validate_role(cls, role: str) -> str:
        """Validate team member role."""
        normalized_role = role.lower().strip()

        if normalized_role not in cls.VALID_ROLES:
            valid_roles = ", ".join(cls.VALID_ROLES)
            raise TeamMemberUpdateValidationError(
                f"Invalid role '{role}'. Valid roles: {valid_roles}"
            )

        # Return properly capitalized role
        return role.strip().title()

    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email address format."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, email.strip()):
            raise TeamMemberUpdateValidationError(
                f"Invalid email format. Please provide a valid email address. Got: {email}"
            )

        return email.strip().lower()

    @classmethod
    def validate_emergency_contact(cls, contact: str) -> str:
        """Validate emergency contact information."""
        if len(contact.strip()) < 5:
            raise TeamMemberUpdateValidationError(
                "Emergency contact must be at least 5 characters long"
            )

        if len(contact.strip()) > 200:
            raise TeamMemberUpdateValidationError(
                "Emergency contact must be less than 200 characters"
            )

        return contact.strip()

    @classmethod
    def validate_field_value(cls, field: str, value: str) -> str:
        """Validate field value based on field type."""
        field_lower = field.lower()

        if field_lower == "phone":
            return cls.validate_phone(value)
        elif field_lower == "role":
            return cls.validate_role(value)
        elif field_lower == "email":
            return cls.validate_email(value)
        elif field_lower == "emergency_contact":
            return cls.validate_emergency_contact(value)
        else:
            raise TeamMemberUpdateValidationError(f"Unknown field type: {field}")


@tool
def update_team_member_information(
    user_id: str, team_id: str, field: str, value: str, username: str = "Unknown"
) -> str:
    """
    Update specific team member information field with validation and audit logging.

    Args:
        user_id: Telegram user ID of the team member
        team_id: Team ID
        field: Field name to update (phone, email, emergency_contact, role)
        value: New value for the field
        username: Username of the person making the update

    Returns:
        Success or error message
    """
    try:
        logger.info(
            f"🔄 Team member update request: user_id={user_id}, team_id={team_id}, field={field}"
        )

        # Validate inputs
        if not user_id or not team_id or not field or not value:
            return "❌ Update Failed: Missing required parameters (user_id, team_id, field, value)"

        # Initialize Firebase service
        container = get_container()
        firebase_service = container.get_service(FirebaseClient)
        collection_name = get_team_members_collection(team_id)

        # Check if team member exists
        logger.info(f"🔍 Checking if team member exists: user_id={user_id}")
        members = firebase_service.query_documents(collection_name, [("user_id", "==", user_id)])

        if not members:
            logger.warning(f"❌ Team member not found: user_id={user_id}")
            return "❌ Update Failed: You are not registered as a team member. Use /register to register."

        member = members[0]
        member_id = member.get("id", "unknown")
        member_name = member.get("name", "Unknown Member")

        logger.info(f"✅ Found team member: {member_name} (ID: {member_id})")

        # Validate field name
        validator = TeamMemberUpdateValidator()
        validator.validate_field_name(field)

        # Validate and normalize field value
        validated_value = validator.validate_field_value(field, value)
        logger.info(f"✅ Field validation passed: {field} = {validated_value}")

        # Check if field requires admin approval
        requires_approval = validator.requires_admin_approval(field)

        # Check for duplicate phone numbers (if updating phone)
        if field.lower() == "phone":
            existing_members = firebase_service.query_documents(
                collection_name, [("phone", "==", validated_value)]
            )

            # Filter out the current member
            duplicate_members = [m for m in existing_members if m.get("user_id") != user_id]

            if duplicate_members:
                duplicate_name = duplicate_members[0].get("name", "Unknown")
                logger.warning(
                    f"❌ Duplicate phone number: {validated_value} already used by {duplicate_name}"
                )
                return f"❌ Update Failed: Phone number {validated_value} is already registered to another team member ({duplicate_name})"

        # Prepare update data
        current_time = datetime.now().isoformat()
        old_value = member.get(field, "Not set")

        if requires_approval:
            # Create approval request instead of direct update
            approval_data = {
                "request_type": "field_update",
                "user_id": user_id,
                "member_id": member_id,
                "member_name": member_name,
                "team_id": team_id,
                "field": field,
                "old_value": old_value,
                "new_value": validated_value,
                "requested_by": username,
                "requested_at": current_time,
                "status": "pending",
                "approved_by": None,
                "approved_at": None,
            }

            # Store approval request
            firebase_service.create_document(f"kickai_{team_id}_approval_requests", approval_data)

            logger.info(f"✅ Approval request created for {field} update")

            return f"""⏳ Role Change Request Submitted

📋 Requested Change: {field} → {validated_value}
👤 Requested By: {username}
📅 Requested: {datetime.fromisoformat(current_time).strftime("%d %b %Y at %H:%M")}

🔒 This change requires admin approval.
📧 You'll be notified when the request is processed.

💡 Contact a team admin to expedite the approval."""

        else:
            # Direct update for non-approval fields
            update_data = {
                field: validated_value,
                "updated_at": current_time,
                "updated_by": username,
                f"{field}_updated_at": current_time,
                f"{field}_previous_value": old_value,
            }

            # Update team member record
            firebase_service.update_document(collection_name, member_id, update_data)

            logger.info(
                f"✅ Team member information updated successfully: {field} = {validated_value}"
            )

        # Create audit log
        audit_data = {
            "action": "team_member_info_update"
            if not requires_approval
            else "team_member_update_request",
            "user_id": user_id,
            "member_id": member_id,
            "member_name": member_name,
            "team_id": team_id,
            "field": field,
            "old_value": old_value,
            "new_value": validated_value,
            "updated_by": username,
            "timestamp": current_time,
            "requires_approval": requires_approval,
            "source": "self_service_update",
        }

        try:
            firebase_service.create_document(f"kickai_{team_id}_audit_logs", audit_data)
            logger.info("✅ Audit log created for team member update")
        except Exception as e:
            logger.warning(f"⚠️ Failed to create audit log: {e}")

        # Return success message for direct updates
        if not requires_approval:
            field_description = validator.UPDATABLE_FIELDS.get(field, field)

            return f"""✅ Information Updated Successfully!

📋 Team Member: {member_name}
🔄 Updated Field: {field_description}
🆕 New Value: {validated_value}
🕐 Updated: {datetime.fromisoformat(current_time).strftime("%d %b %Y at %H:%M")}
👤 Updated By: {username}

💡 Use /myinfo to view your complete updated information."""

    except TeamMemberUpdateValidationError as e:
        logger.warning(f"❌ Validation error: {e}")
        return f"❌ Update Failed: {e!s}"

    except Exception as e:
        logger.error(f"❌ Error updating team member information: {e}", exc_info=True)
        return (
            "❌ Update Failed: An unexpected error occurred. Please try again or contact support."
        )


@tool
def get_team_member_updatable_fields(user_id: str, team_id: str) -> str:
    """
    Get list of fields that a team member can update with examples and validation rules.

    Args:
        user_id: Telegram user ID of the team member
        team_id: Team ID

    Returns:
        List of updatable fields with descriptions and examples
    """
    try:
        logger.info(f"📋 Getting updatable fields for team member: user_id={user_id}")

        # Check if team member exists
        container = get_container()
        firebase_service = container.get_service(FirebaseClient)
        collection_name = get_team_members_collection(team_id)

        members = firebase_service.query_documents(collection_name, [("user_id", "==", user_id)])

        if not members:
            return """❌ Update Not Available

🔍 You are not registered as a team member in this team.

📝 To register as a team member:
1. Use /register [name] [phone] [role]
2. Example: /register John Smith +447123456789 Assistant Coach
3. You'll be added to the team members collection

💡 Need help? Use /help to see available commands."""

        member = members[0]
        member_name = member.get("name", "Unknown Member")
        current_role = member.get("role", "Not set")

        # Get valid roles for reference
        roles = ", ".join(TeamMemberUpdateValidator.VALID_ROLES[:8]) + "..."

        return f"""✅ Team Member Information Update

👤 {member_name} (Current Role: {current_role})

📋 Available Fields to Update:

📱 **phone** - Your contact phone number
   Example: /update phone 07123456789
   Format: UK numbers (+44 or 07xxx format)

📧 **email** - Your email address
   Example: /update email admin@example.com
   Format: Valid email address

🚨 **emergency_contact** - Emergency contact info
   Example: /update emergency_contact +44787654321
   Format: Phone number or contact details

👔 **role** - Your administrative role ⚠️ ADMIN APPROVAL REQUIRED
   Example: /update role Assistant Coach
   Valid: {roles}

📝 Usage: /update [field] [new value]

🔒 Security:
• You can update your own contact information immediately
• Role changes require admin approval and will be pending
• All changes are logged for audit purposes
• Phone numbers must be unique within the team

💡 Use /myinfo to view your current information before updating."""

    except Exception as e:
        logger.error(f"❌ Error getting updatable fields: {e}", exc_info=True)
        return "❌ Error retrieving updatable fields. Please try again."


@tool
def validate_team_member_update_request(user_id: str, team_id: str, field: str, value: str) -> str:
    """
    Validate a team member update request without actually performing the update.

    Args:
        user_id: Telegram user ID of the team member
        team_id: Team ID
        field: Field name to validate
        value: Value to validate

    Returns:
        Validation result message
    """
    try:
        logger.info(f"🔍 Validating team member update: field={field}, value={value}")

        # Check if team member exists
        container = get_container()
        firebase_service = container.get_service(FirebaseClient)
        collection_name = get_team_members_collection(team_id)

        members = firebase_service.query_documents(collection_name, [("user_id", "==", user_id)])

        if not members:
            return "❌ Validation Failed: You are not registered as a team member"

        # Validate field and value
        validator = TeamMemberUpdateValidator()
        validator.validate_field_name(field)
        validated_value = validator.validate_field_value(field, value)
        requires_approval = validator.requires_admin_approval(field)

        # Check for duplicates if phone
        if field.lower() == "phone":
            existing_members = firebase_service.query_documents(
                collection_name, [("phone", "==", validated_value)]
            )

            duplicate_members = [m for m in existing_members if m.get("user_id") != user_id]

            if duplicate_members:
                return "❌ Validation Failed: Phone number already in use"

        field_description = validator.UPDATABLE_FIELDS.get(field, field)
        approval_note = " (requires admin approval)" if requires_approval else ""

        return f"""✅ Validation Successful

🔄 Field: {field_description}{approval_note}
🆕 Validated Value: {validated_value}
📋 Status: Ready to update

💡 Use /update {field} {validated_value} to apply this change."""

    except TeamMemberUpdateValidationError as e:
        return f"❌ Validation Failed: {e!s}"

    except Exception as e:
        logger.error(f"❌ Error validating update request: {e}")
        return "❌ Validation Error: Please check your input and try again"


@tool
def get_pending_team_member_approval_requests(team_id: str, user_id: str = None) -> str:
    """
    Get pending approval requests for team member updates.

    Args:
        team_id: Team ID
        user_id: Optional user ID to filter requests for specific user

    Returns:
        List of pending approval requests
    """
    try:
        logger.info(f"📋 Getting pending approval requests for team: {team_id}")

        container = get_container()
        firebase_service = container.get_service(FirebaseClient)

        # Build query filters
        filters = [("status", "==", "pending"), ("request_type", "==", "field_update")]
        if user_id:
            filters.append(("user_id", "==", user_id))

        # Get pending requests
        requests = firebase_service.query_documents(f"kickai_{team_id}_approval_requests", filters)

        if not requests:
            if user_id:
                return "✅ No pending approval requests for your account."
            else:
                return "✅ No pending approval requests."

        # Format response
        if user_id:
            # Single user view
            request_list = []
            for req in requests:
                request_time = datetime.fromisoformat(req["requested_at"]).strftime(
                    "%d %b %Y at %H:%M"
                )
                request_list.append(
                    f"• {req['field']}: {req['old_value']} → {req['new_value']} (Requested: {request_time})"
                )

            return f"""⏳ Your Pending Approval Requests:

{chr(10).join(request_list)}

🔒 These requests require admin approval.
📧 You'll be notified when processed.
💡 Contact a team admin for status updates."""

        else:
            # Admin view - all pending requests
            request_list = []
            for req in requests:
                request_time = datetime.fromisoformat(req["requested_at"]).strftime(
                    "%d %b %Y at %H:%M"
                )
                request_list.append(
                    f"• {req['member_name']}: {req['field']} → {req['new_value']} (Requested: {request_time})"
                )

            return f"""⏳ All Pending Approval Requests:

{chr(10).join(request_list)}

🔧 Admin Action Required:
Use team admin tools to approve or reject these requests.

📊 Total Requests: {len(requests)}"""

    except Exception as e:
        logger.error(f"❌ Error getting approval requests: {e}", exc_info=True)
        return "❌ Error retrieving approval requests. Please try again."
