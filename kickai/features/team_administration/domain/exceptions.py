#!/usr/bin/env python3
"""
Team Administration Domain Exceptions

Custom exception hierarchy for team administration operations to provide
specific error types instead of generic Exception handling.
"""


class TeamAdministrationError(Exception):
    """Base exception for team administration errors."""

    pass


class TeamServiceError(TeamAdministrationError):
    """Base exception for team service errors."""

    pass


class TeamNotFoundError(TeamServiceError):
    """Team not found in system."""

    def __init__(self, team_id: str):
        self.team_id = team_id
        super().__init__(f"Team not found: {team_id}")


class TeamServiceUnavailableError(TeamServiceError):
    """Team service is not available."""

    def __init__(self, message: str = "Team service unavailable - please try again later"):
        super().__init__(message)


class LeadershipChatNotConfiguredError(TeamServiceError):
    """Team leadership chat is not configured."""

    def __init__(self, team_id: str):
        self.team_id = team_id
        super().__init__(
            f"Leadership chat not configured for team {team_id} - contact administrator"
        )


class TeamMemberError(TeamAdministrationError):
    """Base exception for team member errors."""

    pass


class TeamMemberNotFoundError(TeamMemberError):
    """Team member not found."""

    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        super().__init__(f"Team member not found by {identifier_type}: {identifier}")


class DuplicatePhoneNumberError(TeamMemberError):
    """Phone number already registered to another team member."""

    def __init__(self, phone_number: str, existing_member_name: str):
        self.phone_number = phone_number
        self.existing_member_name = existing_member_name
        super().__init__(
            f"Phone number {phone_number} is already registered to {existing_member_name}"
        )


class TeamMemberServiceUnavailableError(TeamMemberError):
    """Team member service is not available."""

    def __init__(self, message: str = "Team member service not available"):
        super().__init__(message)


class InviteLinkError(TeamAdministrationError):
    """Base exception for invite link errors."""

    pass


class InviteLinkServiceUnavailableError(InviteLinkError):
    """Invite link service is not available."""

    def __init__(
        self,
        message: str = "Invite link service unavailable - member added but no invite generated",
    ):
        super().__init__(message)


class InviteLinkCreationError(InviteLinkError):
    """Failed to create invite link."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Failed to create invite link: {reason}")


class ValidationError(TeamAdministrationError):
    """Base exception for validation errors."""

    pass


class InvalidPhoneNumberError(ValidationError):
    """Invalid phone number format."""

    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        super().__init__(
            f"Invalid phone number format: {phone_number}. Please use UK format: +44xxxxxxxxxx or 07xxxxxxxxx"
        )


class InvalidTeamMemberRoleError(ValidationError):
    """Invalid team member role."""

    def __init__(self, role: str, valid_roles: list[str]):
        self.role = role
        self.valid_roles = valid_roles
        super().__init__(f"Invalid role '{role}'. Valid roles: {', '.join(valid_roles)}")


class MissingRequiredFieldError(ValidationError):
    """Required field is missing."""

    def __init__(self, field_name: str):
        self.field_name = field_name
        super().__init__(f"Required field missing: {field_name}")


class PermissionError(TeamAdministrationError):
    """Permission denied for operation."""

    def __init__(self, operation: str, required_permission: str):
        self.operation = operation
        self.required_permission = required_permission
        super().__init__(f"Permission denied for {operation}. Required: {required_permission}")


class RepositoryError(TeamAdministrationError):
    """Base exception for repository errors."""

    pass


class RepositoryUnavailableError(RepositoryError):
    """Repository service is not available."""

    def __init__(self, repository_type: str):
        self.repository_type = repository_type
        super().__init__(f"{repository_type} repository service not available")


class TeamMemberLookupError(TeamMemberError):
    """Error looking up team member."""

    def __init__(self, member_identifier: str, team_id: str, details: str = ""):
        self.member_identifier = member_identifier
        self.team_id = team_id
        self.details = details
        message = f"Failed to lookup team member {member_identifier} in team {team_id}"
        if details:
            message += f": {details}"
        super().__init__(message)


class TeamMemberUpdateError(TeamMemberError):
    """Error updating team member."""

    def __init__(self, member_identifier: str, field: str, details: str = ""):
        self.member_identifier = member_identifier
        self.field = field
        self.details = details
        message = f"Failed to update {field} for team member {member_identifier}"
        if details:
            message += f": {details}"
        super().__init__(message)


class TeamMemberCreationError(TeamMemberError):
    """Error creating team member."""

    def __init__(self, member_name: str, details: str = ""):
        self.member_name = member_name
        self.details = details
        message = f"Failed to create team member {member_name}"
        if details:
            message += f": {details}"
        super().__init__(message)
