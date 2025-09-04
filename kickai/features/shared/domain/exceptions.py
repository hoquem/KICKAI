#!/usr/bin/env python3
"""
Shared Domain Exceptions

Custom exception hierarchy for shared operations across features to provide
specific error types instead of generic Exception handling.
"""

from kickai.core.exceptions import KickAIError


class SharedError(KickAIError):
    """Base exception for shared feature errors."""

    pass


class CommandProcessingError(SharedError):
    """Base exception for command processing errors."""

    pass


class CommandProcessingServiceUnavailableError(CommandProcessingError):
    """Command processing service is not available."""

    def __init__(self, message: str = "Command processing service unavailable"):
        super().__init__(message)


class InvalidCommandError(CommandProcessingError):
    """Invalid command format or structure."""

    def __init__(self, command: str, reason: str):
        self.command = command
        self.reason = reason
        super().__init__(
            f"Invalid command '{command}': {reason}", context={"command": command, "reason": reason}
        )


class CommandExecutionError(CommandProcessingError):
    """Command execution failed."""

    def __init__(self, command: str, telegram_id: str, error_details: str):
        self.command = command
        self.telegram_id = telegram_id
        self.error_details = error_details
        super().__init__(
            f"Command '{command}' execution failed for user {telegram_id}: {error_details}",
            context={
                "command": command,
                "telegram_id": telegram_id,
                "error_details": error_details,
            },
        )


class UserContextError(SharedError):
    """Base exception for user context errors."""

    pass


class UserContextBuildError(UserContextError):
    """Failed to build user context."""

    def __init__(self, telegram_id: str, reason: str):
        self.telegram_id = telegram_id
        self.reason = reason
        super().__init__(
            f"Failed to build context for user {telegram_id}: {reason}",
            context={"telegram_id": telegram_id, "reason": reason},
        )


class UserNotRegisteredError(UserContextError):
    """User is not registered in the system."""

    def __init__(self, telegram_id: str, chat_type: str, registration_type: str):
        self.telegram_id = telegram_id
        self.chat_type = chat_type
        self.registration_type = registration_type
        super().__init__(
            f"User {telegram_id} not registered as {registration_type} for {chat_type} chat",
            context={
                "telegram_id": telegram_id,
                "chat_type": chat_type,
                "registration_type": registration_type,
            },
        )


class LinkedRecordError(SharedError):
    """Base exception for linked record operations."""

    pass


class LinkedRecordSyncError(LinkedRecordError):
    """Failed to sync linked records."""

    def __init__(self, source_type: str, target_type: str, record_id: str, reason: str):
        self.source_type = source_type
        self.target_type = target_type
        self.record_id = record_id
        self.reason = reason
        super().__init__(
            f"Failed to sync {source_type} to {target_type} for record {record_id}: {reason}",
            context={
                "source_type": source_type,
                "target_type": target_type,
                "record_id": record_id,
                "reason": reason,
            },
        )


class LinkedRecordNotFoundError(LinkedRecordError):
    """Linked record not found."""

    def __init__(self, source_type: str, target_type: str, identifier: str):
        self.source_type = source_type
        self.target_type = target_type
        self.identifier = identifier
        super().__init__(
            f"No linked {target_type} record found for {source_type} with identifier {identifier}",
            context={
                "source_type": source_type,
                "target_type": target_type,
                "identifier": identifier,
            },
        )


class FieldValidationError(SharedError):
    """Base exception for field validation errors."""

    pass


class InvalidFieldNameError(FieldValidationError):
    """Invalid field name specified."""

    def __init__(self, field_name: str, entity_type: str, valid_fields: list[str]):
        self.field_name = field_name
        self.entity_type = entity_type
        self.valid_fields = valid_fields
        super().__init__(
            f"Invalid field '{field_name}' for {entity_type}. Valid fields: {', '.join(valid_fields)}",
            context={
                "field_name": field_name,
                "entity_type": entity_type,
                "valid_fields": valid_fields,
            },
        )


class InvalidFieldValueError(FieldValidationError):
    """Invalid field value provided."""

    def __init__(self, field_name: str, field_value: str, reason: str):
        self.field_name = field_name
        self.field_value = field_value
        self.reason = reason
        super().__init__(
            f"Invalid value for field '{field_name}' = '{field_value}': {reason}",
            context={"field_name": field_name, "field_value": field_value, "reason": reason},
        )


class ProtectedFieldError(FieldValidationError):
    """Attempted to modify a protected field."""

    def __init__(self, field_name: str, entity_type: str):
        self.field_name = field_name
        self.entity_type = entity_type
        super().__init__(
            f"Field '{field_name}' is protected and cannot be modified for {entity_type}",
            context={"field_name": field_name, "entity_type": entity_type},
        )


class AdminApprovalRequiredError(FieldValidationError):
    """Field modification requires admin approval."""

    def __init__(self, field_name: str, telegram_id: str):
        self.field_name = field_name
        self.telegram_id = telegram_id
        super().__init__(
            f"Field '{field_name}' modification by user {telegram_id} requires admin approval",
            context={"field_name": field_name, "telegram_id": telegram_id},
        )


class UtilityError(SharedError):
    """Base exception for utility function errors."""

    pass


class PhoneValidationError(UtilityError):
    """Phone number validation failed."""

    def __init__(self, phone_number: str, reason: str):
        self.phone_number = phone_number
        self.reason = reason
        super().__init__(
            f"Phone number validation failed for '{phone_number}': {reason}",
            context={"phone_number": phone_number, "reason": reason},
        )


class EmailValidationError(UtilityError):
    """Email validation failed."""

    def __init__(self, email: str, reason: str):
        self.email = email
        self.reason = reason
        super().__init__(
            f"Email validation failed for '{email}': {reason}",
            context={"email": email, "reason": reason},
        )


class DataFormatError(UtilityError):
    """Data format is invalid."""

    def __init__(self, data_type: str, data_value: str, expected_format: str):
        self.data_type = data_type
        self.data_value = data_value
        self.expected_format = expected_format
        super().__init__(
            f"Invalid {data_type} format: '{data_value}'. Expected: {expected_format}",
            context={
                "data_type": data_type,
                "data_value": data_value,
                "expected_format": expected_format,
            },
        )


class ToolError(SharedError):
    """Base exception for tool errors."""

    pass


class ToolExecutionError(ToolError):
    """Tool execution failed."""

    def __init__(self, tool_name: str, telegram_id: str, error_details: str):
        self.tool_name = tool_name
        self.telegram_id = telegram_id
        self.error_details = error_details
        super().__init__(
            f"Tool '{tool_name}' execution failed for user {telegram_id}: {error_details}",
            context={
                "tool_name": tool_name,
                "telegram_id": telegram_id,
                "error_details": error_details,
            },
        )


class ToolParameterError(ToolError):
    """Invalid tool parameters."""

    def __init__(self, tool_name: str, parameter: str, value: str, reason: str):
        self.tool_name = tool_name
        self.parameter = parameter
        self.value = value
        self.reason = reason
        super().__init__(
            f"Invalid parameter '{parameter}' = '{value}' for tool '{tool_name}': {reason}",
            context={
                "tool_name": tool_name,
                "parameter": parameter,
                "value": value,
                "reason": reason,
            },
        )
