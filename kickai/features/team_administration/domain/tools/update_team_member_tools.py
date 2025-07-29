#!/usr/bin/env python3
"""
Team Member Update Tools for KICKAI System

This module provides tools for updating team member information in the leadership chat context.
Team members can update their own information with proper validation and audit logging.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from crewai.tools import tool

from kickai.core.constants import get_team_members_collection
from kickai.core.exceptions import InputValidationError
from kickai.database.firebase_client import get_firebase_client

logger = logging.getLogger(__name__)


class TeamMemberUpdateValidationError(InputValidationError):
    """Exception raised for team member update validation errors."""
    pass


class TeamMemberUpdateValidator:
    """Validator for team member information updates."""
    
    # Valid roles for team members
    VALID_ROLES = [
        "team manager", "coach", "assistant coach", "head coach",
        "club administrator", "treasurer", "secretary", 
        "volunteer coordinator", "volunteer", "parent helper",
        "first aid coordinator", "equipment manager", "transport coordinator"
    ]
    
    # Fields that team members can update
    UPDATABLE_FIELDS = {
        "phone": "Contact phone number",
        "email": "Email address", 
        "emergency_contact": "Emergency contact information",
        "role": "Administrative role (admin approval required)"
    }
    
    # Fields that cannot be updated by users
    PROTECTED_FIELDS = {
        "user_id", "team_id", "telegram_id", "status", "created_at", 
        "source", "id", "name", "full_name", "approved_at", "approved_by"
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
        """Validate and normalize UK phone number."""
        # Remove spaces and special characters
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        # UK phone number patterns
        uk_patterns = [
            r'^\+44\d{10}$',  # +44xxxxxxxxxx
            r'^44\d{10}$',    # 44xxxxxxxxxx  
            r'^07\d{9}$',     # 07xxxxxxxxx
            r'^01\d{9}$',     # 01xxxxxxxxx
            r'^020\d{8}$',    # 020xxxxxxxx (London)
            r'^011\d{8}$',    # 011xxxxxxxx (Northern Ireland)
        ]
        
        # Try to match patterns
        for pattern in uk_patterns:
            if re.match(pattern, cleaned_phone):
                # Normalize to +44 format
                if cleaned_phone.startswith('0'):
                    return f"+44{cleaned_phone[1:]}"
                elif cleaned_phone.startswith('44'):
                    return f"+{cleaned_phone}"
                else:
                    return cleaned_phone
        
        raise TeamMemberUpdateValidationError(
            f"Invalid phone number format. Please use UK format: "
            f"+44xxxxxxxxxx or 07xxxxxxxxx. Got: {phone}"
        )
    
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
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
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


@tool("update_team_member_information")
def update_team_member_information(user_id: str, team_id: str, field: str, value: str, username: str = "Unknown") -> str:
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
        logger.info(f"🔄 Team member update request: user_id={user_id}, team_id={team_id}, field={field}")
        
        # Validate inputs
        if not user_id or not team_id or not field or not value:
            return "❌ Update Failed: Missing required parameters (user_id, team_id, field, value)"
        
        # Initialize Firebase service
        firebase_service = get_firebase_client()
        collection_name = get_team_members_collection(team_id)
        
        # Check if team member exists
        logger.info(f"🔍 Checking if team member exists: user_id={user_id}")
        members = firebase_service.query_documents(
            collection_name, 
            [("user_id", "==", user_id)]
        )
        
        if not members:
            logger.warning(f"❌ Team member not found: user_id={user_id}")
            return "❌ Update Failed: You are not registered as a team member. Use /register to register."
        
        member = members[0]
        member_id = member.get('id', 'unknown')
        member_name = member.get('name', 'Unknown Member')
        
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
                collection_name,
                [("phone", "==", validated_value)]
            )
            
            # Filter out the current member
            duplicate_members = [m for m in existing_members if m.get('user_id') != user_id]
            
            if duplicate_members:
                duplicate_name = duplicate_members[0].get('name', 'Unknown')
                logger.warning(f"❌ Duplicate phone number: {validated_value} already used by {duplicate_name}")
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
                "approved_at": None
            }
            
            # Store approval request
            approval_collection = f"kickai_approval_requests_{team_id}"
            firebase_service.add_document(approval_collection, approval_data)
            
            logger.info(f"⏳ Approval request created for field '{field}'")
            return f"⏳ Update request submitted for approval. Field '{field}' will be updated to '{validated_value}' once approved by team leadership."
        
        else:
            # Direct update for non-admin fields
            update_data = {
                field: validated_value,
                "updated_at": current_time,
                "updated_by": username
            }
            
            # Update the document
            firebase_service.update_document(collection_name, member_id, update_data)
            
            logger.info(f"✅ Team member updated successfully: {field} = {validated_value}")
            return f"✅ Team member information updated successfully! Field '{field}' changed to '{validated_value}'"
            
    except TeamMemberUpdateValidationError as e:
        logger.error(f"❌ Validation error in team member update: {e}")
        return f"❌ Update Failed: {str(e)}"
        
    except Exception as e:
        logger.error(f"❌ Error updating team member: {e}")
        return f"❌ Update Failed: An unexpected error occurred. Please try again or contact team leadership."


@tool("get_team_member_updatable_fields")
def get_team_member_updatable_fields(user_id: str, team_id: str) -> str:
    """
    Get list of fields that a team member can update.
    
    Args:
        user_id: Telegram user ID of the team member
        team_id: Team ID
        
    Returns:
        List of updatable fields with descriptions
    """
    try:
        logger.info(f"📋 Getting updatable fields for team member: user_id={user_id}, team_id={team_id}")
        
        # Initialize Firebase service
        firebase_service = get_firebase_client()
        collection_name = get_team_members_collection(team_id)
        
        # Check if team member exists
        members = firebase_service.query_documents(
            collection_name, 
            [("user_id", "==", user_id)]
        )
        
        if not members:
            return "❌ You are not registered as a team member. Use /register to register."
        
        # Get updatable fields
        validator = TeamMemberUpdateValidator()
        updatable_fields = validator.UPDATABLE_FIELDS
        
        # Format the response
        fields_list = []
        for field, description in updatable_fields.items():
            requires_approval = validator.requires_admin_approval(field)
            approval_note = " (requires admin approval)" if requires_approval else ""
            fields_list.append(f"• **{field.replace('_', ' ').title()}**: {description}{approval_note}")
        
        response = f"""
📋 **UPDATABLE FIELDS**

You can update the following information:

{chr(10).join(fields_list)}

💡 **Usage:** /update [field_name] [new_value]
📝 **Example:** /update phone +447123456789
        """
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"❌ Error getting updatable fields: {e}")
        return "❌ Error retrieving updatable fields. Please try again."


@tool("validate_team_member_update_request")
def validate_team_member_update_request(user_id: str, team_id: str, field: str, value: str) -> str:
    """
    Validate a team member update request before processing.
    
    Args:
        user_id: Telegram user ID of the team member
        team_id: Team ID
        field: Field name to update
        value: New value for the field
        
    Returns:
        Validation result message
    """
    try:
        logger.info(f"🔍 Validating team member update request: user_id={user_id}, field={field}")
        
        # Validate inputs
        if not user_id or not team_id or not field or not value:
            return "❌ Validation Failed: Missing required parameters"
        
        # Initialize Firebase service
        firebase_service = get_firebase_client()
        collection_name = get_team_members_collection(team_id)
        
        # Check if team member exists
        members = firebase_service.query_documents(
            collection_name, 
            [("user_id", "==", user_id)]
        )
        
        if not members:
            return "❌ Validation Failed: You are not registered as a team member"
        
        # Validate field name
        validator = TeamMemberUpdateValidator()
        try:
            validator.validate_field_name(field)
        except TeamMemberUpdateValidationError as e:
            return f"❌ Validation Failed: {str(e)}"
        
        # Validate field value
        try:
            validated_value = validator.validate_field_value(field, value)
        except TeamMemberUpdateValidationError as e:
            return f"❌ Validation Failed: {str(e)}"
        
        # Check for duplicate phone numbers (if updating phone)
        if field.lower() == "phone":
            existing_members = firebase_service.query_documents(
                collection_name,
                [("phone", "==", validated_value)]
            )
            
            # Filter out the current member
            duplicate_members = [m for m in existing_members if m.get('user_id') != user_id]
            
            if duplicate_members:
                duplicate_name = duplicate_members[0].get('name', 'Unknown')
                return f"❌ Validation Failed: Phone number {validated_value} is already registered to another team member ({duplicate_name})"
        
        # Check if approval is required
        requires_approval = validator.requires_admin_approval(field)
        
        if requires_approval:
            return f"✅ Validation passed. Field '{field}' with value '{validated_value}' requires admin approval."
        else:
            return f"✅ Validation passed. Field '{field}' with value '{validated_value}' can be updated immediately."
            
    except Exception as e:
        logger.error(f"❌ Error validating team member update: {e}")
        return f"❌ Validation Failed: An unexpected error occurred"


@tool("get_pending_team_member_approval_requests")
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
        
        # Initialize Firebase service
        firebase_service = get_firebase_client()
        approval_collection = f"kickai_approval_requests_{team_id}"
        
        # Query for pending requests
        query_filters = [("status", "==", "pending")]
        if user_id:
            query_filters.append(("user_id", "==", user_id))
        
        pending_requests = firebase_service.query_documents(approval_collection, query_filters)
        
        if not pending_requests:
            if user_id:
                return "✅ No pending approval requests found for your account."
            else:
                return "✅ No pending approval requests found for this team."
        
        # Format the response
        requests_list = []
        for request in pending_requests:
            request_id = request.get('id', 'unknown')
            member_name = request.get('member_name', 'Unknown')
            field = request.get('field', 'unknown')
            new_value = request.get('new_value', 'unknown')
            requested_by = request.get('requested_by', 'Unknown')
            requested_at = request.get('requested_at', 'Unknown')
            
            requests_list.append(f"""
📋 **Request ID:** {request_id}
👤 **Member:** {member_name}
🔄 **Field:** {field.replace('_', ' ').title()}
🆕 **New Value:** {new_value}
👤 **Requested By:** {requested_by}
📅 **Requested:** {requested_at}
            """)
        
        response = f"""
⏳ **PENDING APPROVAL REQUESTS**

Found {len(pending_requests)} pending request(s):

{chr(10).join(requests_list)}

💡 **Admin Actions:**
• Use /approve [request_id] to approve a request
• Use /reject [request_id] [reason] to reject a request
        """
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"❌ Error getting pending approval requests: {e}")
        return "❌ Error retrieving pending approval requests. Please try again."