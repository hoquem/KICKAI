#!/usr/bin/env python3
"""
Communication Domain Exceptions

Custom exception hierarchy for communication operations to provide
specific error types instead of generic Exception handling.
"""

from kickai.core.exceptions import KickAIError


class CommunicationError(KickAIError):
    """Base exception for communication errors."""

    pass


class CommunicationServiceError(CommunicationError):
    """Base exception for communication service errors."""

    pass


class CommunicationServiceUnavailableError(CommunicationServiceError):
    """Communication service is not available."""

    def __init__(self, message: str = "Communication service unavailable"):
        super().__init__(message)


class MessageSendError(CommunicationServiceError):
    """Failed to send message."""

    def __init__(self, chat_id: str, message: str, reason: str):
        self.chat_id = chat_id
        self.message = message
        self.reason = reason
        super().__init__(
            f"Failed to send message to chat {chat_id}: {reason}",
            context={"chat_id": chat_id, "message_preview": message[:100], "reason": reason},
        )


class InvalidChatIdError(CommunicationServiceError):
    """Invalid or inaccessible chat ID."""

    def __init__(self, chat_id: str):
        self.chat_id = chat_id
        super().__init__(
            f"Invalid or inaccessible chat ID: {chat_id}", context={"chat_id": chat_id}
        )


class MessageServiceError(CommunicationError):
    """Base exception for message service errors."""

    pass


class MessageServiceUnavailableError(MessageServiceError):
    """Message service is not available."""

    def __init__(self, message: str = "Message service unavailable"):
        super().__init__(message)


class MessageNotFoundError(MessageServiceError):
    """Message not found."""

    def __init__(self, message_id: str):
        self.message_id = message_id
        super().__init__(f"Message not found: {message_id}", context={"message_id": message_id})


class MessageValidationError(MessageServiceError):
    """Message validation failed."""

    def __init__(self, field: str, value: str, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(
            f"Message validation failed for {field}: {reason}",
            context={"field": field, "value": value, "reason": reason},
        )


class NotificationError(CommunicationError):
    """Base exception for notification errors."""

    pass


class NotificationServiceUnavailableError(NotificationError):
    """Notification service is not available."""

    def __init__(self, message: str = "Notification service unavailable"):
        super().__init__(message)


class NotificationSendError(NotificationError):
    """Failed to send notification."""

    def __init__(self, user_id: str, notification_type: str, reason: str):
        self.user_id = user_id
        self.notification_type = notification_type
        self.reason = reason
        super().__init__(
            f"Failed to send {notification_type} notification to user {user_id}: {reason}",
            context={"user_id": user_id, "notification_type": notification_type, "reason": reason},
        )


class NotificationNotFoundError(NotificationError):
    """Notification not found."""

    def __init__(self, notification_id: str):
        self.notification_id = notification_id
        super().__init__(
            f"Notification not found: {notification_id}",
            context={"notification_id": notification_id},
        )


class InviteLinkError(CommunicationError):
    """Base exception for invite link errors."""

    pass


class InviteLinkServiceUnavailableError(InviteLinkError):
    """Invite link service is not available."""

    def __init__(self, message: str = "Invite link service unavailable"):
        super().__init__(message)


class InviteLinkCreationError(InviteLinkError):
    """Failed to create invite link."""

    def __init__(self, team_id: str, member_id: str, reason: str):
        self.team_id = team_id
        self.member_id = member_id
        self.reason = reason
        super().__init__(
            f"Failed to create invite link for member {member_id} in team {team_id}: {reason}",
            context={"team_id": team_id, "member_id": member_id, "reason": reason},
        )


class InviteLinkNotFoundError(InviteLinkError):
    """Invite link not found."""

    def __init__(self, invite_link: str):
        self.invite_link = invite_link
        super().__init__(
            f"Invite link not found or invalid: {invite_link[:20]}...",
            context={"invite_link_preview": invite_link[:20]},
        )


class InviteLinkExpiredError(InviteLinkError):
    """Invite link has expired."""

    def __init__(self, invite_link: str):
        self.invite_link = invite_link
        super().__init__(
            f"Invite link has expired: {invite_link[:20]}...",
            context={"invite_link_preview": invite_link[:20]},
        )


class InviteLinkAlreadyUsedError(InviteLinkError):
    """Invite link has already been used."""

    def __init__(self, invite_link: str, used_by: str):
        self.invite_link = invite_link
        self.used_by = used_by
        super().__init__(
            f"Invite link already used by {used_by}",
            context={"invite_link_preview": invite_link[:20], "used_by": used_by},
        )


class TelegramBotError(CommunicationError):
    """Base exception for Telegram bot errors."""

    pass


class TelegramBotServiceUnavailableError(TelegramBotError):
    """Telegram bot service is not available."""

    def __init__(self, message: str = "Telegram bot service unavailable"):
        super().__init__(message)


class TelegramApiError(TelegramBotError):
    """Telegram API error."""

    def __init__(self, api_method: str, error_code: int, error_description: str):
        self.api_method = api_method
        self.error_code = error_code
        self.error_description = error_description
        super().__init__(
            f"Telegram API error in {api_method}: [{error_code}] {error_description}",
            context={
                "api_method": api_method,
                "error_code": error_code,
                "error_description": error_description,
            },
        )


class InvalidBotTokenError(TelegramBotError):
    """Invalid or missing bot token."""

    def __init__(self, token_hint: str = ""):
        self.token_hint = token_hint
        message = "Invalid or missing Telegram bot token"
        if token_hint:
            message += f" (hint: {token_hint})"
        super().__init__(message, context={"token_hint": token_hint})


class ChatAccessError(TelegramBotError):
    """Bot cannot access the specified chat."""

    def __init__(self, chat_id: str, reason: str):
        self.chat_id = chat_id
        self.reason = reason
        super().__init__(
            f"Cannot access chat {chat_id}: {reason}",
            context={"chat_id": chat_id, "reason": reason},
        )
