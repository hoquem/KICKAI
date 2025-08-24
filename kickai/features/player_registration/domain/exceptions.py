#!/usr/bin/env python3
"""
Player Registration Domain Exceptions

Custom exception hierarchy for player registration operations to provide
specific error types instead of generic Exception handling.
"""

from kickai.core.exceptions import KickAIError


class PlayerRegistrationError(KickAIError):
    """Base exception for player registration errors."""
    pass


class PlayerServiceError(PlayerRegistrationError):
    """Base exception for player service errors."""
    pass


class PlayerNotFoundError(PlayerServiceError):
    """Player not found in system."""
    
    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        super().__init__(
            f"Player not found by {identifier_type}: {identifier}",
            context={"identifier": identifier, "identifier_type": identifier_type}
        )


class PlayerAlreadyExistsError(PlayerServiceError):
    """Player already exists in the system."""
    
    def __init__(self, phone_number: str, team_id: str):
        self.phone_number = phone_number
        self.team_id = team_id
        super().__init__(
            f"Player with phone {phone_number} already exists in team {team_id}",
            context={"phone_number": phone_number, "team_id": team_id}
        )


class PlayerServiceUnavailableError(PlayerServiceError):
    """Player service is not available."""
    
    def __init__(self, message: str = "Player service unavailable - please try again later"):
        super().__init__(message)


class PlayerRegistrationServiceError(PlayerRegistrationError):
    """Base exception for registration service errors."""
    pass


class RegistrationServiceUnavailableError(PlayerRegistrationServiceError):
    """Registration service is not available."""
    
    def __init__(self, message: str = "Registration service unavailable"):
        super().__init__(message)


class PlayerValidationError(PlayerRegistrationError):
    """Base exception for player validation errors."""
    pass


class InvalidPlayerNameError(PlayerValidationError):
    """Invalid player name format."""
    
    def __init__(self, name: str):
        self.name = name
        super().__init__(
            f"Invalid player name format: {name}. Name must be 2-50 characters and contain only letters, spaces, hyphens, and apostrophes",
            context={"name": name}
        )


class InvalidPlayerPhoneError(PlayerValidationError):
    """Invalid player phone number format."""
    
    def __init__(self, phone_number: str):
        self.phone_number = phone_number
        super().__init__(
            f"Invalid phone number format: {phone_number}. Please use UK format: +44xxxxxxxxxx or 07xxxxxxxxx",
            context={"phone_number": phone_number}
        )


class InvalidPlayerPositionError(PlayerValidationError):
    """Invalid player position."""
    
    def __init__(self, position: str, valid_positions: list[str]):
        self.position = position
        self.valid_positions = valid_positions
        super().__init__(
            f"Invalid position '{position}'. Valid positions: {', '.join(valid_positions)}",
            context={"position": position, "valid_positions": valid_positions}
        )


class DuplicatePlayerPhoneError(PlayerValidationError):
    """Phone number already registered to another player."""
    
    def __init__(self, phone_number: str, existing_player_name: str):
        self.phone_number = phone_number
        self.existing_player_name = existing_player_name
        super().__init__(
            f"Phone number {phone_number} is already registered to {existing_player_name}",
            context={"phone_number": phone_number, "existing_player_name": existing_player_name}
        )


class MissingRequiredFieldError(PlayerValidationError):
    """Required field is missing."""
    
    def __init__(self, field_name: str):
        self.field_name = field_name
        super().__init__(
            f"Required field missing: {field_name}",
            context={"field_name": field_name}
        )


class PlayerLookupError(PlayerRegistrationError):
    """Base exception for player lookup errors."""
    
    def __init__(self, player_identifier: str, team_id: str, error_details: str):
        self.player_identifier = player_identifier
        self.team_id = team_id
        self.error_details = error_details
        super().__init__(
            f"Player lookup failed for {player_identifier} in team {team_id}: {error_details}",
            context={"player_identifier": player_identifier, "team_id": team_id, "error_details": error_details}
        )


class PlayerLookupServiceUnavailableError(PlayerLookupError):
    """Player lookup service is not available."""
    
    def __init__(self, message: str = "Player lookup service unavailable"):
        super().__init__(message)


class PlayerRepositoryError(PlayerRegistrationError):
    """Base exception for player repository errors."""
    pass


class PlayerRepositoryUnavailableError(PlayerRepositoryError):
    """Player repository is not available."""
    
    def __init__(self, message: str = "Player repository service not available"):
        super().__init__(message)


class PlayerDataCorruptionError(PlayerRepositoryError):
    """Player data is corrupted or invalid."""
    
    def __init__(self, player_id: str, corruption_details: str):
        self.player_id = player_id
        self.corruption_details = corruption_details
        super().__init__(
            f"Player data corruption detected for {player_id}: {corruption_details}",
            context={"player_id": player_id, "corruption_details": corruption_details}
        )


class PlayerUpdateError(PlayerRegistrationError):
    """Base exception for player update operations."""
    pass


class PlayerUpdateValidationError(PlayerUpdateError):
    """Player update validation failed."""
    
    def __init__(self, field: str, value: str, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(
            f"Player update validation failed for {field}='{value}': {reason}",
            context={"field": field, "value": value, "reason": reason}
        )


class PlayerPermissionError(PlayerRegistrationError):
    """Permission denied for player operation."""
    
    def __init__(self, operation: str, user_id: str, required_permission: str):
        self.operation = operation
        self.user_id = user_id
        self.required_permission = required_permission
        super().__init__(
            f"Permission denied for user {user_id} to perform {operation}. Required: {required_permission}",
            context={"operation": operation, "user_id": user_id, "required_permission": required_permission}
        )


class PlayerDataError(PlayerRegistrationError):
    """Player data operation failed."""
    
    def __init__(self, message: str, player_id: str = None):
        self.player_id = player_id
        super().__init__(
            message,
            context={"player_id": player_id} if player_id else {}
        )