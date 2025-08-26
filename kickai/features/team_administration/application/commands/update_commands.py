#!/usr/bin/env python3
"""
Team Administration Update Commands

This module registers team member update and administration commands.
These commands use the update tools created in Phase 5.
"""

from kickai.core.command_registry import CommandType, PermissionLevel, command


@command(
    name="/updateteam",
    description="Update team member information (Admin operations)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration", 
    examples=[
        "/updateteam member M01JS phone +447123456789",
        "/updateteam role M01JS Assistant Coach",
        "/updateteam status M01JS inactive"
    ],
    parameters={
        "operation": "Operation type (member, role, status, etc.)",
        "target": "Target member ID or identifier",
        "field": "Field to update",
        "value": "New value"
    },
    help_text="""
🔧 Team Administration Updates (Leadership Only)

Administrative commands for updating team member information and managing the team.

Usage:
/updateteam [operation] [target] [field] [value]

🔑 Admin Operations:
• member - Update another member's information
• role - Update a member's role (admin approval required)
• status - Update member status (active/inactive/suspended)
• bulk - Perform bulk updates

💡 Examples:
• /updateteam member M01JS phone +447123456789
• /updateteam member M01JS email newuser@example.com  
• /updateteam role M01JS Assistant Coach
• /updateteam status M01JS inactive

📋 Member Update Fields:
• phone - Contact phone number
• email - Email address
• emergency_contact_name - Emergency contact name
• emergency_contact_phone - Emergency contact phone
• role - Administrative role

📊 Status Values:
• active - Member is active and can perform duties
• inactive - Member is temporarily inactive
• suspended - Member is suspended from duties
• pending - Member is pending approval

🔐 Admin Only Operations:
• Role changes for other members
• Status changes
• Bulk operations
• Member activation/deactivation

🔍 To see team member list: /listmembers
🔍 To get detailed help: /updateteam help

⚠️ Note: These operations require leadership permissions and some require admin rights.
    """,
)
async def handle_updateteam_command(update, context, **kwargs):
    """Handle /updateteam administrative command."""
    # This will be handled by the agent system
    return None


@command(
    name="/listmembers",
    description="List all team members with status (Leadership only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.LEADERSHIP,
    feature="team_administration",
    examples=["/listmembers", "/listmembers active", "/listmembers pending"],
    parameters={"status": "Optional status filter (active, inactive, pending, all)"},
    help_text="""
📋 Team Members List (Leadership Only)

Display list of all team members with their status and information.

Usage:
/listmembers [status]

🔍 Status Filters:
• active - Only active members (default)
• inactive - Only inactive members  
• pending - Only pending approval
• suspended - Only suspended members
• all - All members regardless of status

📊 Information Displayed:
• Member ID and Name
• Role and Admin Status
• Contact Information
• Status and Last Updated
• Join Date

💡 Examples:
• /listmembers - Show active members
• /listmembers all - Show all members
• /listmembers pending - Show pending approvals
• /listmembers inactive - Show inactive members

🔧 Quick Actions:
• To update a member: /updateteam member [ID] [field] [value]
• To change status: /updateteam status [ID] [new_status]
• To update role: /updateteam role [ID] [new_role]

🔒 Note: This command is only available in leadership chat.
    """,
)
async def handle_listmembers_command(update, context, **kwargs):
    """Handle /listmembers command."""
    # This will be handled by the agent system
    return None


@command(
    name="/approvemember", 
    description="Approve pending team member (Admin only)",
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.ADMIN,
    feature="team_administration",
    examples=["/approvemember M01JS", "/approvemember M01JS Assistant Coach"],
    parameters={
        "member_id": "Member ID to approve",
        "role": "Optional role to assign (default: Team Member)"
    },
    help_text="""
✅ Approve Team Member (Admin Only)

Approve a pending team member and optionally assign a role.

Usage:
/approvemember [member_id] [role]

💡 Examples:
• /approvemember M01JS - Approve with default role
• /approvemember M01JS Assistant Coach - Approve with specific role
• /approvemember M01JS Team Manager - Approve as manager

📋 Available Roles:
• Team Member (default)
• Assistant Coach
• Coach  
• Team Manager
• Club Administrator

✅ What Happens:
1. Member status changes from 'pending' to 'active'
2. Role is assigned (or updated if specified)
3. Member gains access to leadership chat features
4. Member receives approval notification
5. Member can now perform their role duties

🔐 Admin Rights Required:
• Only admins can approve members
• Only admins can assign leadership roles
• Role assignments are logged for audit

🔍 To see pending members: /listmembers pending
📝 To update role later: /updateteam role [ID] [new_role]

⚠️ Note: This command requires admin permissions.
    """,
)
async def handle_approvemember_command(update, context, **kwargs):
    """Handle /approvemember command."""
    # This will be handled by the agent system
    return None


@command(
    name="/rejectmember",
    description="Reject pending team member with reason (Admin only)", 
    command_type=CommandType.SLASH_COMMAND,
    permission_level=PermissionLevel.ADMIN,
    feature="team_administration",
    examples=["/rejectmember M01JS Insufficient qualifications"],
    parameters={
        "member_id": "Member ID to reject",
        "reason": "Reason for rejection (optional)"
    },
    help_text="""
❌ Reject Team Member (Admin Only)

Reject a pending team member with an optional reason.

Usage:
/rejectmember [member_id] [reason]

💡 Examples:
• /rejectmember M01JS - Reject without specific reason
• /rejectmember M01JS Insufficient experience
• /rejectmember M01JS Position already filled

❌ What Happens:
1. Member status changes from 'pending' to 'rejected'
2. Reason is recorded in the member record
3. Member receives rejection notification with reason
4. Member loses access to leadership chat features
5. Decision is logged for audit purposes

📝 Reason Guidelines:
• Be professional and constructive
• Provide specific feedback when possible
• Consider if member can reapply later
• Document decision clearly

🔄 Future Considerations:
• Rejected members can potentially reapply
• Status can be changed if circumstances change
• Rejection reasons help with future decisions

🔍 To see pending members: /listmembers pending
🔍 To see rejected members: /listmembers rejected

⚠️ Note: This command requires admin permissions.
    """,
)
async def handle_rejectmember_command(update, context, **kwargs):
    """Handle /rejectmember command."""
    # This will be handled by the agent system
    return None